from __future__ import annotations

from datetime import datetime, timezone


def build_fix_plan(report: dict) -> dict:
    actions: list[dict] = []
    for idx, issue in enumerate(report.get("issues", []), start=1):
        action = issue.get("suggested_action", {})
        actions.append(
            {
                "action_id": f"ACT-{idx:04d}",
                "action_type": action.get("action_type", "UPDATE_FIELDS"),
                "target": issue.get("location", {}),
                "params": action.get("params", {}),
                "preconditions": ["target exists"],
                "rollback_hint": "restore previous document snapshot",
            }
        )

    return {
        "plan_id": "PLAN-SKELETON-0001",
        "doc_id": report.get("doc_id", "unknown.docx"),
        "ruleset": report.get("ruleset", "thu_v1"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "actions": actions,
    }
