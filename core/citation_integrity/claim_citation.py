from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from core.citation_integrity.models import BibEntry, CitationWithContext


HALLUCINATION_RISK_BASE: dict[str, float] = {
    "PASS": 0.0,
    "WARN": 0.10,
    "REVIEW": 0.25,
    "HIGH_RISK": 0.50,
}

SCORE_MISSING_RISK_LABEL = 0.30
SCORE_MISSING_BIB_ENTRY = 0.50
SCORE_MISSING_METADATA = 0.10
SCORE_BARE_CONTEXT = 0.15
SCORE_EXTRA_CITATION_KEY = 0.05
SCORE_SINGLE_CITATION = 0.05
SCORE_OVER_CITATION = 0.05
OVER_CITATION_THRESHOLD = 10

_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "were",
    "with",
}

_CLAIM_TYPE_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
    ("empirical_result", ("improve", "increase", "decrease", "significant", "outperform", "achieve", "accuracy", "results")),
    ("method_claim", ("propose", "introduce", "use", "based on", "framework", "method", "approach")),
    ("background", ("prior work", "studies", "literature", "has explored", "have explored", "work explored")),
    ("definition", ("defined as", "refers to", "means", "is defined")),
]

LABEL_THRESHOLDS: list[tuple[float, str]] = [
    (0.0, "WELL_SUPPORTED"),
    (0.25, "SUPPORTED"),
    (0.50, "WEAK"),
]


def _label_for_score(score: float, bib_entry_exists: bool) -> str:
    if not bib_entry_exists and score >= 0.50:
        return "ORPHANED"
    for threshold, label in LABEL_THRESHOLDS:
        if score == 0.0:
            return "WELL_SUPPORTED"
        if score < threshold:
            return label
    return "WEAK"


def _recommended_action(triage_label: str, hallucination_risk_label: str | None) -> str:
    if triage_label == "UNVERIFIABLE":
        return "Cited reference is UNSUPPORTED in V3.0 hallucination risk check and cannot be automatically verified."
    if triage_label == "ORPHANED":
        return "Citation key not found in bibliography. Add the missing entry or fix the citation key."
    if triage_label == "WEAK":
        if hallucination_risk_label == "HIGH_RISK":
            return "Cited reference has HIGH_RISK hallucination risk. Manual verification strongly recommended."
        return f"Cited reference has weak structural support (risk={hallucination_risk_label}). Consider verifying the source manually."
    if triage_label == "SUPPORTED":
        return "Reference appears structurally adequate but may have minor risks."
    return "Cited reference is well-supported with complete metadata and low hallucination risk."


def _claim_type(context: str) -> str:
    text = context.lower()
    if not text.strip():
        return "unclear"
    for label, patterns in _CLAIM_TYPE_PATTERNS:
        if any(pattern in text for pattern in patterns):
            return label
    return "unclear"


def _tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9_-]+", text.lower())
        if len(token) > 2 and token not in _STOPWORDS
    }


def _metadata_overlap(context: str, bib_entry: BibEntry | None) -> dict[str, object]:
    if bib_entry is None:
        return {"title_token_overlap": 0.0, "overlap_tokens": []}
    context_tokens = _tokens(context)
    title_tokens = _tokens(bib_entry.fields.get("title", ""))
    if not context_tokens or not title_tokens:
        return {"title_token_overlap": 0.0, "overlap_tokens": []}
    overlap = sorted(context_tokens & title_tokens)
    denominator = max(1, len(context_tokens | title_tokens))
    return {
        "title_token_overlap": round(len(overlap) / denominator, 4),
        "overlap_tokens": overlap,
    }


def _support_review(
    label: str,
    hallucination_label: str | None,
    claim_type: str,
    metadata_overlap: dict[str, object],
    has_complete_metadata: bool,
    has_claim_context: bool,
) -> tuple[str, str, list[str], list[str], list[str]]:
    support_signals: list[str] = []
    risk_signals: list[str] = []
    next_actions: list[str] = []

    if has_complete_metadata:
        support_signals.append("complete_metadata")
    else:
        risk_signals.append("incomplete_metadata")

    if has_claim_context:
        support_signals.append("has_claim_context")
    else:
        risk_signals.append("bare_context")

    if hallucination_label == "PASS":
        support_signals.append("low_hallucination_risk")
    elif hallucination_label in {"REVIEW", "HIGH_RISK"}:
        risk_signals.append(f"{hallucination_label.lower()}_reference")
    elif hallucination_label == "UNSUPPORTED":
        risk_signals.append("unsupported_reference")
    elif hallucination_label is None:
        risk_signals.append("missing_hallucination_evidence")

    overlap_score = float(metadata_overlap.get("title_token_overlap") or 0.0)
    if overlap_score > 0:
        support_signals.append("metadata_title_overlap")

    if claim_type == "empirical_result" and overlap_score == 0.0:
        risk_signals.append("empirical_claim_without_title_overlap")

    if label == "ORPHANED":
        next_actions.append("Fix the citation key or add the missing bibliography entry after manual confirmation.")
        return "ORPHANED", "Citation key is missing from the bibliography.", support_signals, risk_signals, next_actions

    if label == "UNVERIFIABLE":
        next_actions.append("Manually verify the source because current evidence cannot automatically assess it.")
        return "UNVERIFIABLE", "Reference is unsupported by the current automatic evidence layer.", support_signals, risk_signals, next_actions

    if "high_risk_reference" in risk_signals:
        next_actions.append("Verify the cited source against DOI, publisher, database, or original document evidence.")
        return "NEEDS_MANUAL_REVIEW", "Cited reference carries HIGH_RISK hallucination evidence.", support_signals, risk_signals, next_actions

    if label == "WEAK":
        next_actions.append("Check whether this reference directly supports the nearby claim or add a closer source.")
        return "WEAK_REVIEW", "Evidence is structurally weak or incomplete.", support_signals, risk_signals, next_actions

    if risk_signals:
        next_actions.append("Review the citation context and metadata before final submission.")
        return "ADEQUATE_REVIEW", "Evidence appears adequate with minor caveats.", support_signals, risk_signals, next_actions

    next_actions.append("No immediate action; keep available for final human review.")
    return "STRONG_REVIEW", "Evidence is structurally strong and low-risk.", support_signals, risk_signals, next_actions


def triage_claim_citation(
    context: CitationWithContext,
    bib_entry: BibEntry | None,
    hallucination_entry: dict[str, object] | None,
    citation_frequency: int,
    group_size: int = 1,
) -> dict[str, object]:
    hallucination_label = None
    hallucination_score_val = None
    if isinstance(hallucination_entry, dict):
        hallucination_label = str(hallucination_entry.get("risk_label", ""))

    if hallucination_label == "UNSUPPORTED":
        return _build_triage_result(
            context,
            bib_entry,
            None,
            "UNVERIFIABLE",
            hallucination_label,
            None,
            citation_frequency,
            group_size,
        )

    score = 0.0

    if bib_entry is None:
        score += SCORE_MISSING_BIB_ENTRY
    else:
        if not bib_entry.fields.get("title") or not bib_entry.fields.get("author"):
            score += SCORE_MISSING_METADATA

    base = HALLUCINATION_RISK_BASE.get(hallucination_label or "", SCORE_MISSING_RISK_LABEL)
    score += base
    if hallucination_label is None:
        pass
    elif hallucination_label not in HALLUCINATION_RISK_BASE:
        score += SCORE_MISSING_RISK_LABEL

    if not context.context.strip():
        score += SCORE_BARE_CONTEXT

    if group_size > 1:
        score += SCORE_EXTRA_CITATION_KEY * (group_size - 1)

    if citation_frequency == 1:
        score += SCORE_SINGLE_CITATION
    if citation_frequency > OVER_CITATION_THRESHOLD:
        score += SCORE_OVER_CITATION

    label = _label_for_score(score, bib_entry is not None)

    return _build_triage_result(
        context,
        bib_entry,
        score,
        label,
        hallucination_label,
        hallucination_score_val,
        citation_frequency,
        group_size,
    )


def _build_triage_result(
    context: CitationWithContext,
    bib_entry: BibEntry | None,
    score: float | None,
    label: str,
    hallucination_label: str | None,
    hallucination_score_val: float | None,
    citation_frequency: int,
    group_size: int,
) -> dict[str, object]:
    reference_metadata: dict[str, str] = {}
    has_complete_metadata = False
    if bib_entry is not None:
        for k in ("title", "author", "year"):
            if bib_entry.fields.get(k):
                reference_metadata[k] = bib_entry.fields[k]
        has_complete_metadata = bool(reference_metadata.get("title") and reference_metadata.get("author"))

    claim_type = _claim_type(context.context)
    metadata_overlap = _metadata_overlap(context.context, bib_entry)
    support_review_label, support_review_reason, support_signals, risk_signals, next_actions = _support_review(
        label,
        hallucination_label,
        claim_type,
        metadata_overlap,
        has_complete_metadata,
        bool(context.context.strip()),
    )

    return {
        "citation_key": context.key,
        "triage_label": label,
        "triage_score": round(score, 4) if score is not None else None,
        "claim_type": claim_type,
        "support_review_label": support_review_label,
        "support_review_reason": support_review_reason,
        "claim_context": context.context,
        "citation_command": context.command,
        "file": context.file,
        "line": context.line,
        "reference_metadata": reference_metadata,
        "hallucination_risk_label": hallucination_label,
        "citation_frequency": citation_frequency,
        "support_signals": support_signals,
        "risk_signals": risk_signals,
        "evidence": {
            "has_complete_metadata": has_complete_metadata,
            "has_claim_context": bool(context.context.strip()),
            "is_grouped_citation": group_size > 1,
            "group_size": group_size,
            **metadata_overlap,
        },
        "recommended_action": _recommended_action(label, hallucination_label),
        "next_actions": next_actions,
    }


def _build_entries(
    contexts: list[CitationWithContext],
    bib_entries: list[BibEntry],
    hallucination_report: dict[str, object] | None,
) -> list[dict[str, object]]:
    bib_by_key: dict[str, BibEntry] = {}
    for entry in bib_entries:
        if entry.key not in bib_by_key:
            bib_by_key[entry.key] = entry

    risk_by_key: dict[str, dict[str, object]] = {}
    if isinstance(hallucination_report, dict):
        entries = hallucination_report.get("entries")
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict):
                    key = str(e.get("citation_key", ""))
                    if key:
                        risk_by_key[key] = e

    freq: dict[str, int] = {}
    for ctx in contexts:
        freq[ctx.key] = freq.get(ctx.key, 0) + 1

    group_counts: dict[tuple[str, str, int], int] = {}
    for ctx in contexts:
        key = (ctx.file, ctx.command, ctx.line)
        group_counts[key] = group_counts.get(key, 0) + 1

    results: list[dict[str, object]] = []
    for ctx in contexts:
        bib_entry = bib_by_key.get(ctx.key)
        risk_entry = risk_by_key.get(ctx.key)
        f = freq.get(ctx.key, 0)
        gs = group_counts.get((ctx.file, ctx.command, ctx.line), 1)
        results.append(triage_claim_citation(ctx, bib_entry, risk_entry, f, gs))
    return results


def _compute_report_status(entries: list[dict[str, object]]) -> str:
    labels = {e.get("triage_label") for e in entries}
    for st in ("ORPHANED", "WEAK", "UNVERIFIABLE", "SUPPORTED", "WELL_SUPPORTED"):
        if st in labels:
            return st
    return "PASS"


def _compute_claim_summary(triage_entries: list[dict[str, object]], contexts: list[CitationWithContext], bib_entries: list[BibEntry]) -> dict[str, object]:
    cited_keys = {ctx.key for ctx in contexts}
    bib_keys = {entry.key for entry in bib_entries}
    uncited_keys = bib_keys - cited_keys

    counts: dict[str, int] = {
        "well_supported_pairs": 0,
        "supported_pairs": 0,
        "weak_pairs": 0,
        "orphaned_pairs": 0,
        "unverifiable_pairs": 0,
    }
    for entry in triage_entries:
        label = str(entry.get("triage_label", ""))
        key = label.lower() + "_pairs"
        if key in counts:
            counts[key] += 1

    return {
        "claim_citation_pairs": len(triage_entries),
        **counts,
        "unique_references_cited": len(cited_keys),
        "unique_references_never_cited": len(uncited_keys),
    }


def _uncited_references(
    triage_entries: list[dict[str, object]],
    contexts: list[CitationWithContext],
    bib_entries: list[BibEntry],
    hallucination_report: dict[str, object] | None,
) -> list[dict[str, object]]:
    cited_keys = {ctx.key for ctx in contexts}
    risk_by_key: dict[str, str] = {}
    if isinstance(hallucination_report, dict):
        entries = hallucination_report.get("entries")
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict):
                    key = str(e.get("citation_key", ""))
                    if key:
                        risk_by_key[key] = str(e.get("risk_label", ""))

    uncited: list[dict[str, object]] = []
    seen: set[str] = set()
    for entry in sorted(bib_entries, key=lambda e: (e.key, e.file, e.line)):
        if entry.key in cited_keys or entry.key in seen:
            continue
        seen.add(entry.key)
        uncited.append({
            "citation_key": entry.key,
            "title": entry.fields.get("title", ""),
            "hallucination_risk_label": risk_by_key.get(entry.key),
        })
    return uncited


def build_claim_citation_report(
    contexts: list[CitationWithContext],
    bib_entries: list[BibEntry],
    hallucination_report: dict[str, object] | None = None,
) -> dict[str, object]:
    triage_entries = _build_entries(contexts, bib_entries, hallucination_report)
    return {
        "module": "claim_citation_triage",
        "version": "3.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": _compute_report_status(triage_entries),
        "summary": _compute_claim_summary(triage_entries, contexts, bib_entries),
        "entries": triage_entries,
        "uncited_references": _uncited_references(triage_entries, contexts, bib_entries, hallucination_report),
    }


def write_claim_citation_report_json(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


_LABEL_GROUP_ORDER: list[str] = [
    "ORPHANED",
    "UNVERIFIABLE",
    "WEAK",
    "SUPPORTED",
    "WELL_SUPPORTED",
]


def render_claim_citation_markdown(report: dict[str, object]) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    entries: list[dict[str, object]] = report.get("entries") if isinstance(report.get("entries"), list) else []
    by_label: dict[str, list[dict[str, object]]] = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        label = str(e.get("triage_label", ""))
        by_label.setdefault(label, []).append(e)

    lines = [
        "# Claim-Citation Triage Report",
        "",
        f"**Status:** {report.get('status', 'UNKNOWN')}",
        "",
        "## Summary",
        "",
    ]
    for key in sorted(summary):
        lines.append(f"- `{key}`: {summary[key]}")
    lines.append("")

    for label in _LABEL_GROUP_ORDER:
        group = by_label.get(label, [])
        if not group:
            continue
        lines.append(f"## {label}")
        lines.append("")
        for entry in sorted(group, key=lambda e: (str(e.get("file", "")), int(e.get("line") or 0))):
            file = entry.get("file", "")
            line_num = entry.get("line", "")
            claim = str(entry.get("claim_context", "") or "")
            key = entry.get("citation_key", "")
            score = entry.get("triage_score", "")
            risk = entry.get("hallucination_risk_label", "")
            review = entry.get("support_review_label", "")
            reason = entry.get("support_review_reason", "")
            action = entry.get("recommended_action", "")
            lines.append(f"- `{key}` {file}:{line_num} (score={score}, risk={risk}, review={review})")
            if reason:
                lines.append(f"  - {reason}")
            if claim:
                lines.append(f"  > {claim}")
            if action:
                lines.append(f"  *{action}*")
            lines.append("")
    return "\n".join(lines) + "\n"


def write_claim_citation_report_md(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_claim_citation_markdown(report), encoding="utf-8")


_CSV_FIELDNAMES = [
    "citation_key",
    "triage_label",
    "triage_score",
    "claim_type",
    "support_review_label",
    "support_review_reason",
    "claim_context",
    "file",
    "line",
    "hallucination_risk_label",
    "citation_frequency",
    "support_signals",
    "risk_signals",
    "recommended_action",
    "next_actions",
]


def write_claim_citation_report_csv(report: dict[str, object], output: str | Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, object]] = report.get("entries") if isinstance(report.get("entries"), list) else []
    non_pass = [e for e in entries if isinstance(e, dict) and e.get("triage_label") != "WELL_SUPPORTED"]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_CSV_FIELDNAMES)
        writer.writeheader()
        for entry in sorted(non_pass, key=lambda e: (str(e.get("file", "")), int(e.get("line") or 0))):
            row = {key: entry.get(key, "") for key in _CSV_FIELDNAMES}
            for key in ("support_signals", "risk_signals", "next_actions"):
                value = row.get(key)
                if isinstance(value, list):
                    row[key] = "; ".join(str(item) for item in value)
            writer.writerow(row)
