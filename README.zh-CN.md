# Thesis Skills

![Python](https://img.shields.io/badge/python-3.x-blue?logo=python&logoColor=white)
![License](https://img.shields.io/github/license/quzhiii/thesis-skills)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)

面向 `Word -> LaTeX` 迁移、引用完整性、中文语言规范、格式验证与高校规则包的确定性 thesis workflow 仓库。

[English README](README.md)

> 如果你要的是给学生直接安装使用的一键 Word 插件，
> 请使用独立仓库：`thu-word-plugin-lite`。

---

## 这个仓库是什么

`thesis-skills` 是整个论文工具链里的 **skills 与自动化主线仓库**。

它负责：

- Word 到 LaTeX 的迁移辅助
- 针对引用、语言、结构、格式的确定性检查
- 基于 JSON report 的受约束修复
- 面向学校与期刊的 YAML 规则包
- OpenCode / Claude / OpenClaw 风格的自动化接入

它不是一个“帮你自由改稿”的写作助手，而是一套可验证、可追踪、可复用的工程化工作流。

---

## 它能做什么

| 会做 | 不做 |
|---|---|
| 校验 `\cite{key}` 与 `.bib` 一致性 | 改写你的论证内容 |
| 检测孤立文献条目 | 修改研究方法或结论 |
| 检查中文标点、引号与中英混排 | 自由改写整章正文 |
| 验证图表、标签、交叉引用完整性 | 替代导师审阅 |
| 扫描符号和缩略语 | 判断学术质量高低 |
| 通过 YAML 执行学校规则 | 负责最终 Word 插件分发 |

---

## 仓库边界

当前仓库负责的是 **技术工作流层**：

- migration helpers
- deterministic checkers
- report-driven fixers
- rulesets 与 pack 生成
- Word 自动化规范和 Pro 规划骨架

当前仓库**不负责**最终面向学生分发的 Word Ribbon 插件。那部分已经拆到独立仓库 `thu-word-plugin-lite`。

---

## 核心模块

```text
thesis-skills/
├── 00-zotero/      # Zotero 文献质量检查
├── 00-endnote/     # EndNote 导出流程说明
├── 01-migrate/     # Word -> LaTeX 迁移工作流
├── 02-content/     # 结构、摘要、符号与缩略语检查
├── 03-references/  # 引用完整性与文献库规范
├── 04-language/    # 中文标点与语言规范检查
├── 05-format/      # 图表、标签、交叉引用、结构检查
├── 06-rules/       # 可复用 YAML 规则集
└── 07-word/        # Word 技术规范、Lite 备份、Pro 骨架
```

### 模块职责

- `00-zotero`：在迁移和质检之前，先验证 `.bib` 导出质量
- `00-endnote`：为 EndNote 用户提供导出与规范化流程
- `01-migrate`：把 Word 导出的 LaTeX 资产整理成更适合 thesis project 的结构
- `02-content`：检查摘要、结构、符号、缩略语等内容性元信息
- `03-references`：校验引用键与参考文献一致性
- `04-language`：处理中文标点、引号、中英混排等规范问题
- `05-format`：验证图表、label、ref 以及整体结构完整性
- `06-rules`：把学校或期刊规范从代码中抽离出来，做成可复用规则包
- `07-word`：保留 Word 相关规范、Lite 源码备份和 Pro 自动化方向

---

## 快速开始

### 你已经有 LaTeX 项目

```bash
python run_check_once.py --project-root "../your-thesis-project" --rules tsinghua --skip-compile
```

### 你在用清华 `thuthesis`

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

### 你要安装到 OpenClaw

```bash
python install_openclaw.py
```

---

## 技术流程

```text
Word 草稿 / 现有 LaTeX 项目
    |
    +-- migration metadata / bibliography exports / school rules
    v
01-migrate/ + intake metadata
    |
    v
目标 LaTeX 项目
    |
    +-- run_check_once.py
           |
           +-- 00-zotero
           +-- 03-references
           +-- 04-language
           +-- 05-format
           +-- 02-content
           v
         JSON reports
```

这个仓库的核心原则很明确：**AI 负责解释和辅助，代码负责约束和验证。**

---

## 规则集与扩展能力

规则存放在 `06-rules/rules/<ruleset>/` 下。

如果你要支持新的学校或期刊，通常只需要补齐：

- `format.yaml`
- `citation.yaml`
- `structure.yaml`
- `language.yaml`

这也是仓库可扩展性的关键：**规范是数据，不是硬编码。**

---

## 当前状态

- 已具备可运行的确定性检查主链路
- 已具备 Word -> LaTeX 迁移工作流
- 已具备基于规则包的扩展架构
- 已支持 OpenClaw 安装
- 已在 `07-word/` 中保留 Word 技术规范、源码备份与 Pro 方向

---

## 关联仓库

- `thu-word-plugin-lite`：面向最终用户的一键 Word Ribbon 插件

---

## 许可证

详见 [LICENSE](LICENSE)。第三方声明见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。
