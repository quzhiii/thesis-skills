"""
Core modules for thesis-skills.

This package provides:
- Project discovery and configuration (project.py)
- Rule pack management (rules.py)
- Citation extraction and mapping (zotero_extract.py, citation_mapping.py)
- Checkers and fixers (checkers.py, fixers.py)
- Report generation (reports.py)
- Word to LaTeX migration (migration.py)
"""

from __future__ import annotations

# Import key modules for convenience
from core.project import ThesisProject
from core.rules import RulePack, find_rule_pack, load_rule_pack
from core.citation_mapping import CitationMapping
from core.zotero_extract import (
    ZoteroCitation,
    ZoteroExtractionResult,
    extract_zotero_citations,
)
from core.common import Finding
from core.reports import write_report

__all__ = [
    "ThesisProject",
    "RulePack",
    "find_rule_pack",
    "load_rule_pack",
    "CitationMapping",
    "ZoteroCitation",
    "ZoteroExtractionResult",
    "extract_zotero_citations",
    "Finding",
    "write_report",
]
