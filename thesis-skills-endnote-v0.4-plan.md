# thesis-skills：EndNote v0.4 改造方案与执行文档

> **归档说明**
>
> 本文档为最初的“大全式汇总草案”。为便于主线长期维护，相关内容已拆分为两份文档：
>
> - 产品/架构说明：`docs/plans/2026-03-23-endnote-v0.4-product-architecture.md`
> - 执行计划文档：`docs/plans/2026-03-23-endnote-v0.4-execution-plan.md`
>
> 若后续继续迭代方案，请优先维护上述两份拆分文档；本文档保留为历史汇总参考。

## 文档目的

本文档将以下三部分内容整合为一个可直接使用的 Markdown 交付件：

1. EndNote v0.4 目录改造清单与文件级实现说明
2. 可直接交给 Claude Code / OpenCode 的执行 Prompt
3. 人工验收的检查清单

适用对象：
- 你本人做方案决策与版本规划
- Claude Code / OpenCode / 其他 AI agent 执行改造任务
- 改造完成后的人工验收与回归检查

---

# 一、EndNote v0.4 目录改造清单与文件级实现说明

## 1.1 当前状态判断

当前 `thesis-skills` 仓库中：

- Zotero 工作流已经较完整：
  - `00-bib-zotero/THESIS_BIB_ZOTERO.md`
  - `00-bib-zotero/sync_from_word.py`
  - `core/zotero_extract.py`
  - `core/citation_mapping.py`
- EndNote 工作流目前仍较弱：
  - `00-bib-endnote/THESIS_BIB_ENDNOTE.md`
  - 实际上仍是“先从 EndNote 导出 BibTeX，再复用已有 Bib 检查逻辑”

因此，EndNote 目前更接近“导入兼容”，还不是“一等支持”。

---

## 1.2 v0.4 的目标范围

### 本版要完成

- 支持从 EndNote **XML / RIS / BibTeX** 导入参考文献
- 自动归一化为内部统一结构
- 生成 `ref/refs-import.bib`
- 生成 / 更新 `ref/citation-mapping.json`
- 输出导入与检查报告（JSON）
- 扩充文档、样例、测试
- 保持对现有 Zotero 工作流的兼容

### 本版不做

- 不做完整的 EndNote `Word -> 引文抽取 -> 增量同步`
- 不做 GUI
- 不引入重量级运行时依赖
- 不大幅重写现有 Zotero 路径

---

## 1.3 改造策略

本次采用 **import-first** 策略，而不是一步到位做 EndNote Word 原生同步。

### 核心思路

EndNote v0.4 先完成这条链路：

```text
EndNote XML / RIS / BibTeX
-> 解析
-> 归一化
-> 去重
-> 生成 CanonicalRef
-> 分配/复用 refNNN
-> 写入 refs-import.bib
-> 更新 citation-mapping.json
-> 输出 report
```

### 这样做的原因

1. 风险更低，能快速形成可运行版本
2. 复用你仓库现有的 checker / fixer / rule-pack 主干
3. 不会把 EndNote 逻辑硬塞进 Zotero 专用代码
4. 为 v0.5 再做 EndNote `Word -> sync` 预留接口

---

## 1.4 建议目录结构

```text
thesis-skills/
├─ 00-bib-endnote/
│  ├─ THESIS_BIB_ENDNOTE.md
│  ├─ import_library.py
│  ├─ check_endnote_export.py
│  ├─ sample/
│  │  ├─ endnote-demo.xml
│  │  ├─ endnote-demo.ris
│  │  └─ expected-refs-import.bib
│  └─ fixtures/
│     └─ README.md
│
├─ core/
│  ├─ citation_models.py
│  ├─ canonicalize.py
│  ├─ endnote_xml.py
│  ├─ endnote_ris.py
│  ├─ bib_render.py
│  ├─ match_refs.py
│  ├─ citation_mapping.py
│  ├─ zotero_extract.py
│  └─ checkers.py
│
├─ tests/
│  ├─ test_endnote_xml.py
│  ├─ test_endnote_ris.py
│  ├─ test_canonicalize.py
│  ├─ test_bib_render.py
│  ├─ test_endnote_import_workflow.py
│  └─ data/
│     ├─ sample_endnote.xml
│     ├─ sample_endnote.ris
│     └─ sample_expected.bib
│
├─ 90-rules/
│  └─ packs/
│     └─ tsinghua-thesis/
│        └─ rules.yaml
│
└─ skills-manifest.json
```

---

## 1.5 文件级实现说明

### A. `core/citation_models.py`

作用：定义 Zotero / EndNote 共用的数据模型，避免内部结构继续绑定 Zotero。

建议包含：

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class PersonName:
    family: str = ""
    given: str = ""

@dataclass
class CanonicalRef:
    source_system: str
    source_id: str | None
    canonical_id: str
    entry_type: str
    title: str | None
    authors: list[PersonName]
    year: str | None
    doi: str | None
    isbn: str | None
    issn: str | None
    journal: str | None
    booktitle: str | None
    publisher: str | None
    langid: str | None
    raw: dict[str, Any]

@dataclass
class ImportResult:
    source_file: Path
    source_format: str
    refs: list[CanonicalRef]
    warnings: list[str]
    errors: list[str]
```

### 设计目的

- 内部抽象从 “Zotero key” 升级为 “source-agnostic ref”
- 为后续 EndNote / Zotero 共用渲染、匹配、映射逻辑打基础

---

### B. `core/canonicalize.py`

作用：做字段标准化与内部稳定 ID 生成。

建议实现的函数：

- `normalize_title(text: str) -> str`
- `normalize_person_name(...)`
- `normalize_doi(text: str) -> str | None`
- `guess_langid(ref: CanonicalRef) -> str | None`
- `build_canonical_id(ref: CanonicalRef) -> str`

### `canonical_id` 生成优先级

1. DOI
2. PMID / accession number（如有）
3. `normalized_title + year + first_author`
4. fallback hash

### 原因

- EndNote 的 record number 不能视为长期稳定主键
- 需要一个跨导出格式、跨来源也尽量稳定的内部 ID

---

### C. `core/endnote_xml.py`

作用：解析 EndNote XML 导出文件。

建议函数：

- `parse_endnote_xml(path: str | Path) -> ImportResult`

要求：

- 使用标准库 `xml.etree.ElementTree`
- 支持常见字段提取：
  - title
  - authors
  - year
  - journal
  - booktitle
  - publisher
  - doi
  - isbn
  - issn
  - label
  - accession number
- 能处理中文和英文标题
- 将 EndNote type 映射为内部统一 entry type
- 保留 `raw`

---

### D. `core/endnote_ris.py`

作用：解析 RIS 导出文件。

建议函数：

- `parse_ris(path: str | Path) -> ImportResult`

要求：

- 支持 RIS 常见 tag：
  - `TY`
  - `TI`
  - `T1`
  - `AU`
  - `A1`
  - `PY`
  - `Y1`
  - `JO`
  - `JF`
  - `T2`
  - `PB`
  - `DO`
  - `SN`
  - `SP`
  - `EP`
  - `VL`
  - `IS`
  - `UR`
  - `AB`
  - `LA`
  - `ER`
- 支持多作者
- 支持 continuation line
- 支持 type mapping
- 输出 `ImportResult`

---

### E. `core/bib_render.py`

作用：把统一后的 `CanonicalRef` 渲染为 `.bib`。

建议函数：

- `canonical_ref_to_bibtex(ref: CanonicalRef, latex_key: str) -> str`
- `render_bib_file(refs: list[CanonicalRef], mapping: dict[str, str]) -> str`

输出原则：

- 使用现有 `ref001/ref002/...` 体系
- 中英文尽量自动补 `langid`
- DOI 去空格
- 优先限制 entry type 到有限集合
- 生成的 BibTeX 尽量稳定、可读、可 diff

---

### F. `core/match_refs.py`

作用：提供去重与后续扩展的匹配能力。

建议函数：

- `match_ref(candidate, library_refs) -> MatchResult`
- `dedupe_refs(refs) -> tuple[list[CanonicalRef], list[str]]`

匹配优先级：

1. DOI exact
2. ISBN/ISSN + title
3. normalized title + year + first author

规则：

- 高置信匹配可自动合并
- 低置信匹配只给 warning，不自动合并
- 生成 warning 清单供人工复核

---

### G. `core/citation_mapping.py`

现有问题：

- 类名与字段语义偏向 Zotero
- 当前实际上是 `zotero_key -> refNNN` 映射

v0.4 建议做兼容式重构，而不是暴力推倒重写。

### 目标

- 兼容旧格式
- 支持新格式
- 旧 API 尽量保留

### 旧格式

```json
{
  "description": "Zotero citation-key to LaTeX ref number mapping",
  "version": "1.0",
  "mappings": {
    "old_zotero_key": "ref001"
  }
}
```

### 新格式建议

```json
{
  "description": "Source citation key to LaTeX ref number mapping",
  "version": "2.0",
  "mappings": {
    "endnote:doi:10.1000/xyz": {
      "latex_key": "ref001",
      "source_system": "endnote",
      "match_method": "doi"
    },
    "zotero:WuZeXinSomeKey": {
      "latex_key": "ref002",
      "source_system": "zotero",
      "match_method": "source_key"
    }
  }
}
```

### API 要求

- 保留现有方法，避免 Zotero 工作流直接断掉
- 新增通用方法，例如：
  - `get_or_create_latex_key(source_key: str, source_system: str = "generic") -> str`

---

### H. `00-bib-endnote/import_library.py`

这是 EndNote v0.4 的主入口。

建议 CLI：

```bash
python 00-bib-endnote/import_library.py \
  --project-root <latex-project> \
  --input <endnote.xml|endnote.ris|endnote.bib> \
  --format auto \
  --apply \
  --report <path>
```

### 主流程

1. 自动识别输入格式
2. 解析为 `CanonicalRef`
3. 标准化
4. 去重
5. 复用或分配 `refNNN`
6. 写入/更新：
   - `ref/refs-import.bib`
   - `ref/citation-mapping.json`
7. 输出 `reports/endnote_import-report.json`

### 报告建议包含

- total refs
- imported refs
- deduped refs
- reused mapping count
- new mapping count
- warnings
- unsupported types
- missing fields

### 模式建议

- `--apply`：真正写文件
- 默认 dry-run：只预览和生成报告

---

### I. `00-bib-endnote/check_endnote_export.py`

作用：导入前检查器。

建议检查：

- XML 是否可解析
- RIS 是否有 `TY` / `ER`
- 记录是否缺 `title`
- year 是否缺失或不可解析
- DOI 是否带空格
- authors 是否为空
- entry type 是否无法映射
- 是否存在明显重复条目

输出：

- JSON report 到 `reports/`
- 适合作为导入前快速健康检查

---

### J. `core/checkers.py`

当前 `run_bib_quality_check()` 更偏 LaTeX `.bib` 成品检查。

建议在 v0.4 中做两点增强：

1. 对 `refs-import.bib` 输出更具体的来源与归因
2. 为 EndNote 导入提供额外统计字段，例如：
   - `source_system_counts`
   - `normalized_type_counts`
   - `langid_inferred_count`

---

### K. `90-rules/packs/tsinghua-thesis/rules.yaml`

建议新增或调整：

- EndNote import 相关规则
- 适度扩充允许的条目类型
- 主要 type 归一化仍放在 normalizer 内做，不要把规则写成“类型白名单大杂烩”

示意：

```yaml
reference:
  endnote_import:
    preferred_formats:
      - xml
      - ris
      - bib
    infer_langid: true
    normalize_types: true
    dedupe:
      enabled: true
      primary_keys: [doi, title_year_author]
```

---

### L. `00-bib-endnote/THESIS_BIB_ENDNOTE.md`

当前内容过短，需要重写。

应包含：

- 模块概述
- 推荐导出顺序：XML > RIS > BibTeX
- CLI 用法
- EndNote 与 Zotero 工作流差异
- 常见错误与修复方式
- v0.4 范围与 v0.5 规划

---

### M. `tests/`

建议新增以下测试：

- `tests/test_endnote_xml.py`
- `tests/test_endnote_ris.py`
- `tests/test_canonicalize.py`
- `tests/test_bib_render.py`
- `tests/test_endnote_import_workflow.py`

测试数据建议：

- `tests/data/sample_endnote.xml`
- `tests/data/sample_endnote.ris`
- `tests/data/sample_expected.bib`

---

## 1.6 v0.4 / v0.5 边界

### v0.4

完成：
- EndNote XML / RIS / BibTeX 导入
- 归一化
- 去重
- 生成 `refs-import.bib`
- 更新 mapping
- 报告与测试

### v0.5

再做：
- `core/endnote_extract.py`
- `00-bib-endnote/sync_from_word.py`

也就是再考虑：
- 从 Word 中读取 EndNote field codes
- 从 Traveling Library 提取被引文献信息
- 做真正的 Word -> LaTeX 增量同步

---

## 1.7 v0.4 验收标准

必须满足：

1. 能从 EndNote XML 导入中英文文献并生成 `refs-import.bib`
2. 能从 RIS 导入中英文文献并保留多作者
3. 相同 DOI 的重复项可自动去重
4. 未知 type 不会导致崩溃，而是 warning
5. `citation-mapping.json` 可重复运行且 `refNNN` 稳定
6. 不破坏现有 Zotero 命令与工作流
7. 有基本测试覆盖
8. 文档可直接给用户使用

---

# 二、可直接交给 Claude Code / OpenCode 的执行 Prompt

下面这份 Prompt 可直接发给 agent。

```markdown
你现在是 `thesis-skills` 仓库的 Python maintainer / refactoring engineer。

## 项目背景

当前仓库中：
- Zotero 工作流已经较完整：
  - `00-bib-zotero/THESIS_BIB_ZOTERO.md`
  - `00-bib-zotero/sync_from_word.py`
  - `core/zotero_extract.py`
  - `core/citation_mapping.py`
- EndNote 工作流目前很弱，只有一个占位式说明：
  - `00-bib-endnote/THESIS_BIB_ENDNOTE.md`
  - 当前逻辑基本等于“从 EndNote 导出 BibTeX，然后复用 Zotero 的 `check_bib_quality.py`”

本次任务目标是实现 **EndNote v0.4**：
- 先做 **import-first** 方案
- 支持 EndNote XML / RIS / BibTeX 导入
- 自动归一化为内部统一结构
- 生成 `ref/refs-import.bib`
- 生成 / 更新 `ref/citation-mapping.json`
- 输出 JSON report
- 不破坏现有 Zotero workflow
- 暂时不实现 EndNote Word field-code 原生同步

---

## 设计原则

1. **不要引入重量级运行时依赖**
   - 优先使用 Python 标准库
   - 开发测试依赖可用 pytest
   - 若确需第三方库，必须先说明理由，并尽量做成 optional

2. **保持向后兼容**
   - 现有 Zotero 命令和已有 mapping 文件尽量继续可用
   - `core/citation_mapping.py` 可以内部重构，但旧 API 尽量保留

3. **先抽象，再实现**
   - 不要把 EndNote 逻辑硬塞进 Zotero 代码里
   - 先引入 source-agnostic 的 citation model

4. **本次范围只做 v0.4**
   - 不做 GUI
   - 不做 EndNote Word field-code parser
   - 可以为 v0.5 预留接口，但不要过度设计

---

## 需要完成的代码改造

### 一、在 `core/` 新增通用模型与解析器

新增文件：

- `core/citation_models.py`
- `core/canonicalize.py`
- `core/endnote_xml.py`
- `core/endnote_ris.py`
- `core/bib_render.py`
- `core/match_refs.py`

要求：

#### `core/citation_models.py`
定义：

```python
@dataclass
class PersonName:
    family: str = ""
    given: str = ""

@dataclass
class CanonicalRef:
    source_system: str
    source_id: str | None
    canonical_id: str
    entry_type: str
    title: str | None
    authors: list[PersonName]
    year: str | None
    doi: str | None
    isbn: str | None
    issn: str | None
    journal: str | None
    booktitle: str | None
    publisher: str | None
    langid: str | None
    raw: dict[str, Any]

@dataclass
class ImportResult:
    source_file: Path
    source_format: str
    refs: list[CanonicalRef]
    warnings: list[str]
    errors: list[str]
```

#### `core/canonicalize.py`
实现：
- DOI 规范化（去空格、统一前缀）
- 标题规范化（去多余空白、括号/花括号清洗、统一大小写比较用形式）
- 作者名规范化
- `langid` 推断（至少 english / chinese）
- `canonical_id` 生成策略：
  1. DOI
  2. PMID / accession number（如有）
  3. normalized title + year + first author
  4. fallback hash

#### `core/endnote_xml.py`
实现：
- 解析 EndNote XML 导出
- 返回 `ImportResult`
- 能处理：
  - 中英文标题
  - 多作者
  - 缺 DOI
  - 常见 type
- 使用标准库 XML parser

#### `core/endnote_ris.py`
实现：
- 解析 RIS 文件
- 支持：
  - 多作者
  - continuation lines
  - 常见 tags：TY TI T1 AU A1 PY Y1 JO JF T2 PB DO SN SP EP VL IS UR AB LA ER
- 返回 `ImportResult`

#### `core/bib_render.py`
实现：
- `canonical_ref_to_bibtex(ref, latex_key)`
- `render_bib_file(refs, mapping)`
- 输出稳定、可读的 bibtex
- 自动补 `langid`
- 统一 entry type 到有限集合

#### `core/match_refs.py`
实现：
- 用于去重与后续扩展
- 匹配优先级：
  1. DOI exact
  2. ISBN/ISSN + title
  3. normalized title + year + first author
- 低置信匹配不要自动合并，写 warning

---

### 二、重构 `core/citation_mapping.py`

当前文件过于绑定 Zotero 语义，需要改成通用版本，但保持兼容。

要求：
- 支持读取旧格式：

```json
{
  "description": "...",
  "version": "1.0",
  "mappings": {
    "old_zotero_key": "ref001"
  }
}
```

- 支持新格式：

```json
{
  "description": "Source citation key to LaTeX ref number mapping",
  "version": "2.0",
  "mappings": {
    "endnote:doi:10.1000/xyz": {
      "latex_key": "ref001",
      "source_system": "endnote",
      "match_method": "doi"
    }
  }
}
```

- 保留现有可用 API
- 新增通用 API，例如：
  - `get_or_create_latex_key(source_key: str, source_system: str = "generic") -> str`

---

### 三、实现 `00-bib-endnote/import_library.py`

新增 CLI 脚本：

```bash
python 00-bib-endnote/import_library.py \
  --project-root <latex-project> \
  --input <file> \
  --format auto \
  --apply \
  --report <path>
```

要求：
- 支持自动判断输入格式：xml / ris / bib
- 解析导入文件
- 标准化
- 去重
- 为每个 canonical ref 分配或复用 `refNNN`
- 写入 / 更新：
  - `ref/refs-import.bib`
  - `ref/citation-mapping.json`
- 生成 report：
  - imported count
  - deduped count
  - warnings
  - unsupported types
  - missing fields
- 支持 dry-run 和 apply
- 报错时退出码合理

---

### 四、实现 `00-bib-endnote/check_endnote_export.py`

新增导入前检查器。

要求检查：
- XML 解析失败
- RIS 缺少 `TY` 或 `ER`
- 记录无标题
- 年份缺失或无法解析
- DOI 含空格
- 作者字段为空
- entry type 无法映射
- 可能重复条目

输出 JSON report 到 `reports/`

---

### 五、更新规则与文档

#### 修改 `90-rules/packs/tsinghua-thesis/rules.yaml`
新增或调整：
- EndNote import 相关规则
- 适度扩展允许的条目类型
- 不要无限扩大规则，把主要类型映射放在 normalizer 内完成

#### 重写 `00-bib-endnote/THESIS_BIB_ENDNOTE.md`
文档应包含：
- 概述
- 推荐导出顺序：XML > RIS > BibTeX
- CLI 用法
- EndNote 与 Zotero workflow 的差异
- 常见报错
- v0.4 范围 / v0.5 计划

---

### 六、补测试

新增：

- `tests/test_endnote_xml.py`
- `tests/test_endnote_ris.py`
- `tests/test_canonicalize.py`
- `tests/test_bib_render.py`
- `tests/test_endnote_import_workflow.py`

并提供最小测试数据：
- `tests/data/sample_endnote.xml`
- `tests/data/sample_endnote.ris`
- `tests/data/sample_expected.bib`

要求：
- pytest 可运行
- 测试覆盖导入、规范化、去重、输出稳定性

---

## 代码风格要求

- Python 3.11+ 兼容
- 尽量使用 dataclass
- 所有函数加类型注解
- 关键函数加 docstring
- 错误处理明确，不要 silent pass
- 不要删除现有 Zotero 功能
- 命名清晰，不要继续把 EndNote 逻辑写成 `zotero_*`

---

## 实施顺序

请按以下顺序执行，并在每一步完成后输出简短进度说明：

1. 先阅读并总结当前仓库的 Zotero 结构与可复用组件
2. 实现通用数据模型与 canonicalize
3. 实现 EndNote XML / RIS parser
4. 重构 citation_mapping 为兼容版
5. 实现 import_library.py
6. 实现 check_endnote_export.py
7. 更新 rules.yaml 和 THESIS_BIB_ENDNOTE.md
8. 编写并运行测试
9. 最后输出：
   - 改动文件清单
   - 关键设计说明
   - 剩余风险点
   - 建议的 v0.5 下一步

---

## 验收标准

必须满足：

1. 能从 EndNote XML 导入中英文文献，输出 `refs-import.bib`
2. 能从 RIS 导入中英文文献，保留多作者
3. 相同 DOI 的重复项可自动去重
4. 未知 type 不崩溃，而是 warning
5. `citation-mapping.json` 可重复运行且 `refNNN` 稳定
6. 现有 Zotero 命令不被破坏
7. 测试通过
8. 文档可直接给用户看

---

## 输出要求

先不要直接贴所有代码。
请先输出：
1. 你对当前仓库结构的理解
2. 计划新增/修改的文件列表
3. 你准备如何保证 Zotero 兼容性
4. 你认为最容易出错的 3 个点

然后再开始逐步修改代码。
```

### 建议给 agent 的补充限制语句

如果 agent 第一轮输出过散，可再追加一句：

```text
请严格控制本轮范围为 EndNote v0.4 import-first，不要实现 EndNote Word field-code parser，不要引入重量级依赖，不要大幅重写 Zotero workflow。
```

---

# 三、人工验收检查清单

下面这份清单用于：  
1）agent 改完后你自己逐项核对；  
2）判断这版是否真的达到 “可合并 / 可继续迭代” 的标准。

---

## 3.1 结构层验收

### 目录与文件是否到位

- [ ] `00-bib-endnote/import_library.py` 已新增
- [ ] `00-bib-endnote/check_endnote_export.py` 已新增
- [ ] `core/citation_models.py` 已新增
- [ ] `core/canonicalize.py` 已新增
- [ ] `core/endnote_xml.py` 已新增
- [ ] `core/endnote_ris.py` 已新增
- [ ] `core/bib_render.py` 已新增
- [ ] `core/match_refs.py` 已新增
- [ ] `tests/` 下对应测试文件已新增
- [ ] `00-bib-endnote/THESIS_BIB_ENDNOTE.md` 已重写
- [ ] `rules.yaml` 已补充 EndNote import 相关规则

### 命名与边界

- [ ] 没有继续把 EndNote 逻辑塞进 `zotero_*` 文件中
- [ ] 内部抽象已经从 “zotero_key” 升级到通用 source model
- [ ] Zotero 工作流未被破坏

---

## 3.2 导入能力验收

### XML 导入

准备一份真实或半真实的 EndNote XML 样本，检查：

- [ ] XML 能被正常识别
- [ ] 至少导入 10 条以上记录不报错
- [ ] 中文标题能保留
- [ ] 英文标题能保留
- [ ] 多作者能正确解析
- [ ] DOI 能正确提取
- [ ] 缺 DOI 记录不会崩溃
- [ ] journal / publisher / year 至少能提取核心字段
- [ ] 导入后的条目数与预期基本一致

### RIS 导入

准备一份真实或半真实的 RIS 样本，检查：

- [ ] RIS 能被识别
- [ ] `TY` / `ER` 边界处理正确
- [ ] 多作者不会丢失
- [ ] continuation lines 不会串行或截断
- [ ] 中英文混合记录可处理
- [ ] 常见字段能正确映射
- [ ] type 不支持时给 warning，不崩溃

### BibTeX 导入

- [ ] 对 EndNote 导出的 BibTeX 至少可作为兼容输入被接受
- [ ] 即便 BibTeX 字段不完美，也不会导致整个流程失败
- [ ] 能在 report 中提示字段问题

---

## 3.3 标准化与去重验收

### DOI 规范化

- [ ] DOI 中的空格被去掉
- [ ] `https://doi.org/...` 能被归一为 DOI
- [ ] 大小写/前缀差异不会导致同一 DOI 被当成两条

### 标题标准化

- [ ] 多余空格被清理
- [ ] 基本的花括号/括号噪音不会影响匹配
- [ ] 中英文标题不会因简单清洗而被破坏

### 去重逻辑

准备两条相同 DOI 的记录：

- [ ] 能自动去重
- [ ] report 中能看到 dedupe 结果

准备两条“题名近似但 DOI 不同”的记录：

- [ ] 不会被错误自动合并
- [ ] 若匹配置信度低，应只给 warning

准备两条“标题相同、年份相同、作者接近”的记录：

- [ ] 若自动合并，应有明确规则说明
- [ ] 若不自动合并，应输出 warning 供人工复核

---

## 3.4 mapping 稳定性验收

### 首次运行

- [ ] 首次导入后，生成 `ref/citation-mapping.json`
- [ ] `refNNN` 从 `ref001` 或现有最大编号后继续
- [ ] 生成的 mapping 结构可读

### 重复运行

在同一输入文件上连续运行两次：

- [ ] 已存在记录不会重新分配新的 `refNNN`
- [ ] mapping 内容保持稳定
- [ ] `refs-import.bib` 不会重复追加同一条记录

### 增量导入

先导入一批，再导入一批新增记录：

- [ ] 旧记录编号不变
- [ ] 新记录从最大编号继续追加
- [ ] 不会把旧记录重排

### 兼容旧格式

使用旧版 mapping 文件测试：

- [ ] 旧版 `{"key": "ref001"}` 结构仍可读取
- [ ] 不会导致 Zotero 现有脚本报错
- [ ] 如升级到新格式，应是平滑兼容，而不是强制破坏

---

## 3.5 BibTeX 输出验收

打开生成的 `ref/refs-import.bib`，人工看以下几点：

- [ ] 文件编码正常，无乱码
- [ ] 中文条目可读
- [ ] 英文条目可读
- [ ] `refNNN` 作为 key 稳定
- [ ] 输出字段顺序较稳定
- [ ] DOI 无明显格式污染
- [ ] `langid` 已合理补充
- [ ] entry type 没有大量离谱/未归一化情况
- [ ] 不会频繁产生完全重复条目

如条件允许，再做一次 LaTeX 编译验证：

- [ ] `refs-import.bib` 不会直接引发编译级错误
- [ ] 生成后的引用列表能正常工作

---

## 3.6 CLI 与错误处理验收

### `import_library.py`

- [ ] `--format auto` 可用
- [ ] `--apply` 可用
- [ ] 默认 dry-run 可用
- [ ] `--report` 可指定输出路径
- [ ] 输入文件不存在时退出码合理
- [ ] 输入格式错误时退出码合理
- [ ] 错误信息可读，不是 Python 大段 traceback 直接甩给用户

### `check_endnote_export.py`

- [ ] 可独立运行
- [ ] 能输出 JSON report
- [ ] 对 XML / RIS 格式错误给出明确提示
- [ ] 对缺字段条目给出 warning
- [ ] 对可能重复条目给出提示

---

## 3.7 Zotero 回归验收

这是非常关键的一组。

### 原有命令是否仍能运行

- [ ] `00-bib-zotero/check_bib_quality.py` 仍可运行
- [ ] `00-bib-zotero/sync_from_word.py` 仍可运行
- [ ] `core/zotero_extract.py` 未被无关改坏
- [ ] `citation_mapping.py` 改造后，Zotero 路径仍兼容

### 行为是否稳定

- [ ] 旧 Zotero mapping 仍可识别
- [ ] 旧 Zotero 工作流不会因为新格式而直接报错
- [ ] 没有把 Zotero 的字段含义错误泛化到 EndNote，也没有反过来污染 Zotero

---

## 3.8 测试与工程完整性验收

### 测试文件

- [ ] `tests/test_endnote_xml.py` 存在
- [ ] `tests/test_endnote_ris.py` 存在
- [ ] `tests/test_canonicalize.py` 存在
- [ ] `tests/test_bib_render.py` 存在
- [ ] `tests/test_endnote_import_workflow.py` 存在

### 测试执行

- [ ] pytest 可运行
- [ ] 至少端到端测试能通过
- [ ] 测试不是空壳断言
- [ ] 测试数据能覆盖中英文、缺字段、重复项三类场景

### 工程可维护性

- [ ] 新代码有类型注解
- [ ] 核心函数有 docstring
- [ ] 没有大量复制粘贴式重复逻辑
- [ ] 没有明显的硬编码路径
- [ ] 不依赖本地私人环境才可运行

---

## 3.9 文档验收

### `THESIS_BIB_ENDNOTE.md`

- [ ] 有模块概述
- [ ] 有推荐导出顺序
- [ ] 有 CLI 示例
- [ ] 有常见报错说明
- [ ] 有 v0.4 / v0.5 边界说明
- [ ] 用户读完后知道如何操作，不需要反复猜

### 仓库整体文档

- [ ] 如有必要，主 README 或 manifest 中也同步了 EndNote 能力变化
- [ ] 文档没有把“计划中的功能”写成“已经完成”
- [ ] 文档与真实命令保持一致

---

## 3.10 人工验收结论模板

你可以在 agent 完成后，按下面格式快速做结论记录：

```text
EndNote v0.4 人工验收结论

一、通过项
- 
- 
- 

二、未通过项
- 
- 
- 

三、阻塞性问题
- 
- 
- 

四、可接受但需后续迭代的问题
- 
- 
- 

五、是否建议合并
- 建议合并 / 不建议合并

六、下一步建议
- 继续做 v0.5 EndNote Word sync
- 先补测试
- 先修 mapping 兼容
- 先补文档
```

---

# 四、建议的执行顺序

如果你要把这份文档真正落地执行，建议顺序如下：

1. 先把第 2 部分 Prompt 发给 Claude Code / OpenCode
2. 要求它严格限制在 v0.4 import-first 范围
3. 等它改完后，用第 3 部分人工验收清单逐项核对
4. 通过后再考虑 v0.5 的 EndNote Word 同步

---

# 五、补充说明

这份方案的重点，不是“尽快补一个 EndNote 脚本”，而是把仓库内部抽象从 Zotero 单源模型升级为可扩展的多来源模型。

对你这个项目来说，更关键的价值在于：

- 先把 EndNote 用户纳入你现有的 check/fix 主干
- 同时避免一次性把结构做乱
- 后续无论是 EndNote Word 同步，还是再扩 Mendeley / RIS 通用导入，都有更好的扩展基础

如果后续进入 v0.5，再单独补：
- `core/endnote_extract.py`
- `00-bib-endnote/sync_from_word.py`

会更稳。
