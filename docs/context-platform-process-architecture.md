# Automated Agile

## Context Engineering Platform — Process Architecture

**Version 1.0 · March 2026 · Part of the Automated Agile Framework**

> A complete framework for AI-powered software delivery. Every activity in this platform exists to answer one question: does the right person have the right context to make the right decision at the right time?

---

## 01 — The Fundamental Model: Three Primitives

The entire process architecture is built from three primitives. Every activity in this platform exists to ensure the right person has the right context to make the right decision at the right time.

| Primitive | Definition | Examples |
|-----------|-----------|---------|
| **INPUTS** | Raw material that enters the system. Conversations, code, documents, decisions, observations. Anything that contains knowledge relevant to building software. | Meeting transcript, Git commit, Jira update, Slack thread, architecture diagram, stakeholder email, test result, production incident |
| **DECISIONS** | Judgment calls that require sufficient context. Every decision transforms inputs into direction. Decisions are the value-creating moments in the process. | Scope a feature, choose a technical approach, prioritise the backlog, approve a context package, triage generated code, sign off a release |
| **OUTPUTS** | Artifacts produced by decisions. Documents, code, context packages, approvals. Every output becomes an input to a downstream decision. | Context package, user story, acceptance criteria, generated code, triage classification, phase plan, sign-off document, pattern library entry |

### The Chain Rule

Every output from one decision becomes an input to the next.

The quality of upstream decisions determines the quality of downstream ones. This is why context engineering exists: to ensure every decision has sufficient, structured inputs before it is made.

### How Meetings Fit

Meetings are not administrative overhead. They are the primary mechanism for converting tacit human knowledge into explicit, structured context. Every meeting in this framework has three properties:

- **Context-gap-driven agenda** — The platform analyses what it knows and what it does not know, then generates an agenda of specific gaps to fill. Participants arrive knowing exactly what context is needed and why.
- **Real-time sufficiency feedback** — During the meeting, the platform assesses the transcript against the required context model. A live indicator shows whether each agenda item has been addressed with sufficient depth.
- **Structured extraction with human sign-off** — After the meeting, the platform extracts decisions, requirements, and action items into structured documents. A human reviews and signs off before anything enters the official context graph.

### The Quarterly Planning Cadence

All work is planned on a quarterly cycle. Within each quarter, work flows through three phases at the appropriate cadence.

| Cadence | Phase | Key Decisions | Outputs |
|---------|-------|--------------|---------|
| Quarterly | Inception | What do we build this quarter? What order? What resources? | Quarterly roadmap, MoSCoW priorities, phase plan |
| Per Phase (2–4 wk) | Discovery | How do we build each feature? What does done look like? What patterns apply? | Context packages, user stories, testing contracts |
| Per Sprint (2 wk) | Delivery | Is context sufficient to manufacture? Triage AI output. | Working code (Q1/Q2/Q3), triage feedback, pattern library updates |
| Daily | Delivery | What is blocked? What needs context improvement today? | Unblocked items, urgent context requests |

---

## 02 — The Decision Taxonomy: Twelve Decision Types

There are exactly twelve decision types in the agile delivery process. Every meeting, every review, every approval maps to one of these. The platform is designed to ensure every decision type has the context it needs.

### Strategic Decisions — Quarterly

#### D1 — Portfolio Prioritisation

*"Of everything we could build, what matters most this quarter?"*

- **Inputs required:** Business strategy, market conditions, customer feedback themes, technical debt severity scores, team capacity and velocity, prior quarter delivery vs. plan.
- **Decision maker:** Head of Product with Engineering leadership.
- **Output:** Prioritised quarterly roadmap with MoSCoW classification.
- **Sign-off:** Quarterly Roadmap Document — signed by Product, Engineering, and Business stakeholders.

#### D2 — Phase Breakdown

*"How do we break the quarter into testable, deliverable increments?"*

- **Inputs required:** Prioritised roadmap, dependency map between items, team structure, integration complexity, risk register.
- **Decision maker:** Delivery Lead with Product and Engineering.
- **Output:** Phase plan with 2–4 phases of 2–4 weeks each, with defined scope and success criteria.
- **Sign-off:** Phase Plan Document — signed by Delivery Lead and Product Owner.

#### D3 — T-Shirt Sizing & Resource Allocation

*"How big is each piece of work, and which teams own it?"*

- **Inputs required:** Roadmap items, product team boundaries, historical velocity data, team skill matrices, known technical constraints.
- **Decision maker:** Engineering Leads in Three Amigos with Product.
- **Output:** T-shirt sizes per item per team. Team assignments. Dependency identification.
- **Sign-off:** Resource Allocation Matrix — signed by Engineering Leads.

### Discovery Decisions — Per Phase

#### D4 — Story Decomposition

*"How do we break a feature into implementable stories with clear acceptance criteria?"*

- **Inputs required:** Feature description from roadmap, business rules from stakeholder meetings, existing user journeys, architectural constraints, similar past features.
- **Decision maker:** Product Owner with Tech Lead and Context Engineer (Three Amigos).
- **Output:** User stories with Given/When/Then acceptance criteria, each linked to parent feature.
- **Sign-off:** Story Definition Document — all three Amigos confirm each story is testable, implementable, and correctly scoped.

#### D5 — Technical Approach

*"Which code patterns, files, and architectural approach should each story use?"*

- **Inputs required:** Codebase analysis (affected files, dependency chain), success patterns, API contracts, data model, security requirements.
- **Decision maker:** Tech Lead, validated in Pattern Review meeting.
- **Output:** Technical section of the context package: components, files to modify/create, patterns to follow, error handling approach.
- **Sign-off:** Technical Approach section of Context Package — signed by Tech Lead.

#### D6 — Testing Contract

*"What are the preconditions, postconditions, invariants, and test scenarios?"*

- **Inputs required:** Acceptance criteria, business rules, technical approach, existing test coverage, edge cases identified in Three Amigos.
- **Decision maker:** Context Engineer with Tech Lead review.
- **Output:** Testing contract within context package: preconditions, postconditions, invariants, and typed test scenarios.
- **Sign-off:** Testing Contract section of Context Package — signed by Tech Lead.

#### D7 — Context Package Approval ⚠️ CRITICAL GATE

*"Is this context package complete enough to manufacture working software?"*

- **Inputs required:** Assembled context package with completeness score, gap analysis, predicted queue outcome, all provenance trails.
- **Decision maker:** Context Engineer (completeness), Developer (technical accuracy), Product Owner (business correctness).
- **Output:** Approved context package (version-pinned), ready for manufacturing pipeline.
- **Sign-off:** Three signatures: Context Engineer, Tech Lead, Product Owner.

> Decision 7 is the most important gate in the entire process. **Nothing enters the manufacturing pipeline without a signed-off context package.** This is where quality is assured—not after code is generated, but before.

### Delivery Decisions — Per Sprint / Per Story

#### D8 — Sprint Commitment

*"Which stories do we commit to this sprint?"*

- **Inputs required:** Context readiness scores for all candidate stories, team capacity, dependency status, prior sprint velocity.
- **Decision maker:** Development team with Product Owner.
- **Output:** Sprint backlog with manufacturing sequence. Only stories with approved context packages enter.
- **Sign-off:** Sprint Plan — team consensus in Sprint Planning.

#### D9 — Manufacturing Submission

*"Is this specific story ready to submit to the AI manufacturing pipeline right now?"*

- **Inputs required:** Approved context package, current codebase snapshot, manufacturing configuration, predicted queue outcome.
- **Decision maker:** Developer assigned to the story.
- **Output:** Manufacturing request submitted. Code generation begins.
- **Sign-off:** Developer clicks Submit — implicit sign-off that context has been reviewed.

#### D10 — Triage Classification

*"Is the generated code production-ready (Q1), a solid foundation needing human finishing (Q2), or unusable (Q3)?"*

- **Inputs required:** Generated code, test results, AI self-assessment, acceptance criteria from context package, coding standards.
- **Decision maker:** Developer who submitted the manufacturing request.
- **Output:** Queue classification with structured feedback. For Q2: specific gap list. For Q3: failure analysis with root cause.
- **Sign-off:** Triage Feedback Form — completed by developer, reviewed by Context Engineer.

#### D11 — Context Improvement Priority

*"Based on triage feedback, which context packages need improvement most urgently?"*

- **Inputs required:** Triage feedback from current sprint, queue distribution trends, differential analysis of Q2 code, Q3 failure patterns.
- **Decision maker:** Context Engineer, informed by Analytics Engine.
- **Output:** Prioritised improvement backlog: Q3 failures immediately, Q2 patterns weekly, Q1 successes monthly.
- **Sign-off:** Context Improvement Plan — reviewed in Context Retrospective.

#### D12 — Phase / Release Approval

*"Has this phase delivered its success criteria? Can we release?"*

- **Inputs required:** All stories in phase: acceptance criteria pass/fail, test coverage, queue distribution, defect count, performance benchmarks, stakeholder demo feedback.
- **Decision maker:** Product Owner with Engineering Lead.
- **Output:** Release approval or list of items required before release.
- **Sign-off:** Phase Completion Report — signed by PO, Engineering Lead, and relevant stakeholders.

---

## 03 — The Meeting Architecture: Seven Meeting Types

Every meeting in this framework is a context-generating machine. The platform curates each meeting's agenda based on known context gaps, monitors the conversation in real time for sufficiency, and extracts structured outputs for human review.

### How Meetings Are Curated

| When | What Happens |
|------|-------------|
| **Before** | The platform scans the Context Graph for gaps relevant to the meeting's purpose and participants. It produces a structured agenda of specific questions that need answers, sent to participants in advance. |
| **During** | The platform processes the transcript in real time and provides a live sufficiency dashboard. Green: covered. Amber: partially addressed. Red: not yet discussed. The facilitator uses this to steer conversation. |
| **After** | Within minutes of the meeting ending, the platform produces a Meeting Extraction Document. Automated extraction → facilitator review → participant sign-off. No item enters the Context Graph without human confirmation. |

> **The Documentation Contract:** No extracted item enters the Context Graph without human confirmation. **The platform proposes; humans approve.** This ensures the context library is trustworthy — every item has a human who vouches for its accuracy.

### M1 — Quarterly Planning

- **Phase:** Inception
- **Frequency:** Once per quarter — half-day or full-day session
- **Participants:** Product Leads, Engineering Leads, Business Stakeholders, Context Engineers
- **Decisions served:** D1 Portfolio Prioritisation · D2 Phase Breakdown · D3 T-Shirt Sizing
- **Platform agenda:** Prior quarter results, carry-over items, new backlog candidates, technical debt ranked by impact, team capacity, dependency conflicts.
- **Real-time monitoring:** Tracks whether each roadmap item has a clear business rationale, owner, MoSCoW classification, T-shirt size, and identified dependencies.
- **Outputs:** Quarterly Roadmap · Phase Plan · Resource Allocation Matrix

### M2 — Stakeholder Deep-Dive

- **Phase:** Inception / Discovery
- **Frequency:** As needed — typically 3–5 sessions during inception, ad-hoc during discovery
- **Participants:** Specific stakeholder(s) + Context Engineer. Optionally Product Owner
- **Decisions served:** Feeds D1, D4, D6 with business domain knowledge
- **Platform agenda:** Specific business context gaps, questions from ambiguous requirements, business rules needing clarification, edge cases from similar past features.
- **Real-time monitoring:** Tracks whether each gap has been addressed. Highlights contradictions with existing context.
- **Outputs:** Stakeholder Interview Summary · Updated business requirements · New constraints added to Context Graph

### M3 — Three Amigos

- **Phase:** Discovery
- **Frequency:** Weekly 2-hour sessions during discovery phases — the most important recurring meeting
- **Participants:** Product Owner + Tech Lead + Context Engineer. Always all three. No substitutes.
- **Decisions served:** D4 Story Decomposition · D5 Technical Approach · D6 Testing Contract
- **Platform agenda:** Features requiring story decomposition, draft stories needing acceptance criteria, context gaps per story with role-specific questions for each Amigo, success patterns for reference.
- **Real-time monitoring:** Per-story context completeness tracker. Alerts when a story has been discussed for >15 minutes without any testable acceptance criteria stated.
- **Outputs:** Story Definition Documents · Draft Context Packages auto-assembled from session outputs · Follow-up gap items

### M4 — Pattern Review

- **Phase:** Discovery
- **Frequency:** Once per discovery phase, or triggered when Codebase Intelligence detects new patterns
- **Participants:** Tech Lead + Context Engineer + Senior Developer(s)
- **Decisions served:** D5 Technical Approach — specifically the success patterns section
- **Platform agenda:** Candidate patterns detected by Codebase Intelligence, stories lacking matched patterns, patterns needing validation, anti-patterns from Q3 failure analysis.
- **Outputs:** Validated Pattern Library entries · Anti-pattern register · Updated context packages with newly matched patterns

### M5 — Sprint Planning

- **Phase:** Delivery
- **Frequency:** Start of each sprint — fortnightly
- **Participants:** Full development team + Product Owner + Context Engineer
- **Decisions served:** D8 Sprint Commitment
- **Platform agenda:** Candidate stories ranked by context readiness score, phase priority, and dependency order. Each story shows predicted queue outcome and blocking gaps.
- **Real-time monitoring:** Running capacity tracker. Alerts when committing a story with context readiness below 70%. Highlights dependency chains.
- **Outputs:** Sprint Plan with committed stories, manufacturing sequence, and capacity allocation

### M6 — Daily Stand-Up

- **Phase:** Delivery
- **Frequency:** Daily — 15 minutes maximum
- **Participants:** Development team + Context Engineer
- **Decisions served:** D9 Manufacturing Submission, unblocking decisions, scope micro-adjustments
- **Platform agenda:** Overnight manufacturing results requiring triage, stories blocked by context gaps, stories ready for manufacturing, context improvements completed since yesterday.
- **Real-time monitoring:** Sprint burndown with context readiness overlay — not just "work remaining" but "context-ready work remaining".
- **Outputs:** No formal document. Actions captured as context gap requests or Jira status updates via integration.

### M7 — Context Retrospective

- **Phase:** Delivery
- **Frequency:** End of each sprint — 1 hour
- **Participants:** Context Engineer + Tech Lead + interested developers
- **Decisions served:** D11 Context Improvement Priority
- **Platform agenda:** Sprint queue distribution (Q1/Q2/Q3 trends), top 3 Q3 failure causes, common patterns in Q2 developer modifications, Q1 success patterns to replicate.
- **Outputs:** Context Improvement Plan for next sprint · Updated pattern library entries · Sprint Context Quality Report

---

## 04 — The Self-Curating Context Model

The platform's most distinctive capability is that context curates itself. Meetings are scheduled because gaps exist. Agendas are generated because specific questions need answers. The system learns what "complete" means from outcomes.

### The Self-Curation Loop

1. **Gap Detection** — The Context Graph continuously evaluates completeness for every active work item. When a section falls below threshold (configured per team), a context gap is created automatically.
2. **Resolution Routing** — Each gap is classified by type and routed to the appropriate resolution mechanism. A missing business rule goes to the stakeholder meeting agenda. A missing code pattern triggers Codebase Intelligence analysis.
3. **Meeting Curation** — The Process Engine aggregates pending gaps by meeting type and schedules or adds to the next appropriate meeting. If enough high-severity gaps accumulate, it can trigger an ad-hoc session.
4. **Resolution Capture** — When a meeting occurs, the extraction pipeline processes the transcript and marks gaps as resolved — pending human confirmation.
5. **Quality Feedback** — When manufactured code is triaged, the triage feedback reveals whether gaps were truly resolved or merely appeared to be. Q2 and Q3 outcomes may reopen gaps that were marked resolved.

### Context from the Codebase

The codebase is not just a manufacturing target — it is a rich context source. The Codebase Intelligence engine continuously produces structured insights.

| Insight Type | How It's Generated | How It's Used |
|-------------|-------------------|---------------|
| **Success Patterns** | Analysing which code patterns correlate with clean PR approvals, high test coverage, and production stability. Developers validate these in Pattern Review meetings. | Added to pattern library. Matched to context packages automatically. |
| **Anti-Patterns** | Analysing which patterns correlate with production incidents, high defect rates, or repeated reviewer comments. | Become hard constraints in context packages. |
| **Change Impact Maps** | Analysing historical co-change patterns (files that tend to change together). | Predicts blast radius of a modification. Feeds the "affected components" section of every context package. |

### Queue Classification

Every piece of manufactured code is classified into one of three queues. The distribution across these queues is the primary health metric for the platform.

| Queue | Label | Definition |
|-------|-------|------------|
| **Q1** | Production Ready | Code meets all acceptance criteria. Passes all tests. Requires only standard code review. No developer rework needed. This is the target state. |
| **Q2** | Solid Foundation | Code demonstrates correct understanding but requires human finishing. Developer documents the specific gaps. These gaps feed directly back into context improvement. |
| **Q3** | Unusable | Code is not a useful starting point. Developer documents the root cause of failure. Q3 failures trigger immediate context package review and are the highest priority for improvement. |

---

## 05 — Integration Architecture: Inputs, Outputs & Integrations

The platform wraps around existing tools. No one changes their workflow. Context is captured where work already happens.

### Input Sources

| Source | Capture Method | Context Produced | Decisions Fed |
|--------|---------------|-----------------|---------------|
| Meeting transcript | Auto-record + transcribe | Decisions, requirements, action items, clarifications | D1–D8, D11 |
| Git commit / PR | Webhook listener | Code patterns, file changes, review feedback | D5, D10, D11 |
| Jira / PM tool update | Bidirectional sync | Story status, scope changes, blocking issues | D4, D8, D9 |
| Slack / Teams thread | Opt-in channel listener | Ad-hoc decisions, clarifications, technical discussions | D4–D7 |
| CI/CD pipeline result | Webhook listener | Test pass/fail, build status, coverage metrics | D10, D12 |
| Architecture document | Manual upload or Confluence sync | System constraints, component boundaries, NFRs | D2, D5, D7 |
| Production incident | Alerting integration | Failure patterns, constraint updates, risk factors | D5, D6, D11 |
| User research / feedback | Manual upload or tool sync | Business context, user needs, priority signals | D1, D4 |
| Codebase scan | Scheduled analysis pipeline | Success patterns, dependency graphs, file maps | D5, D7, D9 |
| Triage feedback form | In-platform submission | Gap analysis, Q2 diffs, Q3 failure causes | D11 |

### Integration Architecture

#### Chat Tools — Slack · Microsoft Teams

- **Passive context capture** — Opt-in channels are monitored for project-relevant decisions and clarifications. When the platform detects a decision, it creates a draft context item and sends a confirmation prompt. The user confirms with a single emoji reaction or button click.
- **Meeting agenda distribution** — Before each curated meeting, the platform posts the context-gap agenda to the relevant channel or DMs participants directly. Agenda items link to the specific context gaps in the platform so participants can prepare.
- **Sign-off collection** — After meeting extractions are ready for review, participants receive a Slack/Teams message with a summary and approve/reject buttons. Sign-offs are collected asynchronously without requiring anyone to log into the platform.

#### Call Tools — Zoom · Microsoft Teams · Google Meet

- **Recording and transcription** — A bot joins scheduled meetings automatically (based on calendar integration). It records, transcribes using speaker diarisation, and delivers the transcript to the Meeting Intelligence engine. Participants see the bot join and can remove it if the meeting should not be recorded.
- **Real-time sufficiency dashboard** — During the meeting, the facilitator has a browser tab showing the live sufficiency tracker. This is a lightweight web view — not a plugin that requires installation. It updates every 30 seconds as the transcript is processed.

#### Project Management — Jira · Linear · Azure DevOps

- **Bidirectional sync** — Work items created in the platform push to the PM tool. Status changes in the PM tool reflect in the Context Graph. Context packages link to stories via custom fields.
- **Context readiness field** — A custom field on each story shows the current context readiness score (0–100%). Developers see at a glance which stories have sufficient context. Product owners can filter the backlog by context readiness.
- **Auto-story creation** — When Three Amigos sessions produce new stories, they are automatically created in the PM tool with acceptance criteria, linked to the context package, and placed in the appropriate sprint or backlog position.

#### Source Control — GitHub · GitLab · Bitbucket

- **Pattern detection** — Every push and merge triggers Codebase Intelligence analysis. New patterns, convention changes, and dependency updates flow into the Context Graph automatically.
- **PR enrichment** — When a PR is created from AI-manufactured code, the platform automatically adds a comment linking to the context package that generated it. Reviewers can trace any line of code back to the business requirement that motivated it.
- **Feedback capture** — PR review comments on manufactured code are captured as potential context improvements. A reviewer who writes "This should handle the null case" is automatically flagged as a testing contract gap.

---

## 06 — Output & Sign-Off Matrix: Every Document. Every Gate.

Every output document has a defined owner, reviewer, and sign-off authority. Nothing enters the official context library or crosses a phase gate without documented human approval.

| Document | Produced by | Reviewed by | Signed off by | Gate it enables |
|----------|-------------|-------------|---------------|-----------------|
| Quarterly Roadmap | Product Lead | Eng Lead | Business Sponsor | Quarter start |
| Phase Plan | Delivery Lead | Product Owner | Eng Lead + PO | Phase start |
| Resource Allocation | Eng Leads | Context Eng | Eng Leads | Phase start |
| Story Definition | Three Amigos | Context Eng | All three Amigos | Discovery exit |
| Context Package | Context Eng (auto-assembled) | Developer + PO | CE + TL + PO | Manufacturing entry |
| Testing Contract | Context Eng | Tech Lead | Tech Lead | Manufacturing entry |
| Sprint Plan | Dev Team | PO + CE | Team consensus | Sprint start |
| Triage Feedback | Developer | Context Eng | Developer | Context improvement |
| Context Improvement Plan | Context Eng | Tech Lead | CE + TL | Next sprint |
| Phase Completion Report | Delivery Lead | PO + Eng Lead | PO + Eng Lead + Stakeholders | Release / next phase |
| Meeting Extraction | Platform (auto) | Context Eng | All participants | Context Graph entry |
| Pattern Library Entry | Codebase Intel (auto) | Senior Dev | Tech Lead | Pattern library entry |

---

## Closing Principle

> **The platform proposes. Humans approve. Every time.**

The entire architecture rests on a single principle: AI accelerates every part of the process, but humans remain accountable for every decision. Context is captured automatically, structured automatically, and assembled automatically — but it is never *approved* automatically.

---

## Reference implementation (this repository)

An MVP aligned with **D7** / **D8** (sprint commitments with D7 gate + override) / **D9** / **D10** / **D4** (meeting extraction sign-off), plus **`decision_records`** and **`artifacts`** for traceability, **audit events**, and request **`X-Context-Actor`**, lives in `src/context_platform/`: roadmap **cycle → phase → feature → story**, structured package sections, SQLite persistence (with migration from legacy `work_items`), REST API under `/api/context`, and a dashboard at `/context`. Run `python run.py` and see the repository README for URLs and `CONTEXT_DB_PATH`.

---

*Learn more: [contextengineering.team](https://contextengineering.team/) · [softwaremanufacturing.team](https://softwaremanufacturing.team/)*  
*Contact: Paul@AutomatedAgile.co.uk*  
*Version 1.0 · March 2026 · Part of the Automated Agile Framework*
