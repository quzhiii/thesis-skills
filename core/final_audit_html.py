from __future__ import annotations

import html
import json
from pathlib import Path


I18N = {
    "zh": {
        "lang": "zh-CN",
        "title": "终稿审计报告",
        "kicker": "Thesis Skills / Final Audit",
        "hero_title": "终稿<br>审计",
        "overall_verdict": "总体结论",
        "dimensions": "维度数",
        "blockers": "阻断项",
        "warnings": "警告项",
        "missing_required": "缺失必需证据",
        "dimension_matrix": "维度矩阵",
        "source_linked": "可回溯到源证据",
        "blocking_issues": "阻断问题",
        "must_resolve": "必须处理",
        "warning_issues": "警告问题",
        "manual_review": "人工复核",
        "next_actions": "下一步动作",
        "deduped": "去重后",
        "source_artifacts": "源产物",
        "source_truth": "JSON / CSV 仍是 authoritative source",
        "related_reports": "相关报告",
        "related_reports_note": "在报告入口、readiness 门禁、引用台账和声明-引用支撑分级之间快速跳转。",
        "report_index": "报告入口页",
        "readiness_json": "readiness JSON",
        "reference_ledger_html": "引用审计 HTML",
        "claim_citation_html": "声明-引用 HTML",
        "artifact": "产物",
        "status": "状态",
        "kind": "类型",
        "path": "路径",
        "required": "必需",
        "optional": "可选",
        "present": "已生成",
        "missing": "缺失",
        "unreadable": "不可读取",
        "no_blockers": "当前没有阻断项。",
        "no_warnings": "当前没有警告项。",
        "no_next_actions": "当前没有下一步动作。",
        "no_compact_metrics": "暂无紧凑指标",
        "generated_from": "本页面根据",
        "regenerate_note": "生成。请先更新 JSON checker 报告，再重新生成本 HTML 页面。",
        "headline_warn": "终稿审计结论：WARN",
        "headline_pass": "终稿审计结论：PASS",
        "headline_block": "终稿审计结论：BLOCK",
        "source_truth_summary": "JSON 报告仍是 authoritative source；本产物只做聚合展示，不重新运行检查，也不改写源文件。",
    },
    "en": {
        "lang": "en",
        "title": "Final Audit Report",
        "kicker": "Thesis Skills / Final Audit",
        "hero_title": "Final<br>Audit",
        "overall_verdict": "Overall verdict",
        "dimensions": "dimensions",
        "blockers": "blockers",
        "warnings": "warnings",
        "missing_required": "missing required",
        "dimension_matrix": "Dimension Matrix",
        "source_linked": "source-linked",
        "blocking_issues": "Blocking Issues",
        "must_resolve": "must resolve",
        "warning_issues": "Warnings",
        "manual_review": "manual review",
        "next_actions": "Next Actions",
        "deduped": "deduped",
        "source_artifacts": "Source Artifacts",
        "source_truth": "JSON / CSV remain authoritative",
        "related_reports": "Related Reports",
        "related_reports_note": "Jump quickly between the report index, readiness gate, reference-ledger, and claim-citation review surfaces.",
        "report_index": "Report index",
        "readiness_json": "Readiness JSON",
        "reference_ledger_html": "Reference ledger HTML",
        "claim_citation_html": "Claim-citation HTML",
        "artifact": "Artifact",
        "status": "Status",
        "kind": "Kind",
        "path": "Path",
        "required": "required",
        "optional": "optional",
        "present": "present",
        "missing": "missing",
        "unreadable": "unreadable",
        "no_blockers": "No blockers.",
        "no_warnings": "No warnings.",
        "no_next_actions": "No next actions.",
        "no_compact_metrics": "no compact metrics",
        "generated_from": "This page is generated from",
        "regenerate_note": ". Re-run the JSON checkers first, then regenerate this HTML page.",
        "headline_warn": "Final audit verdict: WARN",
        "headline_pass": "Final audit verdict: PASS",
        "headline_block": "Final audit verdict: BLOCK",
        "source_truth_summary": "JSON reports remain authoritative; this artifact aggregates them without rerunning checks or rewriting source files.",
    },
}


TITLE_I18N = {
    "Final cleanup": "终稿清理检查",
    "Statistical consistency": "统计表达一致性",
    "Manual anchor": "手工锚点检查",
    "Readiness gate": "readiness 门禁",
    "Citation integrity": "本地引用完整性",
    "Final reference set": "最终参考文献集",
    "External reference verification": "外部元数据核验",
    "Missing DOI candidates": "DOI 候选补全",
    "URL verification": "URL 可达性核验",
    "Hallucination risk": "幻觉风险评分",
    "Claim-citation support": "声明-引用支撑分级",
}


REASON_I18N = {
    "checker reported no findings": "checker 未发现问题",
    "checker reported review findings": "checker 报告了需复核项",
    "checker reported blocking findings": "checker 报告了阻断项",
    "required evidence missing": "缺少必需证据",
    "optional evidence missing": "缺少可选证据",
    "evidence JSON could not be read": "证据 JSON 无法读取",
    "citation integrity reported blocking issues": "本地引用完整性报告了阻断问题",
    "citation integrity reported warnings": "本地引用完整性报告了警告项",
    "citation integrity reported no blockers": "本地引用完整性未报告阻断项",
    "final reference set reported missing final bibliography entries": "最终参考文献集报告了缺失条目",
    "final reference set reported review issues": "最终参考文献集报告了需复核问题",
    "final reference set reported no blocking issues": "最终参考文献集未报告阻断问题",
    "external verification reported advisory review items": "外部元数据核验报告了 advisory 复核项",
    "external verification reported strong matches": "外部元数据核验报告了较强匹配",
    "missing DOI candidates are available for manual review": "已生成可人工核验的 DOI 候选项",
    "no missing DOI candidates reported": "未报告 DOI 候选项",
    "URL verification reported flagged URLs": "URL 可达性核验报告了标记链接",
    "URL verification reported no flagged URLs": "URL 可达性核验未报告标记链接",
    "hallucination risk reported high-risk references for manual verification": "幻觉风险评分报告了高风险条目，建议人工核验",
    "hallucination risk reported review items": "幻觉风险评分报告了需复核项",
    "hallucination risk reported no blocking findings": "幻觉风险评分未报告阻断问题",
    "claim-citation triage found orphaned citation keys": "声明-引用分级发现了孤立 citation key",
    "claim-citation triage reported review items": "声明-引用分级报告了需复核项",
    "claim-citation triage reported no blocking findings": "声明-引用分级未报告阻断问题",
    "readiness gate verdict imported": "已导入 readiness gate 结论",
    "report type is not mapped": "该报告类型尚未映射本地化说明",
    "readiness report has unknown verdict": "readiness 报告 verdict 无法识别",
    "citation integrity status is unknown": "本地引用完整性状态无法识别",
    "final reference set status is unknown": "最终参考文献集状态无法识别",
    "external verification status is unknown": "外部元数据核验状态无法识别",
    "URL verification status is unknown": "URL 可达性核验状态无法识别",
    "hallucination risk status is unknown": "幻觉风险评分状态无法识别",
    "claim-citation status is unknown": "声明-引用分级状态无法识别",
}


ACTION_PREFIX_I18N = {
    "Resolve blocking findings in ": "先解决以下维度的阻断项：",
    "Generate or repair evidence for ": "生成或修复以下维度的证据：",
    "Review remaining risk in ": "复核以下维度的剩余风险：",
}


DIMENSION_NAME_I18N = {
    "final_cleanup": "终稿清理检查",
    "statistical_consistency": "统计表达一致性",
    "manual_anchor": "手工锚点检查",
    "readiness": "readiness 门禁",
    "citation_integrity": "本地引用完整性",
    "final_reference_set": "最终参考文献集",
    "external_verification": "外部元数据核验",
    "doi_candidates": "DOI 候选补全",
    "url_verification": "URL 可达性核验",
    "hallucination_risk": "幻觉风险评分",
    "claim_citation": "声明-引用支撑分级",
}


def _load_json(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("final audit report must be a JSON object")
    return payload


def _e(value: object) -> str:
    return html.escape(str(value if value is not None else ""))


def _text(key: str, lang: str) -> str:
    return I18N[lang][key]


def _status_text(value: str, lang: str) -> str:
    mapping = {
        "present": _text("present", lang),
        "missing": _text("missing", lang),
        "unreadable": _text("unreadable", lang),
        "required": _text("required", lang),
        "optional": _text("optional", lang),
    }
    return mapping.get(value, value)


def _title_text(title: str, lang: str) -> str:
    if lang == "zh":
        return TITLE_I18N.get(title, title)
    return title


def _reason_text(reason: str, lang: str) -> str:
    if lang == "zh":
        return REASON_I18N.get(reason, reason)
    return reason


def _headline_text(headline: str, verdict: str, lang: str) -> str:
    if lang == "zh":
        mapping = {
            "Final audit verdict: WARN": _text("headline_warn", lang),
            "Final audit verdict: PASS": _text("headline_pass", lang),
            "Final audit verdict: BLOCK": _text("headline_block", lang),
        }
        return mapping.get(headline, mapping.get(f"Final audit verdict: {verdict}", headline))
    return headline


def _source_truth_text(text: str, lang: str) -> str:
    if lang == "zh" and text == "JSON reports remain authoritative; this artifact aggregates them without rerunning checks or rewriting source files.":
        return _text("source_truth_summary", lang)
    return text


def _next_action_text(action: str, lang: str) -> str:
    if lang != "zh":
        return action
    for prefix, translated in ACTION_PREFIX_I18N.items():
        if action.startswith(prefix):
            dimension = action[len(prefix):].rstrip(".")
            return translated + DIMENSION_NAME_I18N.get(dimension, dimension)
    return action


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


def _dimension_card(name: str, dimension: dict[str, object], lang: str) -> str:
    verdict = str(dimension.get("verdict", "WARN"))
    evidence_status = str(dimension.get("evidence_status", "missing"))
    title = _title_text(str(dimension.get("title", name)), lang)
    reason = _reason_text(str(dimension.get("reason", "")), lang)
    source = str(dimension.get("source", ""))
    summary = dimension.get("summary") if isinstance(dimension.get("summary"), dict) else {}
    summary_bits: list[str] = []
    for key in ("errors", "warnings", "infos", "files_scanned", "residue_findings", "mixed_families", "missing_phantomsection"):
        value = dimension.get(key, summary.get(key))
        if value not in (None, ""):
            summary_bits.append(f"{key}: {_e(value)}")
    summary_html = " / ".join(summary_bits) if summary_bits else _text("no_compact_metrics", lang)
    source_link = f'<a href="{_e(source)}">{_e(source)}</a>' if source else ""
    return f"""
      <article class="dimension verdict-{_e(verdict.lower())} evidence-{_e(evidence_status)}">
        <div class="dimension-top">
          <span class="verdict">{_e(verdict)}</span>
          <span class="evidence">{_e(_status_text(evidence_status, lang))}</span>
        </div>
        <h3>{_e(title)}</h3>
        <p>{_e(reason)}</p>
        <div class="mini">{summary_html}</div>
        <div class="source">{source_link}</div>
      </article>
"""


def _issue_card(issue: dict[str, object], lang: str) -> str:
    verdict = str(issue.get("verdict", "WARN"))
    dimension = str(issue.get("dimension", ""))
    raw_title = str(issue.get("title", dimension))
    title = _title_text(raw_title, lang)
    reason = _reason_text(str(issue.get("reason", "")), lang)
    source = str(issue.get("source", ""))
    evidence_status = str(issue.get("evidence_status", ""))
    risk_level = str(issue.get("risk_level", ""))
    source_link = f'<a href="{_e(source)}">{_e(source)}</a>' if source else ""
    risk_class = f" risk-level-{_e(risk_level.lower())}" if risk_level else ""
    return f"""
      <article class="issue verdict-{_e(verdict.lower())}{risk_class}">
        <div class="issue-code">{_e(verdict)} · {_e(_status_text(evidence_status, lang))}</div>
        <h3>{_e(title)}</h3>
        <p>{_e(reason)}</p>
        <div class="source">{source_link}</div>
      </article>
"""


def _source_row(source: dict[str, object], lang: str) -> str:
    path = str(source.get("path", ""))
    status = str(source.get("status", ""))
    required = _text("required", lang) if source.get("required") else _text("optional", lang)
    title = _title_text(str(source.get("title", source.get("id", ""))), lang)
    return f"""
      <tr>
        <td>{_e(title)}</td>
        <td><span class="pill status-{_e(status)}">{_e(_status_text(status, lang))}</span></td>
        <td>{_e(required)}</td>
        <td><a href="{_e(path)}">{_e(path)}</a></td>
      </tr>
"""


def _related_reports(lang: str) -> str:
    links = [
        ("index.html", _text("report_index", lang)),
        ("readiness-report.json", _text("readiness_json", lang)),
        (f"reference-audit-ledger.html#evidence-rows-{lang}", _text("reference_ledger_html", lang)),
        (f"claim-citation-triage.html#{lang}-review-groups", _text("claim_citation_html", lang)),
    ]
    pills = "".join(f'<a class="nav-pill" href="{_e(path)}">{_e(label)}</a>' for path, label in links)
    return f"""
      <section class="section nav-section">
        <div class="section-head"><h2>{_e(_text('related_reports', lang))}</h2><span class="meta">{_e(_text('related_reports_note', lang))}</span></div>
        <div class="nav-pills">{pills}</div>
      </section>
"""


def _render_lang_block(report: dict[str, object], lang: str) -> str:
    overall = str(report.get("overall_verdict", "WARN"))
    summary = report.get("summary") if isinstance(report.get("summary"), dict) else {}
    dimensions = report.get("dimensions") if isinstance(report.get("dimensions"), dict) else {}
    blockers = report.get("blockers") if isinstance(report.get("blockers"), list) else []
    warnings = report.get("warnings") if isinstance(report.get("warnings"), list) else []
    sources = report.get("sources") if isinstance(report.get("sources"), list) else []
    next_actions = report.get("next_actions") if isinstance(report.get("next_actions"), list) else []
    dimension_cards = "".join(
        _dimension_card(str(name), dimension, lang)
        for name, dimension in dimensions.items()
        if isinstance(dimension, dict)
    )
    blocker_cards = "".join(_issue_card(item, lang) for item in blockers if isinstance(item, dict)) or f'<p class="empty">{_e(_text("no_blockers", lang))}</p>'
    warning_cards = "".join(_issue_card(item, lang) for item in warnings if isinstance(item, dict)) or f'<p class="empty">{_e(_text("no_warnings", lang))}</p>'
    source_rows = "".join(_source_row(item, lang) for item in sources if isinstance(item, dict))
    action_items = "".join(f"<li>{_e(_next_action_text(str(item), lang))}</li>" for item in next_actions) or f'<li>{_e(_text("no_next_actions", lang))}</li>'
    source_truth = _source_truth_text(str(summary.get("source_of_truth", "")), lang)
    headline = _headline_text(str(summary.get("headline", "")), overall, lang)
    return f"""
    <section class="lang-panel" data-lang-panel="{lang}">
      <header>
        <div>
          <div class="kicker">{_e(_text('kicker', lang))}</div>
          <h1>{_text('hero_title', lang)}</h1>
          <p class="hero-copy">{_e(source_truth)}</p>
        </div>
        <aside class="verdict-panel">
          <div class="label">{_e(_text('overall_verdict', lang))}</div>
          <div class="value">{_e(overall)}</div>
          <div class="meta">{_e(headline)}</div>
        </aside>
      </header>

      <section class="kpis" aria-label="final audit kpis">
        <div class="kpi"><strong>{_e(summary.get('dimension_count', 0))}</strong><span>{_e(_text('dimensions', lang))}</span></div>
        <div class="kpi"><strong>{_e(summary.get('blocker_count', 0))}</strong><span>{_e(_text('blockers', lang))}</span></div>
        <div class="kpi"><strong>{_e(summary.get('warning_count', 0))}</strong><span>{_e(_text('warnings', lang))}</span></div>
        <div class="kpi"><strong>{_e(summary.get('missing_required_evidence_count', 0))}</strong><span>{_e(_text('missing_required', lang))}</span></div>
      </section>

      <section class="section">
        <div class="section-head"><h2>{_e(_text('dimension_matrix', lang))}</h2><span class="meta">{_e(_text('source_linked', lang))}</span></div>
        <div class="matrix">{dimension_cards}</div>
      </section>

      <section class="section">
        <div class="section-head"><h2>{_e(_text('blocking_issues', lang))}</h2><span class="meta">{_e(_text('must_resolve', lang))}</span></div>
        <div class="issue-grid">{blocker_cards}</div>
      </section>

      <section class="section" id="warning-issues-{lang}">
        <div class="section-head"><h2>{_e(_text('warning_issues', lang))}</h2><span class="meta">{_e(_text('manual_review', lang))}</span></div>
        <div class="issue-grid">{warning_cards}</div>
      </section>

      <section class="section">
        <div class="section-head"><h2>{_e(_text('next_actions', lang))}</h2><span class="meta">{_e(_text('deduped', lang))}</span></div>
        <ol>{action_items}</ol>
      </section>

      <section class="section">
        <div class="section-head"><h2>{_e(_text('source_artifacts', lang))}</h2><span class="meta">{_e(_text('source_truth', lang))}</span></div>
        <table>
          <thead><tr><th>{_e(_text('artifact', lang))}</th><th>{_e(_text('status', lang))}</th><th>{_e(_text('kind', lang))}</th><th>{_e(_text('path', lang))}</th></tr></thead>
          <tbody>{source_rows}</tbody>
        </table>
      </section>
      {_related_reports(lang)}
      <div class="raw-note">{_e(_text('generated_from', lang))} <a href="final-audit-report.json">final-audit-report.json</a>{_e(_text('regenerate_note', lang))}</div>
    </section>
"""


def render_final_audit_html(report: dict[str, object]) -> str:
    zh_block = _render_lang_block(report, "zh")
    en_block = _render_lang_block(report, "en")
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{_e(_text('title', 'zh'))}</title>
  <style>
    :root {{ --paper:#fafaf8; --ink:#0a0a0a; --grey-1:#f0f0ee; --grey-2:#d4d4d2; --grey-3:#737373; --accent:#002FA7; --accent-on:#fff; --warn:#b45309; --block:#b42318; --pass:#047857; }}
    * {{ box-sizing: border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font-family:Inter, "Helvetica Neue", Helvetica, Arial, "Noto Sans SC", sans-serif; }}
    .page {{ max-width:1280px; margin:0 auto; padding:24px 22px 56px; }}
    .lang-switch {{ display:flex; justify-content:flex-end; gap:8px; margin-bottom:14px; }}
    .lang-btn {{ border:1px solid var(--grey-2); background:#fff; color:var(--ink); padding:8px 12px; font:600 13px/1 Inter, "Helvetica Neue", Helvetica, Arial, sans-serif; cursor:pointer; }}
    .lang-btn.active {{ background:var(--accent); color:var(--accent-on); border-color:var(--accent); }}
    [data-lang-panel] {{ display:none; }}
    html[data-lang="zh"] [data-lang-panel="zh"], html[data-lang="en"] [data-lang-panel="en"] {{ display:block; }}
    header {{ display:grid; grid-template-columns:1.3fr .7fr; gap:28px; border-bottom:2px solid var(--ink); padding-bottom:28px; }}
    .kicker, .meta, .issue-code, .pill {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; letter-spacing:.12em; font-size:12px; font-weight:700; }}
    .kicker {{ color:var(--accent); }}
    h1 {{ margin:10px 0 0; font-size:clamp(54px, 11vw, 150px); line-height:.86; letter-spacing:-.075em; font-weight:200; }}
    .hero-copy {{ color:var(--grey-3); font-size:18px; line-height:1.55; max-width:760px; }}
    .verdict-panel {{ background:var(--accent); color:var(--accent-on); padding:24px; min-height:210px; display:flex; flex-direction:column; justify-content:space-between; }}
    .verdict-panel .label {{ font-size:13px; text-transform:uppercase; letter-spacing:.14em; }}
    .verdict-panel .value {{ font-size:76px; line-height:.9; font-weight:200; letter-spacing:-.06em; }}
    .kpis {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:24px 0; }}
    .kpi {{ background:#fff; border:1px solid var(--grey-2); padding:16px; }}
    .kpi strong {{ display:block; font-size:42px; font-weight:250; letter-spacing:-.04em; }}
    .kpi span {{ color:var(--grey-3); font-size:13px; }}
    .section {{ margin-top:34px; }}
    .section-head {{ display:flex; justify-content:space-between; align-items:end; gap:18px; border-bottom:1px solid var(--ink); padding-bottom:10px; margin-bottom:16px; }}
    h2 {{ margin:0; font-size:34px; font-weight:300; letter-spacing:-.04em; }}
    .matrix {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .dimension, .issue {{ background:#fff; border:1px solid var(--grey-2); padding:16px; min-height:210px; display:flex; flex-direction:column; gap:10px; }}
    .dimension-top {{ display:flex; justify-content:space-between; gap:10px; }}
    .verdict-pass .verdict {{ color:var(--pass); }} .verdict-warn .verdict {{ color:var(--warn); }} .verdict-block .verdict {{ color:var(--block); }}
    .evidence {{ color:var(--grey-3); font-family:"IBM Plex Mono", Consolas, monospace; font-size:12px; text-transform:uppercase; }}
    h3 {{ margin:0; font-size:23px; font-weight:420; letter-spacing:-.03em; }}
    p {{ margin:0; color:var(--grey-3); line-height:1.48; }}
    .mini, .source {{ color:var(--grey-3); font-size:13px; word-break:break-word; }}
    a {{ color:var(--accent); font-weight:700; text-decoration:none; }} a:hover {{ text-decoration:underline; }}
    .issue-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }}
    .empty {{ padding:18px; border:1px solid var(--grey-2); background:#fff; }}
    ol {{ margin:0; padding-left:22px; display:grid; gap:8px; color:var(--ink); }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th, td {{ border-bottom:1px solid var(--grey-2); text-align:left; padding:12px 10px; vertical-align:top; font-size:14px; }}
    th {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; letter-spacing:.1em; font-size:11px; color:var(--grey-3); }}
    .pill {{ display:inline-block; padding:4px 7px; background:var(--grey-1); }}
    .nav-pills {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .nav-pill {{ display:inline-block; padding:10px 12px; border:1px solid var(--grey-2); background:#fff; }}
    .nav-section .meta {{ text-transform:none; letter-spacing:0; font-family:Inter, "Helvetica Neue", Helvetica, Arial, sans-serif; font-size:14px; color:var(--grey-3); }}
    .status-present {{ color:var(--pass); }} .status-missing {{ color:var(--warn); }} .status-unreadable {{ color:var(--block); }}
    .raw-note {{ margin-top:24px; padding:16px; border:1px solid var(--grey-2); background:var(--grey-1); color:var(--grey-3); }}
    .skip-to-content {{ position:absolute; left:-9999px; top:auto; width:1px; height:1px; overflow:hidden; }}
    .skip-to-content:focus {{ position:static; width:auto; height:auto; padding:8px 12px; background:var(--accent); color:var(--accent-on); z-index:1000; }}
    :focus-visible {{ outline:2px solid var(--accent); outline-offset:2px; }}
    @media (max-width:920px) {{ header, .matrix, .issue-grid {{ grid-template-columns:1fr; }} .kpis {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:560px) {{ .page {{ padding:18px 14px 40px; }} .kpis {{ grid-template-columns:1fr; }} h1 {{ font-size:64px; }} .verdict-panel .value {{ font-size:56px; }} }}
  </style>
</head>
<body>
  <a class="skip-to-content" href="#main-content">Skip to content</a>
  <main class="page" id="main-content" tabindex="-1">
    {_lang_switch()}
    {zh_block}
    {en_block}
  </main>
{_lang_script()}
</body>
</html>
"""


def write_final_audit_html(report_path: str | Path, output: str | Path) -> None:
    report = _load_json(report_path)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_final_audit_html(report), encoding="utf-8")
