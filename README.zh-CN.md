# Thesis Skills v1.0.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/论文-技能-4285f4?style=for-the-badge&logo=book&logoColor=white)

**确定性、可检查的论文与期刊写作工作流系统**
*文献接入 · LaTeX/Word 交接 · 检查器 · 安全修复器 · Readiness Gate · 规则包*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![展示页面](https://img.shields.io/badge/🚀%20展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** • [English](README.md) • [🚀 展示页面](https://quzhiii.github.io/thesis-skills)

[快速开始](#快速开始) • [核心工作流](#核心工作流) • [规则包系统](#规则包系统) • [当前边界](#当前边界) • [路线图](docs/roadmap.md) • [架构文档](docs/architecture.md) • [贡献指南](CONTRIBUTING.md)

</div>

---

## Thesis Skills 是什么

`thesis-skills` 是一套确定性、报告驱动的学术写作工作流层。它帮助你把论文或期刊稿件推进过文献接入、Word/LaTeX 交接、确定性检查、有边界修复、审阅闭环、readiness 判断、答辩前整理，以及可复用的学校/期刊规则包。

它不是通用 AI 写作助手，不是论文模板，不是图形界面编辑器，不是协作文档平台，也不承诺覆盖所有学校或机构的提交规则。每条工作流都应该留下人能打开检查的显式 artifact。

---

## 为什么需要 Thesis Skills？

| 痛点 | 传统工作流 | Thesis Skills |
|:---|:---|:---|
| Word→LaTeX 引用迁移 | 手动映射，容易出错 | 自动提取与同步，并保持稳定 ID |
| 文献库接入 | 从 EndNote / Zotero 复制粘贴 | XML/RIS/BibTeX 导入与质量检查 |
| 学校或期刊规则 | 人工读长文档 | YAML 规则包 + 可重复检查 |
| 导师审阅交接 | 临时导 Word、反馈四处分散 | 审阅友好导出、diff、ingest 与 TODO artifact |
| 定稿前判断 | 人工翻多份报告 | 有边界的 `PASS / WARN / BLOCK` readiness verdict |
| 答辩准备 | 一边翻全文一边做 PPT | 大纲、章节要点、图表清单、候选视觉材料和讲稿备注 |

---

## 核心工作流

| 工作流 | 入口 | 输出 / 作用 |
|:---|:---|:---|
| Zotero 引用同步 | `00-bib-zotero/sync_from_word.py` | 从 Word 引用映射到 LaTeX 友好的引用结构 |
| Zotero 文献质量检查 | `00-bib-zotero/check_bib_quality.py` | 结构化文献质量 findings |
| EndNote 导出预检 | `00-bib-endnote/check_endnote_export.py` | 导入前发现导出文件问题 |
| EndNote 导入 | `00-bib-endnote/import_library.py` | 规范化引用与稳定 `refNNN` ID |
| Word→LaTeX 迁移 | `01-word-to-latex/migrate_project.py` | 结构化迁移报告 |
| LaTeX→Word 导出 | `02-latex-to-word/migrate_project.py` | 审阅友好 `.docx` 与限制摘要 |
| Review package | `03-latex-review-diff/review_diff.py` | review diff、triage、digest 与 TODO 导向 artifact |
| Feedback ingest | `04-word-review-ingest/feedback_ingest.py` | 将有边界反馈归一化成结构化 issue |
| 确定性检查 | `10-check-*` 到 `14-check-*` | 引用、语言、格式、内容和深度语言报告 |
| 编译诊断 | `15-check-compile/check_compile.py` | 从已有 LaTeX 日志生成结构化 findings |
| Readiness gate | `16-check-readiness/check_readiness.py` | 基于已有 artifacts 的 `PASS / WARN / BLOCK` 汇总 |
| 答辩前整理 | `17-defense-pack/*.py` | 大纲、章节要点、图表、候选视觉材料和讲稿备注 |
| 安全修复器 | `20-fix-*` 到 `24-fix-*` | 报告驱动补丁、dry-run 与 review-gated 应用 |
| 规则包工具 | `90-rules/*.py` | 创建、草稿脚手架、lint、completeness、schema、scorecard |

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

# 快速检查示例
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

如果你还没有 LaTeX 基础，建议先阅读：

- [零基础入门教程：先安装 LaTeX，再使用 Thesis Skills](docs/getting-started-zh.md)

### EndNote 接入

```bash
python 00-bib-endnote/check_endnote_export.py \
  --project-root thesis \
  --input refs.xml

python 00-bib-endnote/import_library.py \
  --project-root thesis \
  --input refs.xml \
  --apply
```

### Zotero 同步 + 检查 + 修复循环

```bash
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file thesis.docx \
  --apply

python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

python run_fix_cycle.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --apply false
```

### 编译诊断

```bash
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile
```

定位说明：

- 编译解析会把已有 LaTeX 日志转换成结构化 findings
- 它不是 TeX 工具链替代品，也不承诺完整编译编排
- 如果没有可用 `.log` 文件，runner 会显式报告，而不是静默跳过或崩溃

### LaTeX 到 Word 审阅导出

```bash
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply false
```

定位说明：

- `review-friendly` 是当前一等支持的导出 profile
- 更严格的 submission-friendly 导出仍属于后续路径
- 不支持或有降级风险的构造要显式报告，不做隐式承诺

### 审阅闭环

```bash
python 03-latex-review-diff/review_diff.py \
  --project-root thesis

python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json
```

定位说明：

- 审阅闭环是面向 revision round 的有边界 workflow，不是协作文档平台
- diff/triage 和 feedback ingest 都保留显式 JSON artifact
- 含糊或高判断成本的修改保持 review-gated，不会静默自动应用

### 预提交 Gate

```bash
python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

定位说明：

- gate 汇总已有报告和 workflow artifact
- 它输出 `PASS`、`WARN` 或 `BLOCK`，并列出 blockers、warnings、next actions 和来源
- 它不会替你重跑整条流程、不会自动修复问题，也不会声称自己能覆盖所有提交规则
- `run_check_once.py` 也可以在 `run-summary.json` 里暴露 `derived_artifacts.readiness_gate`

### 答辩前整理

```bash
python 17-defense-pack/generate_outline.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

python 17-defense-pack/generate_figure_inventory.py \
  --project-root thesis \
  --ruleset tsinghua-thesis
```

定位说明：

- 答辩前整理脚本生成有边界的准备材料，不生成最终 PPT
- 输出是可编辑的大纲、摘要、清单、候选项和备注
- 系统不会替你决定最终讲述策略或设计 PPT 页面

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

从启动包创建自定义规则包：

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "我的大学论文" \
  --starter university-generic \
  --kind university-thesis
```

从 intake 元数据创建草稿规则包：

```bash
python 90-rules/create_draft_pack.py \
  --intake adapters/intake/example-intake.json
```

当前规则包合同文档：

- `90-rules/THESIS_RULE_PACKS.md`
- `90-rules/STARTER_PACK_BASELINE.md`
- `90-rules/MIXED_PACK_WORKFLOWS.md`

信任或分享一个规则包前，先跑 lint：

```bash
python 90-rules/lint_pack.py --pack-path 90-rules/packs/university-generic
```

当前 linter 会检查并输出：

- 必需文件：`pack.yaml`、`rules.yaml`、`mappings.yaml`
- `pack.yaml` 的基线元数据完整性
- `rules.yaml` 的必需顶层 section：`project`、`reference`、`language`
- 当前接受的 `mappings.yaml` 形态：
  - starter-pack 形态：`mappings`
  - draft-pack 形态：`source_template_mappings` + `chapter_role_mappings`
- scorecard：required files、metadata completeness、baseline completeness、schema consistency、overall status 和 finding counts

---

## 当前边界

| 不支持 / 不承诺 | 当前定位 |
|:---|:---|
| 完整 GUI 或 Web 编辑器 | 仓库当前是 CLI-first |
| 完整编译编排 | 解析已有日志，不替代 TeX 工具链 |
| 覆盖所有学校规则 | 规则包编码 policy，但机构规则仍需要人工确认 |
| 自动理解导师真实意图 | Feedback ingest 有边界，并保持 review-gated |
| AI 生成论文正文 | 系统检查、整理和修复有边界问题，不替你写论文 |
| 自动生成最终答辩 PPT | 答辩前整理只生成给人修改的准备材料 |
| 正式规则包 registry | 当前是本地、Git-tracked 或 handoff-oriented workflow |

---

## 技术架构

```text
thesis-skills/
├── core/                   # 共享实现
├── 00-bib-*/               # 文献库工作流
├── 01-word-to-latex/       # 迁移工作流
├── 02-latex-to-word/       # 审阅优先导出工作流
├── 03-latex-review-diff/   # 审阅包与分诊工作流
├── 04-word-review-ingest/  # 有边界反馈归一化工作流
├── 10-check-*/             # 确定性检查器
├── 15-check-compile/       # 编译日志诊断翻译层
├── 16-check-readiness/     # 有边界预提交 readiness gate
├── 17-defense-pack/        # 有边界答辩前整理 artifact 生成器
├── 20-fix-*/               # 安全修复器
├── 90-rules/               # 规则包系统
└── 99-runner/              # 入口点
```

更完整的层次说明见 [`docs/architecture.md`](docs/architecture.md)。

---

## 版本历史

| 版本 | 主题 |
|:---|:---|
| v0.3.0 | 公开仓库重组、双语 README、CI、Zotero 主路径 |
| v0.4.0 | EndNote XML/RIS/BibTeX 导入、DOI 去重、`refNNN` 稳定性 |
| v0.5.x | 确定性语言检查、深度语言审阅和选择性补丁预览 |
| v0.6.0 | 审阅友好 LaTeX→Word 导出、编译日志解析、审阅闭环 |
| v0.7.x | Readiness gate、审阅摘要硬化、feedback ingest 校准 |
| v0.8.x | 答辩前整理、静态 showcase、规则包 lint/completeness/schema/scorecard 硬化 |
| v1.0.0 | README、roadmap、site、manifest、规则包文档与实际代码路径对齐的稳定公开叙事 |

当前稳定化清单见 [`docs/roadmap.md`](docs/roadmap.md)。

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
