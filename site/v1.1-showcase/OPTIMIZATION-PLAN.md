# Thesis Skills 展示页 v1.1 优化计划

## 1. 当前状态诊断

### 1.1 已具备的基础（保留）

- **视觉系统成熟**：`editorial-theme.css` 建立了完整的学术风格设计体系，配色克制、排版有层次、响应式已覆盖
- **边界意识到位**：现有页面已明确写出"不生成论文正文、不替代导师判断"等关键边界
- **内容骨架完整**：首页、场景页、输出页、文档页、两个场景详情页已形成完整结构
- **技术约束合理**：纯静态 HTML+CSS，无构建步骤，适合当前项目气质

### 1.2 核心问题（需解决）

| 问题 | 具体表现 | 影响 |
|---|---|---|
| 首屏转化弱 | 标题偏理念表达，没有直接展示命令或artifact | 新用户10秒内难以判断"这对我有没有用" |
| artifact展示不完整 | gallery只展示答辩准备5个模块，缺少检查报告、readiness gate等核心输出 | 你无法看到完整流程的价值 |
| 缺少快速试跑入口 | 首页只有一个命令行片段，没有独立的quickstart页面 | 你难以在3分钟内完成第一次运行 |
| 场景页缺少落点 | 场景卡片只有文字说明，没有明确的"输入-命令-输出"结构 | 你知道阶段但不知道怎么动手 |
| 导航不一致 | 不同页面的nav链接数量和内容不统一 | 浏览时感到不连贯 |
| 缺少Before/After | 没有直观对比"用之前vs用之后"的状态差异 | 难以建立"这能帮我解决什么问题"的直观认知 |

---

## 2. 优化目标

把展示页从"项目说明页"升级为"研究生第一次接触时能快速判断、快速定位、快速试跑、快速相信"的产品入口。

核心指标：

| 目标 | 判断标准 |
|---|---|
| 10秒理解 | 你能说出它解决"论文收尾的可检查输出"问题 |
| 30秒定位 | 你能找到自己对应的论文阶段 |
| 1分钟建立信任 | 你能看到真实artifact输出 |
| 3分钟试跑 | 你能复制命令跑出demo |
| 5分钟深入 | 你能进入对应文档或GitHub模块 |

---

## 3. 新信息架构

```
site/v1.1-showcase/
├── editorial-theme.css          # 继承并微调现有主题
├── index.html                   # 首页：产品定位 + 3分钟试跑 + artifact证据
├── quickstart.html              # 【新增】3分钟跑通最小示例
├── scenario-entry.html          # 按论文阶段进入（增强：增加输入-命令-输出）
├── artifact-gallery.html        # 【改版】全流程artifact gallery（6类输出）
├── rule-packs.html              # 【新增】规则包说明与贡献入口
├── boundaries.html              # 【新增】边界与不承诺（独立页面提高可信度）
├── docs-home.html               # 文档入口（退到二级，简化首屏）
├── advisor-handoff.html         # 交导师场景（保留，从scenario引流）
├── submission-prep.html         # 送审前场景（保留，从scenario引流）
└── README.md                    # 本目录说明
```

### 3.1 导航统一

所有页面顶部导航统一为6个入口：

```
首页 | 场景入口 | 输出样例 | 快速上手 | 文档 | GitHub
```

---

## 4. 各页面调整方案

### 4.1 首页 (index.html)

#### 当前问题
- 标题"论文不是只靠最后通读，而是靠一串可检查的文件推进"偏理念表达
- 第一屏缺少可直接看到的命令或artifact证据
- CTA只有"看当前能力"和"去文档入口"，缺少"直接试跑"
- 6个workflow卡片平铺，没有形成流程感

#### 改版结构

**第一屏（Hero）**
```
左侧：
  Badge: Thesis Skills v1.0.0 · CLI-first · MIT · Python 3.10+
  H1: 把论文收尾变成一组可检查的文件
  Subhead: 文献接入、Word/LaTeX 交接、检查修复、readiness gate、答辩前整理，一条确定性 CLI 工作流。
  CTA:
    [3 分钟跑通示例] → quickstart.html
    [查看真实输出] → artifact-gallery.html
    [按论文阶段进入] → scenario-entry.html

右侧：
  terminal mockup + readiness report 卡片（静态展示）
```

**第二屏：三类用户入口**
```
我正在写论文 → 按阶段找流程（去scenario-entry）
我准备提交/送审 → 看readiness gate和final packet（去submission-prep）
我想改造/贡献规则包 → 看rule pack和模块结构（去rule-packs）
```

**第三屏：核心workflow流程**
```
Intake → Convert/Handoff → Check → Fix Preview → Gate → Defense/Submit

每步展示：输入 | 动作 | 输出 | 边界
```

**第四屏：真实artifact预览**
```
嵌入3个最有说服力的小样例（8-12行）：
1. readiness-report.json
2. check_language-report.json
3. defense/review artifact

每个样例底部："查看完整解释 →" 链接到artifact-gallery
```

**第五屏：Boundary block**
```
不生成论文正文
不替代导师判断
不保证所有学校规则
不自动完成最终PPT
```

**第六屏：Closing CTA**
```
[去场景入口] [去快速上手] [查看GitHub]
```

---

### 4.2 快速上手页 (quickstart.html) 【新增】

页面目标：让第一次访问者3分钟跑通最小示例。

结构：
1. **Requirements** - Python 3.10+, git
2. **Clone** - `git clone` 命令
3. **Run demo** - 完整命令（带注释说明每个参数）
4. **Expected output** - 文件树 + 每个文件的用途说明
5. **First files to inspect** - 先看哪几个报告，重点看什么
6. **Common failure notes** - 常见报错和解决方式
7. **Next step links** - 去场景入口 / 去输出样例 / 去文档

设计要点：
- 命令行区块使用深色背景，突出可复制的命令
- 文件树使用等宽字体，模拟真实终端输出
- 每个步骤有明确的"预期结果"说明

---

### 4.3 输出样例页 (artifact-gallery.html) 【改版】

#### 当前问题
- 只展示答辩准备的5个模块
- 缺少检查报告、readiness gate等核心输出展示
- 没有展示"完整流程"概念

#### 改版结构

  页面标题：**每一步都留下可检查的输出**

**01 文献接入输出**
- 输入：EndNote XML / Zotero / BibTeX
- 输出：citation mapping、duplicate warning、refs-import.bib
- 适合：文献库混乱、编号漂移
- 样例片段：citation mapping JSON

**02 检查报告输出**
- check_references-report.json
- check_language-report.json
- check_format-report.json
- check_content-report.json
- 每个报告展示8-10行样例

**03 修复预览输出**
- dry-run patch preview
- safe / suggest / mixed mode
- 重点展示"不会静默乱改"

**04 Readiness gate**
- PASS / WARN / BLOCK 样例
- blockers / warnings / next actions
- source references

**05 Review handoff**
- review diff
- feedback ingest
- TODO artifact
- advisor handoff packet

**06 Defense prep**
- 保留现有5个defense模块
- defense outline、chapter highlights、figure inventory、candidate tables/diagrams、talk prep notes

每个artifact card必须包含：
- 输入
- 命令（复制即用）
- 输出路径
- 样例片段（8-12行）
- 使用时机
- 边界说明

---

### 4.4 场景入口页 (scenario-entry.html) 【增强】

#### 当前问题
- 场景卡片只有文字说明
- 缺少"输入-运行-输出"的落点
- 你知道阶段但不知道怎么动手

#### 增强方案

保留现有5个阶段卡片结构，在每个卡片底部新增三个固定字段：

```
输入：你需要准备什么
运行：复制哪条命令
输出：会得到哪个artifact
```

示例（"定稿前最后一遍检查"卡片）：
```
输入：一个 LaTeX 项目 + ruleset
运行：python run_check_once.py --project-root thesis --ruleset university-generic --skip-compile
输出：reports/run-summary.json + reports/readiness-report.json
```

---

### 4.5 规则包页 (rule-packs.html) 【新增】

页面目标：解释规则包是什么、适合谁、如何扩展。

结构：
1. **什么是 rule pack** - 学校/期刊规则包的定义
2. **适合谁** - 进阶用户和潜在贡献者
3. **内置规则包** - university-generic、journal-generic、tsinghua-thesis、demo-university-thesis
4. **如何创建** - 从university-generic创建的命令示例
5. **如何贡献** - 提交新规则包的流程
6. **重要说明** - tsinghua-thesis只是示例，不代表覆盖所有学校

---

### 4.6 边界页 (boundaries.html) 【新增】

页面目标：独立、清晰地展示能力边界，提高可信度。

结构：
1. **明确不做什么**（避免被误解为AI写论文工具）
2. **明确做什么**（确定性工作流、可检查输出）
3. **适合谁 / 不适合谁**
4. **使用前提**（已有论文项目、已有LaTeX基础等）

---

### 4.7 文档首页 (docs-home.html) 【简化】

#### 调整方向
- 从一级转化入口退到二级
- 简化首屏，减少阅读线数量
- 突出"你已经决定深入了解"的定位

#### 简化方案
- 保留核心文档入口（README、Quickstart、Architecture、Examples）
- 减少阅读线数量（从4条减少到2-3条）
- 增加"刚接触？先去快速上手"的提示

---

### 4.8 保留页面（不做大改）

- **advisor-handoff.html** - 内容完整，从scenario-entry引流即可
- **submission-prep.html** - 内容完整，从scenario-entry引流即可

---

## 5. 视觉调整方案

### 5.1 继承现有设计系统

- 继续使用 `editorial-theme.css` 的配色和排版
- 保持学术风格，不走向营销风
- 保持响应式断点（1180px、980px、720px）

### 5.2 新增/调整的元素

| 元素 | 调整方式 |
|---|---|
| Terminal mockup | 新增深色代码块样式，模拟终端输出 |
| Artifact卡片 | 统一为"输入-命令-输出-样例"结构 |
| Before/After | 新增对比区块，Before用浅灰，After用正常色 |
| Quickstart步骤 | 新增编号步骤样式，突出可复制命令 |
| Rule pack卡片 | 新增简单的网格卡片展示 |

### 5.3 CSS微调（在editorial-theme.css基础上）

新增以下样式类（不破坏现有）：

```css
/* Terminal/code block dark theme */
.terminal-block { ... }

/* Artifact card structure */
.artifact-card { ... }
.artifact-input { ... }
.artifact-command { ... }
.artifact-output { ... }

/* Step-by-step for quickstart */
.step-list { ... }
.step-item { ... }

/* Before/After comparison */
.compare-grid { ... }
.compare-before { ... }
.compare-after { ... }
```

---

## 6. 内容用语规范

### 6.1 避免AI感重的表达

| 避免 | 改用 |
|---|---|
| "不是...，而是..." | 直接陈述"它做什么" |
| "旨在" | "用于" |
| "旨在帮助用户" | "帮你..." |
| "通过...实现" | "用...来" |
| "赋能" | 删掉 |
| "解决方案" | "工具" / "流程" |

### 6.2 保持的语调

- 直接、具体、有边界
- 像工程师写文档，像产品经理写说明
- 不夸大，不承诺做不到的事
- 用"你"而不是"用户"

---

## 7. 实施阶段

### P0：核心转化流程（必须完成）

1. **创建新目录** `site/v1.1-showcase/`
2. **复制基础文件** - editorial-theme.css、保留页面
3. **改版首页** - 新增hero右侧terminal mockup、三类用户入口、workflow流程、artifact预览、boundary block
4. **新增 quickstart.html** - 3分钟跑通最小示例
5. **改版 artifact-gallery.html** - 从答辩输出扩展到全流程6类artifact
6. **增强 scenario-entry.html** - 每个场景卡增加"输入-命令-输出"
7. **统一导航** - 所有页面导航统一为6个入口
8. **微调CSS** - 新增terminal、artifact-card、step等样式

### P1：增强证据感（重要但可延后）

1. **生成真实demo artifacts** - 从examples/minimal-latex-project运行并提取JSON片段
2. **嵌入真实JSON样例** - 替换当前mock数据
3. **新增 Before/After 区块** - 在首页和artifact-gallery加入对比
4. **移动端检查** - 375px宽度下测试所有页面

### P2：扩展与传播（可做可不做）

1. **新增 rule-packs.html** - 规则包说明与贡献
2. **新增 boundaries.html** - 独立边界页面
3. **简化 docs-home.html** - 退到二级入口
4. **准备英文首页草稿** - 仅翻译首页和artifact gallery核心内容

---

## 8. 验收标准

| 检查项 | 通过标准 |
|---|---|
| 首屏 | 10秒内能看懂项目解决"论文收尾的可检查输出"问题 |
| CTA | 首页首屏有且只有2-3个主要行动 |
| Quickstart | 不读README也能跑通demo |
| Artifact | 至少展示6类真实输出或准真实输出 |
| 边界 | 明确写出不生成论文正文、不替代导师判断 |
| 移动端 | 首页、gallery、scenario页面在手机上不出现横向溢出 |
| 一致性 | README、site、docs版本号与模块路径一致 |
| 导航 | 所有页面导航一致，内部链接有效 |

---

## 9. 技术实施要点

### 9.1 文件复制策略

```bash
# 1. 复制现有主题
cp site/editorial-theme.css site/v1.1-showcase/editorial-theme.css

# 2. 复制保留页面
cp site/advisor-handoff.html site/v1.1-showcase/
cp site/submission-prep.html site/v1.1-showcase/

# 3. 改版页面（基于现有修改）
cp site/index.html site/v1.1-showcase/index.html
# ...然后修改
cp site/artifact-gallery.html site/v1.1-showcase/artifact-gallery.html
# ...然后修改
cp site/scenario-entry.html site/v1.1-showcase/scenario-entry.html
# ...然后修改
cp site/docs-home.html site/v1.1-showcase/docs-home.html
# ...然后简化

# 4. 新增页面
# quickstart.html, rule-packs.html, boundaries.html
```

### 9.2 本地预览

```bash
cd site/v1.1-showcase
python -m http.server 8081
```

访问 http://localhost:8081

### 9.3 部署方式

开发完成后：
1. 确认所有页面在本地预览正常
2. 将 `site/v1.1-showcase/` 内容复制到 `site/` 根目录（或保持独立目录并通过GitHub Pages配置部署）
3. 更新 `site/README.md`

---

## 10. 风险评估

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| 新增页面工作量超预期 | P0延期 | P0聚焦核心3页（首页、quickstart、gallery），其余可延后 |
| CSS兼容性问题 | 移动端显示异常 | 每个页面在375px、768px、1280px下测试 |
| 内容与实际代码不一致 | 误导你 | 所有命令和输出路径必须与README、docs/modules.md一致 |
| 用语风格不统一 | 阅读感受割裂 | 统一用语规范，避免AI感表达 |

---

*计划制定时间：2026-04-29*
*目标版本：v1.1 showcase*
*核心原则：原版不动，在新目录独立开发，验证后再切换*
