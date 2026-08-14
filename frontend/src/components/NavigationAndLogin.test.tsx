import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { user } from '../test/fixtures'
import HomeLogin from './HomeLogin'
import Navbar from './Navbar'

const mocks = vi.hoisted(() => ({
  login: vi.fn(),
  logout: vi.fn(),
  getLinks: vi.fn(),
  auth: { user: null as typeof user | null, restoring: false },
}))

vi.mock('../useAuth', () => ({
  useAuth: () => ({ ...mocks.auth, login: mocks.login, logout: mocks.logout }),
}))
vi.mock('../useCart', () => ({ useCart: () => ({ itemCount: 3 }) }))
vi.mock('../api', () => ({ getNavigationLinks: mocks.getLinks }))

describe('navigation and home login', () => {
  it('opens search and mobile navigation with supplied links', async () => {
    const tester = userEvent.setup()
    render(<Navbar links={[{ id: 1, label: 'Shop', url: '/products', sort_order: 1, open_in_new_tab: false }]} />)
    const logos = screen.getByLabelText('NazRiy home').querySelectorAll('img')
    expect(logos).toHaveLength(2)
    expect(logos[0]).toHaveAttribute('src', '/brand/nazriy-logo.jpeg')
    expect(logos[1]).toHaveAttribute('src', '/brand/nazriy-logo-light.png')
    expect(screen.getByLabelText(/Shopping cart with 3/)).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: 'Search products' }))
    expect(screen.getByRole('search')).toBeInTheDocument()
    await tester.type(screen.getByRole('searchbox'), 'dress')
    await tester.click(screen.getByRole('button', { name: 'Close' }))
    expect(screen.queryByRole('search')).not.toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: 'Toggle navigation' }))
    expect(screen.getByRole('navigation')).toHaveClass('open')
  })

  it('fetches and normalizes legacy women navigation links', async () => {
    mocks.getLinks.mockResolvedValueOnce([
      { id: 1, label: ' Women ', url: '/products?category=Women', sort_order: 1, open_in_new_tab: true },
    ])
    render(<Navbar />)
    await waitFor(() => {
      const link = screen.getByRole('link', { name: /Women/ })
      expect(link).toHaveAttribute('href', '/products?view=women')
      expect(link).toHaveAttribute('target', '_blank')
    })
  })

  it('shows the signed-in account and logs out', async () => {
    mocks.auth.user = user
    const tester = userEvent.setup()
    render(<Navbar activePage="account" links={[]} />)
    expect(screen.getByLabelText(/Open Test's account/)).toHaveClass('active')
    await tester.click(screen.getByRole('button', { name: 'Log out' }))
    expect(mocks.logout).toHaveBeenCalled()
    mocks.auth.user = null
  })

  it('logs in successfully from the homepage', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ token: 'token', user }), { status: 200 })))
    const tester = userEvent.setup()
    render(<HomeLogin />)
    await tester.type(screen.getByLabelText('Username'), 'buyer')
    await tester.type(screen.getByLabelText('Password'), 'StrongPass!42')
    await tester.click(screen.getByRole('button', { name: /Log in/ }))
    await waitFor(() => expect(mocks.login).toHaveBeenCalledWith('token', user))
    expect(screen.getByRole('status')).toHaveTextContent(/Welcome back/)
  })

  it('shows API, fallback, and network login errors', async () => {
    const tester = userEvent.setup()
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Invalid login.' }), { status: 400 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({}), { status: 400 }))
      .mockRejectedValueOnce(new Error('offline'))
    vi.stubGlobal('fetch', fetchMock)
    render(<HomeLogin />)
    await tester.type(screen.getByLabelText('Username'), 'buyer')
    await tester.type(screen.getByLabelText('Password'), 'bad')
    await tester.click(screen.getByRole('button', { name: /Log in/ }))
    expect(await screen.findByText('Invalid login.')).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: /Log in/ }))
    expect(await screen.findByText(/Check your username/)).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: /Log in/ }))
    expect(await screen.findByText(/temporarily unavailable/)).toBeInTheDocument()
  })

  it('shows the current user instead of a login form', () => {
    mocks.auth.user = user
    render(<HomeLogin />)
    expect(screen.getByText(/signed in as/)).toHaveTextContent('Test Buyer')
    expect(screen.queryByLabelText('Username')).not.toBeInTheDocument()
    mocks.auth.user = null
  })
})
