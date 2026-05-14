from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_DIR / "src"


def _path_from_env(name: str, default: str) -> Path:
    value = os.getenv(name, default)
    path = Path(value)
    return path if path.is_absolute() else PROJECT_DIR / path


@dataclass(frozen=True)
class Settings:
    data_path: Path = _path_from_env("HIS_DATA_PATH", "data/telemetry_logs.csv")
    manuals_dir: Path = _path_from_env("HIS_MANUALS_DIR", "knowledge/manuals")
    audit_log_path: Path = _path_from_env("HIS_AUDIT_LOG", "data/audit_log.jsonl")
    policy_path: Path = SRC_DIR / "his" / "security" / "policy.yaml"
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model_fast: str = os.getenv("GEMINI_MODEL_FAST", "gemini-2.5-flash")
    gemini_model_reasoning: str = os.getenv("GEMINI_MODEL_REASONING", "gemini-2.5-pro")
    lobster_trap_base_url: str = os.getenv("LOBSTER_TRAP_BASE_URL", "http://localhost:8080/v1")
    lobster_trap_enabled: bool = os.getenv("LOBSTER_TRAP_ENABLED", "false").lower() == "true"


settings = Settings()
