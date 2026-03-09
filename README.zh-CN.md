# Thesis Skills

`Thesis Skills` 是一个面向论文写作、期刊投稿、模板接入与 `Word -> LaTeX` 迁移的 `Python + Skills` 工作流仓库。

它不是“提示词集合”，而是一套可执行、可验证、可复用的学术写作基础设施：把学术规范转成确定性检查、报告驱动修复，以及可复用的规则包。

## 目录

- [项目概览](#项目概览)
- [为什么要做这个项目](#为什么要做这个项目)
- [项目优势](#项目优势)
- [技术路线图](#技术路线图)
- [常见使用场景](#常见使用场景)
- [仓库结构](#仓库结构)
- [快速开始](#快速开始)
- [增强版 Intake 规范](#增强版-intake-规范)
- [适配其他学校与期刊](#适配其他学校与期刊)
- [主流模板链接](#主流模板链接)
- [详细架构文档](#详细架构文档)
- [当前状态](#当前状态)

## 项目概览

`thesis-skills` 聚焦于学术写作中最容易反复出错、但又最适合程序化处理的部分。

它提供：

- `Word -> LaTeX` 迁移助手
- 面向引用、语言、格式、内容结构的确定性 checker
- 基于 JSON report 的安全 fixer，而不是自由发挥式全文改写
- 面向学校与期刊的 YAML 规则包
- 基于上传材料元数据生成 draft pack 的脚手架

因此，这个仓库更适合被理解为：

- 论文迁移助手
- 模板接入工具包
- 学位论文 / 期刊投稿质量门控工具
- AI + Python 协作的学术写作基础设施层

## 为什么要做这个项目

很多 AI 写作辅助方案停留在“提示词”层。它们适合 brainstorming，但在学校模板、期刊规范、长周期论文维护这种强约束场景里，稳定性往往不够。

这个项目的目标，就是把能编码的部分编码，把不该完全交给模型的部分从模型手里拿出来：

1. Python 负责确定性扫描、文件发现、规则判断和报告输出。
2. Skills 负责流程编排、解释、辅助决策和最小修改协作。
3. Rule packs 负责承载学校 / 期刊的具体要求。

这样就不需要让模型“记住整本写作指南”，而是把规范沉淀为可重复执行的流程。

## 项目优势

### 1. 不是只靠提示词，而是可执行闭环

核心流程是代码，不是想象：`run_check_once.py`、`run_fix_cycle.py`、deterministic checkers 和 rule packs 组成了真正可执行的主链路，因此结果更稳定，也更容易验证。

### 2. 把 AI 擅长和程序擅长的部分分开

- Python 负责扫描、匹配、规则判断、报告输出
- Skills / AI 负责解释、迁移辅助和最小修改建议

这样既减少幻觉，也减少机械劳动。

### 3. 不只服务一个学校模板

当前 starter packs 已经包含：

- `tsinghua-thesis`
- `university-generic`
- `journal-generic`

所以它已经不是“清华专用工具”，而是一个可扩展到其他高校、院系和期刊的规则包架构。

### 4. 迁移与规范边界清晰

`01-word-to-latex` 只负责迁移资产；`90-rules` 只负责定义规范；`run_check_once.py` 与 `run_fix_cycle.py` 只负责消费项目状态与规则。这种边界能显著降低复杂度。

### 5. 对新手友好，但仍保留工程质量

新用户可以直接跑一键命令；高级用户和贡献者则能看到清晰的模块、测试、starter packs 和 intake contracts，便于维护和扩展。

## 技术路线图

```text
上传材料或现有 LaTeX 项目
    |
    +-- 官方指南 / 模板 / 合规样例 / 文献导出文件
    v
adapters/intake/
    |
    +-- example-intake.json
    +-- migration.json
    v
01-word-to-latex/migrate_project.py
    |
    +-- document_metadata
    +-- word_style_mappings
    +-- chapter_role_mappings
    +-- chapter_mappings
    +-- bibliography_mappings
    v
目标 LaTeX 项目
    |
    +-- run_check_once.py
           |
           +-- 00-bib-zotero/check_bib_quality.py
           +-- 10-check-references/check_references.py
           +-- 11-check-language/check_language.py
           +-- 12-check-format/check_format.py
           +-- 13-check-content/check_content.py
           v
         JSON reports
           |
           +-- run_fix_cycle.py
                  |
                  +-- 20-fix-references/fix_references.py
                  +-- 21-fix-language-style/fix_language_style.py
                  +-- 22-fix-format-structure/fix_format_structure.py
                  v
                最小修复结果

上传材料元数据
    |
    +-- pack_id / display_name / starter / sources / mappings
    v
90-rules/create_draft_pack.py
    v
90-rules/packs/<ruleset>/
    |
    +-- pack.yaml
    +-- rules.yaml
    +-- mappings.yaml
    +-- draft-notes.md
```

## 常见使用场景

### 1. 你已经有 Word 草稿

- 整理章节资产和参考文献导出文件
- 编写 `migration.json`
- 运行 `01-word-to-latex/migrate_project.py`
- 再运行 `run_check_once.py` 和 `run_fix_cycle.py`

### 2. 你已经有 LaTeX 项目

- 选择现有 pack，例如 `university-generic` 或 `tsinghua-thesis`
- 运行 `run_check_once.py`
- 阅读生成的 reports
- 用 `run_fix_cycle.py` 做安全、最小的修复

### 3. 你要接入新的学校或期刊

- 收集官方指南、模板、合规样例
- 填写 `adapters/intake/example-intake.json` 一类元数据
- 运行 `90-rules/create_draft_pack.py`
- 基于样例项目继续修订生成的 pack

## 仓库结构

```text
thesis-skills/
├── 00-bib-zotero/              # Zotero 文献预检查
├── 00-bib-endnote/             # EndNote 文献流程说明
├── 01-word-to-latex/           # Word -> LaTeX 迁移入口
├── 10-check-references/        # 引用完整性检查
├── 11-check-language/          # 语言与中英混排检查
├── 12-check-format/            # 图表、格式、交叉引用检查
├── 13-check-content/           # 内容结构检查
├── 20-fix-references/          # 基于 report 的引用修复
├── 21-fix-language-style/      # 基于 report 的语言修复
├── 22-fix-format-structure/    # 基于 report 的格式修复
├── 90-rules/                   # 规则包与 pack 生成器
├── 99-runner/                  # runner 文档
├── adapters/intake/            # 用户上传材料与 intake 元数据
├── core/                       # 确定性核心逻辑
├── docs/                       # 架构与补充说明文档
├── examples/                   # 最小可运行示例
├── tests/                      # 回归测试
├── run_check_once.py           # 一键检查
└── run_fix_cycle.py            # 一键修复
```

## 快速开始

### 运行一轮完整的确定性检查

```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
```

### 根据 report 预览最小修复

```bash
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
```

### 根据上传材料元数据生成 draft pack

```bash
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
```

### 把 intake 资产迁入目标 LaTeX 项目

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## 增强版 Intake 规范

当前 `migration.json` 已经支持结构化字段，而不只是文件复制列表。

支持的顶层字段包括：

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- `chapter_mappings`
- `bibliography_mappings`

示例：

```json
{
  "document_metadata": {
    "source_format": "word-exported-tex",
    "bibliography_source": "zotero",
    "template_family": "university-generic"
  },
  "word_style_mappings": [
    {"style": "Heading 1", "role": "chapter", "latex_command": "chapter"},
    {"style": "Heading 2", "role": "section", "latex_command": "section"}
  ],
  "chapter_role_mappings": [
    {"source": "chapters/chapter1.tex", "role": "introduction", "target": "chapters/01-introduction.tex"}
  ],
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex", "role": "introduction", "word_style": "Heading 1"}
  ],
  "bibliography_mappings": [
    {"from": "refs-import.bib", "to": "ref/refs-import.bib"}
  ]
}
```

这意味着迁移步骤不再只是“复制文件”，而是能显式保留 Word 样式意图、章节逻辑角色和文献来源语义。

## 适配其他学校与期刊

如果要接入其他学校或期刊，建议准备这些材料：

- 官方写作指南：`PDF`、`HTML` 或纯文本
- 官方模板：`DOCX`、`DOTX`、`CLS`、`STY`、`TEX`
- 至少一份合规样例：优先源码，否则 `PDF`
- 可选样式文件：`BST`、`BBX`、`CBX`、`CSL`
- 可选截图：题名页、摘要页、图表页、参考文献页

推荐起点：

- 学位论文从 `90-rules/packs/university-generic/` 开始
- 期刊模板从 `90-rules/packs/journal-generic/` 开始

## 主流模板链接

这些仓库适合作为“先下载模板，再接入 thesis-skills”的跳转入口。实际使用时仍建议以学校或期刊官方规范为准。

### 中国高校

- 清华大学：`tuna/thuthesis` - https://github.com/tuna/thuthesis
- 上海交通大学：`sjtug/SJTUThesis` - https://github.com/sjtug/SJTUThesis
- 中国科学技术大学：`ustctug/ustcthesis` - https://github.com/ustctug/ustcthesis
- 电子科技大学：`tinoryj/UESTC-Thesis-Latex-Template` - https://github.com/tinoryj/UESTC-Thesis-Latex-Template
- 中国科学院大学：`mohuangrui/ucasthesis` - https://github.com/mohuangrui/ucasthesis
- 北京大学：`CasperVector/pkuthss`，以及维护中的 fork，如 `Thesharing/pkuthss`

### 国际高校

- Stanford University：`dcroote/stanford-thesis-example` - https://github.com/dcroote/stanford-thesis-example
- University of Cambridge：`cambridge/thesis` - https://github.com/cambridge/thesis
- University of Oxford：`mcmanigle/OxThesis` - https://github.com/mcmanigle/OxThesis
- EPFL：`HexHive/thesis_template` - https://github.com/HexHive/thesis_template
- ETH Zurich：`tuxu/ethz-thesis` - https://github.com/tuxu/ethz-thesis
- MIT（社区常用，非官方）：`alinush/mit-thesis-template` - https://github.com/alinush/mit-thesis-template

## 详细架构文档

如果你想看更完整的 runner 设计、规则包结构、pack 生命周期以及 check/fix 时序，请查看 `docs/architecture.md`。

## 当前状态

当前仓库已经具备：

- 可运行的 `check -> fix` 主闭环
- 可运行的 `Word -> LaTeX` 迁移入口
- 可运行的 `uploaded materials -> draft pack` 脚手架链路
- `tsinghua-thesis`、`university-generic`、`journal-generic` 三个 starter packs
- 覆盖主流程的回归测试集合

一句话总结：

`thesis-skills` 不是“帮你写论文”的 AI 工具，而是一个把迁移、规范、检查、修复、接入流程工程化的 AI + Python 协作基础设施。
