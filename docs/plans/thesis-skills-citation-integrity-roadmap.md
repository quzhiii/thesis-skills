# Thesis Skills Citation Integrity Engine：V1.1–V5 迭代路线、Roadmap 与验收标准

> 项目归属：`quzhiii/thesis-skills`  
> 模块名称：`Citation Integrity Engine` / `引用完整性引擎`  
> 建议版本起点：`v1.1`  
> 目标用户：研究生、青年科研人员、论文作者、课题组秘书、科研助理、学术编辑/培训服务者  
> 产品定位：论文提交前的引用链安检，而不是 AI 代写、AI 自动编参考文献或自动替换正文引用。

---

## 0. 总体判断

`Citation Integrity Engine` 应作为 `thesis-skills` 的一级核心模块，而不是另开项目。

它承接 `thesis-skills` 当前已经具备的工作流：

```text
Zotero / EndNote / Word / LaTeX
        ↓
check reports
        ↓
dry-run fixes
        ↓
readiness gate
        ↓
advisor handoff / pre-submission package
```

它的目标不是单独做一个“查参考文献是否存在”的小工具，而是把引用检查放入论文交付流程：

```text
引用键一致性
→ 文献库元数据质量
→ 外部数据库真实性核验
→ AI 假文献/幻觉引用筛查
→ 正文上下文与引用支撑关系复核
→ 可复核的候选引用推荐
```

---

## 1. 设计原则

### 1.1 Local-first 优先

第一阶段必须做到本地可运行，不依赖 LLM，不依赖外部 API，不把用户论文内容上传到云端。

适合本地检查的内容包括：

- `\cite{}` 是否存在于 `.bib`；
- `.bib` 中是否存在未被使用条目；
- citation key 是否重复；
- 必填字段是否缺失；
- DOI / year / author / title / journal 字段是否格式异常；
- LaTeX compile log 中是否有 citation warning；
- `\label{}` / `\ref{}` 是否断链；
- report 是否能纳入 readiness gate。

### 1.2 Report-first，而不是 auto-fix-first

引用完整性属于高风险论文内容区域。默认只输出报告与 dry-run patch，不自动替换正文引用、不自动插入推荐文献、不自动生成参考文献。

### 1.3 Conservative AI

LLM 只能用于：

- 生成检索 query；
- 辅助解释 mismatch；
- 对 claim-citation 支撑关系进行 triage；
- 帮助用户理解高风险点。

LLM 不得作为最终证据来源。

### 1.4 Evidence-backed

每一个判断都应尽量留下证据来源：

- local parse evidence；
- CrossRef / OpenAlex / Semantic Scholar / PubMed 返回结果；
- match score；
- not-found evidence；
- 用户确认状态；
- report timestamp。

### 1.5 Human-confirmed

V4–V5 中的 claim support 与 citation recommendation 必须是“候选建议”，由用户确认后才能进入正文或文献库。

---

## 2. 版本路线总览

| 阶段 | 版本 | 核心目标 | 是否可商业化 | 主要交付物 |
|---|---|---|---|---|
| 本地安检 | V1.1 | 引用键、BibTeX、字段、log、readiness gate | 可以作为低价服务试水 | `citation-integrity-report.json` |
| 报告增强 | V1.2 | Markdown/CSV 报告、示例项目、文档和小红书 demo | 可以作为标准服务包 | `citation-integrity-report.md` |
| 外部核验 | V2.0 | CrossRef / OpenAlex / Semantic Scholar metadata verification | 可以做“AI 假文献初筛”服务 | `external-verification-report.json` |
| 幻觉筛查 | V3.0 | hallucination risk score，多源一致性判断 | 商业感知最强 | `high-risk-references.csv` |
| 引用支撑复核 | V4.0 | claim-citation support triage | 高客单深度服务 | `claim-citation-support-report.md` |
| 引用推荐 | V5.0 | 基于上下文与用户文献库推荐候选文献 | 适合 Pro / 课题组版 | `candidate-references.json` |

---

## 3. V1.1：本地引用完整性检查

### 3.1 目标

在 `thesis-skills` 现有 `10-check-references` 基础上，升级为可稳定运行的本地 Citation Integrity 检查模块。

### 3.2 核心功能

| 功能 | 输入 | 输出 |
|---|---|---|
| citation key 检查 | `.tex` + `.bib` | 文中引用但 bib 缺失 |
| unused bibliography 检查 | `.bib` + `.tex` | bib 中未被引用条目 |
| duplicate key 检查 | `.bib` | 重复 citation key |
| 多 `.bib` 冲突检查 | 多个 `.bib` | 同 key 不同 metadata |
| required fields 检查 | `.bib` | 缺 author/title/year/journal/doi 等 |
| DOI 格式检查 | `.bib` | DOI 格式异常 |
| year 格式检查 | `.bib` | 年份缺失、异常、未来年份 |
| LaTeX log 解析 | `.log` | undefined citation / empty bibliography warning |
| cross-reference 断链 | `.tex` | `\ref{}` 无 `\label{}`、未使用 label |
| readiness gate 集成 | reports | References 维度 PASS/WARN/BLOCK |

### 3.3 建议目录结构

以最小侵入为原则，优先扩展现有 `10-check-references`，必要时新增 `core/citation_integrity`。

```text
10-check-references/
├── check_references.py
├── README.md
└── examples/

core/
└── citation_integrity/
    ├── __init__.py
    ├── models.py
    ├── tex_parser.py
    ├── bib_parser.py
    ├── latex_log_parser.py
    ├── field_lint.py
    ├── crossref_lint.py
    ├── report.py
    └── readiness_adapter.py

tests/
├── test_citation_integrity_keys.py
├── test_citation_integrity_bib_fields.py
├── test_citation_integrity_latex_log.py
└── test_citation_integrity_readiness.py

examples/
└── citation-integrity-broken/
    ├── main.tex
    ├── refs.bib
    ├── main.log
    └── expected-reports/
```

如果现有仓库已有不同的 core 组织方式，优先遵循当前风格，不强行新建不兼容结构。

### 3.4 报告 Schema

建议输出：

```json
{
  "module": "citation_integrity",
  "version": "1.1",
  "status": "WARN",
  "project_root": "examples/citation-integrity-broken",
  "summary": {
    "tex_files": 3,
    "bib_files": 1,
    "cited_keys": 128,
    "bib_entries": 156,
    "missing_cited_keys": 3,
    "unused_bib_entries": 31,
    "duplicate_bib_keys": 2,
    "field_warnings": 18,
    "latex_log_warnings": 4,
    "cross_reference_warnings": 6
  },
  "issues": [
    {
      "id": "CI-MISSING-KEY-001",
      "severity": "BLOCK",
      "category": "missing_cited_key",
      "message": "Citation key `smith2024` is cited but not found in bibliography files.",
      "file": "main.tex",
      "line": 42,
      "evidence": {
        "citation_key": "smith2024",
        "bib_files_checked": ["refs.bib"]
      },
      "suggested_action": "Add the missing bibliography entry or replace the citation key after manual confirmation."
    }
  ]
}
```

### 3.5 PASS / WARN / BLOCK 规则

| 状态 | 条件 |
|---|---|
| PASS | 所有 cited keys 均解析；无重复 key；必填字段无严重缺失；无 LaTeX citation warning |
| WARN | 有未使用文献、字段缺失、非阻断性 DOI/year 格式问题、未使用 label |
| BLOCK | 文中引用 key 缺失、重复 key metadata 冲突、LaTeX log 明确显示 undefined citation |

### 3.6 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| A1 | 可运行 | `python 10-check-references/check_references.py --project-root examples/citation-integrity-broken` 能生成报告 |
| A2 | 输出稳定 | 生成 `reports/citation-integrity-report.json` |
| A3 | key 检查 | 能识别文中引用但 bib 缺失的 citation key |
| A4 | unused 检查 | 能识别 bib 中未被引用文献 |
| A5 | duplicate 检查 | 能识别重复 citation key |
| A6 | field 检查 | 能识别 author/title/year/journal/doi 缺失或异常 |
| A7 | log 检查 | 能解析 LaTeX log 中的 citation warnings |
| A8 | readiness 集成 | `16-check-readiness` 能把 References 维度标为 PASS/WARN/BLOCK |
| A9 | 测试 | 新增测试全部通过，且不破坏现有测试 |
| A10 | 文档 | README / docs/modules.md 增加 Citation Integrity 使用说明 |

---

## 4. V1.2：报告与用户体验增强

### 4.1 目标

让 V1.1 的检查结果更适合展示、服务交付和小红书传播。

### 4.2 功能

- 输出 Markdown 报告；
- 输出 CSV 风险清单；
- 增加 issue code；
- 增加 “next actions”；
- 增加匿名 demo 报告；
- 增加 `examples/citation-integrity-clean` 与 `examples/citation-integrity-broken` 对比；
- 在 landing page / showcase 中展示报告截图。

### 4.3 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| B1 | Markdown 报告 | `reports/citation-integrity-report.md` 可读、分层清楚 |
| B2 | CSV 输出 | 高风险问题可导出为 `citation-issues.csv` |
| B3 | demo 对比 | clean / broken 两个样例均可运行 |
| B4 | 文档 | 文档中包含 3 个真实场景：LaTeX、Zotero/BibTeX、Word→LaTeX |
| B5 | 展示 | README 中有一段 Citation Integrity preview |

---

## 5. V2.0：外部数据库 Metadata 核验

### 5.1 目标

接入 CrossRef、OpenAlex、Semantic Scholar，对文献真实性与元数据一致性进行多源核验。

### 5.2 数据源

| 数据源 | 用途 |
|---|---|
| CrossRef | DOI、标题、作者、期刊、出版年 |
| OpenAlex | open scholarly works、作者、机构、来源、概念 |
| Semantic Scholar | paper search、citation、abstract、recommendations |
| PubMed | 医学、公共卫生、生命科学方向 |
| DBLP | 计算机方向 |

### 5.3 功能

- DOI 查询；
- title fuzzy search；
- author/year/venue match；
- 多源候选合并；
- 匹配置信度；
- rate limit 与 cache；
- offline fallback；
- 输出 evidence。

### 5.4 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| C1 | CrossRef verifier | DOI 或 title 查询可返回候选 |
| C2 | OpenAlex verifier | title 查询可返回候选 |
| C3 | Semantic Scholar verifier | title 查询可返回候选 |
| C4 | consensus | 能汇总多源结果并给出 match_status |
| C5 | cache | 同一文献重复查询时使用本地缓存 |
| C6 | offline | 无网络/API 失败时不阻断本地检查 |
| C7 | evidence | 每个外部判断保留来源、候选、分数和时间戳 |

---

## 6. V3.0：AI 假文献 / 幻觉引用筛查

### 6.1 目标

基于多源数据库核验结果，输出 hallucination risk score，识别高风险疑似假文献。

### 6.2 风险等级

| 等级 | 含义 |
|---|---|
| PASS | 多源匹配，metadata 基本一致 |
| WARN | 文献存在，但字段差异明显 |
| REVIEW | 可能存在，但匹配证据不足 |
| HIGH_RISK | 多源未找到或字段严重冲突 |
| UNSUPPORTED | 中文文献、学位论文、灰色文献等暂无法自动判定 |

### 6.3 禁止表达

不要输出：

```text
这是假的。
```

应该输出：

```text
HIGH_RISK：未能在已启用数据库中找到可信匹配，建议人工核验 DOI、期刊官网、数据库记录或原文。
```

### 6.4 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| D1 | 风险分数 | 对每条文献输出 hallucination_risk_score |
| D2 | 高风险清单 | 生成 `high-risk-references.csv` |
| D3 | 证据可追溯 | 每条高风险判断有 not-found / mismatch evidence |
| D4 | 不误判中文文献 | 对中文库无法核验文献输出 UNSUPPORTED，而非 HIGH_RISK |
| D5 | demo | 至少 3 个 demo：真实文献字段错误、AI 编造文献、中文文献无法自动判定 |

---

## 7. V4.0：上下文—引用支撑关系检查

### 7.1 目标

检查正文中的关键 claim 与附近 citation cluster 是否存在明显错配。

这一阶段开始使用 LLM，但 LLM 只做 triage，不做最终裁判。

### 7.2 检查类型

| 类型 | 示例 |
|---|---|
| topic mismatch | 正文讲医保支付，引用文献讲 AI coding |
| overclaim | 正文说“显著降低”，引用文献只是观点性综述 |
| outdated support | 正文讨论 2026 工具，引用 2019 工具报告 |
| weak support | title/abstract 相关，但无法确认具体结论 |
| citation needed | 关键断言附近没有引用 |

### 7.3 输入输出

输入：

- 正文段落；
- citation cluster；
- 文献 title / abstract / keywords；
- 用户指定学科领域；
- 可选：用户上传 PDF 摘要或原文片段。

输出：

```text
claim-citation-support-report.md
```

### 7.4 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| E1 | claim extraction | 能抽取段落中的主要 claim |
| E2 | citation cluster | 能识别 claim 附近的 citation keys |
| E3 | metadata linkage | 能获取对应文献 title/abstract/keywords |
| E4 | triage report | 输出 topic mismatch / overclaim / weak support 等标签 |
| E5 | conservative language | 所有判断都标记为“需人工复核”或“可能” |
| E6 | no auto rewrite | 不自动改正文，不自动替换引用 |

---

## 8. V5.0：基于上下文的候选引用推荐

### 8.1 目标

在用户确认下，为缺引用、弱支撑或 topic mismatch 的段落推荐候选文献。

### 8.2 推荐模式

| 模式 | 说明 | 优先级 |
|---|---|---|
| Local Library Recommendation | 从用户已有 BibTeX / Zotero 文献库中推荐 | 最高 |
| Seed Paper Recommendation | 基于用户已引用的 seed paper 扩展推荐 | 高 |
| External Query Search | 用 OpenAlex / Semantic Scholar / PubMed 搜索候选 | 中 |
| LLM-generated Reference | 禁止作为文献来源 | 不做 |

### 8.3 输出

```json
{
  "claim_id": "claim-001",
  "claim_text": "...",
  "candidate_references": [
    {
      "title": "...",
      "authors": [],
      "year": 2024,
      "venue": "...",
      "doi": "...",
      "source": "OpenAlex",
      "match_reason": "topic and methodology match",
      "confidence": "REVIEW",
      "already_in_library": false,
      "user_action": "confirm_before_insert"
    }
  ]
}
```

### 8.4 验收标准

| 编号 | 验收项 | 标准 |
|---|---|---|
| F1 | 本地推荐 | 能从用户已有文献库中推荐候选 |
| F2 | 外部推荐 | 能基于数据库 API 返回候选 |
| F3 | 去重 | 能识别候选是否已在用户文献库中 |
| F4 | 证据 | 每个候选有 DOI/source/match reason |
| F5 | 用户确认 | 不自动插入正文或 bib |
| F6 | 导出 | 可导出 candidate-references.json / .bib candidates |

---

## 9. 商业化探索路线

### 9.1 不要等到 V4–V5 才商业化

商业化应从 V1.1 就开始，但 V1.1–V3 的商业化形式应是“服务 + 报告”，不是 SaaS。

原因：

- 研究生用户最先买的是确定性风险下降，不是复杂 AI 推荐；
- V4–V5 技术不稳定，过早商业化容易承诺过度；
- 引用真实性、假文献筛查、readiness report 更容易形成付费转化；
- V4–V5 更适合作为高客单深度服务或 Pro 功能。

### 9.2 商业化阶段

| 阶段 | 版本 | 商业形式 | 价格试探 | 验证指标 |
|---|---|---|---:|---|
| Beta 服务 | V1.1 | 基础引用安检报告 | 49–99 元 | 10 个付费/咨询 |
| 标准服务 | V1.2–V2 | 引用完整性 + 外部核验 | 199–399 元 | 20 个付费，满意度 >80% |
| 强痛点服务 | V3 | AI 假文献筛查 | 299–799 元 | 转化率、复购、案例数 |
| 深度服务 | V4 | claim-citation 支撑复核 | 999–2999 元 | 课题组/论文作者付费 |
| Pro 工具包 | V5 | 候选引用推荐 + 文献库清洗 | 499–1999 元/次 | 用户是否愿意重复使用 |
| 机构版 | V2–V5 | 课题组/实验室/学院规则包 | 3000–20000 元 | 试点合作数 |

### 9.3 最早可卖的三个服务包

#### 服务包 A：基础引用安检

适合：硕士论文、毕业论文、LaTeX 用户。  
价格试探：49–99 元。  
交付：

- citation key 缺失；
- 未使用文献；
- 重复 key；
- 必填字段缺失；
- DOI/year 格式问题；
- readiness gate 结论。

#### 服务包 B：AI 假文献筛查

适合：使用 AI 写文献综述、开题报告、论文背景的用户。  
价格试探：199–399 元。  
交付：

- 多源数据库核验；
- high-risk references；
- metadata mismatch；
- 人工复核建议。

#### 服务包 C：盲审前引用完整性报告

适合：毕业论文盲审前 1–2 周用户。  
价格试探：399–999 元。  
交付：

- 引用完整性；
- 交叉引用；
- Word/LaTeX 风险；
- 高风险文献；
- readiness report；
- 30 分钟解释。

### 9.4 V4–V5 如何商业化

V4–V5 不适合卖给普通学生做低价工具，而适合卖给：

- 课题组；
- 医学/公共卫生/管理学研究者；
- 论文辅导工作室；
- 科研助理；
- 医院科研部门；
- 系统综述团队。

#### V4 商业化：Claim-Citation Deep Review

卖点：

> 不只是查文献是否存在，而是检查“这句话是否真的适合引用这些文献”。

适合收费：999–2999 元/篇，或按章节收费。

交付：

- 关键 claim 清单；
- 引用支撑强弱；
- overclaim 风险；
- citation needed；
- topic mismatch；
- 人工复核建议。

#### V5 商业化：Citation Candidate Pack

卖点：

> 对缺引用或弱支撑段落，给出可复核候选文献，而不是 AI 编参考文献。

适合收费：499–1999 元/章节，或作为 V4 的加购项。

交付：

- candidate references；
- DOI/source；
- match reason；
- 是否已在用户文献库；
- 建议插入位置；
- BibTeX / CSL JSON 候选导出。

---

## 10. 内容与获客路线

### 10.1 小红书标题方向

```text
AI 写论文最危险的，不是 AI 味，而是假文献
盲审前一定要查：你的参考文献真的存在吗
LaTeX 能编译，不代表引用没问题
Zotero 里有，不代表正文引用对了
Word 转 LaTeX 后，引用最容易坏在哪里
参考文献格式对了，但 DOI 是错的
文献综述最怕的不是少引用，而是错引用
```

### 10.2 GitHub 展示方向

README 中应增加一个 Citation Integrity preview：

```text
References: BLOCK
- 3 cited keys are missing from bibliography files
- 2 duplicate citation keys conflict across bib files
- 7 references have missing DOI or year fields
- 2 references are high-risk hallucination candidates
```

### 10.3 服务转化路径

```text
小红书痛点内容
  ↓
示例报告截图
  ↓
填写表单 / 私信
  ↓
免费初筛 1 页
  ↓
付费完整报告
  ↓
二次转化：PRISMA / thesis-skills / 文献库清洗
```

---

## 11. 风险与边界

### 11.1 技术风险

| 风险 | 处理方式 |
|---|---|
| 中文文献数据库覆盖不足 | 输出 UNSUPPORTED，不判定为假文献 |
| API rate limit | cache + backoff + offline fallback |
| title fuzzy match 误判 | 使用 REVIEW，不直接 BLOCK |
| LLM 判断过度自信 | V4–V5 全部采用 triage 语言 |
| 用户要求自动改文献 | 默认拒绝，最多生成 dry-run patch |

### 11.2 产品边界

不做：

- AI 代写；
- 代发论文；
- 规避查重或 AI 检测；
- 自动生成虚构参考文献；
- 无证据地替换引用；
- 承诺通过盲审或投稿。

---

## 12. 90 天里程碑

### Day 0–30：V1.1

交付：

- 本地引用完整性检查；
- JSON report；
- readiness gate 集成；
- broken demo；
- tests。

验收：

- 可以稳定跑通；
- 能发现 key 缺失、未使用、重复、字段问题；
- 不破坏现有 pipeline。

### Day 31–60：V1.2 + 商业测试

交付：

- Markdown / CSV report；
- 示例报告；
- landing page 文案；
- 3 篇小红书内容；
- 3–5 个真实样本文档测试。

验收：

- 至少 10 个咨询；
- 至少 3 个付费或深度试用；
- 能明确用户最关心的是 key、格式、假文献还是 claim 支撑。

### Day 61–90：V2 原型

交付：

- CrossRef / OpenAlex / Semantic Scholar verifier prototype；
- metadata match score；
- cache；
- external verification report。

验收：

- 对英文 DOI 文献可稳定核验；
- 对无 DOI 文献可 title search；
- 对无法核验中文文献输出 UNSUPPORTED。

---

## 13. 最终路线判断

最适合现在推进的是：

```text
V1.1 引用完整性本地检查
→ V1.2 报告增强与服务化
→ V2 多源 metadata 核验
→ V3 AI 假文献筛查
→ V4 claim-citation 支撑复核
→ V5 候选引用推荐
```

商业化不应等 V4–V5。  
V1.1 开始卖“基础引用安检”；V3 成为最强传播点；V4–V5 变成高客单深度服务。
