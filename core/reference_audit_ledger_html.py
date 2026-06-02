from __future__ import annotations

import csv
import html
from collections import defaultdict
from pathlib import Path


I18N = {
    "zh": {
        "title": "引用审计总表",
        "kicker": "Thesis Skills / Reference Audit Ledger",
        "hero_title": "引用<br>审计总表",
        "lede": "这是一份面向表格交付的引用证据总表。CSV 仍然是 source of truth，HTML 只是本地阅读面。",
        "rows": "总行数",
        "unique_keys": "唯一 key",
        "scopes": "scope 数量",
        "statuses": "status 数量",
        "scope_section": "按 scope 查看",
        "key_section": "按引用 key 查看",
        "summary_section": "摘要",
        "table_section": "完整表格",
        "scope_count": "行",
        "source_truth": "CSV 仍然是 authoritative source。这个页面只帮助你按 scope / key 快速浏览。",
        "open_csv": "打开 CSV 源文件",
        "related_reports": "相关报告",
        "related_note": "在报告入口、终稿审计和声明-引用支撑分级之间跳转。",
        "report_index": "报告入口页",
        "final_audit": "终稿审计 HTML",
        "claim_citation": "声明-引用 HTML",
        "column_key": "key",
        "column_title": "标题",
        "column_authors": "作者",
        "column_year": "年份",
        "column_venue": "刊物/来源",
        "column_doi": "DOI",
        "column_scope": "scope",
        "column_source_checked": "来源证据",
        "column_status": "状态",
        "column_issue": "问题",
        "column_action": "建议动作",
        "no_value": "—",
    },
    "en": {
        "title": "Reference Audit Ledger",
        "kicker": "Thesis Skills / Reference Audit Ledger",
        "hero_title": "Reference<br>Audit Ledger",
        "lede": "This is a spreadsheet-oriented handoff ledger for reference evidence. CSV remains the source of truth; HTML is only a local reading surface.",
        "rows": "rows",
        "unique_keys": "unique keys",
        "scopes": "scopes",
        "statuses": "statuses",
        "scope_section": "Browse by scope",
        "key_section": "Browse by citation key",
        "summary_section": "Summary",
        "table_section": "Full table",
        "scope_count": "rows",
        "source_truth": "CSV remains authoritative. This page only helps you browse by scope and citation key.",
        "open_csv": "Open CSV source",
        "related_reports": "Related Reports",
        "related_note": "Jump between the report index, final-audit detail, and claim-citation review surfaces.",
        "report_index": "Report index",
        "final_audit": "Final audit HTML",
        "claim_citation": "Claim-citation HTML",
        "column_key": "key",
        "column_title": "title",
        "column_authors": "authors",
        "column_year": "year",
        "column_venue": "venue",
        "column_doi": "doi",
        "column_scope": "scope",
        "column_source_checked": "source_checked",
        "column_status": "status",
        "column_issue": "issue",
        "column_action": "action_suggested",
        "no_value": "—",
    },
}


def _e(value: object) -> str:
    return html.escape(str(value if value not in (None, "") else "—"))


def _read_csv(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def _table_headers(lang: str) -> str:
    keys = [
        "column_key",
        "column_title",
        "column_authors",
        "column_year",
        "column_venue",
        "column_doi",
        "column_scope",
        "column_source_checked",
        "column_status",
        "column_issue",
        "column_action",
    ]
    return "".join(f"<th>{html.escape(I18N[lang][key])}</th>" for key in keys)


def _row_html(row: dict[str, str]) -> str:
    ordered = [
        row.get("key", ""),
        row.get("title", ""),
        row.get("authors", ""),
        row.get("year", ""),
        row.get("venue", ""),
        row.get("doi", ""),
        row.get("scope", ""),
        row.get("source_checked", ""),
        row.get("status", ""),
        row.get("issue", ""),
        row.get("action_suggested", ""),
    ]
    return "<tr>" + "".join(f"<td>{_e(value)}</td>" for value in ordered) + "</tr>"


def _group_cards(rows: list[dict[str, str]], group_key: str, lang: str) -> str:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row.get(group_key, "")].append(row)
    cards: list[str] = []
    for key in sorted(grouped):
        if not key:
            continue
        group_rows = grouped[key]
        subtitle = html.escape(I18N[lang]["scope_count"])
        sample = group_rows[0]
        cards.append(
            f"""
      <article class="group-card">
        <div class="group-top">
          <span class="group-key">{_e(key)}</span>
          <span class="group-count">{len(group_rows)} {subtitle}</span>
        </div>
        <div class="group-meta">{_e(sample.get('title', ''))}</div>
        <div class="group-meta">{_e(sample.get('issue', ''))}</div>
      </article>
"""
        )
    return "".join(cards)


def _related_reports(lang: str) -> str:
    links = [
        ("index.html", I18N[lang]["report_index"]),
        ("final-audit-report.html", I18N[lang]["final_audit"]),
        ("claim-citation-triage.html", I18N[lang]["claim_citation"]),
    ]
    pills = "".join(f'<a class="nav-pill" href="{html.escape(path)}">{html.escape(label)}</a>' for path, label in links)
    return f"""
      <section class="section nav-section">
        <div class="section-head"><h2>{html.escape(I18N[lang]['related_reports'])}</h2><span class="meta-copy">{html.escape(I18N[lang]['related_note'])}</span></div>
        <div class="nav-pills">{pills}</div>
      </section>
"""


def _lang_block(rows: list[dict[str, str]], csv_name: str, lang: str) -> str:
    unique_keys = len({row.get("key", "") for row in rows if row.get("key", "")})
    scopes = len({row.get("scope", "") for row in rows if row.get("scope", "")})
    statuses = len({row.get("status", "") for row in rows if row.get("status", "")})
    scope_cards = _group_cards(rows, "scope", lang)
    key_cards = _group_cards(rows, "key", lang)
    table_rows = "".join(_row_html(row) for row in rows)
    return f"""
    <section class="lang-panel" data-lang-panel="{lang}">
      <header>
        <div>
          <div class="kicker">{html.escape(I18N[lang]['kicker'])}</div>
          <h1>{I18N[lang]['hero_title']}</h1>
          <p class="lede">{html.escape(I18N[lang]['lede'])}</p>
        </div>
        <div class="stats">
          <div class="stat"><strong>{len(rows)}</strong><span>{html.escape(I18N[lang]['rows'])}</span></div>
          <div class="stat"><strong>{unique_keys}</strong><span>{html.escape(I18N[lang]['unique_keys'])}</span></div>
          <div class="stat"><strong>{scopes}</strong><span>{html.escape(I18N[lang]['scopes'])}</span></div>
          <div class="stat"><strong>{statuses}</strong><span>{html.escape(I18N[lang]['statuses'])}</span></div>
        </div>
      </header>

      <section class="notice">{html.escape(I18N[lang]['source_truth'])} <a href="{html.escape(csv_name)}">{html.escape(I18N[lang]['open_csv'])}</a></section>

      <section class="section">
        <div class="section-head"><h2>{html.escape(I18N[lang]['scope_section'])}</h2></div>
        <div class="group-grid">{scope_cards}</div>
      </section>

      <section class="section">
        <div class="section-head"><h2>{html.escape(I18N[lang]['key_section'])}</h2></div>
        <div class="group-grid">{key_cards}</div>
      </section>

      <section class="section">
        <div class="section-head"><h2>{html.escape(I18N[lang]['table_section'])}</h2></div>
        <table>
          <thead><tr>{_table_headers(lang)}</tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </section>
      {_related_reports(lang)}
    </section>
"""


def render_reference_audit_ledger_html(rows: list[dict[str, str]], *, csv_name: str = "reference-audit-ledger.csv") -> str:
    zh_block = _lang_block(rows, csv_name, "zh")
    en_block = _lang_block(rows, csv_name, "en")
    return f"""<!DOCTYPE html>
<html lang="zh-CN" data-lang="zh">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(I18N['zh']['title'])}</title>
  <style>
    :root {{ --paper:#fafaf8; --ink:#0a0a0a; --grey-1:#f0f0ee; --grey-2:#d4d4d2; --grey-3:#737373; --accent:#002FA7; --accent-on:#fff; --warn:#b45309; --pass:#047857; }}
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
    .section-head {{ border-bottom:1px solid var(--ink); padding-bottom:10px; margin-bottom:16px; }}
    h2 {{ margin:0; font-size:32px; font-weight:300; letter-spacing:-.04em; }}
    .group-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .group-card {{ background:#fff; border:1px solid var(--grey-2); padding:16px; min-height:150px; display:flex; flex-direction:column; gap:10px; }}
    .group-top {{ display:flex; justify-content:space-between; gap:10px; align-items:center; }}
    .group-key, .group-count {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; font-size:12px; letter-spacing:.1em; }}
    .group-count {{ color:var(--grey-3); }}
    .group-meta {{ color:var(--grey-3); font-size:14px; line-height:1.45; }}
    .nav-pills {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .nav-pill {{ display:inline-block; padding:10px 12px; border:1px solid var(--grey-2); background:#fff; }}
    .meta-copy {{ color:var(--grey-3); font-size:14px; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th, td {{ border-bottom:1px solid var(--grey-2); text-align:left; padding:10px 8px; vertical-align:top; font-size:13px; }}
    th {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; letter-spacing:.1em; font-size:11px; color:var(--grey-3); position:sticky; top:0; background:#fff; }}
    a {{ color:var(--accent); font-weight:700; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:980px) {{ header, .group-grid {{ grid-template-columns:1fr; }} .stats {{ grid-template-columns:repeat(2,1fr); }} }}
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


def write_reference_audit_ledger_html(csv_path: str | Path, output: str | Path) -> None:
    rows = _read_csv(csv_path)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_reference_audit_ledger_html(rows, csv_name=Path(csv_path).name), encoding="utf-8")
