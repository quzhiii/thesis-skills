"""
Citation mapping management for Zotero→LaTeX workflow.

Handles mapping between Zotero citation-keys and LaTeX reference numbers.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CitationMapping:
    """Manages Zotero citation-key to LaTeX ref number mapping."""

    root: Path
    mapping_file: Path
    mappings: dict[str, str] = field(default_factory=dict)
    next_ref_number: int = 1

    @classmethod
    def load(
        cls, project_root: str | Path, mapping_file: str = "ref/citation-mapping.json"
    ) -> "CitationMapping":
        """Load existing mapping or create new one."""
        root = Path(project_root).resolve()
        mapping_path = root / mapping_file

        mappings = {}
        next_ref = 1
        load_errors = []

        if mapping_path.exists():
            try:
                data = json.loads(mapping_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    mappings_raw = data.get("mappings", {})
                    # Validate mappings is a dict
                    if isinstance(mappings_raw, dict):
                        mappings = mappings_raw
                        # Find the next ref number
                        ref_numbers = []
                        for v in mappings.values():
                            if isinstance(v, str) and v.startswith("ref"):
                                try:
                                    num = int(v[3:])
                                    ref_numbers.append(num)
                                except ValueError:
                                    pass
                        if ref_numbers:
                            next_ref = max(ref_numbers) + 1
                    else:
                        load_errors.append(
                            f"Invalid mappings type: expected dict, got {type(mappings_raw).__name__}"
                        )
                else:
                    load_errors.append(
                        f"Invalid mapping file format: expected dict, got {type(data).__name__}"
                    )
            except json.JSONDecodeError as e:
                load_errors.append(f"Invalid JSON in mapping file: {e}")
            except IOError as e:
                load_errors.append(f"Error reading mapping file: {e}")

        # Log warnings if any issues occurred
        if load_errors:
            import warnings

            for error in load_errors:
                warnings.warn(f"CitationMapping.load: {error}")

        return cls(
            root=root,
            mapping_file=mapping_path,
            mappings=mappings,
            next_ref_number=next_ref,
        )

    def get_latex_key(self, zotero_key: str) -> str | None:
        """Get LaTeX key for a Zotero key."""
        return self.mappings.get(zotero_key)

    def get_or_create_latex_key(self, zotero_key: str) -> str:
        """Get existing LaTeX key or create new one."""
        if zotero_key in self.mappings:
            return self.mappings[zotero_key]

        latex_key = f"ref{self.next_ref_number:03d}"
        self.mappings[zotero_key] = latex_key
        self.next_ref_number += 1
        return latex_key

    def add_mapping(self, zotero_key: str, latex_key: str | None = None) -> str:
        """Add a new mapping. Returns the LaTeX key used."""
        if latex_key is None:
            return self.get_or_create_latex_key(zotero_key)

        self.mappings[zotero_key] = latex_key
        # Update next_ref_number if needed
        if latex_key.startswith("ref"):
            try:
                num = int(latex_key[3:])
                self.next_ref_number = max(self.next_ref_number, num + 1)
            except ValueError:
                pass
        return latex_key

    def get_all_latex_keys(self) -> set[str]:
        """Get all LaTeX keys in use."""
        return set(self.mappings.values())

    def get_all_zotero_keys(self) -> set[str]:
        """Get all Zotero keys in mapping."""
        return set(self.mappings.keys())

    def save(self, description: str | None = None) -> None:
        """Save mapping to file."""
        self.mapping_file.parent.mkdir(parents=True, exist_ok=True)

        data: dict[str, Any] = {
            "description": description
            or "Zotero citation-key to LaTeX ref number mapping",
            "version": "1.0",
            "mappings": self.mappings,
        }

        self.mapping_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def to_citation_lock_content(self) -> str:
        """Generate citation-lock.tex content."""
        keys = sorted(self.mappings.values(), key=lambda x: (len(x), x))
        return f"% Auto-generated citation lock file\n% Do not edit manually\n\\nocite{{{','.join(keys)}}}\n"


def parse_bib_keys(bib_content: str) -> set[str]:
    """Extract all citation keys from a bib file."""
    return set(re.findall(r"@\w+\s*\{\s*([^,\s]+)\s*,", bib_content))


def parse_bib_keys_from_files(bib_files: list[Path]) -> set[str]:
    """Extract all citation keys from multiple bib files."""
    keys = set()
    for bib_file in bib_files:
        if bib_file.exists():
            content = bib_file.read_text(encoding="utf-8", errors="ignore")
            keys |= parse_bib_keys(content)
    return keys


def parse_tex_citations(tex_content: str) -> list[str]:
    """Extract all \\cite{} keys from tex content."""
    pattern = re.compile(r"\\cite[a-zA-Z*]*\s*(?:\[[^\]]*\]\s*)?\{([^}]+)\}")
    citations = []
    for match in pattern.finditer(tex_content):
        for key in match.group(1).split(","):
            key = key.strip()
            if key:
                citations.append(key)
    return citations


def generate_citation_lock(latex_keys: list[str]) -> str:
    """Generate citation-lock.tex content from a list of LaTeX keys."""
    keys = sorted(latex_keys, key=lambda x: (len(x), x))
    return f"\\nocite{{{','.join(keys)}}}\n"
