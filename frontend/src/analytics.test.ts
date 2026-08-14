import { afterEach, describe, expect, it, vi } from 'vitest'
import { product } from './test/fixtures'

describe('analytics helpers', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
    vi.resetModules()
    document.head.querySelectorAll('script[src*="googletagmanager"]').forEach(script => script.remove())
    delete (window as Window & { dataLayer?: unknown[]; gtag?: unknown }).dataLayer
    delete (window as Window & { dataLayer?: unknown[]; gtag?: unknown }).gtag
  })

  it('initializes Google Analytics once and sends page and item events', async () => {
    vi.stubEnv('VITE_GA_MEASUREMENT_ID', 'G-NAZRIY')
    const analytics = await import('./analytics')

    analytics.initAnalytics()
    analytics.initAnalytics()

    const scripts = document.head.querySelectorAll('script[src*="googletagmanager"]')
    expect(scripts).toHaveLength(1)
    expect(scripts[0]).toHaveAttribute('src', expect.stringContaining('G-NAZRIY'))

    const analyticsWindow = window as Window & { dataLayer?: unknown[][]; gtag?: (...args: unknown[]) => void }
    expect(analyticsWindow.dataLayer).toHaveLength(2)

    analytics.trackPageView('/products')
    analytics.trackItemEvent('view_item', product, 2)

    expect(analyticsWindow.dataLayer?.[2]).toEqual(['event', 'page_view', { page_path: '/products' }])
    expect(analyticsWindow.dataLayer?.[3]?.[0]).toBe('event')
    expect(analyticsWindow.dataLayer?.[3]?.[1]).toBe('view_item')
    expect(analyticsWindow.dataLayer?.[3]?.[2]).toMatchObject({ currency: 'BDT', value: 2000 })
  })

  it('filters undefined event parameters', async () => {
    vi.stubEnv('VITE_GA_MEASUREMENT_ID', 'G-NAZRIY')
    const analytics = await import('./analytics')
    analytics.initAnalytics()
    analytics.trackEvent('search', { term: 'dress', optional: undefined, count: 2 })

    const analyticsWindow = window as Window & { dataLayer?: unknown[][] }
    expect(analyticsWindow.dataLayer?.at(-1)).toEqual(['event', 'search', { term: 'dress', count: 2 }])
  })

  it('does nothing when analytics is not configured', async () => {
    vi.stubEnv('VITE_GA_MEASUREMENT_ID', '')
    const analytics = await import('./analytics')
    analytics.initAnalytics()
    analytics.trackPageView('/')

    expect(document.head.querySelector('script[src*="googletagmanager"]')).not.toBeInTheDocument()
    expect((window as Window & { dataLayer?: unknown[] }).dataLayer).toBeUndefined()
  })
})
