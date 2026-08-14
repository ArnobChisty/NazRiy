import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { product } from '../test/fixtures'
import ProductListingPage from './ProductListingPage'

const mocks = vi.hoisted(() => ({ products: vi.fn(), categories: vi.fn() }))
vi.mock('../api', () => ({ getProducts: mocks.products, getCategories: mocks.categories }))
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../components/ProductCard', () => ({ default: ({ product: item }: { product: typeof product }) => <article>{item.name}</article> }))

describe('ProductListingPage integration', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/products')
    mocks.products.mockReset().mockResolvedValue([product])
    mocks.categories.mockReset().mockResolvedValue([product.category])
  })

  it('loads products and applies catalogue filters', async () => {
    const tester = userEvent.setup()
    render(<ProductListingPage />)
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    expect(screen.getByText('1 piece')).toBeInTheDocument()
    await tester.type(screen.getByPlaceholderText('Product name'), 'dress')
    await tester.type(screen.getByPlaceholderText('Min'), '500')
    await tester.selectOptions(screen.getByLabelText('Size'), 'M')
    await tester.selectOptions(screen.getByLabelText('Colour'), 'Red')
    await tester.click(screen.getByRole('button', { name: 'Apply filters' }))
    await waitFor(() => expect(mocks.products).toHaveBeenCalledWith(expect.objectContaining({ search: 'dress', min_price: '500', size: 'M', color: 'Red' })))
  })

  it('changes ordering and resets filters', async () => {
    const tester = userEvent.setup()
    render(<ProductListingPage />)
    await screen.findByText('Test Set')
    await tester.selectOptions(screen.getByLabelText('Sort'), 'price_desc')
    await waitFor(() => expect(mocks.products).toHaveBeenCalledWith(expect.objectContaining({ ordering: 'price_desc' })))
    await tester.click(screen.getByRole('button', { name: 'Reset all' }))
    await waitFor(() => expect(mocks.products).toHaveBeenCalledWith(expect.objectContaining({ search: '', min_price: '' })))
  })

  it('renders women and new-arrival catalogue headings from navigation', async () => {
    window.history.pushState({}, '', '/products?view=women')
    const view = render(<ProductListingPage />)
    expect(screen.getByRole('heading', { name: 'Designed for her.' })).toBeInTheDocument()
    view.unmount()
    window.history.pushState({}, '', '/products?ordering=newest')
    render(<ProductListingPage />)
    expect(screen.getByRole('heading', { name: 'The latest from NazRiy.' })).toBeInTheDocument()
  })

  it('renders empty results and clears filters', async () => {
    mocks.products.mockResolvedValue([])
    const tester = userEvent.setup()
    render(<ProductListingPage />)
    await tester.click(await screen.findByRole('button', { name: 'Clear filters' }))
    expect(mocks.products).toHaveBeenCalled()
  })

  it('renders an API error and retries', async () => {
    mocks.products.mockRejectedValueOnce(new Error('offline')).mockResolvedValue([product])
    const tester = userEvent.setup()
    render(<ProductListingPage />)
    await tester.click(await screen.findByRole('button', { name: 'Try again' }))
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
  })
})
