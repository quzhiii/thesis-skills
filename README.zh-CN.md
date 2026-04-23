# Thesis Skills v0.7.0

<div align="center">

![Thesis Skills](https://img.shields.io/badge/论文-技能-4285f4?style=for-the-badge&logo=book&logoColor=white)

**确定性论文写作工作流**  
*Python 检查器 · 安全修复器 · YAML 规则包 · 一键运行*

[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/quzhiii/thesis-skills)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](https://github.com/quzhiii/thesis-skills)
[![展示页面](https://img.shields.io/badge/🚀%20展示页面-在线-success)](https://quzhiii.github.io/thesis-skills)

**中文文档** • [English](README.md) • [🚀 展示页面](https://quzhiii.github.io/thesis-skills)

[快速开始](#快速开始) • [零基础入门教程](docs/getting-started-zh.md) • [核心功能](#核心功能) • [版本历史](#版本历史) • [架构文档](docs/architecture.md) • [贡献指南](CONTRIBUTING.md)

</div>

---

## 为什么需要 Thesis Skills？

**我们解决的痛点：**

| 痛点 | 传统工作流 | Thesis Skills |
|:---|:---|:---|
| Word→LaTeX 引用迁移 | 手动映射，容易出错 | 自动提取与同步 |
| 引用编号稳定性 | 删除后编号变化 | Citation Lock 锁定机制 |
| 高校格式合规 | 阅读文档、手动检查 | YAML 规则包 + 自动检查 |
| 语言质量 | 人工校对 | 确定性检查 + 深度审阅 |
| 文献库导入 | EndNote 复制粘贴 | XML/RIS/BibTeX 自动导入 |

---

## 版本历史

### v0.7.0 — 预提交判断层 🆕

> **把分散在多个报告里的信息，收束成一个更容易做决定的 readiness verdict**

| v0.7.0 新增 | 增加了什么 | 实际价值 |
|:---|:---|:---|
| `16-check-readiness` | 新的预提交 Gate | 不用再来回翻多份报告，先看一个统一结论，再决定下一步 |
| Gate modes | `advisor-handoff` + `submission-prep` | 同样是“继续往前走”，但导师预审和正式提交前的要求可以明确区分 |
| Runner bridge | `run-summary.json` 中新增 `derived_artifacts.readiness_gate` | 现有 runner 不用重写，也能稳定暴露 readiness 结果 |

**这一版重点解决的是：**
- 现有检查、修复、编译、导出、审阅产物已经很多，但缺少最后一层“现在能不能继续”的统一判断
- 用户不需要自己把多份 artifact 再拼成 go / no-go 结论
- Gate 会给出机器可读的 `PASS / WARN / BLOCK`，并明确列出 blockers、warnings、next actions 和来源

### v0.6.0 — 交付基础层

> **审阅优先导出 + 编译诊断 + 有边界审阅闭环**

| v0.6.0 新增 | 增加了什么 | 实际价值 |
|:---|:---|:---|
| `02-latex-to-word` | 审阅优先 `.docx` 导出 | 更适合导师和协作者审阅 |
| `15-check-compile` | 结构化编译日志解析 | 把原始 TeX 报错转成更清晰的 findings |
| `03-latex-review-diff` + `04-word-review-ingest` | 审阅闭环 artifact | 让 revision round 可检查、可追踪 |

**核心新增：**
- 面向审阅的 LaTeX→Word 导出，并显式报告限制边界
- compile-log parser 接入 `run_check_once.py`
- review package、feedback ingest、TODO 拆分与 revision summary

### v0.5.2 — 深度补丁预览与选择性应用

> **审阅型发现 → 选择性补丁**

| 之前 (v0.5.1) | 之后 (v0.5.2) | 效果 |
|:---|:---|:---|
| 深度发现 = 只读报告 | 基于范围的补丁预览 | **可执行修复** |
| 深度问题无法自动修复 | 验证 `old_text` 匹配后应用 | **安全应用** |
| 单一修复模式 | `--apply-mode safe\|suggest\|mixed` | **灵活控制** |

**核心新增：**
- `24-fix-language-deep`: 将发现项转换为基于范围的补丁
- 补丁验证：检查 `old_text`，拒绝重叠
- 尊重 `review_required` 标志（默认跳过需审阅项）

### v0.5.1 — 深度语言审阅层

> **句子级感知、跨文件语言筛查**

| 指标 | v0.5.0 | v0.5.1 | 变化 |
|:---|:---|:---|:---|
| 检查深度 | 字符级 | 句子级 + 跨文件 | **+3 层** |
| 输出字段 | 基础 | 10+ 字段 (范围、证据、置信度) | **丰富元数据** |
| 审阅工作流 | 平面列表 | 优先级队列 + 聚类 | **高效分类** |

**新增检查器：** `14-check-language-deep`
- 连接词误用检测
- 搭配分析
- 术语一致性
- 缩写首次使用验证
- LaTeX 感知屏蔽 (cite/ref、数学、图表)

### v0.5.0 — 基础语言层

> **确定性语言检查层**

```
v0.5.0 覆盖范围：
├── 中西文间距
├── 标点规范化
├── 括号引号平衡
├── 书名号一致性
├── 单位间距
├── 省略号与破折号样式
├── 中英标点边界
├── 数字范围
├── 枚举标点
└── 连接词黑名单
```

### v0.4 — EndNote 优先支持

| 功能 | v0.3 | v0.4 | 提升 |
|:---|:---|:---|:---|
| 文献源 | 仅 Zotero | Zotero + EndNote | **+100%** |
| 导入格式 | 手动 BibTeX | XML/RIS/BibTeX | **自动检测** |
| 重复处理 | 无 | DOI 精确 + 模糊警告 | **干净导入** |
| 规范化 | Zotero 专用 | 源无关模型 | **通用模型** |

### v0.3 — 效率革命

> **4-5 倍工作流提速**

| 工作流 | v0.2 时间 | v0.3 时间 | 提速 |
|:---|:---|:---|:---|
| 日常引用更新 (10 条) | ~85 分钟 | ~2 分钟 | **42×** |
| Word→LaTeX 迁移 (首次) | ~210 分钟 | ~40 分钟 | **5.25×** |
| 新高校格式适配 | ~100 分钟 | ~56 分钟 | **1.8×** |
| 引用同步 | 手动映射 | 自动提取 | **快 80%** |
| 项目发现 | 手动配置 | 自动检测 | **快 90%** |

---

## 核心功能

### 五层架构

```
┌─────────────────────────────────────────┐
│  第 6 层：规则包接入层                   │  ← YAML 配置、启动包
├─────────────────────────────────────────┤
│  第 5 层：报告驱动修复                   │  ← 20-fix-*、24-fix-language-deep
├─────────────────────────────────────────┤
│  第 4 层：确定性检查                     │  ← 10-check-*、14-check-language-deep
├─────────────────────────────────────────┤
│  第 3 层：LaTeX→Word 导出                │  ← 02-latex-to-word
├─────────────────────────────────────────┤
│  第 2 层：Word→LaTeX 迁移                │  ← 01-word-to-latex
├─────────────────────────────────────────┤
│  第 1 层：文献库接入                     │  ← 00-bib-endnote、00-bib-zotero
└─────────────────────────────────────────┘
```

### 功能模块

| 模块 | 状态 | 描述 |
|:---|:---|:---|
| **EndNote 导入** | ✅ v0.4 | XML/RIS/BibTeX → `refNNN` 自动去重 |
| **Zotero 同步** | ✅ v0.3 | Word docx → LaTeX 引用映射 |
| **LaTeX→Word 导出** | ✅ v0.6 | 面向审阅的 `.docx` 导出，并显式暴露限制 |
| **引用检查** | ✅ 稳定 | 缺失键、孤立项、重复标题 |
| **语言检查** | ✅ v0.5.0 | 10+ 确定性规则 |
| **深度语言审阅** | ✅ v0.5.1 | 句子级感知筛查 |
| **深度补丁修复** | ✅ v0.5.2 | 选择性范围修复 |
| **格式检查** | ✅ 稳定 | 图表、居中 |
| **内容检查** | ✅ 稳定 | 必需章节、摘要关键词 |
| **编译日志解析** | ✅ v0.6 | 基于现有 `.log` 文件提供更友好的编译诊断 |
| **审阅闭环** | ✅ v0.6 | 审阅 diff、反馈归一化、TODO 拆分与修订摘要 |
| **预提交 Gate** | ✅ v0.7 | 基于现有 workflow artifacts 的有边界 readiness verdict |

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

### 新手从这里开始

如果你还没有 LaTeX 基础，建议先阅读：

- [零基础入门教程：先安装 LaTeX，再使用 Thesis Skills](docs/getting-started-zh.md)

### EndNote 工作流

```bash
# 1. EndNote 导出 → XML/RIS/BibTeX
# 2. 预检
python 00-bib-endnote/check_endnote_export.py \
  --project-root thesis --input refs.xml

# 3. 导入
python 00-bib-endnote/import_library.py \
  --project-root thesis --input refs.xml --apply
```

### Zotero 工作流

```bash
# 从 Word 同步到 LaTeX
python 00-bib-zotero/sync_from_word.py \
  --project-root thesis --word-file thesis.docx --apply

# 运行检查
python run_check_once.py \
  --project-root thesis --ruleset tsinghua-thesis --skip-compile

# 修复问题（先试运行）
python run_fix_cycle.py \
  --project-root thesis --ruleset tsinghua-thesis --apply false
```

### 编译诊断

```bash
# 当项目里已有 .log 文件时，解析编译问题
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis

# 如果只想看结构、内容、语言问题，可跳过编译解析
python run_check_once.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --skip-compile
```

定位说明：

- 编译日志解析会把原始 LaTeX 日志转换成结构化 findings
- 它不是 TeX 工具链的替代品，也不承诺完整编译编排
- 如果没有可用 `.log` 文件，runner 会显式报告，而不是直接崩溃

### LaTeX 到 Word 工作流

```bash
# 先生成审阅优先的导出摘要
python 02-latex-to-word/migrate_project.py \
  --project-root thesis \
  --output-file thesis-review.docx \
  --profile review-friendly \
  --apply false
```

首发边界：

- 第一优先是 review-friendly（审阅友好）导出
- submission-friendly（提交友好）导出属于后续更严格路径
- 不支持或有降级风险的构造要显式报告，不做隐式承诺

### 审阅闭环工作流

```bash
# 基于当前报告生成 review package 和 triage artifact
python 03-latex-review-diff/review_diff.py \
  --project-root thesis

# 将有边界的审阅反馈归一化成结构化 issue
python 04-word-review-ingest/feedback_ingest.py \
  --project-root thesis \
  --input review-feedback.json
```

定位说明：

- 审阅闭环是面向 revision round 的有边界 workflow，不是协作文档平台
- diff/triage 与 feedback ingest 都保留显式 JSON artifact
- 含糊或高判断成本的修改保持 review-gated，不会静默自动应用

### 预提交 Gate

```bash
# 生成有边界的 readiness artifact
python 16-check-readiness/check_readiness.py \
  --project-root thesis \
  --ruleset tsinghua-thesis \
  --mode advisor-handoff
```

定位说明：

- 它更像“最后一层判断”，不是新的底层工具链
- 它会复用已有报告和 workflow artifact，把结果汇总成一个更容易理解的 readiness verdict
- 输出不是模糊评分，而是明确的 `PASS`、`WARN`、`BLOCK`，并告诉你哪里卡住了、哪里只是有风险、下一步该先做什么
- 它不会替你重跑整条流程、不会自动修复问题，也不会声称自己能覆盖所有学校或机构的提交规则
- 如果你走的是 `run_check_once.py`，也可以直接在 `run-summary.json` 里看到 readiness gate 的 derived artifact 引用

---

## 规则包系统

内置启动包：

```
90-rules/packs/
├── university-generic/     # 通用高校论文
├── journal-generic/        # 通用期刊论文
└── tsinghua-thesis/        # 清华大学示例
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

## 技术架构

```
thesis-skills/
├── core/                   # 共享实现
│   ├── canonicalize.py     # 引用规范化
│   ├── citation_*.py       # 映射与模型
│   └── reports.py          # JSON 报告生成
├── 00-bib-*/               # 文献库工作流
├── 01-word-to-latex/       # 迁移工作流
├── 02-latex-to-word/       # 审阅优先导出工作流
├── 03-latex-review-diff/   # 审阅包与分诊工作流
├── 04-word-review-ingest/  # 有边界的反馈归一化工作流
├── 10-check-*/             # 确定性检查器
├── 15-check-compile/       # 编译日志诊断翻译层
├── 16-check-readiness/     # 有边界的预提交 readiness gate
├── 20-fix-*/               # 安全修复器
├── 90-rules/               # 规则包系统
└── 99-runner/              # 入口点
```

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

**特别感谢 [tuna/thuthesis](https://github.com/tuna/thuthesis)** 开源 LaTeX 论文模板，该项目造福了众多清华师生，也启发了本项目的开发。

---

## 许可证

MIT License
