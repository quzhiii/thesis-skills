from __future__ import annotations

from core.canonicalize import guess_langid, normalize_doi, normalize_entry_type
from core.citation_models import CanonicalRef


def _format_authors(ref: CanonicalRef) -> str | None:
    if not ref.authors:
        return None
    return " and ".join(
        f"{author.family}, {author.given}".strip().rstrip(",")
        for author in ref.authors
        if author.family or author.given
    )


def canonical_ref_to_bibtex(ref: CanonicalRef, latex_key: str) -> str:
    entry_type = normalize_entry_type(ref.entry_type)
    if entry_type == "misc" and ref.entry_type not in {
        "misc",
        "article",
        "book",
        "inproceedings",
        "online",
        "phdthesis",
        "mastersthesis",
    }:
        entry_type = "misc"

    fields: list[tuple[str, str]] = []
    author_value = _format_authors(ref)
    langid = ref.langid or guess_langid(ref)
    doi = normalize_doi(ref.doi)

    for key, value in [
        ("author", author_value),
        ("title", ref.title),
        ("journal", ref.journal),
        ("booktitle", ref.booktitle),
        ("publisher", ref.publisher),
        ("year", ref.year),
        ("doi", doi),
        ("isbn", ref.isbn),
        ("issn", ref.issn),
        ("langid", langid),
    ]:
        if value:
            fields.append((key, value))

    lines = [f"@{entry_type}{{{latex_key},"]
    for key, value in fields:
        lines.append(f"  {key} = {{{value}}},")
    lines.append("}")
    return "\n".join(lines)


def render_bib_file(refs: list[CanonicalRef], mapping: dict[str, str]) -> str:
    rendered_entries: list[tuple[str, str]] = []
    for ref in refs:
        latex_key = mapping.get(ref.canonical_id)
        if not latex_key:
            continue
        rendered_entries.append((latex_key, canonical_ref_to_bibtex(ref, latex_key)))

    rendered_entries.sort(key=lambda item: item[0])
    return "\n\n".join(entry for _, entry in rendered_entries)
