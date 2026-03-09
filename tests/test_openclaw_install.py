from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from install_openclaw import install_openclaw_skills


ROOT = Path(__file__).resolve().parents[1]


class OpenClawInstallTest(unittest.TestCase):
    def test_install_openclaw_skills_creates_skill_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            written = install_openclaw_skills(ROOT, target)
            self.assertTrue(written)
            skill_file = target / "thesis-skills-11-check-language" / "SKILL.md"
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("name: thesis-skills-11-check-language", content)
            self.assertIn("Repository root:", content)
            self.assertIn("11-check-language/check_language.py", content)


if __name__ == "__main__":
    unittest.main()
