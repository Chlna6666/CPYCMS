# CPYCMS Frontend Structure

前端源码采用“页面目录 + 局部组件”的组织方式，避免 `index.vue` 和多层无意义嵌套。

```text
src/
├── app/                    # 应用级插件、动画、启动辅助
├── assets/                 # 全局 CSS 与参与打包的静态资源
├── components/
│   ├── common/             # 跨页面通用组件，如 MarkdownRenderer、LocaleSwitcher
│   ├── layout/             # 路由布局：FrontLayout、AdminLayout、FrontHeader
│   └── search/             # 跨页面复用的搜索组件：GlobalSearch
├── composables/            # Vue 组合式函数
├── i18n/                   # JSON 语言包与翻译工具
├── router/
│   ├── index.ts            # Router 实例入口
│   ├── routes.ts           # 路由表
│   └── guards.ts           # 初始化与后台登录守卫
├── services/api/           # Axios 实例、接口封装和 API 类型
├── stores/
│   ├── auth.ts             # 管理员登录状态
│   ├── site.ts             # 站点公开信息、分类、标签
│   ├── ui.ts               # 语言和深浅色状态
│   └── index.ts            # Store 聚合导出
├── utils/                  # 前端工具函数
└── views/
    ├── home/               # 首页页面和首页专属组件
    │   ├── HomeView.vue
    │   └── components/
    ├── articles/           # 文章列表、详情和文章评论组件
    │   ├── ArticleListView.vue
    │   ├── ArticleDetailView.vue
    │   └── components/
    ├── search/             # 搜索结果页和搜索页专属组件
    │   ├── SearchView.vue
    │   └── components/
    ├── portfolio/          # 作品列表和作品详情页
    ├── resources/          # 资源下载页
    ├── guestbook/          # 留言板页
    ├── about/              # 关于页
    ├── contact/            # 联系页
    ├── init/               # 初始化页
    └── admin/              # 后台页面，使用 *View.vue 显式命名
```

约定：

- 路由页面使用 `*View.vue` 显式命名，不使用 `index.vue`。
- 每个页面自己的拼装组件放在对应 `views/<page>/components/`。
- 跨页面复用组件才放入 `components/`。
- 前后台布局属于 `components/layout/`，不再维护独立 `layouts/` 顶层目录。
- 路由配置拆分为 `router/routes.ts` 和 `router/guards.ts`。
- Pinia Store 拆分为 `stores/auth.ts`、`stores/site.ts`、`stores/ui.ts`。
- 接口类型和请求函数统一从 `@/services/api` 导入。
