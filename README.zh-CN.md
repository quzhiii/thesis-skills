# Thesis Skills v1.0.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/论文-技能-4285f4?style=for-the-badge&logo=book&logoColor=white)

# 你的论文时间应该花在思考上，而不是格式上

*自动化学术写作中的重复性格式劳动 —— 引用迁移、格式检查、审阅交接、答辩准备*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![Landing Page](https://img.shields.io/badge/🚀%20展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** • [English](README.md) • [🚀 展示页面](https://quzhiii.github.io/thesis-skills)

[6 大痛点](#这些场景你是否经历过) • [能力矩阵](#核心能力) • [按场景使用](#按场景使用) • [规则包系统](#规则包系统) • [当前边界](#当前边界)

</div>

---

## 这些场景，你是否经历过？

> **「新增一个引用，后面十几个编号全乱了。」**
>
u003e **「导师突然说要 Word 版本审稿，我懵了。」**
>
u003e **「用 AI 改了一段文字，Zotero 引用全崩了。」**
>
u003e **「学校格式规范 30 多条，改了 3 轮还是漏了某处。」**
>
u003e **「定稿前不敢点提交，怕还有隐藏问题。」**>
> **「答辩前手动梳理图表清单，翻了 3 小时全文。」**

| 💔 传统工作流 | 😰 典型耗时 |
|:---|:---|
| Word 写论文 → 手动调整三线表、交叉引用、页眉页脚 | 数小时/处 |
| 想转 LaTeX → 手动迁移章节、重建引用、调整格式 | 1-3 天 |
| 用 AI 改 Word 稿 → Zotero 域代码崩坏，引用变纯文本 | 数小时修复 |
| 人工逐项核对学校格式规范 | 1-3 小时/轮 |
| 定稿前翻阅 5-10 份分散报告确认状态 | 30-60 分钟 |
| 答辩前手动整理大纲、图表清单、讲稿 | 2-4 小时 |

---

## 核心能力

### Before → After：每一步省多少时间

| 阶段 | 传统方式 | Thesis Skills | 节省时间 |
|:---|:---|:---|:---|
| **📚 文献接入** | 从 Zotero/EndNote 手动复制粘贴，重建引用编号 | 自动导入，生成稳定 `refNNN` ID，增量同步 | **30-60 分钟 → 2-5 分钟** |
| **🔄 Word ↔ LaTeX** | 手动复制内容、重建结构、重新映射引用 | 自动迁移引用 + 结构化检查；一键导出 review-friendly Word | **1-3 小时 → 5-10 分钟** |
| **✅ 格式检查** | 人工逐项核对 28+ 项规范，易遗漏 | YAML 规则包驱动，28+ 项自动检查，2 分钟出报告 | **1-3 小时 → 2-5 分钟** |
| **🔧 安全修复** | 手动定位、修改、验证 | 基于报告生成可预览补丁，dry-run 后应用 | **1-2 小时 → 5-10 分钟** |
| **🚦 定稿确认** | 翻阅多份报告，仍不确定是否 ready | `PASS / WARN / BLOCK` 单页汇总，blockers + next actions | **30-60 分钟 → 1-2 分钟** |
| **🎯 答辩准备** | 手动梳理大纲、整理图表、准备讲稿 | 自动生成大纲、章节要点、图表清单、候选视觉材料 | **2-4 小时 → 10-15 分钟** |

> ⚠️ **客观说明**：以上时间为保守估算，节省的是重复性格式劳动时间。工具不替代写作思考。

### 实际输出示例

**Readiness Gate —— 定稿前最后一道检查：**

```bash
$ python 16-check-readiness/check_readiness.py \
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

**格式检查报告 —— 具体到文件、行号、修复建议：**

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

### 🚀 场景 1：我刚从 Word 转到 LaTeX

```bash
# 1. 将 Zotero 引用从 Word 同步到 LaTeX（稳定 refNNN 编号）
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis --word-file thesis.docx --apply

# 2. 运行全面检查（引用、语言、格式、内容）
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis --skip-compile

# 3. 预览并应用安全修复
python run_fix_cycle.py \
  --project-root thesis --ruleset tsinghua-thesis --apply false
```

### 🚀 场景 2：我一直在用 LaTeX，要检查论文

```bash
# 运行完整检查（含编译诊断）
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis

# 查看 readiness gate
python 16-check-readiness/check_readiness.py \
  --project-root thesis --ruleset tsinghua-thesis --mode advisor-handoff
```

### 🚀 场景 3：导师/合作者需要 Word 版本审稿

```bash
# 生成 review-friendly Word（显式报告降级项）
python 02-latex-to-word/migrate_project.py \
  --project-root thesis --output-file thesis-review.docx \
  --profile review-friendly --apply true

# 查看 reports/latex_to_word-report.json 了解降级情况
```

### 🚀 场景 4：导师给了 Word 反馈，我要修改 LaTeX

```bash
# 1. 将 Word 反馈归一化为结构化 issues
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis --input review-feedback.json

# 2. 生成 review diff 和 TODO
python 03-latex-review-diff/review_diff.py --project-root thesis
```

### 🚀 场景 5：我要准备答辩了

```bash
# 自动生成答辩准备材料
python 17-defense-pack/generate_outline.py \
  --project-root thesis --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis --ruleset tsinghua-thesis
```

---

## 模块速览

| 工作流 | 入口 | 输出 / 作用 |
|:---|:---|:---|
| Zotero 引用同步 | `00-bib-zotero/sync_from_word.py` | 从 Word 提取 Zotero 引用，生成稳定 `refNNN` 映射 |
| Zotero 文献质量检查 | `00-bib-zotero/check_bib_quality.py` | 检查 BibTeX 质量（缺失字段、DOI 格式等） |
| EndNote 导出预检 | `00-bib-endnote/check_endnote_export.py` | 导入前检查 EndNote 导出文件 |
| EndNote 导入 | `00-bib-endnote/import_library.py` | 规范化引用与稳定 `refNNN` ID |
| Word→LaTeX 迁移 | `01-word-to-latex/migrate_project.py` | 按 spec 映射文件到 LaTeX 项目结构 |
| LaTeX→Word 导出 | `02-latex-to-word/migrate_project.py` | 生成 review-friendly `.docx`，显式报告降级项 |
| Review package | `03-latex-review-diff/review_diff.py` | 生成 review diff、triage、TODO artifact |
| Feedback ingest | `04-word-review-ingest/feedback_ingest.py` | 将 Word 反馈归一化为结构化 issues |
| 引用检查 | `10-check-references/check_references.py` | 验证 `\cite{}` 与文献库一致性 |
| 语言检查 | `11-check-language/check_language.py` | 28+ 项确定性语言规则检查 |
| 格式检查 | `12-check-format/check_format.py` | 图表、标签、交叉引用、前置事项检查 |
| 内容检查 | `13-check-content/check_content.py` | 内容结构和摘要元数据检查 |
| 深度语言检查 | `14-check-language-deep/check_language_deep.py` | 高阶语言问题筛查 |
| 编译诊断 | `15-check-compile/check_compile.py` | 结构化解析 LaTeX 编译日志 |
| Readiness gate | `16-check-readiness/check_readiness.py` | 汇总所有报告，输出 PASS/WARN/BLOCK |
| 答辩准备 | `17-defense-pack/*.py` | 大纲、章节要点、图表清单、候选视觉材料、讲稿备注 |
| 安全修复器 | `20-fix-*` 到 `24-fix-*` | 基于报告生成可预览补丁，dry-run 后应用 |
| 规则包工具 | `90-rules/*.py` | 规则包创建、lint、完整性检查、scorecard |

---

## 规则包系统

内置启动包和示例包：

```text
90-rules/packs/
 ├── university-generic/     # 通用高校论文启动包
 ├── journal-generic/        # 通用期刊文章启动包
 ├── tsinghua-thesis/        # 清华大学示例
 └── demo-university-thesis/ # 具体的非清华示例包
```

创建自定义规则包：

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "我的大学论文" \
  --starter university-generic \
  --kind university-thesis
```

规则包包含学校/期刊特定的策略：项目布局、引用格式、语言规则、格式要求、内容要求。

---

## 当前边界

| 不支持 / 不承诺 | 当前定位 |
|:---|:---|
| 完整 GUI 或 Web 编辑器 | CLI-first 仓库 |
| 完整编译编排 | 解析已有日志，不替代 TeX 工具链 |
| 覆盖所有学校规则 | 规则包编码 policy，机构规则需人工确认 |
| 自动理解导师意图 | Feedback ingest 有边界，保持 review-gated |
| AI 生成论文正文 | 系统检查和修复有边界问题，不替你写论文 |
| 自动生成最终答辩 PPT | 答辩前整理只生成给人修改的准备材料 |
| 正式规则包 registry | 当前是本地、Git-tracked 或 handoff-oriented |
| Word .docx 直接解析 | Word→LaTeX 迁移需预导出为 `.tex` 和 `.bib` |
| 完美 LaTeX→Word 转换 | review-friendly 模式为主，部分构造会降级 |

---

## 技术架构

```text
thesis-skills/
├── core/                   # 共享实现（项目发现、检查器、修复器、报告）
├── 00-bib-endnote/         # EndNote 文献接入
├── 00-bib-zotero/          # Zotero 文献接入和 Word 同步
├── 01-word-to-latex/       # Word→LaTeX 迁移（文件映射层）
├── 02-latex-to-word/       # LaTeX→Word 导出（review-friendly）
├── 03-latex-review-diff/   # Review 包和分诊工作流
├── 04-word-review-ingest/  # Word 反馈归一化
├── 10-check-references/    # 引用检查
├── 11-check-language/      # 语言检查（28+ 规则）
├── 12-check-format/        # 格式检查
├── 13-check-content/       # 内容检查
├── 14-check-language-deep/ # 深度语言筛查
├── 15-check-compile/       # 编译日志诊断
├── 16-check-readiness/     # 预提交 readiness gate
├── 17-defense-pack/        # 答辩前准备材料
├── 20-fix-references/      # 引用修复
├── 21-fix-language-style/  # 语言风格修复
├── 22-fix-format-structure/# 格式结构修复
├── 24-fix-language-deep/   # 深度语言修复（预览）
├── 90-rules/               # 规则包系统
├── 99-runner/              # 统一入口（run_check_once.py, run_fix_cycle.py）
└── examples/               # 示例项目
```

详细架构说明见 [`docs/architecture.md`](docs/architecture.md)。

---

## 版本历史

| 版本 | 主题 |
|:---|:---|
| v0.3.0 | 公开仓库重组、双语 README、CI、Zotero 主路径 |
| v0.4.0 | EndNote XML/RIS/BibTeX 导入、DOI 去重、`refNNN` 稳定性 |
| v0.5.x | 确定性语言检查、深度语言审阅、选择性补丁预览 |
| v0.6.0 | 审阅友好 LaTeX→Word 导出、编译日志解析、审阅闭环 |
| v0.7.x | Readiness gate、审阅摘要硬化、feedback ingest 校准 |
| v0.8.x | 答辩前整理、静态 showcase、规则包 lint/completeness/schema/scorecard 硬化 |
| v1.0.0 | README、roadmap、site、manifest、规则包文档与实际代码路径对齐的稳定公开叙事 |

---

## 模板推荐

| 高校 | 仓库 |
|:---|:---|
| 清华大学 | [tuna/thuthesis](https://github.com/tuna/thuthesis) |
| 上海交通大学 | [sjtug/SJTUThesis](https://github.com/sjtug/SJTUThesis) |
| 中国科学技术大学 | [ustctug/ustcthesis](https://github.com/ustctug/ustcthesis) |
| 北京大学 | [CasperVector/pkuthss](https://github.com/CasperVector/pkuthss) |
| Stanford | [dcroote/stanford-thesis-example](https://github.com/dcroote/stanford-thesis-example) |
| Cambridge | [cambridge/thesis](https://github.com/cambridge/thesis) |

---

## 致谢

特别感谢 [tuna/thuthesis](https://github.com/tuna/thuthesis) 开源 LaTeX 论文模板，该项目造福了众多清华师生，也启发了本项目的开发。

---

## 许可证

MIT License
