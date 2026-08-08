import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CartPage from './CartPage'
import { order, product, user } from '../test/fixtures'

const clearCart = vi.fn()
const authFetch = vi.fn()
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../components/ProductArtwork', () => ({ default: () => <span>Artwork</span> }))
vi.mock('../useCart', () => ({
  useCart: () => ({
    items: [{ key: '10:M:Red', product, size: 'M', color: 'Red', quantity: 2 }],
    itemCount: 2,
    subtotal: 2000,
    updateQuantity: vi.fn(),
    removeItem: vi.fn(),
    clearCart,
  }),
}))
vi.mock('../useAuth', () => ({ useAuth: () => ({ user, authFetch }) }))

describe('CartPage bKash checkout', () => {
  it('creates an order, submits a bKash transaction ID, and shows pending verification', async () => {
    window.history.pushState({}, '', '/checkout')
    const submitted = { ...order.payment, provider_reference: 'BK7A1B2C3D' }
    authFetch
      .mockResolvedValueOnce(new Response(JSON.stringify(order), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(submitted), { status: 202 }))
    const tester = userEvent.setup()
    render(<CartPage />)
    await tester.type(screen.getByLabelText(/Phone number/), '+8801712345678')
    await tester.type(screen.getByLabelText(/^Address/), '12 Test Road')
    await tester.type(screen.getByLabelText(/^City/), 'Dhaka')
    await tester.type(screen.getByLabelText(/Postal code/), '1205')
    await tester.type(screen.getByLabelText(/bKash transaction ID/), 'bk7a1b2c3d')
    await tester.click(screen.getByRole('button', { name: /Place order/ }))
    expect(await screen.findByRole('heading', { name: 'bKash payment submitted' })).toBeInTheDocument()
    expect(screen.getByText(/BK7A1B2C3D/)).toBeInTheDocument()
    expect(clearCart).toHaveBeenCalledOnce()
    expect(authFetch).toHaveBeenCalledTimes(2)
    const paymentRequest = JSON.parse(authFetch.mock.calls[1][1].body)
    expect(paymentRequest).toMatchObject({ action: 'submit', transaction_id: 'BK7A1B2C3D' })
  })

  it('requires a valid bKash transaction ID accessibly', async () => {
    window.history.pushState({}, '', '/checkout')
    const tester = userEvent.setup()
    render(<CartPage />)
    await tester.click(screen.getByRole('button', { name: /Place order/ }))
    expect(screen.getByRole('alert')).toHaveTextContent(/transaction ID/)
    expect(authFetch).not.toHaveBeenCalled()
  })

  it('hides the bKash verification notice for cash on delivery', async () => {
    window.history.pushState({}, '', '/checkout')
    const tester = userEvent.setup()
    render(<CartPage />)
    await tester.click(screen.getByLabelText(/Cash on delivery/))
    expect(screen.queryByText(/Never share your bKash PIN/)).not.toBeInTheDocument()
  })
})
