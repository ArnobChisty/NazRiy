import { useEffect, type ReactNode } from 'react'
import { getWebsiteTheme } from '../api'
import { applyWebsiteTheme, readCachedTheme } from '../site-theme'

export default function WebsiteThemeProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    applyWebsiteTheme(readCachedTheme())
    let active = true
    const refreshTheme = async () => {
      try {
        const { theme } = await getWebsiteTheme()
        if (active) applyWebsiteTheme(theme)
      } catch {
        // The cached/default theme keeps the website usable while offline.
      }
    }
    const idleId = window.requestIdleCallback?.(() => void refreshTheme(), { timeout: 1000 })
    const timerId = idleId === undefined ? window.setTimeout(() => void refreshTheme(), 0) : undefined
    const refreshOnFocus = () => void refreshTheme()
    const refreshWhenVisible = () => {
      if (document.visibilityState === 'visible') void refreshTheme()
    }
    window.addEventListener('focus', refreshOnFocus)
    document.addEventListener('visibilitychange', refreshWhenVisible)
    return () => {
      active = false
      if (idleId !== undefined) window.cancelIdleCallback?.(idleId)
      if (timerId !== undefined) window.clearTimeout(timerId)
      window.removeEventListener('focus', refreshOnFocus)
      document.removeEventListener('visibilitychange', refreshWhenVisible)
    }
  }, [])

  return children
}
