from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

logger = logging.getLogger(__name__)

from src.context_platform.context_actor import get_actor
from src.context_platform.meeting_extraction import extract_transcript_auto
from src.context_platform.package_models import (
    ContextPackageSectionsV2,
    compute_readiness_v2,
    gap_analysis_dict,
    sections_from_legacy_dicts,
    sections_to_storage_tuple,
)
from src.context_platform.schemas import (
    ArtifactRead,
    AuditEventRead,
    ContextGapCreate,
    ContextGapRead,
    ContextPackageCreate,
    ContextPackageRead,
    ContextPackageSections,
    ContextPackageUpdate,
    DecisionRecordRead,
    DeliveryPhaseCreate,
    DeliveryPhaseRead,
    FeatureCreate,
    FeatureRead,
    ManufacturingRead,
    ManufacturingStatus,
    ManufacturingSubmit,
    MeetingCreate,
    ImprovementItemRead,
    MeetingExtractionConfirm,
    MeetingRead,
    MeetingTranscriptUpdate,
    MeetingTypeRef,
    PackageStatus,
    PhaseKind,
    RoadmapCycleCreate,
    RoadmapCycleRead,
    SignOffCreate,
    SignOffRead,
    SignOffRole,
    SprintBoardRead,
    SprintCommitmentRead,
    SprintCommitStoryBody,
    SprintCreate,
    SprintRead,
    StoryCreate,
    StoryRead,
    TriageQueue,
    TriageRead,
    TriageSubmit,
)

TECHNICAL_SIGNOFF_ROLES = frozenset({SignOffRole.tech_lead, SignOffRole.developer})
REQUIRED_SIGN_OFF_ROLES = frozenset(
    {SignOffRole.context_engineer, SignOffRole.product_owner}
)


def _sign_offs_satisfy_d7(roles: set[SignOffRole]) -> bool:
    if not REQUIRED_SIGN_OFF_ROLES.issubset(roles):
        return False
    return bool(roles & TECHNICAL_SIGNOFF_ROLES)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid() -> str:
    return str(uuid.uuid4())


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.execute(f"PRAGMA table_info({table})")
    return {row[1] for row in cur.fetchall()}


def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    r = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone()
    return r is not None


SCHEMA_V2 = """
CREATE TABLE IF NOT EXISTS roadmap_cycles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS delivery_phases (
    id TEXT PRIMARY KEY,
    roadmap_cycle_id TEXT NOT NULL REFERENCES roadmap_cycles(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    phase_kind TEXT NOT NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS features (
    id TEXT PRIMARY KEY,
    delivery_phase_id TEXT NOT NULL REFERENCES delivery_phases(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS stories (
    id TEXT PRIMARY KEY,
    feature_id TEXT NOT NULL REFERENCES features(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sprints (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    roadmap_cycle_id TEXT REFERENCES roadmap_cycles(id) ON DELETE SET NULL,
    starts_at TEXT,
    ends_at TEXT,
    capacity_notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sprint_commitments (
    id TEXT PRIMARY KEY,
    sprint_id TEXT NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    UNIQUE(sprint_id, story_id),
    UNIQUE(story_id)
);

CREATE TABLE IF NOT EXISTS context_packages (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'draft',
    readiness_score REAL NOT NULL DEFAULT 0,
    business_context TEXT NOT NULL DEFAULT '{}',
    technical_approach TEXT NOT NULL DEFAULT '{}',
    testing_contract TEXT NOT NULL DEFAULT '{}',
    package_schema_version INTEGER NOT NULL DEFAULT 2,
    approved_at TEXT,
    content_hash TEXT,
    approved_snapshot_json TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(story_id, version)
);

CREATE TABLE IF NOT EXISTS sign_offs (
    id TEXT PRIMARY KEY,
    context_package_id TEXT NOT NULL REFERENCES context_packages(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    signed_by TEXT NOT NULL,
    signed_at TEXT NOT NULL,
    UNIQUE(context_package_id, role)
);

CREATE TABLE IF NOT EXISTS context_gaps (
    id TEXT PRIMARY KEY,
    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
    context_package_id TEXT REFERENCES context_packages(id) ON DELETE SET NULL,
    description TEXT NOT NULL,
    gap_type TEXT NOT NULL DEFAULT '',
    severity TEXT NOT NULL DEFAULT 'medium',
    meeting_hint TEXT NOT NULL DEFAULT '',
    resolved INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS manufacturing_requests (
    id TEXT PRIMARY KEY,
    context_package_id TEXT NOT NULL REFERENCES context_packages(id) ON DELETE CASCADE,
    package_content_hash TEXT,
    submitted_by TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',
    started_at TEXT,
    finished_at TEXT,
    output_summary TEXT,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS triage_results (
    id TEXT PRIMARY KEY,
    manufacturing_request_id TEXT NOT NULL REFERENCES manufacturing_requests(id) ON DELETE CASCADE,
    queue TEXT NOT NULL,
    feedback TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meetings (
    id TEXT PRIMARY KEY,
    meeting_type TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    scheduled_at TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    created_at TEXT NOT NULL,
    transcript TEXT,
    extraction_draft_json TEXT,
    extraction_status TEXT NOT NULL DEFAULT 'none',
    extraction_confirmed_at TEXT
);

CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    occurred_at TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'anonymous',
    detail_json TEXT
);

CREATE TABLE IF NOT EXISTS context_improvement_items (
    id TEXT PRIMARY KEY,
    source_triage_id TEXT REFERENCES triage_results(id) ON DELETE SET NULL,
    story_id TEXT REFERENCES stories(id) ON DELETE SET NULL,
    context_package_id TEXT REFERENCES context_packages(id) ON DELETE SET NULL,
    manufacturing_request_id TEXT REFERENCES manufacturing_requests(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'high',
    status TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS decision_records (
    id TEXT PRIMARY KEY,
    decision_code TEXT NOT NULL,
    summary TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    actor TEXT NOT NULL DEFAULT 'anonymous',
    detail_json TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    artifact_kind TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    title TEXT NOT NULL,
    body_json TEXT,
    actor TEXT NOT NULL DEFAULT 'anonymous',
    created_at TEXT NOT NULL
);
"""


def _migrate_legacy_to_v2(conn: sqlite3.Connection) -> None:
    if not _table_exists(conn, "work_items"):
        return
    cols = _table_columns(conn, "context_packages")
    if "work_item_id" not in cols:
        return

    conn.executescript(SCHEMA_V2)

    def _count(table: str) -> int:
        return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

    if _count("stories") == 0 and _count("work_items") > 0:
        ts = _now()
        cid = _uid()
        conn.execute(
            "INSERT INTO roadmap_cycles (id, name, created_at) VALUES (?,?,?)",
            (cid, "Imported", ts),
        )
        phase_by_kind: dict[str, str] = {}
        for row in conn.execute(
            "SELECT DISTINCT phase FROM work_items"
        ).fetchall():
            raw = row[0] or "discovery"
            kind = raw if raw in ("inception", "discovery", "delivery") else "discovery"
            pid = _uid()
            conn.execute(
                """INSERT INTO delivery_phases
                (id, roadmap_cycle_id, name, phase_kind, sort_order, created_at)
                VALUES (?,?,?,?,?,?)""",
                (pid, cid, f"Migrated ({kind})", kind, 0, ts),
            )
            phase_by_kind[kind] = pid
        feature_by_phase_id: dict[str, str] = {}
        for wi in conn.execute("SELECT * FROM work_items").fetchall():
            raw = wi["phase"] or "discovery"
            kind = raw if raw in phase_by_kind else "discovery"
            if kind not in phase_by_kind:
                pid = _uid()
                conn.execute(
                    """INSERT INTO delivery_phases
                    (id, roadmap_cycle_id, name, phase_kind, sort_order, created_at)
                    VALUES (?,?,?,?,?,?)""",
                    (pid, cid, f"Migrated ({kind})", kind, 0, ts),
                )
                phase_by_kind[kind] = pid
            phase_id = phase_by_kind[kind]
            if phase_id not in feature_by_phase_id:
                fid = _uid()
                conn.execute(
                    """INSERT INTO features
                    (id, delivery_phase_id, title, description, sort_order, created_at)
                    VALUES (?,?,?,?,?,?)""",
                    (fid, phase_id, "Imported stories", "", 0, ts),
                )
                feature_by_phase_id[phase_id] = fid
            fid = feature_by_phase_id[phase_id]
            conn.execute(
                """INSERT INTO stories (id, feature_id, title, description, created_at)
                VALUES (?,?,?,?,?)""",
                (wi["id"], fid, wi["title"], wi["description"], wi["created_at"]),
            )

    cols_cp = _table_columns(conn, "context_packages")
    if "story_id" not in cols_cp:
        conn.execute("ALTER TABLE context_packages ADD COLUMN story_id TEXT")
    conn.execute(
        "UPDATE context_packages SET story_id = work_item_id WHERE story_id IS NULL"
    )

    cols_cp = _table_columns(conn, "context_packages")
    for col, typ, _ in [
        ("package_schema_version", "INTEGER", "2"),
        ("approved_at", "TEXT", None),
        ("content_hash", "TEXT", None),
        ("approved_snapshot_json", "TEXT", None),
    ]:
        if col not in cols_cp:
            conn.execute(f"ALTER TABLE context_packages ADD COLUMN {col} {typ}")
    conn.execute(
        "UPDATE context_packages SET package_schema_version = 2 WHERE package_schema_version IS NULL"
    )

    gcols = _table_columns(conn, "context_gaps")
    if "story_id" not in gcols:
        conn.execute("ALTER TABLE context_gaps ADD COLUMN story_id TEXT")
    conn.execute(
        "UPDATE context_gaps SET story_id = work_item_id WHERE story_id IS NULL"
    )

    mcols = _table_columns(conn, "manufacturing_requests")
    if "package_content_hash" not in mcols:
        conn.execute(
            "ALTER TABLE manufacturing_requests ADD COLUMN package_content_hash TEXT"
        )

    conn.commit()
    return


def _normalize_mfg_status(raw: str) -> str:
    if raw == "in_progress":
        return ManufacturingStatus.running.value
    return raw


class ContextStore:
    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._ensure_extensions()

    def _init_db(self) -> None:
        with self._connect() as conn:
            if not _table_exists(conn, "context_packages"):
                conn.executescript(SCHEMA_V2)
                conn.commit()
                return
            cols = _table_columns(conn, "context_packages")
            if "work_item_id" in cols:
                _migrate_legacy_to_v2(conn)
            else:
                conn.executescript(SCHEMA_V2)
                for stmt in [
                    "ALTER TABLE context_packages ADD COLUMN package_schema_version INTEGER DEFAULT 2",
                    "ALTER TABLE context_packages ADD COLUMN approved_at TEXT",
                    "ALTER TABLE context_packages ADD COLUMN content_hash TEXT",
                    "ALTER TABLE context_packages ADD COLUMN approved_snapshot_json TEXT",
                    "ALTER TABLE manufacturing_requests ADD COLUMN package_content_hash TEXT",
                ]:
                    try:
                        conn.execute(stmt)
                    except sqlite3.OperationalError:
                        pass
                conn.commit()

    def _ensure_extensions(self) -> None:
        with self._connect() as conn:
            mcols = _table_columns(conn, "manufacturing_requests")
            for col, ddl in [
                ("started_at", "ALTER TABLE manufacturing_requests ADD COLUMN started_at TEXT"),
                ("finished_at", "ALTER TABLE manufacturing_requests ADD COLUMN finished_at TEXT"),
                ("output_summary", "ALTER TABLE manufacturing_requests ADD COLUMN output_summary TEXT"),
                ("error_message", "ALTER TABLE manufacturing_requests ADD COLUMN error_message TEXT"),
            ]:
                if col not in mcols:
                    try:
                        conn.execute(ddl)
                    except sqlite3.OperationalError:
                        pass
            conn.execute(
                "UPDATE manufacturing_requests SET status = ? WHERE status = ?",
                (ManufacturingStatus.running.value, "in_progress"),
            )
            mtcols = _table_columns(conn, "meetings")
            for col, ddl in [
                ("transcript", "ALTER TABLE meetings ADD COLUMN transcript TEXT"),
                (
                    "extraction_draft_json",
                    "ALTER TABLE meetings ADD COLUMN extraction_draft_json TEXT",
                ),
                (
                    "extraction_status",
                    "ALTER TABLE meetings ADD COLUMN extraction_status TEXT DEFAULT 'none'",
                ),
                (
                    "extraction_confirmed_at",
                    "ALTER TABLE meetings ADD COLUMN extraction_confirmed_at TEXT",
                ),
            ]:
                if col not in mtcols:
                    try:
                        conn.execute(ddl)
                    except sqlite3.OperationalError:
                        pass
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    occurred_at TEXT NOT NULL,
                    action TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    actor TEXT NOT NULL DEFAULT 'anonymous',
                    detail_json TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS context_improvement_items (
                    id TEXT PRIMARY KEY,
                    source_triage_id TEXT REFERENCES triage_results(id) ON DELETE SET NULL,
                    story_id TEXT REFERENCES stories(id) ON DELETE SET NULL,
                    context_package_id TEXT REFERENCES context_packages(id) ON DELETE SET NULL,
                    manufacturing_request_id TEXT REFERENCES manufacturing_requests(id) ON DELETE SET NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    priority TEXT NOT NULL DEFAULT 'high',
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS decision_records (
                    id TEXT PRIMARY KEY,
                    decision_code TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    actor TEXT NOT NULL DEFAULT 'anonymous',
                    detail_json TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY,
                    artifact_kind TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    body_json TEXT,
                    actor TEXT NOT NULL DEFAULT 'anonymous',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sprints (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    roadmap_cycle_id TEXT REFERENCES roadmap_cycles(id) ON DELETE SET NULL,
                    starts_at TEXT,
                    ends_at TEXT,
                    capacity_notes TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sprint_commitments (
                    id TEXT PRIMARY KEY,
                    sprint_id TEXT NOT NULL REFERENCES sprints(id) ON DELETE CASCADE,
                    story_id TEXT NOT NULL REFERENCES stories(id) ON DELETE CASCADE,
                    sort_order INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE(sprint_id, story_id),
                    UNIQUE(story_id)
                )
                """
            )
            conn.commit()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def log_audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        *,
        actor: Optional[str] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> None:
        act = actor if actor is not None else get_actor()
        try:
            eid = _uid()
            ts = _now()
            dj = json.dumps(detail, ensure_ascii=False) if detail else None
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO audit_events (id, occurred_at, action, entity_type, entity_id, actor, detail_json)
                    VALUES (?,?,?,?,?,?,?)""",
                    (eid, ts, action, entity_type, entity_id, act, dj),
                )
                conn.commit()
        except Exception as e:
            logger.warning("audit_log_failed: %s", e)

    def list_audit_events(
        self,
        *,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100,
    ) -> list[AuditEventRead]:
        q = "SELECT * FROM audit_events WHERE 1=1"
        params: list[Any] = []
        if entity_type:
            q += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id:
            q += " AND entity_id = ?"
            params.append(entity_id)
        q += " ORDER BY occurred_at DESC LIMIT ?"
        params.append(min(limit, 500))
        with self._connect() as conn:
            rows = conn.execute(q, params).fetchall()
        out = []
        for r in rows:
            det: dict[str, Any] = {}
            if r["detail_json"]:
                try:
                    det = json.loads(r["detail_json"])
                except json.JSONDecodeError:
                    det = {}
            out.append(
                AuditEventRead(
                    id=r["id"],
                    occurred_at=datetime.fromisoformat(r["occurred_at"]),
                    action=r["action"],
                    entity_type=r["entity_type"],
                    entity_id=r["entity_id"],
                    actor=r["actor"],
                    detail=det,
                )
            )
        return out

    def record_decision(
        self,
        decision_code: str,
        summary: str,
        entity_type: str,
        entity_id: str,
        *,
        actor: Optional[str] = None,
        detail: Optional[dict[str, Any]] = None,
    ) -> DecisionRecordRead:
        act = actor if actor is not None else get_actor()
        did = _uid()
        ts = _now()
        dj = json.dumps(detail, ensure_ascii=False) if detail else None
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO decision_records
                (id, decision_code, summary, entity_type, entity_id, actor, detail_json, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (did, decision_code[:32], summary[:2000], entity_type, entity_id, act, dj, ts),
            )
            conn.commit()
        self.log_audit(
            "decision_recorded",
            "decision_record",
            did,
            actor=act,
            detail={"decision_code": decision_code, "entity_type": entity_type},
        )
        return self.get_decision_record(did)

    def get_decision_record(self, decision_id: str) -> DecisionRecordRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM decision_records WHERE id = ?", (decision_id,)
            ).fetchone()
        if not row:
            raise KeyError("decision_record_not_found")
        det: dict[str, Any] = {}
        if row["detail_json"]:
            try:
                det = json.loads(row["detail_json"])
            except json.JSONDecodeError:
                det = {}
        return DecisionRecordRead(
            id=row["id"],
            decision_code=row["decision_code"],
            summary=row["summary"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            actor=row["actor"],
            detail=det,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_decision_records(
        self,
        *,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        decision_code: Optional[str] = None,
        limit: int = 100,
    ) -> list[DecisionRecordRead]:
        q = "SELECT id FROM decision_records WHERE 1=1"
        params: list[Any] = []
        if entity_type:
            q += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id:
            q += " AND entity_id = ?"
            params.append(entity_id)
        if decision_code:
            q += " AND decision_code = ?"
            params.append(decision_code)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(min(limit, 500))
        with self._connect() as conn:
            ids = [r["id"] for r in conn.execute(q, params).fetchall()]
        return [self.get_decision_record(i) for i in ids]

    def record_artifact(
        self,
        artifact_kind: str,
        entity_type: str,
        entity_id: str,
        title: str,
        *,
        body: Optional[dict[str, Any]] = None,
        actor: Optional[str] = None,
    ) -> ArtifactRead:
        act = actor if actor is not None else get_actor()
        aid = _uid()
        ts = _now()
        bj = json.dumps(body or {}, ensure_ascii=False)
        if len(bj) > 100_000:
            bj = json.dumps(
                {"_truncated": True, "approx_bytes": len(bj)}, ensure_ascii=False
            )
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO artifacts
                (id, artifact_kind, entity_type, entity_id, title, body_json, actor, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (aid, artifact_kind[:64], entity_type, entity_id, title[:500], bj, act, ts),
            )
            conn.commit()
        self.log_audit(
            "artifact_recorded",
            "artifact",
            aid,
            actor=act,
            detail={"artifact_kind": artifact_kind, "entity_type": entity_type},
        )
        return self.get_artifact(aid)

    def get_artifact(self, artifact_id: str) -> ArtifactRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM artifacts WHERE id = ?", (artifact_id,)
            ).fetchone()
        if not row:
            raise KeyError("artifact_not_found")
        body: dict[str, Any] = {}
        if row["body_json"]:
            try:
                body = json.loads(row["body_json"])
            except json.JSONDecodeError:
                body = {}
        return ArtifactRead(
            id=row["id"],
            artifact_kind=row["artifact_kind"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            title=row["title"],
            body=body,
            actor=row["actor"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_artifacts(
        self,
        *,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        artifact_kind: Optional[str] = None,
        limit: int = 100,
    ) -> list[ArtifactRead]:
        q = "SELECT id FROM artifacts WHERE 1=1"
        params: list[Any] = []
        if entity_type:
            q += " AND entity_type = ?"
            params.append(entity_type)
        if entity_id:
            q += " AND entity_id = ?"
            params.append(entity_id)
        if artifact_kind:
            q += " AND artifact_kind = ?"
            params.append(artifact_kind)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(min(limit, 500))
        with self._connect() as conn:
            ids = [r["id"] for r in conn.execute(q, params).fetchall()]
        return [self.get_artifact(i) for i in ids]

    @staticmethod
    def _coerce_extraction_draft(draft: dict[str, Any]) -> dict[str, Any]:
        out = dict(draft)
        items = list(out.get("proposed_items") or [])
        rev = dict(out.get("item_reviews") or {})
        for i in range(len(items)):
            k = str(i)
            if k not in rev:
                rev[k] = "pending"
        out["proposed_items"] = items
        out["item_reviews"] = rev
        return out

    def ensure_default_backlog_feature_id(self) -> str:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT f.id FROM features f
                JOIN delivery_phases p ON f.delivery_phase_id = p.id
                WHERE f.title = '__default_backlog__' LIMIT 1"""
            ).fetchone()
            if row:
                return row[0]
            ts = _now()
            cid = _uid()
            conn.execute(
                "INSERT INTO roadmap_cycles (id, name, created_at) VALUES (?,?,?)",
                (cid, "Default", ts),
            )
            pid = _uid()
            conn.execute(
                """INSERT INTO delivery_phases
                (id, roadmap_cycle_id, name, phase_kind, sort_order, created_at)
                VALUES (?,?,?,?,?,?)""",
                (pid, cid, "Discovery", PhaseKind.discovery.value, 0, ts),
            )
            fid = _uid()
            conn.execute(
                """INSERT INTO features
                (id, delivery_phase_id, title, description, sort_order, created_at)
                VALUES (?,?,?,?,?,?)""",
                (fid, pid, "__default_backlog__", "", 0, ts),
            )
            conn.commit()
            return fid

    # --- roadmap ---
    def create_roadmap_cycle(self, data: RoadmapCycleCreate) -> RoadmapCycleRead:
        rid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO roadmap_cycles (id, name, created_at) VALUES (?,?,?)",
                (rid, data.name, ts),
            )
            conn.commit()
        self.log_audit("created", "roadmap_cycle", rid, detail={"name": data.name})
        return self.get_roadmap_cycle(rid)

    def get_roadmap_cycle(self, cycle_id: str) -> RoadmapCycleRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM roadmap_cycles WHERE id = ?", (cycle_id,)
            ).fetchone()
        if not row:
            raise KeyError("roadmap_cycle_not_found")
        return RoadmapCycleRead(
            id=row["id"],
            name=row["name"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_roadmap_cycles(self) -> list[RoadmapCycleRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM roadmap_cycles ORDER BY created_at DESC"
            ).fetchall()
        return [
            RoadmapCycleRead(
                id=r["id"],
                name=r["name"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def create_delivery_phase(self, data: DeliveryPhaseCreate) -> DeliveryPhaseRead:
        self.get_roadmap_cycle(data.roadmap_cycle_id)
        pid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO delivery_phases
                (id, roadmap_cycle_id, name, phase_kind, sort_order, created_at)
                VALUES (?,?,?,?,?,?)""",
                (
                    pid,
                    data.roadmap_cycle_id,
                    data.name,
                    data.phase_kind.value,
                    data.sort_order,
                    ts,
                ),
            )
            conn.commit()
        self.log_audit(
            "created",
            "delivery_phase",
            pid,
            detail={"roadmap_cycle_id": data.roadmap_cycle_id, "name": data.name},
        )
        return self.get_delivery_phase(pid)

    def get_delivery_phase(self, phase_id: str) -> DeliveryPhaseRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM delivery_phases WHERE id = ?", (phase_id,)
            ).fetchone()
        if not row:
            raise KeyError("delivery_phase_not_found")
        return DeliveryPhaseRead(
            id=row["id"],
            roadmap_cycle_id=row["roadmap_cycle_id"],
            name=row["name"],
            phase_kind=PhaseKind(row["phase_kind"]),
            sort_order=row["sort_order"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_delivery_phases(self, cycle_id: str) -> list[DeliveryPhaseRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM delivery_phases WHERE roadmap_cycle_id = ? ORDER BY sort_order, created_at",
                (cycle_id,),
            ).fetchall()
        return [
            DeliveryPhaseRead(
                id=r["id"],
                roadmap_cycle_id=r["roadmap_cycle_id"],
                name=r["name"],
                phase_kind=PhaseKind(r["phase_kind"]),
                sort_order=r["sort_order"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def create_feature(self, data: FeatureCreate) -> FeatureRead:
        self.get_delivery_phase(data.delivery_phase_id)
        fid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO features
                (id, delivery_phase_id, title, description, sort_order, created_at)
                VALUES (?,?,?,?,?,?)""",
                (
                    fid,
                    data.delivery_phase_id,
                    data.title,
                    data.description,
                    data.sort_order,
                    ts,
                ),
            )
            conn.commit()
        self.log_audit(
            "created",
            "feature",
            fid,
            detail={"delivery_phase_id": data.delivery_phase_id, "title": data.title},
        )
        return self.get_feature(fid)

    def get_feature(self, feature_id: str) -> FeatureRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM features WHERE id = ?", (feature_id,)
            ).fetchone()
        if not row:
            raise KeyError("feature_not_found")
        return FeatureRead(
            id=row["id"],
            delivery_phase_id=row["delivery_phase_id"],
            title=row["title"],
            description=row["description"],
            sort_order=row["sort_order"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_features(self, delivery_phase_id: str) -> list[FeatureRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM features WHERE delivery_phase_id = ? ORDER BY sort_order, created_at",
                (delivery_phase_id,),
            ).fetchall()
        return [
            FeatureRead(
                id=r["id"],
                delivery_phase_id=r["delivery_phase_id"],
                title=r["title"],
                description=r["description"],
                sort_order=r["sort_order"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def create_story(self, data: StoryCreate) -> StoryRead:
        self.get_feature(data.feature_id)
        sid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO stories (id, feature_id, title, description, created_at)
                VALUES (?,?,?,?,?)""",
                (sid, data.feature_id, data.title, data.description, ts),
            )
            conn.commit()
        self.log_audit(
            "created",
            "story",
            sid,
            detail={"feature_id": data.feature_id, "title": data.title},
        )
        return self.get_story(sid)

    def create_story_on_default_backlog(self, title: str, description: str = "") -> StoryRead:
        fid = self.ensure_default_backlog_feature_id()
        return self.create_story(StoryCreate(feature_id=fid, title=title, description=description))

    def get_story(self, story_id: str) -> StoryRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM stories WHERE id = ?", (story_id,)
            ).fetchone()
        if not row:
            raise KeyError("story_not_found")
        return StoryRead(
            id=row["id"],
            feature_id=row["feature_id"],
            title=row["title"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_stories(self, feature_id: Optional[str] = None) -> list[StoryRead]:
        with self._connect() as conn:
            if feature_id:
                rows = conn.execute(
                    "SELECT * FROM stories WHERE feature_id = ? ORDER BY created_at DESC",
                    (feature_id,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM stories ORDER BY created_at DESC"
                ).fetchall()
        return [
            StoryRead(
                id=r["id"],
                feature_id=r["feature_id"],
                title=r["title"],
                description=r["description"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def roadmap_tree(self) -> list[dict[str, Any]]:
        """Nested dicts for dashboard: cycles → phases → features → stories."""

        out: list[dict[str, Any]] = []
        for c in self.list_roadmap_cycles():
            cdict: dict[str, Any] = {
                "cycle": c,
                "phases": [],
            }
            for p in self.list_delivery_phases(c.id):
                pdict = {
                    "phase": p,
                    "features": [],
                }
                for f in self.list_features(p.id):
                    pdict["features"].append(
                        {
                            "feature": f,
                            "stories": self.list_stories(f.id),
                        }
                    )
                cdict["phases"].append(pdict)
            out.append(cdict)
        return out

    def _sprint_row_to_read(self, row: sqlite3.Row) -> SprintRead:
        return SprintRead(
            id=row["id"],
            name=row["name"],
            roadmap_cycle_id=row["roadmap_cycle_id"],
            starts_at=(
                datetime.fromisoformat(row["starts_at"]) if row["starts_at"] else None
            ),
            ends_at=(
                datetime.fromisoformat(row["ends_at"]) if row["ends_at"] else None
            ),
            capacity_notes=row["capacity_notes"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def create_sprint(self, data: SprintCreate) -> SprintRead:
        if data.roadmap_cycle_id:
            self.get_roadmap_cycle(data.roadmap_cycle_id)
        sid = _uid()
        ts = _now()
        starts = data.starts_at.isoformat() if data.starts_at else None
        ends = data.ends_at.isoformat() if data.ends_at else None
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO sprints
                (id, name, roadmap_cycle_id, starts_at, ends_at, capacity_notes, created_at)
                VALUES (?,?,?,?,?,?,?)""",
                (
                    sid,
                    data.name,
                    data.roadmap_cycle_id,
                    starts,
                    ends,
                    data.capacity_notes,
                    ts,
                ),
            )
            conn.commit()
        self.log_audit("created", "sprint", sid, detail={"name": data.name})
        return self.get_sprint(sid)

    def get_sprint(self, sprint_id: str) -> SprintRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM sprints WHERE id = ?", (sprint_id,)
            ).fetchone()
        if not row:
            raise KeyError("sprint_not_found")
        return self._sprint_row_to_read(row)

    def list_sprints(self) -> list[SprintRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM sprints ORDER BY created_at DESC"
            ).fetchall()
        return [self._sprint_row_to_read(r) for r in rows]

    def story_has_approved_context_package(self, story_id: str) -> bool:
        with self._connect() as conn:
            r = conn.execute(
                "SELECT 1 FROM context_packages WHERE story_id = ? AND status = ? LIMIT 1",
                (story_id, PackageStatus.approved.value),
            ).fetchone()
        return r is not None

    def _latest_approved_package_id(self, story_id: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT id FROM context_packages WHERE story_id = ? AND status = ?
                ORDER BY version DESC LIMIT 1""",
                (story_id, PackageStatus.approved.value),
            ).fetchone()
        return row["id"] if row else None

    def _sprint_id_for_story(self, story_id: str) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT sprint_id FROM sprint_commitments WHERE story_id = ?",
                (story_id,),
            ).fetchone()
        return row["sprint_id"] if row else None

    def _commitment_row_to_read(self, row: sqlite3.Row, has_ap: bool) -> SprintCommitmentRead:
        return SprintCommitmentRead(
            id=row["id"],
            sprint_id=row["sprint_id"],
            story_id=row["story_id"],
            sort_order=row["sort_order"],
            story_title=row["story_title"],
            has_approved_context=has_ap,
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_sprint_commitment_read(self, commitment_id: str) -> SprintCommitmentRead:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT sc.*, s.title AS story_title
                FROM sprint_commitments sc
                JOIN stories s ON s.id = sc.story_id
                WHERE sc.id = ?""",
                (commitment_id,),
            ).fetchone()
        if not row:
            raise KeyError("commitment_not_found")
        ha = self.story_has_approved_context_package(row["story_id"])
        return self._commitment_row_to_read(row, ha)

    def sprint_board(self, sprint_id: str) -> SprintBoardRead:
        sp = self.get_sprint(sprint_id)
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT sc.*, s.title AS story_title
                FROM sprint_commitments sc
                JOIN stories s ON s.id = sc.story_id
                WHERE sc.sprint_id = ?
                ORDER BY sc.sort_order ASC, sc.created_at ASC""",
                (sprint_id,),
            ).fetchall()
        cm: list[SprintCommitmentRead] = []
        for r in rows:
            ha = self.story_has_approved_context_package(r["story_id"])
            cm.append(self._commitment_row_to_read(r, ha))
        return SprintBoardRead(sprint=sp, commitments=cm)

    def commit_story_to_sprint(
        self, sprint_id: str, body: SprintCommitStoryBody
    ) -> SprintCommitmentRead:
        self.get_sprint(sprint_id)
        self.get_story(body.story_id)
        has_pkg = self.story_has_approved_context_package(body.story_id)
        allow_override = body.allow_unapproved or _env_truthy(
            "CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT"
        )
        if not has_pkg and not allow_override:
            raise ValueError(
                "d8_gate: story needs an approved context package (set "
                "CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT=1 or pass allow_unapproved)"
            )
        other = self._sprint_id_for_story(body.story_id)
        if other and other != sprint_id:
            raise ValueError("story_already_committed_to_another_sprint")
        pkg_id = self._latest_approved_package_id(body.story_id)
        ts = _now()
        commitment_id: str
        is_new: bool
        with self._connect() as conn:
            hit = conn.execute(
                """SELECT id FROM sprint_commitments
                WHERE sprint_id = ? AND story_id = ?""",
                (sprint_id, body.story_id),
            ).fetchone()
            if hit:
                commitment_id = hit["id"]
                is_new = False
                conn.execute(
                    "UPDATE sprint_commitments SET sort_order = ? WHERE id = ?",
                    (body.sort_order, commitment_id),
                )
            else:
                commitment_id = _uid()
                is_new = True
                conn.execute(
                    """INSERT INTO sprint_commitments
                    (id, sprint_id, story_id, sort_order, created_at)
                    VALUES (?,?,?,?,?)""",
                    (commitment_id, sprint_id, body.story_id, body.sort_order, ts),
                )
            conn.commit()
        if is_new:
            st = self.get_story(body.story_id)
            self.record_decision(
                "D8",
                f"Sprint commitment: {st.title[:120]}",
                "sprint_commitment",
                commitment_id,
                detail={
                    "sprint_id": sprint_id,
                    "story_id": body.story_id,
                    "context_package_id": pkg_id,
                    "override_unapproved": bool(allow_override and not has_pkg),
                },
            )
            self.record_artifact(
                "sprint_commitment",
                "sprint",
                sprint_id,
                title=f"Committed: {st.title[:200]}",
                body={
                    "commitment_id": commitment_id,
                    "story_id": body.story_id,
                    "context_package_id": pkg_id,
                    "override_unapproved": bool(allow_override and not has_pkg),
                },
            )
            self.log_audit(
                "committed",
                "sprint_commitment",
                commitment_id,
                detail={"sprint_id": sprint_id, "story_id": body.story_id},
            )
        else:
            self.log_audit(
                "updated",
                "sprint_commitment",
                commitment_id,
                detail={
                    "sprint_id": sprint_id,
                    "story_id": body.story_id,
                    "sort_order": body.sort_order,
                },
            )
        return self.get_sprint_commitment_read(commitment_id)

    def remove_sprint_commitment(self, sprint_id: str, story_id: str) -> None:
        with self._connect() as conn:
            r = conn.execute(
                """SELECT id FROM sprint_commitments
                WHERE sprint_id = ? AND story_id = ?""",
                (sprint_id, story_id),
            ).fetchone()
            if not r:
                raise KeyError("commitment_not_found")
            cid = r["id"]
            conn.execute("DELETE FROM sprint_commitments WHERE id = ?", (cid,))
            conn.commit()
        self.log_audit(
            "removed",
            "sprint_commitment",
            cid,
            detail={"sprint_id": sprint_id, "story_id": story_id},
        )

    @staticmethod
    def allow_unapproved_sprint_commit_env() -> bool:
        return _env_truthy("CONTEXT_ALLOW_UNAPPROVED_SPRINT_COMMIT")

    def _row_to_package(self, row: sqlite3.Row, signs: list[sqlite3.Row]) -> ContextPackageRead:
        use_snapshot = (
            row["status"] == PackageStatus.approved.value
            and row["approved_snapshot_json"]
        )
        if use_snapshot:
            snap = json.loads(row["approved_snapshot_json"])
            biz = snap.get("business", {})
            tech = snap.get("technical", {})
            tst = snap.get("testing", {})
            ga = snap.get("gap_analysis", {})
        else:
            biz = json.loads(row["business_context"] or "{}")
            tech = json.loads(row["technical_approach"] or "{}")
            tst = json.loads(row["testing_contract"] or "{}")
            sec = sections_from_legacy_dicts(biz, tech, tst)
            ga = gap_analysis_dict(sec)

        return ContextPackageRead(
            id=row["id"],
            story_id=row["story_id"],
            version=row["version"],
            status=PackageStatus(row["status"]),
            readiness_score=row["readiness_score"],
            package_schema_version=int(row["package_schema_version"] or 2),
            business_context=biz,
            technical_approach=tech,
            testing_contract=tst,
            gap_analysis=ga if isinstance(ga, dict) else {},
            content_hash=row["content_hash"] if row["content_hash"] else None,
            approved_at=(
                datetime.fromisoformat(row["approved_at"])
                if row["approved_at"]
                else None
            ),
            created_at=datetime.fromisoformat(row["created_at"]),
            sign_offs=[
                SignOffRead(
                    role=SignOffRole(s["role"]),
                    signed_by=s["signed_by"],
                    signed_at=datetime.fromisoformat(s["signed_at"]),
                )
                for s in signs
            ],
        )

    def create_context_package(self, data: ContextPackageCreate) -> ContextPackageRead:
        self.get_story(data.story_id)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(version),0)+1 AS v FROM context_packages WHERE story_id = ?",
                (data.story_id,),
            ).fetchone()
            version = int(row["v"])
            pid = _uid()
            ts = _now()
            conn.execute(
                """INSERT INTO context_packages
                (id, story_id, version, status, readiness_score,
                business_context, technical_approach, testing_contract,
                package_schema_version, created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    pid,
                    data.story_id,
                    version,
                    PackageStatus.draft.value,
                    0.0,
                    "{}",
                    "{}",
                    "{}",
                    2,
                    ts,
                ),
            )
            conn.commit()
        self.log_audit(
            "created",
            "context_package",
            pid,
            detail={"story_id": data.story_id, "version": version},
        )
        return self.get_context_package(pid)

    def get_context_package(self, package_id: str) -> ContextPackageRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM context_packages WHERE id = ?", (package_id,)
            ).fetchone()
            if not row:
                raise KeyError("context_package_not_found")
            signs = conn.execute(
                "SELECT role, signed_by, signed_at FROM sign_offs WHERE context_package_id = ? ORDER BY signed_at",
                (package_id,),
            ).fetchall()
        return self._row_to_package(row, signs)

    def list_packages_for_story(self, story_id: str) -> list[ContextPackageRead]:
        with self._connect() as conn:
            ids = [
                r["id"]
                for r in conn.execute(
                    "SELECT id FROM context_packages WHERE story_id = ? ORDER BY version DESC",
                    (story_id,),
                ).fetchall()
            ]
        return [self.get_context_package(i) for i in ids]

    def update_context_package(
        self, package_id: str, data: ContextPackageUpdate
    ) -> ContextPackageRead:
        pkg = self.get_context_package(package_id)
        if pkg.status == PackageStatus.approved:
            raise ValueError("cannot_edit_approved_package")

        biz_d = pkg.business_context
        tech_d = pkg.technical_approach
        tst_d = pkg.testing_contract
        if data.sections:
            biz_d = data.sections.business_context
            tech_d = data.sections.technical_approach
            tst_d = data.sections.testing_contract

        sec = sections_from_legacy_dicts(biz_d, tech_d, tst_d)
        readiness = (
            data.readiness_score
            if data.readiness_score is not None
            else compute_readiness_v2(sec)
        )
        bj, tj, ttj = sections_to_storage_tuple(sec)

        status = pkg.status
        if status == PackageStatus.draft and readiness >= 70:
            status = PackageStatus.in_review

        with self._connect() as conn:
            conn.execute(
                """UPDATE context_packages SET
                business_context = ?, technical_approach = ?, testing_contract = ?,
                readiness_score = ?, status = ?, package_schema_version = ?
                WHERE id = ?""",
                (
                    bj,
                    tj,
                    ttj,
                    readiness,
                    status.value,
                    2,
                    package_id,
                ),
            )
            conn.commit()
        self.log_audit(
            "updated",
            "context_package",
            package_id,
            detail={"readiness_score": readiness, "status": status.value},
        )
        return self.get_context_package(package_id)

    def _approval_snapshot_payload_conn(
        self, conn: sqlite3.Connection, package_id: str
    ) -> tuple[str, str]:
        row = conn.execute(
            "SELECT business_context, technical_approach, testing_contract FROM context_packages WHERE id = ?",
            (package_id,),
        ).fetchone()
        if not row:
            raise KeyError("context_package_not_found")
        biz = json.loads(row["business_context"] or "{}")
        tech = json.loads(row["technical_approach"] or "{}")
        tst = json.loads(row["testing_contract"] or "{}")
        sec = sections_from_legacy_dicts(biz, tech, tst)
        ga = gap_analysis_dict(sec)
        payload = {
            "business": sec.business.model_dump(),
            "technical": sec.technical.model_dump(),
            "testing": sec.testing.model_dump(),
            "gap_analysis": ga,
            "schema_version": 2,
        }
        canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        return digest, json.dumps(payload, ensure_ascii=False)

    def add_sign_off(self, package_id: str, data: SignOffCreate) -> ContextPackageRead:
        pkg = self.get_context_package(package_id)
        if pkg.status == PackageStatus.approved:
            return pkg
        if pkg.status not in (PackageStatus.in_review, PackageStatus.draft):
            raise ValueError("package_not_signable")

        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO sign_offs (id, context_package_id, role, signed_by, signed_at)
                VALUES (?,?,?,?,?)
                ON CONFLICT(context_package_id, role) DO UPDATE SET
                signed_by = excluded.signed_by, signed_at = excluded.signed_at""",
                (_uid(), package_id, data.role.value, data.signed_by, ts),
            )
            roles = {
                SignOffRole(r["role"])
                for r in conn.execute(
                    "SELECT role FROM sign_offs WHERE context_package_id = ?",
                    (package_id,),
                ).fetchall()
            }
            if _sign_offs_satisfy_d7(roles):
                digest, snap = self._approval_snapshot_payload_conn(conn, package_id)
                conn.execute(
                    """UPDATE context_packages SET
                    status = ?, approved_at = ?, content_hash = ?, approved_snapshot_json = ?
                    WHERE id = ?""",
                    (
                        PackageStatus.approved.value,
                        ts,
                        digest,
                        snap,
                        package_id,
                    ),
                )
            conn.commit()
        self.log_audit(
            "sign_off",
            "context_package",
            package_id,
            actor=data.signed_by,
            detail={"role": data.role.value},
        )
        out = self.get_context_package(package_id)
        if out.status == PackageStatus.approved:
            self.log_audit(
                "approved",
                "context_package",
                package_id,
                detail={"content_hash": out.content_hash},
            )
            self.record_decision(
                "D7",
                "Context package approved for manufacturing",
                "context_package",
                package_id,
                actor=data.signed_by,
                detail={
                    "content_hash": out.content_hash,
                    "version": out.version,
                    "story_id": out.story_id,
                },
            )
            self.record_artifact(
                "approved_context_package",
                "context_package",
                package_id,
                title=f"Approved context package v{out.version}",
                actor=data.signed_by,
                body={
                    "content_hash": out.content_hash,
                    "version": out.version,
                    "story_id": out.story_id,
                },
            )
        return out

    def create_gap(self, data: ContextGapCreate) -> ContextGapRead:
        self.get_story(data.story_id)
        if data.context_package_id:
            self.get_context_package(data.context_package_id)
        gid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO context_gaps
                (id, story_id, context_package_id, description, gap_type, severity, meeting_hint, resolved, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    gid,
                    data.story_id,
                    data.context_package_id,
                    data.description,
                    data.gap_type,
                    data.severity,
                    data.meeting_hint,
                    0,
                    ts,
                ),
            )
            conn.commit()
        self.log_audit("created", "context_gap", gid, detail={"story_id": data.story_id})
        return self.get_gap(gid)

    def get_gap(self, gap_id: str) -> ContextGapRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM context_gaps WHERE id = ?", (gap_id,)
            ).fetchone()
        if not row:
            raise KeyError("gap_not_found")
        return ContextGapRead(
            id=row["id"],
            story_id=row["story_id"],
            context_package_id=row["context_package_id"],
            description=row["description"],
            gap_type=row["gap_type"],
            severity=row["severity"],
            meeting_hint=row["meeting_hint"],
            resolved=bool(row["resolved"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_gaps(
        self, story_id: Optional[str] = None, unresolved_only: bool = False
    ) -> list[ContextGapRead]:
        q = "SELECT * FROM context_gaps WHERE 1=1"
        params: list[Any] = []
        if story_id:
            q += " AND story_id = ?"
            params.append(story_id)
        if unresolved_only:
            q += " AND resolved = 0"
        q += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(q, params).fetchall()
        return [
            ContextGapRead(
                id=r["id"],
                story_id=r["story_id"],
                context_package_id=r["context_package_id"],
                description=r["description"],
                gap_type=r["gap_type"],
                severity=r["severity"],
                meeting_hint=r["meeting_hint"],
                resolved=bool(r["resolved"]),
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def resolve_gap(self, gap_id: str) -> ContextGapRead:
        with self._connect() as conn:
            conn.execute(
                "UPDATE context_gaps SET resolved = 1 WHERE id = ?", (gap_id,)
            )
            conn.commit()
        self.log_audit("resolved", "context_gap", gap_id)
        return self.get_gap(gap_id)

    def submit_manufacturing(
        self, package_id: str, data: ManufacturingSubmit
    ) -> ManufacturingRead:
        pkg = self.get_context_package(package_id)
        if pkg.status != PackageStatus.approved:
            raise ValueError("d7_gate: package must be approved before manufacturing")
        mid = _uid()
        ts = _now()
        h = pkg.content_hash
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO manufacturing_requests
                (id, context_package_id, package_content_hash, submitted_by, submitted_at, status)
                VALUES (?,?,?,?,?,?)""",
                (mid, package_id, h, data.submitted_by, ts, ManufacturingStatus.queued.value),
            )
            conn.commit()
        self.log_audit(
            "submitted",
            "manufacturing_request",
            mid,
            actor=data.submitted_by,
            detail={"context_package_id": package_id, "package_content_hash": h},
        )
        return self.get_manufacturing(mid)

    def _mfg_row_to_read(self, row: sqlite3.Row) -> ManufacturingRead:
        keys = set(row.keys())
        raw_st = row["status"]
        try:
            st = ManufacturingStatus(_normalize_mfg_status(str(raw_st)))
        except ValueError:
            st = ManufacturingStatus.queued
        started = row["started_at"] if "started_at" in keys else None
        finished = row["finished_at"] if "finished_at" in keys else None
        out = row["output_summary"] if "output_summary" in keys else None
        err = row["error_message"] if "error_message" in keys else None
        return ManufacturingRead(
            id=row["id"],
            context_package_id=row["context_package_id"],
            package_content_hash=row["package_content_hash"],
            submitted_by=row["submitted_by"],
            submitted_at=datetime.fromisoformat(row["submitted_at"]),
            status=st,
            started_at=datetime.fromisoformat(started) if started else None,
            finished_at=datetime.fromisoformat(finished) if finished else None,
            output_summary=out,
            error_message=err,
        )

    def get_manufacturing_row(self, request_id: str) -> sqlite3.Row:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM manufacturing_requests WHERE id = ?", (request_id,)
            ).fetchone()
        if not row:
            raise KeyError("manufacturing_not_found")
        return row

    def get_manufacturing(self, request_id: str) -> ManufacturingRead:
        return self._mfg_row_to_read(self.get_manufacturing_row(request_id))

    def update_manufacturing_status(
        self,
        request_id: str,
        status: ManufacturingStatus,
        *,
        started: bool = False,
        finished: bool = False,
        output_summary: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        ts = _now()
        with self._connect() as conn:
            parts = ["status = ?"]
            params: list[Any] = [status.value]
            if started:
                parts.append("started_at = ?")
                params.append(ts)
            if finished:
                parts.append("finished_at = ?")
                params.append(ts)
            if output_summary is not None:
                parts.append("output_summary = ?")
                params.append(output_summary)
            if error_message is not None:
                parts.append("error_message = ?")
                params.append(error_message)
            params.append(request_id)
            conn.execute(
                f"UPDATE manufacturing_requests SET {', '.join(parts)} WHERE id = ?",
                params,
            )
            conn.commit()
        self.log_audit(
            "status_changed",
            "manufacturing_request",
            request_id,
            detail={"status": status.value},
        )

    def list_manufacturing_for_package(self, package_id: str) -> list[ManufacturingRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM manufacturing_requests WHERE context_package_id = ? ORDER BY submitted_at DESC",
                (package_id,),
            ).fetchall()
        return [self._mfg_row_to_read(r) for r in rows]

    def submit_triage(self, request_id: str, data: TriageSubmit) -> TriageRead:
        m = self.get_manufacturing(request_id)
        if m.status == ManufacturingStatus.completed:
            raise ValueError("already_triaged")
        if m.status == ManufacturingStatus.failed:
            raise ValueError("manufacturing_failed")
        if m.status == ManufacturingStatus.running:
            raise ValueError("manufacturing_running")
        if m.status not in (
            ManufacturingStatus.awaiting_triage,
            ManufacturingStatus.queued,
        ):
            raise ValueError("not_ready_for_triage")
        tid = _uid()
        ts = _now()
        pkg = self.get_context_package(m.context_package_id)
        story_id = pkg.story_id
        improvement_id: Optional[str] = None
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO triage_results
                (id, manufacturing_request_id, queue, feedback, created_at)
                VALUES (?,?,?,?,?)""",
                (tid, request_id, data.queue.value, data.feedback, ts),
            )
            conn.execute(
                "UPDATE manufacturing_requests SET status = ? WHERE id = ?",
                (ManufacturingStatus.completed.value, request_id),
            )
            if data.queue in (TriageQueue.Q2, TriageQueue.Q3):
                improvement_id = _uid()
                pr = "high" if data.queue == TriageQueue.Q3 else "medium"
                title = f"{data.queue.value} triage: context follow-up"
                conn.execute(
                    """INSERT INTO context_improvement_items
                    (id, source_triage_id, story_id, context_package_id, manufacturing_request_id,
                    title, description, priority, status, created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (
                        improvement_id,
                        tid,
                        story_id,
                        m.context_package_id,
                        request_id,
                        title,
                        data.feedback[:4000],
                        pr,
                        "open",
                        ts,
                    ),
                )
            conn.commit()
        self.log_audit(
            "submitted",
            "triage",
            tid,
            detail={
                "queue": data.queue.value,
                "manufacturing_request_id": request_id,
            },
        )
        if improvement_id:
            self.log_audit(
                "created",
                "context_improvement_item",
                improvement_id,
                detail={"source_triage_id": tid, "queue": data.queue.value},
            )
        self.record_decision(
            "D10",
            f"Triage classification: {data.queue.value}",
            "manufacturing_request",
            request_id,
            detail={
                "triage_id": tid,
                "queue": data.queue.value,
                "feedback_preview": data.feedback[:500],
            },
        )
        self.record_artifact(
            "triage_result",
            "manufacturing_request",
            request_id,
            title=f"Triage {data.queue.value}",
            body={
                "triage_id": tid,
                "queue": data.queue.value,
                "feedback": data.feedback[:8000],
            },
        )
        return self.get_triage(tid)

    def get_triage(self, triage_id: str) -> TriageRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM triage_results WHERE id = ?", (triage_id,)
            ).fetchone()
        if not row:
            raise KeyError("triage_not_found")
        return TriageRead(
            id=row["id"],
            manufacturing_request_id=row["manufacturing_request_id"],
            queue=TriageQueue(row["queue"]),
            feedback=row["feedback"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_latest_triage_for_request(self, request_id: str) -> Optional[TriageRead]:
        with self._connect() as conn:
            row = conn.execute(
                """SELECT * FROM triage_results WHERE manufacturing_request_id = ?
                ORDER BY created_at DESC LIMIT 1""",
                (request_id,),
            ).fetchone()
        if not row:
            return None
        return TriageRead(
            id=row["id"],
            manufacturing_request_id=row["manufacturing_request_id"],
            queue=TriageQueue(row["queue"]),
            feedback=row["feedback"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _meeting_row_to_read(self, row: sqlite3.Row) -> MeetingRead:
        keys = set(row.keys())
        sched = (
            datetime.fromisoformat(row["scheduled_at"]) if row["scheduled_at"] else None
        )
        transcript = row["transcript"] if "transcript" in keys else None
        ext_raw = row["extraction_draft_json"] if "extraction_draft_json" in keys else None
        draft: dict[str, Any] = {}
        if ext_raw:
            try:
                draft = json.loads(ext_raw)
            except json.JSONDecodeError:
                draft = {}
        ext_status = (
            row["extraction_status"] if "extraction_status" in keys else "none"
        ) or "none"
        conf = row["extraction_confirmed_at"] if "extraction_confirmed_at" in keys else None
        return MeetingRead(
            id=row["id"],
            meeting_type=MeetingTypeRef(row["meeting_type"]),
            title=row["title"] or "",
            scheduled_at=sched,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            transcript=transcript,
            extraction_status=ext_status,
            extraction_draft=draft,
            extraction_confirmed_at=(
                datetime.fromisoformat(conf) if conf else None
            ),
        )

    def create_meeting(self, data: MeetingCreate) -> MeetingRead:
        mid = _uid()
        ts = _now()
        sched = data.scheduled_at.isoformat() if data.scheduled_at else None
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO meetings (id, meeting_type, title, scheduled_at, status, created_at)
                VALUES (?,?,?,?,?,?)""",
                (mid, data.meeting_type.value, data.title, sched, "planned", ts),
            )
            conn.commit()
        self.log_audit(
            "created",
            "meeting",
            mid,
            detail={"meeting_type": data.meeting_type.value, "title": data.title},
        )
        return self.get_meeting(mid)

    def get_meeting(self, meeting_id: str) -> MeetingRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
            ).fetchone()
        if not row:
            raise KeyError("meeting_not_found")
        return self._meeting_row_to_read(row)

    def list_meetings(self) -> list[MeetingRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM meetings ORDER BY created_at DESC"
            ).fetchall()
        return [self._meeting_row_to_read(r) for r in rows]

    def set_meeting_transcript(self, meeting_id: str, data: MeetingTranscriptUpdate) -> MeetingRead:
        self.get_meeting(meeting_id)
        with self._connect() as conn:
            conn.execute(
                """UPDATE meetings SET transcript = ?, extraction_status = 'none',
                extraction_draft_json = NULL, extraction_confirmed_at = NULL
                WHERE id = ?""",
                (data.text, meeting_id),
            )
            conn.commit()
        self.log_audit("transcript_saved", "meeting", meeting_id)
        return self.get_meeting(meeting_id)

    def run_meeting_extraction_stub(self, meeting_id: str) -> MeetingRead:
        m = self.get_meeting(meeting_id)
        if not m.transcript:
            raise ValueError("meeting_has_no_transcript")
        raw = extract_transcript_auto(m.transcript)
        draft = self._coerce_extraction_draft(raw)
        with self._connect() as conn:
            conn.execute(
                """UPDATE meetings SET extraction_draft_json = ?, extraction_status = 'draft',
                status = 'extraction_pending'
                WHERE id = ?""",
                (json.dumps(draft, ensure_ascii=False), meeting_id),
            )
            conn.commit()
        self.log_audit(
            "extraction_drafted",
            "meeting",
            meeting_id,
            detail={"extractor": draft.get("extractor"), "n_items": len(draft.get("proposed_items") or [])},
        )
        return self.get_meeting(meeting_id)

    def set_meeting_extraction_item_review(
        self,
        meeting_id: str,
        item_index: int,
        decision: str,
        *,
        actor: str = "anonymous",
    ) -> MeetingRead:
        if decision not in ("accept", "reject"):
            raise ValueError("invalid_decision")
        m = self.get_meeting(meeting_id)
        if m.extraction_status != "draft":
            raise ValueError("no_active_draft")
        draft = dict(m.extraction_draft)
        items = list(draft.get("proposed_items") or [])
        if item_index < 0 or item_index >= len(items):
            raise ValueError("invalid_item_index")
        rev = dict(draft.get("item_reviews") or {})
        rev[str(item_index)] = "accepted" if decision == "accept" else "rejected"
        draft["item_reviews"] = rev
        with self._connect() as conn:
            conn.execute(
                "UPDATE meetings SET extraction_draft_json = ? WHERE id = ?",
                (json.dumps(draft, ensure_ascii=False), meeting_id),
            )
            conn.commit()
        self.log_audit(
            "extraction_item_reviewed",
            "meeting",
            meeting_id,
            actor=actor,
            detail={"item_index": item_index, "decision": decision},
        )
        return self.get_meeting(meeting_id)

    def meeting_extraction_accept_all(self, meeting_id: str) -> MeetingRead:
        m = self.get_meeting(meeting_id)
        if m.extraction_status != "draft":
            raise ValueError("no_active_draft")
        draft = self._coerce_extraction_draft(dict(m.extraction_draft))
        rev = {str(i): "accepted" for i in range(len(draft.get("proposed_items") or []))}
        draft["item_reviews"] = rev
        with self._connect() as conn:
            conn.execute(
                "UPDATE meetings SET extraction_draft_json = ? WHERE id = ?",
                (json.dumps(draft, ensure_ascii=False), meeting_id),
            )
            conn.commit()
        self.log_audit("extraction_accept_all", "meeting", meeting_id)
        return self.get_meeting(meeting_id)

    def confirm_meeting_extraction(
        self, meeting_id: str, data: MeetingExtractionConfirm
    ) -> MeetingRead:
        m = self.get_meeting(meeting_id)
        if m.extraction_status != "draft":
            raise ValueError("no_draft_to_confirm")
        draft = dict(m.extraction_draft)
        items = list(draft.get("proposed_items") or [])
        rev = draft.get("item_reviews") or {}

        if data.accepted_indices:
            picked = []
            for i in data.accepted_indices:
                if isinstance(i, int) and 0 <= i < len(items):
                    picked.append(items[i])
            payload = {
                **draft,
                "confirmed_items": picked,
                "confirmed": True,
            }
        elif rev:
            draft = self._coerce_extraction_draft(draft)
            rev = draft["item_reviews"]
            for i in range(len(items)):
                if rev.get(str(i), "pending") == "pending":
                    raise ValueError("extraction_items_pending_review")
            confirmed = [
                items[i]
                for i in range(len(items))
                if rev.get(str(i)) == "accepted"
            ]
            payload = {
                **draft,
                "confirmed_items": confirmed,
                "confirmed": True,
            }
        else:
            payload = {
                **draft,
                "confirmed_items": items,
                "confirmed": True,
            }
        act = get_actor()
        ci = payload.get("confirmed_items") or []
        preview = [
            {"type": x.get("type"), "text": (x.get("text") or "")[:400]}
            for x in ci[:20]
            if isinstance(x, dict)
        ]
        self.record_decision(
            "D4",
            "Meeting extraction signed off for downstream use",
            "meeting",
            meeting_id,
            actor=act,
            detail={
                "n_confirmed": len(ci),
                "extractor": payload.get("extractor"),
            },
        )
        self.record_artifact(
            "meeting_extraction_confirmed",
            "meeting",
            meeting_id,
            title="Confirmed meeting extraction",
            actor=act,
            body={
                "extractor": payload.get("extractor"),
                "n_confirmed": len(ci),
                "items_preview": preview,
            },
        )
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """UPDATE meetings SET extraction_draft_json = ?, extraction_status = 'confirmed',
                extraction_confirmed_at = ?, status = 'extraction_confirmed'
                WHERE id = ?""",
                (json.dumps(payload, ensure_ascii=False), ts, meeting_id),
            )
            conn.commit()
        self.log_audit(
            "extraction_confirmed",
            "meeting",
            meeting_id,
            actor=act,
            detail={"n_confirmed": len(ci)},
        )
        return self.get_meeting(meeting_id)

    def list_improvement_items(
        self, *, status: Optional[str] = "open", limit: int = 200
    ) -> list[ImprovementItemRead]:
        q = "SELECT * FROM context_improvement_items WHERE 1=1"
        params: list[Any] = []
        if status:
            q += " AND status = ?"
            params.append(status)
        q += " ORDER BY created_at DESC LIMIT ?"
        params.append(min(limit, 500))
        with self._connect() as conn:
            rows = conn.execute(q, params).fetchall()
        return [
            ImprovementItemRead(
                id=r["id"],
                source_triage_id=r["source_triage_id"],
                story_id=r["story_id"],
                context_package_id=r["context_package_id"],
                manufacturing_request_id=r["manufacturing_request_id"],
                title=r["title"],
                description=r["description"],
                priority=r["priority"],
                status=r["status"],
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    def resolve_improvement_item(self, item_id: str) -> ImprovementItemRead:
        with self._connect() as conn:
            conn.execute(
                "UPDATE context_improvement_items SET status = 'closed' WHERE id = ?",
                (item_id,),
            )
            conn.commit()
        row = self._get_improvement_row(item_id)
        self.log_audit("resolved", "context_improvement_item", item_id)
        return self._improvement_row_to_read(row)

    def _get_improvement_row(self, item_id: str) -> sqlite3.Row:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM context_improvement_items WHERE id = ?", (item_id,)
            ).fetchone()
        if not row:
            raise KeyError("improvement_item_not_found")
        return row

    def _improvement_row_to_read(self, row: sqlite3.Row) -> ImprovementItemRead:
        return ImprovementItemRead(
            id=row["id"],
            source_triage_id=row["source_triage_id"],
            story_id=row["story_id"],
            context_package_id=row["context_package_id"],
            manufacturing_request_id=row["manufacturing_request_id"],
            title=row["title"],
            description=row["description"],
            priority=row["priority"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )


_store: Optional[ContextStore] = None


def init_store(db_path: str | Path) -> ContextStore:
    global _store
    _store = ContextStore(db_path)
    return _store


def get_store() -> ContextStore:
    if _store is None:
        raise RuntimeError("ContextStore not initialized; call init_store first")
    return _store
