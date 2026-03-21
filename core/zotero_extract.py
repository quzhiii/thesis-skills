"""
Zotero citation extraction from Word docx files.

Extracts embedded CSL_CITATION JSON objects from Word document.xml.
"""

from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass, field
from html import unescape
from pathlib import Path
from typing import Any


@dataclass
class ZoteroCitation:
    """Represents a single Zotero citation extracted from Word."""

    zotero_key: str
    item_data: dict[str, Any]
    position: int = 0  # Order of appearance in document

    @property
    def title(self) -> str | None:
        return self.item_data.get("title")

    @property
    def authors(self) -> list[str]:
        authors = []
        for author in self.item_data.get("author", []):
            if isinstance(author, dict):
                given = author.get("given", "")
                family = author.get("family", "")
                if family:
                    authors.append(f"{family} {given}".strip())
        return authors

    @property
    def year(self) -> str | None:
        return (
            self.item_data.get("issued", {}).get("date-parts", [[None]])[0][0]
            if self.item_data.get("issued")
            else None
        )

    @property
    def entry_type(self) -> str:
        return self.item_data.get("type", "article")

    def to_bibtex_stub(self, latex_key: str) -> str:
        """Generate a BibTeX stub for this citation."""
        lines = [f"@{self.entry_type}{{{latex_key},"]

        if self.authors:
            author_str = " and ".join(self.authors)
            lines.append(f"  author = {{{author_str}}},")

        if self.title:
            lines.append(f"  title = {{{self.title}}},")

        if self.year:
            lines.append(f"  year = {{{self.year}}},")

        lines.append("  note = {TODO: complete from Zotero export},")
        lines.append("}")
        return "\n".join(lines)


@dataclass
class ZoteroExtractionResult:
    """Result of extracting Zotero citations from a Word file."""

    source_file: Path
    citations: list[ZoteroCitation] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def citation_count(self) -> int:
        return len(self.citations)

    @property
    def zotero_keys(self) -> set[str]:
        return {c.zotero_key for c in self.citations}

    def get_citations_by_key(self) -> dict[str, ZoteroCitation]:
        return {c.zotero_key: c for c in self.citations}


def extract_zotero_citations(docx_path: str | Path) -> ZoteroExtractionResult:
    """
    Extract all Zotero citations from a Word docx file.

    Zotero stores citations as CSL_CITATION JSON objects embedded in
    Word field codes (w:instrText elements in document.xml).
    """
    path = Path(docx_path)
    result = ZoteroExtractionResult(source_file=path)

    if not path.exists():
        result.errors.append(f"File not found: {path}")
        return result

    if not path.suffix.lower() == ".docx":
        result.errors.append(f"Not a docx file: {path}")
        return result

    try:
        with zipfile.ZipFile(path, "r") as z:
            try:
                with z.open("word/document.xml") as f:
                    content = f.read().decode("utf-8")
            except KeyError:
                result.errors.append("Invalid docx: missing word/document.xml")
                return result
            except UnicodeDecodeError as e:
                result.errors.append(f"Unicode decode error in document.xml: {e}")
                return result
    except zipfile.BadZipFile:
        result.errors.append(f"Invalid zip file: {path}")
        return result
    except PermissionError:
        result.errors.append(f"Permission denied: {path}")
        return result
    except OSError as e:
        result.errors.append(f"OS error reading {path}: {e}")
        return result

    # Extract all instrText elements
    instr_texts = re.findall(r"<w:instrText[^>]*>([^<]*)</w:instrText>", content)

    # Merge all fragments and decode XML entities
    full_text = unescape("".join(instr_texts))

    # Find all JSON objects
    json_objects = _extract_json_objects(full_text)

    # Extract citations in order of appearance
    seen_keys = set()
    position = 0

    for obj in json_objects:
        if "citationItems" in obj:
            for item in obj["citationItems"]:
                if "itemData" in item:
                    item_data = item["itemData"]
                    key = item_data.get("citation-key", str(item.get("id", "unknown")))

                    if key not in seen_keys:
                        seen_keys.add(key)
                        citation = ZoteroCitation(
                            zotero_key=key, item_data=item_data, position=position
                        )
                        result.citations.append(citation)
                        position += 1

    return result


def _extract_json_objects(text: str) -> list[dict[str, Any]]:
    """Extract all JSON objects from text using string-aware parsing."""
    objects = []
    i = 0

    while i < len(text):
        start = text.find("{", i)
        if start == -1:
            break

        # Find matching closing brace with string awareness
        depth = 0
        end = start
        in_string = False
        escape_next = False

        for j in range(start, len(text)):
            ch = text[j]

            # Handle escape sequences in strings
            if escape_next:
                escape_next = False
                continue

            if ch == "\\" and in_string:
                escape_next = True
                continue

            # Handle string boundaries
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue

            # Only count braces outside strings
            if not in_string:
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end = j + 1
                        break

        if end > start:
            json_str = text[start:end]
            try:
                data = json.loads(json_str)
                if isinstance(data, dict):
                    objects.append(data)
            except json.JSONDecodeError:
                pass

        i = end if end > start else start + 1

    return objects


def compare_citations(
    word_citations: ZoteroExtractionResult, existing_mapping: dict[str, str]
) -> dict[str, Any]:
    """
    Compare Word citations with existing mapping.

    Returns:
        - new_keys: Zotero keys in Word but not in mapping
        - removed_keys: Zotero keys in mapping but not in Word
        - unchanged_keys: Keys present in both
    """
    word_keys = word_citations.zotero_keys
    mapped_keys = set(existing_mapping.keys())

    new_keys = word_keys - mapped_keys
    removed_keys = mapped_keys - word_keys
    unchanged_keys = word_keys & mapped_keys

    return {
        "new_keys": new_keys,
        "removed_keys": removed_keys,
        "unchanged_keys": unchanged_keys,
        "word_citation_count": len(word_keys),
        "mapped_citation_count": len(mapped_keys),
    }
