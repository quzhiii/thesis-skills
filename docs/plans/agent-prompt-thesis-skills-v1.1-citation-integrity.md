# AI Agent 开发 Prompt：Thesis Skills v1.1 Citation Integrity Engine

你是一个严谨的软件工程 agent。现在需要在 GitHub 仓库 `quzhiii/thesis-skills` 中开发 `v1.1 Citation Integrity Engine`。

## 一、项目背景

`thesis-skills` 是一个面向研究生和科研作者的确定性论文工作流仓库。它连接 Word、Zotero、EndNote、LaTeX、结构化检查报告、安全修复补丁和提交前 readiness gate。它不是 AI 写作助手，也不自动生成论文内容。

本次任务是在现有 `10-check-references` 和 `16-check-readiness` 基础上，增强引用完整性检查能力。

目标模块名称：

```text
Citation Integrity Engine
```

中文定位：

```text
引用完整性引擎：在论文提交前检查引用键、BibTeX 文献库、LaTeX 编译日志、基础字段和交叉引用是否存在高风险问题。
```

## 二、最高优先级约束

1. 不要实现 AI 写作功能。
2. 不要自动生成、替换或插入参考文献。
3. 不要调用 LLM。
4. 不要依赖外部 API。
5. V1.1 必须 local-first、deterministic、可测试。
6. 默认只输出报告，不自动修改正文。
7. 保持现有 CLI 风格、报告风格、目录结构和测试习惯。
8. 不要大规模重构无关模块。
9. 所有新增功能必须有测试或 demo evidence。
10. 如果已有同类函数，优先复用，不重复造轮子。

## 三、开发前检查

开始前先执行：

```bash
git status
ls
find . -maxdepth 2 -type f | sort | sed -n '1,200p'
```

重点阅读：

```text
README.md
README.zh-CN.md
10-check-references/check_references.py
16-check-readiness/check_readiness.py
20-fix-references/fix_references.py
core/
tests/
examples/
docs/modules.md
run_check_once.py
```

如果某些文件不存在，以实际仓库结构为准，不要假设。

## 四、V1.1 功能范围

### 4.1 必须实现

实现或增强以下检查：

1. `\cite{}` citation key 检查：
   - 文中引用但 `.bib` 缺失；
   - 多 key citation，如 `\cite{a,b,c}`；
   - 常见命令：`\cite`、`\citep`、`\citet`、`\parencite`、`\textcite`、`\autocite` 等，能覆盖多少覆盖多少，并在文档中说明范围。

2. unused bibliography 检查：
   - `.bib` 中存在，但正文未引用。

3. duplicate key 检查：
   - 同一个 `.bib` 内重复 key；
   - 多个 `.bib` 文件中重复 key；
   - 如果 key 相同但 metadata 不同，标记为 BLOCK 或 WARN。

4. required fields 检查：
   - 基础字段：title、author、year；
   - 类型相关字段：article 需 journal 或 journaltitle；inproceedings 需 booktitle；book 需 publisher；
   - DOI 缺失默认 WARN，不 BLOCK；
   - 对中文文献或无 DOI 文献不要误判为错误。

5. DOI 格式检查：
   - 只检查格式，不访问网络；
   - 格式明显异常标记 WARN。

6. year 格式检查：
   - 缺失、非数字、异常未来年份标记 WARN；
   - 不要因为 2026 以后年份简单误判，允许配置当前年份或容忍未来 1 年。

7. LaTeX log citation warning 解析：
   - 支持读取 `.log`；
   - 解析 undefined citations、empty bibliography、citation undefined 等常见 warning。

8. label/ref 交叉引用断链：
   - 检查 `\ref{}`、`\eqref{}`、`\autoref{}` 是否有对应 `\label{}`；
   - 未使用 label 标记 INFO 或 WARN；
   - 不要影响 citation 主流程。

9. 输出统一报告：
   - `reports/citation-integrity-report.json`；
   - 如果现有 pipeline 仍使用 `check_references-report.json`，可以同时保留兼容输出。

10. readiness gate 集成：
   - References 维度根据 Citation Integrity 结果给出 PASS / WARN / BLOCK；
   - BLOCK 条件至少包括 cited key missing、duplicate key metadata conflict、LaTeX log undefined citation。

### 4.2 暂不实现

V1.1 不做：

- CrossRef / OpenAlex / Semantic Scholar 查询；
- AI 假文献判断；
- LLM claim-citation 支撑判断；
- 引用推荐；
- Zotero Web API；
- Word field 深度解析；
- 自动修复正文引用。

这些属于 V2–V5。

## 五、建议实现结构

优先遵循仓库现有结构。如果需要新增模块，可采用：

```text
core/citation_integrity/
├── __init__.py
├── models.py
├── tex_parser.py
├── bib_parser.py
├── latex_log_parser.py
├── field_lint.py
├── cross_reference_lint.py
├── report.py
└── readiness_adapter.py
```

也可以直接在现有 `10-check-references` 下拆分，只要结构清晰、测试可维护。

## 六、报告 Schema 要求

输出 JSON 至少包含：

```json
{
  "module": "citation_integrity",
  "version": "1.1",
  "status": "PASS|WARN|BLOCK",
  "summary": {
    "tex_files": 0,
    "bib_files": 0,
    "cited_keys": 0,
    "bib_entries": 0,
    "missing_cited_keys": 0,
    "unused_bib_entries": 0,
    "duplicate_bib_keys": 0,
    "field_warnings": 0,
    "latex_log_warnings": 0,
    "cross_reference_warnings": 0
  },
  "issues": [
    {
      "id": "CI-...",
      "severity": "INFO|WARN|BLOCK",
      "category": "missing_cited_key|unused_bib_entry|duplicate_key|field_warning|doi_format|year_format|latex_log_warning|missing_label|unused_label",
      "message": "Human-readable message.",
      "file": "relative/path.tex",
      "line": 0,
      "evidence": {},
      "suggested_action": "What the user should check manually."
    }
  ]
}
```

要求：

- 文件路径使用相对路径；
- line 获取不到时允许为 null；
- issue id 稳定；
- 输出顺序稳定，便于测试；
- JSON 可被后续 readiness 读取。

## 七、PASS / WARN / BLOCK 策略

### PASS

满足：

- 所有 cited keys 均存在；
- 无 duplicate key conflict；
- 无 LaTeX undefined citation warning；
- 仅有 INFO 或无问题。

### WARN

包括：

- unused bib entries；
- DOI 缺失或格式异常；
- year 缺失或异常；
- optional fields 缺失；
- unused labels；
- 非阻断性 field warning。

### BLOCK

包括：

- 文中引用 key 缺失；
- duplicate key 且 metadata 冲突；
- LaTeX log 显示 undefined citation；
- bibliography 文件无法解析且项目存在引用。

## 八、示例项目

新增或更新示例：

```text
examples/citation-integrity-broken/
├── main.tex
├── refs.bib
├── main.log
└── README.md
```

示例应覆盖：

- 一个 missing cited key；
- 一个 unused bib entry；
- 一个 duplicate key；
- 一个缺 DOI 的 article；
- 一个 year 异常；
- 一个 LaTeX log undefined citation；
- 一个 `\ref{}` 缺失 label。

同时可新增：

```text
examples/citation-integrity-clean/
```

用于 PASS demo。

## 九、测试要求

新增测试至少覆盖：

```text
tests/test_citation_integrity_keys.py
tests/test_citation_integrity_bib_fields.py
tests/test_citation_integrity_latex_log.py
tests/test_citation_integrity_readiness.py
```

测试必须验证：

1. missing cited key 被识别为 BLOCK；
2. unused bib entry 被识别为 WARN 或 INFO；
3. duplicate key 被识别；
4. required field warning 被识别；
5. DOI 格式异常被识别；
6. LaTeX log warning 被识别；
7. readiness gate 能读取 citation integrity 状态；
8. 现有 examples/minimal-latex-project 不被破坏。

运行：

```bash
pytest
python run_check_once.py --project-root examples/minimal-latex-project --ruleset university-generic --skip-compile
python 10-check-references/check_references.py --project-root examples/citation-integrity-broken
```

如果仓库当前测试命令不同，使用仓库实际命令。

## 十、CLI 要求

尽量保持兼容：

```bash
python 10-check-references/check_references.py \
  --project-root examples/citation-integrity-broken \
  --ruleset university-generic
```

可选参数：

```text
--output reports/citation-integrity-report.json
--include-unused true|false
--include-crossrefs true|false
--log-file path/to/main.log
```

不要破坏 `run_check_once.py` 对 reference check 的调用。

## 十一、文档要求

更新：

```text
README.md
docs/modules.md
10-check-references/README.md
examples/citation-integrity-broken/README.md
CHANGELOG.md
```

README 中增加一个简短 preview：

```text
References: BLOCK
- 3 cited keys are missing from bibliography files
- 2 duplicate citation keys conflict across bib files
- 7 references have missing DOI or year fields
- 4 LaTeX citation warnings found in compile log
```

文档必须明确边界：

```text
V1.1 only checks local citation integrity. It does not verify whether a reference exists in external databases and does not detect hallucinated references yet.
```

## 十二、开发流程

请按以下顺序执行：

1. Inspect repository structure。
2. 总结现有 reference check 和 readiness gate 的调用关系。
3. 制定最小实现计划。
4. 实现 parser / linter / report。
5. 接入 CLI。
6. 接入 readiness gate。
7. 添加 examples。
8. 添加 tests。
9. 更新 docs。
10. 运行测试和 smoke test。
11. 输出最终变更摘要。

## 十三、最终交付格式

完成后输出：

```text
## Summary
- ...

## Files changed
- ...

## New commands
- ...

## Reports generated
- ...

## Tests
- command: ...
  result: passed/failed

## Known limitations
- ...

## Next version notes
- V1.2: Markdown/CSV reports
- V2: CrossRef/OpenAlex/Semantic Scholar verification
```

## 十四、验收标准

本任务完成必须满足：

- [ ] 不破坏现有 check pipeline；
- [ ] 本地 examples 能跑通；
- [ ] 生成 `citation-integrity-report.json`；
- [ ] readiness gate 能读取并反映 References 状态；
- [ ] 新增测试通过；
- [ ] README 和 docs 更新；
- [ ] 无外部 API 依赖；
- [ ] 无 LLM 调用；
- [ ] 无自动改写论文正文；
- [ ] 输出中明确 V1.1 边界。
