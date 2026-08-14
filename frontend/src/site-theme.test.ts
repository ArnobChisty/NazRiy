import { describe, expect, it, vi } from 'vitest'
import { applyWebsiteTheme, DEFAULT_THEME, isWebsiteTheme, readCachedTheme, THEME_STORAGE_KEY } from './site-theme'

describe('website theme utilities', () => {
  it('validates supported admin themes', () => {
    expect(isWebsiteTheme('dark')).toBe(true)
    expect(isWebsiteTheme('white')).toBe(true)
    expect(isWebsiteTheme('pink')).toBe(true)
    expect(isWebsiteTheme('blue')).toBe(false)
    expect(isWebsiteTheme(null)).toBe(false)
  })

  it('uses dark when no valid theme is cached', () => {
    expect(readCachedTheme()).toBe(DEFAULT_THEME)
    localStorage.setItem(THEME_STORAGE_KEY, 'blue')
    expect(readCachedTheme()).toBe('dark')
  })

  it('reads, applies, and persists a valid theme', () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'pink')
    expect(readCachedTheme()).toBe('pink')
    applyWebsiteTheme('white')
    expect(document.documentElement).toHaveAttribute('data-theme', 'white')
    expect(document.documentElement.style.colorScheme).toBe('light')
    expect(localStorage.getItem(THEME_STORAGE_KEY)).toBe('white')
    applyWebsiteTheme('dark')
    expect(document.documentElement.style.colorScheme).toBe('dark')
  })

  it('falls back safely when browser storage is unavailable', () => {
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new Error('blocked') })
    expect(readCachedTheme()).toBe('dark')
    vi.restoreAllMocks()
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new Error('blocked') })
    expect(() => applyWebsiteTheme('pink')).not.toThrow()
    expect(document.documentElement).toHaveAttribute('data-theme', 'pink')
  })
})
