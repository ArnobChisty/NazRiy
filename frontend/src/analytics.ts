const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID as string | undefined

type AnalyticsParams = Record<string, string | number | boolean | undefined>
type AnalyticsWindow = Window & { dataLayer?: unknown[]; gtag?: (...args: unknown[]) => void }

let initialized = false

export const initAnalytics = () => {
  if (initialized || !measurementId || typeof document === 'undefined') return
  initialized = true
  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`
  document.head.appendChild(script)
  const win = window as AnalyticsWindow
  win.dataLayer = win.dataLayer || []
  win.gtag = (...args: unknown[]) => win.dataLayer?.push(args)
  win.gtag('js', new Date())
  win.gtag('config', measurementId, { send_page_view: false })
}

export const trackEvent = (name: string, params: AnalyticsParams = {}) => {
  if (!measurementId || typeof window === 'undefined') return
  const win = window as AnalyticsWindow
  win.gtag?.('event', name, Object.fromEntries(Object.entries(params).filter(([, value]) => value !== undefined)))
}

export const trackPageView = (path: string) => trackEvent('page_view', { page_path: path })

export const trackItemEvent = (name: 'view_item' | 'add_to_cart' | 'remove_from_cart', product: { id: number; name: string; category?: { name: string }; price: string | number }, quantity = 1) => {
  trackEvent(name, {
    currency: 'BDT',
    value: Number(product.price) * quantity,
    items: JSON.stringify([{ item_id: String(product.id), item_name: product.name, item_category: product.category?.name, price: Number(product.price), quantity }]),
  })
}

