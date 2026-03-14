# Word 专项 Skills 可行性评估（Lite / Pro）

## 结论
- **可行**：基于 Word VBA 对样式、目录、字段、题注、表格边框和 PDF 导出均有成熟 API。
- **阶段建议**：先发布 **Lite（VBA-only）**，再迭代 **Pro（Python 规则引擎 + VBA 执行器）**。

## 为什么先 Lite
- 分发成本最低：单个 `.dotm` 即可运行。
- 用户门槛低：无需 Python 环境。
- 能最快形成闭环：一键检测修复 + 导出 docx/pdf + log。

## Pro 的价值
- 可审计：`report.json` + `fix_plan.json`。
- 可扩展：规则外置后可支持更多高校 ruleset。
- 可版本化：动作白名单、计划 schema、规则版本分离。

## 关键技术点（已验证可实现）
- 模板绑定：`Document.AttachedTemplate`
- 样式与段落：`Document.Styles`、`Paragraph.Format`
- 目录与图表目录：`TablesOfContents.Update`、`TablesOfFigures.Update`
- 字段更新：`Fields.Update`（含 TOC/REF/SEQ/页码）
- 题注序列：`wdFieldSequence` / `CaptionLabels`
- 三线表：`Table.Borders`
- 导出 PDF：`ExportAsFixedFormat`

## 主要风险与规避
- 宏安全策略：默认可能阻止互联网来源宏。
  - 规避：受信任位置、签名、内网分发。
- 大文档性能：全量字段更新耗时明显。
  - 规避：批处理 + 屏幕刷新优化 + 分阶段执行。
- 样式冲突：同名样式可能定义不同。
  - 规避：模板绑定后强制样式映射与校验。
- 直接格式覆盖（Direct Formatting）导致样式失效。
  - 规避：样式应用前清理手工格式覆盖（Font/Paragraph reset）。
- 浮动图锚点影响题注编号顺序。
  - 规避：题注附近浮动图转 Inline（白名单动作）。

## 与当前仓库的衔接
- 已新增 `07-word/`，并在 `skills-manifest.json` 注册 `07-word` 工作流。
- 已落地两份规范：`actions_spec.md`、`plan_schema.md`。
- 已落地骨架：
  - Lite：`lite/THU_Formatter_Lite.bas`
  - Pro：`pro/thu_word_lint/*` + `pro/rules/thu_v1.yaml`
- 当前里程碑状态：M0/M1/M2/M3 已落地（模板绑定、伪标题、题注+SEQ、三线表规则）。
