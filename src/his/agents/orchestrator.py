from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from openai import OpenAI

from his.agents.prompts import SYSTEM_PROMPT
from his.agents.tools import policy_check, query_manual, read_telemetry, risk_assessment
from his.config import settings
from his.security.lobster_client import evaluate_policy


@dataclass(frozen=True)
class AgentResponse:
    answer: str
    policy: dict[str, Any]
    telemetry: dict[str, Any] | None = None
    risk: dict[str, Any] | None = None
    manual_hits: list[dict[str, Any]] | None = None
    model_mode: str = "local-demo"

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "policy": self.policy,
            "telemetry": self.telemetry,
            "risk": self.risk,
            "manual_hits": self.manual_hits or [],
            "model_mode": self.model_mode,
        }


class HiveSentinelAgent:
    def __init__(self, asset_id: str = "TX-138KV-01") -> None:
        self.asset_id = asset_id

    def respond(self, user_prompt: str) -> AgentResponse:
        ingress = policy_check(user_prompt)
        if not ingress["allowed"]:
            return AgentResponse(answer=ingress["message"], policy=ingress)

        telemetry = read_telemetry(asset_id=self.asset_id, window_minutes=90)
        risk = risk_assessment(telemetry["latest"])
        manual_hits = query_manual(
            "thermal overload transformer oil temperature emergency load shedding cooling alarms",
            top_k=3,
        )

        if settings.gemini_api_key:
            answer = self._gemini_response(user_prompt, telemetry, risk, manual_hits)
            mode = settings.gemini_model_reasoning
        else:
            answer = self._local_response(risk, manual_hits)
            mode = "local-demo"

        egress = evaluate_policy(answer, direction="egress").to_dict()
        if not egress["allowed"]:
            return AgentResponse(
                answer=egress["message"],
                policy=egress,
                telemetry=telemetry,
                risk=risk,
                manual_hits=manual_hits,
                model_mode=mode,
            )

        return AgentResponse(
            answer=answer,
            policy=ingress,
            telemetry=telemetry,
            risk=risk,
            manual_hits=manual_hits,
            model_mode=mode,
        )

    def _gemini_response(
        self,
        user_prompt: str,
        telemetry: dict[str, Any],
        risk: dict[str, Any],
        manual_hits: list[dict[str, Any]],
    ) -> str:
        base_url = (
            settings.lobster_trap_base_url
            if settings.lobster_trap_enabled
            else "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        client = OpenAI(api_key=settings.gemini_api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=settings.gemini_model_reasoning,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Operator question: {user_prompt}\n\n"
                        f"Telemetry: {telemetry}\n\n"
                        f"Risk assessment: {risk}\n\n"
                        f"Manual evidence: {manual_hits}\n\n"
                        "Return a concise operational diagnosis and safe next actions."
                    ),
                },
            ],
        )
        return response.choices[0].message.content or ""

    @staticmethod
    def _local_response(risk: dict[str, Any], manual_hits: list[dict[str, Any]]) -> str:
        evidence = manual_hits[0]["source"] if manual_hits else "demo manual"
        return (
            f"Risk level: {risk['risk_level']} (score {risk['score']}). "
            f"{risk['recommended_action']} "
            f"Evidence source: {evidence}. "
            "Keep protective interlocks enabled and document the operator decision in the audit log."
        )
