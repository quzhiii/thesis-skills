# 07-word 模块仓库定位说明

本目录在未来拆分后，属于 `thesis-skills` 仓库中的 Word 技术规范与自动化能力模块，而不是面向最终学生用户的插件分发目录。

## 定位
- 面向 OpenCode / Claude / 自动化工作流
- 面向开发者、研究助理、规则维护者
- 提供 Word 处理的规范、规划、规则和 Pro 骨架

## 包含内容
- `THESIS_WORD.md`：总览说明
- `actions_spec.md`：动作白名单
- `plan_schema.md`：计划与报告 schema
- `FEASIBILITY.zh-CN.md`：可行性与风险说明
- `VALIDATION_PLAN.zh-CN.md`：回归验证计划
- `lite/THU_Formatter_Lite.bas`：Lite 版本源码备份（非分发入口）
- `pro/`：Python lint/planner 骨架与规则

## 不包含内容
- 面向学生的最终 dotm 插件分发
- Ribbon 打包交付物
- 安装/卸载脚本作为最终用户入口

## 与 A 档插件仓库的关系
- A 档插件仓库：`thu-word-plugin-lite`
- 当前目录：`thesis-skills/07-word`

关系说明：
- A 仓库负责最终用户安装和使用体验
- B 仓库负责技术实现、规则演进和自动化能力
