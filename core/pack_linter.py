from __future__ import annotations

from pathlib import Path

from core.common import Finding
from core.rules import load_rule_pack
from core.yamlish import load_yaml_file


REQUIRED_PACK_FILES = ("pack.yaml", "rules.yaml", "mappings.yaml")
REQUIRED_PACK_FIELDS = (
    "id",
    "kind",
    "display_name",
    "version",
    "precedence",
    "starter",
)
ALLOWED_KINDS = {"university-thesis", "journal"}
REQUIRED_RULES_TOP_LEVEL = ("project", "reference", "language")
STARTER_MAPPINGS_TOP_LEVEL = ("mappings",)
DRAFT_MAPPINGS_TOP_LEVEL = ("source_template_mappings", "chapter_role_mappings")

REQUIRED_FILE_CODES = {"missing_required_file", "pack_parse_error"}
METADATA_CODES = {
    "missing_pack_field",
    "invalid_pack_field",
    "pack_id_directory_mismatch",
}
COMPLETENESS_CODES = {"missing_rules_section"}
SCHEMA_CODES = {
    "unknown_mappings_schema",
    "invalid_rules_section_type",
    "invalid_mappings_section_type",
}


def lint_pack(path: str | Path) -> list[Finding]:
    root = Path(path)
    findings: list[Finding] = []

    missing_files = [name for name in REQUIRED_PACK_FILES if not (root / name).exists()]
    for name in missing_files:
        findings.append(
            Finding(
                severity="error",
                code="missing_required_file",
                message=f"Required pack file is missing: {name}",
                file=name,
            )
        )

    if missing_files:
        pack_path = root / "pack.yaml"
        if pack_path.exists():
            findings.extend(_lint_pack_metadata(pack_path, root.name))
        return findings

    try:
        pack = load_rule_pack(root)
    except Exception as exc:  # pragma: no cover - exercised by CLI/report path if needed later
        findings.append(
            Finding(
                severity="error",
                code="pack_parse_error",
                message=f"Pack files could not be parsed: {exc}",
                file=str(root),
            )
        )
        return findings

    findings.extend(_lint_pack_metadata(root / "pack.yaml", root.name))
    findings.extend(_lint_rules_completeness(pack.rules))
    findings.extend(_lint_mappings_completeness(pack.mappings))
    return findings


def build_pack_scorecard(findings: list[Finding]) -> dict[str, object]:
    errors = sum(1 for item in findings if item.severity == "error")
    warnings = sum(1 for item in findings if item.severity == "warning")
    infos = sum(1 for item in findings if item.severity == "info")

    def status_for(codes: set[str]) -> str:
        return "FAIL" if any(item.code in codes for item in findings) else "PASS"

    return {
        "required_files": {"status": status_for(REQUIRED_FILE_CODES)},
        "metadata_completeness": {"status": status_for(METADATA_CODES)},
        "baseline_completeness": {"status": status_for(COMPLETENESS_CODES)},
        "schema_consistency": {"status": status_for(SCHEMA_CODES)},
        "overall_status": "FAIL" if errors else "PASS",
        "finding_counts": {
            "errors": errors,
            "warnings": warnings,
            "infos": infos,
        },
    }


def _lint_pack_metadata(pack_path: Path, directory_name: str) -> list[Finding]:
    findings: list[Finding] = []
    pack_data = load_yaml_file(pack_path)

    for field in REQUIRED_PACK_FIELDS:
        if field not in pack_data:
            findings.append(
                Finding(
                    severity="error",
                    code="missing_pack_field",
                    message=f"Required pack.yaml field is missing: {field}",
                    file="pack.yaml",
                )
            )

    pack_id = pack_data.get("id")
    if isinstance(pack_id, str):
        if not pack_id.strip():
            findings.append(
                Finding(
                    severity="error",
                    code="invalid_pack_field",
                    message="pack.yaml field 'id' must be a non-empty string",
                    file="pack.yaml",
                )
            )
        elif pack_id != directory_name:
            findings.append(
                Finding(
                    severity="error",
                    code="pack_id_directory_mismatch",
                    message=f"pack.yaml id '{pack_id}' does not match directory name '{directory_name}'",
                    file="pack.yaml",
                )
            )

    display_name = pack_data.get("display_name")
    if display_name is not None and (not isinstance(display_name, str) or not display_name.strip()):
        findings.append(
            Finding(
                severity="error",
                code="invalid_pack_field",
                message="pack.yaml field 'display_name' must be a non-empty string",
                file="pack.yaml",
            )
        )

    precedence = pack_data.get("precedence")
    if precedence is not None and (not isinstance(precedence, str) or not precedence.strip()):
        findings.append(
            Finding(
                severity="error",
                code="invalid_pack_field",
                message="pack.yaml field 'precedence' must be a non-empty string",
                file="pack.yaml",
            )
        )

    kind = pack_data.get("kind")
    if kind is not None:
        if not isinstance(kind, str) or kind not in ALLOWED_KINDS:
            findings.append(
                Finding(
                    severity="error",
                    code="invalid_pack_field",
                    message="pack.yaml field 'kind' must be one of: university-thesis, journal",
                    file="pack.yaml",
                )
            )

    starter = pack_data.get("starter")
    if starter is not None and not isinstance(starter, bool):
        findings.append(
            Finding(
                severity="error",
                code="invalid_pack_field",
                message="pack.yaml field 'starter' must be a boolean",
                file="pack.yaml",
            )
        )

    return findings


def _lint_rules_completeness(rules_data: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []
    for section in REQUIRED_RULES_TOP_LEVEL:
        if section not in rules_data:
            findings.append(
                Finding(
                    severity="error",
                    code="missing_rules_section",
                    message=f"rules.yaml is missing required top-level section: {section}",
                    file="rules.yaml",
                )
            )
        elif not isinstance(rules_data[section], dict):
            findings.append(
                Finding(
                    severity="error",
                    code="invalid_rules_section_type",
                    message=f"rules.yaml top-level section '{section}' must be a mapping",
                    file="rules.yaml",
                )
            )
    return findings


def _lint_mappings_completeness(mappings_data: dict[str, object]) -> list[Finding]:
    findings: list[Finding] = []

    has_starter_shape = all(section in mappings_data for section in STARTER_MAPPINGS_TOP_LEVEL)
    has_draft_shape = all(section in mappings_data for section in DRAFT_MAPPINGS_TOP_LEVEL)

    if not has_starter_shape and not has_draft_shape:
        findings.append(
            Finding(
                severity="error",
                code="unknown_mappings_schema",
                message=(
                    "mappings.yaml must match either the starter-pack shape "
                    "(`mappings`) or the draft-pack shape "
                    "(`source_template_mappings` + `chapter_role_mappings`)"
                ),
                file="mappings.yaml",
            )
        )
        return findings

    if has_starter_shape and not isinstance(mappings_data["mappings"], dict):
        findings.append(
            Finding(
                severity="error",
                code="invalid_mappings_section_type",
                message="mappings.yaml top-level section 'mappings' must be a mapping",
                file="mappings.yaml",
            )
        )

    if has_draft_shape:
        for section in DRAFT_MAPPINGS_TOP_LEVEL:
            if not isinstance(mappings_data[section], dict):
                findings.append(
                    Finding(
                        severity="error",
                        code="invalid_mappings_section_type",
                        message=f"mappings.yaml top-level section '{section}' must be a mapping",
                        file="mappings.yaml",
                    )
                )

    return findings
