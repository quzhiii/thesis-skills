# Thesis Skills 新手入门教程（零基础版）

<div align="center">

![Getting Started](https://img.shields.io/badge/新手入门-零基础版-4285f4?style=for-the-badge&logo=book&logoColor=white)

> 面向 **完全没有 LaTeX 基础** 的同学。  
> 按这份教程走完，你就能在本地把环境装好，然后用 `thesis-skills` 开始检查自己的论文。

[开始前先看这里 →](#先搞清楚你到底在装什么) · [直接跳到安装 →](#第-1-步安装-python) · [常见问题 →](#新人最容易卡住的几个问题)

</div>

---

## 这份教程能帮你做到什么？

学完这篇后，你应该能完成 4 件事：

1. 明白 `LaTeX`、论文模板、`thesis-skills` 三者分别是什么
2. 在本地正确安装一套可用的 LaTeX 环境
3. 跑通一个最小示例，确认环境没问题
4. 开始用 `thesis-skills` 检查你的论文项目

如果你现在只想先跑起来，不追求完全理解，可以直接看：

- [第 1 步：安装 Python](#第-1-步安装-python)
- [第 2 步：安装 LaTeX](#第-2-步安装-latex)
- [第 5 步：下载 thesis-skills](#第-5-步下载-thesis-skills)
- [第 6 步：运行最小检查](#第-6-步运行最小检查)

---

## 先搞清楚：你到底在装什么？

很多同学第一次接触时，容易把下面几样东西混在一起。花 1 分钟看清楚，后面少走很多弯路。

| 名称 | 是什么 | 是否必须安装 |
| :--- | :--- | :--- |
| **LaTeX** | 用来排版论文的"打印系统" | ✅ 必须 |
| **论文模板** | 学校 / 期刊提供的 `.tex` 项目骨架 | ✅ 通常必须 |
| **Python** | 运行 `thesis-skills` 工具的语言环境 | ✅ 必须 |
| **thesis-skills** | 用 Python 写的检查 / 修复脚本集 | ✅ 如果你想自动检查论文 |
| **VS Code** | 代码编辑器（写 `.tex` 最顺手） | 推荐，但不强制 |

### 🏠 最直观的比喻

```
你写论文，就好比你在做饭：

LaTeX           = 厨房（有炉子、有刀、能加热）
论文模板         = 菜谱（告诉你做什么、长什么样）
你的论文内容      = 食材
thesis-skills   = 质检员（帮你查食材是否合格、菜谱是否被正确执行）
```

因此，正确的安装顺序是：

```
┌───────────────────────────────────────────────────────┐
│                                                       │
│   1. 装 Python   →   2. 装 LaTeX   →   3. 装编辑器    │
│                                                       │
│        然后：                                         │
│   4. 下载 thesis-skills   →   5. 跑最小示例           │
│                                                       │
└───────────────────────────────────────────────────────┘
```

---

## 安装路线建议

根据你的操作系统，选一条最短路径：

```
你的操作系统是？
│
├── Windows ──→  TeX Live + VS Code + LaTeX Workshop  ← 本教程重点讲这条
│
├── macOS   ──→  MacTeX   + VS Code + LaTeX Workshop
│
└── Linux   ──→  TeX Live + VS Code + LaTeX Workshop
```

> 💡 对新手而言，**Windows + TeX Live + VS Code** 是踩坑最少的组合，本教程以此为主线，macOS / Linux 的差异会在各步骤中单独说明。

---

## 第 1 步：安装 Python

`thesis-skills` 需要 **Python 3.10 或更高版本**。

### 🔍 先检查你是否已安装

打开终端（Windows 里是 PowerShell 或 CMD，macOS / Linux 里是 Terminal），运行：

```bash
python --version
```

**看到这样的输出，说明已经装好，跳过这步：**

```
Python 3.11.8
```

**看到"找不到命令"，需要安装：**

```
'python' is not recognized as an internal or external command
```

### 📥 下载并安装 Python

访问官网：<https://www.python.org/downloads/>

下载最新稳定版并运行安装程序。

### ⚠️ Windows 用户必做：勾选 PATH

安装程序启动后，第一个界面有个非常重要的选项：

```
┌─────────────────────────────────────────────────┐
│  Install Python 3.xx                            │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  □ Install launcher for all users       │   │
│  │                                         │   │
│  │  ☑ Add python.exe to PATH    ← 必须勾选  │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
│  [Install Now]   [Customize installation]       │
└─────────────────────────────────────────────────┘
```

> ⚠️ **如果忘记勾选 `Add python.exe to PATH`，之后运行 `python` 命令时会一直报"找不到命令"。**  
> 解决方法：卸载后重新安装，这次记得勾选。

<!-- 截图提示：docs/images/python-install-path.png
     建议截取：Python 安装首页，圈出 "Add python.exe to PATH" 选项 -->

### ✅ 安装后验证

关闭终端，重新打开一个新终端，再次运行：

```bash
python --version
```

看到版本号即成功。

---

## 第 2 步：安装 LaTeX

这是整个流程里**最关键也最耗时**的一步。

LaTeX 的安装包（称为"发行版"）比较大，完整安装通常需要 5–10 GB 磁盘空间，安装时间视网速而定，可能需要 30 分钟到 2 小时。

---

### 方案 A：Windows 安装 TeX Live（推荐）

#### 你将获得什么？

安装完成后，你的电脑会具备：

```
TeX Live 2024
├── xelatex     ← 中文论文首选编译器
├── pdflatex    ← 英文论文常用编译器
├── bibtex      ← 参考文献处理
├── biber       ← 更现代的参考文献处理
└── 数千个宏包  ← 几乎不会再缺包
```

#### 安装步骤

**① 访问下载安装器（国内用户优先用镜像站）：**

> **推荐（国内访问更快）：** <https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/texlive/>

> **官网（备选）：** <https://www.tug.org/texlive/acquire-netinstall.html>

进入清华镜像站后，找到：
- `install-tl-windows.exe` —— Windows 在线安装器
- 或 `tlnet/` 目录下的安装包

**提示**：如果镜像站访问慢，也可以尝试：
- 北外镜像：<https://mirrors.bfsu.edu.cn/CTAN/systems/texlive/>
- 阿里云镜像：<https://mirrors.aliyun.com/CTAN/systems/texlive/>

**② 双击运行，等待加载后看到主界面：**

```
┌─────────────────────────────────────────────────────┐
│  TeX Live 2024 Installer                            │
│                                                     │
│  Installation root:  C:\texlive\2024               │
│  Selected scheme:    scheme-full  ← 保持默认        │
│  Disk space required: ~8.9 GB                       │
│                                                     │
│  [Advanced]   [Install]    ← 直接点 Install         │
└─────────────────────────────────────────────────────┘
```

<!-- 截图提示：docs/images/texlive-installer-main.png
     建议截取：TeX Live 安装主界面，圈出 scheme-full 和 Install 按钮 -->

**③ 点击 `Install`，耐心等待（30 分钟到 2 小时）。**

安装过程中你会看到类似进度：

```
Installing: 1234 / 4567 packages ...
[ ##########                    ]  27%
```

**④ 安装完成后，看到成功提示：**

```
Welcome to TeX Live!
The TeX Live web site (https://tug.org/texlive/) contains ...
```

#### 为什么推荐完整安装（scheme-full）？

新手最常见的折磨不是"磁盘不够"，而是：

- 编译时报 `! LaTeX Error: File 'xxx.sty' not found.`
- 中文字体支持残缺
- 某个模板依赖的宏包没装

完整安装一次性解决这些问题，省去后续频繁补包的痛苦。

#### ✅ 验证

打开**新的**终端，运行：

```bash
xelatex --version
```

成功输出示例：

```
XeTeX 3.141592653-2.6-0.999995 (TeX Live 2024/W32TeX)
...
```

---

### 方案 B：Windows 安装 MiKTeX（可选）

MiKTeX 体积较小，会在编译时**自动下载缺失宏包**，对网络有依赖但初始安装快。

官网：<https://miktex.org/download>

安装后验证：

```bash
xelatex --version
```

> 💡 如果你使用清华、交大、中科大等高校中文模板，TeX Live 完整安装往往更稳定，推荐优先选择方案 A。

---

### 方案 C：macOS 安装 MacTeX

**① 下载安装包（国内用户优先用镜像站）：**

> **推荐（国内访问更快）：** <https://mirrors.tuna.tsinghua.edu.cn/CTAN/systems/mac/mactex/>

> **官网（备选）：** <https://www.tug.org/mactex/>

在清华镜像站找到 `MacTeX.pkg`（约 4 GB），下载后双击安装，按引导操作。

**提示**：如果镜像站访问慢，也可以尝试：
- 北外镜像：<https://mirrors.bfsu.edu.cn/CTAN/systems/mac/mactex/>

**② 安装后验证：**

```bash
xelatex --version
```

<!-- 截图提示：docs/images/mactex-installer.png
     建议截取：MacTeX 安装引导第一页 -->

---

### 方案 D：Linux 安装 TeX Live

不同发行版安装命令不同。

#### Ubuntu / Debian

使用清华镜像源加速：

```bash
# 添加清华镜像源
sudo sed -i 's|http://.*ubuntu\.com|https://mirrors.tuna.tsinghua.edu.cn|' /etc/apt/sources.list

# 更新并安装
sudo apt update
sudo apt install texlive-full
```

或者直接用默认源（可能较慢）：

```bash
sudo apt install texlive-full
```

#### Fedora

```bash
sudo dnf install texlive-scheme-full
```

#### Arch Linux

```bash
sudo pacman -S texlive-most
```

**提示**：如果安装过程下载太慢，可以搜索对应发行版 "换源 清华镜像"。

安装后验证：

```bash
xelatex --version
```

---

## 第 3 步：安装编辑器（推荐但非强制）

你当然可以用记事本写 `.tex` 文件，但有一个好编辑器会让写论文体验好很多。

### 推荐：VS Code + LaTeX Workshop

#### ① 安装 VS Code

官网：<https://code.visualstudio.com/>

下载对应平台的安装包，按引导安装即可。

#### ② 安装 LaTeX Workshop 插件

打开 VS Code，按快捷键 `Ctrl+Shift+X`（macOS 是 `Cmd+Shift+X`）打开插件市场：

```
┌─────────────────────────────────────────────────────┐
│  扩展  [ 搜索框：输入 LaTeX Workshop ]               │
│  ─────────────────────────────────────────────────  │
│  📦  LaTeX Workshop                                 │
│      James Yu · ★ 4.9M 下载                        │
│      [安装]    ← 点这个                             │
│                                                     │
│  📦  LaTeX language support                         │
│      ...                                            │
└─────────────────────────────────────────────────────┘
```

<!-- 截图提示：docs/images/vscode-latex-workshop.png
     建议截取：VS Code 插件页面，搜索结果中的 LaTeX Workshop，圈出安装按钮 -->

#### ③ 你将获得什么？

安装完成后，打开 `.tex` 文件，你会发现：

```
VS Code 侧边栏多了 TeX 图标  ← 显示文档大纲、编译状态
右上角有 ▶ Build 按钮        ← 一键编译
右侧内置 PDF 预览            ← 不需要外部 PDF 阅读器
错误高亮                     ← 编译错误直接在编辑器里标红
Ctrl+点击引用                ← 跳转到参考文献条目
```

---

## 第 4 步：验证 LaTeX 环境

**不要一装完就直接上手你的正式论文。**  
先用本仓库内置的最小示例项目验证环境，能大幅降低排查难度。

### 项目结构

仓库里已经内置了一个最小 LaTeX 项目：

```
examples/minimal-latex-project/
│
├── main.tex                 ← 主文件（入口）
├── abstract.tex             ← 摘要
├── chapters/
│   ├── 01-introduction.tex  ← 第一章
│   └── 02-methods.tex       ← 第二章
└── ref/
    └── refs.bib             ← 参考文献库
```

`main.tex` 的内容非常简单：

```tex
\documentclass{article}
\begin{document}
\tableofcontents
\input{chapters/01-introduction}
\input{chapters/02-methods}
\bibliographystyle{plain}
\bibliography{ref/refs}
\end{document}
```

### 用命令行编译

进入该目录，执行完整编译链：

```bash
cd examples/minimal-latex-project

xelatex main.tex    # 第一遍：生成辅助文件
bibtex main         # 处理参考文献
xelatex main.tex    # 第二遍：写入参考文献
xelatex main.tex    # 第三遍：修正交叉引用
```

> 💡 为什么要跑 3 遍 `xelatex`？  
> 因为 LaTeX 的目录、引用编号、参考文献需要多次编译才能完全同步。这是 LaTeX 的正常工作方式，不是 bug。

### 用 VS Code 编译

在 VS Code 里打开 `main.tex`，按 `Ctrl+Alt+B`（macOS 是 `Cmd+Alt+B`）触发编译，LaTeX Workshop 会自动完成多次编译。

### ✅ 成功标志

编译成功后，目录里会出现：

```
examples/minimal-latex-project/
├── main.pdf    ← 这个文件出现了，说明 LaTeX 环境正常！
├── main.aux
├── main.bbl
└── ...（其他辅助文件）
```

<!-- 截图提示：docs/images/minimal-project-pdf.png
     建议截取：VS Code 中 main.pdf 预览效果，或文件夹里出现 main.pdf 的截图 -->

---

## 第 5 步：下载 thesis-skills

### 方式一：用 Git 克隆（推荐）

```bash
git clone https://github.com/quzhiii/thesis-skills.git
cd thesis-skills
```

### 方式二：直接下载 ZIP

如果你没有安装 Git：

```
1. 打开 https://github.com/quzhiii/thesis-skills
2. 点击绿色的 [Code ▼] 按钮
3. 点击 [Download ZIP]
4. 解压到你想放的目录
5. 进入解压后的目录
```

```
┌─────────────────────────────────────────────────────┐
│  github.com/quzhiii/thesis-skills                   │
│                                                     │
│  [Code ▼]   ← 点这里                               │
│  ┌─────────────────────────────────┐               │
│  │  Clone                          │               │
│  │  HTTPS: https://github.com/...  │               │
│  │                                 │               │
│  │  [Download ZIP]  ← 或者点这里   │               │
│  └─────────────────────────────────┘               │
└─────────────────────────────────────────────────────┘
```

<!-- 截图提示：docs/images/github-download-zip.png
     建议截取：GitHub 仓库页面展开 Code 下拉菜单，圈出 Download ZIP -->

---

## 第 6 步：运行最小检查

这是你第一次使用 `thesis-skills` 时最推荐的命令：

```bash
python run_check_once.py \
  --project-root examples/minimal-latex-project \
  --ruleset university-generic \
  --skip-compile
```

逐段解释：

```
python run_check_once.py        ← 调用项目的检查入口脚本
  --project-root                ← 指定要检查的论文项目目录
    examples/minimal-latex-project   ← 先用内置示例项目
  --ruleset university-generic  ← 使用通用高校论文规则包
  --skip-compile                ← 先跳过编译，只检查结构/格式
```

### 为什么先加 `--skip-compile`？

让 `thesis-skills` 和 LaTeX 编译解耦，分开排查：

```
不加 --skip-compile：thesis-skills 检查 + LaTeX 编译，两个问题混在一起
加   --skip-compile：只跑 thesis-skills 检查，问题更容易定位
```

新手建议先加，等确认工具本身能跑起来，再去掉这个参数。

### 看到报告输出，就说明成功了

运行后你会看到类似：

```
[thesis-skills] Checking project: examples/minimal-latex-project
[check-references] ✓ No missing citation keys
[check-language]   ✓ 0 issues found
[check-format]     ! 2 issues found
  → figures/fig1.png: caption not centered
  → table 3: missing \label
[check-content]    ✓ Required sections present
```

<!-- 截图提示：docs/images/run-check-output.png
     建议截取：终端中运行 run_check_once.py 后的完整输出 -->

---

## 第 7 步：接入你自己的论文项目

当你确认示例项目能跑通后，把 `--project-root` 换成你自己的论文目录：

```bash
python run_check_once.py \
  --project-root "你的论文目录路径" \
  --ruleset tsinghua-thesis \
  --skip-compile
```

### 可用的规则包

仓库内置了三个 starter：

```
90-rules/packs/
├── university-generic/    ← 通用高校，不确定用哪个先用这个
├── journal-generic/       ← 通用期刊
└── tsinghua-thesis/       ← 清华大学示例
```

如果你不是清华模板，先用 `university-generic`：

```bash
--ruleset university-generic
```

等你熟悉工具后，再从它派生出属于自己学校的规则包：

```bash
python 90-rules/create_pack.py \
  --pack-id my-university \
  --display-name "我的大学论文" \
  --starter university-generic \
  --kind university-thesis
```

---

## 完整工作流一览

用一张图看清楚 `thesis-skills` 的五层架构，对应你写论文的各个阶段：

```
你的论文写作阶段                      thesis-skills 对应模块
──────────────────────────────────────────────────────────────

① 建立参考文献库
   · 从 EndNote 导出                ─→  00-bib-endnote
   · 从 Zotero 同步                 ─→  00-bib-zotero

② Word 草稿 → LaTeX 迁移            ─→  01-word-to-latex

③ 检查阶段
   · 引用完整性                     ─→  10-check-references
   · 语言规范（基础）                ─→  11-check-language
   · 格式（图表、章节结构）          ─→  12-check-format
   · 内容完整性                     ─→  13-check-content
   · 语言规范（深度）                ─→  14-check-language-deep

④ 修复阶段
   · 自动修复引用                   ─→  20-fix-references
   · 自动修复语言                   ─→  21-fix-language-style
   · 自动修复格式                   ─→  22-fix-format-structure
   · 深度语言补丁                   ─→  24-fix-language-deep

⑤ 规则包管理                        ─→  90-rules
```

### 新手推荐工作顺序

```
第一次使用时：
Step 1  先 check-references   →  把缺引用、孤立引用全清干净
Step 2  再 check-format        →  图表格式、章节结构
Step 3  再 check-language      →  语言问题
Step 4  最后 check-content     →  摘要、关键词等结构性检查
```

---

## 常用命令速查

```bash
# ── 日常检查（先用这个）──────────────────────────────────────
python run_check_once.py \
  --project-root "论文目录" \
  --ruleset university-generic \
  --skip-compile

# ── 查看有哪些问题，但不修改文件（干跑模式）────────────────────
python run_fix_cycle.py \
  --project-root "论文目录" \
  --ruleset tsinghua-thesis \
  --apply false

# ── 确认没问题后，实际执行修复 ─────────────────────────────────
python run_fix_cycle.py \
  --project-root "论文目录" \
  --ruleset tsinghua-thesis \
  --apply true

# ── Zotero 文献从 Word 同步到 LaTeX ─────────────────────────────
python 00-bib-zotero/sync_from_word.py \
  --project-root "论文目录" \
  --word-file thesis.docx \
  --apply

# ── EndNote 导入文献 ──────────────────────────────────────────
python 00-bib-endnote/import_library.py \
  --project-root "论文目录" \
  --input refs.xml \
  --apply
```

---

## 新人最容易卡住的几个问题

### ❌ `python` 找不到

**现象：**

```
'python' is not recognized as an internal or external command
```

**原因和解决方法：**

```
原因：Python 安装时没有勾选 Add to PATH，或安装后没有重启终端

解决：
  1. 重新打开终端（重要！）
  2. 还是不行 → 重新安装 Python，这次务必勾选 Add python.exe to PATH
```

---

### ❌ `xelatex` 找不到

**现象：**

```
'xelatex' is not recognized as an internal or external command
```

**原因和解决方法：**

```
原因：TeX Live 安装未完成，或安装后 PATH 未刷新

解决：
  1. 重新打开终端（重要！）
  2. 还是不行 → 检查 TeX Live 是否安装完成
     → Windows：开始菜单搜索 TeX Live Manager
     → 如果找不到，说明 TeX Live 没装好，重装
```

---

### ❌ 编译时报"找不到宏包"

**现象：**

```
! LaTeX Error: File 'ctex.sty' not found.
```

**原因和解决方法：**

```
原因：TeX Live 安装时没有选 full scheme，缺少宏包

解决（TeX Live 用户）：
  tlmgr install ctex

解决（MiKTeX 用户）：
  MiKTeX 会自动弹窗询问是否安装，点确认即可

根本解法：重装 TeX Live，选择 scheme-full（完整安装）
```

---

### ❌ 编译中文时乱码或无法显示

**现象：**

```
PDF 生成了，但中文全是方块或空白
```

**原因和解决方法：**

```
原因：使用了 pdflatex 编译中文，而 pdflatex 不直接支持中文

解决：改用 xelatex 编译
  xelatex main.tex        ← 而不是 pdflatex main.tex
```

---

### ❌ `thesis-skills` 报告很多问题

```
原因：这通常不是坏事，反而说明工具在正常工作

建议处理顺序：
  1. 先处理引用问题（check-references）
  2. 再处理格式问题（check-format）
  3. 最后处理语言问题（check-language）

不要一次性全部修改，先 dry-run（--apply false）预览再执行
```

---

### ❌ 我不是清华模板，能用吗？

```
可以！

先用：--ruleset university-generic
等熟悉工具后，创建自己学校的规则包：

python 90-rules/create_pack.py \
  --pack-id my-school \
  --display-name "我的学校论文" \
  --starter university-generic \
  --kind university-thesis
```

---

## 给新人的 3 天上手计划

### Day 1：先把环境装对

```
□ 安装 Python 3.10+
□ 验证：python --version
□ 安装 TeX Live（完整安装）
□ 验证：xelatex --version
□ 安装 VS Code + LaTeX Workshop
```

### Day 2：先跑通示例

```
□ 克隆 thesis-skills 仓库
□ 打开 examples/minimal-latex-project/main.tex
□ 用 VS Code 或命令行编译出 main.pdf
□ 看到 main.pdf，说明 LaTeX 环境 OK
```

### Day 3：接入真实论文

```
□ 运行最小检查命令（先用内置示例）：
  python run_check_once.py \
    --project-root examples/minimal-latex-project \
    --ruleset university-generic \
    --skip-compile

□ 把 --project-root 换成自己的论文目录
□ 阅读报告，按优先级处理问题
```

---

## 一张图总结整个上手路径

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│    🐍 安装 Python 3.10+                                  │
│                ↓                                         │
│    📦 安装 TeX Live / MacTeX                             │
│                ↓                                         │
│    ✅ 验证：xelatex --version                            │
│                ↓                                         │
│    📝 打开最小示例，编译出 PDF                           │
│                ↓                                         │
│    📥 克隆 thesis-skills 仓库                            │
│                ↓                                         │
│    🔍 运行 run_check_once.py（先用示例项目）              │
│                ↓                                         │
│    🎯 换成你自己的论文目录，开始真正使用                  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## 接下来你可以读什么？

| 文档 | 用途 |
| :--- | :--- |
| [README.zh-CN.md](../README.zh-CN.md) | 项目全貌、功能模块概览 |
| [docs/architecture.md](./architecture.md) | 五层架构详细说明 |
| [examples/minimal-latex-project](../examples/minimal-latex-project) | 内置最小项目，可以随意改 |
| [90-rules/packs/university-generic](../90-rules/packs/university-generic) | 通用规则包，可以作为自定义起点 |

---

## 维护者：后续可补充的截图

如果你想让这份教程更"图文并茂"，建议后续补充以下截图到 `docs/images/`：

| 文件名 | 建议截取内容 |
| :--- | :--- |
| `python-install-path.png` | Python 安装页面，圈出 `Add python.exe to PATH` |
| `texlive-installer-main.png` | TeX Live 安装主界面，圈出 `scheme-full` 和 `Install` 按钮 |
| `mactex-installer.png` | MacTeX 安装引导首页 |
| `vscode-latex-workshop.png` | VS Code 插件市场，搜索结果里的 LaTeX Workshop |
| `minimal-project-pdf.png` | VS Code 中 `main.pdf` 的预览效果 |
| `github-download-zip.png` | GitHub 页面展开 Code 下拉，圈出 Download ZIP |
| `run-check-output.png` | 终端里运行 `run_check_once.py` 后的完整输出 |

插入方式（替换对应注释行即可）：

```markdown
![TeX Live 安装界面](./images/texlive-installer-main.png)
```

---

> 💬 **最后一句话给新手：**  
> 不要一开始就想"完全学会 LaTeX"。先把环境装好、把最小示例编译出来、再把 `thesis-skills` 接到你的论文上——这样你的学习曲线会平缓很多。  
> 遇到问题先看本文末尾的 [常见问题](#新人最容易卡住的几个问题) 部分，通常都能找到解法。
