import type { WebsiteTheme } from './types'

export const DEFAULT_THEME: WebsiteTheme = 'dark'
export const THEME_STORAGE_KEY = 'nazriy-site-theme'
const themes: WebsiteTheme[] = ['dark', 'white', 'pink']

export const isWebsiteTheme = (value: unknown): value is WebsiteTheme =>
  typeof value === 'string' && themes.includes(value as WebsiteTheme)

export const readCachedTheme = (): WebsiteTheme => {
  try {
    const cached = window.localStorage.getItem(THEME_STORAGE_KEY)
    return isWebsiteTheme(cached) ? cached : DEFAULT_THEME
  } catch {
    return DEFAULT_THEME
  }
}

export const applyWebsiteTheme = (theme: WebsiteTheme) => {
  document.documentElement.dataset.theme = theme
  document.documentElement.style.colorScheme = theme === 'dark' ? 'dark' : 'light'
  try { window.localStorage.setItem(THEME_STORAGE_KEY, theme) } catch { /* storage is optional */ }
}
