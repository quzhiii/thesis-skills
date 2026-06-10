from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from collections import Counter
from pathlib import Path


I18N = {
    "zh": {
        "lang": "zh-CN",
        "title": "声明-引用支撑分级",
        "kicker": "Thesis Skills / 声明-引用复核",
        "hero_title": "声明-引用<br>支撑分级",
        "lede": "这是一个基于声明-引用分级 JSON 生成的本地阅读页面。JSON 仍然是权威来源，HTML 只帮助人工复核。",
        "status": "总体状态",
        "pairs": "引用对",
        "citation_needed": "待补引用",
        "uncited_refs": "未被引用参考文献",
        "summary": "摘要",
        "review_aggregates": "复核聚合",
        "top_review_focus": "优先复核焦点",
        "review_groups": "复核分组",
        "review_groups_note": "仅基于现有 triage_label、support_review_label、risk_signals 和 hallucination_risk_label 的显示层优先级分组，不改变 JSON / Markdown / CSV 判断。",
        "group_evidence": "证据摘要",
        "group_rationale": "判断依据",
        "group_action": "建议动作",
        "entry_review_summary": "复核摘要",
        "review_queue": "复核队列",
        "review_queue_note": "先打开最高优先分级条目，再按源码顺序检查待补引用候选句。",
        "review_sequence": "先看最高优先分级分组，再看待补引用候选句，最后确认未被引用参考文献。",
        "triage_groups": "按分级标签查看",
        "citation_needed_section": "待补引用候选句",
        "uncited_section": "未被引用参考文献",
        "entries_section": "详细条目",
        "source_truth": "JSON / Markdown / CSV 仍然是权威来源。这个页面只帮助你按分级、引用簇和风险信号快速浏览。",
        "open_json": "打开 JSON 源文件",
        "open_md": "打开 Markdown 源文件",
        "open_csv": "打开 CSV 源文件",
        "related_reports": "相关报告",
        "quick_jumps": "快速跳转",
        "related_note": "在报告入口、readiness 门禁、终稿审计页面和引用审计台账页面之间跳转。",
        "report_index": "报告入口页",
        "readiness_json": "readiness JSON 报告",
        "final_audit": "终稿审计页面",
        "reference_ledger": "引用审计台账页面",
        "claim_type": "声明类型",
        "review_label": "复核标签",
        "risk_signals": "风险信号",
        "support_signals": "支撑信号",
        "next_actions": "下一步动作",
        "cluster": "引用簇",
        "risk_signal_key": "风险信号",
        "support_review_label_key": "复核标签",
        "cluster_reason": "簇级说明",
        "context": "声明上下文",
        "file": "文件",
        "line": "行号",
        "risk": "风险",
        "reason": "原因",
        "sentence": "句子",
        "key": "引用键",
        "citation_key_heading": "引用键",
        "title_label": "标题",
        "headline": "状态概览",
        "no_entries": "当前没有该分组条目。",
        "no_candidates": "当前没有待补引用候选句。",
        "no_uncited": "当前没有未被引用的参考文献。",
        "generated_from": "本页面根据",
        "regenerate_note": "生成。请先更新 claim-citation JSON 报告，再重新生成本 HTML 页面。",
        "no_value": "—",
    },
    "en": {
        "lang": "en",
        "title": "Claim-Citation Triage",
        "kicker": "Thesis Skills / Claim-Citation Review",
        "hero_title": "Claim-Citation<br>Triage",
        "lede": "This is a local reading surface generated from claim-citation triage JSON. JSON remains the source of truth; HTML only helps human review.",
        "status": "Overall status",
        "pairs": "pairs",
        "citation_needed": "citation-needed",
        "uncited_refs": "uncited refs",
        "summary": "Summary",
        "review_aggregates": "Review Aggregates",
        "top_review_focus": "Top review focus",
        "review_groups": "Review Groups",
        "review_groups_note": "Display-only priority buckets based only on existing triage_label, support_review_label, risk_signals, and hallucination_risk_label; JSON / Markdown / CSV judgments do not change.",
        "group_evidence": "Evidence",
        "group_rationale": "Rationale",
        "group_action": "Suggested action",
        "entry_review_summary": "Review summary",
        "review_queue": "Review queue",
        "review_queue_note": "Open the highest-priority triage entries first, then review citation-needed candidates in source order.",
        "review_sequence": "Start with the top triage group, then review citation-needed candidates, then confirm uncited references.",
        "triage_groups": "Browse by triage label",
        "citation_needed_section": "Citation-Needed Candidates",
        "uncited_section": "Uncited References",
        "entries_section": "Detailed entries",
        "source_truth": "JSON / Markdown / CSV remain authoritative. This page only helps you browse by triage label, cluster, and risk signals.",
        "open_json": "Open JSON source",
        "open_md": "Open Markdown source",
        "open_csv": "Open CSV source",
        "related_reports": "Related Reports",
        "quick_jumps": "Quick jumps",
        "related_note": "Jump between the report index, readiness gate, final-audit detail, and reference-ledger review surfaces.",
        "report_index": "Report index",
        "readiness_json": "Readiness JSON",
        "final_audit": "Final audit HTML",
        "reference_ledger": "Reference ledger HTML",
        "claim_type": "claim type",
        "review_label": "review label",
        "risk_signals": "risk signals",
        "support_signals": "support signals",
        "next_actions": "next actions",
        "cluster": "cluster",
        "risk_signal_key": "risk_signal",
        "support_review_label_key": "support_review_label",
        "cluster_reason": "cluster reason",
        "context": "claim context",
        "file": "file",
        "line": "line",
        "risk": "risk",
        "reason": "reason",
        "sentence": "sentence",
        "key": "citation key",
        "headline": "Status snapshot",
        "no_entries": "No entries in this group.",
        "no_candidates": "No citation-needed candidates.",
        "no_uncited": "No uncited references.",
        "generated_from": "This page is generated from",
        "regenerate_note": ". Re-run the claim-citation JSON report first, then regenerate this HTML page.",
        "no_value": "—",
    },
}


TRIAGE_ORDER = ["ORPHANED", "UNVERIFIABLE", "WEAK", "SUPPORTED", "WELL_SUPPORTED"]

REVIEW_GROUPS = [
    {
        "key": "p0",
        "labels": {"zh": "P0 · 必须先处理", "en": "P0 · Must review first"},
        "notes": {
            "zh": "孤立/不可核验引用、高风险参考文献信号，或 HIGH_RISK 幻觉风险标签。",
            "en": "ORPHANED / UNVERIFIABLE entries, high-risk reference signals, or HIGH_RISK hallucination labels.",
        },
    },
    {
        "key": "p1",
        "labels": {"zh": "P1 · 高优先复核", "en": "P1 · High-priority review"},
        "notes": {
            "zh": "支撑偏弱、需要人工复核、WARN/REVIEW 风险标签，或仍有风险信号的条目。",
            "en": "WEAK support, manual-review labels, WARN/REVIEW risk labels, or remaining risk signals.",
        },
    },
    {
        "key": "p2",
        "labels": {"zh": "P2 · 常规复核", "en": "P2 · Regular review"},
        "notes": {
            "zh": "未触发 P0/P1，但仍建议人工确认的常规支撑复核条目。",
            "en": "Entries that do not trigger P0/P1 but still deserve normal human confirmation.",
        },
    },
    {
        "key": "p3",
        "labels": {"zh": "P3 · 仅留档查看", "en": "P3 · Archive-only view"},
        "notes": {
            "zh": "SUPPORTED_DIRECTLY、PASS 且没有风险信号的条目，主要用于最终留档查看。",
            "en": "SUPPORTED_DIRECTLY, PASS, and no risk signals; kept mainly for final archive review.",
        },
    },
]

ZH_LABELS = {
    "ORPHANED": "孤立引用",
    "UNVERIFIABLE": "不可核验",
    "WEAK": "支撑偏弱",
    "SUPPORTED": "基本支撑",
    "WELL_SUPPORTED": "支撑充分",
    "NEEDS_MANUAL_REVIEW": "需要人工复核",
    "SUPPORTED_DIRECTLY": "直接支撑",
    "ADEQUATE_REVIEW": "基本可用",
    "WEAK_REVIEW": "需补强复核",
    "STRONG_REVIEW": "支撑较强",
    "empirical_result": "实证结果",
    "background_fact": "背景事实",
    "background": "背景说明",
    "unclear": "类型未明",
    "method_claim": "方法主张",
    "possible_topic_mismatch": "可能存在主题错配",
    "possible_outdated_support": "可能存在支撑过时",
    "possible_overclaim": "可能存在过度表述",
    "uncited_empirical_result": "实证结果缺少引用",
    "uncited_background_fact": "背景事实缺少引用",
    "complete_metadata": "元数据完整",
    "title_overlap": "标题词面重合",
    "metadata_title_overlap": "标题元数据重合",
    "metadata_abstract_overlap": "摘要元数据重合",
    "metadata_keyword_overlap": "关键词元数据重合",
    "has_claim_context": "存在声明上下文",
    "grouped_citation_cluster": "成组引用簇",
    "mixed_cluster_risk": "引用簇风险混合",
    "REVIEW": "需复核",
    "WARN": "警告",
    "PASS": "通过",
    "HIGH_RISK": "高风险",
    "UNSUPPORTED": "暂不支持自动核验",
    "incomplete_metadata": "元数据不完整",
    "bare_context": "上下文过少",
    "low_hallucination_risk": "幻觉风险较低",
    "unsupported_reference": "参考来源暂不支持自动核验",
    "missing_hallucination_evidence": "缺少幻觉风险证据",
    "empirical_claim_without_metadata_overlap": "实证声明缺少元数据重合",
    "high_risk_reference": "高风险参考文献",
    "weak_reference": "支撑偏弱参考文献",
    "cluster_high_risk_reference": "引用簇含高风险参考文献",
    "cluster_weak_reference": "引用簇含支撑偏弱参考文献",
    "orphaned_reference": "缺失参考文献条目",
}

ZH_HIDDEN_LABELS = {
    "complete_metadata",
    "title_overlap",
    "metadata_title_overlap",
    "metadata_abstract_overlap",
    "metadata_keyword_overlap",
    "has_claim_context",
    "grouped_citation_cluster",
    "mixed_cluster_risk",
}

ZH_TEXT_REWRITES = {
    "Citation key is missing from the bibliography.": "该引用键未出现在参考文献中。",
    "Reference is unsupported by the current automatic evidence layer.": "当前自动证据层暂时无法判断该来源是否可靠。",
    "Cited reference carries HIGH_RISK hallucination evidence.": "该引用携带 HIGH_RISK 幻觉风险证据，需要人工复核。",
    "Conservative support-risk heuristic flagged this claim-citation pair for manual review.": "保守的支撑风险启发式规则已将这组声明-引用对标记为需要人工复核。",
    "Evidence appears adequate with minor caveats.": "当前证据总体可用，但仍存在轻微注意点。",
    "Evidence is structurally weak or incomplete.": "当前证据在结构上偏弱或不完整。",
    "Evidence is structurally strong and low-risk.": "当前证据在结构上较强且风险较低。",
    "Review the grouped citations together.": "建议将这组引用作为同一引用簇一起复核。",
    "Single-citation cluster.": "当前只有单条引用，不构成成组引用簇。",
    "Repeated cluster.": "该引用簇在多个相邻位置重复出现。",
    "Review support.": "成组引用说明需复核。",
    "Manual review needed.": "该条引用需要人工复核。",
    "Direct support found.": "已发现直接支撑证据。",
    "Missing support details.": "当前缺少足够的支撑细节。",
    "Weak support pattern.": "当前支撑模式偏弱。",
    "Second manual review.": "该条目需要再次人工复核。",
    "No action needed.": "当前无需额外处理。",
    "Review again.": "建议再次复核。",
    "Open cited source and compare claim scope.": "请打开引用来源，并核对其支撑范围是否覆盖当前声明。",
    "Verify the cited source against DOI, publisher, database, or original document evidence.": "请结合 DOI、出版方、数据库或原始文档证据核对该引用来源。",
    "Review this citation cluster as a group because at least one grouped citation has risk signals.": "请作为同一引用簇一起复核这些引用，因为至少有一条成组引用带有风险信号。",
    "This citation appears in a grouped cluster with risk signals; review the grouped citations together.": "该引用出现在带有风险信号的成组引用簇中，建议将成组引用一起复核。",
    "This citation appears in a grouped cluster with no cluster-level risk flags.": "该引用出现在成组引用簇中，当前没有发现簇级风险标记。",
    "Verify whether the cited source supports the strength of the claim before final submission.": "请在最终提交前核对引用来源是否足以支撑当前声明强度。",
    "Check whether the cited source is on the same topic as the nearby claim; lexical metadata overlap is absent.": "请核对引用来源与邻近声明是否属于同一主题，因为当前词面元数据没有重合。",
    "Check whether newer evidence is needed or soften current/latest wording.": "请判断是否需要更新证据，或适当减弱当前/最新这类表述。",
    "Fix the citation key or add the missing bibliography entry after manual confirmation.": "请在人工确认后修复引用键，或补入缺失的参考文献条目。",
    "Manually verify the source because current evidence cannot automatically assess it.": "请人工核验该来源，因为当前自动证据无法完成判断。",
    "Check whether this reference directly supports the nearby claim or add a closer source.": "请核对这条参考文献是否直接支撑邻近声明，或补充更贴近的来源。",
    "Confirm whether the citation supports the stronger wording.": "请确认该引用是否足以支撑当前较强表述。",
    "Review the citation context and metadata before final submission.": "请在最终提交前复核引用上下文和元数据。",
    "No immediate action; keep available for final human review.": "当前无需立即处理，但请保留到最终人工复核阶段。",
    "The method achieves state-of-the-art results.": "该方法取得了当前最先进的结果。",
    "Ablation studies confirm each component.": "消融实验验证了各个组成部分的作用。",
    "The approach from also generalizes well.": "该方法也表现出良好的泛化能力。",
    "Prior work explored similar architectures with limited success.": "既有工作探索了类似架构，但效果有限。",
    "Multiple studies provide evidence for this hypothesis.": "多项研究为这一假设提供了证据。",
    "Another line of work has been proposed but details remain unclear.": "另一条研究路线已被提出，但细节仍不清楚。",
    "Chinese-language studies have also contributed with valuable insights.": "中文研究也提供了有价值的见解。",
}

ZH_SUMMARY_KEYS = {
    "citation_needed_candidates": "待补引用候选句",
    "claim_citation_pairs": "声明-引用对",
    "orphaned_pairs": "孤立引用对",
    "supported_pairs": "基本支撑引用对",
    "unique_references_cited": "已引用唯一参考文献数",
    "unique_references_never_cited": "未被引用唯一参考文献数",
    "unverifiable_pairs": "不可核验引用对",
    "weak_pairs": "支撑偏弱引用对",
    "well_supported_pairs": "支撑充分引用对",
}


def _load_json(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("claim-citation report must be a JSON object")
    return payload


def _e(value: object, lang: str = "en") -> str:
    fallback = I18N[lang]["no_value"]
    return html.escape(str(value if value not in (None, "", []) else fallback))


def _display_value(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        zh_label = ZH_LABELS.get(text)
        if zh_label:
            return html.escape(f"{zh_label}（{text}）")
    return html.escape(text)


def _display_list_item(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        zh_label = ZH_LABELS.get(text)
        if zh_label:
            if text in ZH_HIDDEN_LABELS:
                return html.escape(zh_label)
            return html.escape(f"{zh_label}（{text}）")
    return html.escape(text)


def _display_free_text(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        rewritten = ZH_TEXT_REWRITES.get(text)
        if rewritten:
            return html.escape(rewritten)
    return html.escape(text)


def _display_status_value(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        zh_label = ZH_LABELS.get(text)
        if zh_label:
            return html.escape(zh_label)
    return html.escape(text)


def _display_citation_heading(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        return html.escape(f"{I18N[lang]['citation_key_heading']}：{text}")
    return html.escape(text)


def _display_summary_key(value: object, lang: str = "en") -> str:
    if value in (None, "", []):
        return _e("", lang)
    text = str(value)
    if lang == "zh":
        zh_label = ZH_SUMMARY_KEYS.get(text)
        if zh_label:
            return html.escape(zh_label)
    return html.escape(text)


def _slug_fragment(value: object) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "item"


def _panel_anchor_id(lang: str, suffix: str) -> str:
    return f"{lang}-{suffix}"


def _entry_anchor_id(entry: dict[str, object], lang: str) -> str:
    return "-".join(
        [
            lang,
            "entry",
            _slug_fragment(entry.get("triage_label", "entry")),
            _slug_fragment(entry.get("file", "item")),
            _slug_fragment(entry.get("citation_key", "item")),
            _slug_fragment(entry.get("line", "0")),
        ]
    )


def _citation_needed_anchor_id(candidate: dict[str, object], lang: str, occurrence: int = 1) -> str:
    anchor = "-".join(
        [
            lang,
            "citation-needed",
            _slug_fragment(candidate.get("file", "item")),
            _slug_fragment(candidate.get("line", "0")),
        ]
    )
    if occurrence == 1:
        return anchor
    return f"{anchor}-{occurrence}"


def _citation_needed_candidates_with_anchor_ids(
    candidates: list[dict[str, object]],
    lang: str,
) -> list[tuple[dict[str, object], str]]:
    seen: Counter[str] = Counter()
    anchored: list[tuple[dict[str, object], str]] = []
    for candidate in sorted(candidates, key=_candidate_sort_key):
        base_anchor = _citation_needed_anchor_id(candidate, lang)
        seen[base_anchor] += 1
        anchored.append((candidate, _citation_needed_anchor_id(candidate, lang, seen[base_anchor])))
    return anchored


def _candidate_sort_key(candidate: dict[str, object]) -> tuple[str, int]:
    return (str(candidate.get("file", "")), int(candidate.get("line") or 0))


def _lang_switch() -> str:
    return """
    <div class="lang-switch" role="group" aria-label="Language switch">
      <button type="button" class="lang-btn active" data-lang-btn="zh">中文</button>
      <button type="button" class="lang-btn" data-lang-btn="en">EN</button>
    </div>
"""


def _lang_script() -> str:
    return """
  <script>
    (() => {
      const root = document.documentElement;
      const buttons = Array.from(document.querySelectorAll('[data-lang-btn]'));
      const apply = (lang) => {
        root.setAttribute('data-lang', lang);
        buttons.forEach((btn) => btn.classList.toggle('active', btn.dataset.langBtn === lang));
      };
      buttons.forEach((btn) => btn.addEventListener('click', () => apply(btn.dataset.langBtn)));
      apply('zh');
    })();
  </script>
"""


def _list_html(values: object, lang: str) -> str:
    if not isinstance(values, list) or not values:
        return f"<span class=\"muted\">{_e('', lang)}</span>"
    return "<ul>" + "".join(f"<li>{_display_list_item(item, lang)}</li>" for item in values) + "</ul>"


def _free_text_list_html(values: object, lang: str) -> str:
    if not isinstance(values, list) or not values:
        return f"<span class=\"muted\">{_e('', lang)}</span>"
    return "<ul>" + "".join(f"<li>{_display_free_text(item, lang)}</li>" for item in values) + "</ul>"


def _summary_rows(summary: dict[str, object], lang: str) -> str:
    rows = []
    for key in sorted(summary):
        rows.append(f"<tr><th>{_display_summary_key(key, lang)}</th><td>{_display_value(summary[key], lang)}</td></tr>")
    return "".join(rows)


def _aggregate_rows(entries: list[dict[str, object]], citation_needed: list[dict[str, object]], lang: str) -> str:
    support_review_counts = Counter(
        str(entry.get("support_review_label", ""))
        for entry in entries
        if entry.get("support_review_label")
    )
    risk_signal_counts = Counter()
    for entry in entries:
        signals = entry.get("risk_signals")
        if isinstance(signals, list):
            risk_signal_counts.update(str(item) for item in signals if item)
    citation_needed_counts = Counter(
        str(item.get("risk_signal", ""))
        for item in citation_needed
        if item.get("risk_signal")
    )
    cluster_counts = Counter()
    for entry in entries:
        cluster_keys = entry.get("cluster_keys")
        if isinstance(cluster_keys, list) and cluster_keys:
            cluster_counts.update([", ".join(str(key) for key in cluster_keys)])

    sections = [
        (I18N[lang]["support_review_label_key"], support_review_counts),
        (I18N[lang]["risk_signal_key"], risk_signal_counts),
        (I18N[lang]["citation_needed"], citation_needed_counts),
        (I18N[lang]["cluster"], cluster_counts),
    ]
    rows: list[str] = []
    for name, counts in sections:
        if counts:
            value = "<ul>" + "".join(
                f"<li>{_display_value(label, lang)} ({count})</li>" for label, count in sorted(counts.items())
            ) + "</ul>"
        else:
            value = f'<span class="muted">{_e("", lang)}</span>'
        rows.append(f"<tr><th>{_e(name, lang)}</th><td>{value}</td></tr>")
    return "".join(rows)


def _top_focus_line(entries: list[dict[str, object]], citation_needed: list[dict[str, object]], lang: str) -> str:
    triage_counts = Counter(
        str(entry.get("triage_label", ""))
        for entry in entries
        if entry.get("triage_label")
    )
    support_review_counts = Counter(
        str(entry.get("support_review_label", ""))
        for entry in entries
        if entry.get("support_review_label")
    )
    risk_signal_counts = Counter()
    for entry in entries:
        signals = entry.get("risk_signals")
        if isinstance(signals, list):
            risk_signal_counts.update(str(item) for item in signals if item)
    cluster_counts = Counter()
    for entry in entries:
        cluster_keys = entry.get("cluster_keys")
        if isinstance(cluster_keys, list) and cluster_keys:
            cluster_counts.update([", ".join(str(key) for key in cluster_keys)])

    focus_parts: list[str] = []
    if triage_counts:
        for triage_label in TRIAGE_ORDER:
            triage_count = triage_counts.get(triage_label, 0)
            if triage_count:
                focus_parts.append(
                    f'<a href="#{html.escape(_panel_anchor_id(lang, f"triage-{triage_label.lower()}"))}">{_display_value(triage_label, lang)} ({triage_count})</a>'
                )
                break
    if support_review_counts:
        label, count = support_review_counts.most_common(1)[0]
        focus_parts.append(f"{_display_value(label, lang)} ({count})")
    if risk_signal_counts:
        label, count = risk_signal_counts.most_common(1)[0]
        focus_parts.append(f"{_display_value(label, lang)} ({count})")
    if cluster_counts:
        label, count = cluster_counts.most_common(1)[0]
        focus_parts.append(f"{_display_value(label, lang)} ({count})")
    if not focus_parts and citation_needed:
        signal_counts = Counter(
            str(item.get("risk_signal", "")) for item in citation_needed if item.get("risk_signal")
        )
        if signal_counts:
            label, count = signal_counts.most_common(1)[0]
            focus_parts.append(f"{_display_value(label, lang)} ({count})")
    if not focus_parts:
        return f'<p class="meta-copy">{_e("", lang)}</p>'
    return f'<p class="meta-copy"><strong>{_e(I18N[lang]["top_review_focus"], lang)}</strong>: {" · ".join(focus_parts)}</p>'


def _review_queue(entries: list[dict[str, object]], lang: str) -> str:
    queue = [
        entry
        for entry in entries
        if not (
            str(entry.get("triage_label", "")) in {"SUPPORTED", "WELL_SUPPORTED"}
            and str(entry.get("support_review_label", "")) == "SUPPORTED_DIRECTLY"
        )
    ]
    if not queue:
        return ""
    order = {label: index for index, label in enumerate(TRIAGE_ORDER)}
    pills = "".join(
        f'<a class="nav-pill" href="#{html.escape(_entry_anchor_id(entry, lang))}">{_display_value(entry.get("triage_label", ""), lang)} · {_e(entry.get("citation_key", ""), lang)} · {_e(entry.get("file", ""), lang)}:{_e(entry.get("line", ""), lang)}</a>'
        for entry in sorted(
            queue,
            key=lambda item: (
                order.get(str(item.get("triage_label", "")), len(TRIAGE_ORDER)),
                str(item.get("file", "")),
                int(item.get("line") or 0),
                str(item.get("citation_key", "")),
            ),
        )
    )
    return f'<div class="review-queue"><p class="meta-copy"><strong>{_e(I18N[lang]["review_queue"], lang)}</strong></p><p class="meta-copy">{_e(I18N[lang]["review_queue_note"], lang)}</p><div class="nav-pills">{pills}</div></div>'


def _review_group_key(entry: dict[str, object]) -> str:
    triage_label = str(entry.get("triage_label", ""))
    support_review_label = str(entry.get("support_review_label", ""))
    risk_label = str(entry.get("hallucination_risk_label", ""))
    risk_signals = entry.get("risk_signals")
    signal_values = {str(item) for item in risk_signals if item} if isinstance(risk_signals, list) else set()
    if triage_label in {"ORPHANED", "UNVERIFIABLE"} or risk_label == "HIGH_RISK" or any(
        signal in signal_values for signal in {"high_risk_reference", "cluster_high_risk_reference"}
    ):
        return "p0"
    if (
        triage_label == "WEAK"
        or support_review_label in {"NEEDS_MANUAL_REVIEW", "WEAK_REVIEW"}
        or risk_label in {"WARN", "REVIEW"}
        or bool(signal_values)
    ):
        return "p1"
    if support_review_label in {"SUPPORTED_DIRECTLY", "STRONG_REVIEW"} and risk_label == "PASS" and not signal_values:
        return "p3"
    return "p2"


def _review_groups(entries: list[dict[str, object]], lang: str) -> str:
    if not entries:
        return ""
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        grouped[_review_group_key(entry)].append(entry)

    group_nav = "".join(
        f'<a class="nav-pill" href="#{html.escape(_panel_anchor_id(lang, f"review-group-{group_key}"))}">{html.escape(group["labels"][lang])} ({len(grouped[group_key])})</a>'
        for group in REVIEW_GROUPS
        for group_key in [str(group["key"])]
        if grouped.get(group_key, [])
    )
    cards: list[str] = []
    for group in REVIEW_GROUPS:
        key = str(group["key"])
        group_entries = sorted(
            grouped.get(key, []),
            key=lambda item: (str(item.get("file", "")), int(item.get("line") or 0), str(item.get("citation_key", ""))),
        )
        if not group_entries:
            continue
        lead_entry = group_entries[0]
        lead_risk_signals = lead_entry.get("risk_signals") if isinstance(lead_entry.get("risk_signals"), list) else []
        lead_evidence = [
            _display_value(lead_entry.get("hallucination_risk_label", ""), lang),
            _display_list_item(lead_risk_signals[0], lang) if lead_risk_signals else "",
        ]
        lead_evidence = " · ".join(item for item in lead_evidence if item and item != _e("", lang))
        links = "".join(
            f'<a class="nav-pill" href="#{html.escape(_entry_anchor_id(entry, lang))}">{_display_value(entry.get("triage_label", ""), lang)} · {_e(entry.get("citation_key", ""), lang)} · {_e(entry.get("file", ""), lang)}:{_e(entry.get("line", ""), lang)}</a>'
            for entry in group_entries
        )
        cards.append(
            f'<article class="review-group-card" id="{html.escape(_panel_anchor_id(lang, f"review-group-{key}"))}"><h3>{html.escape(group["labels"][lang])}</h3><p class="meta-copy">{html.escape(group["notes"][lang])}</p><div class="detail"><strong>{_e(I18N[lang]["group_evidence"], lang)}</strong><span>{lead_evidence or _e("", lang)}</span></div><div class="detail"><strong>{_e(I18N[lang]["group_rationale"], lang)}</strong><span>{_display_free_text(lead_entry.get("support_review_reason", ""), lang)}</span></div><div class="detail"><strong>{_e(I18N[lang]["group_action"], lang)}</strong><span>{_display_free_text((lead_entry.get("next_actions") or [""])[0], lang)}</span></div><div class="nav-pills">{links}</div></article>'
        )
    return f'<div class="review-groups" id="{html.escape(_panel_anchor_id(lang, "review-groups"))}"><p class="meta-copy"><strong>{_e(I18N[lang]["review_groups"], lang)}</strong></p><p class="meta-copy">{_e(I18N[lang]["review_groups_note"], lang)}</p><div class="nav-pills">{group_nav}</div><div class="review-group-grid">{"".join(cards)}</div></div>'


def _triage_group_pills(entries: list[dict[str, object]], lang: str) -> str:
    triage_counts = Counter(
        str(entry.get("triage_label", ""))
        for entry in entries
        if entry.get("triage_label")
    )
    pills = "".join(
        f'<a class="nav-pill" href="#{html.escape(_panel_anchor_id(lang, f"triage-{label.lower()}"))}">{_display_value(label, lang)} ({triage_counts[label]})</a>'
        for label in TRIAGE_ORDER
        if triage_counts.get(label, 0)
    )
    if not pills:
        return ""
    return f'<div class="nav-pills">{pills}</div>'


def _citation_needed_jump_pills(candidates: list[dict[str, object]], lang: str) -> str:
    if not candidates:
        return ""
    pills = "".join(
        f'<a class="nav-pill" href="#{html.escape(anchor_id)}">{_e(item.get("file", ""), lang)}:{_e(item.get("line", ""), lang)}</a>'
        for item, anchor_id in _citation_needed_candidates_with_anchor_ids(candidates, lang)
    )
    return f'<div class="nav-pills">{pills}</div>'


def _entry_card(entry: dict[str, object], lang: str) -> str:
    cluster_keys = entry.get("cluster_keys")
    cluster_html = ", ".join(_e(item, lang) for item in cluster_keys) if isinstance(cluster_keys, list) and cluster_keys else _e("", lang)
    next_actions = entry.get("next_actions") if isinstance(entry.get("next_actions"), list) else []
    summary_parts = [
        _display_value(entry.get("triage_label", ""), lang),
        _display_value(entry.get("hallucination_risk_label", ""), lang),
    ]
    if next_actions:
        action_label = "建议动作" if lang == "zh" else "Suggested action"
        summary_parts.append(f"{action_label}: {_display_free_text(next_actions[0], lang)}")
    review_summary = " · ".join(part for part in summary_parts if part and part != _e("", lang))
    return f"""
      <article id="{html.escape(_entry_anchor_id(entry, lang))}" class="entry-card status-{_e(entry.get('triage_label', ''), lang).lower()}">
        <div class="entry-top">
          <span class="pill">{_display_value(entry.get('triage_label', ''), lang)}</span>
          <span class="pill muted">{_display_value(entry.get('support_review_label', ''), lang)}</span>
        </div>
        <h3>{_display_citation_heading(entry.get('citation_key', ''), lang)}</h3>
        <p class="meta">{_e(I18N[lang]['file'], lang)}: {_e(entry.get('file', ''), lang)} · {_e(I18N[lang]['line'], lang)}: {_e(entry.get('line', ''), lang)}</p>
        <p>{_display_free_text(entry.get('support_review_reason', ''), lang)}</p>
        <p class="meta-copy"><strong>{_e(I18N[lang]['entry_review_summary'], lang)}</strong>: {review_summary}</p>
        <div class="detail"><strong>{_e(I18N[lang]['claim_type'], lang)}</strong><span>{_display_value(entry.get('claim_type', ''), lang)}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['risk'], lang)}</strong><span>{_display_value(entry.get('hallucination_risk_label', ''), lang)}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['cluster'], lang)}</strong><span>{cluster_html}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['cluster_reason'], lang)}</strong><span>{_display_free_text(entry.get('cluster_review_reason', ''), lang)}</span></div>
        <div class="detail-block"><strong>{_e(I18N[lang]['risk_signals'], lang)}</strong>{_list_html(entry.get('risk_signals'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['support_signals'], lang)}</strong>{_list_html(entry.get('support_signals'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['next_actions'], lang)}</strong>{_free_text_list_html(entry.get('next_actions'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['context'], lang)}</strong><blockquote>{_display_free_text(entry.get('claim_context', ''), lang)}</blockquote></div>
      </article>
"""


def _triage_sections(entries: list[dict[str, object]], lang: str) -> str:
    by_label: dict[str, list[dict[str, object]]] = defaultdict(list)
    for entry in entries:
        by_label[str(entry.get("triage_label", ""))].append(entry)
    blocks: list[str] = []
    for label in TRIAGE_ORDER:
        group = by_label.get(label, [])
        cards = "".join(_entry_card(entry, lang) for entry in sorted(group, key=lambda item: (str(item.get("file", "")), int(item.get("line") or 0))))
        if not cards:
            cards = f"<div class=\"empty\">{_e(I18N[lang]['no_entries'], lang)}</div>"
        blocks.append(
            f"""
      <section class="section" id="{html.escape(_panel_anchor_id(lang, f'triage-{label.lower()}'))}">
        <div class="section-head"><h2>{_display_value(label, lang)}</h2><span class="meta">{len(group)}</span></div>
        <div class="entry-grid">{cards}</div>
      </section>
"""
        )
    return "".join(blocks)


def _candidate_rows(candidates: list[dict[str, object]], lang: str) -> str:
    if not candidates:
        return f"<div class=\"empty\">{_e(I18N[lang]['no_candidates'], lang)}</div>"
    rows = []
    for item, anchor_id in _citation_needed_candidates_with_anchor_ids(candidates, lang):
        rows.append(
            f"<tr id=\"{html.escape(anchor_id)}\"><td>{_e(item.get('file', ''), lang)}:{_e(item.get('line', ''), lang)}</td><td>{_display_value(item.get('claim_type', ''), lang)}</td><td>{_display_value(item.get('risk_signal', ''), lang)}</td><td>{_e(item.get('sentence', ''), lang)}</td></tr>"
        )
    return f"<table><thead><tr><th>{_e(I18N[lang]['file'], lang)}</th><th>{_e(I18N[lang]['claim_type'], lang)}</th><th>{_e(I18N[lang]['risk_signals'], lang)}</th><th>{_e(I18N[lang]['sentence'], lang)}</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"


def _uncited_rows(rows: list[dict[str, object]], lang: str) -> str:
    if not rows:
        return f"<div class=\"empty\">{_e(I18N[lang]['no_uncited'], lang)}</div>"
    body = []
    for item in rows:
        body.append(f"<tr><td>{_e(item.get('citation_key', ''), lang)}</td><td>{_e(item.get('title', ''), lang)}</td><td>{_display_value(item.get('hallucination_risk_label', ''), lang)}</td></tr>")
    return f"<table><thead><tr><th>{_e(I18N[lang]['key'], lang)}</th><th>{_e(I18N[lang].get('title_label', 'title'), lang)}</th><th>{_e(I18N[lang]['risk'], lang)}</th></tr></thead><tbody>{''.join(body)}</tbody></table>"


def _related_reports(lang: str) -> str:
    links = [
        ("index.html", I18N[lang]["report_index"]),
        ("readiness-report.json", I18N[lang]["readiness_json"]),
        (f"final-audit-report.html#warning-issues-{lang}", I18N[lang]["final_audit"]),
        (f"reference-audit-ledger.html#evidence-rows-{lang}", I18N[lang]["reference_ledger"]),
    ]
    pills = "".join(f'<a class="nav-pill" href="{html.escape(path)}">{html.escape(label)}</a>' for path, label in links)
    return f"""
      <section class="section nav-section">
        <div class="section-head"><h2>{_e(I18N[lang]['related_reports'], lang)}</h2><span class="meta-copy">{_e(I18N[lang]['related_note'], lang)}</span></div>
        <div class="nav-pills">{pills}</div>
      </section>
"""


def _quick_jumps(lang: str) -> str:
    links = [
        (f"#{_panel_anchor_id(lang, 'review-groups')}", I18N[lang]["review_groups"]),
        (f"#{_panel_anchor_id(lang, 'citation-needed')}", I18N[lang]["citation_needed_section"]),
        (f"#{_panel_anchor_id(lang, 'uncited-references')}", I18N[lang]["uncited_section"]),
        (f"#{_panel_anchor_id(lang, 'triage-groups')}", I18N[lang]["triage_groups"]),
    ]
    pills = "".join(f'<a class="nav-pill" href="{html.escape(path)}">{html.escape(label)}</a>' for path, label in links)
    return f'<div class="nav-pills quick-jumps"><span class="meta-copy">{_e(I18N[lang]["quick_jumps"], lang)}</span>{pills}</div>'


def _lang_block(report: dict[str, object], lang: str) -> str:
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    entries = report.get("entries") if isinstance(report.get("entries"), list) else []
    citation_needed = report.get("citation_needed_candidates") if isinstance(report.get("citation_needed_candidates"), list) else []
    uncited = report.get("uncited_references") if isinstance(report.get("uncited_references"), list) else []
    return f"""
    <section class="lang-panel" data-lang-panel="{lang}">
      <header>
        <div>
          <div class="kicker">{html.escape(I18N[lang]['kicker'])}</div>
          <h1>{I18N[lang]['hero_title']}</h1>
          <p class="lede">{html.escape(I18N[lang]['lede'])}</p>
        </div>
        <div class="stats">
          <div class="stat"><strong>{_display_status_value(report.get('status', ''), lang)}</strong><span>{_e(I18N[lang]['status'], lang)}</span></div>
          <div class="stat"><strong>{len(entries)}</strong><span>{_e(I18N[lang]['pairs'], lang)}</span></div>
          <div class="stat"><strong>{len(citation_needed)}</strong><span>{_e(I18N[lang]['citation_needed'], lang)}</span></div>
          <div class="stat"><strong>{len(uncited)}</strong><span>{_e(I18N[lang]['uncited_refs'], lang)}</span></div>
        </div>
      </header>
      <section class="notice">{html.escape(I18N[lang]['source_truth'])} <a href="claim-citation-triage-report.json">{html.escape(I18N[lang]['open_json'])}</a> · <a href="claim-citation-triage.md">{html.escape(I18N[lang]['open_md'])}</a> · <a href="claim-citation-triage.csv">{html.escape(I18N[lang]['open_csv'])}</a></section>
      <section class="section">
        <div class="section-head"><h2>{_e(I18N[lang]['summary'], lang)}</h2></div>
        <table><tbody>{_summary_rows(summary, lang)}</tbody></table>
      </section>
      <section class="section">
        <div class="section-head"><h2>{_e(I18N[lang]['review_aggregates'], lang)}</h2></div>
        {_top_focus_line(entries, citation_needed, lang)}
        {_review_groups(entries, lang)}
        {_review_queue(entries, lang)}
        <p class="meta-copy">{_e(I18N[lang]['review_sequence'], lang)}</p>
        {_quick_jumps(lang)}
        <table><tbody>{_aggregate_rows(entries, citation_needed, lang)}</tbody></table>
      </section>
      <section class="section" id="{html.escape(_panel_anchor_id(lang, 'citation-needed'))}">
        <div class="section-head"><h2>{_e(I18N[lang]['citation_needed_section'], lang)}</h2></div>
        {_citation_needed_jump_pills(citation_needed, lang)}
        {_candidate_rows(citation_needed, lang)}
      </section>
      <section class="section" id="{html.escape(_panel_anchor_id(lang, 'uncited-references'))}">
        <div class="section-head"><h2>{_e(I18N[lang]['uncited_section'], lang)}</h2></div>
        {_uncited_rows(uncited, lang)}
      </section>
      <section class="section" id="{html.escape(_panel_anchor_id(lang, 'triage-groups'))}">
        <div class="section-head"><h2>{_e(I18N[lang]['triage_groups'], lang)}</h2></div>
        {_triage_group_pills(entries, lang)}
      </section>
      {_triage_sections(entries, lang)}
      {_related_reports(lang)}
      <div class="raw-note">{_e(I18N[lang]['generated_from'], lang)} <a href="claim-citation-triage-report.json">claim-citation-triage-report.json</a>{_e(I18N[lang]['regenerate_note'], lang)}</div>
    </section>
"""


def render_claim_citation_html(report: dict[str, object]) -> str:
    zh_block = _lang_block(report, "zh")
    en_block = _lang_block(report, "en")
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(I18N['zh']['title'])}</title>
  <style>
    :root {{ --paper:#fafaf8; --ink:#0a0a0a; --grey-1:#f0f0ee; --grey-2:#d4d4d2; --grey-3:#737373; --accent:#002FA7; --accent-on:#fff; --warn:#b45309; --block:#b42318; --pass:#047857; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font-family:Inter, "Helvetica Neue", Helvetica, Arial, "Noto Sans SC", sans-serif; }}
    .page {{ max-width:1320px; margin:0 auto; padding:24px 20px 56px; }}
    .lang-switch {{ display:flex; justify-content:flex-end; gap:8px; margin-bottom:14px; }}
    .lang-btn {{ border:1px solid var(--grey-2); background:#fff; color:var(--ink); padding:8px 12px; font:600 13px/1 Inter, "Segoe UI", sans-serif; cursor:pointer; }}
    .lang-btn.active {{ background:var(--accent); color:#fff; border-color:var(--accent); }}
    [data-lang-panel] {{ display:none; }}
    html[data-lang="zh"] [data-lang-panel="zh"], html[data-lang="en"] [data-lang-panel="en"] {{ display:block; }}
    header {{ display:grid; grid-template-columns:1.2fr .8fr; gap:24px; align-items:end; border-bottom:2px solid var(--ink); padding-bottom:24px; }}
    .kicker {{ text-transform:uppercase; letter-spacing:.16em; font-size:12px; font-weight:800; color:var(--accent); }}
    h1 {{ font-size:clamp(42px, 9vw, 96px); line-height:.9; letter-spacing:-.06em; margin:12px 0; font-weight:200; }}
    .lede {{ color:var(--grey-3); font-size:18px; line-height:1.55; max-width:760px; }}
    .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }}
    .stat {{ background:#fff; border:1px solid var(--grey-2); padding:14px; }}
    .stat strong {{ display:block; font-size:34px; font-weight:250; letter-spacing:-.04em; }}
    .stat span {{ color:var(--grey-3); font-size:13px; }}
    .notice {{ margin:24px 0; border:1px solid var(--grey-2); background:#fff7ed; padding:16px; color:#7c2d12; }}
    .section {{ margin-top:30px; }}
    .section-head {{ display:flex; justify-content:space-between; gap:12px; align-items:end; border-bottom:1px solid var(--ink); padding-bottom:10px; margin-bottom:16px; }}
    h2 {{ margin:0; font-size:32px; font-weight:300; letter-spacing:-.04em; }}
    .entry-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .entry-card {{ background:#fff; border:1px solid var(--grey-2); padding:16px; display:flex; flex-direction:column; gap:10px; min-height:260px; }}
    .entry-top {{ display:flex; gap:8px; flex-wrap:wrap; }}
    .pill {{ display:inline-block; padding:4px 7px; background:var(--grey-1); font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; font-size:11px; letter-spacing:.1em; }}
    .muted {{ color:var(--grey-3); }}
    .nav-pills {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .nav-pill {{ display:inline-block; padding:10px 12px; border:1px solid var(--grey-2); background:#fff; }}
    .meta-copy {{ color:var(--grey-3); font-size:14px; }}
    .review-groups {{ display:flex; flex-direction:column; gap:12px; margin:16px 0 18px; }}
    .review-group-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .review-group-card {{ background:#fff; border:1px solid var(--grey-2); padding:14px; display:flex; flex-direction:column; gap:10px; }}
    .review-queue {{ display:flex; flex-direction:column; gap:10px; margin:14px 0 18px; }}
    h3 {{ margin:0; font-size:24px; font-weight:420; letter-spacing:-.03em; }}
    p {{ margin:0; color:var(--grey-3); line-height:1.5; }}
    .meta {{ font-family:"IBM Plex Mono", Consolas, monospace; font-size:12px; }}
    .detail {{ display:grid; grid-template-columns:140px 1fr; gap:8px; font-size:14px; }}
    .detail strong, .detail-block strong {{ color:var(--ink); }}
    .detail-block {{ border-top:1px solid var(--grey-2); padding-top:10px; }}
    ul {{ margin:8px 0 0 18px; padding:0; }}
    li {{ margin:4px 0; color:var(--grey-3); }}
    blockquote {{ margin:8px 0 0; padding:12px 14px; border-left:3px solid var(--accent); background:var(--grey-1); color:var(--ink); }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th, td {{ border-bottom:1px solid var(--grey-2); text-align:left; padding:10px 8px; vertical-align:top; font-size:13px; }}
    th {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; letter-spacing:.1em; font-size:11px; color:var(--grey-3); }}
    .empty {{ padding:18px; border:1px solid var(--grey-2); background:#fff; color:var(--grey-3); }}
    .raw-note {{ margin-top:24px; padding:16px; border:1px solid var(--grey-2); background:var(--grey-1); color:var(--grey-3); }}
    a {{ color:var(--accent); font-weight:700; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:980px) {{ header, .entry-grid, .review-group-grid {{ grid-template-columns:1fr; }} .stats {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:560px) {{ .stats {{ grid-template-columns:1fr; }} .page {{ padding:18px 14px 40px; }} .nav-pill {{ width:100%; }} .detail {{ grid-template-columns:1fr; }} .quick-jumps {{ flex-direction:column; align-items:stretch; }} .review-group-card {{ padding:12px; }} .entry-card {{ min-height:0; }} }}
  </style>
</head>
<body>
  <main class="page">
    {_lang_switch()}
    {zh_block}
    {en_block}
  </main>
{_lang_script()}
</body>
</html>
"""


def write_claim_citation_html(report_path: str | Path, output: str | Path) -> None:
    report = _load_json(report_path)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_claim_citation_html(report), encoding="utf-8")
