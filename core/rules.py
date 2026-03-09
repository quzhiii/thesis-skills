from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.yamlish import load_yaml_file


@dataclass
class RulePack:
    root: Path
    pack: dict[str, object]
    rules: dict[str, object]
    mappings: dict[str, object]

    @property
    def ruleset(self) -> str:
        return str(self.pack["id"])


def load_rule_pack(path: str | Path) -> RulePack:
    root = Path(path)
    pack = load_yaml_file(root / "pack.yaml")
    rules = load_yaml_file(root / "rules.yaml")
    mappings = load_yaml_file(root / "mappings.yaml")
    return RulePack(root=root, pack=pack, rules=rules, mappings=mappings)


def find_rule_pack(repo_root: str | Path, ruleset: str) -> RulePack:
    return load_rule_pack(Path(repo_root) / "90-rules" / "packs" / ruleset)
