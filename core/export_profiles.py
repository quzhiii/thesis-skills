from __future__ import annotations


_PROFILES: dict[str, dict[str, object]] = {
    "review-friendly": {
        "id": "review-friendly",
        "display_name": "Review-Friendly Export",
        "description": "Prioritizes structural readability over visual perfection. Allows degraded constructs.",
        "allow_degraded": True,
        "require_template_match": False,
        "math_handling": "convert",
        "figure_handling": "inline",
        "citation_handling": "basic",
        "supported": True,
    },
    "submission-friendly": {
        "id": "submission-friendly",
        "display_name": "Submission-Friendly Export",
        "description": "Stricter export targeting university submission requirements. Not yet fully implemented.",
        "allow_degraded": False,
        "require_template_match": True,
        "math_handling": "strict",
        "figure_handling": "preserve-float",
        "citation_handling": "csl-exact",
        "supported": False,
    },
}


def resolve_export_profile(profile_id: str) -> dict[str, object]:
    if profile_id not in _PROFILES:
        raise ValueError(f"unknown export profile: {profile_id!r}")
    return dict(_PROFILES[profile_id])
