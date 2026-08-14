import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CartProvider from './CartProvider'
import { useCart } from '../useCart'
import { product } from '../test/fixtures'
import { getProduct } from '../api'

vi.mock('../api', () => ({ getProduct: vi.fn() }))

function CartHarness() {
  const cart = useCart()
  return <>
    <span data-testid="count">{cart.itemCount}</span>
    <span data-testid="subtotal">{cart.subtotal}</span>
    <span data-testid="image">{cart.items[0]?.product.primary_image}</span>
    <span data-testid="color">{cart.items[0]?.color}</span>
    <button onClick={() => cart.addItem(product, 'M', 'Red', 2)}>Add</button>
    <button onClick={() => cart.updateQuantity(`${product.id}:M:Red`, 4)}>Update</button>
    <button onClick={() => cart.removeItem(`${product.id}:M:Red`)}>Remove</button>
    <button onClick={() => cart.clearCart()}>Clear</button>
    <button onClick={() => cart.addItem(product, 'M', 'Red', 1)}>Add same</button>
    <button onClick={() => cart.addItem({ ...product, available_colors: [] }, 'M', 'Default', 1)}>Add default no colour</button>
  </>
}

describe('CartProvider', () => {
  beforeEach(() => {
    vi.mocked(getProduct).mockResolvedValue(product)
  })

  it('calculates totals, persists changes, updates, and removes items', async () => {
    const user = userEvent.setup()
    render(<CartProvider><CartHarness /></CartProvider>)
    await user.click(screen.getByRole('button', { name: 'Add' }))
    expect(screen.getByTestId('count')).toHaveTextContent('2')
    expect(screen.getByTestId('subtotal')).toHaveTextContent('2000')
    expect(localStorage.getItem('nazriy-cart-v1')).toContain('"quantity":2')
    await user.click(screen.getByRole('button', { name: 'Update' }))
    expect(screen.getByTestId('count')).toHaveTextContent('4')
    await user.click(screen.getByRole('button', { name: 'Remove' }))
    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })

  it('restores a valid persisted cart and ignores invalid JSON', () => {
    localStorage.setItem('nazriy-cart-v1', JSON.stringify([{ key: '10:M:Red', product, size: 'M', color: 'Red', quantity: 2 }]))
    const { unmount } = render(<CartProvider><CartHarness /></CartProvider>)
    expect(screen.getByTestId('count')).toHaveTextContent('2')
    unmount()
    localStorage.setItem('nazriy-cart-v1', '{bad json')
    render(<CartProvider><CartHarness /></CartProvider>)
    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })

  it('ignores persisted JSON that is not an array', () => {
    localStorage.setItem('nazriy-cart-v1', JSON.stringify({ item: product }))
    render(<CartProvider><CartHarness /></CartProvider>)
    expect(screen.getByTestId('count')).toHaveTextContent('0')
  })

  it('merges duplicate options, supports default colour fallback, and clears cart', async () => {
    const user = userEvent.setup()
    render(<CartProvider><CartHarness /></CartProvider>)
    await user.click(screen.getByRole('button', { name: 'Add' }))
    await user.click(screen.getByRole('button', { name: 'Add same' }))
    expect(screen.getByTestId('count')).toHaveTextContent('3')
    await user.click(screen.getByRole('button', { name: 'Clear' }))
    expect(screen.getByTestId('count')).toHaveTextContent('0')
    await user.click(screen.getByRole('button', { name: 'Add default no colour' }))
    expect(screen.getByTestId('color')).toHaveTextContent('')
  })

  it('refreshes persisted product data so temporary media URLs do not expire in the cart', async () => {
    const staleProduct = { ...product, primary_image: 'https://storage.example/expired.jpg' }
    const refreshedProduct = { ...product, primary_image: 'https://storage.example/fresh.jpg' }
    localStorage.setItem('nazriy-cart-v1', JSON.stringify([{ key: '10:M:Red', product: staleProduct, size: 'M', color: 'Red', quantity: 2 }]))
    vi.mocked(getProduct).mockResolvedValue(refreshedProduct)

    render(<CartProvider><CartHarness /></CartProvider>)

    await waitFor(() => expect(screen.getByTestId('image')).toHaveTextContent(refreshedProduct.primary_image))
    expect(getProduct).toHaveBeenCalledWith(product.slug)
  })

  it('replaces the legacy Default colour with the product default colour', async () => {
    localStorage.setItem('nazriy-cart-v1', JSON.stringify([{ key: '10:M:Default', product, size: 'M', color: 'Default', quantity: 1 }]))
    vi.mocked(getProduct).mockResolvedValue(product)
    render(<CartProvider><CartHarness /></CartProvider>)
    await waitFor(() => expect(screen.getByTestId('color')).toHaveTextContent('Red'))
    expect(screen.getByTestId('color')).not.toHaveTextContent('Default')
  })

  it('keeps a stored item when refreshing its product fails', async () => {
    localStorage.setItem('nazriy-cart-v1', JSON.stringify([{ key: '10:M:Red', product, size: 'M', color: 'Red', quantity: 2 }]))
    vi.mocked(getProduct).mockRejectedValue(new Error('offline'))
    render(<CartProvider><CartHarness /></CartProvider>)
    await waitFor(() => expect(getProduct).toHaveBeenCalled())
    expect(screen.getByTestId('count')).toHaveTextContent('2')
  })
})
