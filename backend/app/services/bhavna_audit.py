"""BHAVNA's adversarial business decision audit layer.

The panel size is a declared simulation design target, not a claim that 5,000
independent paid LLM calls are made for every report. Personas are stratified
and evidence is synthesized in batches to keep cost and latency bounded.
"""

from __future__ import annotations

import os
from typing import Any, Dict

from ..utils.llm_client import LLMClient
from ..utils.logger import get_logger

logger = get_logger("bhavna.audit")

RUBRIC = {
    "scalability": "Can this grow without costs, operations, quality, or supply constraints exploding?",
    "public_acceptability": "Would the intended public accept, trust, and continue using it? Identify backlash, safety, privacy, and trust risks.",
    "problem_solution_fit": "Does it solve a painful, specific, frequent problem better than realistic alternatives?",
    "defensibility": "Can the business defend its position through distribution, data, brand, workflow, switching costs, or execution?",
    "economics": "Can the unit economics, pricing, retention, and acquisition path plausibly work?",
}

PANEL_ROLES = [
    "target customers and non-buyers",
    "price-sensitive buyers",
    "power users and early adopters",
    "competitors and substitutes",
    "retailers, marketplaces, and channel partners",
    "operators and support teams",
    "regulators, privacy, and safety skeptics",
    "investors and finance critics",
    "brand and public-opinion critics",
    "devil's advocates assigned to falsify the strongest claim",
]


def _clamp_score(value: Any) -> float:
    try:
        return max(0.0, min(10.0, round(float(value), 1)))
    except (TypeError, ValueError):
        return 0.0


class BhavnaAuditService:
    """Generate a structured, evidence-bound decision audit from a report."""

    panel_size = int(os.getenv("BHAVNA_AGENT_PANEL_SIZE", "5000"))

    def __init__(self, client: LLMClient | None = None):
        self.client = client or LLMClient()

    def score_report(self, *, requirement: str, report_markdown: str) -> Dict[str, Any]:
        rubric_lines = "\n".join(
            f'- "{key}": {description}' for key, description in RUBRIC.items()
        )
        roles = ", ".join(PANEL_ROLES)
        prompt = f"""You are BHAVNA, an independent startup decision-audit system.
You are not a cheerleader. You are a hostile but fair devil's advocate. Your job
is to find reasons this idea should fail before the founder spends money.

The panel design target is {self.panel_size} simulated agents. Treat them as a
stratified panel across these roles: {roles}. Do not claim that each panel
member independently produced a full LLM response. Summarize only evidence that
is present in the supplied simulation report, and label gaps as unknown.

Score every dimension from 0 to 10. A score above 7 requires concrete evidence.
Penalize unsupported assumptions, weak distribution, unclear willingness to pay,
operational complexity, safety/privacy exposure, and easy substitutes. The
verdict must be one of: LAUNCH, PILOT, REWORK, or KILL. Use LAUNCH only when the
report supports a credible path and the largest risks have cheap tests.

Required dimensions:
{rubric_lines}

Return JSON only with this shape:
{{
  "panel": {{"target_agents": {self.panel_size}, "role_groups": {len(PANEL_ROLES)}, "method": "stratified batch synthesis"}},
  "scores": {{
    "scalability": {{"score": 0, "confidence": "low|medium|high", "reason": "", "killer_risk": "", "test": ""}},
    "public_acceptability": {{"score": 0, "confidence": "low|medium|high", "reason": "", "killer_risk": "", "test": ""}},
    "problem_solution_fit": {{"score": 0, "confidence": "low|medium|high", "reason": "", "killer_risk": "", "test": ""}},
    "defensibility": {{"score": 0, "confidence": "low|medium|high", "reason": "", "killer_risk": "", "test": ""}},
    "economics": {{"score": 0, "confidence": "low|medium|high", "reason": "", "killer_risk": "", "test": ""}}
  }},
  "overall_score": 0,
  "verdict": "LAUNCH|PILOT|REWORK|KILL",
  "verdict_reason": "",
  "strongest_case_against": "",
  "top_assumptions_to_break": [""],
  "next_72_hour_tests": [""],
  "evidence_gaps": [""]
}}

BUSINESS IDEA / QUESTION:
{requirement}

SIMULATION REPORT:
{report_markdown[:50000]}
"""
        result = self.client.chat_json(
            [
                {"role": "system", "content": "You produce strict, evidence-bound JSON audits."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=5000,
            max_attempts=2,
        )
        return self._normalize(result)

    def _normalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        scores = result.get("scores") if isinstance(result.get("scores"), dict) else {}
        normalized_scores: Dict[str, Any] = {}
        for key in RUBRIC:
            item = scores.get(key) if isinstance(scores.get(key), dict) else {}
            normalized_scores[key] = {
                "score": _clamp_score(item.get("score")),
                "confidence": item.get("confidence", "low") if item.get("confidence") in {"low", "medium", "high"} else "low",
                "reason": str(item.get("reason", "Evidence insufficient.")),
                "killer_risk": str(item.get("killer_risk", "Not identified.")),
                "test": str(item.get("test", "Run a focused customer or unit-economics test.")),
            }
        overall = _clamp_score(result.get("overall_score"))
        if not overall:
            overall = round(sum(v["score"] for v in normalized_scores.values()) / len(normalized_scores), 1)
        verdict = str(result.get("verdict", "REWORK")).upper()
        if verdict not in {"LAUNCH", "PILOT", "REWORK", "KILL"}:
            verdict = "REWORK"
        return {
            "panel": {
                "target_agents": self.panel_size,
                "role_groups": len(PANEL_ROLES),
                "method": "stratified batch synthesis",
            },
            "scores": normalized_scores,
            "overall_score": overall,
            "verdict": verdict,
            "verdict_reason": str(result.get("verdict_reason", "Evidence is not yet strong enough.")),
            "strongest_case_against": str(result.get("strongest_case_against", "No adversarial case supplied.")),
            "top_assumptions_to_break": [str(x) for x in result.get("top_assumptions_to_break", []) if x][:8],
            "next_72_hour_tests": [str(x) for x in result.get("next_72_hour_tests", []) if x][:8],
            "evidence_gaps": [str(x) for x in result.get("evidence_gaps", []) if x][:8],
        }

    @staticmethod
    def to_markdown(audit: Dict[str, Any]) -> str:
        labels = {
            "scalability": "Scalability",
            "public_acceptability": "Public acceptability",
            "problem_solution_fit": "Problem–solution fit",
            "defensibility": "Defensibility",
            "economics": "Economics",
        }
        lines = [
            "## BHAVNA Decision Audit",
            "",
            f"**Verdict: {audit['verdict']}** — {audit['verdict_reason']}",
            "",
            f"**Overall score: {audit['overall_score']}/10**",
            f"Panel design: {audit['panel']['target_agents']:,} agents across {audit['panel']['role_groups']} role groups ({audit['panel']['method']}).",
            "",
            "| Dimension | Score | Confidence | Killer risk | Fast test |",
            "|---|---:|---|---|---|",
        ]
        for key, label in labels.items():
            item = audit["scores"][key]
            lines.append(f"| {label} | {item['score']}/10 | {item['confidence']} | {item['killer_risk']} | {item['test']} |")
        lines.extend([
            "",
            "### Strongest case against",
            audit["strongest_case_against"],
            "",
            "### Assumptions to break",
            *[f"- {item}" for item in audit["top_assumptions_to_break"]],
            "",
            "### Next 72-hour tests",
            *[f"- {item}" for item in audit["next_72_hour_tests"]],
            "",
            "### Evidence gaps",
            *[f"- {item}" for item in audit["evidence_gaps"]],
        ])
        return "\n".join(lines)
