# Decision agent fleet (D1–D12)

**Goal:** Treat each **process decision** (D1–D12) as its own **lightweight agent** that uses the **same LLM API path** as everything else (meeting extraction, future tools). One **model configuration**; twelve **prompt contracts**.

## Configuration (single surface)

| Variable | Purpose |
|----------|---------|
| `OPENAI_API_KEY` | Required for any LLM call. |
| `CONTEXT_LLM_MODEL` | Preferred model id for **all** agents (decision + meeting). |
| `OPENAI_MODEL` | Fallback if `CONTEXT_LLM_MODEL` unset. |
| `CONTEXT_LLM_BASE_URL` | Optional OpenAI-compatible API base (same for all calls). |
| `OPENAI_BASE_URL` | Alternative env name for base URL. |

Meeting extraction (`meeting_llm`) and **decision agents** both use [`llm_client`](../src/context_platform/llm_client.py).

## API

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/context/decision-agents` | List D1–D12 with titles and process questions. |
| `POST` | `/api/context/decision-agents/{D1..D12}/invoke` | Body: `{ "context": { ... }, "extra_instructions": "optional" }`. |

Response includes `ok`, `decision_code`, `model`, and `result` (parsed JSON from the model: `summary`, `structured`, `recommended_next_actions`, `confidence`, `open_questions`).

Successful and failed invocations append **`audit_events`** (`decision_agent_invoked` / `decision_agent_failed`).

## Continuous improvement loop

The same `POST …/invoke` contract supports:

- **Human-in-the-loop:** Workbench or CLI gathers context JSON, calls the agent, human decides.
- **Automation:** Scheduled job or webhook handler **re-invokes** with updated context (e.g. after triage, append Q2 notes to `context` and call **D11** again).
- **MCP (future):** Expose each decision code as a tool that wraps this endpoint or `invoke_decision_agent()` directly.

Agents **propose**; they do **not** replace D7 sign-offs or stored `decision_records` unless you add explicit workflows that create records from reviewed output.

## Code

- Registry + prompts: [`decision_agents.py`](../src/context_platform/decision_agents.py)
- HTTP client: [`llm_client.py`](../src/context_platform/llm_client.py)
