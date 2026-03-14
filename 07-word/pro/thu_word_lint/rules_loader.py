from __future__ import annotations

import json
from pathlib import Path


def load_rules(path: Path) -> dict:
    # v1: accept JSON-compatible text in .yaml file for zero dependencies.
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "rules parse failed; v1 skeleton expects JSON-formatted content in .yaml"
        ) from exc
