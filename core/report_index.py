from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path


I18N = {
    "zh": {
        "lang": "zh-CN",
        "page_title": "Thesis Skills 报告入口",
        "kicker": "Thesis Skills / Report Index",
        "hero_title": "本地<br>报告入口",
        "lede_suffix": "。这个静态 HTML 页面只用于阅读和跳转，原始 JSON / CSV 仍然是 source of truth。",
        "present": "已生成",
        "missing": "缺失",
        "unreadable": "不可读取",
        "notice": "JSON / CSV 仍然是 source of truth。这个页面只是本地阅读入口，适合导师、实验室或服务交付时浏览。",
        "open_source": "打开源产物",
        "generate_first": "请先生成这个产物",
        "rows": "行数",
        "path": "路径",
        "summary": "摘要",
        "no_summary": "暂无摘要",
        "json_source": "JSON source",
        "csv_source": "CSV source",
    },
    "en": {
        "lang": "en",
        "page_title": "Thesis Skills Report Index",
        "kicker": "Thesis Skills / Report Index",
        "hero_title": "Local<br>Report Index",
        "lede_suffix": ". This static HTML page links to the raw JSON and CSV source-of-truth artifacts. It does not replace the machine-readable reports.",
        "present": "present",
        "missing": "missing",
        "unreadable": "unreadable",
        "notice": "Source of truth remains JSON / CSV. This page is a local reading surface for advisor, lab, or service handoff.",
        "open_source": "Open source artifact",
        "generate_first": "Generate this artifact first",
        "rows": "rows",
        "path": "path",
        "summary": "summary",
        "no_summary": "No summary available",
        "json_source": "JSON source",
        "csv_source": "CSV source",
    },
}


@dataclass(frozen=True)
class ReportArtifactSpec:
    id: str
    title: str
    title_zh: str
    path: str
    role: str
    role_zh: str
    description: str
    description_zh: str


REPORT_ARTIFACTS: tuple[ReportArtifactSpec, ...] = (
    ReportArtifactSpec("final_audit", "Final audit report", "终稿审计总报告", "final-audit-report.json", "JSON source", "JSON 源产物", "Aggregated final-audit dimensions, blockers, warnings, and source links.", "聚合终稿审计维度、阻断项、警告项和 source links。"),
    ReportArtifactSpec("final_cleanup", "Final cleanup", "终稿清理检查", "final-cleanup-report.json", "JSON source", "JSON 源产物", "Process-residue scan for TODO/FIXME/blue markers/draft/debug traces.", "扫描 TODO/FIXME/蓝字/draft/debug 等过程残留。"),
    ReportArtifactSpec("statistical_consistency", "Statistical consistency", "统计表达一致性", "statistical-consistency-report.json", "JSON source", "JSON 源产物", "Dominant-style and deviation evidence for statistical notation families.", "统计表达主流写法与偏离项证据。"),
    ReportArtifactSpec("manual_anchor", "Manual anchor", "手工锚点检查", "manual-anchor-report.json", "JSON source", "JSON 源产物", "Manual addcontentsline / phantomsection hyperlink-jump evidence.", "手工 addcontentsline / phantomsection 跳转风险证据。"),
    ReportArtifactSpec("reference_ledger", "Reference audit ledger", "引用审计总表", "reference-audit-ledger.csv", "CSV source", "CSV 源产物", "Spreadsheet handoff across local and advisory reference evidence.", "面向表格交付的引用证据总表。"),
    ReportArtifactSpec("readiness", "Readiness gate", "readiness 门禁", "readiness-report.json", "JSON source", "JSON 源产物", "PASS/WARN/BLOCK readiness summary when available.", "如果存在，则展示 PASS/WARN/BLOCK readiness 汇总。"),
    ReportArtifactSpec("citation_integrity", "Citation integrity", "本地引用完整性", "citation-integrity-report.json", "JSON source", "JSON 源产物", "Local citation and bibliography integrity evidence.", "本地 citation 和 bibliography 完整性证据。"),
    ReportArtifactSpec("final_reference_set", "Final reference set", "最终参考文献集", "final-reference-set-report.json", "JSON source", "JSON 源产物", "Final cited/reference-set scope evidence.", "最终被引用/进入参考文献集范围的证据。"),
    ReportArtifactSpec("external_verification", "External verification", "外部元数据核验", "external-verification-report.json", "JSON source", "JSON 源产物", "CrossRef/OpenAlex/Semantic Scholar advisory evidence.", "CrossRef/OpenAlex/Semantic Scholar advisory evidence。"),
    ReportArtifactSpec("doi_candidates", "DOI candidates", "DOI 候选补全", "missing-doi-candidates.json", "JSON source", "JSON 源产物", "Advisory candidate DOI suggestions.", "建议性的 DOI 候选补全。"),
    ReportArtifactSpec("url_verification", "URL verification", "URL 可达性核验", "url-verification-report.json", "JSON source", "JSON 源产物", "URL reachability evidence, not authenticity proof.", "URL 可达性证据，不代表真实性判断。"),
    ReportArtifactSpec("hallucination_risk", "Hallucination risk", "幻觉风险评分", "hallucination-risk-report.json", "JSON source", "JSON 源产物", "Reference hallucination-risk scoring evidence.", "参考文献幻觉风险评分证据。"),
    ReportArtifactSpec("claim_citation", "Claim-citation support", "声明-引用支撑分级", "claim-citation-triage-report.json", "JSON source", "JSON 源产物", "Claim-citation structural support triage evidence.", "声明-引用结构性支撑分级证据。"),
)

HTML_DETAILS = {
    "final_audit": "final-audit-report.html",
    "reference_ledger": "reference-audit-ledger.html",
    "claim_citation": "claim-citation-triage.html",
}


def _load_json(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _csv_row_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _row in csv.DictReader(handle))


def _artifact_status(path: Path) -> str:
    if not path.exists():
        return "missing"
    if path.suffix == ".json" and _load_json(path) is None:
        return "unreadable"
    return "present"


def _json_summary(payload: dict[str, object] | None) -> dict[str, object]:
    if not payload:
        return {}
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return summary
    result: dict[str, object] = {}
    for key in ("status", "overall_verdict", "module"):
        if key in payload:
            result[key] = payload[key]
    return result


def collect_report_index_items(reports_dir: str | Path) -> list[dict[str, object]]:
    root = Path(reports_dir)
    items: list[dict[str, object]] = []
    for spec in REPORT_ARTIFACTS:
        path = root / spec.path
        status = _artifact_status(path)
        payload = _load_json(path) if path.suffix == ".json" else None
        item: dict[str, object] = {
            "id": spec.id,
            "title": spec.title,
            "title_zh": spec.title_zh,
            "path": spec.path,
            "role": spec.role,
            "role_zh": spec.role_zh,
            "description": spec.description,
            "description_zh": spec.description_zh,
            "status": status,
            "summary": _json_summary(payload),
        }
        if spec.id in HTML_DETAILS:
            item["detail_path"] = HTML_DETAILS[spec.id]
        if path.suffix == ".csv" and status == "present":
            item["row_count"] = _csv_row_count(path)
        items.append(item)
    return items


def _summary_value(summary: dict[str, object], *keys: str) -> str:
    for key in keys:
        value = summary.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


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


def _card(item: dict[str, object], lang: str) -> str:
    status = str(item.get("status", "missing"))
    summary = item.get("summary") if isinstance(item.get("summary"), dict) else {}
    summary_text = _summary_value(summary, "headline", "status", "overall_verdict", "checker", "module")
    row_count = item.get("row_count")
    row_text = f'<div class="meta">{html.escape(I18N[lang]["rows"])}: {html.escape(str(row_count))}</div>' if row_count is not None else ""
    link = html.escape(str(item.get("path", "")))
    detail_link = str(item.get("detail_path") or HTML_DETAILS.get(str(item.get("id", "")), ""))
    title = html.escape(str(item.get("title_zh" if lang == "zh" else "title", "")))
    role = html.escape(str(item.get("role_zh" if lang == "zh" else "role", "")))
    description = html.escape(str(item.get("description_zh" if lang == "zh" else "description", "")))
    status_text = html.escape(I18N[lang].get(status, status))
    summary_html = html.escape(summary_text) if summary_text else I18N[lang]["no_summary"]
    if status == "present":
        if detail_link:
            detail_html = html.escape(detail_link)
            action = f'<a href="{detail_html}">{html.escape(I18N[lang]["open_source"])} HTML</a> · <a href="{link}">{html.escape(I18N[lang]["open_source"])} JSON/CSV</a>'
        else:
            action = f'<a href="{link}">{html.escape(I18N[lang]["open_source"])}</a>'
    else:
        action = f'<span>{html.escape(I18N[lang]["generate_first"])}</span>'
    return f"""
      <article class="card status-{html.escape(status)}">
        <div class="card-top">
          <span class="status">{status_text}</span>
          <span class="role">{role}</span>
        </div>
        <h2>{title}</h2>
        <p>{description}</p>
        <div class="meta">{html.escape(I18N[lang]['path'])}: <code>{link}</code></div>
        <div class="meta">{html.escape(I18N[lang]['summary'])}: {summary_html}</div>
        {row_text}
        <div class="card-action">{action}</div>
      </article>
"""


def _lang_block(items: list[dict[str, object]], project_label: str, lang: str) -> str:
    present_count = sum(1 for item in items if item.get("status") == "present")
    missing_count = sum(1 for item in items if item.get("status") == "missing")
    unreadable_count = sum(1 for item in items if item.get("status") == "unreadable")
    cards = "".join(_card(item, lang) for item in items)
    label = html.escape(project_label)
    return f"""
    <section class="lang-panel" data-lang-panel="{lang}">
      <header>
        <div>
          <div class="kicker">{html.escape(I18N[lang]['kicker'])}</div>
          <h1>{I18N[lang]['hero_title']}</h1>
          <p class="lede">{label}{html.escape(I18N[lang]['lede_suffix'])}</p>
        </div>
        <div class="stats">
          <div class="stat"><strong>{present_count}</strong><span>{html.escape(I18N[lang]['present'])}</span></div>
          <div class="stat"><strong>{missing_count}</strong><span>{html.escape(I18N[lang]['missing'])}</span></div>
          <div class="stat"><strong>{unreadable_count}</strong><span>{html.escape(I18N[lang]['unreadable'])}</span></div>
        </div>
      </header>
      <section class="notice">{html.escape(I18N[lang]['notice'])}</section>
      <section class="grid" aria-label="Report artifacts">{cards}</section>
    </section>
"""


def render_report_index_html(items: list[dict[str, object]], *, project_label: str = "Local thesis project") -> str:
    zh_block = _lang_block(items, project_label, "zh")
    en_block = _lang_block(items, project_label, "en")
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(I18N['zh']['page_title'])}</title>
  <style>
    :root {{ color-scheme: light; --ink:#111827; --muted:#667085; --line:#d0d5dd; --paper:#f8fafc; --card:#ffffff; --blue:#1d4ed8; --green:#047857; --orange:#b45309; --red:#b42318; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", sans-serif; color: var(--ink); background: var(--paper); }}
    .page {{ max-width: 1180px; margin: 0 auto; padding: 24px 20px 48px; }}
    .lang-switch {{ display:flex; justify-content:flex-end; gap:8px; margin-bottom:14px; }}
    .lang-btn {{ border:1px solid var(--line); background:#fff; color:var(--ink); padding:8px 12px; font:600 13px/1 Inter, "Segoe UI", sans-serif; cursor:pointer; }}
    .lang-btn.active {{ background:var(--blue); color:#fff; border-color:var(--blue); }}
    [data-lang-panel] {{ display:none; }}
    html[data-lang="zh"] [data-lang-panel="zh"], html[data-lang="en"] [data-lang-panel="en"] {{ display:block; }}
    header {{ display: grid; grid-template-columns: 1.5fr 1fr; gap: 24px; align-items: end; border-bottom: 2px solid var(--ink); padding-bottom: 24px; }}
    .kicker {{ text-transform: uppercase; letter-spacing: .16em; font-size: 12px; font-weight: 800; color: var(--blue); }}
    h1 {{ font-size: clamp(40px, 8vw, 88px); line-height: .9; letter-spacing: -.06em; margin: 12px 0; font-weight:200; }}
    .lede {{ font-size: 18px; color: var(--muted); max-width: 720px; }}
    .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }}
    .stat {{ background: var(--card); border: 1px solid var(--line); padding: 14px; }}
    .stat strong {{ display: block; font-size: 28px; font-weight:250; }}
    .stat span {{ color: var(--muted); font-size: 13px; }}
    .notice {{ margin: 24px 0; border: 1px solid var(--line); background: #fff7ed; padding: 16px; color: #7c2d12; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 24px; }}
    .card {{ background: var(--card); border: 1px solid var(--line); padding: 18px; min-height: 260px; display: flex; flex-direction: column; gap: 10px; }}
    .card-top {{ display: flex; justify-content: space-between; gap: 10px; align-items: center; }}
    .status, .role {{ font-size: 12px; font-weight: 800; text-transform: uppercase; letter-spacing: .08em; }}
    .status-present .status {{ color: var(--green); }}
    .status-missing .status {{ color: var(--orange); }}
    .status-unreadable .status {{ color: var(--red); }}
    .role {{ color: var(--muted); }}
    h2 {{ margin: 4px 0 0; font-size: 24px; letter-spacing: -.03em; font-weight:420; }}
    p {{ margin: 0; color: var(--muted); line-height: 1.5; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: .92em; }}
    .meta {{ color: var(--muted); font-size: 13px; word-break: break-word; }}
    .card-action {{ margin-top: auto; padding-top: 12px; border-top: 1px solid var(--line); }}
    a {{ color: var(--blue); font-weight: 700; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    @media (max-width: 860px) {{ header, .grid {{ grid-template-columns: 1fr; }} .stats {{ grid-template-columns: repeat(3, 1fr); }} }}
    @media (max-width: 560px) {{ .stats {{ grid-template-columns: 1fr; }} .page {{ padding: 20px 14px 36px; }} }}
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


def write_report_index_html(reports_dir: str | Path, output: str | Path, *, project_label: str = "Local thesis project") -> None:
    items = collect_report_index_items(reports_dir)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_report_index_html(items, project_label=project_label), encoding="utf-8")
