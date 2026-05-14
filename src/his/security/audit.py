from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from his.config import settings


def write_audit_event(event: dict[str, Any], path: Path | None = None) -> None:
    log_path = path or settings.audit_log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **event,
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def read_audit_events(path: Path | None = None, limit: int = 50) -> list[dict[str, Any]]:
    log_path = path or settings.audit_log_path
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    events = [json.loads(line) for line in lines[-limit:] if line.strip()]
    return list(reversed(events))
