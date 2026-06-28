# CPYCMS 开发说明

本文档记录 CPYCMS 迁移到 Django 后的目录职责、API 约定、测试策略和部署方式。

## 后端结构

```text
backend/
├── config/
│   ├── settings.py           # Django settings，只支持 SQLite3
│   ├── urls.py               # API、uploads、SPA fallback
│   ├── asgi.py
│   └── wsgi.py
└── apps/
    ├── accounts/
    │   ├── models.py         # 自定义 User(AbstractUser)
    │   ├── serializers.py    # 用户输出序列化
    │   ├── views.py          # 登录、退出、session、个人资料、密码
    │   └── urls.py
    ├── cms/
    │   ├── models.py         # 分类、标签、文章、作品、资源、留言、评论、设置
    │   ├── serializers.py    # API 输出字典
    │   ├── views.py          # 前台与后台业务 API
    │   └── urls.py
    └── common/
        ├── database.py       # SQLite PRAGMA、旧库备份、按需 migrate
        ├── uploads.py        # 上传校验和路径安全
        ├── logging.py        # 队列日志、彩色控制台、gzip 滚动清理
        ├── middleware.py     # 请求耗时日志
        ├── pagination.py     # DRF 风格分页
        ├── search.py         # 安全 token 化搜索
        └── permissions.py    # 后台权限装饰器
```

旧 Flask `backend/app/` 已移除。不要再新增 Flask、Flask-SQLAlchemy、Blueprint 或 `create_app` 入口。

## API 约定

新接口统一位于 `/api/v1/`：

- `/api/v1/init/check/`
- `/api/v1/init/setup/`
- `/api/v1/auth/login/`
- `/api/v1/auth/session/`
- `/api/v1/site/bootstrap/`
- `/api/v1/articles/`
- `/api/v1/admin/articles/`

Django/DRF 后端直接返回对象、列表或分页对象：

```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "page": 1,
  "page_size": 10,
  "total_pages": 1,
  "results": []
}
```

前端集中在 `frontend/src/services/api/index.ts` 适配为页面原来使用的 `code/data/msg/items` 结构。业务页面不直接拼接后端路径。

后台写接口使用 Django session + CSRF。前端服务层会在写操作前自动请求 `/api/v1/auth/csrf/` 并带上 `X-CSRFToken`。

## 初始化和数据库

项目只支持 SQLite3。默认文件是根目录 `cpycms.db`。

未初始化时：

- `/api/v1/init/check/` 返回 `{"initialized": false}`
- `/api/v1/site/bootstrap/` 返回默认站点信息、空分类、空标签
- 不会因为检查接口而创建数据库文件

初始化提交时会执行：

1. 如数据库不存在，运行 Django migrations 创建表。
2. 如存在旧 Flask SQLite 文件且无 `django_migrations` 表，先重命名备份为 `cpycms.flask-backup-时间戳.db`。
3. 创建超级管理员、站点设置、基础分类、标签和 `Hello CPYCMS` 默认文章。

初始化页的“绑定域名”会保存为 `SiteSetting.bound_domains`。程序启动时会把重要站点设置加载到内存运行时缓存，CSRF Origin 校验读取内存缓存而不是每次查数据库；后台“站点设置”保存后会立即刷新该缓存。

如果 Windows 报数据库被占用，先关闭旧后端进程、PyCharm 数据库工具或 SQLite 查看器。

## 本地开发

后端：

```bash
pip install -r requirements.txt
python manage.py migrate
python app.py
```

`python app.py` 在 `CPYCMS_DEBUG=1` 时会自动启动 `frontend` 目录下的 `npm run dev`，并把 Django 上的前端页面、`/src/*`、`/@vite/client`、`/assets/*` 等请求代理到 Vite。开发时不需要先编译 `frontend/dist`，Vite 的热更新与日志会直接出现在当前控制台。

如需手动管理 Vite：

```bash
set CPYCMS_AUTO_START_VITE=0
cd frontend
npm install
npm run dev
```

默认 Vite 负责代理 `/api` 与 `/uploads` 到 `http://127.0.0.1:5000`。如果 Django 端口变化，`python app.py` 会为自动启动的 Vite 注入 `VITE_BACKEND_URL`。

如果希望只验证构建后的前端，可执行 `npm run build`，Django 会通过 `backend/config/urls.py` 的 SPA fallback 返回 `frontend/dist/index.html`。

## 日志

日志模块位于 `backend/apps/common/logging.py`：

- `QueueHandler + QueueListener` 异步输出
- 控制台自动判断是否支持 ANSI 高亮
- `logs/cpycms.log` 按天滚动
- 历史日志自动 gzip 压缩
- 按 `CPYCMS_LOG_BACKUP_DAYS` 和 `CPYCMS_LOG_MAX_TOTAL_MB` 清理旧文件

请求耗时由 `RequestLogMiddleware` 输出，超过 `CPYCMS_SLOW_REQUEST_MS` 的请求使用 `WARNING`。

## 上传和安全

上传根目录由 `CPYCMS_UPLOAD_FOLDER` 控制，默认 `uploads/`。

规则：

- 图片只允许 `png/jpg/jpeg/gif/webp`，禁止 SVG。
- 资源只允许课程项目常用文档、压缩包和文本格式。
- 文件名不得包含路径片段、`..`、控制字符。
- 保存和删除前必须确认物理路径位于对应上传目录内。
- 站点 Logo、头像等设置项必须来自 `/uploads/` 本地路径。
- 评论内容会去除脚本和 HTML 标签，邮箱必填，指纹只保存服务端哈希。

## 前端结构

页面按路由业务目录组织：

```text
frontend/src/
├── components/               # 公共组件
├── router/                   # 路由表和守卫
├── services/api/index.ts     # 唯一 API 适配层
├── stores/                   # Pinia 状态
├── i18n/locales/*.json       # 所有可见文案
└── views/
    ├── home/HomeView.vue
    ├── home/components/
    ├── articles/
    ├── portfolio/
    ├── resources/
    ├── guestbook/
    ├── search/
    ├── init/
    └── admin/
```

`.vue` 是主要组件格式；需要 JSX 时在 `.vue` 内使用 `<script lang="tsx">`。图标直接从 `@lucide/vue` 导入。

## 正式前端分块

正式环境必须构建前端：

```bash
cd frontend
npm run typecheck
npm run build
```

Vite 已配置分块：

- `vendor-vue`：Vue、Router、Pinia
- `vendor-http`：Axios
- `vendor-motion`：动效
- `vendor-charts`：ECharts
- `markdown-core`、`markdown-math`：Markdown、代码高亮、KaTeX
- `admin-auth`、`admin-layout`：后台登录与后台布局

这能减少前台首屏流量，避免普通访客提前下载后台页面代码。权限仍由 Django session、CSRF 和后台 API 权限控制保证。

## 测试

```bash
python -m pytest -q
cd frontend
npm run typecheck
npm run build
```

后端测试使用 pytest-django 测试库，不读写生产 `cpycms.db`。覆盖范围包括初始化、登录/退出、CRUD、上传下载删除、留言/评论审核、站点设置校验、日志压缩和上传安全。

## Docker 部署

```bash
copy .env.example .env
docker compose up --build -d
```

`docker compose up --build -d` 会触发构建并后台启动，但 Docker 会复用缓存层。需要彻底重新构建时先运行 `docker compose build --no-cache backend`，再 `docker compose up -d`。

线上通过 HTTPS 域名访问时，`.env` 必须包含真实域名，否则 Django CSRF 会拒绝后台写接口：

```env
CPYCMS_ALLOWED_HOSTS=cms.chlna6666.com,127.0.0.1,localhost
CPYCMS_CSRF_TRUSTED_ORIGINS=https://cms.chlna6666.com,http://127.0.0.1:5000,http://localhost:5000
```

初始化页和后台“站点设置”也支持维护绑定域名，数据库中的绑定域名会与 `.env` 中的 CSRF trusted origins 合并进入运行时缓存。`.env` 仍建议保留生产域名作为首次启动兜底。

只修改 `.env` 时不需要重新 build，执行 `docker compose up -d --force-recreate backend` 即可让新环境变量生效。

容器启动命令：

```bash
python manage.py migrate --noinput && gunicorn -c gunicorn.conf.py wsgi:application
```

Docker 只运行 Django + Gunicorn，不配置 Nginx。外部 Web 服务器需要代理 `/api/` 与 `/uploads/`，并托管前端构建产物。
