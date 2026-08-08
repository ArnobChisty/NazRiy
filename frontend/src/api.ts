import type { Category, HomepageData, NavigationLink, Product, ProductAvailability, ProductFilters, TopProduct } from './types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

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
  return response.json() as Promise<T>
}

export const getProducts = (filters: ProductFilters) => {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value) params.set(key, value)
  })
  const query = params.toString()
  return request<Product[]>(`/products/${query ? `?${query}` : ''}`)
}

export const getFeaturedProducts = () => request<Product[]>('/products/featured/')
export const getTopProducts = () => request<TopProduct[]>('/top-products/')
export const getNavigationLinks = () => request<NavigationLink[]>('/navigation-links/')
export const getCategories = () => request<Category[]>('/categories/')
export const getHomepageData = () => request<HomepageData>('/homepage/')
export const getProduct = (slug: string) => request<Product>(`/products/${slug}/`)
export const getProductAvailability = (slug: string) => request<ProductAvailability>(`/products/${encodeURIComponent(slug)}/availability/?_=${Date.now()}`, { cache: 'no-store' })
export const getRelatedProducts = (slug: string, limit = 4) => request<Product[]>(`/products/${encodeURIComponent(slug)}/related/?limit=${limit}`)
export const getRecommendations = (limit = 4) => request<Product[]>(`/recommendations/?limit=${limit}`)
