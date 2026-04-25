from __future__ import annotations

from typing import Any


def build_chapter_summaries(review_queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build per-chapter summaries from a prioritized review queue.

    Each summary is deterministic, inspectable, and bounded to counts +
    categories.  It does not synthesize free-form interpretation.
    """
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in review_queue:
        file_path = str(item.get("file", ""))
        if not file_path:
            continue
        grouped.setdefault(file_path, []).append(item)

    summaries: list[dict[str, Any]] = []
    for chapter_file in sorted(grouped):
        members = grouped[chapter_file]
        categories = sorted({str(item.get("category", "uncategorized")) for item in members})
        priority_breakdown: dict[str, int] = {"high": 0, "medium": 0, "low": 0}
        for item in members:
            priority = str(item.get("priority", "medium"))
            if priority in priority_breakdown:
                priority_breakdown[priority] += 1
            else:
                priority_breakdown["medium"] += 1

        issue_count = len(members)
        parts: list[str] = []
        if priority_breakdown["high"]:
            parts.append(f"{priority_breakdown['high']} high")
        if priority_breakdown["medium"]:
            parts.append(f"{priority_breakdown['medium']} medium")
        if priority_breakdown["low"]:
            parts.append(f"{priority_breakdown['low']} low")
        summary_text = f"{issue_count} issues ({', '.join(parts)}) across categories: {', '.join(categories)}"

        summaries.append(
            {
                "chapter_file": chapter_file,
                "issue_count": issue_count,
                "categories": categories,
                "priority_breakdown": priority_breakdown,
                "summary_text": summary_text,
            }
        )

    return summaries
