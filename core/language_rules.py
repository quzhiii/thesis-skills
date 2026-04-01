from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LanguageRule:
    enabled: bool
    severity: str
    autofix_safe: bool
    patterns: tuple[str, ...]


def get_language_rule(
    config: dict[str, object],
    key: str,
    *,
    default_enabled: bool = False,
    default_severity: str = "warning",
    default_autofix_safe: bool = False,
) -> LanguageRule:
    node = config.get(key, {})
    if not isinstance(node, dict):
        return LanguageRule(
            enabled=default_enabled,
            severity=default_severity,
            autofix_safe=default_autofix_safe,
            patterns=(),
        )
    patterns = node.get("patterns", [])
    if not isinstance(patterns, list):
        patterns = []
    return LanguageRule(
        enabled=bool(node.get("enabled", default_enabled)),
        severity=str(node.get("severity", default_severity)),
        autofix_safe=bool(node.get("autofix_safe", default_autofix_safe)),
        patterns=tuple(str(item) for item in patterns),
    )


def get_rule_severity(
    config: dict[str, object], key: str, default: str = "warning"
) -> str:
    return get_language_rule(config, key, default_severity=default).severity
