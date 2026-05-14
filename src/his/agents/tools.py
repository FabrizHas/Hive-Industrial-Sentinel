from __future__ import annotations

from typing import Any

from his.knowledge.retrieval import query_manual as retrieve_manual
from his.security.lobster_client import policy_check as check_policy
from his.telemetry.repository import get_asset_window, summarize_window
from his.telemetry.risk import assess_risk


def read_telemetry(asset_id: str = "TX-138KV-01", window_minutes: int = 60) -> dict[str, Any]:
    window = get_asset_window(asset_id=asset_id, window_minutes=window_minutes)
    return summarize_window(window)


def risk_assessment(snapshot: dict[str, Any]) -> dict[str, Any]:
    return assess_risk(snapshot)


def query_manual(question: str, top_k: int = 3) -> list[dict[str, str | int]]:
    return retrieve_manual(question=question, top_k=top_k)


def policy_check(prompt: str, proposed_action: str | None = None) -> dict[str, Any]:
    return check_policy(prompt=prompt, proposed_action=proposed_action)


TOOL_SCHEMAS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "read_telemetry",
            "description": "Read recent transformer telemetry and return latest snapshot, trend, and events.",
            "parameters": {
                "type": "object",
                "properties": {
                    "asset_id": {"type": "string"},
                    "window_minutes": {"type": "integer", "minimum": 1, "maximum": 1440},
                },
                "required": ["asset_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "risk_assessment",
            "description": "Score transformer operating risk from a telemetry snapshot.",
            "parameters": {
                "type": "object",
                "properties": {"snapshot": {"type": "object"}},
                "required": ["snapshot"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_manual",
            "description": "Retrieve relevant operating guidance from transformer manuals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 5},
                },
                "required": ["question"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "policy_check",
            "description": "Evaluate whether an operator prompt or proposed action violates safety policy.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string"},
                    "proposed_action": {"type": "string"},
                },
                "required": ["prompt"],
            },
        },
    },
]
