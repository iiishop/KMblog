# KMblog

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=for-the-badge&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/iiishop/KMblog)

一个现代化的静态博客系统，基于 Vue 3 构建，配备功能完善的桌面管理工具。

## 项目简介

KMblog 是一个轻量级的静态博客解决方案，提供优雅的前端展示和强大的后台管理功能。项目采用前后端分离架构，前端使用 Vue 3 + Vite 构建，后台管理工具使用 Python + Flet 开发。

## 核心特性

### 前端博客系统

- 基于 Vue 3 + Vite 的现代化单页应用
- 支持 Markdown 文章渲染，包含代码高亮、数学公式、Mermaid 图表
- 响应式设计，支持多种设备访问
- 主题系统支持明暗模式切换和自定义主题
- 文章分类、标签、归档功能
- 合集管理，支持系列文章组织
- 加密文章功能，保护私密内容
- 内嵌 Monaco 编辑器，支持在线编辑

### 桌面管理工具

- 现代化 GUI 界面，基于 Flet 框架
- 文章管理：创建、删除、移动文章
- 合集管理：组织和管理文章合集
- 配置管理：可视化编辑博客配置
- 一键构建和部署到 GitHub Pages
- Hexo 文章迁移工具
- 框架自动更新功能
- 内置 Markdown 编辑器服务

### 开发工具

- 完整的 CI/CD 流程，自动构建跨平台可执行文件
- 支持 Windows、macOS、Linux 三大平台
- 属性测试框架集成（fast-check）
- Vitest 单元测试支持

## 技术栈

### 前端

- Vue 3 - 渐进式 JavaScript 框架
- Vite - 下一代前端构建工具
- Vue Router - 官方路由管理器
- Markdown-it - Markdown 解析器
- KaTeX - 数学公式渲染
- Highlight.js - 代码语法高亮
- Mermaid - 图表和流程图
- Monaco Editor - 代码编辑器
- GSAP - 动画库

### 后端管理工具

- Python 3.11+
- Flet - 跨平台 GUI 框架
- PyInstaller - 打包工具
- Axios - HTTP 客户端

### 测试

- Vitest - 单元测试框架
- fast-check - 属性测试库
- jsdom - DOM 环境模拟

## 快速开始

### 前端开发

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 运行测试
npm run test
```

### 管理工具使用

#### 方式一：使用预编译版本

从 [Releases](https://github.com/iiishop/KMblog/releases) 页面下载对应平台的可执行文件：

- Windows: `KMblogManager-{version}-windows.zip`
- macOS: `KMblogManager-{version}-macos.tar.gz`
- Linux: `KMblogManager-{version}-linux.tar.gz`

解压后直接运行即可。

#### 方式二：从源码运行

```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 运行管理工具
python blog_manager.py
```

## 项目结构

```
KMblog/
├── src/                      # Vue 前端源码
│   ├── components/          # Vue 组件
│   ├── views/              # 页面视图
│   ├── router/             # 路由配置
│   ├── composables/        # 组合式函数
│   └── utils/              # 工具函数
├── mainTools/               # 管理工具后端
│   ├── commands.py         # 命令系统
│   ├── editor_server.py    # 编辑器服务
│   ├── github_commands.py  # GitHub 部署
│   └── update_framework.py # 框架更新
├── public/                  # 静态资源
│   ├── Posts/              # 文章目录
│   └── assets/             # 配置文件
├── .github/workflows/       # CI/CD 配置
├── blog_manager.py         # 管理工具入口
└── KMblogManager.spec      # PyInstaller 配置
```

## 功能模块

### 已完成功能

- 文章管理系统
  - 文章创建、删除、移动
  - Markdown 渲染和预览
  - 代码高亮和复制功能
  - 数学公式支持
  - Mermaid 图表支持
  - 任务列表支持

- 主题系统
  - 明暗模式切换
  - 自定义主题配置
  - 系统主题跟随
  - 平滑过渡动画

- 合集管理
  - 文章合集组织
  - 拖拽排序
  - 合集展示页面

- 管理工具
  - 现代化 GUI 界面
  - 可视化配置编辑
  - 一键构建部署
  - Hexo 迁移工具
  - 框架自动更新

- 特殊功能
  - 加密文章支持
  - 公告模块
  - 自我介绍模块
  - 时钟组件
  - 社交链接

- 开发工具
  - 完整 CI/CD 流程
  - 跨平台构建
  - 单元测试
  - 属性测试

### 计划中功能

- 评论系统（考虑中）
- 音乐播放模块
- 搜索功能增强
- 文章推荐系统
- 访问统计

## 配置说明

博客配置文件位于 `src/config.js`，主要配置项包括：

- `ProjectUrl` - 博客基础 URL
- `BlogName` - 博客名称
- `ShortDesc` - 博客描述
- `BackgroundImg` - 背景图片
- `LightTheme` / `DarkTheme` - 主题配置
- `PostsPerPage` - 每页文章数
- `Links` - 社交链接

详细配置说明请参考配置文件中的注释。

## 部署

### GitHub Pages 部署

1. 在管理工具中选择"部署到 GitHub"
2. 输入 GitHub Token 和仓库名称
3. 点击开始部署

或手动部署：

```bash
# 构建项目
npm run build

# 将 dist 目录推送到 gh-pages 分支
git subtree push --prefix dist origin gh-pages
```

## 开发指南

### 添加新组件

1. 在 `src/components/` 创建组件文件
2. 在 `src/config.js` 中注册组件
3. 在对应的列表配置中添加组件名称

### 自定义主题

1. 编辑 `src/color.css` 添加新主题
2. 在 `src/config.js` 中配置主题名称
3. 主题变量遵循 CSS 自定义属性规范

### 运行测试

```bash
# 运行所有测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:run

# 使用 UI 界面运行测试
npm run test:ui
```

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

## 致谢

感谢所有开源项目的贡献者，特别是：

- Vue.js 团队
- Vite 团队
- Flet 框架
- 所有依赖库的维护者

## 联系方式

- GitHub: [@iiishop](https://github.com/iiishop)
- 项目主页: [KMblog](https://github.com/iiishop/KMblog)