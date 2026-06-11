from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from core.claim_citation_html import render_claim_citation_html, write_claim_citation_html
from tests.helpers import materialize_project, workspace_tempdir


ROOT = Path(__file__).resolve().parents[1]
CLI_SCRIPT = ROOT / "32-claim-citation-html" / "build_claim_citation_html.py"


class ClaimCitationHtmlTest(unittest.TestCase):
    def test_render_outputs_bilingual_sections(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 1,
                    "weak_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 1,
                },
                "entries": [
                    {
                        "citation_key": "ref1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Conservative support-risk heuristic flagged this claim-citation pair for manual review.",
                        "claim_type": "empirical_result",
                        "file": "chapters/01-introduction.tex",
                        "line": 7,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref1", "ref2"],
                        "cluster_review_reason": "Review the grouped citations together.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Verify whether the cited source supports the strength of the claim before final submission."],
                        "claim_context": "The method significantly improves accuracy.",
                    }
                ],
                "citation_needed_candidates": [
                    {
                        "file": "main.tex",
                        "line": 3,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The method significantly improves accuracy.",
                    }
                ],
                "uncited_references": [
                    {
                        "citation_key": "unused2024",
                        "title": "Unused Reference",
                        "hallucination_risk_label": "HIGH_RISK",
                    }
                ],
            }
        )

        self.assertIn("声明-引用<br>支撑分级", html)
        self.assertIn("Claim-Citation<br>Triage", html)
        self.assertIn("Citation-Needed Candidates", html)
        self.assertIn("待补引用候选句", html)
        self.assertIn("Browse by triage label", html)
        self.assertIn("按分级标签查看", html)
        self.assertIn("Related Reports", html)
        self.assertIn("相关报告", html)
        self.assertIn("readiness-report.json", html)
        self.assertIn("claim-citation-triage-report.json", html)
        self.assertIn("final-audit-report.html", html)
        self.assertIn("reference-audit-ledger.html", html)
        self.assertIn("final-audit-report.html#warning-issues-zh", html)
        self.assertIn("final-audit-report.html#warning-issues-en", html)
        self.assertIn("reference-audit-ledger.html#evidence-rows-en", html)
        self.assertIn("reference-audit-ledger.html#evidence-rows-zh", html)
        self.assertIn("possible_overclaim", html)
        self.assertIn("NEEDS_MANUAL_REVIEW", html)
        self.assertIn("possible_overclaim", html)
        self.assertIn("ref1, ref2", html)
        self.assertIn("Review the grouped citations together.", html)
        self.assertIn("uncited_empirical_result", html)

    def test_render_surfaces_review_aggregates_before_entry_cards(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 2,
                    "weak_pairs": 1,
                    "supported_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Manual review needed.",
                        "claim_type": "empirical_result",
                        "file": "main.tex",
                        "line": 10,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref1", "ref2"],
                        "cluster_review_reason": "Review the grouped citations together.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review grouped support."],
                        "claim_context": "Claim one.",
                    },
                    {
                        "citation_key": "ref3",
                        "triage_label": "SUPPORTED",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Second manual review.",
                        "claim_type": "background_fact",
                        "file": "main.tex",
                        "line": 18,
                        "hallucination_risk_label": "PASS",
                        "cluster_keys": ["ref1", "ref2"],
                        "cluster_review_reason": "Repeated cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["Review again."],
                        "claim_context": "Claim two.",
                    },
                    {
                        "citation_key": "ref4",
                        "triage_label": "SUPPORTED",
                        "support_review_label": "SUPPORTED_DIRECTLY",
                        "support_review_reason": "Direct support found.",
                        "claim_type": "background_fact",
                        "file": "main.tex",
                        "line": 30,
                        "hallucination_risk_label": "PASS",
                        "cluster_keys": ["ref4"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": [],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["No action needed."],
                        "claim_context": "Claim three.",
                    },
                ],
                "citation_needed_candidates": [
                    {
                        "file": "main.tex",
                        "line": 22,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "Needs citation.",
                    }
                ],
                "uncited_references": [],
            }
        )

        self.assertIn("Review Aggregates", html)
        self.assertIn("复核聚合", html)
        self.assertIn("Top review focus", html)
        self.assertIn("优先复核焦点", html)
        self.assertIn("Start with the top triage group, then review citation-needed candidates, then confirm uncited references.", html)
        self.assertIn("先看最高优先分级分组，再看待补引用候选句，最后确认未被引用参考文献。", html)
        self.assertIn('href="#zh-triage-weak"', html)
        self.assertIn('href="#zh-citation-needed"', html)
        self.assertIn('href="#zh-uncited-references"', html)
        self.assertIn('href="#zh-triage-groups"', html)
        self.assertIn('href="#en-triage-weak"', html)
        self.assertIn('href="#en-citation-needed"', html)
        self.assertIn('href="#en-uncited-references"', html)
        self.assertIn('href="#en-triage-groups"', html)
        self.assertIn("support_review_label", html)
        self.assertIn("risk_signal", html)
        self.assertIn("cluster", html)
        self.assertIn("NEEDS_MANUAL_REVIEW (2)", html)
        self.assertIn("SUPPORTED_DIRECTLY", html)
        self.assertIn("possible_overclaim (2)", html)
        self.assertIn("uncited_empirical_result (1)", html)
        self.assertIn("ref1, ref2 (2)", html)
        self.assertIn("Single-citation cluster.", html)
        self.assertLess(html.index("NEEDS_MANUAL_REVIEW (2)"), html.index("SUPPORTED_DIRECTLY (1)"))
        self.assertLess(html.index("possible_overclaim (2)"), html.index("uncited_empirical_result (1)"))

    def test_render_adds_review_queue_with_entry_jump_links(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 3,
                    "weak_pairs": 1,
                    "unverifiable_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref-orphaned",
                        "triage_label": "UNVERIFIABLE",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Missing support details.",
                        "claim_type": "empirical_result",
                        "file": "chapters/results.tex",
                        "line": 8,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref-orphaned", "ref-other"],
                        "cluster_review_reason": "Review cluster together.",
                        "risk_signals": ["possible_topic_mismatch"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Open cited source and compare claim scope."],
                        "claim_context": "The intervention outperforms all baselines.",
                    },
                    {
                        "citation_key": "ref-weak",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Weak support pattern.",
                        "claim_type": "background_fact",
                        "file": "chapters/discussion.tex",
                        "line": 14,
                        "hallucination_risk_label": "WARN",
                        "cluster_keys": ["ref-weak"],
                        "cluster_review_reason": "Single review.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["Confirm whether the citation supports the stronger wording."],
                        "claim_context": "This result establishes a universal mechanism.",
                    },
                    {
                        "citation_key": "ref-supported",
                        "triage_label": "SUPPORTED",
                        "support_review_label": "SUPPORTED_DIRECTLY",
                        "support_review_reason": "Direct support found.",
                        "claim_type": "background_fact",
                        "file": "chapters/intro.tex",
                        "line": 3,
                        "hallucination_risk_label": "PASS",
                        "cluster_keys": ["ref-supported"],
                        "cluster_review_reason": "Single support.",
                        "risk_signals": [],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["No action needed."],
                        "claim_context": "A supported background statement.",
                    },
                ],
                "citation_needed_candidates": [
                    {
                        "file": "chapters/results.tex",
                        "line": 16,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The intervention reduces variance by 50%.",
                    }
                ],
                "uncited_references": [],
            }
        )

        self.assertIn("Review queue", html)
        self.assertIn("复核队列", html)
        self.assertIn("Open the highest-priority triage entries first, then review citation-needed candidates in source order.", html)
        self.assertIn("先打开最高优先分级条目，再按源码顺序检查待补引用候选句。", html)
        self.assertIn('href="#zh-entry-unverifiable-chapters-results-tex-ref-orphaned-8"', html)
        self.assertIn('href="#zh-entry-weak-chapters-discussion-tex-ref-weak-14"', html)
        self.assertIn('id="zh-entry-unverifiable-chapters-results-tex-ref-orphaned-8"', html)
        self.assertIn('id="zh-entry-weak-chapters-discussion-tex-ref-weak-14"', html)
        self.assertIn('href="#en-entry-unverifiable-chapters-results-tex-ref-orphaned-8"', html)
        self.assertIn('href="#en-entry-weak-chapters-discussion-tex-ref-weak-14"', html)
        self.assertIn('id="en-entry-unverifiable-chapters-results-tex-ref-orphaned-8"', html)
        self.assertIn('id="en-entry-weak-chapters-discussion-tex-ref-weak-14"', html)
        self.assertLess(html.index('href="#zh-entry-unverifiable-chapters-results-tex-ref-orphaned-8"'), html.index('href="#zh-entry-weak-chapters-discussion-tex-ref-weak-14"'))

    def test_render_adds_conservative_review_groups_with_entry_links(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 4,
                    "weak_pairs": 1,
                    "supported_pairs": 2,
                    "well_supported_pairs": 1,
                    "citation_needed_candidates": 0,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref-high",
                        "triage_label": "SUPPORTED",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Cited reference carries HIGH_RISK hallucination evidence.",
                        "claim_type": "background_fact",
                        "file": "chapters/risk.tex",
                        "line": 3,
                        "hallucination_risk_label": "HIGH_RISK",
                        "cluster_keys": ["ref-high"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["high_risk_reference"],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["Verify the cited source against DOI, publisher, database, or original document evidence."],
                        "claim_context": "High-risk source supports this claim.",
                    },
                    {
                        "citation_key": "ref-weak",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Weak support pattern.",
                        "claim_type": "empirical_result",
                        "file": "chapters/results.tex",
                        "line": 12,
                        "hallucination_risk_label": "WARN",
                        "cluster_keys": ["ref-weak"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Confirm whether the citation supports the stronger wording."],
                        "claim_context": "The result establishes a universal mechanism.",
                    },
                    {
                        "citation_key": "ref-adequate",
                        "triage_label": "SUPPORTED",
                        "support_review_label": "ADEQUATE_REVIEW",
                        "support_review_reason": "Evidence appears adequate with minor caveats.",
                        "claim_type": "background_fact",
                        "file": "chapters/intro.tex",
                        "line": 8,
                        "hallucination_risk_label": "PASS",
                        "cluster_keys": ["ref-adequate"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": [],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["No immediate action; keep available for final human review."],
                        "claim_context": "Prior work explored similar architectures.",
                    },
                    {
                        "citation_key": "ref-direct",
                        "triage_label": "WELL_SUPPORTED",
                        "support_review_label": "STRONG_REVIEW",
                        "support_review_reason": "Evidence is structurally strong and low-risk.",
                        "claim_type": "background_fact",
                        "file": "chapters/intro.tex",
                        "line": 20,
                        "hallucination_risk_label": "PASS",
                        "cluster_keys": ["ref-direct"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": [],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["No action needed."],
                        "claim_context": "A directly supported background statement.",
                    },
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        self.assertIn("Review Groups", html)
        self.assertIn("复核分组", html)
        self.assertIn("P0 · Must review first", html)
        self.assertIn("P0 · 必须先处理", html)
        self.assertIn("P1 · High-priority review", html)
        self.assertIn("P1 · 高优先复核", html)
        self.assertIn("P2 · Regular review", html)
        self.assertIn("P2 · 常规复核", html)
        self.assertIn("P3 · Archive-only view", html)
        self.assertIn("P3 · 仅留档查看", html)
        self.assertIn('href="#zh-review-groups"', html)
        self.assertIn('href="#zh-review-group-p0"', html)
        self.assertIn("P0 · Must review first (1)", html)
        self.assertIn("P1 · High-priority review (1)", html)
        self.assertIn("P2 · Regular review (1)", html)
        self.assertIn("P3 · Archive-only view (1)", html)
        self.assertIn('href="#en-review-group-p0"', html)
        self.assertIn('href="#en-review-groups"', html)
        zh_p0 = html.split('id="zh-review-group-p0"', 1)[1].split("</article>", 1)[0]
        zh_p1 = html.split('id="zh-review-group-p1"', 1)[1].split("</article>", 1)[0]
        zh_p2 = html.split('id="zh-review-group-p2"', 1)[1].split("</article>", 1)[0]
        zh_p3 = html.split('id="zh-review-group-p3"', 1)[1].split("</article>", 1)[0]
        en_p0 = html.split('id="en-review-group-p0"', 1)[1].split("</article>", 1)[0]
        self.assertIn('href="#zh-entry-supported-chapters-risk-tex-ref-high-3"', zh_p0)
        self.assertIn('href="#zh-entry-weak-chapters-results-tex-ref-weak-12"', zh_p1)
        self.assertIn('href="#zh-entry-supported-chapters-intro-tex-ref-adequate-8"', zh_p2)
        self.assertIn('href="#zh-entry-well-supported-chapters-intro-tex-ref-direct-20"', zh_p3)
        self.assertIn("证据摘要", zh_p0)
        self.assertIn("判断依据", zh_p0)
        self.assertIn("建议动作", zh_p0)
        self.assertIn("高风险（HIGH_RISK）", zh_p0)
        self.assertIn("高风险参考文献（high_risk_reference）", zh_p0)
        self.assertIn("该引用携带 HIGH_RISK 幻觉风险证据，需要人工复核。", zh_p0)
        self.assertIn("请结合 DOI、出版方、数据库或原始文档证据核对该引用来源。", zh_p0)
        self.assertIn("Evidence", en_p0)
        self.assertIn("Rationale", en_p0)
        self.assertIn("Suggested action", en_p0)
        self.assertIn("HIGH_RISK", en_p0)
        self.assertIn("high_risk_reference", en_p0)
        self.assertIn("Cited reference carries HIGH_RISK hallucination evidence.", en_p0)
        self.assertIn("Verify the cited source against DOI, publisher, database, or original document evidence.", en_p0)
        self.assertLess(html.index("P0 · Must review first"), html.index("P1 · High-priority review"))
        self.assertLess(html.index("P1 · High-priority review"), html.index("P2 · Regular review"))
        self.assertLess(html.index("P2 · Regular review"), html.index("P3 · Archive-only view"))
        self.assertLess(html.index("Review Groups"), html.index("Review queue"))

    def test_render_adds_triage_group_jump_pills_for_non_empty_groups(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 2,
                    "weak_pairs": 1,
                    "unverifiable_pairs": 1,
                    "citation_needed_candidates": 0,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref-unverifiable",
                        "triage_label": "UNVERIFIABLE",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Missing support details.",
                        "claim_type": "empirical_result",
                        "file": "chapters/results.tex",
                        "line": 8,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref-unverifiable"],
                        "cluster_review_reason": "Review support.",
                        "risk_signals": ["possible_topic_mismatch"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Open cited source and compare claim scope."],
                        "claim_context": "The intervention outperforms all baselines.",
                    },
                    {
                        "citation_key": "ref-weak",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Weak support pattern.",
                        "claim_type": "background_fact",
                        "file": "chapters/discussion.tex",
                        "line": 14,
                        "hallucination_risk_label": "WARN",
                        "cluster_keys": ["ref-weak"],
                        "cluster_review_reason": "Single review.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["title_overlap"],
                        "next_actions": ["Confirm whether the citation supports the stronger wording."],
                        "claim_context": "This result establishes a universal mechanism.",
                    },
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        self.assertIn('class="nav-pill" href="#zh-triage-unverifiable">不可核验（UNVERIFIABLE） (1)</a>', html)
        self.assertIn('class="nav-pill" href="#zh-triage-weak">支撑偏弱（WEAK） (1)</a>', html)
        self.assertIn('class="nav-pill" href="#en-triage-unverifiable">UNVERIFIABLE (1)</a>', html)
        self.assertIn('class="nav-pill" href="#en-triage-weak">WEAK (1)</a>', html)
        self.assertNotIn('class="nav-pill" href="#zh-triage-orphaned">', html)
        self.assertNotIn('class="nav-pill" href="#zh-triage-supported">', html)
        self.assertNotIn('class="nav-pill" href="#en-triage-orphaned">', html)
        self.assertNotIn('class="nav-pill" href="#en-triage-supported">', html)

    def test_render_adds_citation_needed_row_anchors_and_source_order_jump_links(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 0,
                    "weak_pairs": 0,
                    "citation_needed_candidates": 2,
                    "unique_references_never_cited": 0,
                },
                "entries": [],
                "citation_needed_candidates": [
                    {
                        "file": "chapters/discussion.tex",
                        "line": 22,
                        "claim_type": "background_fact",
                        "risk_signal": "uncited_background_fact",
                        "sentence": "This observation remains understudied.",
                    },
                    {
                        "file": "chapters/results.tex",
                        "line": 16,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The intervention reduces variance by 50%.",
                    },
                ],
                "uncited_references": [],
            }
        )

        self.assertIn('id="zh-citation-needed-chapters-discussion-tex-22"', html)
        self.assertIn('id="zh-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('id="en-citation-needed-chapters-discussion-tex-22"', html)
        self.assertIn('id="en-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('class="nav-pill" href="#zh-citation-needed-chapters-discussion-tex-22"', html)
        self.assertIn('class="nav-pill" href="#zh-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('class="nav-pill" href="#en-citation-needed-chapters-discussion-tex-22"', html)
        self.assertIn('class="nav-pill" href="#en-citation-needed-chapters-results-tex-16"', html)
        citation_needed_section = html.split('<section class="section" id="zh-citation-needed">', 1)[1].split('</section>', 1)[0]
        self.assertLess(
            citation_needed_section.index('href="#zh-citation-needed-chapters-discussion-tex-22"'),
            citation_needed_section.index('<table>'),
        )
        self.assertLess(
            html.index('href="#zh-citation-needed-chapters-discussion-tex-22"'),
            html.index('href="#zh-citation-needed-chapters-results-tex-16"'),
        )

    def test_render_disambiguates_citation_needed_row_anchors_for_same_file_and_line(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 0,
                    "weak_pairs": 0,
                    "citation_needed_candidates": 2,
                    "unique_references_never_cited": 0,
                },
                "entries": [],
                "citation_needed_candidates": [
                    {
                        "file": "chapters/results.tex",
                        "line": 16,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The intervention reduces variance by 50%.",
                    },
                    {
                        "file": "chapters/results.tex",
                        "line": 16,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The ablation improves calibration by 12%.",
                    },
                ],
                "uncited_references": [],
            }
        )

        self.assertIn('id="zh-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('id="zh-citation-needed-chapters-results-tex-16-2"', html)
        self.assertIn('id="en-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('id="en-citation-needed-chapters-results-tex-16-2"', html)
        self.assertIn('class="nav-pill" href="#zh-citation-needed-chapters-results-tex-16"', html)
        self.assertIn('class="nav-pill" href="#zh-citation-needed-chapters-results-tex-16-2"', html)
        self.assertLess(
            html.index('href="#zh-citation-needed-chapters-results-tex-16"'),
            html.index('href="#zh-citation-needed-chapters-results-tex-16-2"'),
        )
        self.assertLess(
            html.index("The intervention reduces variance by 50%."),
            html.index("The ablation improves calibration by 12%."),
        )

    def test_render_localizes_zh_labels_with_english_in_parentheses(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "UNVERIFIABLE",
                "summary": {
                    "claim_citation_pairs": 1,
                    "unverifiable_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 1,
                },
                "entries": [
                    {
                        "citation_key": "ref-unverifiable",
                        "triage_label": "UNVERIFIABLE",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Missing support details.",
                        "claim_type": "empirical_result",
                        "file": "chapters/results.tex",
                        "line": 8,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref-unverifiable"],
                        "cluster_review_reason": "Review support.",
                        "risk_signals": ["possible_topic_mismatch"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Open cited source and compare claim scope."],
                        "claim_context": "The intervention outperforms all baselines.",
                    }
                ],
                "citation_needed_candidates": [
                    {
                        "file": "chapters/results.tex",
                        "line": 16,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "The intervention reduces variance by 50%.",
                    }
                ],
                "uncited_references": [
                    {
                        "citation_key": "unused2024",
                        "title": "Unused Reference",
                        "hallucination_risk_label": "HIGH_RISK",
                    }
                ],
            }
        )

        zh_section = html.split('<section class="lang-panel" data-lang-panel="zh">', 1)[1].split('<section class="lang-panel" data-lang-panel="en">', 1)[0]

        self.assertIn("不可核验（UNVERIFIABLE）", zh_section)
        self.assertIn("需要人工复核（NEEDS_MANUAL_REVIEW）", zh_section)
        self.assertIn("实证结果（empirical_result）", zh_section)
        self.assertIn("需复核（REVIEW）", zh_section)
        self.assertIn("可能存在主题错配（possible_topic_mismatch）", zh_section)
        self.assertIn("实证结果缺少引用（uncited_empirical_result）", zh_section)
        self.assertIn("高风险（HIGH_RISK）", zh_section)
        self.assertIn("相关报告", zh_section)
        self.assertIn("终稿审计页面", zh_section)
        self.assertIn("引用审计台账页面", zh_section)
        self.assertIn("当前缺少足够的支撑细节。", zh_section)
        self.assertIn("成组引用说明需复核。", zh_section)
        self.assertIn("请打开引用来源，并核对其支撑范围是否覆盖当前声明。", zh_section)
        self.assertIn("元数据完整", zh_section)
        self.assertNotIn("Citation-needed 候选句", zh_section)
        self.assertNotIn("claim 类型", zh_section)
        self.assertNotIn("authoritative source", zh_section)

    def test_render_localizes_zh_grouped_entry_heading_reason_and_context(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 2,
                    "weak_pairs": 2,
                    "citation_needed_candidates": 0,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "supported1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Cited reference carries HIGH_RISK hallucination evidence.",
                        "claim_type": "background",
                        "file": "main.tex",
                        "line": 12,
                        "hallucination_risk_label": "HIGH_RISK",
                        "cluster_keys": ["supported1", "weak1"],
                        "cluster_review_reason": "This citation appears in a grouped cluster with risk signals; review the grouped citations together.",
                        "risk_signals": ["high_risk_reference", "mixed_cluster_risk", "cluster_high_risk_reference", "cluster_weak_reference"],
                        "support_signals": ["has_claim_context", "grouped_citation_cluster"],
                        "next_actions": [
                            "Verify the cited source against DOI, publisher, database, or original document evidence.",
                            "Review this citation cluster as a group because at least one grouped citation has risk signals.",
                        ],
                        "claim_context": "Multiple studies provide evidence for this hypothesis.",
                    }
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        zh_section = html.split('<section class="lang-panel" data-lang-panel="zh">', 1)[1].split('<section class="lang-panel" data-lang-panel="en">', 1)[0]

        self.assertIn("引用键：supported1", zh_section)
        self.assertIn("该引用出现在带有风险信号的成组引用簇中，建议将成组引用一起复核。", zh_section)
        self.assertIn("多项研究为这一假设提供了证据。", zh_section)

    def test_render_adds_entry_review_summary_before_detail_blocks(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 1,
                    "weak_pairs": 1,
                    "citation_needed_candidates": 0,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref-summary",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Weak support pattern.",
                        "claim_type": "empirical_result",
                        "file": "chapters/results.tex",
                        "line": 12,
                        "hallucination_risk_label": "WARN",
                        "cluster_keys": ["ref-summary"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Confirm whether the citation supports the stronger wording."],
                        "claim_context": "The result establishes a universal mechanism.",
                    }
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        zh_entry = html.split('id="zh-entry-weak-chapters-results-tex-ref-summary-12"', 1)[1].split("</article>", 1)[0]
        en_entry = html.split('id="en-entry-weak-chapters-results-tex-ref-summary-12"', 1)[1].split("</article>", 1)[0]
        self.assertIn("复核摘要", zh_entry)
        self.assertIn("支撑偏弱（WEAK）", zh_entry)
        self.assertIn("警告（WARN）", zh_entry)
        self.assertIn("建议动作", zh_entry)
        self.assertIn("请确认该引用是否足以支撑当前较强表述", zh_entry)
        self.assertIn("Review summary", en_entry)
        self.assertIn("WEAK", en_entry)
        self.assertIn("WARN", en_entry)
        self.assertIn("Suggested action: Confirm whether the citation supports the stronger wording.", en_entry)
        self.assertLess(zh_entry.index("复核摘要"), zh_entry.index("风险信号"))
        self.assertLess(en_entry.index("Review summary"), en_entry.index("risk signals"))

    def test_render_localizes_zh_summary_rows(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 8,
                    "well_supported_pairs": 0,
                    "supported_pairs": 0,
                    "weak_pairs": 6,
                    "orphaned_pairs": 1,
                    "unverifiable_pairs": 1,
                    "unique_references_cited": 6,
                    "unique_references_never_cited": 0,
                    "citation_needed_candidates": 0,
                },
                "entries": [],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        zh_section = html.split('<section class="lang-panel" data-lang-panel="zh">', 1)[1].split('<section class="lang-panel" data-lang-panel="en">', 1)[0]

        self.assertIn("待补引用候选句", zh_section)
        self.assertIn("声明-引用对", zh_section)
        self.assertIn("孤立引用对", zh_section)
        self.assertIn("基本支撑引用对", zh_section)
        self.assertIn("已引用唯一参考文献数", zh_section)
        self.assertIn("未被引用唯一参考文献数", zh_section)
        self.assertIn("不可核验引用对", zh_section)
        self.assertIn("支撑偏弱引用对", zh_section)
        self.assertIn("支撑充分引用对", zh_section)
        self.assertIn("当前没有待补引用候选句。", zh_section)
        self.assertNotIn("CLAIM_CITATION_PAIRS", zh_section)
        self.assertNotIn("UNIQUE_REFERENCES_NEVER_CITED", zh_section)

    def test_render_scopes_navigation_anchors_per_language_panel(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 1,
                    "weak_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Manual review needed.",
                        "claim_type": "empirical_result",
                        "file": "main.tex",
                        "line": 10,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref1"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review again."],
                        "claim_context": "Claim one.",
                    }
                ],
                "citation_needed_candidates": [
                    {
                        "file": "main.tex",
                        "line": 22,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "Needs citation.",
                    }
                ],
                "uncited_references": [],
            }
        )

        self.assertIn('id="zh-citation-needed"', html)
        self.assertIn('id="en-citation-needed"', html)
        self.assertIn('href="#zh-citation-needed"', html)
        self.assertIn('href="#en-citation-needed"', html)
        self.assertIn('id="zh-triage-weak"', html)
        self.assertIn('id="en-triage-weak"', html)

    def test_render_adds_mobile_readability_rules_for_dense_review_surfaces(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 1,
                    "weak_pairs": 1,
                    "citation_needed_candidates": 1,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "ref1",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Manual review needed.",
                        "claim_type": "empirical_result",
                        "file": "main.tex",
                        "line": 10,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["ref1"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review again."],
                        "claim_context": "Claim one.",
                    }
                ],
                "citation_needed_candidates": [
                    {
                        "file": "main.tex",
                        "line": 22,
                        "claim_type": "empirical_result",
                        "risk_signal": "uncited_empirical_result",
                        "sentence": "Needs citation.",
                    }
                ],
                "uncited_references": [],
            }
        )

        self.assertIn("@media (max-width:560px)", html)
        self.assertIn(".nav-pill { width:100%; }", html)
        self.assertIn(".detail { grid-template-columns:1fr; }", html)
        self.assertIn(".review-group-card { padding:12px; }", html)
        self.assertIn(".entry-card { min-height:0; }", html)
        self.assertIn(".quick-jumps { flex-direction:column; align-items:stretch; }", html)

    def test_render_includes_file_slug_in_entry_anchors(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {
                    "claim_citation_pairs": 2,
                    "weak_pairs": 2,
                    "citation_needed_candidates": 0,
                    "unique_references_never_cited": 0,
                },
                "entries": [
                    {
                        "citation_key": "shared-ref",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Manual review needed.",
                        "claim_type": "empirical_result",
                        "file": "chapters/main.tex",
                        "line": 12,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["shared-ref"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review again."],
                        "claim_context": "Claim one.",
                    },
                    {
                        "citation_key": "shared-ref",
                        "triage_label": "WEAK",
                        "support_review_label": "NEEDS_MANUAL_REVIEW",
                        "support_review_reason": "Manual review needed.",
                        "claim_type": "empirical_result",
                        "file": "appendix/main.tex",
                        "line": 12,
                        "hallucination_risk_label": "REVIEW",
                        "cluster_keys": ["shared-ref"],
                        "cluster_review_reason": "Single-citation cluster.",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review again."],
                        "claim_context": "Claim two.",
                    },
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        self.assertIn('id="zh-entry-weak-chapters-main-tex-shared-ref-12"', html)
        self.assertIn('id="zh-entry-weak-appendix-main-tex-shared-ref-12"', html)
        self.assertIn('href="#zh-entry-weak-chapters-main-tex-shared-ref-12"', html)
        self.assertIn('href="#zh-entry-weak-appendix-main-tex-shared-ref-12"', html)

    def test_triage_sections_have_color_coded_css_classes(self) -> None:
        html = render_claim_citation_html(
            {
                "status": "WEAK",
                "summary": {"claim_citation_pairs": 3, "weak_pairs": 1, "supported_pairs": 1, "well_supported_pairs": 1},
                "entries": [
                    {
                        "citation_key": "orphan_ref",
                        "triage_label": "ORPHANED",
                        "support_review_label": "ORPHANED",
                        "support_review_reason": "Missing from bibliography.",
                        "claim_type": "empirical_result",
                        "file": "main.tex",
                        "line": 5,
                        "hallucination_risk_label": "HIGH_RISK",
                        "risk_signals": ["high_risk_reference"],
                        "support_signals": [],
                        "next_actions": ["Add the reference to bibliography."],
                        "claim_context": "The method improves accuracy.",
                    },
                    {
                        "citation_key": "weak_ref",
                        "triage_label": "WEAK",
                        "support_review_label": "WEAK_REVIEW",
                        "support_review_reason": "Weak support.",
                        "claim_type": "empirical_result",
                        "file": "main.tex",
                        "line": 10,
                        "hallucination_risk_label": "REVIEW",
                        "risk_signals": ["possible_overclaim"],
                        "support_signals": ["complete_metadata"],
                        "next_actions": ["Review the claim strength."],
                        "claim_context": "Significantly outperforms.",
                    },
                    {
                        "citation_key": "good_ref",
                        "triage_label": "WELL_SUPPORTED",
                        "support_review_label": "STRONG_REVIEW",
                        "support_review_reason": "Strong support.",
                        "claim_type": "background",
                        "file": "main.tex",
                        "line": 15,
                        "hallucination_risk_label": "PASS",
                        "risk_signals": [],
                        "support_signals": ["complete_metadata", "low_hallucination_risk"],
                        "next_actions": [],
                        "claim_context": "Prior work explored this.",
                    },
                ],
                "citation_needed_candidates": [],
                "uncited_references": [],
            }
        )

        self.assertIn('id="zh-triage-orphaned"', html)
        self.assertIn('id="zh-triage-weak"', html)
        self.assertIn('id="zh-triage-well_supported"', html)
        self.assertIn('class="section triage-group triage-orphaned"', html)
        self.assertIn('class="section triage-group triage-weak"', html)
        self.assertIn('class="section triage-group triage-well_supported"', html)

    def test_write_and_cli_generate_html(self) -> None:
        with workspace_tempdir("claim-citation-html-") as base:
            project = materialize_project(
                base / "project",
                {
                    "reports/claim-citation-triage-report.json": json.dumps(
                        {
                            "status": "SUPPORTED",
                            "summary": {"claim_citation_pairs": 1, "citation_needed_candidates": 0, "unique_references_never_cited": 0},
                            "entries": [],
                            "citation_needed_candidates": [],
                            "uncited_references": [],
                        },
                        ensure_ascii=False,
                    )
                },
            )
            write_claim_citation_html(
                project / "reports" / "claim-citation-triage-report.json",
                project / "reports" / "custom-claim-citation-triage.html",
            )
            result = subprocess.run(
                [sys.executable, str(CLI_SCRIPT), "--project-root", str(project)],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            default_output = project / "reports" / "claim-citation-triage.html"
            custom_output = project / "reports" / "custom-claim-citation-triage.html"
            default_exists = default_output.exists()
            custom_exists = custom_output.exists()
            html = default_output.read_text(encoding="utf-8")

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(default_exists)
        self.assertTrue(custom_exists)
        self.assertIn("Claim-Citation<br>Triage", html)
        self.assertIn("声明-引用<br>支撑分级", html)


if __name__ == "__main__":
    unittest.main()
