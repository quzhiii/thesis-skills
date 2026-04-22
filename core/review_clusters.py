from __future__ import annotations


def _recommended_action(category: str) -> str:
    mapping = {
        "language": "Review wording issues together before deciding whether to patch locally",
        "argument": "Review claim strength and evidence scope before rewriting",
        "structure": "Review structural changes as a grouped revision task",
        "citation": "Review bibliography and citation consistency before editing prose",
    }
    return mapping.get(category, "Review grouped issues and decide between TODOs and candidate patches")


def build_review_clusters(items: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = {}
    for item in items:
        category = str(item.get("category", "uncategorized"))
        grouped.setdefault(category, []).append(item)
    clusters: list[dict[str, object]] = []
    for category in sorted(grouped):
        members = grouped[category]
        files = sorted({str(item.get("file", "")) for item in members if item.get("file")})
        clusters.append(
            {
                "category": category,
                "issue_count": len(members),
                "affected_files_count": len(files),
                "affected_files": files,
                "recommended_action": _recommended_action(category),
                "review_focus": f"Review repeated {category} issues before applying changes",
            }
        )
    return clusters
