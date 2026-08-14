import { act, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from './App'

const mocks = vi.hoisted(() => ({ trackPage: vi.fn() }))

vi.mock('@vercel/analytics/react', () => ({ Analytics: () => <span>Analytics</span> }))
vi.mock('./analytics', () => ({ trackPageView: mocks.trackPage }))
vi.mock('./components/AuthProvider', () => ({ default: ({ children }: { children: React.ReactNode }) => <>{children}</> }))
vi.mock('./components/CartProvider', () => ({ default: ({ children }: { children: React.ReactNode }) => <>{children}</> }))
vi.mock('./components/ProtectedRoute', () => ({ default: ({ children }: { children: React.ReactNode }) => <div>Protected {children}</div> }))
vi.mock('./components/WebsiteThemeProvider', () => ({ default: ({ children }: { children: React.ReactNode }) => <>{children}</> }))
vi.mock('./components/SitePromotions', () => ({ default: () => null }))
vi.mock('./pages/AccountPage', () => ({ default: () => <h1>Account route</h1> }))
vi.mock('./pages/AuthPage', () => ({ default: ({ mode }: { mode: string }) => <h1>Auth {mode}</h1> }))
vi.mock('./pages/CartPage', () => ({ default: () => <h1>Cart route</h1> }))
vi.mock('./pages/HomePage', () => ({ default: () => <h1>Home route</h1> }))
vi.mock('./pages/OrderDetailPage', () => ({ default: ({ orderId }: { orderId: string }) => <h1>Order {orderId}</h1> }))
vi.mock('./pages/OrdersPage', () => ({ default: () => <h1>Orders route</h1> }))
vi.mock('./pages/PasswordRecoveryPage', () => ({ default: ({ mode }: { mode: string }) => <h1>Password {mode}</h1> }))
vi.mock('./pages/ProductDetailsPage', () => ({ default: ({ slug }: { slug: string }) => <h1>Product {slug}</h1> }))
vi.mock('./pages/ProductListingPage', () => ({ default: () => <h1>Products route</h1> }))

describe('App routing', () => {
  const routes: Array<[string, string]> = [
    ['/', 'Home route'],
    ['/login', 'Auth login'],
    ['/register', 'Auth register'],
    ['/forgot-password', 'Password request'],
    ['/reset-password', 'Password confirm'],
    ['/account', 'Account route'],
    ['/orders', 'Orders route'],
    ['/orders/order%201', 'Order order 1'],
    ['/products', 'Products route'],
    ['/products/red%20dress', 'Product red dress'],
    ['/checkout', 'Cart route'],
    ['/cart', 'Cart route'],
    ['/unknown', 'Home route'],
  ]

  it.each(routes)('routes %s to the expected page', async (path, heading) => {
    window.history.pushState({}, '', path)
    render(<App />)
    expect(await screen.findByRole('heading', { name: heading })).toBeInTheDocument()
    expect(screen.getByText('Analytics')).toBeInTheDocument()
    expect(mocks.trackPage).toHaveBeenCalledWith(window.location.pathname)
  })

  it('updates the route after browser history navigation', async () => {
    window.history.pushState({}, '', '/')
    render(<App />)
    act(() => {
      window.history.pushState({}, '', '/products')
      window.dispatchEvent(new PopStateEvent('popstate'))
    })
    expect(await screen.findByRole('heading', { name: 'Products route' })).toBeInTheDocument()
  })
})
