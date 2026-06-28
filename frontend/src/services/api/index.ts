/**
 * CPYCMS - Django/DRF API 适配层。
 * 页面仍使用统一的 code/data/msg 结构，底层请求迁移到 /api/v1。
 */

import axios, { type AxiosError, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import { getInitialLocale, translate } from '@/i18n'

export interface ApiResponse<T = any> {
  code: number
  msg?: string
  data?: T
  initialized?: boolean
  logged_in?: boolean
}

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  per_page: number
  pages: number
  has_prev: boolean
  has_next: boolean
}

interface DrfPage<T> {
  count: number
  next: number | string | null
  previous: number | string | null
  page?: number
  page_size?: number
  total_pages?: number
  results: T[]
}

export interface UserInfo {
  id: number
  username: string
  nickname: string
  email: string
  avatar: string
  bio: string
  is_active: boolean
  is_staff?: boolean
  is_superuser?: boolean
  is_admin?: boolean
  created_at: string
  updated_at: string
}

export interface Category {
  id: number
  name: string
  slug: string
  description: string
  sort_order: number
  is_visible: boolean
  article_count: number
  created_at: string
}

export interface Tag {
  id: number
  name: string
  color: string
  article_count: number
}

export interface Article {
  id: number
  title: string
  slug: string
  summary: string
  content?: string
  cover_image: string
  category_id: number | null
  category_name: string
  author_id: number | null
  status: 'draft' | 'published' | 'archived'
  view_count: number
  like_count: number
  is_top: boolean
  created_at: string
  updated_at?: string
  published_at: string
  tags: Tag[]
}

export interface Work {
  id: number
  title: string
  description: string
  content?: string
  cover_image: string
  category_id: number | null
  category_name: string
  tech_stack: string[]
  demo_url: string
  source_url: string
  status: 'draft' | 'published'
  like_count: number
  view_count: number
  sort_order: number
  created_at: string
  updated_at?: string
}

export interface Resource {
  id: number
  title: string
  description: string
  file_name: string
  file_size: number
  file_type: string
  download_count: number
  status: 'draft' | 'published'
  created_at: string
  updated_at: string
}

export interface Message {
  id: number
  nickname: string
  email?: string
  content: string
  reply: string
  author_role: 'visitor' | 'admin'
  is_admin_author: boolean
  is_approved: boolean
  is_replied: boolean
  ip_address?: string
  created_at: string
  replied_at: string
}

export interface ArticleComment {
  id: number
  article_id: number
  nickname: string
  email?: string
  email_masked?: string
  content: string
  reply: string
  author_role: 'visitor' | 'admin'
  is_admin_author: boolean
  is_replied: boolean
  is_approved?: boolean
  ip_address?: string
  fingerprint_hash?: string
  browser: string
  os_name: string
  device_type: string
  user_agent?: string
  article_title?: string
  article_slug?: string
  created_at: string
  approved_at?: string
  replied_at?: string
}

export interface SiteSettings {
  site_name: string
  site_slogan: string
  site_description: string
  site_keywords: string
  site_logo: string
  author_name: string
  author_email: string
  author_avatar: string
  about_content: string
  contact_info: string
  footer_text: string
  footer_note: string
  footer_height: 'compact' | 'normal' | 'large' | string
  icp_beian_number: string
  police_beian_number: string
  bound_domains: string
  friend_links: string | any[]
  banner_title: string
  banner_subtitle: string
  hero_slides: string | any[]
  theme_primary_color: string
  theme_accent_color: string
}

export interface SiteBootstrap {
  info: SiteSettings
  categories: Category[]
  tags: Tag[]
}

export interface StatsData {
  article_count: number
  published_count: number
  draft_count: number
  work_count: number
  resource_count: number
  message_count: number
  pending_messages: number
  comment_count: number
  pending_comments: number
  category_count: number
  total_views: number
  total_likes: number
  total_downloads: number
  daily_articles: { date: string; count: number }[]
  category_distribution: { name: string; count: number }[]
  top_articles: { title: string; views: number }[]
}

export interface UploadResult {
  url: string
  filename: string
}

export interface ArticleFormData {
  title: string
  slug: string
  content: string
  summary: string
  category_id: number | null
  status: string
  cover_image: string
  tag_ids: number[]
  is_top: boolean
}

export interface WorkFormData {
  title: string
  description: string
  content: string
  cover_image: string
  category_id: number | null
  tech_stack: string[] | string
  demo_url: string
  source_url: string
  status: string
  sort_order: number
}

const API_BASE = '/api/v1'
const csrfClient = axios.create({ baseURL: API_BASE, withCredentials: true })

function getCookie(name: string): string {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/([$?*|{}()[\]\\/+^])/g, '\\$1')}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : ''
}

async function ensureCsrfToken(): Promise<string> {
  const existing = getCookie('csrftoken')
  if (existing) return existing
  await csrfClient.get('/auth/csrf/')
  return getCookie('csrftoken')
}

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  withCredentials: true
})

api.interceptors.request.use(async config => {
  const method = (config.method || 'get').toLowerCase()
  if (!['get', 'head', 'options', 'trace'].includes(method)) {
    const token = await ensureCsrfToken()
    if (token) config.headers.set('X-CSRFToken', token)
  }
  return config
})

api.interceptors.response.use(
  (response: AxiosResponse) => response.data,
  (error: AxiosError<{ detail?: string; msg?: string }>) => {
    const status = error.response?.status
    if ((status === 401 || status === 403) && window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
      window.dispatchEvent(new CustomEvent('cpycms:auth-expired'))
      if (!window.location.pathname.startsWith('/admin/login')) {
        window.location.href = `/admin/login?redirect=${encodeURIComponent(window.location.pathname + window.location.search)}`
      }
    } else if (status === 401) {
      if (window.location.pathname.startsWith('/admin') && window.location.pathname !== '/admin/login') {
        window.location.href = '/admin/login'
      }
    }
    const msg = error.response?.data?.detail || error.response?.data?.msg || (
      error.code === 'ERR_NETWORK'
        ? translate(getInitialLocale(), 'common.backendOffline')
        : translate(getInitialLocale(), 'common.networkError')
    )
    return Promise.reject(new Error(msg))
  }
)

function ok<T>(data?: T, msg = ''): ApiResponse<T> {
  return { code: 200, msg, data }
}

function detail(raw: any): string {
  return String(raw?.detail || raw?.msg || '')
}

function parseJsonField(value: unknown): unknown {
  if (typeof value !== 'string' || !value.trim()) return value
  try {
    return JSON.parse(value)
  } catch {
    return value
  }
}

function normalizeSiteInfo(raw: any): SiteSettings {
  return {
    ...(raw || {}),
    friend_links: parseJsonField(raw?.friend_links) || '',
    hero_slides: parseJsonField(raw?.hero_slides) || ''
  } as SiteSettings
}

function adaptPage<T>(raw: DrfPage<T>): PaginatedResult<T> {
  const page = Number(raw.page || 1)
  const perPage = Number(raw.page_size || raw.results?.length || 1)
  const pages = Number(raw.total_pages || Math.max(1, Math.ceil((raw.count || 0) / Math.max(perPage, 1))))
  return {
    items: raw.results || [],
    total: raw.count || 0,
    page,
    per_page: perPage,
    pages,
    has_prev: !!raw.previous,
    has_next: !!raw.next
  }
}

function adaptSearch<T>(raw: { keyword?: string; results?: T[] }): PaginatedResult<T> & { keyword?: string } {
  const items = raw.results || []
  return {
    items,
    total: items.length,
    page: 1,
    per_page: items.length || 1,
    pages: 1,
    has_prev: false,
    has_next: false,
    keyword: raw.keyword || ''
  }
}

function get<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return api.get(url, config) as Promise<T>
}

function post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return api.post(url, data, config) as Promise<T>
}

function put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
  return api.put(url, data, config) as Promise<T>
}

function del<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  return api.delete(url, config) as Promise<T>
}

export const initApi = {
  async check(): Promise<ApiResponse> {
    const raw = await get<{ initialized: boolean }>('/init/check/')
    return { code: 200, initialized: raw.initialized }
  },
  async setup(data: Record<string, string>): Promise<ApiResponse> {
    const raw = await post<{ detail?: string; msg?: string; initialized?: boolean }>('/init/setup/', data)
    return { ...ok(undefined, detail(raw)), initialized: raw.initialized }
  }
}

export const authApi = {
  async login(data: { username: string; password: string }): Promise<ApiResponse<UserInfo>> {
    const raw = await post<UserInfo>('/auth/login/', data)
    return ok(raw)
  },
  async logout(): Promise<ApiResponse> {
    const raw = await post('/auth/logout/')
    return ok(undefined, detail(raw))
  },
  async check(): Promise<ApiResponse & { logged_in: boolean; data?: UserInfo }> {
    const raw = await get<{ logged_in: boolean; user?: UserInfo }>('/auth/session/')
    return { code: 200, logged_in: raw.logged_in, data: raw.user }
  },
  async updateProfile(data: Partial<UserInfo>): Promise<ApiResponse<UserInfo>> {
    const raw = await put<UserInfo>('/auth/profile/', data)
    return ok(raw)
  },
  async changePassword(data: { old_password: string; new_password: string }): Promise<ApiResponse> {
    const raw = await put('/auth/password/', data)
    return ok(undefined, detail(raw))
  }
}

export const siteApi = {
  async getBootstrap(): Promise<ApiResponse<SiteBootstrap>> {
    const raw = await get<any>('/site/bootstrap/')
    return { code: 200, initialized: raw.initialized, data: { ...raw, info: normalizeSiteInfo(raw.info || {}) } }
  },
  async getInfo(): Promise<ApiResponse<SiteSettings>> {
    const raw = await get('/site/info/')
    return ok(normalizeSiteInfo(raw))
  },
  async getCategories(): Promise<ApiResponse<Category[]>> {
    return ok(await get<Category[]>('/site/categories/'))
  },
  async getTags(): Promise<ApiResponse<Tag[]>> {
    return ok(await get<Tag[]>('/site/tags/'))
  }
}

export const articleApi = {
  async getList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Article>>> {
    return ok(adaptPage(await get<DrfPage<Article>>('/articles/', { params })))
  },
  async search(keyword: string, limit = 6): Promise<ApiResponse<PaginatedResult<Article> & { keyword?: string }>> {
    return ok(adaptSearch(await get('/articles/search/', { params: { keyword, limit } })))
  },
  async getDetail(slug: string): Promise<ApiResponse<Article>> {
    return ok(await get<Article>(`/articles/${slug}/`))
  },
  async getHot(): Promise<ApiResponse<Article[]>> {
    return ok(await get<Article[]>('/articles/hot/'))
  },
  async like(slug: string, data: { client_fingerprint: string }): Promise<ApiResponse & { like_count: number }> {
    const raw = await post<{ detail: string; like_count: number }>(`/articles/${slug}/like/`, data)
    return { code: 200, msg: detail(raw), like_count: raw.like_count }
  },
  async adminGetList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Article>>> {
    return ok(adaptPage(await get<DrfPage<Article>>('/admin/articles/', { params })))
  },
  async adminGetDetail(id: number): Promise<ApiResponse<Article>> {
    return ok(await get<Article>(`/admin/articles/${id}/`))
  },
  async create(data: Partial<ArticleFormData>): Promise<ApiResponse<Article>> {
    return ok(await post<Article>('/admin/articles/create/', data))
  },
  async update(id: number, data: Partial<ArticleFormData>): Promise<ApiResponse<Article>> {
    return ok(await put<Article>(`/admin/articles/${id}/`, data))
  },
  async delete(id: number): Promise<ApiResponse> {
    return ok(undefined, detail(await del(`/admin/articles/${id}/`)))
  }
}

export const categoryApi = {
  getList: async (): Promise<ApiResponse<Category[]>> => ok(await get<Category[]>('/site/categories/')),
  adminGetList: async (): Promise<ApiResponse<Category[]>> => ok(await get<Category[]>('/admin/categories/')),
  create: async (data: Partial<Category>): Promise<ApiResponse<Category>> => ok(await post<Category>('/admin/categories/', data)),
  update: async (id: number, data: Partial<Category>): Promise<ApiResponse<Category>> => ok(await put<Category>(`/admin/categories/${id}/`, data)),
  delete: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await del(`/admin/categories/${id}/`)))
}

export const tagApi = {
  getList: async (): Promise<ApiResponse<Tag[]>> => ok(await get<Tag[]>('/site/tags/')),
  adminGetList: async (): Promise<ApiResponse<Tag[]>> => ok(await get<Tag[]>('/admin/tags/')),
  create: async (data: { name: string; color?: string }): Promise<ApiResponse<Tag>> => ok(await post<Tag>('/admin/tags/', data)),
  update: async (id: number, data: { name?: string; color?: string }): Promise<ApiResponse<Tag>> => ok(await put<Tag>(`/admin/tags/${id}/`, data)),
  delete: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await del(`/admin/tags/${id}/`)))
}

export const workApi = {
  async getList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Work>>> {
    return ok(adaptPage(await get<DrfPage<Work>>('/works/', { params })))
  },
  async search(keyword: string, limit = 8): Promise<ApiResponse<PaginatedResult<Work> & { keyword?: string }>> {
    return ok(adaptSearch(await get('/works/search/', { params: { keyword, limit } })))
  },
  async getDetail(id: number): Promise<ApiResponse<Work>> {
    return ok(await get<Work>(`/works/${id}/`))
  },
  async like(id: number, data: { client_fingerprint: string }): Promise<ApiResponse & { like_count: number }> {
    const raw = await post<{ detail: string; like_count: number }>(`/works/${id}/like/`, data)
    return { code: 200, msg: detail(raw), like_count: raw.like_count }
  },
  async adminGetList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Work>>> {
    return ok(adaptPage(await get<DrfPage<Work>>('/admin/works/', { params })))
  },
  async create(data: Partial<WorkFormData>): Promise<ApiResponse<Work>> {
    return ok(await post<Work>('/admin/works/', data))
  },
  async update(id: number, data: Partial<WorkFormData>): Promise<ApiResponse<Work>> {
    return ok(await put<Work>(`/admin/works/${id}/`, data))
  },
  async delete(id: number): Promise<ApiResponse> {
    return ok(undefined, detail(await del(`/admin/works/${id}/`)))
  }
}

export const resourceApi = {
  async getList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Resource>>> {
    return ok(adaptPage(await get<DrfPage<Resource>>('/resources/', { params })))
  },
  async search(keyword: string, limit = 8): Promise<ApiResponse<PaginatedResult<Resource> & { keyword?: string }>> {
    return ok(adaptSearch(await get('/resources/search/', { params: { keyword, limit } })))
  },
  download: (id: number): string => `${API_BASE}/resources/${id}/download/`,
  async adminGetList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Resource>>> {
    return ok(adaptPage(await get<DrfPage<Resource>>('/admin/resources/', { params })))
  },
  async upload(formData: FormData): Promise<ApiResponse<Resource>> {
    return ok(await post<Resource>('/admin/resources/', formData))
  },
  async update(id: number, data: Partial<Resource>): Promise<ApiResponse<Resource>> {
    return ok(await put<Resource>(`/admin/resources/${id}/`, data))
  },
  async delete(id: number): Promise<ApiResponse> {
    return ok(undefined, detail(await del(`/admin/resources/${id}/`)))
  }
}

export const messageApi = {
  async getList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Message>>> {
    return ok(adaptPage(await get<DrfPage<Message>>('/messages/', { params })))
  },
  async create(data: { nickname: string; email?: string; content: string }): Promise<ApiResponse> {
    return ok(undefined, detail(await post('/messages/create/', data)))
  },
  async adminGetList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<Message>>> {
    return ok(adaptPage(await get<DrfPage<Message>>('/admin/messages/', { params })))
  },
  approve: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await put(`/admin/messages/${id}/approve/`))),
  reply: async (id: number, data: { reply: string }): Promise<ApiResponse> => ok(undefined, detail(await put(`/admin/messages/${id}/reply/`, data))),
  delete: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await del(`/admin/messages/${id}/`)))
}

export const commentApi = {
  async getList(slug: string, params: Record<string, any>): Promise<ApiResponse<PaginatedResult<ArticleComment>>> {
    return ok(adaptPage(await get<DrfPage<ArticleComment>>(`/articles/${slug}/comments/`, { params })))
  },
  async create(slug: string, data: { nickname?: string; email?: string; content: string; client_fingerprint?: string }): Promise<ApiResponse> {
    return ok(undefined, detail(await post(`/articles/${slug}/comments/create/`, data)))
  },
  async adminGetList(params: Record<string, any>): Promise<ApiResponse<PaginatedResult<ArticleComment>>> {
    return ok(adaptPage(await get<DrfPage<ArticleComment>>('/admin/comments/', { params })))
  },
  approve: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await put(`/admin/comments/${id}/approve/`))),
  reply: async (id: number, data: { reply: string }): Promise<ApiResponse> => ok(undefined, detail(await put(`/admin/comments/${id}/reply/`, data))),
  delete: async (id: number): Promise<ApiResponse> => ok(undefined, detail(await del(`/admin/comments/${id}/`)))
}

export const uploadApi = {
  image: async (formData: FormData): Promise<ApiResponse<UploadResult>> => ok(await post<UploadResult>('/admin/upload/image/', formData)),
  articleCover: async (formData: FormData): Promise<ApiResponse<UploadResult>> => ok(await post<UploadResult>('/admin/upload/article-cover/', formData)),
  workCover: async (formData: FormData): Promise<ApiResponse<UploadResult>> => ok(await post<UploadResult>('/admin/upload/work-cover/', formData)),
  siteLogo: async (formData: FormData): Promise<ApiResponse<UploadResult>> => ok(await post<UploadResult>('/admin/upload/site-logo/', formData))
}

export const settingsApi = {
  async get(): Promise<ApiResponse<SiteSettings>> {
    const raw = await get('/admin/settings/')
    return ok(raw as SiteSettings)
  },
  async update(data: Partial<SiteSettings>): Promise<ApiResponse> {
    return ok(undefined, detail(await put('/admin/settings/', data)))
  }
}

export const statsApi = {
  get: async (): Promise<ApiResponse<StatsData>> => ok(await get<StatsData>('/admin/stats/'))
}

export default api
