from pathlib import Path

from his.knowledge.retrieval import query_manual
from his.telemetry.generator import generate_industrial_data
from his.telemetry.repository import get_asset_window, summarize_window


def test_generator_creates_predictable_thermal_overload(tmp_path: Path):
    output = tmp_path / "telemetry.csv"
    df = generate_industrial_data(hours=3, output_path=output)
    assert output.exists()
    assert "thermal_overload" in set(df["status_label"])


def test_read_window_summary(tmp_path: Path):
    output = tmp_path / "telemetry.csv"
    generate_industrial_data(hours=3, output_path=output)
    window = get_asset_window(window_minutes=30, path=output)
    summary = summarize_window(window)
    assert summary["latest"]["asset_id"] == "TX-138KV-01"
    assert "oil_temp_delta_c" in summary["trend"]


def test_query_manual_returns_relevant_excerpt():
    hits = query_manual("thermal overload oil temperature controlled load shedding", top_k=1)
    assert hits
    assert "thermal" in hits[0]["excerpt"].lower()
