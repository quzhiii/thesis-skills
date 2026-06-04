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
        "final_reference_count": "最终引用文献",
        "all_bibliography_count": "全部 Bib 条目",
        "unused_bibliography_count": "未引用 Bib 条目",
        "evidence_row_count": "证据行",
        "scope_section": "按 scope 查看",
        "final_section": "最终引用文献 / Final references only",
        "final_section_hint": "默认主视图。只展示真正进入最终参考文献集或被正文引用的 key，避免模板 Bib 条目混入最终参考文献审计。",
        "all_bibliography_section": "全部 Bib 条目 / All bibliography entries",
        "all_bibliography_hint": "来自 active .bib 文件的全量条目，包含最终引用文献和未引用/模板残留候选。",
        "unused_bibliography_section": "未引用 Bib 条目 / Unused bibliography entries",
        "unused_bibliography_hint": "这些 key 在 .bib 文件中存在，但未在 TeX 正文中被引用，通常也未进入最终参考文献集。建议移除或检查 bib 文件。",
        "evidence_section": "证据行 / Evidence rows",
        "evidence_hint": "保留 final_reference_set、local_citation_integrity、hallucination_risk 等证据行；CSV 仍完整保留所有来源证据。",
        "summary_section": "摘要",
        "scope_count": "行",
        "source_truth": "CSV 仍然是 authoritative source。这个页面只帮助你按 final/all/unused/evidence 分区和 scope 摘要快速浏览。",
        "filter_note": "默认先看 Final references only；全部 Bib 条目、未引用条目和 hallucination_risk 证据放在后续 secondary sections。",
        "open_csv": "打开 CSV 源文件",
        "related_reports": "相关报告",
        "related_note": "在报告入口、readiness 门禁、终稿审计和声明-引用支撑分级之间跳转。",
        "report_index": "报告入口页",
        "readiness_json": "readiness JSON",
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
        "column_is_final_reference": "最终引用",
        "column_is_cited_in_tex": "正文引用",
        "column_is_unused_bib_entry": "未引用 Bib",
        "no_value": "—",
        "empty_rows": "当前没有此类行。",
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
        "final_reference_count": "Final references",
        "all_bibliography_count": "All bibliography entries",
        "unused_bibliography_count": "Unused bibliography entries",
        "evidence_row_count": "Evidence rows",
        "scope_section": "Browse by scope",
        "final_section": "Final references only",
        "final_section_hint": "Default primary view. Shows only keys that entered the final reference set or are cited in TeX, so template BibTeX entries do not look like final references.",
        "all_bibliography_section": "All bibliography entries",
        "all_bibliography_hint": "Full entries from active .bib files, including final references and unused/template-leftover candidates.",
        "unused_bibliography_section": "Unused bibliography entries",
        "unused_bibliography_hint": "These keys are present in .bib files but were not cited in discovered TeX files and usually did not enter the final reference set. Remove them or check the bib files.",
        "evidence_section": "Evidence rows",
        "evidence_hint": "Keeps final_reference_set, local_citation_integrity, hallucination_risk, and other evidence rows; CSV still preserves every source row.",
        "summary_section": "Summary",
        "scope_count": "rows",
        "source_truth": "CSV remains authoritative. This page only helps you browse final/all/unused/evidence sections and the scope summary.",
        "filter_note": "Start with Final references only. All bibliography entries, unused entries, and hallucination_risk evidence are kept in secondary sections below.",
        "open_csv": "Open CSV source",
        "related_reports": "Related Reports",
        "related_note": "Jump between the report index, readiness gate, final-audit detail, and claim-citation review surfaces.",
        "report_index": "Report index",
        "readiness_json": "Readiness JSON",
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
        "column_is_final_reference": "is_final_reference",
        "column_is_cited_in_tex": "is_cited_in_tex",
        "column_is_unused_bib_entry": "is_unused_bib_entry",
        "no_value": "—",
        "empty_rows": "No rows in this section.",
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
        "column_is_final_reference",
        "column_is_cited_in_tex",
        "column_is_unused_bib_entry",
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
        row.get("is_final_reference", ""),
        row.get("is_cited_in_tex", ""),
        row.get("is_unused_bib_entry", ""),
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


def _truthy(row: dict[str, str], field: str) -> bool:
    return row.get(field, "").strip().lower() in {"1", "true", "yes", "y"}


def _has_field(row: dict[str, str], field: str) -> bool:
    return field in row and row.get(field, "").strip() != ""


def _row_key(row: dict[str, str]) -> str:
    return row.get("key", "").strip()


def _is_bibliography_row(row: dict[str, str]) -> bool:
    return row.get("scope", "") == "bibliography"


def _final_reference_keys(rows: list[dict[str, str]]) -> set[str]:
    flagged = {_row_key(row) for row in rows if _row_key(row) and _truthy(row, "is_final_reference")}
    if flagged:
        return flagged
    included = {
        _row_key(row)
        for row in rows
        if _row_key(row)
        and row.get("scope", "") == "final_reference_set"
        and row.get("status", "") == "included_final"
    }
    if included:
        return included
    if any(row.get("scope", "") == "final_reference_set" for row in rows):
        return set()
    return {_row_key(row) for row in rows if _row_key(row) and _truthy(row, "is_cited_in_tex")}


def _is_final_table_row(row: dict[str, str]) -> bool:
    return _is_bibliography_row(row) or row.get("scope", "") == "final_reference_set"


def _row_sort_key(row: dict[str, str]) -> tuple[str, str]:
    return (row.get("scope", ""), _row_key(row))


def _dedupe_reference_rows(rows: list[dict[str, str]], keys: set[str]) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for key in sorted(keys):
        candidates = [row for row in rows if _row_key(row) == key and _is_final_table_row(row)]
        if not candidates:
            continue
        result.append(
            sorted(
                candidates,
                key=lambda row: (
                    0 if _is_bibliography_row(row) else 1 if row.get("scope", "") == "final_reference_set" else 2,
                    0 if row.get("title", "") else 1,
                ),
            )[0]
        )
    return result


def _status_blob(row: dict[str, str]) -> str:
    return " ".join([row.get("status", ""), row.get("issue", ""), row.get("action_suggested", "")]).lower()


def _all_bibliography_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted([row for row in rows if _is_bibliography_row(row)], key=_row_sort_key)


def _unused_bibliography_rows(rows: list[dict[str, str]], final_keys: set[str]) -> list[dict[str, str]]:
    unused_rows: list[dict[str, str]] = []
    for row in _all_bibliography_rows(rows):
        key = _row_key(row)
        blob = _status_blob(row)
        if _truthy(row, "is_unused_bib_entry") or "unused_bib_entry" in blob or "not cited in discovered tex files" in blob:
            is_unused = True
        elif _has_field(row, "is_cited_in_tex"):
            is_unused = not _truthy(row, "is_cited_in_tex") and (
                "not_in_final_reference_set" in blob
                or "not in the final reference set" in blob
                or (bool(final_keys) and key not in final_keys)
            )
        else:
            is_unused = "not_in_final_reference_set" in blob or "not in the final reference set" in blob or (bool(final_keys) and key not in final_keys)
        if is_unused:
            unused_rows.append(row)
    return unused_rows


def _evidence_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted([row for row in rows if not _is_bibliography_row(row)], key=_row_sort_key)


def _table(rows: list[dict[str, str]], lang: str) -> str:
    if not rows:
        return f"<div class=\"empty\">{html.escape(I18N[lang]['empty_rows'])}</div>"
    table_rows = "".join(_row_html(row) for row in rows)
    return f"""
        <table>
          <thead><tr>{_table_headers(lang)}</tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
"""


def _ledger_section(section_id: str, title: str, hint: str, rows: list[dict[str, str]], lang: str) -> str:
    return f"""
      <section id="{html.escape(section_id)}" class="section ledger-section">
        <div class="section-head"><h2>{html.escape(title)}</h2><span class="meta-copy">{html.escape(hint)}</span></div>
        {_table(rows, lang)}
      </section>
"""


def _related_reports(lang: str) -> str:
    links = [
        ("index.html", I18N[lang]["report_index"]),
        ("readiness-report.json", I18N[lang]["readiness_json"]),
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
    final_keys = _final_reference_keys(rows)
    all_bib_rows = _all_bibliography_rows(rows)
    unused_bib_rows = _unused_bibliography_rows(rows, final_keys)
    evidence_rows = _evidence_rows(rows)
    final_rows = _dedupe_reference_rows(rows, final_keys)
    unique_keys = len({row.get("key", "") for row in rows if row.get("key", "")})
    scopes = len({row.get("scope", "") for row in rows if row.get("scope", "")})
    statuses = len({row.get("status", "") for row in rows if row.get("status", "")})
    scope_cards = _group_cards(rows, "scope", lang)
    return f"""
    <section class="lang-panel" data-lang-panel="{lang}">
      <header>
        <div>
          <div class="kicker">{html.escape(I18N[lang]['kicker'])}</div>
          <h1>{I18N[lang]['hero_title']}</h1>
          <p class="lede">{html.escape(I18N[lang]['lede'])}</p>
        </div>
        <div class="stats">
          <div class="stat"><strong>{len(final_keys)}</strong><span>{html.escape(I18N[lang]['final_reference_count'])}</span></div>
          <div class="stat"><strong>{len(all_bib_rows)}</strong><span>{html.escape(I18N[lang]['all_bibliography_count'])}</span></div>
          <div class="stat"><strong>{len(unused_bib_rows)}</strong><span>{html.escape(I18N[lang]['unused_bibliography_count'])}</span></div>
          <div class="stat"><strong>{len(evidence_rows)}</strong><span>{html.escape(I18N[lang]['evidence_row_count'])}</span></div>
        </div>
      </header>

      <section class="notice">{html.escape(I18N[lang]['source_truth'])} {html.escape(I18N[lang]['filter_note'])} <a href="{html.escape(csv_name)}">{html.escape(I18N[lang]['open_csv'])}</a></section>

      {_ledger_section(f"final-references-{lang}", I18N[lang]['final_section'], I18N[lang]['final_section_hint'], final_rows, lang)}

      {_ledger_section(f"all-bibliography-{lang}", I18N[lang]['all_bibliography_section'], I18N[lang]['all_bibliography_hint'], all_bib_rows, lang)}

      {_ledger_section(f"unused-bibliography-{lang}", I18N[lang]['unused_bibliography_section'], I18N[lang]['unused_bibliography_hint'], unused_bib_rows, lang)}

      {_ledger_section(f"evidence-rows-{lang}", I18N[lang]['evidence_section'], I18N[lang]['evidence_hint'], evidence_rows, lang)}

      <section class="section">
        <div class="section-head"><h2>{html.escape(I18N[lang]['scope_section'])}</h2><span class="meta-copy">{len(rows)} {html.escape(I18N[lang]['rows'])} · {unique_keys} {html.escape(I18N[lang]['unique_keys'])} · {scopes} {html.escape(I18N[lang]['scopes'])} · {statuses} {html.escape(I18N[lang]['statuses'])}</span></div>
        <div class="group-grid">{scope_cards}</div>
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
    .section-head {{ border-bottom:1px solid var(--ink); padding-bottom:10px; margin-bottom:16px; display:flex; justify-content:space-between; gap:16px; align-items:end; }}
    .ledger-section {{ overflow-x:auto; }}
    h2 {{ margin:0; font-size:32px; font-weight:300; letter-spacing:-.04em; }}
    .group-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }}
    .group-card {{ background:#fff; border:1px solid var(--grey-2); padding:16px; min-height:150px; display:flex; flex-direction:column; gap:10px; }}
    .group-top {{ display:flex; justify-content:space-between; gap:10px; align-items:center; }}
    .group-key, .group-count {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; font-size:12px; letter-spacing:.1em; }}
    .group-count {{ color:var(--grey-3); }}
    .group-meta {{ color:var(--grey-3); font-size:14px; line-height:1.45; }}
    .nav-pills {{ display:flex; flex-wrap:wrap; gap:10px; }}
    .nav-pill {{ display:inline-block; padding:10px 12px; border:1px solid var(--grey-2); background:#fff; }}
    .meta-copy {{ color:var(--grey-3); font-size:14px; line-height:1.45; max-width:720px; }}
    .empty {{ background:#fff; border:1px dashed var(--grey-2); color:var(--grey-3); padding:18px; }}
    table {{ width:100%; border-collapse:collapse; background:#fff; }}
    th, td {{ border-bottom:1px solid var(--grey-2); text-align:left; padding:10px 8px; vertical-align:top; font-size:13px; }}
    th {{ font-family:"IBM Plex Mono", Consolas, monospace; text-transform:uppercase; letter-spacing:.1em; font-size:11px; color:var(--grey-3); position:sticky; top:0; background:#fff; }}
    a {{ color:var(--accent); font-weight:700; text-decoration:none; }}
    a:hover {{ text-decoration:underline; }}
    @media (max-width:980px) {{ header, .group-grid {{ grid-template-columns:1fr; }} .stats {{ grid-template-columns:repeat(2,1fr); }} .section-head {{ display:block; }} .meta-copy {{ display:block; margin-top:8px; }} }}
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
