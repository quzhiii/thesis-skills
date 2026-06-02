# Thesis Skills v3.3.0

<div align="center">

**用于引用同步、格式检查、审阅交接和提交前 readiness 检查的确定性论文工作流工具。**

把时间花在思考上，而不是反复修格式。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** · [English](README.md) · [展示页面](https://quzhiii.github.io/thesis-skills)

[v3.3.0 亮点](#v330-有哪些更新) · [快速开始](#快速开始) · [输出](#输出) · [使用场景](#使用场景) · [如何同步后续更新](#如何同步后续更新) · [规则包](#规则包) · [创建自己的规则包](#创建你自己的学校规则包) · [边界](#边界)

</div>

---

## 这是什么？

Thesis Skills **不是** AI 写作助手，**不是**论文模板，也**不会**替你生成论文正文。

它是一个**命令行工作流系统**，用来连接很多研究生和科研作者已经在使用的工具：Word、Zotero、EndNote、LaTeX、结构化检查报告、安全修复补丁、审阅交接材料，以及提交前 readiness 检查。

```text
                  ┌───────────────────────────────────────────┐
Zotero / EndNote ─┤                                           ├─→ LaTeX 论文
Word .docx ───────┤              Thesis Skills                ├─→ 审阅用 Word 导出
LaTeX 项目 ───────┤                                           ├─→ 答辩准备材料
                  └───────────────────────────────────────────┘
                                      │
                                      ▼
                 检查报告 → dry-run 修复 → readiness gate
```

目标很简单：把分散、手工、容易出错的论文后期工作，变成一个**可检查、可复现、可审计**的流程。

对重复性后期工作来说，节省时间是具体可感知的：

| 工作流 | 手工基线 | 使用 Thesis Skills | 提速 |
|---|---:|---:|---:|
| 文献接入 | 30-60 分钟 | 2-5 分钟 | **约 10 倍** |
| Word ↔ LaTeX 审阅交接 | 1-3 小时 | 5-10 分钟 | **约 15 倍** |
| 确定性格式检查 | 1-3 小时 | 2-5 分钟 | **约 20 倍** |
| 基于报告的安全修复 | 1-2 小时 | 5-10 分钟 | **约 10 倍** |
| 提交前 readiness 复核 | 30-60 分钟 | 1-2 分钟 | **约 30 倍** |
| 答辩前清单整理 | 2-4 小时 | 10-15 分钟 | **约 15 倍** |

> 时间节省是对重复性格式和交接工作的保守估算。Thesis Skills 不替代写作、思考、导师判断或学校/期刊规则的最终人工确认。

---

## v3.3.0 有哪些更新

- **Readiness Gate 集成** 的四层引用证据流水线继续保留，依然可以一键跑完四层引用证据流水线；V3.3 在其上新增 final reference set、DOI 候选和 URL 验证。
- **引用验证加固**：新增 `.aux` / `.bbl` final reference set 解析，能区分“最终编译进参考文献表的条目”和“只是 bib 里存在但没有进入最终文档的条目”。
- 新增报告：`reports/final-reference-set-report.json`、`reports/final-reference-set-report.csv`、`reports/missing-doi-candidates.json`、`reports/missing-doi-candidates.csv`、`reports/url-verification-report.json`、`reports/url-verification-flagged.csv`。
- `18-verify-references/verify_external_references.py` 新增 `--scope final|cited|all`、`--resume`、`--only-key`，并支持 crash-safe partial report 写入。
- 外部验证 mismatch taxonomy 扩展到 DOI、标题、subtitle、作者人数/顺序、年份、venue、volume/issue/pages。
- `run_evidence_pipeline.py` 现在线性执行 final reference set → 外部验证 → 幻觉风险 → 声明-引用分级。

---

## 快速开始

先用内置最小示例跑一遍检查流水线：

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

test -d examples/minimal-latex-project

python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

预期结果：`examples/minimal-latex-project/reports/` 下会生成 JSON 报告，包括 `run-summary.json` 和 `readiness-report.json`，并且不需要本机安装 LaTeX。

如果你已经有自己的 LaTeX 论文项目：

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

更多说明见 [`docs/quickstart.md`](docs/quickstart.md)。

---

## 输出

### 核心工作流

```text
1. 接入          2. 检查            3. 安全修复          4. 放行判断      5. 交接
──────────       ───────────        ─────────────        ─────────       ─────────────
Zotero           引用完整性         预览补丁             通过            导师审阅 Word
EndNote     →    语言规则      →    dry-run 优先   →     警告      →     审阅 TODO
Word/LaTeX       格式结构           显式确认修改         阻断            答辩准备材料
```

### Readiness gate 预览

```text
┌──────────────────────────────────────────────────────────────┐
│ Readiness verdict: WARN（存在警告）                           │
├───────────────────────┬────────┬─────────────────────────────┤
│ 检查维度              │ 状态   │ 含义                        │
├───────────────────────┼────────┼─────────────────────────────┤
│ 引用                  │ PASS   │ 引用 key 全部可解析         │
│ 语言                  │ WARN   │ 仍有 2 条风格警告           │
│ 格式                  │ PASS   │ 标签和交叉引用稳定          │
│ 编译证据              │ WARN   │ demo 模式跳过编译           │
│ Word 导出证据         │ WARN   │ smoke test 不生成该产物     │
│ 审阅闭环证据          │ WARN   │ smoke test 不生成该产物     │
└───────────────────────┴────────┴─────────────────────────────┘

下一步：
1. 查看 reports/check_language-report.json
2. 需要导师审阅交接时，再生成 Word 导出和 review-loop 产物
3. 最终提交前，去掉 --skip-compile 重新运行
```

基础的 `run_check_once.py` 命令会生成这些机器可读 artifacts：

- `reports/check_bib_quality-report.json`
- `reports/check_references-report.json`
- `reports/citation-integrity-report.json`
- `reports/citation-integrity-report.md`
- `reports/citation-issues.csv`
- `reports/check_language-report.json`
- `reports/check_language_deep-report.json`
- `reports/check_format-report.json`
- `reports/check_content-report.json`
- `reports/readiness-report.json`
- `reports/run-summary.json`

可选的 final-audit foundation artifact：

- `reports/final-cleanup-report.json`，由 `23-check-final-cleanup/check_final_cleanup.py` 生成
- `reports/statistical-consistency-report.json`，由 `25-check-statistical-consistency/check_statistical_consistency.py` 生成
- `reports/manual-anchor-report.json`，由 `26-check-manual-anchor/check_manual_anchor.py` 生成
- `reports/final-audit-report.json`，由 `27-final-audit-report/build_final_audit_report.py` 生成
- `reports/reference-audit-ledger.csv`，由 `28-reference-audit-ledger/build_reference_audit_ledger.py` 生成
- `reports/index.html`，由 `29-report-index/build_report_index.py` 生成
- `reports/final-audit-report.html`，由 `30-final-audit-html/build_final_audit_html.py` 生成
- `reports/reference-audit-ledger.html`，由 `31-reference-ledger-html/build_reference_audit_ledger_html.py` 生成

可选的 v3.3 evidence pipeline 会生成这些引用证据 artifacts：

- `reports/final-reference-set-report.json`
- `reports/final-reference-set-report.csv`
- `reports/external-verification-report.json`（未跳过外部验证时）
- `reports/missing-doi-candidates.json`（未跳过外部验证时）
- `reports/missing-doi-candidates.csv`（未跳过外部验证时）
- `reports/url-verification-report.json`（未跳过外部验证时）
- `reports/url-verification-flagged.csv`（未跳过外部验证时）
- `reports/hallucination-risk-report.json`
- `reports/high-risk-references.csv`
- `reports/claim-citation-triage-report.json`
- `reports/claim-citation-triage.md`
- `reports/claim-citation-triage.csv`

输出示例和演示流程见 [`docs/examples.md`](docs/examples.md)。

### Citation Integrity 预览

当前 `v3.3.0` 版本线把本地优先的 Citation Integrity 作为提交前引用检查的第一层：

```text
References: BLOCK
- 文中引用 key 在 bibliography 文件中缺失
- 重复 citation key 且 metadata 冲突
- DOI/year 字段警告
- 本地编译日志中的 undefined citation 警告
```

边界：当前 Citation Integrity 只检查本地引用完整性，不会联网查询外部数据库，也不会自动插入或重写参考文献。外部验证、幻觉风险评分和声明-引用支撑分级是后续独立证据层。

### 外部引用验证（v2.0.0）

可选的外部元数据验证层，对每条参考文献查询 **CrossRef**、**OpenAlex** 和 **Semantic Scholar**，输出 `reports/external-verification-report.json`。

适合在你想快速筛查 AI 生成、来源不明、或看起来可疑的参考文献时使用，作为人工终审前的一层真实性检查。

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic
```

或通过现有引用检查器加显式标志：

```bash
python 10-check-references/check_references.py \
  --project-root thesis \
  --ruleset university-generic \
  --with-external-verification
```

V2.0 边界：

- 数据源：CrossRef、OpenAlex、Semantic Scholar。
- 不影响 readiness gate 里本地 `references` 的 blocking 逻辑。
- `external_verification` 只是 advisory 维度。
- 暂不包含幻觉风险评分。
- 不自动改写引用。
- 适合做“可疑引用 / AI 幻觉引用”的快速筛查，但不是最终造假判定。
- 网络故障降级为 `UNAVAILABLE`，不会崩溃。

### Final Reference Set + DOI / URL 检查（v3.3.0）

V3.3 把引用验证范围拆成三层：

- `final`：真正进入最终编译参考文献表的 key（来自 `.aux` / `.bbl`）
- `cited`：TeX 源码里 `\cite{}` 出现过的 key
- `all`：活动 `.bib` 文件里的全部条目

final reference set 步骤会写出：

- `reports/final-reference-set-report.json`
- `reports/final-reference-set-report.csv`

外部验证现在支持长项目断点续跑：

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic \
  --scope final \
  --resume
```

V3.3 还新增两类 advisory 报告：

- `reports/missing-doi-candidates.json` / `.csv`：缺 DOI 条目的候选 DOI 建议
- `reports/url-verification-report.json` / `reports/url-verification-flagged.csv`：URL 可达性检查

边界：

- 不使用 LLM。
- 不自动把 DOI 写回 `.bib`。
- 不自动替换 URL。
- URL 检查只判断链接是否能解析，不判断文档真伪。

## 使用场景

### 1. 我刚从 Word 转到 LaTeX

```bash
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

### 2. 我已经在用 LaTeX，只想检查论文

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic

python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset university-generic \
  --mode advisor-handoff
```

### 3. 导师需要 Word 版本审稿

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply true
```

### 4. 我收到 Word 反馈，需要更新 LaTeX

```bash
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json

python 03-latex-review-diff/review_diff.py \
  --project-root thesis
```

### 5. 我要准备答辩了

```bash
python 17-defense-pack/generate_outline.py \
  --project-root thesis \
  --ruleset university-generic

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset university-generic
```

### 6. 我想筛查 AI 生成或可疑的参考文献

```bash
python 18-verify-references/verify_external_references.py \
  --project-root thesis \
  --ruleset university-generic

python 10-check-references/check_references.py \
  --project-root thesis \
  --ruleset university-generic \
  --with-external-verification
```

适合在你怀疑部分参考文献是 AI 生成、来源不清、或 metadata 不可靠时使用。它会把可疑、弱匹配、无法联网核验的条目标出来，但不会自动改写 bibliography。

如果你还要继续做声明-引用支撑分级，可以进一步运行：

```bash
python 20-check-claim-citation/check_claim_citation.py \
  --project-root thesis \
  --ruleset university-generic
```

它会输出 `reports/claim-citation-triage-report.json`，对声明-引用支撑分级做确定性分层。报告保留原有 `triage_label`，并额外给出 `claim_type`、`support_review_label`、`support_review_reason`、`support_signals`、`risk_signals`、`cluster_keys`、`cluster_risk_summary` 和 `next_actions`，帮助人工判断单条引用或成组引用下一步该核验什么；这些字段不等同于最终真伪判断。如果 `.bib` 中有 title、abstract、keywords，本地词面证据会分别计算这些字段与 claim context 的 token overlap。`possible_topic_mismatch`、`possible_outdated_support`、`possible_overclaim` 等保守风险信号只提示人工复核，不自动判定引用错误。JSON/Markdown 报告也可能包含 advisory `citation_needed_candidates`，用于提示没有引用但像强断言的句子，默认不作为 blocking 结果。

### 7. 我准备提交终稿，需要清理过程痕迹

```bash
python 23-check-final-cleanup/check_final_cleanup.py \
  --project-root thesis \
  --ruleset university-generic
```

输出：`reports/final-cleanup-report.json`。它会扫描 `TODO`、`FIXME`、`???`、`\textcolor{blue}`、`\color{blue}`、`draft`、`debug`、`待修改`、`待核查` 等终稿残留，但只报告定位，不自动删除、不改写正文。这个 JSON artifact 后续可以并入 `reports/final-audit-report.json`，再由 static HTML report surfaces 展示。

### 8. 我需要检查统计表达和手工目录锚点

```bash
python 25-check-statistical-consistency/check_statistical_consistency.py \
  --project-root thesis \
  --ruleset university-generic

python 26-check-manual-anchor/check_manual_anchor.py \
  --project-root thesis \
  --ruleset university-generic
```

统计一致性报告输出 `reports/statistical-consistency-report.json`，会先统计当前项目的主流写法，再报告偏离主流的 `p值/P值`、`p=/P=`、`95%CI/95\%CI/95%置信区间`、`Bootstrap/自助法`、`SMD/标准化均数差` 等混用情况。手工锚点报告输出 `reports/manual-anchor-report.json`，会提示 `\addcontentsline` 前可能缺少 `\phantomsection` 的位置。两者都只报告风险，不自动改写统计表达、不改 label、caption、编号、表格、图片或 `\ref{}`。

### 9. 我需要一份终稿审计总报告

```bash
python 27-final-audit-report/build_final_audit_report.py \
  --project-root thesis \
  --ruleset university-generic
```

输出：`reports/final-audit-report.json`。它只聚合已经生成的 JSON evidence，把 final cleanup、statistical consistency、manual anchor、readiness、citation integrity、final reference set、external verification、DOI candidates、URL verification、hallucination risk、claim-citation support 等维度汇总成一个 handoff artifact。它不重新运行检查器、不联网、不修改 `.tex` / `.bib`，也不替代原始 JSON source-of-truth。

### 10. 我需要引用审计表格交付

```bash
python 28-reference-audit-ledger/build_reference_audit_ledger.py \
  --project-root thesis \
  --ruleset university-generic
```

输出：`reports/reference-audit-ledger.csv`。它把本地 citation integrity、final reference set、external verification、DOI candidates、URL verification、hallucination risk 等已有证据合并为表格行，保留每个来源自己的 status。它不修改 `.bib`、不自动插入 DOI、不替换 URL、不联网，也不会把外部数据库 `NO_CANDIDATE` 直接说成假文献。

### 11. 我需要一个本地报告入口页

```bash
python 29-report-index/build_report_index.py \
  --project-root thesis
```

输出：`reports/index.html`。这个页面只作为本地阅读入口，链接已有 JSON / CSV artifacts，并展示 present / missing / unreadable 数量。JSON / CSV 仍然是 source of truth，不需要前端框架或后端服务。

### 12. 我想先看一版终稿审计 HTML 页

```bash
python 30-final-audit-html/build_final_audit_html.py \
  --project-root thesis
```

输出：`reports/final-audit-report.html`。它从 `final-audit-report.json` 生成，展示 overall verdict、KPI、dimension matrix、issues、next actions 和 source links。JSON 仍然是 authoritative source，不会被 HTML 替代。

### 13. 我想先看一版引用审计台账 HTML 页

```bash
python 31-reference-ledger-html/build_reference_audit_ledger_html.py \
  --project-root thesis
```

输出：`reports/reference-audit-ledger.html`。它从 `reference-audit-ledger.csv` 生成，展示 summary stats、按 scope 浏览、按 citation key 浏览，以及完整台账表格。CSV 仍然是 authoritative source，不会被 HTML 替代。

如果你想先看外部元数据层面的风险分值，可先运行 `19-check-hallucination-risk/check_hallucination_risk.py`，查看每条文献的 `hallucination_risk_score`。

更多场景见 [`docs/examples.md`](docs/examples.md)。

---

## 规则包

规则包是 Thesis Skills 最核心的概念之一：它把你学校的格式要求编码成结构化的 YAML 配置，让检查器知道什么算"对"、什么算"错"。

### 内置规则包

```text
90-rules/packs/
 ├── university-generic/        # 通用高校论文启动包（默认、宽松）
 ├── journal-generic/           # 通用期刊文章启动包（英文、精简）
 ├── tsinghua-thesis/           # 清华大学硕士/博士学位论文包
 │                              #   已按《研究生学位论文写作指南（202503）》做过首轮校准
 │                              #   中英文混排规则、图表编号、参考文献默认项已按写作指南调整
 └── demo-university-thesis/    # 非清华高校的具体示例包
```

- `university-generic` 适合**大部分国内高校**的学位论文，规则覆盖面广、阈值适中。
- `tsinghua-thesis` 针对清华同学做了专门校准：引用格式按 GB/T 7714、中英混排参照学校写作指南、章节命名匹配中文学位论文惯例。对很多清华论文项目来说，这个包可以直接作为起点使用，但仍建议结合院系模板和本地要求再复核 1 轮。
- `journal-generic` 适合英文期刊投稿场景，关闭了 CJK 特有规则（中英空格、全半角标点等）。

### 规则包内部结构

每个规则包是一个文件夹，包含三个文件：

```
90-rules/packs/your-school/
 ├── pack.yaml      # 包元信息：名称、类型、版本
  ├── rules.yaml     # 规则定义：做什么检查、报什么级别
 └── mappings.yaml  # 文件名/路径映射（如主文件候选名、bib 文件位置）
```

`rules.yaml` 是核心，按维度分为：

| 配置区 | 控制什么 | 示例 |
|---|---|---|
| `project` | 项目结构：主 tex 文件名、章节文件 glob、bib 文件路径 | `main_tex_candidates`、`chapter_globs` |
| `reference` | 引用完整性：缺失 key、孤立条目、重复标题、bib 质量 | `missing_key: error` |
| `language` | 语言规范：中英空格、括号配对、标点风格、弱词检测 | `cjk_latin_spacing`、`bracket_mismatch` |
| `language_deep` | 深层语言：连接词、搭配、推断力度、边界声明 | `inference_overclaim`、`boundary_signpost` |
| `consistency` | 术语一致性：相同概念的不同写法 | `terminology_consistency` |
| `format` | 格式结构：图表清单、编号、交叉引用 | `require_list_of_figures` |
| `content` | 内容完整性：必含章节、摘要关键词数量 | `required_sections` |
| `compile` | 编译诊断：引擎、错误分类、严重度 | `engine_hint: xelatex` |

### 创建你自己的学校规则包

如果你不是清华学生，或者你的学院/期刊有特殊要求，可以基于内置包创建自己的规则包。

**第 1 步：创建包骨架**

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "我的大学硕士学位论文" \
  --starter university-generic \
  --kind university-thesis
```

这会在 `90-rules/packs/my-university/` 下生成三个文件，内容从 `university-generic` 复制而来作为起点。

**第 2 步：修改项目结构配置**

打开 `rules.yaml`，修改 `project` 部分让它匹配你的论文目录结构：

```yaml
project:
  main_tex_candidates:       # 主文件可能叫这些名字，按优先级排列
    - thesis.tex
    - main.tex
    - 毕业论文.tex
  chapter_globs:             # 章节文件在哪里、叫什么模式
    - chapters/*.tex
  bibliography_files:        # bib 文件路径
    - ref/refs.bib
```

**第 3 步：按学校要求调整规则**

对照你学校的学位论文写作指南，逐条决定：

- **要开的规则**：你的学校规范里明确要求、且 checker 能自动检测的（如引用 key 缺失、图表编号格式）
- **要降级的规则**：学校规范没有强制要求的，把 `severity` 从 `warning` 改成 `info`（如中英空格）
- **要关的规则**：明显不适用于你们学校或学科的，设 `enabled: false`（如英文投稿不需要 CJK 规则）

一个常见的调整示例——把中英空格从强警告降为信息提示：

```yaml
# 修改前
cjk_latin_spacing:
  enabled: true
  severity: warning

# 修改后（学校指南没规定中英空格）
cjk_latin_spacing:
  enabled: true
  severity: info
```

**第 4 步：更新 content 要求的章节名**

如果你的论文章节不是英文 IMRaD 结构，记得同步修改：

```yaml
content:
  required_sections:
    - 绪论
    - 文献综述
    - 研究方法
    - 结论
```

**第 5 步：使用自定义包运行检查**

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset my-university \
  --skip-compile
```

**第 6 步：验证并迭代**

运行后查看 `reports/` 下的 JSON 报告。如果发现：
- **某类误报过多** → 降低该规则的 severity 或禁用
- **某类真实问题没检测到** → 检查规则是否已启用、severity 是否过低
- **项目发现失败** → 调整 `main_tex_candidates` 或 `chapter_globs`

修改 → 重新运行 → 查看报告，通常 1-2 轮就能校准到位。

> **给非清华同学的建议**：如果你希望我们宣传你的学校规则包，欢迎提 PR 把校准好的规则包放到 `90-rules/packs/` 下。这样后来的同学就不需要从零开始。

---

## Tested on

- Python 3.10+
- Windows / macOS / Linux
- `--skip-compile` demo 不需要 LaTeX；需要编译日志诊断时再去掉 `--skip-compile`

---

## 边界

| Thesis Skills 是 | Thesis Skills 不是 |
|---|---|
| Word、Zotero、EndNote 和 LaTeX 之间的工作流桥梁 | 论文模板或文档类 |
| 面向格式与结构规则的确定性检查器 | 会生成论文正文的 AI 写作助手 |
| 基于报告和 dry-run 预览的修复流程 | Grammarly 或其他润色工具的替代品 |
| 提交前 readiness gate | 自动生成最终答辩 PPT 的工具 |
| 可通过学校/期刊规则包扩展 | 已经覆盖所有学校或期刊规则的保证 |
| CLI-first、artifact 可审计的本地流程 | GUI 或 Web 编辑器 |

---

## 文档

| 文档 | 用途 |
|---|---|
| [`docs/quickstart.md`](docs/quickstart.md) | 最小安装和首次检查运行 |
| [`docs/examples.md`](docs/examples.md) | 输出预览和场景示例 |
| [`docs/modules.md`](docs/modules.md) | 从 README 拆出的完整模块参考 |
| [`docs/architecture.md`](docs/architecture.md) | 工作流与模块架构 |
| [`docs/getting-started-zh.md`](docs/getting-started-zh.md) | 中文新手完整教程 |
| [`CHANGELOG.md`](CHANGELOG.md) | 版本历史 |

---

## 历史迭代记录

- `v3.3.0`：加入 final reference set、可续跑外部验证、DOI 候选建议和 URL 验证。
- `v3.2.0`：将幻觉风险评分和声明-引用分级接入 readiness gate，新增统一证据流水线 runner。
- `v3.1.0`：加入声明-引用支撑分级、`claim-citation-triage-report.json`、确定性分级评分，以及三个 demo 项目。
- `v3.0.0`：加入幻觉风险评分、`hallucination-risk-report.json`、`high-risk-references.csv`、中文文献 `UNSUPPORTED` 处理，以及三个 demo 项目。
- `v2.0.0`：加入 CrossRef / OpenAlex / Semantic Scholar 外部验证、候选合并，以及 `external_verification` advisory。
- `v1.0.0`：把公开工作流叙事稳定下来，让 README、roadmap、站点、示例和代码路径一致。
- `v1.1.0`：加入本地优先的 Citation Integrity 引擎，并接入 readiness gate。
- `v1.2.0`：加入 Citation Integrity 的 Markdown/CSV 输出、clean/broken demo，以及公开版本线对齐。
- 更完整的变更记录见 [`CHANGELOG.md`](CHANGELOG.md)。

---

## 如何同步后续更新

无论你是第一次下载还是第一次 `git clone`，后续更新都**不会自动出现在你的本地**。

你需要根据自己的获取方式手动更新：

### 如果你是用 Git clone 下来的

运行：

```bash
git pull origin main
```

这会把 GitHub 上最新提交的内容拉到你的本地仓库。

如果你想先看远端有哪些更新，再决定是否同步：

```bash
git fetch origin
git log --oneline HEAD..origin/main
```

### 如果你是直接下载 ZIP

ZIP 只是一个快照，**不会自己同步更新**。

后续要拿新版本，你有两种办法：

1. 去 GitHub 重新下载新的 ZIP，然后手动替换本地目录
2. 改用 `git clone`，以后只需要 `git pull`

### 如果你已经在本地改过代码或文档

本地有未提交修改时，直接更新更容易遇到冲突。先检查：

```bash
git status
```

如果看到有本地改动，建议先自己提交、备份，或者复制出一份，再去执行 `git pull`。

---

## 模块参考

长模块表已移动到 [`docs/modules.md`](docs/modules.md)，让 README 聚焦产品工作流。

---

## 模板推荐

Thesis Skills 不是 LaTeX 论文模板，它适合搭配成熟模板和学校特定文档类一起使用。

| 机构 | 模板仓库 |
|---|---|
| 清华大学 | [tuna/thuthesis](https://github.com/tuna/thuthesis) |
| 上海交通大学 | [sjtug/SJTUThesis](https://github.com/sjtug/SJTUThesis) |
| 中国科学技术大学 | [ustctug/ustcthesis](https://github.com/ustctug/ustcthesis) |
| 北京大学 | [CasperVector/pkuthss](https://github.com/CasperVector/pkuthss) |
| Stanford University | [dcroote/stanford-thesis-example](https://github.com/dcroote/stanford-thesis-example) |
| University of Cambridge | [cambridge/thesis](https://github.com/cambridge/thesis) |

---

## 致谢

特别感谢 [tuna/thuthesis](https://github.com/tuna/thuthesis) 以及其他开源论文模板项目。这些项目让高质量 LaTeX 论文写作更容易，也启发了 Thesis Skills 的工作流设计。

---

## 许可证

MIT License
