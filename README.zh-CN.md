# Thesis Skills v1.0.0

<div align="center">

**用于引用同步、格式检查、审阅交接和提交前 readiness 检查的确定性论文工作流工具。**

把时间花在思考上，而不是反复修格式。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Showcase](https://img.shields.io/badge/展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** · [English](README.md) · [展示页面](https://quzhiii.github.io/thesis-skills)

[快速开始](#快速开始) · [输出](#输出) · [使用场景](#使用场景) · [规则包](#规则包) · [创建自己的规则包](#创建你自己的学校规则包) · [边界](#边界)

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

规则包是 Thesis Skills 最核心的概念之一：它把你学校的格式要求编码成结构化的 YAML 配置，让检查器知道什么算"对"、什么算"错"。

### 内置规则包

```text
90-rules/packs/
 ├── university-generic/        # 通用高校论文启动包（默认、宽松）
 ├── journal-generic/           # 通用期刊文章启动包（英文、精简）
 ├── tsinghua-thesis/           # 清华大学硕士/博士学位论文包
 │                              #   已对标《研究生学位论文写作指南（202503）》
 │                              #   中英文混排规则、图表编号、参考文献格式等均与校内规范一致
 ├── tsinghua-thesis-experimental/  # 同上，实验校准版（与正式包同步更新）
 └── demo-university-thesis/    # 非清华高校的具体示例包
```

- `university-generic` 适合**大部分国内高校**的学位论文，规则覆盖面广、阈值适中。
- `tsinghua-thesis` 针对清华同学做了专门校准：引用格式按 GB/T 7714、中英混排参照学校写作指南、章节命名匹配中文学位论文惯例。清华同学直接用这个包即可，无需额外配置。
- `journal-generic` 适合英文期刊投稿场景，关闭了 CJK 特有规则（中英空格、全半角标点等）。

### 规则包内部结构

每个规则包是一个文件夹，包含三个文件：

```
90-rules/packs/your-school/
 ├── pack.yaml      # 包元信息：名称、类型、版本
 ├── rules.yaml     # 规则定义：做什么检查、什么行业、报什么级别
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
