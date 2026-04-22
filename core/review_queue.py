from __future__ import annotations


_SEVERITY_RANK = {"error": 0, "warning": 1, "info": 2}
_PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}


def _priority_for_item(item: dict[str, object]) -> str:
    if bool(item.get("review_required", False)):
        return "high"
    severity = str(item.get("severity", "warning"))
    confidence = float(item.get("confidence", 0.0) or 0.0)
    if severity == "error":
        return "high"
    if confidence >= 0.85:
        return "high"
    if severity == "info":
        return "low"
    return "medium"


def build_review_queue(items: list[dict[str, object]]) -> list[dict[str, object]]:
    queue: list[dict[str, object]] = []
    for item in items:
        payload = dict(item)
        payload["priority"] = _priority_for_item(item)
        queue.append(payload)
    return sorted(
        queue,
        key=lambda item: (
            _PRIORITY_RANK.get(str(item.get("priority", "medium")), 1),
            _SEVERITY_RANK.get(str(item.get("severity", "warning")), 1),
            str(item.get("category", "")),
            str(item.get("file", "")),
            int(item.get("line", 0) or 0),
        ),
    )
