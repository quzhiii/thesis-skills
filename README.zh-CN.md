# Thesis Skills v1.2.0

> 面向论文和期刊投稿的确定性技能仓库：保留 `Python + Skills` 主线，提供一键检查、一键修复循环、真实 YAML 规则包，以及面向其他学校/期刊的适配入口。

## 为什么需要 Thesis Skills？

### 痛点 1：Word → LaTeX 转换时文献引用混乱

**问题**：在 Word 中用 Zotero 写论文，需要转换为 LaTeX 格式时：
- Zotero 的 citation-key（如 `WuZeXinZhongYiYouShiBingZhongNaRuDRGDIPFuFeiGuiFanFenXia`）在 LaTeX 中无法使用
- 需要手动映射为 `ref001, ref002, ...`，工作量大且容易出错
- 每次在 Word 中修改引用，都要重新同步到 LaTeX

**解决方案**：Thesis Skills v1.2.0 新增 Zotero 同步功能
- 自动从 Word docx 中提取 Zotero 引用（解析内嵌的 CSL_CITATION JSON）
- 自动创建 Zotero key ↔ LaTeX ref 的映射
- 增量更新：只处理新增/删除的引用，不用重新生成整个参考文献

```bash
# 从 Word 同步引用到 LaTeX
python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx --apply
```

### 痛点 2：文献引用编号不稳定

**问题**：当 Word 中删除某个引用时：
- 如果直接删除对应的 bib 条目，后续所有引用编号都会改变
- 例如：删除 ref005 后，ref006 变成 ref005，所有 `\cite{ref006}` 都要修改

**解决方案**：Citation Lock 机制
- 生成 `citation-lock.tex`，用 `\nocite{}` 锁定所有引用编号
- 删除引用时保留 bib 条目（只是不在文中出现）
- 引用编号始终保持稳定

```latex
% citation-lock.tex 自动生成
\nocite{ref001,ref002,ref003,...}
```

### 痛点 3：不同学校/期刊格式要求不同

**问题**：每个学校、期刊都有自己的格式规范：
- 参考文献格式（作者名格式、年份位置等）
- 章节结构要求
- 图表编号和引用规则

**解决方案**：YAML 规则包系统
- 规则用 YAML 定义，易读易改
- 提供 Starter Pack（university-generic、journal-generic）
- 一键生成新学校的规则包

```bash
# 从 Starter Pack 创建新学校规则包
python 90-rules/create_pack.py --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis
```

### 痛点 4：检查和修复流程不清晰

**问题**：传统 LaTeX 项目：
- 编译错误信息难以理解
- 不知道哪些地方不符合格式要求
- 修复后需要重新编译检查

**解决方案**：确定性检查 + 安全修复
- 检查器输出 JSON 报告，清晰列出所有问题
- 修复器读取报告，做最小化修改
- 一键运行，支持 dry-run 预览

```bash
# 一键检查（跳过编译）
python run_check_once.py --project-root thesis --ruleset tsinghua-thesis --skip-compile

# 一键修复循环（dry-run 预览）
python run_fix_cycle.py --project-root thesis --ruleset tsinghua-thesis --apply false
```

## 使用场景

### 场景 1：在 Word 中写论文，需要转换为 LaTeX

```bash
# 1. 从 Word 同步 Zotero 引用到 LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis \
  --word-file 论文初稿.docx \
  --apply

# 2. 运行检查
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile

# 3. 查看报告
cat thesis/reports/sync_from_word-report.json
cat thesis/reports/run-summary.json
```

### 场景 2：已有 LaTeX 项目，需要适配新学校格式

```bash
# 1. 创建新学校的规则包
python 90-rules/create_pack.py \
  --pack-id peking-thesis \
  --display-name "Peking University Thesis" \
  --starter university-generic \
  --kind university-thesis

# 2. 编辑 90-rules/packs/peking-thesis/rules.yaml
# 3. 运行检查
python run_check_once.py \
  --project-root thesis \
  --ruleset peking-thesis \
  --skip-compile
```

### 场景 3：Word → LaTeX 完整迁移

```bash
# 1. 准备迁移规范
cat > migration.json << EOF
{
  "document_metadata": {
    "source_format": "word-exported-tex",
    "bibliography_source": "zotero"
  },
  "chapter_mappings": [
    {"from": "chapters/chapter1.tex", "to": "chapters/01-introduction.tex"}
  ],
  "bibliography_mappings": [
    {"from": "refs.bib", "to": "ref/refs.bib"}
  ]
}
EOF

# 2. 执行迁移（dry-run）
python 01-word-to-latex/migrate_project.py \
  --source-root intake \
  --target-root thesis \
  --spec migration.json \
  --apply false

# 3. 确认后应用
python 01-word-to-latex/migrate_project.py \
  --source-root intake \
  --target-root thesis \
  --spec migration.json \
  --apply true
```

## 核心功能

### Zotero 同步（v1.2.0 新增）

```bash
# BibTeX 质量检查
python 00-bib-zotero/check_bib_quality.py --project-root thesis --ruleset tsinghua-thesis

# Word → LaTeX 引用同步
python 00-bib-zotero/sync_from_word.py --project-root thesis --word-file thesis.docx
```

**特性**：
- 从 Word docx 提取 Zotero 引用（CSL_CITATION JSON）
- 维护 Zotero key ↔ LaTeX ref 映射（`ref/citation-mapping.json`）
- 生成引用锁文件（`citation-lock.tex`）
- 检测新增/删除的引用
- 支持 dry-run 预览

### 检查器（10-check-*）

```bash
# 一键运行所有检查
python run_check_once.py --project-root thesis --ruleset tsinghua-thesis
```

**检查项**：
- `10-check-references`：引用完整性检查（缺失的 key、孤立的条目、重复标题）
- `11-check-language`：语言检查（中英文间距、重复标点、混合引号、弱表达）
- `12-check-format`：格式检查（图表目录、图表居中）
- `13-check-content`：内容检查（必需章节、摘要关键词数量）

### 修复器（20-fix-*）

```bash
# 一键修复循环
python run_fix_cycle.py --project-root thesis --ruleset tsinghua-thesis --apply false
```

**特性**：
- 读取检查报告，做最小化修复
- 支持 dry-run 预览
- 生成修复报告

## 规则包系统

### Starter Pack

```bash
90-rules/packs/
├── university-generic/    # 通用大学论文 Starter Pack
├── journal-generic/       # 通用期刊 Starter Pack
└── tsinghua-thesis/       # 清华大学论文 Pack（示例）
```

### 规则包结构

```yaml
# pack.yaml
id: tsinghua-thesis
kind: university-thesis
display_name: Tsinghua Graduate Thesis Pack
version: 1
precedence: guide_over_template
starter: false

# rules.yaml（部分示例）
project:
  main_tex_candidates: [thuthesis-example.tex, thesis.tex, main.tex]
  chapter_globs: [chapters/*.tex, data/chap*.tex]
  bibliography_files: [ref/refs.bib, ref/refs-import.bib]

reference:
  missing_key:
    severity: error
  orphan_entry:
    severity: warning

language:
  cjk_latin_spacing:
    enabled: true
    severity: warning
  weak_phrases:
    enabled: true
    severity: info
    patterns: [众所周知, 不难看出, 本文将]
```

### 创建新规则包

```bash
# 方法 1：从 Starter Pack 创建
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "My University Thesis" \
  --starter university-generic \
  --kind university-thesis

# 方法 2：从上传材料生成 Draft Pack
python 90-rules/create_draft_pack.py \
  --intake adapters/intake/example-intake.json
```

## 为其他学校/期刊创建规则包

建议用户至少上传：

- **官方写作指南**：`PDF`/`HTML`/纯文本
- **官方模板**：`DOCX`/`DOTX` 或 `CLS`/`STY`/`TEX`
- **合规样例**：1 份 `PDF` 或源码
- **可选样式文件**：`BST`/`BBX`/`CBX`/`CSL`

然后从这两个 Starter Pack 复制一份开始：

- `90-rules/packs/university-generic/`
- `90-rules/packs/journal-generic/`

详细指南：`adapters/intake/README.md`

## 技术架构

Thesis Skills 采用模块化设计：

```
thesis-skills/
├── core/                    # 核心模块
│   ├── zotero_extract.py   # Zotero 引用提取
│   ├── citation_mapping.py # 引用映射管理
│   ├── project.py          # 项目发现
│   └── reports.py          # 报告生成
├── 00-bib-zotero/          # Zotero 工作流
│   ├── check_bib_quality.py
│   └── sync_from_word.py
├── 01-word-to-latex/       # Word 迁移工作流
│   └── migrate_project.py
├── 10-check-*/             # 确定性检查器
├── 20-fix-*/               # 安全修复器
├── 90-rules/               # 规则包系统
│   ├── create_pack.py
│   ├── create_draft_pack.py
│   └── packs/              # 学校/期刊规则包
├── adapters/intake/        # 接入指南
├── run_check_once.py       # 一键检查
├── run_fix_cycle.py        # 一键修复
└── examples/               # 示例项目
```

**工作流程**：

```
Word (Zotero) → [sync_from_word.py] → LaTeX Project
                                          ↓
                                    [run_check_once.py]
                                          ↓
                                      JSON Reports
                                          ↓
                                    [run_fix_cycle.py]
                                          ↓
                                      Fixed LaTeX
```

详细技术文档：`docs/architecture.md`

## 模板链接

下面这些仓库适合做"先下载模板，再接入 thesis-skills"的跳转入口。使用前仍建议以学校或期刊官方写作指南为准。

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

## 快速开始

```bash
# 克隆项目
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills

# 运行示例
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

## 许可证

MIT License
