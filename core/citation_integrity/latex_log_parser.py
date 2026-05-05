from __future__ import annotations

from pathlib import Path

from core.compile_parser import parse_compile_log_file
from core.citation_integrity.models import CitationIntegrityIssue


def lint_latex_log_text(text: str, log_file: str, *, default_file: str) -> list[CitationIntegrityIssue]:
    temp_path = Path(log_file)
    if temp_path.exists():
        findings = parse_compile_log_file(temp_path, default_file=default_file)
    else:
        from tempfile import NamedTemporaryFile

        with NamedTemporaryFile("w", encoding="utf-8", suffix=".log", delete=False) as handle:
            handle.write(text)
            name = handle.name
        try:
            findings = parse_compile_log_file(Path(name), default_file=default_file)
        finally:
            Path(name).unlink(missing_ok=True)

    issues: list[CitationIntegrityIssue] = []
    for finding in findings:
        if finding.category == "missing_citation":
            issues.append(
                CitationIntegrityIssue(
                    code="CI-LOG-UNDEFINED-CITATION",
                    severity="BLOCK",
                    category="latex_log_warning",
                    message=finding.message,
                    file=finding.file,
                    line=finding.line,
                    evidence={"log_file": log_file, "compile_code": finding.code},
                    suggested_action="Fix the citation key or bibliography entry and rerun LaTeX/BibTeX.",
                )
            )
        elif finding.category == "bibliography_backend_issue":
            issues.append(
                CitationIntegrityIssue(
                    code="CI-LOG-BIBLIOGRAPHY-BACKEND",
                    severity="WARN",
                    category="latex_log_warning",
                    message=finding.message,
                    file=finding.file,
                    line=finding.line,
                    evidence={"log_file": log_file, "compile_code": finding.code},
                    suggested_action="Run the required bibliography backend and rebuild the document.",
                )
            )
    return issues
