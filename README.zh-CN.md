# Thesis Skills

面向论文与期刊投稿场景的 `Python + Skills` 工作流仓库。

它不是一个“只会给建议的提示词集合”，而是一套可执行、可验证、可复用的学术写作基础设施：

- 输入侧支持 `Word -> LaTeX` 迁移
- 检查侧支持引用、语言、格式、结构的确定性校验
- 修复侧支持基于报告的最小修复
- 规则侧支持学校/期刊规则包复用
- 接入侧支持从上传材料生成 draft pack

如果你正在处理以下问题，这个项目就是为你准备的：

- 已经在 Word 里写了很多内容，想迁到 LaTeX
- 学校或期刊有模板，但没有一套稳定的检查闭环
- 想把“格式规范”从人工记忆变成可运行规则
- 想让 AI 辅助论文工作，但不希望它随意改写正文内容

对应英文版见 `README.md`。

## 项目介绍

`thesis-skills` 的核心目标，是把学术写作里最容易反复出错、但又最适合程序化处理的部分沉淀成可执行流程。

这套项目把整个流程拆成四层：

1. `输入/迁移层`：接收 Word 导出内容、参考文献导出文件、模板材料
2. `规则层`：把学校/期刊规范编码成 YAML rule packs
3. `检查层`：用确定性 checker 输出 JSON 报告
4. `修复层`：根据报告做最小修复，而不是“全文重写”

所以它的定位不是“论文生成器”，而是：

- 论文迁移助手
- 模板接入助手
- 学位论文/期刊投稿质量门控工具
- AI 协作时代的学术写作基础设施

## 项目优势

### 1. 不是只靠提示词，而是可执行闭环

很多“AI 论文辅助”方案停留在提示词层，换一个模型、换一次上下文，结果就会漂。`thesis-skills` 的优势是把关键流程落成了 runner、checker、fixer 和规则包，因此行为更稳定、结果更可复现。

### 2. 把 AI 擅长和程序擅长的部分分开

- 规则判断、文件发现、报告输出由 Python 负责
- 解释、决策辅助、最小修改建议由 Skills/AI 协作负责

这样既减少幻觉，也减少机械劳动。

### 3. 支持学校/期刊复用，而不是只服务单一模板

当前仓库以清华 `thuthesis` 思路为起点，但结构已经升级为通用规则包架构：

- `tsinghua-thesis`
- `university-generic`
- `journal-generic`

后续接入别的学校或期刊，不需要重写整套程序，只需要新增或修订 pack。

### 4. 迁移和规范接入边界清晰

`01-word-to-latex` 只负责把资产送入 LaTeX 项目；`90-rules` 只负责定义规范；`run_check_once.py` 和 `run_fix_cycle.py` 只负责消费项目与规则。这种分层可以显著降低项目复杂度。

### 5. 对新手友好，但不牺牲工程化

用户可以先用一键命令跑起来，不需要先理解内部 Python 结构；但对高级用户来说，仓库内部又保留了足够清晰的模块边界，便于扩展、测试和维护。

## 技术路线图

下面是当前这版项目的技术路线：

```text
上传材料 / 现有项目
    |
    |-- Word 导出 TeX / 章节文本 / .bib
    |-- 官方指南 PDF/HTML
    |-- 官方模板 DOCX / DOTX / CLS / STY / TEX
    |-- 合规样例 PDF 或源码
    v
adapters/intake/
    |
    |-- example-intake.json
    |-- migration.json
    v
01-word-to-latex/migrate_project.py
    |
    |-- document_metadata
    |-- word_style_mappings
    |-- chapter_role_mappings
    |-- chapter_mappings / bibliography_mappings
    v
目标 LaTeX 项目
    |
    +--> run_check_once.py
           |
           |-- 00-bib-zotero/check_bib_quality.py
           |-- 10-check-references/check_references.py
           |-- 11-check-language/check_language.py
           |-- 12-check-format/check_format.py
           |-- 13-check-content/check_content.py
           v
         JSON reports
           |
           +--> run_fix_cycle.py
                  |
                  |-- 20-fix-references/fix_references.py
                  |-- 21-fix-language-style/fix_language_style.py
                  |-- 22-fix-format-structure/fix_format_structure.py
                  v
                最小修复结果

同时：

上传材料元数据
    v
90-rules/create_draft_pack.py
    v
90-rules/packs/<ruleset>/
    |
    |-- pack.yaml
    |-- rules.yaml
    |-- mappings.yaml
    |-- draft-notes.md
```

## 仓库结构

```text
thesis-skills/
├── 00-bib-zotero/              # Zotero 导出文献预检查
├── 00-bib-endnote/             # EndNote 文献导出流程说明
├── 01-word-to-latex/           # Word -> LaTeX 迁移入口
├── 10-check-references/        # 引用完整性检查
├── 11-check-language/          # 中英混排、标点、弱表达检查
├── 12-check-format/            # 图表、交叉引用、结构检查
├── 13-check-content/           # 内容结构与摘要元数据检查
├── 20-fix-references/          # 基于 report 的引用修复
├── 21-fix-language-style/      # 基于 report 的语言修复
├── 22-fix-format-structure/    # 基于 report 的格式修复
├── 90-rules/                   # 学校/期刊规则包与生成器
├── 99-runner/                  # runner 说明
├── adapters/intake/            # 用户上传材料和 intake 规范
├── core/                       # 核心执行逻辑
├── examples/                   # 最小样例与迁移示例
├── tests/                      # 回归测试
├── run_check_once.py           # 一键检查
└── run_fix_cycle.py            # 一键修复循环
```

## 快速开始

### 1. 对现有 LaTeX 项目做一轮检查

```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
```

### 2. 根据检查报告做最小修复预览

```bash
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
```

### 3. 从上传材料元数据生成 draft pack

```bash
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
```

### 4. 把 Word/intake 资产导入 LaTeX 项目

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## 增强版 intake 规范

当前版本的 `migration.json` 已经支持更强的结构化字段：

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- `chapter_mappings`
- `bibliography_mappings`

一个典型示例：

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

这使得迁移步骤不再只是“复制文件”，而是能显式保留 Word 样式意图、章节逻辑角色和文献来源信息。

## 适配其他学校或期刊

这套项目已经不再局限于清华模板。对其他学校/期刊，建议用户准备这些材料：

- 官方写作指南：`PDF / HTML / 纯文本`
- 官方模板：`DOCX / DOTX / CLS / STY / TEX`
- 至少 1 份合规样例：`PDF` 或源码
- 可选样式文件：`BST / BBX / CBX / CSL`
- 可选截图：题名页、摘要页、图表页、参考文献页

如果想快速开始：

- 学校论文从 `90-rules/packs/university-generic/` 起步
- 期刊模板从 `90-rules/packs/journal-generic/` 起步

## 主流模板链接

这些链接适合作为“先下载模板，再接入 thesis-skills”的起点。使用前仍建议以学校或期刊的官方指南为准。

### 中国高校

- 清华大学：`tuna/thuthesis` - https://github.com/tuna/thuthesis
- 上海交通大学：`sjtug/SJTUThesis` - https://github.com/sjtug/SJTUThesis
- 中国科学技术大学：`ustctug/ustcthesis` - https://github.com/ustctug/ustcthesis
- 电子科技大学：`tinoryj/UESTC-Thesis-Latex-Template` - https://github.com/tinoryj/UESTC-Thesis-Latex-Template
- 中国科学院大学：`mohuangrui/ucasthesis` - https://github.com/mohuangrui/ucasthesis
- 北京大学：`CasperVector/pkuthss`，也可参考维护中的 fork，如 `Thesharing/pkuthss`

### 国际高校

- Stanford University：`dcroote/stanford-thesis-example` - https://github.com/dcroote/stanford-thesis-example
- University of Cambridge：`cambridge/thesis` - https://github.com/cambridge/thesis
- University of Oxford：`mcmanigle/OxThesis` - https://github.com/mcmanigle/OxThesis
- EPFL：`HexHive/thesis_template` - https://github.com/HexHive/thesis_template
- ETH Zurich：`tuxu/ethz-thesis` - https://github.com/tuxu/ethz-thesis
- MIT（社区广泛使用，非官方）：`alinush/mit-thesis-template` - https://github.com/alinush/mit-thesis-template

## 当前版本的完成度

当前仓库已经具备：

- 可运行的 `check -> fix` 闭环
- 可运行的 `Word -> LaTeX` 迁移入口
- 可运行的 `uploaded materials -> draft pack` 规则包脚手架
- 可复用的 `tsinghua-thesis / university-generic / journal-generic` starter packs
- 覆盖关键流程的测试集合

## 项目定位总结

一句话概括：

`thesis-skills` 不是“帮你写论文”的 AI 工具，而是“帮你把论文迁移、规范、检查、修复、适配流程工程化”的 AI + Python 协作基础设施。
