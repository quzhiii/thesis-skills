# Thesis Skills v1.0.0

<div align="center">

**用于引用同步、格式检查、审阅交接和提交前 readiness 检查的确定性论文工作流工具。**

把时间花在思考上，而不是反复修格式。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** · [English](README.md) · [展示页面](https://quzhiii.github.io/thesis-skills)

[快速开始](#快速开始) · [输出](#输出) · [使用场景](#使用场景) · [规则包](#规则包) · [边界](#边界)

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

| 工作流 | 手工基线 | 使用 Thesis Skills |
|---|---:|---:|
| 文献接入 | 30-60 分钟 | 2-5 分钟 |
| Word ↔ LaTeX 审阅交接 | 1-3 小时 | 5-10 分钟 |
| 确定性格式检查 | 1-3 小时 | 2-5 分钟 |
| 基于报告的安全修复 | 1-2 小时 | 5-10 分钟 |
| 提交前 readiness 复核 | 30-60 分钟 | 1-2 分钟 |
| 答辩前清单整理 | 2-4 小时 | 10-15 分钟 |

> 时间节省是对重复性格式和交接工作的保守估算。Thesis Skills 不替代写作、思考、导师判断或学校/期刊规则的最终人工确认。

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

### Hero workflow

```text
1. 接入          2. 检查            3. 安全修复          4. Gate         5. 交接
──────────       ───────────        ─────────────        ─────────       ─────────────
Zotero           references         dry-run 补丁         PASS            导师审阅 Word
EndNote     →    language      →    先预览再应用    →    WARN      →     review TODOs
Word/LaTeX       format             显式确认修改         BLOCK           答辩准备材料
```

### Readiness gate preview

```text
┌──────────────────────────────────────────────────────────────┐
│ Readiness verdict: WARN                                      │
├───────────────────────┬────────┬─────────────────────────────┤
│ Dimension             │ Status │ Why it matters              │
├───────────────────────┼────────┼─────────────────────────────┤
│ References            │ PASS   │ all cite keys resolve       │
│ Language              │ WARN   │ 2 style warnings remain     │
│ Format                │ PASS   │ labels and refs are stable  │
│ Compile evidence      │ WARN   │ skipped in demo mode        │
│ Export evidence       │ WARN   │ not produced by smoke test  │
│ Review-loop evidence  │ WARN   │ not produced by smoke test  │
└───────────────────────┴────────┴─────────────────────────────┘

Next actions:
1. Review reports/check_language-report.json
2. Generate Word export / review-loop artifacts when those handoffs are needed
3. Re-run without --skip-compile before final submission
```

一次真实运行会生成这些机器可读 artifacts：

- `reports/check_references-report.json`
- `reports/check_language-report.json`
- `reports/check_format-report.json`
- `reports/check_content-report.json`
- `reports/readiness-report.json`
- `reports/run-summary.json`

输出示例和演示流程见 [`docs/examples.md`](docs/examples.md)。

---

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

更多场景见 [`docs/examples.md`](docs/examples.md)。

---

## 规则包

规则包用于编码学校或期刊的具体要求：项目布局、引用格式、语言规则、格式规则、内容要求，以及 readiness criteria。

```text
90-rules/packs/
 ├── university-generic/      # 通用高校论文启动包
 ├── journal-generic/         # 通用期刊文章启动包
 ├── tsinghua-thesis/         # 清华大学示例
 └── demo-university-thesis/  # 具体的非清华示例包
```

创建自定义规则包：

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "我的大学论文" \
  --starter university-generic \
  --kind university-thesis
```

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
