from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from his.config import settings
from his.security.audit import write_audit_event


@dataclass(frozen=True)
class PolicyDecision:
    action: str
    allowed: bool
    rule: str
    message: str
    direction: str = "ingress"

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "allowed": self.allowed,
            "rule": self.rule,
            "message": self.message,
            "direction": self.direction,
        }


def _default_rules() -> dict[str, list[dict[str, Any]]]:
    return {
        "ingress_rules": [
            {
                "name": "block_alarm_override",
                "action": "DENY",
                "deny_message": "[HIS SHIELD] Blocked: operator request attempts to bypass alarms.",
                "patterns": [
                    r"(?i)ignore\s+(all\s+)?alarms?",
                    r"(?i)bypass\s+(safety|alarm|interlock)",
                    r"(?i)disable\s+(safety|safeguards?|interlocks?|alarms?)",
                ],
            },
            {
                "name": "block_forced_overload",
                "action": "DENY",
                "deny_message": "[HIS SHIELD] Blocked: requested load violates the 120% emergency limit.",
                "patterns": [
                    r"(?i)force\s+load\s+(above|over|to)\s+120%",
                    r"(?i)set\s+load\s+(above|over|to)\s+120%",
                    r"(?i)operate\s+(above|over)\s+120%",
                ],
            },
            {
                "name": "block_prompt_injection",
                "action": "DENY",
                "deny_message": "[HIS SHIELD] Blocked: prompt injection pattern detected.",
                "patterns": [
                    r"(?i)ignore\s+(previous|all)\s+instructions",
                    r"(?i)you\s+are\s+now\s+(developer|system|admin)",
                    r"(?i)reveal\s+(the\s+)?system\s+prompt",
                ],
            },
        ],
        "egress_rules": [
            {
                "name": "block_unsafe_recommendation",
                "action": "DENY",
                "deny_message": "[HIS SHIELD] Blocked: unsafe recommendation detected.",
                "patterns": [
                    r"(?i)ignore\s+(the\s+)?alarms?",
                    r"(?i)force\s+load\s+(above|over|to)\s+120%",
                ],
            }
        ],
    }


def load_policy(path: Path | None = None) -> dict[str, Any]:
    policy_path = path or settings.policy_path
    if not policy_path.exists():
        return _default_rules()
    try:
        import yaml
    except ImportError:
        return _default_rules()

    with policy_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}
    return {
        "ingress_rules": loaded.get("ingress_rules", []),
        "egress_rules": loaded.get("egress_rules", []),
    }


def evaluate_policy(
    text: str,
    direction: str = "ingress",
    policy_path: Path | None = None,
    write_audit: bool = True,
) -> PolicyDecision:
    policy = load_policy(policy_path)
    rules = policy.get(f"{direction}_rules", [])
    for rule in sorted(rules, key=lambda item: int(item.get("priority", 0)), reverse=True):
        for pattern in rule.get("patterns", []):
            if re.search(pattern, text):
                decision = PolicyDecision(
                    action=rule.get("action", "DENY"),
                    allowed=rule.get("action", "DENY") == "ALLOW",
                    rule=rule.get("name", "unnamed_rule"),
                    message=rule.get("deny_message", "Policy violation detected."),
                    direction=direction,
                )
                if write_audit:
                    write_audit_event(
                        {
                            "component": "policy",
                            "decision": decision.to_dict(),
                            "text_preview": text[:240],
                        }
                    )
                return decision

    decision = PolicyDecision(
        action="ALLOW",
        allowed=True,
        rule="default_allow",
        message="Allowed by default policy.",
        direction=direction,
    )
    if write_audit:
        write_audit_event(
            {
                "component": "policy",
                "decision": decision.to_dict(),
                "text_preview": text[:240],
            }
        )
    return decision


def policy_check(prompt: str, proposed_action: str | None = None) -> dict[str, Any]:
    combined = f"{prompt}\n{proposed_action or ''}".strip()
    return evaluate_policy(combined).to_dict()
