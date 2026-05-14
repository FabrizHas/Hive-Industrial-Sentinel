from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from his.config import settings


def generate_industrial_data(
    hours: int = 24,
    asset_id: str = "TX-138KV-01",
    seed: int = 42,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """Generate deterministic transformer telemetry with a late thermal overload."""
    rng = np.random.default_rng(seed)
    now = datetime.now().replace(second=0, microsecond=0)
    timestamps = [now - timedelta(minutes=minutes) for minutes in range(hours * 60)]
    timestamps = sorted(timestamps)
    size = len(timestamps)

    base_temp = np.linspace(40, 48, size) + rng.normal(0, 0.45, size)
    load_pct = rng.normal(72, 4, size)
    current_a = rng.normal(150, 8, size)

    anomaly_window = min(90, size)
    if anomaly_window > 0:
        ramp = np.linspace(0, 47, anomaly_window)
        base_temp[-anomaly_window:] += ramp
        load_pct[-anomaly_window:] += np.linspace(8, 55, anomaly_window)
        current_a[-anomaly_window:] += np.linspace(10, 95, anomaly_window)

    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "asset_id": asset_id,
            "voltage_v": rng.normal(13800, 52, size),
            "current_a": current_a,
            "frequency_hz": rng.normal(60, 0.04, size),
            "oil_temp_c": base_temp,
            "load_pct": load_pct,
            "ambient_temp_c": rng.normal(27, 1.3, size),
        }
    )

    df["status_label"] = np.select(
        [
            df["oil_temp_c"] >= 90,
            df["load_pct"] >= 120,
            df["oil_temp_c"] >= 80,
        ],
        ["thermal_overload", "overload", "thermal_warning"],
        default="normal",
    )

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)

    return df


def main() -> None:
    df = generate_industrial_data(output_path=settings.data_path)
    print(f"Generated {len(df)} telemetry rows at {settings.data_path}")


if __name__ == "__main__":
    main()
