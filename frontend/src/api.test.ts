import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  getCategories,
  getFeaturedProducts,
  getHomepageData,
  getNavigationLinks,
  getProduct,
  getProductAvailability,
  getProducts,
  getRecommendations,
  getRelatedProducts,
  getTopProducts,
} from './api'

const jsonResponse = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } })

describe('API client', () => {
  afterEach(() => { vi.unstubAllGlobals(); sessionStorage.clear() })

  it('builds product filters and omits empty values', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse([])))
    vi.stubGlobal('fetch', fetchMock)

    await getProducts({
      search: 'linen set', category: '', min_price: '100', max_price: '',
      size: 'M', color: '', ordering: 'price_asc',
    })

    const url = String(fetchMock.mock.calls[0][0])
    expect(url).toContain('/products/?')
    expect(url).toContain('search=linen+set')
    expect(url).toContain('min_price=100')
    expect(url).not.toContain('category=')
  })

  it('calls every catalogue endpoint with encoded parameters', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse([])))
    vi.stubGlobal('fetch', fetchMock)

    await getProducts({ search: '', category: '', min_price: '', max_price: '', size: '', color: '', ordering: '' })
    await getFeaturedProducts()
    await getTopProducts()
    await getNavigationLinks()
    await getCategories()
    await getHomepageData()
    await getProduct('red dress')
    await getProductAvailability('red dress')
    await getRelatedProducts('red dress', 6)
    await getRecommendations(2)

    const urls = fetchMock.mock.calls.map(call => String(call[0]))
    expect(urls).toEqual(expect.arrayContaining([
      expect.stringContaining('/products/'),
      expect.stringContaining('/products/featured/'),
      expect.stringContaining('/top-products/'),
      expect.stringContaining('/navigation-links/'),
      expect.stringContaining('/categories/'),
      expect.stringContaining('/homepage/'),
      expect.stringContaining('/products/red dress/'),
      expect.stringContaining('/products/red%20dress/availability/'),
      expect.stringContaining('/products/red%20dress/related/?limit=6'),
      expect.stringContaining('/recommendations/?limit=2'),
    ]))
    expect(fetchMock.mock.calls[7][1]).toMatchObject({ cache: 'no-store' })
  })

  it('uses default recommendation and related-product limits', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse([])))
    vi.stubGlobal('fetch', fetchMock)
    await getRelatedProducts('dress')
    await getRecommendations()
    expect(String(fetchMock.mock.calls[0][0])).toContain('limit=4')
    expect(String(fetchMock.mock.calls[1][0])).toContain('limit=4')
  })

  it('raises a specific not-found error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({}, 404)))
    await expect(getProduct('missing')).rejects.toMatchObject({
      message: 'Product not found.', status: 404,
    })
  })

  it('raises an availability error for other failure statuses', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(jsonResponse({}, 503)))
    await expect(getFeaturedProducts()).rejects.toMatchObject({
      message: 'The NazRiy API is unavailable.', status: 503,
    })
  })

  it('deduplicates in-flight public requests and reuses a fresh session cache', async () => {
    let resolveFetch: ((response: Response) => void) | undefined
    const fetchMock = vi.fn().mockReturnValue(new Promise<Response>((resolve) => { resolveFetch = resolve }))
    vi.stubGlobal('fetch', fetchMock)

    const first = getCategories()
    const second = getCategories()
    expect(fetchMock).toHaveBeenCalledTimes(1)

    resolveFetch?.(jsonResponse([{ id: 1, name: 'Women', slug: 'women' }]))
    await expect(first).resolves.toEqual([{ id: 1, name: 'Women', slug: 'women' }])
    await expect(second).resolves.toEqual([{ id: 1, name: 'Women', slug: 'women' }])

    await expect(getCategories()).resolves.toEqual([{ id: 1, name: 'Women', slug: 'women' }])
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('replaces expired and malformed cached responses', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(jsonResponse([])))
    vi.stubGlobal('fetch', fetchMock)
    sessionStorage.setItem('nazriy-api:/navigation-links/', JSON.stringify({ expires: 0, data: [{ id: 99 }] }))

    await expect(getNavigationLinks()).resolves.toEqual([])
    expect(fetchMock).toHaveBeenCalledTimes(1)

    sessionStorage.setItem('nazriy-api:/top-products/', '{not-json')
    await expect(getTopProducts()).resolves.toEqual([])
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('warms unique remote media origins returned by the API', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({
      id: 1,
      image: 'https://cdn.example.com/products/dress.webp',
      gallery: [
        'https://cdn.example.com/products/detail.webp',
        'https://images.example.org/products/back.webp',
        '/media/local.webp',
      ],
    }))
    vi.stubGlobal('fetch', fetchMock)

    await getProduct('dress')

    const origins = Array.from(document.head.querySelectorAll<HTMLLinkElement>('link[rel="preconnect"]'))
      .map(link => link.href)
    expect(origins).toEqual(expect.arrayContaining([
      'https://cdn.example.com/',
      'https://images.example.org/',
    ]))
    expect(origins.filter(origin => origin === 'https://cdn.example.com/')).toHaveLength(1)
  })
})
