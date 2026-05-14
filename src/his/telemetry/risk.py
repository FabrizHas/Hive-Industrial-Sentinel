from __future__ import annotations

from typing import Any


NOMINAL_VOLTAGE_V = 13_800
MIN_FREQUENCY_HZ = 59.7
MAX_FREQUENCY_HZ = 60.3
WARNING_OIL_TEMP_C = 80
CRITICAL_OIL_TEMP_C = 90
MAX_LOAD_PCT = 120


def assess_risk(snapshot: dict[str, Any]) -> dict[str, Any]:
    voltage = float(snapshot["voltage_v"])
    frequency = float(snapshot["frequency_hz"])
    oil_temp = float(snapshot["oil_temp_c"])
    load_pct = float(snapshot["load_pct"])

    violations: list[dict[str, Any]] = []
    score = 0.0

    voltage_deviation = abs(voltage - NOMINAL_VOLTAGE_V) / NOMINAL_VOLTAGE_V
    if voltage_deviation > 0.05:
        violations.append(
            {
                "metric": "voltage_v",
                "severity": "high",
                "message": "Voltage is outside the +/-5% operating envelope.",
            }
        )
        score += 0.3

    if not MIN_FREQUENCY_HZ <= frequency <= MAX_FREQUENCY_HZ:
        violations.append(
            {
                "metric": "frequency_hz",
                "severity": "medium",
                "message": "Frequency is outside the 59.7-60.3 Hz stability band.",
            }
        )
        score += 0.2

    if oil_temp >= CRITICAL_OIL_TEMP_C:
        violations.append(
            {
                "metric": "oil_temp_c",
                "severity": "critical",
                "message": "Transformer oil temperature indicates thermal overload.",
            }
        )
        score += 0.45
    elif oil_temp >= WARNING_OIL_TEMP_C:
        violations.append(
            {
                "metric": "oil_temp_c",
                "severity": "medium",
                "message": "Transformer oil temperature is approaching the critical range.",
            }
        )
        score += 0.2

    if load_pct >= MAX_LOAD_PCT:
        violations.append(
            {
                "metric": "load_pct",
                "severity": "critical",
                "message": "Load exceeds the 120% emergency limit.",
            }
        )
        score += 0.4
    elif load_pct >= 100:
        violations.append(
            {
                "metric": "load_pct",
                "severity": "medium",
                "message": "Load is above nominal capacity.",
            }
        )
        score += 0.15

    score = min(round(score, 2), 1.0)
    critical = any(item["severity"] == "critical" for item in violations)
    if critical or score >= 0.75:
        risk_level = "CRITICAL"
        recommended_action = (
            "Initiate controlled load shedding, keep cooling active, notify operations, "
            "and do not override protective alarms."
        )
    elif score >= 0.35:
        risk_level = "ELEVATED"
        recommended_action = (
            "Increase monitoring cadence, verify cooling status, and prepare a controlled "
            "load reduction plan."
        )
    else:
        risk_level = "NORMAL"
        recommended_action = "Continue normal monitoring."

    return {
        "asset_id": snapshot.get("asset_id", "unknown"),
        "risk_level": risk_level,
        "score": score,
        "violations": violations,
        "recommended_action": recommended_action,
    }
