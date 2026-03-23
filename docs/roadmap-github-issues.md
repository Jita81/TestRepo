# Roadmap — GitHub issue breakdown

**Master implementation plan:** [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) · **README (quick links + status):** [README.md](../README.md)

**Progress (repo):** **A1**, **B1**, **B2**; **H1** stub manufacturing + file artifact; **D2** transcript + per-item review + optional OpenAI; **`audit_events`** + **`project_id`**; **D11** from Q2/Q3; **A2 (partial):** `decision_records` + `artifacts` (both **`project_id`**) with **D7/D8/D10/D4** wiring + **`X-Context-Actor`**; **C1 (partial):** `sprints` + `sprint_commitments`, D7 gate + env/UI override, dashboard + API; **C2 (partial):** D10 **structured triage** (`detail_json` + queue rules Q1/Q2/Q3, `GET /triage-results`); **A3 (partial):** before/after snapshots on package **update** / **sign_off** + gap **resolve**; optional **`CONTEXT_API_KEY`** for **`/api/*`**; **`projects`** table + **`project_id`** on roadmap/stories/meetings/sprints + **`X-Context-Project`** / cookie / **`CONTEXT_PROJECT_ID`**. **Phase 1 (README):** traceability rows scoped by project. **Phase 2:** optional dashboard session login (`CONTEXT_DASHBOARD_PASSWORD` + `CONTEXT_SESSION_SECRET`), `/context/login`, gated `GET`/`POST` under `/context`. **Phase 3:** manufacturing git adapter (`MANUFACTURING_GIT_URL`, optional patch + run cmd). **Phase 4:** **`meeting_agenda_items`** (optional `context_gap_id`), `GET/POST /meetings/{id}/agenda`, `POST /meetings/{id}/generate-agenda` from open gaps, dashboard block. **Phase 5:** **`POST /api/context/webhooks/scm/github`** (push/ping → `audit_events`, optional `story_id` / `context_project` query params, `CONTEXT_SCM_WEBHOOK_SECRET` + `X-Hub-Signature-256`). **Phase 6:** **`/health`** & **`/ready`**, **`python -m src.context_platform.cli`** (`migrate` / `seed` / `backup`), [docs/deploy-runbook.md](../docs/deploy-runbook.md), [docs/postgres-notes.md](../docs/postgres-notes.md), reference dataset **`prj_reference`**. **Decision agents:** shared **`llm_client`**, **`GET/POST /api/context/decision-agents`** ([decision-agent-fleet.md](decision-agent-fleet.md)). **Phase 7:** EA package extensions + gap contract fields (SQLite migration; D7 snapshot **schema v3**; API **`technical_context`** alias). **Phase 8:** meeting extraction **`unresolved[]`**, **`POST /meetings/{id}/unresolved-to-gaps`**, **`GET /meetings/pending-extraction-confirmation`**. **Phase 9:** **`process_outbox`**, **`process.*`** audits, **`GET/POST /api/context/process-outbox`**, env quick-path + optional note-only extraction auto-accept. **Forward roadmap:** [IMPLEMENTATION-PLAN.md](IMPLEMENTATION-PLAN.md) (Phases **10–14**). Remaining: **A2** (full D1–D12 UI per decision), **A3** (full entity diff coverage), OAuth/org-level auth, integrations, D3 heuristics/D12, PR automation, sprint dates/capacity depth, triage analytics depth, codebase index (**Phase 11**).

Use this document to create **Epics** (GitHub Milestones or parent Issues) and **child Issues**. Each block below is intended as **one issue**: title = first line; body = the rest of the block.

Suggested **labels** (create in the repo if missing): `epic`, `domain-model`, `context-graph`, `d7`, `d8`, `d9`, `d10`, `d11`, `meetings`, `integrations`, `codebase-intel`, `manufacturing`, `auth`, `docs`, `tech-debt`.

---

## Epic A — Domain model & context graph foundation

### Issue A1 — Roadmap hierarchy: quarter → phase → feature → story

**Labels:** `epic`, `domain-model`  
**Milestone:** Epic A (optional)

**Description**  
Replace flat `work_items` with a hierarchy aligned to the process architecture: quarterly roadmap items, phases (inception/discovery/delivery), features, and implementable stories. Stories should be the primary unit that holds links to context packages.

**Acceptance criteria**
- [ ] Data model supports roadmap item, phase, feature, story (names can differ but relationships are explicit).
- [ ] Migration path documented for existing SQLite data (or acceptable break for pre-1.0).
- [ ] API can CRUD at least story + list children/parents.
- [ ] README or `/docs` updated with entity diagram (mermaid or text).

---

### Issue A2 — Decision and artifact records (inputs → decisions → outputs)

**Labels:** `domain-model`, `context-graph`

**Description**  
Model **decisions** (D1–D12) and **artifacts** (documents, approvals, extractions) as first-class entities with timestamps and links to the context graph, so every approval and extraction is traceable.

**Acceptance criteria**
- [ ] `Decision` type references decision taxonomy (enum or table D1–D12).
- [ ] `Artifact` (or document) type with `produced_by_decision_id`, optional file/ref URL, status (draft/approved).
- [ ] API to list decisions/artifacts filtered by story or package.
- [ ] Audit fields: created_at, created_by (string ok until auth lands).

---

### Issue A3 — Audit log / provenance for graph mutations

**Labels:** `context-graph`, `tech-debt`

**Description**  
Append-only **event log** for changes to context graph entities (who/what/when, before/after snapshot or diff). Supports “provenance trails” required for D7 and meeting extractions.

**Acceptance criteria**
- [ ] Every create/update on core entities writes an audit event (or explicit opt-out list).
- [ ] API: fetch audit trail for a story, context package, or meeting extraction.
- [ ] Document retention approach (single DB table is fine for MVP).

---

## Epic B — Context package depth & D7 gate

### Issue B1 — Structured context package schema (replace opaque JSON)

**Labels:** `d7`, `domain-model`

**Description**  
Replace three free-form JSON blobs with **validated Pydantic (or JSON Schema) models** for: business context / rules, technical approach (components, files, patterns), testing contract (preconditions, postconditions, invariants, typed scenarios).

**Acceptance criteria**
- [ ] Schemas versioned (e.g. `schema_version` on package).
- [ ] API validation errors are actionable (field-level messages).
- [ ] Dashboard forms or JSON editor reflect structure (nested fields, not one textarea per section).

**Repo note (Phase 7):** `success_patterns_json`, `risks_dependencies_json`, `section_provenance_json` on `context_packages`; approved snapshot includes them with **`schema_version` 3**; REST body may use **`technical_context`** instead of **`technical_approach`**; dashboard adds JSON textareas for extensions.

---

### Issue B2 — D7 sign-offs: align roles with spec + immutable approved revision

**Labels:** `d7`

**Description**  
Architecture specifies Context Engineer, **Developer** (technical accuracy), Product Owner. Implement role model to match (merge Tech Lead + Developer if policy differs, but document the mapping). On full approval, **freeze** an immutable snapshot (content hash + version) eligible for manufacturing.

**Acceptance criteria**
- [ ] Sign-off roles match documented taxonomy or an explicit ADR explains mapping.
- [ ] Approved package revision is read-only; new edits require new version.
- [ ] Manufacturing submission references **exact** approved package version id.

---

### Issue B3 — Gap analysis artifact and completeness score from requirements

**Labels:** `d7`, `context-graph`

**Description**  
Persist **gap analysis** (missing fields, unresolved ContextGap links, optional LLM summary) and compute **readiness/completeness** from schema rules, not only non-empty JSON.

**Acceptance criteria**
- [ ] Completeness score derives from checklist / required subsections.
- [ ] `gap_analysis` stored or generated on demand with stable JSON shape.
- [ ] Dashboard shows blocking gaps before sign-off (not only percentage).

---

### Issue B4 — “Predicted queue outcome” placeholder for D7

**Labels:** `d7`, `tech-debt`

**Description**  
Add optional field on context package (manual or rule-based): predicted Q1/Q2/Q3 before manufacturing. Stub with heuristic or human entry until analytics model exists.

**Acceptance criteria**
- [ ] Field visible in API and UI with clear “experimental” or “manual” badge.
- [ ] Documented in process doc cross-link.

---

## Epic C — Delivery spine completion (D8–D11)

### Issue C1 — Sprint entity and D8 sprint commitment

**Labels:** `d8`, `domain-model`

**Description**  
Model **sprints** (e.g. 2-week), capacity, and **committed stories** only where context package is approved. Support manufacturing sequence ordering.

**Acceptance criteria**
- [ ] Sprint CRUD; attach stories with ordering.
- [ ] Validation: cannot commit story without approved package (configurable override flag for admins).
- [ ] API + minimal UI on dashboard.

---

### Issue C2 — Structured D10 triage (Q2 gaps, Q3 root cause)

**Labels:** `d10`

**Description**  
Extend triage beyond free-text: Q2 = structured gap list; Q3 = root cause category + narrative. Store as JSON schema.

**Acceptance criteria**
- [ ] Triage form/API validates by queue type (Q1 minimal; Q2 requires gaps; Q3 requires cause).
- [ ] Results queryable for analytics.

---

### Issue C3 — D11 context improvement backlog from triage

**Labels:** `d11`, `context-graph`

**Description**  
Create **Context Improvement Plan** / backlog items from Q3 (immediate) and Q2 patterns (aggregated). Link items to context packages or stories; optional auto-reopen ContextGap on Q3.

**Acceptance criteria**
- [ ] Entity: improvement item (priority, source_triage_id, target_package_id).
- [ ] List/filter API; dashboard section “Improvement backlog”.
- [ ] Document workflow in README.

---

## Epic D — Meeting intelligence (M1–M7)

### Issue D1 — Meeting model: agenda items + transcript + status

**Labels:** `meetings`, `domain-model`

**Description**  
Extend meetings beyond registry: **scheduled_at**, participants, **agenda items** (linked to ContextGap), **transcript** text or storage ref, status (planned/live/processed).

**Repo note (Phase 4):** `meeting_agenda_items` table + REST + dashboard; optional FK to `context_gaps`. Participants and richer meeting status not done.

**Acceptance criteria**
- [ ] Schema supports agenda ↔ gap links.
- [ ] API to attach transcript and transition status.
- [ ] Basic list/detail UI.

---

### Issue D2 — Batch meeting extraction pipeline (post-meeting)

**Labels:** `meetings`, `context-graph`

**Description**  
Upload or paste transcript → LLM proposes **decisions, requirements, action items** → **Meeting Extraction Document** draft → human approve/reject per item → write to graph. No “platform proposes; humans approve” violation.

**Acceptance criteria**
- [ ] Extraction job produces structured draft with per-line confidence optional.
- [ ] Review UI: accept/edit/reject each proposed item.
- [ ] Only accepted items create/ update graph entities; audit log records actor.

---

### Issue D3 — Gap-driven agenda generation (pre-meeting)

**Labels:** `meetings`

**Description**  
Given meeting type (M1–M7) and participants, generate **agenda** from open ContextGaps and missing package sections. Output as meeting agenda entity.

**Repo note (partial):** `POST /meetings/{id}/generate-agenda` seeds one agenda line per **unresolved gap** in the project (no M-type routing yet).

**Acceptance criteria**
- [ ] Rule set maps gap types / severities to meeting types (config table or code).
- [ ] API: `POST /meetings/{id}/generate-agenda` or equivalent.
- [ ] Unit tests for routing rules (at least 3 cases).

---

### Issue D4 — Real-time sufficiency dashboard (during meeting) — stretch

**Labels:** `meetings`, `tech-debt`

**Description**  
Stream or poll transcript chunks; score coverage of agenda items; facilitator UI (green/amber/red). Depends on stable transcript source.

**Acceptance criteria**
- [ ] Document integration options (Zoom bot vs manual paste stream).
- [ ] MVP: manual “mark agenda item addressed” if live NLP deferred.

---

## Epic E — Strategic & phase gates (D1–D3, D12)

### Issue E1 — D1–D3 entities and sign-off documents

**Labels:** `domain-model`, `docs`

**Description**  
Model quarterly roadmap (MoSCoW), phase plan, resource allocation matrix as **artifacts** with sign-off workflow (multi-party). Link roadmap items to features.

**Acceptance criteria**
- [ ] Entities or document types for each output in sign-off matrix (see architecture §06).
- [ ] Sign-off state machine (pending → signed).
- [ ] API read paths for reporting.

---

### Issue E2 — D12 phase / release approval

**Labels:** `domain-model`

**Description**  
Phase completion: aggregate story outcomes, test/coverage hooks (placeholders), triage distribution, **Phase Completion Report** artifact + sign-offs.

**Acceptance criteria**
- [ ] Phase completion checklist entity or generated report JSON.
- [ ] Sign-off roles per architecture (PO, Eng Lead, stakeholders as strings ok).
- [ ] Link to sprint/story data already modeled.

---

## Epic F — Integrations

### Issue F1 — GitHub webhook: PR and push events → context signals

**Labels:** `integrations`

**Description**  
Receive PR open/edit/merge; store events; optional comment on PR with context package link when manufacturing creates PR (stub ok).

**Repo note (Phase 5):** **Push** and **ping** JSON webhooks are accepted at **`POST /api/context/webhooks/scm/github`** with optional HMAC (`CONTEXT_SCM_WEBHOOK_SECRET`). Normalized per-PR rows and PR event types are **not** implemented yet.

**Acceptance criteria**
- [ ] Webhook endpoint + secret validation.
- [ ] Persist normalized event rows linked to repo/story when mapping exists.
- [ ] README: how to configure in a test repo.

---

### Issue F2 — PM tool sync (choose one first: Jira or Linear)

**Labels:** `integrations`

**Description**  
Bidirectional or one-way sync for stories and status; custom field for **context readiness** score.

**Acceptance criteria**
- [ ] OAuth or API token config documented.
- [ ] Map external story id ↔ internal story id.
- [ ] Push readiness score on package update (rate-limited).

---

### Issue F3 — Slack (or Teams) notifications for sign-off and agendas

**Labels:** `integrations`

**Description**  
Post agenda before meeting; notify when extraction ready for review; optional reaction/button sign-off (stretch).

**Acceptance criteria**
- [ ] Incoming webhook or bot token path documented.
- [ ] One concrete flow e2e in dev (e.g. “extraction ready” message).

---

## Epic G — Codebase intelligence

**Platform note:** Agent-facing retrieval should combine **semantic indexes** with **indexed regex / text search** (trigram-style and successors); see [agent-context-retrieval.md](agent-context-retrieval.md) and **§07** in [context-platform-process-architecture.md](context-platform-process-architecture.md).

### Issue G1 — Repository clone + static scan job

**Labels:** `codebase-intel`

**Description**  
On schedule or webhook, clone default branch, build file tree and simple dependency hints; attach **change impact** stub (co-change later).

**Acceptance criteria**
- [ ] Job runner (async task or separate worker script documented).
- [ ] Store snapshot ref tied to story or repo config entity.
- [ ] API to fetch “affected files” suggestion for a story (rule-based ok).

---

### Issue G2 — Pattern library + Pattern Review (M4) workflow

**Labels:** `codebase-intel`, `meetings`

**Description**  
Pattern entries (validated/pending); link patterns to technical approach section; meeting type M4 ties to review list.

**Acceptance criteria**
- [ ] Pattern CRUD + status (candidate/validated/deprecated).
- [ ] Link from context package technical section to pattern ids.
- [ ] Filter “patterns to review” for M4 agenda (manual list ok at first).

---

## Epic H — Manufacturing pipeline

### Issue H1 — Manufacturing job runner + status lifecycle

**Labels:** `manufacturing`, `d9`

**Description**  
Pluggable **manufacturing adapter**: queued → running → succeeded/failed; store logs and output artifact refs (branch name, PR URL). Stub adapter that creates empty branch or placeholder PR acceptable.

**Repo note:** Phase 3 adds an env-driven **git clone → optional `git apply` → optional shell command** path (`MANUFACTURING_*` in README). Recording **PR URL / branch** in the DB is still open.

**Acceptance criteria**
- [ ] State machine matches manufacturing_requests (extend if needed).
- [ ] Retry and idempotency rules documented (one job per package version default).
- [ ] Dashboard shows job status.

---

### Issue H2 — Context package → prompt / spec compiler

**Labels:** `manufacturing`

**Description**  
Deterministic build of LLM context from approved package version (sections + patterns + constraints). Version compiler with package `schema_version`.

**Acceptance criteria**
- [ ] Function or module `compile_context_package(package_id) -> str or structured messages`.
- [ ] Golden-file test with one fixture package.

---

## Epic I — Platform hardening

### Issue I1 — Authentication and multi-user roles

**Labels:** `auth`

**Description**  
Replace free-text `signed_by` with authenticated user; map users to roles (CE, TL, PO, Developer, etc.) per org/project.

**Acceptance criteria**
- [ ] Auth provider choice documented (e.g. OAuth2, SSO stub for dev).
- [ ] All sign-offs and audit events use user id.

---

### Issue I2 — Multi-tenant org / project scoping

**Labels:** `auth`, `domain-model`

**Description**  
Scope all entities by `org_id` / `project_id`; enforce in API.

**Acceptance criteria**
- [ ] Foreign keys or composite uniqueness; no cross-tenant reads.
- [ ] Tests for isolation.

---

### Issue I3 — Observability: structured logging + health checks

**Labels:** `tech-debt`

**Description**  
JSON logs, request ids, `/health` and `/ready` for DB; basic metrics hooks.

**Repo note (Phase 6):** **`GET /health`** (liveness) and **`GET /ready`** (SQLite ping via store) implemented. JSON logs / metrics hooks not done.

**Acceptance criteria**
- [ ] `/health` returns DB connectivity.
- [ ] README runbook section.

---

## Suggested first five issues to create (order)

1. **A1** — Roadmap hierarchy (unblocks everything else).  
2. **B1** — Structured package schema (unblocks real D7 and manufacturing compiler).  
3. **B2** — Immutable approved revision + version pin for manufacturing.  
4. **D2** — Batch meeting extraction (highest product differentiation after graph).  
5. **H1** — Manufacturing job runner (even with stub adapter) to complete D9 end-to-end.

---

## Optional: GitHub Projects columns

**Backlog → Ready → In progress → In review → Done**, with **custom fields**: `Epic` (select), `Decision type` (D1–D12), `Area` (API/UI/ML/Integrations).

---

*Derived from `docs/context-platform-process-architecture.md` and the current MVP in `src/context_platform/`.*
