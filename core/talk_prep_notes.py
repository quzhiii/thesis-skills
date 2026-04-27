from __future__ import annotations

from typing import Any

from core.candidate_tables_diagrams import build_candidate_tables_diagrams
from core.chapter_highlights import _infer_defense_role
from core.defense_outline import _extract_chapter_title, _extract_key_points
from core.project import ThesisProject


_TALK_GOALS = {
    "background": "Set up the research context and question.",
    "approach": "Explain the approach and why it is credible.",
    "evidence": "Present the evidence and the main takeaways.",
    "takeaway": "Close with the contribution and next step.",
    "supporting": "Provide supporting details without losing the main thread.",
}

_TRANSITIONS = {
    "background": "Transition into how the study was designed to answer the question.",
    "approach": "Transition into the evidence produced by this approach.",
    "evidence": "Transition into the contribution and closing takeaway.",
    "takeaway": "Transition into questions or discussion if needed.",
    "supporting": "Transition back to the main defense storyline.",
}


def _visual_candidates_for_chapter(
    chapter_rel: str,
    candidate_payload: dict[str, Any],
) -> list[str]:
    labels: list[str] = []
    for key in ("diagrams", "tables"):
        entries = candidate_payload.get(key, [])
        if not isinstance(entries, list):
            continue
        for item in entries:
            if not isinstance(item, dict):
                continue
            if str(item.get("source_chapter", "")) != chapter_rel:
                continue
            label = str(item.get("label", "")).strip()
            if not label:
                continue
            labels.append(label)
    return labels


def build_talk_prep_notes(project: ThesisProject) -> dict[str, Any]:
    candidate_payload = build_candidate_tables_diagrams(project)
    notes: list[dict[str, Any]] = []
    for chapter_path in project.chapter_files:
        raw_text = chapter_path.read_text(encoding="utf-8", errors="ignore")
        chapter = _extract_chapter_title(raw_text, chapter_path)
        defense_role = _infer_defense_role(chapter)
        chapter_rel = project.rel(chapter_path)
        notes.append(
            {
                "chapter": chapter,
                "source_chapter": chapter_rel,
                "defense_role": defense_role,
                "talk_goal": _TALK_GOALS[defense_role],
                "talking_points": _extract_key_points(raw_text),
                "visual_candidates": _visual_candidates_for_chapter(chapter_rel, candidate_payload),
                "transition_note": _TRANSITIONS[defense_role],
            }
        )

    return {
        "title": "Defense Talk Prep Notes",
        "notes": notes,
    }
