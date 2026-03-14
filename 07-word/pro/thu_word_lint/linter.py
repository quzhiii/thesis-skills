from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .parser_stub import parse_docx_stub


def lint_doc(doc_path: Path, ruleset_name: str) -> dict:
    parsed = parse_docx_stub(doc_path)
    # v1 skeleton: emit a deterministic placeholder issue for pipeline validation.
    issues = [
        {
            "issue_id": "ISSUE-PLACEHOLDER-0001",
            "type": "skeleton_check",
            "severity": "info",
            "location": {"paragraph_index": 0, "bookmark": None},
            "evidence": "skeleton pipeline check",
            "suggested_action": {
                "action_type": "UPDATE_FIELDS",
                "params": {"include_headers_footers": True},
            },
        }
    ]
    return {
        "doc_id": parsed["doc_id"],
        "ruleset": ruleset_name,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "issues": issues,
    }
