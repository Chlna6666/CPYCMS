import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/components/layout/FrontLayout.vue'),
    children: [
      { path: '', name: 'Home', component: () => import('@/views/home/HomeView.vue'), meta: { titleKey: 'route.home' } },
      { path: 'articles', name: 'ArticleList', component: () => import('@/views/articles/ArticleListView.vue'), meta: { titleKey: 'route.articles' } },
      { path: 'article/:slug', name: 'ArticleDetail', component: () => import('@/views/articles/ArticleDetailView.vue'), meta: { titleKey: 'route.articleDetail' } },
      { path: 'search', name: 'GlobalSearch', component: () => import('@/views/search/SearchView.vue'), meta: { titleKey: 'route.search' } },
      { path: 'portfolio', name: 'Portfolio', component: () => import('@/views/portfolio/PortfolioView.vue'), meta: { titleKey: 'route.portfolio' } },
      { path: 'portfolio/:id', name: 'WorkDetail', component: () => import('@/views/portfolio/PortfolioDetailView.vue'), meta: { titleKey: 'route.workDetail' } },
      { path: 'resources', name: 'Resources', component: () => import('@/views/resources/ResourcesView.vue'), meta: { titleKey: 'route.resources' } },
      { path: 'guestbook', name: 'Guestbook', component: () => import('@/views/guestbook/GuestbookView.vue'), meta: { titleKey: 'route.guestbook' } },
      { path: 'about', name: 'About', component: () => import('@/views/about/AboutView.vue'), meta: { titleKey: 'route.about' } },
      { path: 'contact', name: 'Contact', component: () => import('@/views/contact/ContactView.vue'), meta: { titleKey: 'route.contact' } }
    ]
  },
  { path: '/init', name: 'Init', component: () => import('@/views/init/InitView.vue'), meta: { titleKey: 'route.init' } },
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: () => import('@/views/admin/LoginView.vue'),
    meta: { titleKey: 'route.adminLogin' }
  },
  {
    path: '/admin',
    component: () => import('@/components/layout/AdminLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', name: 'Dashboard', component: () => import('@/views/admin/DashboardView.vue'), meta: { titleKey: 'route.dashboard' } },
      { path: 'articles', name: 'ArticleManage', component: () => import('@/views/admin/ArticleListView.vue'), meta: { titleKey: 'route.articleManage' } },
      { path: 'articles/create', name: 'ArticleCreate', component: () => import('@/views/admin/ArticleEditorView.vue'), meta: { titleKey: 'route.articleCreate' } },
      { path: 'articles/edit/:id', name: 'ArticleEdit', component: () => import('@/views/admin/ArticleEditorView.vue'), meta: { titleKey: 'route.articleEdit' } },
      { path: 'categories', name: 'CategoryManage', component: () => import('@/views/admin/CategoryListView.vue'), meta: { titleKey: 'route.categoryManage' } },
      { path: 'works', name: 'WorkManage', component: () => import('@/views/admin/WorkListView.vue'), meta: { titleKey: 'route.workManage' } },
      { path: 'resources', name: 'ResourceManage', component: () => import('@/views/admin/ResourceListView.vue'), meta: { titleKey: 'route.resourceManage' } },
      { path: 'messages', name: 'MessageManage', component: () => import('@/views/admin/MessageListView.vue'), meta: { titleKey: 'route.messageManage' } },
      { path: 'comments', name: 'CommentManage', component: () => import('@/views/admin/CommentListView.vue'), meta: { titleKey: 'route.commentManage' } },
      { path: 'settings', name: 'SiteSettings', component: () => import('@/views/admin/SettingsView.vue'), meta: { titleKey: 'route.settings' } },
      { path: 'profile', name: 'Profile', component: () => import('@/views/admin/ProfileView.vue'), meta: { titleKey: 'route.profile' } }
    ]
  }
]
