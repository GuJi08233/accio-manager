from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path
from typing import Any

from .models import now_text


def _truncate(value: Any, limit: int = 500) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}..."


class ApiLogStore:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def record(self, payload: dict[str, Any]) -> None:
        entry = {
            "id": uuid.uuid4().hex,
            "createdAt": now_text(),
            **payload,
        }
        with self._lock:
            with self.file_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def recent(self, limit: int = 200) -> list[dict[str, Any]]:
        with self._lock:
            if not self.file_path.exists():
                return []
            try:
                lines = self.file_path.read_text(encoding="utf-8").splitlines()
            except OSError:
                return []

        items: list[dict[str, Any]] = []
        for raw_line in reversed(lines):
            if not raw_line.strip():
                continue
            try:
                payload = json.loads(raw_line)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue

            item = {
                "id": str(payload.get("id") or ""),
                "createdAt": str(payload.get("createdAt") or "-"),
                "level": str(payload.get("level") or "info"),
                "event": str(payload.get("event") or "-"),
                "accountName": str(payload.get("accountName") or "-"),
                "accountId": str(payload.get("accountId") or ""),
                "model": str(payload.get("model") or "-"),
                "stream": bool(payload.get("stream", True)),
                "success": bool(payload.get("success", False)),
                "emptyResponse": bool(payload.get("emptyResponse", False)),
                "stopReason": str(payload.get("stopReason") or "-"),
                "statusCode": str(payload.get("statusCode") or "-"),
                "message": _truncate(payload.get("message"), 160) or "-",
                "inputTokens": int(payload.get("inputTokens") or 0),
                "outputTokens": int(payload.get("outputTokens") or 0),
                "durationMs": int(payload.get("durationMs") or 0),
                "detailJson": json.dumps(payload, ensure_ascii=False, indent=2),
            }
            items.append(item)
            if len(items) >= limit:
                break
        return items
