# thesis-skills 中的 07-word 模块（拆分草案）

`07-word` 是 `thesis-skills` 仓库中的 Word 技术模块，目标不是直接向学生分发插件，而是为 AI 助手和后续规则引擎演进提供基础设施。

## 目标
- 提供 Word 格式化方案的规范文档
- 提供 Lite 参考实现源码备份
- 提供 Pro 的 lint / plan 骨架
- 为未来多高校 Word 规则扩展做准备

## 当前状态
- Lite：已覆盖标题、题注、三线表、字段/目录更新等能力
- Pro：已打通 lint/plan 闭环，但真实 docx 解析器尚未接入

## 与插件仓库的边界
- 如果你要“给学生安装并点击按钮使用”，请看独立项目：`thu-word-plugin-lite`
- 如果你要“继续开发规则、自动化、OpenCode skills”，请看当前目录

## 推荐阅读顺序
1. `THESIS_WORD.md`
2. `actions_spec.md`
3. `plan_schema.md`
4. `FEASIBILITY.zh-CN.md`
5. `VALIDATION_PLAN.zh-CN.md`
