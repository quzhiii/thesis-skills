# Thesis Skills

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

英文说明：[`README.md`](README.md)

`thesis-skills` 是一个面向论文、学位论文和期刊投稿场景的确定性工作流仓库。它把 Python runners、可复用 skills、报告驱动 fixer 和规则包结合起来，让学术写作规范从“参考建议”变成“可执行流程”。

`v0.3.0` 的目标不是堆更多功能，而是把这个仓库整理成一个更适合公开发布、结构更清楚、边界更诚实的 GitHub 项目。

> 如果你要的是给学生直接安装使用的一键 Word 插件，
> 请使用独立仓库：`thu-word-plugin-lite`。

## 为什么做这个仓库

学术写作工具通常会落入两种问题：

- 太依赖人工，流程重复且脆弱
- 太依赖 AI，结果难验证、难复现

`thesis-skills` 选择第三条路：

- 用代码做确定性检查、映射和受约束修复
- 用规则包隔离学校或期刊政策
- 让 AI/skills 留在辅助层，而不是偷偷接管最终结果

它不替代学术判断，但可以显著减少格式、引用、迁移和接入上的重复劳动。

## 项目亮点

- 确定性的 `check -> report -> fix` 闭环
- 显式的 `Word -> LaTeX` 迁移契约
- 面向学校与期刊的可复用规则包
- 读取 report 的安全 fixer，而不是全文自由改写
- 带回归测试的 Zotero / migration 主流程
- 面向 GitHub 公开发布重新整理的中英文文档

## 支持矩阵

| 工作流 | v0.3.0 状态 | 含义 |
|---|---|---|
| Zotero BibTeX 质量检查 | 稳定 | 检查导出的文献条目质量 |
| Zotero Word 引用同步 | 稳定 | 从 Word 提取引用、对比映射、更新 `citation-lock.tex` |
| EndNote 导出接入 | 已支持 | 从 EndNote 导出 BibTeX，规范化后进入同一检查链路 |
| EndNote 直接同步 | 暂未实现 | 本版本不做过度承诺 |
| Word -> LaTeX 迁移 | 稳定 | 基于结构化迁移规范 |
| 确定性 checker | 稳定 | 引用、语言、格式、内容结构 |
| report 驱动 fixer | 稳定 | 最小、机械、可回溯的修复 |
| 规则包生成 | 稳定 | 支持 starter 和 draft-pack 两条路径 |

## v0.3.0 的重点变化

- 把仓库重新整理为“按工作流层次理解”的公开结构
- 保留本地更强的工程实现层（`core/`、`tests/`、fixers、CI）
- 明确把 Zotero 作为当前最强的文献工作流
- 保留 EndNote，但只把它定义为“导出接入链路”
- 补齐公开发布需要的打包与发布元数据

## 最简单的上手方式

### 方案 A：你已经有 LaTeX 项目

```bash
python run_check_once.py --project-root <你的-latex-项目> --ruleset university-generic --skip-compile
python run_fix_cycle.py --project-root <你的-latex-项目> --ruleset university-generic --apply false
```

### 方案 B：你先从 Word 草稿迁移

```bash
python 01-word-to-latex/migrate_project.py --source-root <intake> --target-root <latex-project> --spec <migration.json> --apply false
```

### 方案 C：你要做 Zotero Word 引用同步

```bash
python 00-bib-zotero/sync_from_word.py --project-root <latex-project> --word-file <word.docx>
```

### 方案 D：你要安装本地 skills

```bash
python install_openclaw.py
```

## 工作流分层

### 1. 文献接入层

- `00-bib-zotero/`
- `00-bib-endnote/`
- `core/zotero_extract.py`
- `core/citation_mapping.py`

这一层负责在进入主流程前处理文献质量和引用接入。

### 2. Word-to-LaTeX 迁移层

- `01-word-to-latex/`
- `core/migration.py`
- `adapters/intake/`

迁移是显式的，仓库优先相信结构化映射，而不是猜文件名。

### 3. 确定性检查层

- `run_check_once.py`
- `10-check-references/`
- `11-check-language/`
- `12-check-format/`
- `13-check-content/`

checker 只生成 JSON report，不直接偷偷改项目。

### 4. report 驱动修复层

- `run_fix_cycle.py`
- `20-fix-references/`
- `21-fix-language-style/`
- `22-fix-format-structure/`

fixer 读取 report，只做受约束、最小化的修改。

### 5. 规则包与接入层

- `90-rules/`
- `90-rules/packs/`
- `core/rules.py`
- `core/pack_generator.py`

规范放在 pack 里，而不是散落在脚本里。

## 技术路线图

高层路线图见：[`docs/roadmap.md`](docs/roadmap.md)

详细架构见：[`docs/architecture.md`](docs/architecture.md)

当前的总体方向是：

- 保持顶层目录对用户可理解
- 保持 `core/` 作为可复用实现层
- 先把 Zotero 路径做强
- EndNote 只有在数据契约清楚之后才扩展到直接同步

## 仓库结构

```text
thesis-skills/
├── 00-bib-zotero/              # Zotero 文献接入与同步
├── 00-bib-endnote/             # EndNote 导出接入说明
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
├── adapters/intake/            # intake 元数据与迁移规范
├── core/                       # 可复用的确定性核心逻辑
├── docs/                       # 架构与路线图文档
├── examples/                   # 最小可运行示例
├── tests/                      # 回归测试
├── install_openclaw.py         # 一键安装 skills
├── run_check_once.py           # 一键检查
└── run_fix_cycle.py            # 一键修复
```

## 主要使用场景

### 你已经有论文项目

- 选择规则包，例如 `university-generic` 或 `tsinghua-thesis`
- 运行 `run_check_once.py`
- 查看 JSON report
- 再用 `run_fix_cycle.py` 做最小修复或修复预览

### 你需要从 Word 迁移

- 准备 intake 元数据与迁移规范
- 使用 `01-word-to-latex/migrate_project.py` 导入资产
- 再进入确定性检查和最小修复流程

### 你要规范文献接入

- Zotero：可以做质量检查，也可以做 Word 引用同步
- EndNote：先导出 BibTeX、规范化，再进入同一质量门禁

### 你要适配新的学校或期刊

- 收集官方指南、模板和合规样例
- 用 `90-rules/create_pack.py` 或 `90-rules/create_draft_pack.py`
- 再基于样例项目修订规则包

## 适配其他学校与期刊

建议准备这些输入：

- 官方指南（`PDF`、`HTML` 或纯文本）
- 官方模板（`DOCX`、`DOTX`、`CLS`、`STY`、`TEX`）
- 至少一份合规样例（`PDF` 或源码）
- 可选样式文件（`BST`、`BBX`、`CBX`、`CSL`）
- 可选截图（题名页、图表页、参考文献页）

推荐起点：

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`

## 模板链接

这些仓库适合作为迁移和规则包接入前的跳转入口。实际使用时仍以学校或期刊官方规范为准。

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

## 当前状态

当前仓库已经具备：

- 可运行的 `check -> report -> fix` 闭环
- 可运行的 `Word -> LaTeX` 迁移路径
- Zotero 文献质量检查与引用同步
- EndNote 导出接入说明
- 面向学校和期刊的 starter packs
- 覆盖主要公开工作流的回归测试

一句话总结：

`thesis-skills` 是一个把学术写作迁移、规范检查、最小修复与模板接入工程化的公开工作流仓库。

## 许可证

详见 [LICENSE](LICENSE)。第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
