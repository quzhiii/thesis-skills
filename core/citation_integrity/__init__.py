from __future__ import annotations

from core.citation_integrity.bib_parser import find_duplicate_key_groups, parse_bib_entries_from_text
from core.citation_integrity.external_models import (
    ExternalProviderEvidence,
    ExternalVerificationEntry,
    ExternalVerificationSummary,
)
from core.citation_integrity.hallucination_risk import (
    build_hallucination_risk_report,
    score_hallucination_risk,
    write_high_risk_csv,
    write_hallucination_risk_report,
)
from core.citation_integrity.models import BibEntry, CitationOccurrence, DuplicateKeyGroup
from core.citation_integrity.tex_parser import collect_citations_from_text

__all__ = [
    "BibEntry",
    "CitationOccurrence",
    "DuplicateKeyGroup",
    "ExternalProviderEvidence",
    "ExternalVerificationEntry",
    "ExternalVerificationSummary",
    "build_hallucination_risk_report",
    "collect_citations_from_text",
    "find_duplicate_key_groups",
    "parse_bib_entries_from_text",
    "score_hallucination_risk",
    "write_hallucination_risk_report",
    "write_high_risk_csv",
]
