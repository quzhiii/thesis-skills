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

    def as_dict(self) -> dict[str, object]:
        return {
            "status": "FAIL",
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "suggestion": self.suggestion,
        }
