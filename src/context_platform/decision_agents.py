"""
D1–D12 decision agents — same LLM pipeline, one model config, per-decision prompts.

Each decision type is a thin agent: shared ``chat_json`` + decision-specific system text.
Use for assisted analysis; humans remain accountable (per process architecture).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Optional

from src.context_platform.llm_client import chat_json, llm_configured, resolve_llm_model


@dataclass(frozen=True)
class DecisionAgentSpec:
    code: str
    title: str
    process_question: str
    focus: str


# Process architecture v2.0 — twelve decisions, one agent interface each.
DECISION_AGENT_REGISTRY: dict[str, DecisionAgentSpec] = {
    "D1": DecisionAgentSpec(
        "D1",
        "Portfolio prioritisation",
        "Of everything we could build, what matters most this quarter?",
        "Strategic alignment, MoSCoW, capacity, dependencies, debt.",
    ),
    "D2": DecisionAgentSpec(
        "D2",
        "Phase breakdown",
        "How do we break the quarter into testable, deliverable increments?",
        "Phases, milestones, risk, integration points.",
    ),
    "D3": DecisionAgentSpec(
        "D3",
        "T-shirt sizing & resource allocation",
        "How big is each piece of work, and which teams own it?",
        "Sizing, ownership, cross-team dependencies.",
    ),
    "D4": DecisionAgentSpec(
        "D4",
        "Story decomposition",
        "How do we break a feature into implementable stories with clear acceptance criteria?",
        "INVEST stories, G/W/T, scope boundaries.",
    ),
    "D5": DecisionAgentSpec(
        "D5",
        "Technical approach",
        "Which patterns, files, and architecture should this story use?",
        "Components, files, patterns, security, APIs.",
    ),
    "D6": DecisionAgentSpec(
        "D6",
        "Testing contract",
        "What are preconditions, postconditions, invariants, and scenarios?",
        "Test types, edge cases, data setup.",
    ),
    "D7": DecisionAgentSpec(
        "D7",
        "Context package approval",
        "Is this context package complete enough to manufacture working software?",
        "Completeness, gaps, contradictions, sign-off readiness.",
    ),
    "D8": DecisionAgentSpec(
        "D8",
        "Sprint commitment",
        "Which stories do we commit to this sprint?",
        "Capacity, readiness scores, dependencies, carry-over.",
    ),
    "D9": DecisionAgentSpec(
        "D9",
        "Manufacturing submission",
        "Is this story ready to submit to the AI manufacturing pipeline right now?",
        "Approved package, snapshot freshness, risk flags.",
    ),
    "D10": DecisionAgentSpec(
        "D10",
        "Triage classification",
        "Is generated code Q1 (ready), Q2 (finishing), or Q3 (failed)?",
        "Evidence from tests, diffs, acceptance criteria fit.",
    ),
    "D11": DecisionAgentSpec(
        "D11",
        "Context improvement priority",
        "Which context packages should we improve first from triage feedback?",
        "Q2/Q3 patterns, gap severity, blast radius.",
    ),
    "D12": DecisionAgentSpec(
        "D12",
        "Phase / release approval",
        "Has the phase met success criteria; can we release?",
        "Quality bar, defects, stakeholder sign-off signals.",
    ),
}


def normalize_decision_code(code: str) -> Optional[str]:
    c = (code or "").strip().upper()
    if re.fullmatch(r"D(1[0-2]|[1-9])", c):
        return c
    return None


_SHARED_JSON_INSTRUCTION = """
Return ONLY valid JSON with this shape:
{
  "decision_code": "<same as request>",
  "summary": "2-4 sentence assistant view",
  "structured": { },
  "recommended_next_actions": ["short actionable strings"],
  "confidence": 0.0,
  "open_questions": ["what humans should still resolve"]
}
Use "structured" for any bullet lists or key-value hints specific to this decision.
confidence is your calibrated 0-1 estimate; humans decide.
"""


def build_system_prompt(spec: DecisionAgentSpec) -> str:
    return f"""You are a decision-support agent for software delivery (Automated Agile / Context Engineering).

Decision: {spec.code} — {spec.title}
Key question: {spec.process_question}
Analytical focus: {spec.focus}

You receive JSON context from the platform (stories, packages, gaps, audit excerpts, etc.).
You do NOT approve or sign off — you assist humans who remain accountable.
Be concise, factual, and flag missing inputs explicitly.
{_SHARED_JSON_INSTRUCTION}
"""


def invoke_decision_agent(
    decision_code: str,
    context: dict[str, Any],
    *,
    extra_instructions: str = "",
) -> dict[str, Any]:
    """
    Run one decision agent with the shared LLM client.

    ``context`` is forwarded as JSON to the model (truncate upstream if huge).
    """
    norm = normalize_decision_code(decision_code)
    if not norm or norm not in DECISION_AGENT_REGISTRY:
        return {
            "ok": False,
            "error": "unknown_decision_code",
            "valid_codes": sorted(DECISION_AGENT_REGISTRY.keys()),
        }

    spec = DECISION_AGENT_REGISTRY[norm]
    model = resolve_llm_model()

    if not llm_configured():
        return {
            "ok": False,
            "error": "llm_not_configured",
            "hint": "Set OPENAI_API_KEY (and optionally CONTEXT_LLM_MODEL).",
            "decision_code": norm,
            "model": model,
        }

    user_obj: dict[str, Any] = {
        "decision_code": norm,
        "context": context,
    }
    if extra_instructions.strip():
        user_obj["extra_instructions"] = extra_instructions.strip()
    user = json.dumps(user_obj, ensure_ascii=False, indent=2)

    data, err, used_model = chat_json(build_system_prompt(spec), user, temperature=0.25)
    if err or data is None:
        return {
            "ok": False,
            "error": err or "llm_failed",
            "decision_code": norm,
            "model": used_model,
        }

    data.setdefault("decision_code", norm)
    return {
        "ok": True,
        "decision_code": norm,
        "title": spec.title,
        "model": used_model,
        "result": data,
    }
