# Thesis Skills v1.0.0

<div align="center">

**面向研究生论文的引用同步、格式检查、审阅交接与提交前检查工具箱。**

把时间留给研究，而不是反复修格式。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![展示页面](https://img.shields.io/badge/展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** · [English](README.md) · [展示页面](https://quzhiii.github.io/thesis-skills)

</div>

---

## 这是什么？

Thesis Skills **不是** AI 写作助手，**不是**论文模板，也**不替你生成论文内容**。

它是一个 **命令行工作流系统**，用于连接研究生和科研作者已经在使用的工具：Word、Zotero、EndNote、LaTeX、结构化检查报告、安全修复补丁、审阅交接材料和提交前 readiness 检查。

```text
Zotero / EndNote ──→ [ Thesis Skills ] ──→ LaTeX 论文
Word .docx ────────→                         │
                                              ├── 检查报告
                                              ├── dry-run 修复补丁
                                              ├── 审阅友好 Word 导出
                                              ├── PASS / WARN / BLOCK readiness gate
                                              └── 答辩准备材料
```

它的目标很明确：把分散、手动、易错的论文后期工作，变成一个**可检查、可复现、可审计**的流程。

---

## 快速体验

使用内置示例项目跑一次检查流程：

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

预期结果：生成结构化检查报告，不需要本地安装 LaTeX。

如果你已经有自己的 LaTeX 论文项目：

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset university-generic \
  --skip-compile
```

> 正式发布前，建议从 clean clone 环境验证示例项目和所有命令均可运行。

---

## 为什么做这个项目

这个项目来自真实论文写作流程中的问题。

和很多研究者一样，我从 Word 开始写论文——门槛低、导师也在用、Zotero 插件插引用很方便。但写到第 3 章时，噩梦开始了：一个三线表调了 40 分钟边框还是对不齐，新增一个图表后面十几个交叉引用编号全乱了，用 AI 改了一段文字后 Zotero 引用域代码直接崩了。

Word 前期很方便，尤其当导师使用 Word 审阅、文献管理器依赖 Word 插件时。但对于长篇学位论文，表格、图题、交叉引用、文献引用、章节编号和格式规范都会变得脆弱。

LaTeX 更适合长篇学术写作，但迁移、引用映射、导师 Word 审阅、格式检查和提交前确认仍然需要大量重复且易错的机械劳动。

**Thesis Skills 只处理这些重复但高风险的环节。** 不是替你写论文，而是替你处理那些重复、易错、耗时的格式劳动。

---

## 它解决哪些问题？

| 问题 | 常见风险 | Thesis Skills 的处理方式 |
|---|---|---|
| 引用迁移 | Zotero / EndNote 元数据丢失，引用 key 不稳定 | 规范化文献并维护稳定 `refNNN` ID |
| Word 转 LaTeX | 章节、图表、引用和结构需要手动重建 | 按规则将内容迁移到 LaTeX 项目结构 |
| AI 辅助改稿 | Word 域代码或引用标记可能变成普通文本 | 让引用和审阅材料保持显式、可检查 |
| 格式检查 | 学校或期刊规则依赖人工逐项核对 | 运行确定性检查并输出结构化报告 |
| 安全修复 | 盲目自动修改可能引入新错误 | 先生成 dry-run 补丁，再决定是否应用 |
| 导师审阅 | 源文件是 LaTeX，但导师常常需要 Word | 导出审阅友好 Word，并显式记录降级项 |
| 提交前确认 | 多份报告分散，难以判断是否可以提交 | 汇总为 PASS / WARN / BLOCK readiness gate |
| 答辩准备 | 大纲、图表清单、讲稿备注需要反复翻全文 | 生成结构化答辩准备材料 |

---

## 核心流程

| 阶段 | 传统方式 | Thesis Skills 输出 | 节省 |
|---|---|---|---|
| 文献接入 | 手动导出、改名、去重、稳定引用 key（30–60 分钟） | 规范化文献库和稳定 `refNNN` 映射 | **~10×** |
| Word ↔ LaTeX 迁移 | 手动重建结构、图表、引用和审阅版本（1–3 小时） | 迁移 artifact 与审阅友好导出路径 | **~15×** |
| 确定性检查 | 按学校或期刊规范反复人工核对（1–3 小时/轮） | 含文件、行号、规则、严重程度和建议的 JSON 报告 | **~20×** |
| 安全修复 | 人工逐条定位并修改问题（1–2 小时） | 可预览补丁，dry-run 优先 | **~10×** |
| Readiness gate | 提交前翻阅多份分散报告（30–60 分钟） | 一个 PASS / WARN / BLOCK 汇总与下一步行动 | **~30×** |
| 答辩准备 | 手动整理大纲、图表清单和讲稿要点（2–4 小时） | 结构化大纲、图表清单、候选视觉材料和备注 | **~15×** |

> 节省时间为保守估算，基于重复性格式劳动的自动化。工具不替代写作思考时间。

---

## 实际输出示例

### Readiness gate 报告

```bash
python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

```json
{
  "verdict": "WARN",
  "mode": "advisor-handoff",
  "blockers": [],
  "warnings": [
    "3 unreferenced citations (see 10-check-references report)",
    "2 figures lack alt-text (see 13-check-content report)"
  ],
  "next_actions": [
    "Run: python 20-fix-references/fix_references.py --apply false",
    "Review: reports/13-check-content-report.json lines 45-52"
  ]
}
```

### 确定性检查报告

```json
{
  "rule": "cjk_latin_spacing",
  "severity": "warning",
  "file": "chapters/introduction.tex",
  "line": 42,
  "message": "Missing space between CJK and Latin: '人工智能AI' → '人工智能 AI'",
  "autofix_safe": true,
  "suggested_fix": "人工智能 AI"
}
```

---

## 按场景使用

### 1. 我刚从 Word 转到 LaTeX

```bash
# 1. 将 Zotero 引用从 Word 同步到 LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

# 2. 运行全面检查
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

# 3. 预览并应用安全修复
python run_fix_cycle.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --apply false
```

### 2. 我已经在用 LaTeX，想检查论文

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

### 3. 导师/合作者需要 Word 版本审稿

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply true
```

### 4. 导师给了 Word 反馈，我要更新 LaTeX

```bash
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json

python 03-latex-review-diff/review_diff.py \
  --project-root thesis
```

### 5. 我要准备答辩

```bash
python 17-defense-pack/generate_outline.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_talk_prep_notes.py \
  --project-root thesis \
  --ruleset tsinghua-thesis
```

---

## 全流程一览

```text
论文工作阶段                            Thesis Skills 对应模块
────────────────────────────────────────────────────────────────

1. 参考文献库
   · EndNote 导出                     00-bib-endnote/
   · Zotero 同步                      00-bib-zotero/

2. 草稿迁移与审阅交接
   · Word → LaTeX                     01-word-to-latex/
   · LaTeX → 审阅友好 Word            02-latex-to-word/
   · Review diff 与 TODO              03-latex-review-diff/
   · Word 反馈接入                    04-word-review-ingest/

3. 检查阶段
   · 引用完整性                       10-check-references/
   · 基础语言规则                     11-check-language/
   · 格式结构检查                     12-check-format/
   · 内容完整性检查                   13-check-content/
   · 深度语言筛查                     14-check-language-deep/
   · 编译诊断                         15-check-compile/

4. 修复阶段
   · 引用修复                         20-fix-references/
   · 语言风格修复                     21-fix-language-style/
   · 格式结构修复                     22-fix-format-structure/
   · 深度语言补丁                     24-fix-language-deep/

5. 提交前确认
   · PASS / WARN / BLOCK gate         16-check-readiness/

6. 答辩准备
   · 大纲、图表清单、讲稿备注          17-defense-pack/

7. 学校规则适配
   · 自定义规则包                     90-rules/
```

---

## 规则包

规则包用于表达学校或期刊的特定要求：项目布局、引用格式、语言规则、格式规范、内容要求和 readiness 判定标准。

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

## Thesis Skills 是什么，和不是什么

| Thesis Skills 是 | Thesis Skills 不是 |
|---|---|
| Word、Zotero、EndNote 与 LaTeX 之间的桥梁 | 论文模板或文档类 |
| 面向格式和结构规则的确定性检查器 | 帮你生成论文内容的 AI 写作助手 |
| 基于报告、支持 dry-run 预览的工作流 | Grammarly、秘塔写作猫等文本润色工具的替代品 |
| 提交前 readiness gate | 自动生成最终答辩 PPT 的工具 |
| 可通过学校规则包扩展 | 已经支持所有学校或期刊规则的万能工具 |
| 命令行工具，输出可审计 artifact | GUI 或 Web 编辑器 |

---

## 文档

| 文档 | 作用 |
|---|---|
| [`docs/getting-started-zh.md`](docs/getting-started-zh.md) | 中文零基础入门教程（约 880 行） |
| [`docs/architecture.md`](docs/architecture.md) | 工作流和模块架构说明 |
| [`90-rules/`](90-rules/) | 规则包工具与示例 |
| [`examples/`](examples/) | 示例项目和 demo 输入 |
| [`site/`](site/) | 静态展示页面和 landing page 材料 |

---

## 零基础入门

没用过 LaTeX 或命令行工具？从这里开始：

1. **第 1 天**：阅读 [`docs/getting-started-zh.md`](docs/getting-started-zh.md) —— 从安装到生成第一份检查报告的完整教程
2. **第 2 天**：用示例项目（`examples/minimal-latex-project`）加 `--skip-compile` 跑一遍，看所有输出
3. **第 3 天**：把 `run_check_once.py` 指向你自己的论文，查看检查报告

---

## 模块速览

| 阶段 | 模块 | 入口 |
|---|---|---|
| **文献** | `00-bib-zotero/` | `sync_from_word.py`, `check_bib_quality.py` |
| | `00-bib-endnote/` | `check_endnote_export.py`, `import_library.py` |
| **迁移** | `01-word-to-latex/` | `migrate_project.py` |
| | `02-latex-to-word/` | `migrate_project.py` |
| | `03-latex-review-diff/` | `review_diff.py` |
| | `04-word-review-ingest/` | `feedback_ingest.py` |
| **检查** | `10-check-references/` | `check_references.py` |
| | `11-check-language/` | `check_language.py`（28+ 规则） |
| | `12-check-format/` | `check_format.py` |
| | `13-check-content/` | `check_content.py` |
| | `14-check-language-deep/` | `check_language_deep.py` |
| | `15-check-compile/` | `check_compile.py` |
| **修复** | `20-fix-references/` | `fix_references.py` |
| | `21-fix-language-style/` | `fix_language_style.py` |
| | `22-fix-format-structure/` | `fix_format_structure.py` |
| | `24-fix-language-deep/` | `fix_language_deep.py` |
| **Gate** | `16-check-readiness/` | `check_readiness.py` |
| **答辩** | `17-defense-pack/` | `generate_outline.py`, `generate_figure_inventory.py`, `generate_talk_prep_notes.py` |
| **规则** | `90-rules/` | `create_pack.py`, `lint_pack.py`, `scorecard.py` |
| **Runner** | `99-runner/` | `run_check_once.py`, `run_fix_cycle.py` |

---

## 模板推荐

Thesis Skills 不是 LaTeX 论文模板。它更适合与成熟的高校模板和文档类配合使用。

| 高校 | 模板仓库 |
|---|---|
| 清华大学 | [tuna/thuthesis](https://github.com/tuna/thuthesis) |
| 上海交通大学 | [sjtug/SJTUThesis](https://github.com/sjtug/SJTUThesis) |
| 中国科学技术大学 | [ustctug/ustcthesis](https://github.com/ustctug/ustcthesis) |
| 北京大学 | [CasperVector/pkuthss](https://github.com/CasperVector/pkuthss) |
| Stanford University | [dcroote/stanford-thesis-example](https://github.com/dcroote/stanford-thesis-example) |
| University of Cambridge | [cambridge/thesis](https://github.com/cambridge/thesis) |

---

## 致谢

特别感谢 [tuna/thuthesis](https://github.com/tuna/thuthesis) 以及其他开源论文模板项目。这些项目降低了高质量 LaTeX 学位论文写作的门槛，也启发了 Thesis Skills 的工作流设计。

---

## 许可证

MIT License
