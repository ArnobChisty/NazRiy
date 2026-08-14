import { render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { THEME_STORAGE_KEY } from '../site-theme'
import WebsiteThemeProvider from './WebsiteThemeProvider'

const mocks = vi.hoisted(() => ({ getTheme: vi.fn() }))
vi.mock('../api', () => ({ getWebsiteTheme: mocks.getTheme }))

describe('WebsiteThemeProvider', () => {
  beforeEach(() => mocks.getTheme.mockReset())

  it('applies cached theme immediately then the admin theme', async () => {
    localStorage.setItem(THEME_STORAGE_KEY, 'white')
    mocks.getTheme.mockResolvedValue({ theme: 'pink' })
    render(<WebsiteThemeProvider><span>Website</span></WebsiteThemeProvider>)
    expect(screen.getByText('Website')).toBeInTheDocument()
    expect(document.documentElement.dataset.theme).toBe('white')
    await waitFor(() => expect(document.documentElement.dataset.theme).toBe('pink'))
  })
})
