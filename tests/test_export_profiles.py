from __future__ import annotations

import unittest

from core.export_profiles import resolve_export_profile


class ExportProfilesTest(unittest.TestCase):
    def test_review_friendly_resolves_to_default_policy(self) -> None:
        profile = resolve_export_profile("review-friendly")
        self.assertEqual(profile["id"], "review-friendly")
        self.assertTrue(profile["allow_degraded"])
        self.assertFalse(profile["require_template_match"])
        self.assertEqual(profile["math_handling"], "convert")
        self.assertEqual(profile["figure_handling"], "inline")

    def test_submission_friendly_resolves_to_stricter_policy(self) -> None:
        profile = resolve_export_profile("submission-friendly")
        self.assertEqual(profile["id"], "submission-friendly")
        self.assertFalse(profile["allow_degraded"])
        self.assertTrue(profile["require_template_match"])
        self.assertEqual(profile["math_handling"], "strict")
        self.assertEqual(profile["figure_handling"], "preserve-float")

    def test_unknown_profile_fails_clearly(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            resolve_export_profile("nonexistent-profile")
        self.assertIn("nonexistent-profile", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
