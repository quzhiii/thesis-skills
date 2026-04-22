from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.reports import write_review_artifact
from core.review_loop import split_review_actions


def _normalize_item(item: dict[str, object]) -> dict[str, object]:
    text = str(item.get("text", "")).strip()
    ambiguous = len(text.split()) < 3 or "maybe" in text.lower() or "consider" in text.lower()
    normalized = {
        "source_ref": str(item.get("source_ref", "")),
        "text": text,
        "category": str(item.get("category", "review")),
        "confidence": float(item.get("confidence", 0.5) or 0.5),
        "ambiguous": ambiguous or bool(item.get("ambiguous", False)),
        "review_required": True if ambiguous else bool(item.get("review_required", False)),
        "file": str(item.get("file", "")),
        "line": int(item.get("line", 0) or 0),
        "old_text": str(item.get("old_text", "")),
        "suggestions": item.get("suggestions", []),
        "span": item.get("span"),
        "code": str(item.get("code", "REVIEW_FEEDBACK")),
        "severity": str(item.get("severity", "warning")),
    }
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize bounded review feedback into structured issues")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--artifact")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    input_path = Path(args.input)
    artifact_path = Path(args.artifact) if args.artifact else project_root / "reports" / "review-ingest-artifact.json"
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    raw_items = payload.get("items", []) if isinstance(payload, dict) else []
    if not isinstance(raw_items, list):
        raw_items = []
    normalized_items = [_normalize_item(item) for item in raw_items if isinstance(item, dict)]
    selective_action = split_review_actions(str(project_root), normalized_items)
    write_review_artifact(
        artifact_path,
        artifact_type="feedback_ingest",
        summary={
            "project_root": str(project_root),
            "normalized_count": len(normalized_items),
            "ambiguous_count": sum(1 for item in normalized_items if item["ambiguous"]),
        },
        payload={
            "project_root": str(project_root),
            "normalized_items": normalized_items,
            "selective_action": selective_action,
        },
    )
    print(artifact_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
