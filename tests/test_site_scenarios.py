from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


class SiteScenarioPagesTest(unittest.TestCase):
    def _read(self, name: str) -> str:
        return (SITE / name).read_text(encoding="utf-8")

    def test_advisor_handoff_page_exists_with_required_sections(self) -> None:
        path = SITE / "advisor-handoff.html"
        self.assertTrue(path.exists(), "site/advisor-handoff.html should exist")

        text = path.read_text(encoding="utf-8")
        required_snippets = [
            'lang="zh-CN"',
            "如何把当前论文状态清楚交给导师/合作者继续看",
            "handoff packet",
            "当前论文目标",
            "已完成部分",
            "卡住的问题",
            "希望导师重点看的地方",
            "相关文件 / 版本说明",
            "下一步建议",
            "不要只发一份完整草稿而不给阅读说明",
            "一个好的交接说明长什么样",
            "submission-prep.html",
            "scenario-entry.html",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_submission_prep_page_exists_with_required_sections(self) -> None:
        path = SITE / "submission-prep.html"
        self.assertTrue(path.exists(), "site/submission-prep.html should exist")

        text = path.read_text(encoding="utf-8")
        required_snippets = [
            'lang="zh-CN"',
            "投稿/送审前如何系统检查论文材料是否齐备",
            "内容质量检查",
            "提交材料齐备检查",
            "格式 / 模板",
            "摘要、关键词、标题页",
            "图表、编号、引用",
            "附件、声明、补充材料",
            "文件命名与导出格式",
            "最后一轮风险检查",
            "final submission packet",
            "这不是投稿系统，也不是送审门户",
            "advisor-handoff.html",
            "scenario-entry.html",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_scenario_entry_links_to_both_dedicated_pages(self) -> None:
        text = self._read("scenario-entry.html")
        self.assertIn('href="advisor-handoff.html"', text)
        self.assertIn('href="submission-prep.html"', text)

    def test_artifact_gallery_has_before_after_examples_section(self) -> None:
        text = self._read("artifact-gallery.html")
        required_snippets = [
            'id="before-after"',
            "前后对比示例",
            "Before",
            "After",
            "原始论文材料通常是什么状态",
            "经过 thesis-skills 整理后会变成什么",
            "不是自动生成答辩成品",
        ]
        for snippet in required_snippets:
            self.assertIn(snippet, text)

    def test_index_or_docs_home_links_to_before_after_examples(self) -> None:
        index_text = self._read("index.html")
        docs_home_text = self._read("docs-home.html")
        self.assertTrue(
            'artifact-gallery.html#before-after' in index_text
            or 'artifact-gallery.html#before-after' in docs_home_text
        )


if __name__ == "__main__":
    unittest.main()
