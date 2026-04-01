from __future__ import annotations

import unittest

from core.consistency import analyze_terminology_group
from core.terminology import TextOccurrence, find_non_overlapping_literal_occurrences


class ConsistencyTest(unittest.TestCase):
    def test_analyze_terminology_group_returns_aggregate_result(self) -> None:
        occurrences = {
            "大型语言模型": [
                TextOccurrence(
                    file="chapters/01.tex",
                    text="大型语言模型",
                    line=1,
                    span={"start": 1, "end": 6},
                    sentence="大型语言模型在研究中具有重要作用。",
                )
            ],
            "大语言模型": [
                TextOccurrence(
                    file="chapters/02.tex",
                    text="大语言模型",
                    line=2,
                    span={"start": 4, "end": 8},
                    sentence="后文也称大语言模型。",
                )
            ],
        }
        result = analyze_terminology_group("大型语言模型", occurrences)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual(result.anchor_variant, "大语言模型")
        self.assertIn("大型语言模型 (1)", result.evidence)
        self.assertIn("大语言模型 (1)", result.evidence)

    def test_non_overlapping_literal_matching_prefers_longer_variant(self) -> None:
        matches = find_non_overlapping_literal_occurrences(
            "双重差分法用于估计处理效应。",
            ["双重差分", "双重差分法"],
        )
        self.assertEqual(len(matches["双重差分"]), 0)
        self.assertEqual(len(matches["双重差分法"]), 1)


if __name__ == "__main__":
    unittest.main()
