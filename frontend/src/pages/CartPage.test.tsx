import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import CartPage from './CartPage'
import { order, product, user } from '../test/fixtures'

const mocks = vi.hoisted(() => ({
  authFetch: vi.fn(),
  clearCart: vi.fn(),
  getBkashPaymentConfig: vi.fn(),
  startHostedPayment: vi.fn(),
}))
const { authFetch, clearCart } = mocks
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../components/ProductArtwork', () => ({ default: () => <span>Artwork</span> }))
vi.mock('../api', () => ({ getBkashPaymentConfig: mocks.getBkashPaymentConfig }))
vi.mock('../checkout-navigation', () => ({ startHostedPayment: mocks.startHostedPayment }))
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
  beforeEach(() => {
    authFetch.mockReset()
    clearCart.mockReset()
    mocks.startHostedPayment.mockReset()
    mocks.getBkashPaymentConfig.mockReset().mockResolvedValue({
      mode: 'manual', automated: false, manual: true,
      merchant_number: '01700000000', environment: '',
    })
  })

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

  it('redirects to hosted bKash checkout without asking for a transaction ID', async () => {
    window.history.pushState({}, '', '/checkout')
    mocks.getBkashPaymentConfig.mockResolvedValue({
      mode: 'automated', automated: true, manual: true,
      merchant_number: '01700000000', environment: 'sandbox',
    })
    authFetch
      .mockResolvedValueOnce(new Response(JSON.stringify(order), { status: 201 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        payment: order.payment,
        redirect_url: 'https://sandbox.example.com/bkash-checkout',
      }), { status: 201 }))
    const tester = userEvent.setup()
    render(<CartPage />)
    expect(await screen.findByText(/verified automatically/)).toBeInTheDocument()
    expect(screen.queryByLabelText(/bKash transaction ID/)).not.toBeInTheDocument()
    await tester.type(screen.getByLabelText(/Phone number/), '+8801712345678')
    await tester.type(screen.getByLabelText(/^Address/), '12 Test Road')
    await tester.type(screen.getByLabelText(/^City/), 'Dhaka')
    await tester.type(screen.getByLabelText(/Postal code/), '1205')
    await tester.click(screen.getByRole('button', { name: /Place order/ }))
    expect(mocks.startHostedPayment).toHaveBeenCalledWith('https://sandbox.example.com/bkash-checkout')
    expect(authFetch.mock.calls[1][0]).toMatch(/payment\/bkash\/create/)
    expect(clearCart).toHaveBeenCalledOnce()
  })

  it('applies a promo quote and submits the verified code with checkout', async () => {
    window.history.pushState({}, '', '/checkout')
    const discountedOrder = {
      ...order,
      discount_code: 'SAVE10',
      discount_amount: '200.00',
      total: '1800.00',
      payment: { ...order.payment, amount: '1800.00' },
    }
    authFetch
      .mockResolvedValueOnce(new Response(JSON.stringify({
        code: 'SAVE10', title: 'Welcome offer', discount_type: 'percentage',
        subtotal: '2000.00', delivery_charge: '0.00', discount_amount: '200.00',
        total: '1800.00', message: 'Promo code applied successfully.',
      }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify(discountedOrder), { status: 201 }))
    const tester = userEvent.setup()
    render(<CartPage />)
    await tester.type(screen.getByLabelText(/Promo code/), 'save10')
    await tester.click(screen.getByRole('button', { name: 'Apply' }))
    expect(await screen.findByText(/Promo code applied successfully/)).toBeInTheDocument()
    expect(screen.getByText('Promo (SAVE10)').parentElement).toHaveTextContent('−৳200')
    await tester.click(screen.getByLabelText(/Cash on delivery/))
    await tester.type(screen.getByLabelText(/Phone number/), '+8801712345678')
    await tester.type(screen.getByLabelText(/^Address/), '12 Test Road')
    await tester.type(screen.getByLabelText(/^City/), 'Dhaka')
    await tester.type(screen.getByLabelText(/Postal code/), '1205')
    await tester.click(screen.getByRole('button', { name: /Place order/ }))
    const checkoutBody = JSON.parse(authFetch.mock.calls[1][1].body)
    expect(checkoutBody.promo_code).toBe('SAVE10')
  })
})
