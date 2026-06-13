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

    def test_artifact_gallery_uses_existing_patch_preview_command(self) -> None:
        text = self._read("artifact-gallery.html")
        expected_command = (
            "python 24-fix-language-deep/fix_language_deep.py "
            "--project-root thesis "
            "--report reports/check_language_deep-report.json "
            "--apply false"
        )
        script_path = ROOT / "24-fix-language-deep" / "fix_language_deep.py"

        self.assertTrue(script_path.exists(), f"{script_path} should exist")
        self.assertIn(expected_command, text)
        self.assertNotIn("python 15-fix-preview/generate_fix_preview.py", text)

    def test_index_or_docs_home_links_to_before_after_examples(self) -> None:
        index_text = self._read("index.html")
        docs_home_text = self._read("docs-home.html")
        self.assertTrue(
            'artifact-gallery.html#before-after' in index_text
            or 'artifact-gallery.html#before-after' in docs_home_text
        )

    def test_index_rule_pack_entry_uses_existing_current_guidance(self) -> None:
        text = self._read("index.html")
        self.assertNotIn('href="rule-packs.html"', text)
        self.assertIn(
            'href="https://github.com/quzhiii/thesis-skills/blob/main/90-rules/THESIS_RULE_PACKS.md"',
            text,
        )
        self.assertIn("lint、schema、scorecard、导出交接包", text)

    def test_site_copy_surfaces_current_rule_pack_export_contract(self) -> None:
        text = (SITE / "copy-source.md").read_text(encoding="utf-8")
        for snippet in [
            "规则包 lint、schema consistency、scorecard 和最小导出交接包。",
            "rule-pack lint scorecard / export bundle",
            "导出包 `manifest.json` 记录规则包元数据和 lint scorecard 摘要。",
            "YAML 规则包创建、草稿脚手架、lint、schema consistency、scorecard 和最小导出交接包",
            "正式规则包 registry、发布系统或安装器",
        ]:
            self.assertIn(snippet, text)

    def test_site_copy_source_uses_current_version_framing(self) -> None:
        text = (SITE / "copy-source.md").read_text(encoding="utf-8")
        self.assertIn("### v3.5.0 已包含", text)
        self.assertIn("final reference set、外部验证、DOI / URL advisory 和 hallucination risk", text)
        self.assertIn("claim-citation support triage 和本地 HTML 报告界面", text)
        self.assertIn("final-audit JSON / HTML、reference audit ledger 和报告索引", text)
        self.assertIn("Thesis Skills v3.5.0 — MIT License — quzhiii/thesis-skills", text)
        self.assertNotIn("v1.2.0 已包含", text)
        self.assertNotIn("Thesis Skills v1.2.0", text)

    def test_current_site_pages_show_v341_not_stale_version_labels(self) -> None:
        expected_by_page = {
            "index.html": [
                "Thesis Skills v3.5.0",
                '<span class="issue-note">v3.5.0</span>',
                "Thesis Skills v3.5.0 · CLI-first · MIT · Python 3.10+",
                "Thesis Skills / v3.5.0",
            ],
            "quickstart.html": [
                '<span class="issue-note">v3.5.0</span>',
                "生成 v3.3 引用证据链",
                "Thesis Skills / v3.5.0",
            ],
            "scenario-entry.html": [
                '<span class="issue-note">v3.5.0</span>',
                "运行 v3.3 evidence pipeline",
            ],
            "artifact-gallery.html": [
                "输出样例 | Thesis Skills v3.5.0",
                '<span class="issue-note">v3.5.0 / 输出样例</span>',
                "Thesis Skills / v3.5.0 / output samples",
            ],
            "docs-home.html": [
                "当前 v3.5.0 的公开输出样例",
            ],
        }
        stale_snippets = [
            "v3.3.0",
            "v3.3 /",
            "v3.0.0",
        ]
        for page, expected_snippets in expected_by_page.items():
            text = self._read(page)
            with self.subTest(page=page):
                for snippet in expected_snippets:
                    self.assertIn(snippet, text)
                for stale in stale_snippets:
                    self.assertNotIn(stale, text)

    def test_historical_site_pages_use_archive_disclaimers_not_current_story_wording(self) -> None:
        redraft = self._read("index-product-redraft.html")
        self.assertIn("Historical draft page kept for internal reference.", redraft)
        self.assertIn("Use `site/index.html` for the current public story.", redraft)
        self.assertIn("当前公开入口请看正式首页", redraft)
        self.assertNotIn("current v3.3.0 public story", redraft)
        self.assertNotIn("当前 v3.3.0 公开入口请看正式首页", redraft)

        historical_gallery = self._read("v1.1-showcase/artifact-gallery.html")
        self.assertIn("python 15-fix-preview/generate_fix_preview.py --project-root thesis --mode dry-run", historical_gallery)
        self.assertIn("Do not treat the commands on this page as current supported entrypoints.", historical_gallery)

        historical_index = self._read("v1.1-showcase/index.html")
        self.assertNotIn('href="rule-packs.html"', historical_index)
        self.assertIn(
            'href="https://github.com/quzhiii/thesis-skills/blob/main/90-rules/THESIS_RULE_PACKS.md"',
            historical_index,
        )
        self.assertIn("lint、schema、scorecard、导出交接包", historical_index)

        optimization_plan = self._read("v1.1-showcase/OPTIMIZATION-PLAN.md")
        self.assertIn("Historical optimization plan kept for reference; proposed pages are not current site requirements.", optimization_plan)
        self.assertIn("proposed rule-pack page", optimization_plan)
        self.assertNotIn("rule-packs.html", optimization_plan)


if __name__ == "__main__":
    unittest.main()
