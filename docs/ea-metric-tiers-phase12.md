# EA metric tiers (Phase 12 observatory)

This document maps **dashboard/API aggregates** from `GET /api/context/analytics-summary` to a simple **three-tier** lens aligned with enterprise observability practice: *operational*, *process health*, *outcome / learning*.

## Tier 1 — Operational (is the spine moving?)

| Signal in API | Meaning |
|---------------|---------|
| `manufacturing_by_status` | Count of manufacturing jobs per `ManufacturingStatus` (queued, running, awaiting_triage, completed, failed). |
| `process_outbox_pending` | Unprocessed rows in `process_outbox` for the active project (automation backlog). |

**Use:** capacity, stuck jobs, worker health.

## Tier 2 — Process health (are we following the loop?)

| Signal in API | Meaning |
|---------------|---------|
| `triage_by_queue` | Volume of D10 outcomes (Q1 / Q2 / Q3) for the project. |
| `unresolved_gaps_by_severity_tier` | Open `context_gaps` grouped by `severity_tier` (blocking / degrading / minor). |
| `improvement_items_by_status` | D11 backlog counts by `status`. |
| `q2_with_diff_attachment` | Q2 triage rows whose `detail_json` includes a **`diff_attachment`** (Phase 12 feedback hub). |

**Use:** quality pressure, triage mix, whether feedback carries concrete evidence (diffs / refs).

## Tier 3 — Outcome / learning (is prediction and context quality improving?)

| Signal in API | Meaning |
|---------------|---------|
| `triage_prediction.match_rate` | Share of completed manufacturing requests where `predicted_triage_queue` matched the **latest** actual D10 queue (denominator: rows with a non-empty prediction). |

**Use:** calibrate heuristics and manufacturing gateway inputs; *not* a substitute for human review.

## Scope

All fields are **project-scoped** (cookie `context_project_id`, header `X-Context-Project`, or `CONTEXT_PROJECT_ID`). For cross-project roll-ups, export SQLite or move to a warehouse (see [postgres-notes.md](postgres-notes.md)).

## Related

- [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) Phase 12  
- Q2 optional diff: `TriageSubmit.diff_summary` / `diff_ref` / `diff_format` → `detail_json.diff_attachment`
