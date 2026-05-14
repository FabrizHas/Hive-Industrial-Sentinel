from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from his.config import settings


@dataclass(frozen=True)
class TelemetrySnapshot:
    timestamp: str
    asset_id: str
    voltage_v: float
    current_a: float
    frequency_hz: float
    oil_temp_c: float
    load_pct: float
    ambient_temp_c: float
    status_label: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_telemetry(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or settings.data_path
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Telemetry file not found at {csv_path}. Run `python -m his.telemetry.generator`."
        )
    df = pd.read_csv(csv_path, parse_dates=["timestamp"])
    return df.sort_values("timestamp").reset_index(drop=True)


def get_asset_window(
    asset_id: str = "TX-138KV-01",
    window_minutes: int = 60,
    path: Path | None = None,
) -> pd.DataFrame:
    df = load_telemetry(path)
    asset_df = df[df["asset_id"] == asset_id].copy()
    if asset_df.empty:
        raise ValueError(f"No telemetry rows found for asset_id={asset_id}")
    return asset_df.tail(max(1, window_minutes))


def get_latest_snapshot(asset_id: str = "TX-138KV-01", path: Path | None = None) -> TelemetrySnapshot:
    row = get_asset_window(asset_id=asset_id, window_minutes=1, path=path).iloc[-1]
    return TelemetrySnapshot(
        timestamp=row["timestamp"].isoformat()
        if hasattr(row["timestamp"], "isoformat")
        else str(row["timestamp"]),
        asset_id=str(row["asset_id"]),
        voltage_v=float(row["voltage_v"]),
        current_a=float(row["current_a"]),
        frequency_hz=float(row["frequency_hz"]),
        oil_temp_c=float(row["oil_temp_c"]),
        load_pct=float(row["load_pct"]),
        ambient_temp_c=float(row["ambient_temp_c"]),
        status_label=str(row["status_label"]),
    )


def summarize_window(window: pd.DataFrame) -> dict[str, Any]:
    first = window.iloc[0]
    latest = window.iloc[-1]
    events = window[window["status_label"] != "normal"].tail(10)
    latest_snapshot = TelemetrySnapshot(
        timestamp=latest["timestamp"].isoformat()
        if hasattr(latest["timestamp"], "isoformat")
        else str(latest["timestamp"]),
        asset_id=str(latest["asset_id"]),
        voltage_v=float(latest["voltage_v"]),
        current_a=float(latest["current_a"]),
        frequency_hz=float(latest["frequency_hz"]),
        oil_temp_c=float(latest["oil_temp_c"]),
        load_pct=float(latest["load_pct"]),
        ambient_temp_c=float(latest["ambient_temp_c"]),
        status_label=str(latest["status_label"]),
    )
    return {
        "rows": int(len(window)),
        "start": str(first["timestamp"]),
        "end": str(latest["timestamp"]),
        "trend": {
            "oil_temp_delta_c": round(float(latest["oil_temp_c"] - first["oil_temp_c"]), 2),
            "load_delta_pct": round(float(latest["load_pct"] - first["load_pct"]), 2),
            "current_delta_a": round(float(latest["current_a"] - first["current_a"]), 2),
        },
        "latest": latest_snapshot.to_dict(),
        "events": events[
            ["timestamp", "asset_id", "oil_temp_c", "load_pct", "status_label"]
        ].to_dict(orient="records"),
    }
