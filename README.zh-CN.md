# Thesis LaTeX Skills

![Python](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

> **Word → LaTeX 迁移，不再掉坑。**
> 确定性 AI Skill 流水线，专为 LaTeX 学位论文质检设计——引用完整性、中文语言规范、格式验证、Zotero 文献清洗。无幻觉，不改内容，只输出精确的问题报告。

[English README](README.md)

---

## 为什么做这个

大多数研究生一开始并不会用 LaTeX 写论文。Word 更熟悉，上手快，改起来方便——直到某天发现学校要求提交符合 [`thuthesis`](https://github.com/tuna/thuthesis) 模板的 LaTeX 版本，或者 Word 排版根本达不到提交标准。

从 Word 切换到 LaTeX 是一场迁移战：参考文献引用键断掉、交叉引用找不到、中英文标点混用、图表标签丢失、bib 文件缺少 GB7714-2015 要求的 `langid` 和必填字段……这些问题不会主动报错，只会在最后关头集中爆发。

**Thesis LaTeX Skills** 是一套为 Word→LaTeX 迁移场景专门设计的 AI Skill 流水线。无论你正处于迁移中，还是已经在用 LaTeX，每个 Skill 模块都对迁移过程中容易积累的机械性问题做确定性检查——引用完整性、Zotero 文献质量、中文语言规范、格式结构完整性——精确报告需要修复的位置，不改动你的研究内容。

首先为**清华大学** `thuthesis` 模板流程构建，可扩展到任何拥有 LaTeX 模板的学校。

---

## 做什么（以及不做什么）

| ✅ 会做 | ❌ 不做 |
|---|---|
| 交叉验证 `\cite{key}` 与 `.bib` 文件 | 生成或改写你的论点 |
| 检测孤立文献条目 | 修改你的研究方法或结论 |
| 检查中文标点与引号风格一致性 | 自动编辑正文段落 |
| 验证图表标签与 `\ref` 完整性 | 默认改写章节内容 |
| 扫描并去重符号与缩略词 | 替代导师的审阅 |
| 检查章节结构完整性 | 对内容质量做主观判断 |
| 通过 YAML 规则集执行学校格式要求 | 处理非 LaTeX（Word）提交 |

---

## Skill 模块

```
thesis-latex-skills/
├── 00-zotero/      # Zotero/EndNote → .bib 导出与质量检查（在 01-migrate 之前运行）
├── 01-migrate/     # Word → LaTeX 迁移工作流
├── 02-content/     # 结构、摘要、符号/缩略词检查
├── 03-references/  # 引用完整性与文献库规范
├── 04-language/    # 中文标点与引号风格检查
├── 05-format/      # 图、表、公式、交叉引用验证
└── 06-rules/       # 可插拔 YAML 规则集（内置清华规则，支持自定义扩展）
```

### `00-zotero` — Zotero/EndNote `.bib` 导出与质量检查

如果你在 Word 中使用 **Zotero**（或 EndNote）插入参考文献，在运行 `01-migrate` **之前**先运行此 Skill。它验证从文献管理工具导出的 `.bib` 文件，在进入后续流程前捕捉错误。检查项目包括：缺失 `langid` 字段（GB7714-2015 / ThuThesis 强要求）、必填字段不完整、DOI 格式异常、`.bib` 与 `.tex` 引用键不匹配。

**输入：** `ref/refs-import.bib`（从 Zotero Better BibLaTeX 导出）
**报告：** `00-zotero/check_bib_quality-report.json`

### `01-migrate` — Word → LaTeX 迁移

将 Word 导出的 LaTeX（`from_word_full.tex`）转换为干净的 `thuthesis` 兼容章节结构。将引用标记规范化为 `\cite{...}` 格式，并重新生成清理后的参考文献导入文件。保留所有历史迁移脚本——该 Skill 是编排者，而非替代者。

**关键输出：** `data/chap02.tex` … `data/chap06.tex`，`ref/refs-import.bib`

### `02-content` — 内容结构与符号扫描

检查论文是否具备所需章节流程（问题→方法→结果→讨论→结论），摘要是否在中英文中都包含四个必要要素（目的、方法、结果、结论），以及关键词数量是否在限制内。同时扫描所有章节中的符号/缩略词候选项，去重，标记冲突，并可选地修补 `denotation.tex`。

**两种模式：** `--mode report`（安全，只读）→ `--mode patch`（可选写入）

### `03-references` — 引用完整性

对 `\cite{key}` 调用与 `.bib` 文件进行确定性交叉验证。捕捉：
- **缺失键**（错误）— 文中已引用但 bib 中不存在
- **孤立条目**（警告）— bib 中存在但从未被引用
- **重复标题候选**（警告）— 可能的重复条目
- **引用顺序不单调**（提示）— 数字引用风格违规

### `04-language` — 中文语言风格

检查容易忽略的中文学术写作规范：
- 同一段落中混用中文弯引号与直引号
- 中文与拉丁字符之间缺少空格
- 重复标点异常（`。。`，`，，`）
- 可配置的弱表达检测（"众所周知"、"不难看出"等）

### `05-format` — 结构与交叉引用完整性

验证 LaTeX 源码的机械结构：
- 每个 `\figure` 和 `\table` 环境都有 `\caption` 和 `\label`
- 所有 `\ref{key}` 调用在某处都有匹配的 `\label{key}`
- 长表格延续标记完整（`\endfirsthead`、`\endhead`、`\endfoot`、`\endlastfoot`）
- 主 tex 文件中包含图目录和表目录
- 与现有 `thesis_quality_loop.ps1` 编译闭环集成

### `06-rules` — 可插拔规则集

所有检查器从 `06-rules/rules/<ruleset>/` 下的 YAML 文件读取规则。内置的 `tsinghua` 规则集编码了清华研究生论文要求。添加新学校只需填写四个 YAML 文件：`format.yaml`、`citation.yaml`、`structure.yaml`、`language.yaml`。

---

## 架构与技术栈

```
┌─────────────────────────────────────────────────────┐
│                  AI 编程助手                         │
│         (Claude / OpenCode / Cursor / 等)           │
└────────────────────┬────────────────────────────────┘
                     │  调用 Skill 模块
┌────────────────────▼────────────────────────────────┐
│              run_check_once.py（编排器）             │
│    ┌──────────────────────────────────────────┐     │
│    │  00-zotero（文献预检查）                  │     │
│    ├──────────────────────────────────────────┤     │
│    │  03-references  │  04-language  │  05-format │  │
│    │  02-content     │  （可选编译闭环）        │  │
│    └──────────────────────────────────────────┘     │
│                        │                            │
│                 从以下路径读取规则集                  │
│         06-rules/rules/<ruleset>/*.yaml             │
└────────────────────┬────────────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │  你的 LaTeX 项目       │
         │  (thuthesis 或其他)   │
         └───────────────────────┘
```

**技术栈：**
- Python 3.x 检查器（除标准库外无外部依赖）
- YAML 驱动的规则集配置
- PowerShell 编译闭环（`thesis_quality_loop.ps1`）— 可选，Windows
- 每个检查器输出 JSON 结构化报告
- 退出码约定：`0` 通过 · `1` 质量发现 · `2` 配置错误 · `3` 运行时故障

**Skill 格式：** 兼容 OpenCode / Claude Skill 系统——每个模块随附 `THESIS_*.md` Skill 提示词和对应的 Python 检查器。

---

## 快速开始

### 清华用户（`thuthesis`）

```bash
# 一次性运行所有检查（在本仓库根目录执行）
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

按顺序执行：
1. `00-zotero/check_bib_quality.py` — 文献导出质量（Zotero/langid/DOI）
2. `03-references/check_references.py` — 引用审计
3. `04-language/check_language.py` — 语言风格
4. `05-format/check_structure.py` — 结构完整性
5. `02-content/scan_symbols.py --mode report` — 符号扫描
6. 编译闭环（`thesis_quality_loop.ps1`）— 使用 `--skip-compile` 可跳过

跳过编译（更快，适合迭代检查）：
```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua --skip-compile
```

### 其他学校用户

1. 复制模板规则集：
   ```
   06-rules/rules/custom/template/  →  06-rules/rules/my-university/
   ```
2. 在四个 YAML 文件中填写本校要求。
3. 运行：
   ```bash
   python run_check_once.py --project-root "../your-thesis-project" --rules my-university --skip-compile
   ```

`06-rules/rules/my-university/` 中已提供可直接使用的入门示例。

---

## 路线图

| 版本 | 状态 | 内容 |
|---|---|---|
| **v0.1** | ✅ 已发布 | 7 个 Skill 模块（含 Zotero 文献检查器）、清华规则集、一键运行器 |
| **v0.2** | 🔜 计划中 | `07-literature-review` Skill、`08-reviewer-audit` Skill、整合 `run-summary.json` |
| **未来** | 💡 待办 | 供导师审阅的 LaTeX diff 助手、编译日志解析器、答辩幻灯片导出指引 |

---

## 适用人群

- **清华研究生**，使用 `thuthesis` 写作 — 开箱即用，零配置
- **其他学校学生**，已有 LaTeX 模板 — 填写四个 YAML 文件即可
- **导师和助教**，希望在接收章节草稿前有可复现的质量门控
- **任何人**，希望对 LaTeX 论文进行确定性、无 AI 幻觉的检查

---

## 致谢

基于 TUNA 维护的优秀 [`thuthesis`](https://github.com/tuna/thuthesis) 模板构建。

---

## 许可证

详见 [LICENSE](LICENSE)。第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
