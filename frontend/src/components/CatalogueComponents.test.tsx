import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { product } from '../test/fixtures'
import EditorialGallery from './EditorialGallery'
import FeaturedProducts from './FeaturedProducts'
import HeroSection from './HeroSection'
import ProductArtwork from './ProductArtwork'
import ProductCard from './ProductCard'
import ReliableImage from './ReliableImage'
import RecommendationSection from './RecommendationSection'
import TopCategories from './TopCategories'

const mocks = vi.hoisted(() => ({
  addItem: vi.fn(),
  availability: vi.fn(),
  featured: vi.fn(),
  topProducts: vi.fn(),
  trackItem: vi.fn(),
}))

vi.mock('../useCart', () => ({ useCart: () => ({ addItem: mocks.addItem }) }))
vi.mock('../analytics', () => ({ trackItemEvent: mocks.trackItem }))
vi.mock('../api', () => ({
  getProductAvailability: mocks.availability,
  getFeaturedProducts: mocks.featured,
  getTopProducts: mocks.topProducts,
}))

const banner = {
  id: 1,
  eyebrow: 'New edit',
  title: 'Autumn collection',
  description: 'Designed in Dhaka',
  desktop_image: '/hero.jpg',
  mobile_image: '/hero-mobile.jpg',
  image_alt: 'NazRiy collection',
  primary_button_label: 'Shop now',
  primary_button_link: '/products',
  secondary_button_label: 'Learn more',
  secondary_button_link: '/#about',
  theme: 'forest',
  object_position: 'center center',
}

describe('catalogue presentation components', () => {
  beforeEach(() => {
    mocks.addItem.mockReset()
    mocks.availability.mockReset()
    mocks.featured.mockReset()
    mocks.topProducts.mockReset().mockResolvedValue([])
    mocks.trackItem.mockReset()
  })

  afterEach(() => vi.useRealTimers())

  it('retries a failed artwork image before showing its fallback', () => {
    vi.useFakeTimers()
    const withImage = { ...product, primary_image: '/dress.jpg' }
    render(<ProductArtwork product={withImage} />)
    fireEvent.error(screen.getByRole('img'))
    act(() => vi.advanceTimersByTime(350))
    fireEvent.error(screen.getByRole('img'))
    act(() => vi.advanceTimersByTime(900))
    fireEvent.error(screen.getByRole('img'))
    act(() => vi.advanceTimersByTime(1800))
    fireEvent.error(screen.getByRole('img'))
    expect(screen.getByLabelText(/placeholder image/)).toBeInTheDocument()
  })

  it('retries storefront images without exposing a broken-image icon', () => {
    vi.useFakeTimers()
    render(<ReliableImage src="/campaign.jpg" alt="Campaign" />)
    const firstAttempt = screen.getByRole('img')
    expect(firstAttempt).toHaveClass('reliable-image-loading')
    fireEvent.error(firstAttempt)
    act(() => vi.advanceTimersByTime(350))
    const secondAttempt = screen.getByRole('img')
    expect(secondAttempt).toHaveClass('reliable-image-loading')
    fireEvent.load(secondAttempt)
    expect(screen.getByRole('img')).toHaveClass('reliable-image-ready')
  })

  it('renders compact placeholder artwork without an image', () => {
    render(<ProductArtwork product={product} compact />)
    expect(screen.getByLabelText(/placeholder image/)).toHaveClass('compact')
  })

  it('adds an available product to the cart and tracks it', async () => {
    mocks.availability.mockResolvedValue({ stock_quantity: 3, in_stock: true })
    const tester = userEvent.setup()
    render(<ProductCard product={product} />)
    await tester.click(screen.getByRole('button', { name: /Add Test Set to favorites/ }))
    expect(screen.getByRole('button', { name: /Remove Test Set from favorites/ })).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: /Add to cart/ }))
    await waitFor(() => expect(mocks.addItem).toHaveBeenCalledWith(expect.objectContaining({ stock_quantity: 3 }), 'M', 'Red', 1))
    expect(mocks.trackItem).toHaveBeenCalledWith('add_to_cart', expect.any(Object))
  })

  it('handles out-of-stock and failed availability checks', async () => {
    const tester = userEvent.setup()
    mocks.availability.mockResolvedValueOnce({ stock_quantity: 0, in_stock: false })
    const view = render(<ProductCard product={product} />)
    await tester.click(screen.getByRole('button', { name: /Add to cart/ }))
    expect((await screen.findAllByText('Out of stock')).length).toBeGreaterThan(0)

    view.unmount()
    mocks.availability.mockRejectedValueOnce(new Error('offline'))
    render(<ProductCard product={product} />)
    await tester.click(screen.getByRole('button', { name: /Add to cart/ }))
    expect(await screen.findByRole('button', { name: /Please try again/ })).toBeInTheDocument()
  })

  it('renders view-only and initially unavailable product cards', () => {
    const unavailable = { ...product, in_stock: false, stock_quantity: 0 }
    const view = render(<ProductCard product={product} allowAddToCart={false} />)
    expect(screen.getByRole('link', { name: /Choose size/ })).toBeInTheDocument()
    view.rerender(<ProductCard product={unavailable} allowAddToCart={false} />)
    expect(screen.getByRole('link', { name: /View product/ })).toBeInTheDocument()
  })

  it('renders recommendation content only when products exist', () => {
    const view = render(<RecommendationSection products={[]} />)
    expect(view.container).toBeEmptyDOMElement()
    view.rerender(<RecommendationSection products={[product]} title="Related pieces" />)
    expect(screen.getByRole('heading', { name: 'Related pieces' })).toBeInTheDocument()
  })

  it('filters and expands the editorial gallery', async () => {
    const tester = userEvent.setup()
    const galleryProduct = {
      ...product,
      primary_image: '/main.jpg',
      additional_images: Array.from({ length: 7 }, (_, index) => `/detail-${index}.jpg`),
    }
    render(<EditorialGallery products={[galleryProduct]} />)
    expect(screen.getAllByRole('link')).toHaveLength(6)
    await tester.click(screen.getByRole('button', { name: /Load more/ }))
    expect(screen.getAllByRole('link')).toHaveLength(8)
    await tester.click(screen.getByRole('button', { name: /Show less/ }))
    await tester.click(screen.getByRole('button', { name: 'New' }))
    expect(screen.getAllByRole('link')).toHaveLength(4)
    await tester.click(screen.getByRole('button', { name: 'Apparel' }))
    expect(screen.getAllByRole('link')).toHaveLength(6)
  })

  it('does not render an editorial gallery without images', () => {
    const view = render(<EditorialGallery products={[product]} />)
    expect(view.container).toBeEmptyDOMElement()
  })

  it('renders hero loading, empty, and interactive carousel states', async () => {
    const tester = userEvent.setup()
    const view = render(<HeroSection loading />)
    expect(screen.getByLabelText(/Loading featured/)).toHaveAttribute('aria-busy', 'true')
    view.rerender(<HeroSection />)
    expect(screen.getByText(/No featured banner/)).toBeInTheDocument()
    view.rerender(<HeroSection banners={[banner, { ...banner, id: 2, title: 'Second collection' }]} />)
    await tester.click(screen.getByRole('button', { name: 'Next banner' }))
    expect(screen.getByText('02 / 02')).toBeInTheDocument()
    await tester.click(screen.getByRole('button', { name: 'Previous banner' }))
    expect(screen.getByText('01 / 02')).toBeInTheDocument()
  })

  it('automatically advances the hero unless it is paused', () => {
    vi.useFakeTimers()
    render(<HeroSection banners={[banner, { ...banner, id: 2, title: 'Second' }]} />)
    act(() => vi.advanceTimersByTime(5600))
    expect(screen.getByText('02 / 02')).toBeInTheDocument()
    fireEvent.mouseEnter(screen.getByLabelText(/Featured NazRiy/))
    act(() => vi.advanceTimersByTime(5600))
    expect(screen.getByText('02 / 02')).toBeInTheDocument()
  })

  it('loads featured products and handles API failure', async () => {
    mocks.featured.mockResolvedValueOnce([product, { ...product, id: 11 }])
    const view = render(<FeaturedProducts />)
    expect(screen.getByLabelText(/Loading featured/)).toBeInTheDocument()
    expect(await screen.findAllByRole('article')).toHaveLength(2)
    view.unmount()
    mocks.featured.mockRejectedValueOnce(new Error('offline'))
    render(<FeaturedProducts />)
    expect(await screen.findByText(/Start the Django server/)).toBeInTheDocument()
  })

  it('renders supplied top products and loading/empty states', () => {
    const placement = { id: 1, product, image: '/top.jpg', image_alt: 'Top dress', sort_order: 0 }
    const view = render(<TopCategories loading />)
    expect(screen.getByLabelText(/Loading top products/)).toBeInTheDocument()
    view.rerender(<TopCategories products={[]} />)
    expect(view.container).toBeEmptyDOMElement()
    view.rerender(<TopCategories products={[placement]} />)
    expect(screen.getByRole('link', { name: /View Test Set/ })).toBeInTheDocument()
  })

  it('fetches top products when none are supplied and tolerates failure', async () => {
    const placement = { id: 1, product, image: '', image_alt: '', sort_order: 0 }
    mocks.topProducts.mockResolvedValueOnce([placement])
    const view = render(<TopCategories />)
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    view.unmount()
    mocks.topProducts.mockRejectedValueOnce(new Error('offline'))
    render(<TopCategories />)
    await waitFor(() => expect(mocks.topProducts).toHaveBeenCalled())
  })
})
