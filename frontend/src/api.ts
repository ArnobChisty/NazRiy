import type { BkashPaymentConfig, Category, DiscountCampaign, HomepageData, NavigationLink, Product, ProductAvailability, ProductFilters, TopProduct, WebsiteTheme } from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
const pendingPublicRequests = new Map<string, Promise<unknown>>()
const connectedOrigins = new Set<string>()

const warmOrigin = (value: string) => {
  try {
    const origin = new URL(value, window.location.origin).origin
    if (origin === window.location.origin || connectedOrigins.has(origin)) return
    connectedOrigins.add(origin)
    const link = document.createElement('link')
    link.rel = 'preconnect'
    link.href = origin
    link.crossOrigin = 'anonymous'
    document.head.appendChild(link)
  } catch { /* malformed optional media URLs are handled by image fallbacks */ }
}

warmOrigin(API_BASE)

const warmMediaOrigins = (value: unknown, depth = 0) => {
  if (depth > 4 || value == null) return
  if (typeof value === 'string') {
    if (/^https?:\/\//i.test(value)) warmOrigin(value)
    return
  }
  if (Array.isArray(value)) value.slice(0, 12).forEach(item => warmMediaOrigins(item, depth + 1))
  else if (typeof value === 'object') Object.values(value).forEach(item => warmMediaOrigins(item, depth + 1))
}

export class ApiError extends Error {
  status: number

  constructor(message: string, status: number) {
    super(message)
    this.status = status
  }
}

const request = async <T,>(path: string, init?: RequestInit): Promise<T> => {
  const response = await fetch(`${API_BASE}${path}`, init)
  if (!response.ok) {
    throw new ApiError(response.status === 404 ? 'Product not found.' : 'The NazRiy API is unavailable.', response.status)
  }
  const data = await response.json() as T
  warmMediaOrigins(data)
  return data
}

const cachedPublicRequest = <T,>(path: string, ttlMilliseconds: number): Promise<T> => {
  const key = `nazriy-api:${path}`
  try {
    const stored = window.sessionStorage.getItem(key)
    if (stored) {
      const cached = JSON.parse(stored) as { expires: number; data: T }
      if (cached.expires > Date.now()) return Promise.resolve(cached.data)
      window.sessionStorage.removeItem(key)
    }
  } catch { /* caching is an optional acceleration */ }

  const existing = pendingPublicRequests.get(path) as Promise<T> | undefined
  if (existing) return existing
  const pending = request<T>(path).then(data => {
    try { window.sessionStorage.setItem(key, JSON.stringify({ expires: Date.now() + ttlMilliseconds, data })) } catch { /* storage may be unavailable */ }
    return data
  }).finally(() => pendingPublicRequests.delete(path))
  pendingPublicRequests.set(path, pending)
  return pending
}

export const getProducts = (filters: ProductFilters) => {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value)
  })
  const query = params.toString()
  return request<Product[]>(`/products/${query ? `?${query}` : ''}`)
}

export const getFeaturedProducts = () => cachedPublicRequest<Product[]>('/products/featured/', 60_000)
export const getTopProducts = () => cachedPublicRequest<TopProduct[]>('/top-products/', 60_000)
export const getNavigationLinks = () => cachedPublicRequest<NavigationLink[]>('/navigation-links/', 300_000)
export const getCategories = () => cachedPublicRequest<Category[]>('/categories/', 300_000)
export const getHomepageData = () => cachedPublicRequest<HomepageData>('/homepage/', 30_000)
export const getWebsiteTheme = () => request<{ theme: WebsiteTheme }>('/theme/', { cache: 'no-store' })
export const getDiscountCampaigns = () => cachedPublicRequest<DiscountCampaign[]>('/discount-campaigns/', 30_000)
export const getBkashPaymentConfig = () => request<BkashPaymentConfig>('/payments/bkash/config/', { cache: 'no-store' })
export const getProduct = (slug: string) => request<Product>(`/products/${slug}/`)
export const getProductAvailability = (slug: string) => request<ProductAvailability>(`/products/${encodeURIComponent(slug)}/availability/?_=${Date.now()}`, { cache: 'no-store' })
export const getRelatedProducts = (slug: string, limit = 4) => request<Product[]>(`/products/${encodeURIComponent(slug)}/related/?limit=${limit}`)
export const getRecommendations = (limit = 4) => request<Product[]>(`/recommendations/?limit=${limit}`)
