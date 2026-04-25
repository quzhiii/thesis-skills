from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.chapter_summary import build_chapter_summaries
from core.reports import write_review_artifact
from core.review_clusters import build_review_clusters
from core.review_queue import build_review_queue


def _load_report(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build review package and triage artifacts")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--artifact")
    parser.add_argument("--revision-id")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    reports_dir = project_root / "reports"
    artifact_path = Path(args.artifact) if args.artifact else reports_dir / "review-diff-artifact.json"
    revision_id = args.revision_id or datetime.now(timezone.utc).strftime("review-%Y%m%dT%H%M%SZ")

    report_refs: list[str] = []
    findings: list[dict[str, object]] = []
    for report_name in [
        "check_language_deep-report.json",
        "check_compile-report.json",
        "check_content-report.json",
        "check_format-report.json",
    ]:
        report = _load_report(reports_dir / report_name)
        if not report:
            continue
        report_refs.append(f"reports/{report_name}")
        raw_findings = report.get("findings", [])
        if isinstance(raw_findings, list):
            for item in raw_findings:
                if isinstance(item, dict):
                    findings.append(item)

    source_files = [project_root / "main.tex"]
    source_files.extend(sorted(project_root.glob("chapters/*.tex")))
    changed_scope = [path.relative_to(project_root).as_posix() for path in source_files if path.exists()]
    review_queue = build_review_queue(findings)
    review_clusters = build_review_clusters(review_queue)
    review_digest = {
        "total_items": len(review_queue),
        "high_priority_items": sum(1 for item in review_queue if item.get("priority") == "high"),
        "cluster_count": len(review_clusters),
    }
    chapter_summaries = build_chapter_summaries(review_queue)
    payload = {
        "project_root": str(project_root),
        "revision_id": revision_id,
        "changed_scope": changed_scope,
        "report_references": report_refs,
        "review_queue": review_queue,
        "review_clusters": review_clusters,
        "review_digest": review_digest,
        "chapter_summaries": chapter_summaries,
    }
    write_review_artifact(
        artifact_path,
        artifact_type="review_package",
        summary={
            "revision_id": revision_id,
            "project_root": str(project_root),
            "report_reference_count": len(report_refs),
            "changed_scope_count": len(changed_scope),
        },
        payload=payload,
    )
    print(artifact_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
