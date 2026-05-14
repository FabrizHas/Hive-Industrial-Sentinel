from his.telemetry.risk import assess_risk


def base_snapshot(**overrides):
    snapshot = {
        "asset_id": "TX-138KV-01",
        "voltage_v": 13800,
        "current_a": 150,
        "frequency_hz": 60,
        "oil_temp_c": 45,
        "load_pct": 70,
        "ambient_temp_c": 27,
        "status_label": "normal",
    }
    snapshot.update(overrides)
    return snapshot


def test_normal_snapshot_is_low_risk():
    result = assess_risk(base_snapshot())
    assert result["risk_level"] == "NORMAL"
    assert result["violations"] == []


def test_voltage_outside_five_percent_is_violation():
    result = assess_risk(base_snapshot(voltage_v=14_600))
    assert any(item["metric"] == "voltage_v" for item in result["violations"])


def test_thermal_overload_is_critical():
    result = assess_risk(base_snapshot(oil_temp_c=94))
    assert result["risk_level"] == "CRITICAL"
    assert any(item["metric"] == "oil_temp_c" for item in result["violations"])


def test_load_above_120_is_critical():
    result = assess_risk(base_snapshot(load_pct=125))
    assert result["risk_level"] == "CRITICAL"
    assert any(item["metric"] == "load_pct" for item in result["violations"])
