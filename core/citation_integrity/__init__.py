from __future__ import annotations

from core.citation_integrity.bib_parser import find_duplicate_key_groups, parse_bib_entries_from_text
from core.citation_integrity.external_models import (
    ExternalProviderEvidence,
    ExternalVerificationEntry,
    ExternalVerificationSummary,
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
    "collect_citations_from_text",
    "find_duplicate_key_groups",
    "parse_bib_entries_from_text",
]
