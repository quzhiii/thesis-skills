from __future__ import annotations

import json
import zipfile
from pathlib import Path

from core.pack_linter import build_pack_scorecard, lint_pack
from core.rules import load_rule_pack


REQUIRED_BUNDLE_FILES = ("pack.yaml", "rules.yaml", "mappings.yaml")


def export_rule_pack_bundle(pack_root: str | Path, output_path: str | Path) -> Path:
    pack_root = Path(pack_root)
    output_path = Path(output_path)
    findings = lint_pack(pack_root)
    if any(item.severity == "error" for item in findings):
        raise ValueError("rule pack must pass lint before export")
    pack = load_rule_pack(pack_root)
    scorecard = build_pack_scorecard(findings)
    manifest = {
        "bundle_version": 1,
        "pack_id": pack.ruleset,
        "pack_version": pack.pack["version"],
        "pack_kind": pack.pack["kind"],
        "display_name": pack.pack["display_name"],
        "scorecard_summary": {
            "overall_status": scorecard["overall_status"],
            "finding_counts": scorecard["finding_counts"],
        },
        "required_files": list(REQUIRED_BUNDLE_FILES),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for name in REQUIRED_BUNDLE_FILES:
            archive.write(pack_root / name, name)
    return output_path
