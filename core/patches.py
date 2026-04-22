from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TextPatch:
    file: str
    start: dict[str, int]
    end: dict[str, int]
    old_text: str
    new_text: str
    issue_code: str
    confidence: float
    review_required: bool = True
    category: str = ""

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "file": self.file,
            "start": self.start,
            "end": self.end,
            "old_text": self.old_text,
            "new_text": self.new_text,
            "issue_code": self.issue_code,
            "confidence": self.confidence,
        }
        payload["review_required"] = self.review_required
        if self.category:
            payload["category"] = self.category
        return payload


def _line_offsets(text: str) -> list[int]:
    offsets: list[int] = []
    offset = 0
    for line in text.splitlines(keepends=True):
        offsets.append(offset)
        offset += len(line)
    if not offsets:
        offsets.append(0)
    return offsets


def patch_offsets(text: str, patch: TextPatch) -> tuple[int, int]:
    line_offsets = _line_offsets(text)
    start_line = patch.start["line"]
    end_line = patch.end["line"]
    if start_line < 1 or start_line > len(line_offsets):
        raise ValueError(f"Patch start line out of range: {start_line}")
    if end_line < 1 or end_line > len(line_offsets):
        raise ValueError(f"Patch end line out of range: {end_line}")
    start = line_offsets[start_line - 1] + patch.start["column"] - 1
    end = line_offsets[end_line - 1] + patch.end["column"]
    return start, end


def current_patch_text(text: str, patch: TextPatch) -> str:
    start, end = patch_offsets(text, patch)
    return text[start:end]


def validate_patch_text(text: str, patch: TextPatch) -> bool:
    return current_patch_text(text, patch) == patch.old_text


def apply_patch_to_text(text: str, patch: TextPatch) -> str:
    start, end = patch_offsets(text, patch)
    return text[:start] + patch.new_text + text[end:]


def replacement_text(issue_code: str, old_text: str, suggestions: list[str]) -> str:
    if not suggestions:
        return old_text
    if issue_code == "LANG_DEEP_ACRONYM_FIRST_USE":
        suggestion = suggestions[0]
        if old_text and old_text.lower() in suggestion.lower():
            return suggestion
        return f"{suggestion}（{old_text}）"
    return suggestions[0]


def build_patch_from_finding(
    project_root: str | Path, finding: dict[str, object]
) -> tuple[TextPatch | None, str | None]:
    file_name = finding.get("file")
    code = finding.get("code")
    line_no = finding.get("line")
    span = finding.get("span")
    suggestions = finding.get("suggestions", [])
    if not (
        isinstance(file_name, str)
        and file_name
        and isinstance(code, str)
        and isinstance(line_no, int)
        and isinstance(span, dict)
    ):
        return None, "unsupported_finding_shape"
    start_column = span.get("start")
    end_column = span.get("end")
    if not isinstance(start_column, int) or not isinstance(end_column, int):
        return None, "invalid_span"
    if start_column < 1 or end_column < start_column:
        return None, "invalid_span"
    if not isinstance(suggestions, list):
        suggestions = []
    path = Path(project_root) / file_name
    if not path.exists():
        return None, "missing_file"
    lines = path.read_text(encoding="utf-8").splitlines()
    if line_no < 1 or line_no > len(lines):
        return None, "invalid_line"
    line = lines[line_no - 1]
    if end_column > len(line):
        return None, "span_out_of_range"
    old_text = line[start_column - 1 : end_column]
    if not old_text:
        return None, "empty_patch_span"
    new_text = replacement_text(code, old_text, [str(item) for item in suggestions])
    if new_text == old_text:
        return None, "no_effect"
    confidence = finding.get("confidence", 0.0)
    try:
        confidence = float(confidence)
    except (TypeError, ValueError):
        confidence = 0.0
    patch = TextPatch(
        file=file_name,
        start={"line": line_no, "column": start_column},
        end={"line": line_no, "column": end_column},
        old_text=old_text,
        new_text=new_text,
        issue_code=code,
        confidence=confidence,
        review_required=bool(finding.get("review_required", True)),
        category=str(finding.get("category", "")),
    )
    return patch, None


def build_patch_from_review_item(
    project_root: str | Path, item: dict[str, object]
) -> tuple[TextPatch | None, str | None]:
    if bool(item.get("ambiguous", False)):
        return None, "ambiguous"
    if bool(item.get("review_required", False)):
        return None, "review_required"
    old_text = item.get("old_text")
    suggestions = item.get("suggestions")
    span = item.get("span")
    if not isinstance(old_text, str) or not old_text:
        return None, "missing_old_text"
    if not isinstance(suggestions, list) or not suggestions:
        return None, "missing_suggestions"
    if not isinstance(span, dict):
        return None, "missing_span"
    finding_like = {
        "code": item.get("code", "REVIEW_FEEDBACK"),
        "file": item.get("file", ""),
        "line": item.get("line", 0),
        "span": span,
        "suggestions": suggestions,
        "confidence": item.get("confidence", 0.0),
        "review_required": item.get("review_required", False),
        "category": item.get("category", ""),
    }
    patch, reason = build_patch_from_finding(project_root, finding_like)
    if patch is None:
        return None, reason
    if patch.old_text != old_text:
        return None, "old_text_mismatch"
    return patch, None


def detect_patch_conflicts(
    project_root: str | Path, patches: list[TextPatch]
) -> tuple[list[TextPatch], list[dict[str, object]]]:
    project_root = Path(project_root)
    accepted: list[TextPatch] = []
    conflicts: list[dict[str, object]] = []
    rejected_ids: set[int] = set()

    by_file: dict[str, list[tuple[int, TextPatch]]] = {}
    for index, patch in enumerate(patches):
        by_file.setdefault(patch.file, []).append((index, patch))

    for file_name, indexed_patches in by_file.items():
        text = (project_root / file_name).read_text(encoding="utf-8")
        ordered = sorted(indexed_patches, key=lambda item: patch_offsets(text, item[1])[0])
        previous: tuple[int, TextPatch] | None = None
        previous_range: tuple[int, int] | None = None
        for item in ordered:
            current_range = patch_offsets(text, item[1])
            if previous is not None and previous_range is not None:
                if current_range[0] < previous_range[1]:
                    rejected_ids.add(previous[0])
                    rejected_ids.add(item[0])
                    conflicts.append(
                        {
                            "file": file_name,
                            "reason": "overlap",
                            "patches": [previous[1].as_dict(), item[1].as_dict()],
                        }
                    )
            previous = item
            previous_range = current_range

    for index, patch in enumerate(patches):
        if index not in rejected_ids:
            accepted.append(patch)
    return accepted, conflicts
