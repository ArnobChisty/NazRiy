import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { product } from '../test/fixtures'
import ProductDetailsPage from './ProductDetailsPage'

const mocks = vi.hoisted(() => ({
  getProduct: vi.fn(),
  availability: vi.fn(),
  related: vi.fn(),
  addItem: vi.fn(),
  track: vi.fn(),
}))

vi.mock('../api', async () => {
  const actual = await vi.importActual<typeof import('../api')>('../api')
  return {
    ...actual,
    getProduct: mocks.getProduct,
    getProductAvailability: mocks.availability,
    getRelatedProducts: mocks.related,
  }
})
vi.mock('../useCart', () => ({ useCart: () => ({ addItem: mocks.addItem }) }))
vi.mock('../analytics', () => ({ trackItemEvent: mocks.track }))
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../components/ProductArtwork', () => ({ default: ({ imageUrl }: { imageUrl?: string }) => <span>Artwork {imageUrl}</span> }))
vi.mock('../components/RecommendationSection', () => ({ default: ({ products }: { products: unknown[] }) => <aside>Recommendations {products.length}</aside> }))

const fullProduct = {
  ...product,
  primary_image: '/main.jpg',
  additional_images: ['/detail.jpg'],
  available_sizes: ['M', 'L'],
  available_colors: ['Red', 'Blue'],
}

describe('ProductDetailsPage integration and negative states', () => {
  beforeEach(() => {
    mocks.getProduct.mockReset().mockResolvedValue(fullProduct)
    mocks.availability.mockReset().mockResolvedValue({ stock_quantity: 4, in_stock: true })
    mocks.related.mockReset().mockResolvedValue([product])
    mocks.addItem.mockReset()
    mocks.track.mockReset()
  })

  it('loads product details, options, size chart, gallery, and recommendations', async () => {
    const tester = userEvent.setup()
    render(<ProductDetailsPage slug="test-set" />)
    expect(await screen.findByRole('heading', { name: 'Test Set' })).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Size guide' })).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: 'L' }))
    await tester.click(screen.getByRole('button', { name: 'Blue' }))
    await tester.click(screen.getByRole('button', { name: 'View image 2' }))
    expect(screen.getAllByText(/Artwork \/detail.jpg/)).toHaveLength(2)
    await waitFor(() => expect(screen.getByText('Recommendations 1')).toBeInTheDocument())
    expect(mocks.track).toHaveBeenCalledWith('view_item', fullProduct)
  })

  it('checks fresh stock and adds the chosen item to cart', async () => {
    const tester = userEvent.setup()
    render(<ProductDetailsPage slug="test-set" />)
    await screen.findByRole('heading', { name: 'Test Set' })
    await tester.click(screen.getByRole('button', { name: '+' }))
    await tester.click(screen.getByRole('button', { name: 'Add to cart' }))
    await waitFor(() => expect(mocks.addItem).toHaveBeenCalledWith(expect.objectContaining({ stock_quantity: 4 }), 'M', 'Red', 2))
    expect(screen.getByRole('status')).toHaveTextContent(/added to your cart/)
  })

  it('reports out-of-stock, reduced-stock, and network errors', async () => {
    const tester = userEvent.setup()
    mocks.availability.mockResolvedValueOnce({ stock_quantity: 0, in_stock: false })
    const view = render(<ProductDetailsPage slug="test-set" />)
    await tester.click(await screen.findByRole('button', { name: 'Add to cart' }))
    expect(screen.getByRole('status')).toHaveTextContent(/currently out of stock/)

    view.unmount()
    mocks.availability.mockResolvedValueOnce({ stock_quantity: 1, in_stock: true })
    render(<ProductDetailsPage slug="test-set" />)
    await screen.findByRole('heading', { name: 'Test Set' })
    await tester.click(screen.getByRole('button', { name: '+' }))
    await tester.click(screen.getByRole('button', { name: 'Add to cart' }))
    expect(screen.getByRole('status')).toHaveTextContent(/Only 1 item/)

    view.unmount()
    mocks.availability.mockRejectedValueOnce(new Error('offline'))
    render(<ProductDetailsPage slug="test-set" />)
    await tester.click(await screen.findByRole('button', { name: 'Add to cart' }))
    expect(screen.getByRole('status')).toHaveTextContent(/could not confirm current stock/)
  })

  it('handles image zoom coordinates and quantity lower bound', async () => {
    const tester = userEvent.setup()
    render(<ProductDetailsPage slug="test-set" />)
    await screen.findByRole('heading', { name: 'Test Set' })
    const gallery = screen.getByLabelText('Test Set images').querySelector('.gallery-main') as HTMLElement
    vi.spyOn(gallery, 'getBoundingClientRect').mockReturnValue({ left: 0, top: 0, width: 200, height: 100, right: 200, bottom: 100, x: 0, y: 0, toJSON: () => ({}) })
    fireEvent.mouseMove(gallery, { clientX: 50, clientY: 25 })
    expect(gallery.style.getPropertyValue('--zoom-x')).toBe('25%')
    await tester.click(screen.getByRole('button', { name: '−' }))
    expect(screen.getByText('1', { selector: '.quantity-row strong' })).toBeInTheDocument()
  })

  it('renders missing and retryable API errors', async () => {
    const { ApiError } = await import('../api')
    mocks.getProduct.mockRejectedValueOnce(new ApiError('missing', 404))
    const view = render(<ProductDetailsPage slug="missing" />)
    expect(await screen.findByText('404')).toBeInTheDocument()
    view.unmount()

    mocks.getProduct.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(fullProduct)
    const tester = userEvent.setup()
    render(<ProductDetailsPage slug="retry" />)
    await tester.click(await screen.findByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('heading', { name: 'Test Set' })).toBeInTheDocument()
  })
})
