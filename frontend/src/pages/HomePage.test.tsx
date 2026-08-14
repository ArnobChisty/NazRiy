import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { product } from '../test/fixtures'
import HomePage from './HomePage'

const mocks = vi.hoisted(() => ({
  homepage: vi.fn(),
  products: vi.fn(),
  featured: vi.fn(),
}))

vi.mock('../api', () => ({
  getHomepageData: mocks.homepage,
  getProducts: mocks.products,
  getFeaturedProducts: mocks.featured,
}))
vi.mock('../components/Navbar', () => ({ default: ({ links }: { links: unknown[] }) => <nav>Navbar {links.length}</nav> }))
vi.mock('../components/HeroSection', () => ({ default: ({ loading }: { loading: boolean }) => <div>Hero {loading ? 'loading' : 'ready'}</div> }))
vi.mock('../components/TopCategories', () => ({ default: ({ loading }: { loading: boolean }) => <div>Top {loading ? 'loading' : 'ready'}</div> }))
vi.mock('../components/HomeLogin', () => ({ default: () => <div>Home login</div> }))
vi.mock('../components/ProductCard', () => ({ default: ({ product: item }: { product: typeof product }) => <article>{item.name}</article> }))

class ObserverStub {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
  constructor() {}
}

const homepageData = {
  site_theme: 'dark' as const,
  banners: [],
  top_products: [],
  featured_products: [product],
  navigation_links: [{ id: 1, label: 'Shop', url: '/products', sort_order: 1, open_in_new_tab: false }],
}

describe('HomePage integration', () => {
  beforeEach(() => {
    vi.stubGlobal('IntersectionObserver', ObserverStub)
    mocks.homepage.mockReset()
    mocks.products.mockReset()
    mocks.featured.mockReset()
  })

  it('loads homepage content and subscribes an email address', async () => {
    mocks.homepage.mockResolvedValue(homepageData)
    const tester = userEvent.setup()
    render(<HomePage />)
    expect(screen.getByText('Hero loading')).toBeInTheDocument()
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    expect(screen.getByText('Navbar 1')).toBeInTheDocument()
    await tester.type(screen.getByLabelText('Email address'), 'buyer@example.com')
    await tester.click(screen.getByRole('button', { name: 'Subscribe' }))
    expect(screen.getByText(/now on the NazRiy update list/)).toBeInTheDocument()
    expect(screen.getByLabelText('Email address')).toHaveValue('')
  })

  it('loads catalogue products when homepage has no featured products', async () => {
    mocks.homepage.mockResolvedValue({ ...homepageData, featured_products: [] })
    mocks.products.mockResolvedValue([product])
    render(<HomePage />)
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    expect(mocks.products).toHaveBeenCalled()
  })

  it('falls back to the featured endpoint after homepage failure', async () => {
    mocks.homepage.mockRejectedValue(new Error('offline'))
    mocks.featured.mockResolvedValue([product])
    render(<HomePage />)
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    expect(mocks.featured).toHaveBeenCalled()
  })

  it('finishes loading even when both homepage and fallback fail', async () => {
    mocks.homepage.mockRejectedValue(new Error('offline'))
    mocks.featured.mockRejectedValue(new Error('offline'))
    render(<HomePage />)
    await waitFor(() => expect(screen.getByText('Hero ready')).toBeInTheDocument())
    expect(screen.queryByLabelText(/Loading NazRiy collection/)).not.toBeInTheDocument()
  })
})
