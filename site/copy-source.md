# Thesis Skills v1.0 页面文案源文件

这份文件是 `site/` 静态页面的文案源，保持与 `README.md`、`README.zh-CN.md` 和 `docs/roadmap.md` 的 v1.0 public contract 一致。

## 1. Hero 区块

### 主标题
论文不是只靠最后通读，而是靠一串可检查的交付物推进

### 副标题
Thesis Skills v1.0 是一套确定性、可检查的论文工作流系统，帮助研究者管理文献接入、Word/LaTeX 交接、检查修复、审阅闭环、readiness 判断、答辩前整理和规则包扩展。

### Badge
v1.0：稳定公开叙事，覆盖已落地 workflow 与明确边界

### CTA 按钮
- 看当前能力
- 去文档入口
- 看输出样例

### Meta 信息
- CLI-first
- MIT 协议
- Python 3.10+

---

## 2. 痛点区块

### 区块标题
写论文时，真正困难的是把状态持续交付清楚

### 区块描述
Thesis Skills 不是 AI 写作工具，而是一套确定性工作流。它解决的是论文写作中最容易散掉、最需要可检查 artifact 的环节。

### 六个痛点

**痛点 1：导师只审 Word，但论文主线在 LaTeX**
需要一个审阅友好的导出副本，并显式说明降级和不支持构造。

**痛点 2：文献库来源混乱**
EndNote / Zotero / BibTeX 之间容易出现重复、缺字段和编号漂移。

**痛点 3：LaTeX 编译报错难以定位**
原始编译日志冗长，需要把关键错误转换成结构化 findings。

**痛点 4：修改意见分散，难以追踪**
导师批注、邮件反馈和聊天记录需要被归一化成有边界的 issue / TODO artifact。

**痛点 5：提交前没有统一判断**
多份检查、导出、编译和审阅报告需要收束成 `PASS / WARN / BLOCK` verdict。

**痛点 6：答辩前材料散在正文里**
大纲、章节要点、图表清单和讲稿备注需要先整理成可修改的准备材料。

---

## 3. 当前能力区块

### 区块标题
v1.0 稳定公开工作流

### 区块描述
每条能力都对应真实入口和可检查 artifact，不靠隐藏状态或模糊承诺。

### 能力 1：文献接入
EndNote / Zotero 导入、预检、去重和稳定 `refNNN` 映射。

### 能力 2：Word / LaTeX 交接
Word→LaTeX 迁移和审阅友好 LaTeX→Word 导出，并显式报告限制。

### 能力 3：检查与修复
引用、语言、格式、内容、编译日志和 report-driven safe fixers。

### 能力 4：审阅与 readiness
review diff、feedback ingest、TODO artifact 和 `PASS / WARN / BLOCK` gate。

### 能力 5：答辩前整理
大纲、章节要点、图表清单、候选视觉材料和讲稿备注。

### 能力 6：规则包扩展
学校/期刊规则包创建、草稿脚手架、lint、schema 和 scorecard。

---

## 4. 输出样例区块

### 区块标题
每一步都有明确 artifact

### 区块描述
Thesis Skills 的核心设计原则是“产物可检查”：每个工作流步骤都生成结构化报告或可编辑准备材料，而不是静默修改。

### 样例 1：review-friendly `.docx`
审阅友好的 Word 导出，附带显式限制报告。不支持构造被明确列出，而不是静默降级。

### 样例 2：compile findings
将原始 LaTeX 编译日志转换为结构化 findings，保留原始日志片段以便溯源。

### 样例 3：review TODO / ingest debt
将有边界反馈归一化为结构化 TODO，支持 revision round 追踪和 readiness gate 解释。

### 样例 4：readiness gate
汇总已有产物，给出 `PASS / WARN / BLOCK` verdict，以及具体下一步行动和来源。

### 样例 5：defense prep artifacts
答辩大纲、章节要点、图表清单、候选视觉材料和讲稿备注。它们是结构化 artifact 和可编辑准备材料，不是最终 PPT。

### 样例 6：rule-pack lint scorecard
检查 required files、metadata completeness、baseline completeness、schema consistency、overall status 和 finding counts。

---

## 5. 可信区块

### 区块标题
有边界、可检查、不夸大

### 区块描述
Thesis Skills 的价值在于确定性、可重复性和诚实边界。

### 六点可信理由

1. **有边界的工作流**
每个功能都有明确输入、输出和限制。

2. **显式报告**
检查器写报告，修复器读报告，关键状态不会藏在内部。

3. **可检查的产物**
JSON、Markdown、报告和准备材料都可以被人直接打开。

4. **没有“魔法”**
不声称能自动理解所有导师意见，也不自动完成高判断成本修改。

5. **局限性被暴露而非隐藏**
导出限制、编译解析边界、规则包 schema 形态都会被文档和 artifact 说明。

6. **开源可审计**
MIT 协议开源，规则、检查逻辑和修复策略都可查看和自定义。

---

## 6. 当前边界区块

### 区块标题
v1.0 明确支持什么，也明确不承诺什么

### v1.0 已包含
- EndNote / Zotero 文献导入与同步
- Word→LaTeX 迁移
- LaTeX→Word 审阅友好导出
- 引用、语言、格式、内容检查
- 深度语言筛查
- 编译日志结构化解析
- 审阅闭环（diff / feedback ingest / TODO / digest）
- 预提交 readiness gate (`PASS / WARN / BLOCK`)
- 答辩前整理 artifact
- 安全修复与选择性深度补丁
- YAML 规则包创建、草稿脚手架、lint、schema consistency 和 scorecard

### 尚未支持 / 不承诺
- 图形界面或 Web 编辑器
- 完整编译编排或替代 TeX 工具链
- 提交级 Word 导出的完整格式保证
- 自动理解导师自然语言批注
- AI 生成或重写论文内容
- 多用户实时协作
- 覆盖所有高校的特殊格式
- 一键完成论文提交
- 自动生成最终答辩 PPT
- 正式规则包 registry 或发布系统

---

## 7. CTA 区块

### 标题
开始试用 Thesis Skills

### 描述
适合已有论文项目、希望建立确定性检查和交付 artifact 工作流的研究者。如果你还没有 LaTeX 基础，建议先阅读零基础入门教程。

### 主按钮
- 查看 GitHub 仓库
- 零基础入门教程
- 看输出样例

### 链接
- 快速开始
- 架构文档
- 中文 README
- Roadmap

---

## 8. Footer

Thesis Skills v1.0.0 — MIT License — quzhiii/thesis-skills

---

## 设计原则

1. **用户语言优先**：先讲真实论文阶段，再引导到模块名。
2. **诚实不夸大**：明确展示 v1.0 的边界，不承诺尚未实现的功能。
3. **产物导向**：强调每个工作流的 artifact 产出，而非抽象功能描述。
4. **学术可信**：设计风格简洁、专业，避免 flashy startup 风格。
5. **移动友好**：响应式布局，确保在手机上的可读性。
