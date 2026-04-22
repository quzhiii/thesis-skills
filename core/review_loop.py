from __future__ import annotations

from core.patches import build_patch_from_review_item


def split_review_actions(
    project_root: str,
    feedback_items: list[dict[str, object]],
) -> dict[str, object]:
    todos: list[dict[str, object]] = []
    candidate_patches: list[dict[str, object]] = []
    blocked: list[dict[str, object]] = []

    for item in feedback_items:
        ambiguous = bool(item.get("ambiguous", False))
        review_required = bool(item.get("review_required", True))
        confidence = float(item.get("confidence", 0.0) or 0.0)
        if ambiguous:
            blocked.append({**item, "reason": "ambiguous"})
            continue
        if review_required and confidence < 0.9:
            todos.append({**item, "reason": "review_required"})
            continue
        patch, reason = build_patch_from_review_item(project_root, item)
        if patch is None:
            if reason == "review_required":
                todos.append({**item, "reason": reason})
            else:
                blocked.append({**item, "reason": reason or "blocked"})
            continue
        candidate_patches.append({**item, **patch.as_dict()})

    return {
        "todos": todos,
        "candidate_patches": candidate_patches,
        "blocked": blocked,
        "summary": {
            "todo_count": len(todos),
            "candidate_patch_count": len(candidate_patches),
            "blocked_count": len(blocked),
        },
    }
