# Thesis Skills

面向论文和期刊投稿的确定性技能仓库：保留 `Python + Skills` 主线，提供一键检查、一键修复循环、真实 YAML 规则包，以及面向其他学校/期刊的适配入口。

## 快速开始

```bash
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
python run_fix_cycle.py --project-root examples/minimal-latex-project --ruleset university-generic --apply false
python 90-rules/create_pack.py --pack-id my-university --display-name "My University Thesis" --starter university-generic --kind university-thesis
python 90-rules/create_draft_pack.py --intake adapters/intake/example-intake.json
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

## 目录说明

- `00-bib-zotero/`、`00-bib-endnote/`、`01-word-to-latex/`：输入/迁移侧技能
- `10-check-*`：确定性 checker，只产出 report
- `20-fix-*`：读取 report 做最小修复
- `90-rules/packs/`：学校与期刊规则包
- `adapters/intake/`：新学校/期刊接入时应上传什么
- `examples/minimal-latex-project/`：本地闭环验证样例

## 新增的接入辅助工具

- `90-rules/create_pack.py`：从 starter pack 一键生成新的学校或期刊规则包
- `90-rules/create_draft_pack.py`：直接根据上传材料元数据生成 draft pack
- `01-word-to-latex/migrate_project.py`：按显式映射把 intake 资产导入目标 LaTeX 项目
- `adapters/intake/README.md`：说明新接入方应上传哪些材料

增强后的 migration intake 规范已经支持：

- `document_metadata`
- `word_style_mappings`
- `chapter_role_mappings`
- 显式 `chapter_mappings` 与 `bibliography_mappings`

## 模板链接

下面这些仓库适合做“先下载模板，再接入 thesis-skills”的跳转入口。使用前仍建议以学校或期刊官方写作指南为准。

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

## 面向其他学校或期刊

建议用户至少上传：

- 官方写作指南 `PDF/HTML/纯文本`
- 官方模板 `DOCX/DOTX` 或 `CLS/STY/TEX`
- 1 份合规样例 `PDF` 或源码
- 可选样式文件：`BST/BBX/CBX/CSL`

然后从这两个 starter pack 复制一份开始：

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`
