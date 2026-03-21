from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class LayoutTest(unittest.TestCase):
    def test_required_paths_exist(self) -> None:
        required = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "skills-manifest.json",
            ROOT / "core",
            ROOT / "00-bib-zotero",
            ROOT / "00-bib-endnote",
            ROOT / "01-word-to-latex",
            ROOT / "10-check-references",
            ROOT / "11-check-language",
            ROOT / "12-check-format",
            ROOT / "13-check-content",
            ROOT / "20-fix-references",
            ROOT / "21-fix-language-style",
            ROOT / "22-fix-format-structure",
            ROOT / "90-rules",
            ROOT / "99-runner",
            ROOT / "adapters",
            ROOT / "examples",
        ]
        missing = [
            str(path.relative_to(ROOT)) for path in required if not path.exists()
        ]
        self.assertFalse(missing, f"Missing required paths: {missing}")


if __name__ == "__main__":
    unittest.main()
