import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { THEME_STORAGE_KEY } from '../site-theme'
import WebsiteThemeProvider from './WebsiteThemeProvider'

const mocks = vi.hoisted(() => ({ getTheme: vi.fn() }))
vi.mock('../api', () => ({ getWebsiteTheme: mocks.getTheme }))

describe('WebsiteThemeProvider', () => {
  const originalRequestIdleCallback = window.requestIdleCallback
  const originalCancelIdleCallback = window.cancelIdleCallback

  beforeEach(() => {
    mocks.getTheme.mockReset()
    localStorage.clear()
  })

  afterEach(() => {
    Object.defineProperty(window, 'requestIdleCallback', {
      configurable: true,
      value: originalRequestIdleCallback,
    })
    Object.defineProperty(window, 'cancelIdleCallback', {
      configurable: true,
      value: originalCancelIdleCallback,
    })
  })

  it('applies cached theme immediately then the admin theme', async () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'white')
    mocks.getTheme.mockResolvedValue({ theme: 'pink' })
    render(<WebsiteThemeProvider><span>Website</span></WebsiteThemeProvider>)
    expect(screen.getByText('Website')).toBeInTheDocument()
    expect(document.documentElement.dataset.theme).toBe('white')
    await waitFor(() => expect(document.documentElement.dataset.theme).toBe('pink'))
  })

  it('keeps the cached theme when the theme service is unavailable', async () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'dark')
    mocks.getTheme.mockRejectedValue(new Error('offline'))

    render(<WebsiteThemeProvider><span>Offline website</span></WebsiteThemeProvider>)

    await waitFor(() => expect(mocks.getTheme).toHaveBeenCalledTimes(1))
    expect(document.documentElement.dataset.theme).toBe('dark')
  })

  it('uses idle refresh and cancels it when the provider unmounts', async () => {
    let idleCallback: IdleRequestCallback | undefined
    const requestIdleCallback = vi.fn((callback: IdleRequestCallback) => {
      idleCallback = callback
      return 17
    })
    const cancelIdleCallback = vi.fn()
    Object.defineProperty(window, 'requestIdleCallback', {
      configurable: true,
      value: requestIdleCallback,
    })
    Object.defineProperty(window, 'cancelIdleCallback', {
      configurable: true,
      value: cancelIdleCallback,
    })
    mocks.getTheme.mockResolvedValue({ theme: 'white' })

    const view = render(<WebsiteThemeProvider><span>Idle website</span></WebsiteThemeProvider>)
    expect(mocks.getTheme).not.toHaveBeenCalled()

    idleCallback?.({ didTimeout: false, timeRemaining: () => 10 })
    await waitFor(() => expect(document.documentElement.dataset.theme).toBe('white'))
    view.unmount()

    expect(requestIdleCallback).toHaveBeenCalledTimes(1)
    expect(cancelIdleCallback).toHaveBeenCalledWith(17)
  })

  it('does not apply a late response after unmounting', async () => {
    let resolveTheme: ((value: { theme: 'pink' }) => void) | undefined
    mocks.getTheme.mockReturnValue(new Promise((resolve) => { resolveTheme = resolve }))
    localStorage.setItem(THEME_STORAGE_KEY, 'white')

    const view = render(<WebsiteThemeProvider><span>Temporary website</span></WebsiteThemeProvider>)
    await waitFor(() => expect(mocks.getTheme).toHaveBeenCalledTimes(1))
    view.unmount()
    resolveTheme?.({ theme: 'pink' })

    await Promise.resolve()
    expect(document.documentElement.dataset.theme).toBe('white')
  })
})
