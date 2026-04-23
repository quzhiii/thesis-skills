# Thesis Skills 落地页

这是 Thesis Skills v0.7 的展示落地页，用于帮助潜在用户快速了解项目的定位、场景和能力边界。

## 文件结构

```
site/
├── index.html          # 落地页主文件
├── copy-source.md      # 页面文案源文件
└── README.md           # 本文件
```

## 本地预览

落地页是纯静态 HTML + CSS，无需构建步骤。

### 方法一：直接打开
直接在浏览器中打开 `site/index.html` 文件即可预览。

### 方法二：Python 简单服务器（推荐）

```bash
# 进入 site 目录
cd site

# Python 3
python -m http.server 8080

# 访问 http://localhost:8080
```

### 方法三：Node.js

```bash
# 进入 site 目录
cd site

# 使用 npx
npx serve .

# 或使用 http-server
npx http-server -p 8080
```

## 部署到 GitHub Pages

### 方式一：手动部署（当前推荐）

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

1. 编辑 `site/index.html` 修改页面内容
2. 或编辑 `site/copy-source.md` 查看文案源文件
3. 本地预览确认无误
4. 提交并推送

## 设计说明

- **单页静态**：无框架依赖，纯 HTML + CSS
- **响应式**：适配桌面和移动端
- **学术风格**：简洁、可信、不 flashy
- **无构建步骤**：直接部署，零维护成本
- **中文为主**：面向中文论文用户

## 技术约束

- 不使用 JavaScript（保持极简）
- 不引入外部 CSS 框架（避免依赖）
- 内联所有样式（减少 HTTP 请求）
- 使用 SVG 图标（无需图标字体）

## 未来可能的方向

- 添加暗色模式支持
- 增加交互式演示（如 artifact 展开/收起）
- 添加多语言切换
- 集成文档搜索
