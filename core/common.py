from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    file: str
    line: int = 0
    suggestion: str = ""
    span: dict[str, int] | None = None
    evidence: str = ""
    suggestions: list[str] | None = None
    confidence: float | None = None
    review_required: bool | None = None
    category: str = ""
    original_text: str = ""
    rationale: str = ""
    risk_level: str = ""

    def as_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "status": "FAIL",
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }
        if self.span is not None:
            payload["span"] = self.span
        if self.evidence:
            payload["evidence"] = self.evidence
        if self.suggestions:
            payload["suggestions"] = self.suggestions
        if self.confidence is not None:
            payload["confidence"] = self.confidence
        if self.review_required is not None:
            payload["review_required"] = self.review_required
        if self.category:
            payload["category"] = self.category
        if self.original_text:
            payload["original_text"] = self.original_text
        if self.rationale:
            payload["rationale"] = self.rationale
        if self.risk_level:
            payload["risk_level"] = self.risk_level
        return payload
