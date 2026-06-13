from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any


def export_pack(
    pack_dir: str | Path,
    output: str | Path,
    lint_report: str | Path | None = None,
) -> dict[str, Any]:
    pack_dir = Path(pack_dir)
    output = Path(output)

    if not pack_dir.is_dir():
        return {"success": False, "error": f"Pack directory not found: {pack_dir}"}

    pack_yaml = pack_dir / "pack.yaml"
    rules_yaml = pack_dir / "rules.yaml"
    mappings_yaml = pack_dir / "mappings.yaml"

    for required in (pack_yaml, rules_yaml, mappings_yaml):
        if not required.exists():
            return {"success": False, "error": f"Missing required file: {required.name}"}

    pack_id = pack_dir.name
    try:
        pack_content = pack_yaml.read_text(encoding="utf-8")
        for line in pack_content.splitlines():
            if line.startswith("id:"):
                pack_id = line.split(":", 1)[1].strip().strip("'\"")
                break
    except Exception:
        pass

    lint_status = "unknown"
    lint_data = None
    if lint_report is not None:
        lint_path = Path(lint_report)
        if lint_path.exists():
            try:
                lint_data = json.loads(lint_path.read_text(encoding="utf-8"))
                lint_status = lint_data.get("scorecard", {}).get("overall_status", "unknown")
            except Exception:
                pass

    manifest = {
        "pack_id": pack_id,
        "format_version": "1.0",
        "files": [],
        "lint_status": lint_status,
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in sorted(pack_dir.rglob("*")):
            if file_path.is_file():
                arcname = f"{pack_id}/{file_path.relative_to(pack_dir)}"
                zf.write(file_path, arcname)
                manifest["files"].append(arcname)

        if lint_data is not None:
            zf.writestr(f"{pack_id}/pack-lint-report.json", json.dumps(lint_data, ensure_ascii=False, indent=2))
            manifest["files"].append(f"{pack_id}/pack-lint-report.json")

        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))

    return {
        "success": True,
        "output": str(output),
        "pack_id": pack_id,
        "files_count": len(manifest["files"]),
        "lint_status": lint_status,
    }
