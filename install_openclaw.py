from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_manifest(repo_root: Path) -> dict[str, object]:
    return json.loads((repo_root / "skills-manifest.json").read_text(encoding="utf-8"))


def _slug(module_id: str) -> str:
    return f"thesis-skills-{module_id}"


def _render_skill(module: dict[str, object], entry_text: str, repo_root: Path) -> str:
    module_id = str(module["id"])
    module_type = str(module.get("type", "workflow"))
    description = f"Thesis Skills module for {module_id} ({module_type})"
    return "\n".join(
        [
            "---",
            f"name: {_slug(module_id)}",
            f"description: {description}",
            "---",
            "",
            f"Repository root: `{repo_root.as_posix()}`",
            "",
            "This skill was installed from the `thesis-skills` repository for OpenClaw.",
            "When you run commands, prefer absolute paths pointing back to the repository root above, or run from that directory.",
            "",
            entry_text.strip(),
            "",
        ]
    )


def install_openclaw_skills(
    repo_root: str | Path, target_root: str | Path
) -> list[Path]:
    repo_root = Path(repo_root).resolve()
    target_root = Path(target_root).expanduser().resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest(repo_root)
    written: list[Path] = []
    for module in manifest.get("modules", []):
        if not isinstance(module, dict):
            continue
        entry = module.get("entry")
        module_id = module.get("id")
        if not isinstance(entry, str) or not isinstance(module_id, str):
            continue
        source = repo_root / entry
        if not source.exists():
            continue
        skill_dir = target_root / _slug(module_id)
        skill_dir.mkdir(parents=True, exist_ok=True)
        body = source.read_text(encoding="utf-8")
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(_render_skill(module, body, repo_root), encoding="utf-8")
        written.append(skill_file)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install thesis-skills modules into an OpenClaw skills directory"
    )
    parser.add_argument("--target", default=str(Path.home() / ".openclaw" / "skills"))
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parent
    written = install_openclaw_skills(repo_root, args.target)
    print(
        f"Installed {len(written)} OpenClaw skills into {Path(args.target).expanduser().resolve().as_posix()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
