# 🎓 CPYCMS - 期末大作业全栈内容管理系统

> **📌 项目说明**：本项目为**期末大作业（综合实训项目）**。基于现代前后台分离架构打造，集成了全栈开发、数据库优化、多语言国际化 (i18n)、Markdown 高级渲染、安全防护及响应式布局等全套 Web 核心技术栈。

---

## 🌟 项目简介

**CPYCMS** 是一个专注于轻量、高效与现代化体验的全栈内容管理系统 (CMS)。系统分为**前台访客端**与**后台管理端**两大板块，具备完善的权限控制、内容发布、作品展示、资源下载、留言审核及数据可视化统计分析能力。

系统采用了目前主流的 **Django 5 + Django REST Framework** 作为后端 API 引擎，配合前端 **Vue 3 + TypeScript + Vite + Tailwind CSS 4** 构建，拥有高颜值、高性能及极佳的交互体验。

---

## 🚀 核心功能亮点

### 💻 前台功能 (访客/用户端)
- **首页 Hero 轮播与卡片展示**：支持热门作品展示、最新文章聚合、分类快速导航与搜索入口。
- **文章列表与详情**：支持分类筛选、标签云绑定、阅读量统计、文章点赞及互动评论。
- **高级 Markdown 渲染**：支持 Mermaid 图表、KaTeX 数学公式（如 $E=mc^2$）及代码高亮。
- **作品展示与资源下载**：展示创意项目与源码链接，提供各类型文件（PDF/ZIP等）安全下载与下载量统计。
- **互动留言板与全站搜索**：提供防刷限制的访客留言、实时响应式布局以及基于标题和内容的统一搜索中心。
- **关于我们与联系我们**：包含现代化多列 Footer 页脚、作者信息卡片、友情链接以及快捷联系通道。

### 🛡️ 后台功能 (管理员端)
- **数据控制台 (Dashboard)**：仪表盘实时统计文章总数、浏览量、点赞量、下载量及近 7 天发布趋势图表。
- **内容管理 (CRUD)**：可视化管理文章（草稿/发布/置顶）、分类目录、标签库、作品库及资源文件。
- **审核与互动管理**：留言审核/回复、文章评论列表过滤与审核回复。
- **站点全局设置**：支持持久化配置站点名称、Slogan、Logo、友情链接、页脚说明、主题色变体及防 CSRF 绑定域名。
- **个人信息与密码修改**：管理员个人资料维护与安全密码更新。

### 🎨 视觉与体验
- **现代化 UI/UX 设计**：采用 Tailwind CSS 4 + 玻璃拟态 (Glassmorphism) + Vibrant 渐变配色。
- **全响应式移动端适配**：针对手机、平板、桌面大屏进行了 100% 响应式自适应布局重构。
- **多语言国际化 (i18n)**：无缝支持中英文 (`zh-CN` / `en-US`) 实时切换。
- **深浅色主题切换**：支持系统级的 Dark / Light 深浅模式一键切换。

---

## 🛠️ 技术栈架构

| 架构层级 | 技术选型 | 说明 |
| :--- | :--- | :--- |
| **后端 API** | Django 5.0 + DRF | Python 现代化 Web 框架，RESTful API 架构 |
| **数据库** | SQLite3 | 适配轻量部署，优化数据库索引与 ORM 原子自增 |
| **前端框架** | Vue 3 + TypeScript | Composition API + 强类型校验 |
| **构建工具** | Vite 6 | 毫秒级热重载与模块化打包分块 |
| **状态/路由** | Pinia + Vue Router 4 | 状态持久化与路由懒加载/守卫 |
| **CSS 样式** | Tailwind CSS 4 + Lucide Icons | 自定义主题变量与高颜值现代化图标库 |
| **渲染引擎** | Marked.js + KaTeX + Mermaid | Markdown、公式与图表解析 |

---

## 📁 项目目录结构

```text
CPYCMS/
├── app.py                    # Django 开发环境启动入口 (自动代理 Vite)
├── manage.py                 # Django CLI 管理入口
├── wsgi.py / gunicorn.conf.py # 生产环境 WSGI / Gunicorn 配置
├── requirements.txt          # Python 依赖清单
├── docker-compose.yml        # Docker 容器化部署配置
├── backend/                  # Django 后端核心代码
│   ├── config/               # 全局 Settings / URLs 配置
│   └── apps/                 # 业务功能模块 (accounts / cms / common)
├── frontend/                 # Vue 3 + TypeScript 前端源码
│   ├── src/
│   │   ├── components/       # 公共组件 (Layout / Search / Header / Footer)
│   │   ├── views/            # 前后台页面 (Home, Articles, Admin, etc.)
│   │   ├── stores/           # Pinia 状态管理
│   │   └── i18n/             # 国际化语言包 (zh-CN / en-US)
└── docs/                     # 开发与部署详细文档
```

---

## ⚡ 快速开始 (本地运行)

### 1. 克隆项目
```bash
git clone https://github.com/Chlna6666/CPYCMS.git
cd CPYCMS
```

### 2. 后端准备与环境初始化
```bash
# 创建并激活虚拟环境 (Windows)
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate
```

### 3. 启动项目
```bash
python app.py
```
> 💡 **提示**：运行 `python app.py` 会自动在后台启动 Django (`http://127.0.0.1:5000`) 并同步代理启动前端 Vite 开发服务器。首次访问会自动引导进入系统初始化页面，创建管理员账号与初始数据。

---

## 📄 许可与致谢

- 本项目为期末大作业成果，仅供学习与交流参考。
