from __future__ import annotations

from pathlib import Path


def parse_docx_stub(doc_path: Path) -> dict:
    # v1 skeleton: placeholder parser metadata only.
    return {
        "doc_id": doc_path.name,
        "paragraph_count": 0,
        "table_count": 0,
        "notes": "Parser not implemented in skeleton; wire python-docx or COM in next step.",
    }
