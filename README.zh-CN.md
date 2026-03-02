# Thesis 六个 Skills（发布优化副本）

[English README](README.md)

这个目录是六个论文技能的发布优化工作区，用于先打磨再发布。

## 包含的 Skills

- `01-migrate`
- `02-content`
- `03-references`
- `04-language`
- `05-format`
- `06-rules`

## 当前适用范围

- 主要面向：清华 LaTeX 论文模板流程
- 次要面向：其他学校但已具备 LaTeX 模板的同学
- 当前边界：非清华规则需在 `06-rules/rules/custom/template/` 或 `06-rules/rules/my-university/` 基础上补全

## 内容边界（你关心的问题）

- 这六个 skills 不负责生成你的论文研究内容（如论点、方法、结果、结论）。
- 它们主要做迁移、参考文献检查、语言规范检查、结构与排版检查、规则化校验。
- 会读取现有章节文件用于检查，但默认不会自动改写正文内容。

## 一键检查（推荐）

在本目录执行：

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules tsinghua
```

执行顺序：

1. `03-references/check_references.py`
2. `04-language/check_language.py`
3. `05-format/check_structure.py`
4. `02-content/scan_symbols.py --mode report`
5. 编译闭环（可用 `--skip-compile` 跳过）

## 其他学校示例规则

已提供可直接改的示例：

- `06-rules/rules/my-university/`

快速验证：

```bash
python run_check_once.py --project-root "../thuthesis-v7.6.0" --rules my-university --skip-compile
```

## 发布跟踪

- 发布门禁清单：`RELEASE_CHECKLIST.md`

## 致谢

- 感谢 `thuthesis` 项目提供高质量模板基础：
  - https://github.com/tuna/thuthesis
