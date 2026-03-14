from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Location:
    paragraph_index: int | None = None
    bookmark: str | None = None
    table_index: int | None = None


@dataclass
class SuggestedAction:
    action_type: str
    params: dict[str, Any]


@dataclass
class Issue:
    issue_id: str
    type: str
    severity: str
    location: Location
    evidence: str
    suggested_action: SuggestedAction


@dataclass
class PlanAction:
    action_id: str
    action_type: str
    target: Location
    params: dict[str, Any]
    preconditions: list[str]
    rollback_hint: str
