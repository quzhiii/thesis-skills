from __future__ import annotations

import html
import json
from collections import defaultdict
from pathlib import Path


I18N = {
    "zh": {
        "lang": "zh-CN",
        "title": "声明-引用支撑分级",
        "kicker": "Thesis Skills / Claim-Citation Review",
        "hero_title": "声明-引用<br>支撑分级",
        "lede": "这是一个基于 claim-citation triage JSON 的本地阅读面。JSON 仍然是 source of truth，HTML 只帮助人工复核。",
        "status": "总体状态",
        "pairs": "引用对",
        "citation_needed": "待补引用",
        "uncited_refs": "未被引用参考文献",
        "summary": "摘要",
        "triage_groups": "按 triage_label 查看",
        "citation_needed_section": "Citation-needed 候选句",
        "uncited_section": "未被引用参考文献",
        "entries_section": "详细条目",
        "source_truth": "JSON / Markdown / CSV 仍然是 authoritative source。这个页面只帮助你按 triage、cluster 和风险信号快速浏览。",
        "open_json": "打开 JSON 源文件",
        "open_md": "打开 Markdown 源文件",
        "open_csv": "打开 CSV 源文件",
        "related_reports": "相关报告",
        "related_note": "在报告入口、终稿审计和引用审计台账之间跳转。",
        "report_index": "报告入口页",
        "final_audit": "终稿审计 HTML",
        "reference_ledger": "引用审计 HTML",
        "claim_type": "claim 类型",
        "review_label": "复核标签",
        "risk_signals": "风险信号",
        "support_signals": "支撑信号",
        "next_actions": "下一步动作",
        "cluster": "引用簇",
        "cluster_reason": "簇级说明",
        "context": "claim 上下文",
        "file": "文件",
        "line": "行号",
        "risk": "风险",
        "reason": "原因",
        "sentence": "句子",
        "key": "citation key",
        "headline": "状态概览",
        "no_entries": "当前没有该分组条目。",
        "no_candidates": "当前没有 citation-needed 候选句。",
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
        "triage_groups": "Browse by triage label",
        "citation_needed_section": "Citation-Needed Candidates",
        "uncited_section": "Uncited References",
        "entries_section": "Detailed entries",
        "source_truth": "JSON / Markdown / CSV remain authoritative. This page only helps you browse by triage label, cluster, and risk signals.",
        "open_json": "Open JSON source",
        "open_md": "Open Markdown source",
        "open_csv": "Open CSV source",
        "related_reports": "Related Reports",
        "related_note": "Jump between the report index, final-audit detail, and reference-ledger review surfaces.",
        "report_index": "Report index",
        "final_audit": "Final audit HTML",
        "reference_ledger": "Reference ledger HTML",
        "claim_type": "claim type",
        "review_label": "review label",
        "risk_signals": "risk signals",
        "support_signals": "support signals",
        "next_actions": "next actions",
        "cluster": "cluster",
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


def _load_json(path: str | Path) -> dict[str, object]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("claim-citation report must be a JSON object")
    return payload


def _e(value: object, lang: str = "en") -> str:
    fallback = I18N[lang]["no_value"]
    return html.escape(str(value if value not in (None, "", []) else fallback))


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
    return "<ul>" + "".join(f"<li>{_e(item, lang)}</li>" for item in values) + "</ul>"


def _summary_rows(summary: dict[str, object], lang: str) -> str:
    rows = []
    for key in sorted(summary):
        rows.append(f"<tr><th>{_e(key, lang)}</th><td>{_e(summary[key], lang)}</td></tr>")
    return "".join(rows)


def _entry_card(entry: dict[str, object], lang: str) -> str:
    cluster_keys = entry.get("cluster_keys")
    cluster_html = ", ".join(_e(item, lang) for item in cluster_keys) if isinstance(cluster_keys, list) and cluster_keys else _e("", lang)
    return f"""
      <article class="entry-card status-{_e(entry.get('triage_label', ''), lang).lower()}">
        <div class="entry-top">
          <span class="pill">{_e(entry.get('triage_label', ''), lang)}</span>
          <span class="pill muted">{_e(entry.get('support_review_label', ''), lang)}</span>
        </div>
        <h3>{_e(entry.get('citation_key', ''), lang)}</h3>
        <p class="meta">{_e(I18N[lang]['file'], lang)}: {_e(entry.get('file', ''), lang)} · {_e(I18N[lang]['line'], lang)}: {_e(entry.get('line', ''), lang)}</p>
        <p>{_e(entry.get('support_review_reason', ''), lang)}</p>
        <div class="detail"><strong>{_e(I18N[lang]['claim_type'], lang)}</strong><span>{_e(entry.get('claim_type', ''), lang)}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['risk'], lang)}</strong><span>{_e(entry.get('hallucination_risk_label', ''), lang)}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['cluster'], lang)}</strong><span>{cluster_html}</span></div>
        <div class="detail"><strong>{_e(I18N[lang]['cluster_reason'], lang)}</strong><span>{_e(entry.get('cluster_review_reason', ''), lang)}</span></div>
        <div class="detail-block"><strong>{_e(I18N[lang]['risk_signals'], lang)}</strong>{_list_html(entry.get('risk_signals'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['support_signals'], lang)}</strong>{_list_html(entry.get('support_signals'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['next_actions'], lang)}</strong>{_list_html(entry.get('next_actions'), lang)}</div>
        <div class="detail-block"><strong>{_e(I18N[lang]['context'], lang)}</strong><blockquote>{_e(entry.get('claim_context', ''), lang)}</blockquote></div>
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
      <section class="section">
        <div class="section-head"><h2>{_e(label, lang)}</h2><span class="meta">{len(group)}</span></div>
        <div class="entry-grid">{cards}</div>
      </section>
"""
        )
    return "".join(blocks)


def _candidate_rows(candidates: list[dict[str, object]], lang: str) -> str:
    if not candidates:
        return f"<div class=\"empty\">{_e(I18N[lang]['no_candidates'], lang)}</div>"
    rows = []
    for item in sorted(candidates, key=lambda e: (str(e.get("file", "")), int(e.get("line") or 0))):
        rows.append(
            f"<tr><td>{_e(item.get('file', ''), lang)}:{_e(item.get('line', ''), lang)}</td><td>{_e(item.get('claim_type', ''), lang)}</td><td>{_e(item.get('risk_signal', ''), lang)}</td><td>{_e(item.get('sentence', ''), lang)}</td></tr>"
        )
    return f"<table><thead><tr><th>{_e(I18N[lang]['file'], lang)}</th><th>{_e(I18N[lang]['claim_type'], lang)}</th><th>{_e(I18N[lang]['risk_signals'], lang)}</th><th>{_e(I18N[lang]['sentence'], lang)}</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"


def _uncited_rows(rows: list[dict[str, object]], lang: str) -> str:
    if not rows:
        return f"<div class=\"empty\">{_e(I18N[lang]['no_uncited'], lang)}</div>"
    body = []
    for item in rows:
        body.append(f"<tr><td>{_e(item.get('citation_key', ''), lang)}</td><td>{_e(item.get('title', ''), lang)}</td><td>{_e(item.get('hallucination_risk_label', ''), lang)}</td></tr>")
    return f"<table><thead><tr><th>{_e(I18N[lang]['key'], lang)}</th><th>{_e('title', lang)}</th><th>{_e(I18N[lang]['risk'], lang)}</th></tr></thead><tbody>{''.join(body)}</tbody></table>"


def _related_reports(lang: str) -> str:
    links = [
        ("index.html", I18N[lang]["report_index"]),
        ("final-audit-report.html", I18N[lang]["final_audit"]),
        ("reference-audit-ledger.html", I18N[lang]["reference_ledger"]),
    ]
    pills = "".join(f'<a class="nav-pill" href="{html.escape(path)}">{html.escape(label)}</a>' for path, label in links)
    return f"""
      <section class="section nav-section">
        <div class="section-head"><h2>{_e(I18N[lang]['related_reports'], lang)}</h2><span class="meta-copy">{_e(I18N[lang]['related_note'], lang)}</span></div>
        <div class="nav-pills">{pills}</div>
      </section>
"""


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
          <div class="stat"><strong>{_e(report.get('status', ''), lang)}</strong><span>{_e(I18N[lang]['status'], lang)}</span></div>
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
        <div class="section-head"><h2>{_e(I18N[lang]['citation_needed_section'], lang)}</h2></div>
        {_candidate_rows(citation_needed, lang)}
      </section>
      <section class="section">
        <div class="section-head"><h2>{_e(I18N[lang]['uncited_section'], lang)}</h2></div>
        {_uncited_rows(uncited, lang)}
      </section>
      <section class="section">
        <div class="section-head"><h2>{_e(I18N[lang]['triage_groups'], lang)}</h2></div>
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
    @media (max-width:980px) {{ header, .entry-grid {{ grid-template-columns:1fr; }} .stats {{ grid-template-columns:repeat(2,1fr); }} }}
    @media (max-width:560px) {{ .stats {{ grid-template-columns:1fr; }} .page {{ padding:18px 14px 40px; }} }}
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
