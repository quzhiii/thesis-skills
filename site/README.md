# Thesis Skills 静态站点

这是 Thesis Skills 当前 v1.0.0 public-story / docs / showcase 入口的静态页面目录，用于帮助潜在用户快速了解项目定位、使用场景、artifact 示例和能力边界。

## 文件结构

```text
site/
├── editorial-theme.css       # 统一的 v1.0 展示主题样式
├── index.html                # 首页与 v1.0 public-story 入口
├── scenario-entry.html       # 按论文阶段进入的场景入口页
├── artifact-gallery.html     # v1.0 输出样例与答辩前整理展示页
├── docs-home.html            # docs 首页入口
├── advisor-handoff.html      # 交导师/合作者场景页
├── submission-prep.html      # 送审/投稿前场景页
├── copy-source.md            # 可继续维护的页面文案源文件
├── index-product-redraft.html # 历史首页草稿，保留作参考
├── v0.8-roadmap.md           # 历史 v0.8 范围记录，保留作参考
└── README.md                 # 本文件
```

## 本地预览

落地页是纯静态 HTML + CSS，无需构建步骤。

### 方法一：直接打开

直接在浏览器中打开 `site/index.html` 文件即可预览。

### 方法二：Python 简单服务器（推荐）

```bash
cd site
python -m http.server 8080
```

访问 <http://localhost:8080>。

### 方法三：Node.js

```bash
cd site
npx serve .
```

## 部署到 GitHub Pages

### 方式一：手动部署

1. 在仓库设置中启用 GitHub Pages
2. 选择 "Deploy from a branch"
3. 选择分支（如 `main`）和文件夹 `/ (root)` 或 `/docs`
4. 将 `site/` 目录内容复制到仓库根目录或 `docs/` 目录
5. 提交并推送

### 方式二：GitHub Actions 自动部署

创建 `.github/workflows/pages.yml`：

```yaml
name: Deploy Landing Page

on:
  push:
    branches: [ main ]
    paths:
      - 'site/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Pages
        uses: actions/configure-pages@v4

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './site'

      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## 更新页面

1. 编辑 `site/editorial-theme.css` 调整统一视觉样式
2. 编辑 `site/index.html`、`site/artifact-gallery.html`、`site/docs-home.html`、`site/scenario-entry.html` 或场景页修改页面内容
3. 如需先整理文案，可编辑 `site/copy-source.md`
4. 本地预览确认无误
5. 提交并推送

## 设计说明

- **单页静态**：无框架依赖，纯 HTML + CSS
- **统一主题样式**：`editorial-theme.css` 让首页、gallery、docs、scenario 共用一套视觉系统
- **输出样例页**：`artifact-gallery.html` 承接 v1.0 输出样例和 defense-prep artifact 展示
- **docs 导航页**：`docs-home.html` 与 `scenario-entry.html` 用于组织文档入口和按场景进入
- **场景页**：`advisor-handoff.html` 和 `submission-prep.html` 用于解释具体 bounded workflow 场景
- **响应式**：适配桌面和移动端
- **学术风格**：简洁、可信、不 flashy
- **无构建步骤**：直接部署，零维护成本
- **中文为主**：面向中文论文用户

## 技术约束

- 不使用 JavaScript（保持极简）
- 不引入外部 CSS 框架（避免依赖）
- 使用统一 CSS 文件维护视觉系统
- 所有能力描述必须与 README 和 `docs/roadmap.md` 的 v1.0 public contract 一致

## 后续可能方向

- 添加暗色模式支持
- 增加交互式演示（如 artifact 展开/收起）
- 添加多语言切换
- 集成文档搜索
