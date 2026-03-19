from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Optional

from src.context_platform.schemas import (
    ContextGapCreate,
    ContextGapRead,
    ContextPackageCreate,
    ContextPackageRead,
    ContextPackageUpdate,
    ManufacturingRead,
    ManufacturingStatus,
    ManufacturingSubmit,
    MeetingCreate,
    MeetingRead,
    MeetingTypeRef,
    PackageStatus,
    Phase,
    SignOffCreate,
    SignOffRead,
    SignOffRole,
    TriageQueue,
    TriageRead,
    TriageSubmit,
    WorkItemCreate,
    WorkItemRead,
)

REQUIRED_SIGN_OFF_ROLES = frozenset(
    {SignOffRole.context_engineer, SignOffRole.tech_lead, SignOffRole.product_owner}
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uid() -> str:
    return str(uuid.uuid4())


SCHEMA = """
CREATE TABLE IF NOT EXISTS work_items (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    phase TEXT NOT NULL DEFAULT 'discovery',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS context_packages (
    id TEXT PRIMARY KEY,
    work_item_id TEXT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL DEFAULT 'draft',
    readiness_score REAL NOT NULL DEFAULT 0,
    business_context TEXT NOT NULL DEFAULT '{}',
    technical_approach TEXT NOT NULL DEFAULT '{}',
    testing_contract TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    UNIQUE(work_item_id, version)
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
    work_item_id TEXT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
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
    submitted_by TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
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
    created_at TEXT NOT NULL
);
"""


def _compute_readiness(business: dict, technical: dict, testing: dict) -> float:
    score = 0.0
    if business and len(str(business).strip()) > 2:
        score += 33.33
    if technical and len(str(technical).strip()) > 2:
        score += 33.33
    if testing and len(str(testing).strip()) > 2:
        score += 33.34
    return round(min(100.0, score), 1)


class ContextStore:
    def __init__(self, db_path: str | Path) -> None:
        self._path = Path(db_path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(SCHEMA)
            conn.commit()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    # --- work items ---
    def create_work_item(self, data: WorkItemCreate) -> WorkItemRead:
        wid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO work_items (id, title, description, phase, created_at) VALUES (?,?,?,?,?)",
                (wid, data.title, data.description, data.phase.value, ts),
            )
            conn.commit()
        return self.get_work_item(wid)

    def get_work_item(self, work_item_id: str) -> WorkItemRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM work_items WHERE id = ?", (work_item_id,)
            ).fetchone()
        if not row:
            raise KeyError("work_item_not_found")
        return WorkItemRead(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            phase=Phase(row["phase"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_work_items(self) -> list[WorkItemRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM work_items ORDER BY created_at DESC"
            ).fetchall()
        return [
            WorkItemRead(
                id=r["id"],
                title=r["title"],
                description=r["description"],
                phase=Phase(r["phase"]),
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    # --- context packages ---
    def create_context_package(self, data: ContextPackageCreate) -> ContextPackageRead:
        self.get_work_item(data.work_item_id)
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(version),0)+1 AS v FROM context_packages WHERE work_item_id = ?",
                (data.work_item_id,),
            ).fetchone()
            version = int(row["v"])
            pid = _uid()
            ts = _now()
            conn.execute(
                """INSERT INTO context_packages
                (id, work_item_id, version, status, readiness_score, business_context, technical_approach, testing_contract, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (pid, data.work_item_id, version, PackageStatus.draft.value, 0.0, "{}", "{}", "{}", ts),
            )
            conn.commit()
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
        return ContextPackageRead(
            id=row["id"],
            work_item_id=row["work_item_id"],
            version=row["version"],
            status=PackageStatus(row["status"]),
            readiness_score=row["readiness_score"],
            business_context=json.loads(row["business_context"] or "{}"),
            technical_approach=json.loads(row["technical_approach"] or "{}"),
            testing_contract=json.loads(row["testing_contract"] or "{}"),
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

    def list_packages_for_work_item(self, work_item_id: str) -> list[ContextPackageRead]:
        with self._connect() as conn:
            ids = [
                r["id"]
                for r in conn.execute(
                    "SELECT id FROM context_packages WHERE work_item_id = ? ORDER BY version DESC",
                    (work_item_id,),
                ).fetchall()
            ]
        return [self.get_context_package(i) for i in ids]

    def update_context_package(
        self, package_id: str, data: ContextPackageUpdate
    ) -> ContextPackageRead:
        pkg = self.get_context_package(package_id)
        if pkg.status == PackageStatus.approved:
            raise ValueError("cannot_edit_approved_package")

        business = pkg.business_context
        technical = pkg.technical_approach
        testing = pkg.testing_contract
        if data.sections:
            business = data.sections.business_context
            technical = data.sections.technical_approach
            testing = data.sections.testing_contract

        readiness = data.readiness_score
        if readiness is None and data.sections is not None:
            readiness = _compute_readiness(business, technical, testing)
        elif readiness is None:
            readiness = pkg.readiness_score

        status = pkg.status
        if status == PackageStatus.draft and readiness and readiness >= 70:
            status = PackageStatus.in_review

        with self._connect() as conn:
            conn.execute(
                """UPDATE context_packages SET
                business_context = ?, technical_approach = ?, testing_contract = ?,
                readiness_score = ?, status = ?
                WHERE id = ?""",
                (
                    json.dumps(business),
                    json.dumps(technical),
                    json.dumps(testing),
                    readiness,
                    status.value,
                    package_id,
                ),
            )
            conn.commit()
        return self.get_context_package(package_id)

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
                r["role"]
                for r in conn.execute(
                    "SELECT role FROM sign_offs WHERE context_package_id = ?",
                    (package_id,),
                ).fetchall()
            }
            if REQUIRED_SIGN_OFF_ROLES.issubset({SignOffRole(r) for r in roles}):
                conn.execute(
                    "UPDATE context_packages SET status = ? WHERE id = ?",
                    (PackageStatus.approved.value, package_id),
                )
            conn.commit()
        return self.get_context_package(package_id)

    # --- gaps ---
    def create_gap(self, data: ContextGapCreate) -> ContextGapRead:
        self.get_work_item(data.work_item_id)
        if data.context_package_id:
            self.get_context_package(data.context_package_id)
        gid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO context_gaps
                (id, work_item_id, context_package_id, description, gap_type, severity, meeting_hint, resolved, created_at)
                VALUES (?,?,?,?,?,?,?,?,?)""",
                (
                    gid,
                    data.work_item_id,
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
            work_item_id=row["work_item_id"],
            context_package_id=row["context_package_id"],
            description=row["description"],
            gap_type=row["gap_type"],
            severity=row["severity"],
            meeting_hint=row["meeting_hint"],
            resolved=bool(row["resolved"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_gaps(
        self, work_item_id: Optional[str] = None, unresolved_only: bool = False
    ) -> list[ContextGapRead]:
        q = "SELECT * FROM context_gaps WHERE 1=1"
        params: list[Any] = []
        if work_item_id:
            q += " AND work_item_id = ?"
            params.append(work_item_id)
        if unresolved_only:
            q += " AND resolved = 0"
        q += " ORDER BY created_at DESC"
        with self._connect() as conn:
            rows = conn.execute(q, params).fetchall()
        return [
            ContextGapRead(
                id=r["id"],
                work_item_id=r["work_item_id"],
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
        return self.get_gap(gap_id)

    # --- manufacturing & triage (D9, D10) ---
    def submit_manufacturing(
        self, package_id: str, data: ManufacturingSubmit
    ) -> ManufacturingRead:
        pkg = self.get_context_package(package_id)
        if pkg.status != PackageStatus.approved:
            raise ValueError("d7_gate: package must be approved before manufacturing")
        mid = _uid()
        ts = _now()
        with self._connect() as conn:
            conn.execute(
                """INSERT INTO manufacturing_requests
                (id, context_package_id, submitted_by, submitted_at, status)
                VALUES (?,?,?,?,?)""",
                (mid, package_id, data.submitted_by, ts, ManufacturingStatus.queued.value),
            )
            conn.commit()
        return self.get_manufacturing(mid)

    def get_manufacturing(self, request_id: str) -> ManufacturingRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM manufacturing_requests WHERE id = ?", (request_id,)
            ).fetchone()
        if not row:
            raise KeyError("manufacturing_not_found")
        return ManufacturingRead(
            id=row["id"],
            context_package_id=row["context_package_id"],
            submitted_by=row["submitted_by"],
            submitted_at=datetime.fromisoformat(row["submitted_at"]),
            status=ManufacturingStatus(row["status"]),
        )

    def list_manufacturing_for_package(self, package_id: str) -> list[ManufacturingRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM manufacturing_requests WHERE context_package_id = ? ORDER BY submitted_at DESC",
                (package_id,),
            ).fetchall()
        return [
            ManufacturingRead(
                id=r["id"],
                context_package_id=r["context_package_id"],
                submitted_by=r["submitted_by"],
                submitted_at=datetime.fromisoformat(r["submitted_at"]),
                status=ManufacturingStatus(r["status"]),
            )
            for r in rows
        ]

    def submit_triage(self, request_id: str, data: TriageSubmit) -> TriageRead:
        self.get_manufacturing(request_id)
        tid = _uid()
        ts = _now()
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
            conn.commit()
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

    # --- meetings (M1–M7 registry) ---
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
        return self.get_meeting(mid)

    def get_meeting(self, meeting_id: str) -> MeetingRead:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
            ).fetchone()
        if not row:
            raise KeyError("meeting_not_found")
        sched = (
            datetime.fromisoformat(row["scheduled_at"]) if row["scheduled_at"] else None
        )
        return MeetingRead(
            id=row["id"],
            meeting_type=MeetingTypeRef(row["meeting_type"]),
            title=row["title"] or "",
            scheduled_at=sched,
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_meetings(self) -> list[MeetingRead]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM meetings ORDER BY created_at DESC"
            ).fetchall()
        out = []
        for r in rows:
            sched = datetime.fromisoformat(r["scheduled_at"]) if r["scheduled_at"] else None
            out.append(
                MeetingRead(
                    id=r["id"],
                    meeting_type=MeetingTypeRef(r["meeting_type"]),
                    title=r["title"] or "",
                    scheduled_at=sched,
                    status=r["status"],
                    created_at=datetime.fromisoformat(r["created_at"]),
                )
            )
        return out


_store: Optional[ContextStore] = None


def init_store(db_path: str | Path) -> ContextStore:
    global _store
    _store = ContextStore(db_path)
    return _store


def get_store() -> ContextStore:
    if _store is None:
        raise RuntimeError("ContextStore not initialized; call init_store first")
    return _store
