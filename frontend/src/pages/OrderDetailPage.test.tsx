import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { order } from '../test/fixtures'
import OrderDetailPage from './OrderDetailPage'

const mocks = vi.hoisted(() => ({ authFetch: vi.fn() }))
vi.mock('../useAuth', () => ({ useAuth: () => ({ authFetch: mocks.authFetch }) }))
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))

const response = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } })

describe('OrderDetailPage', () => {
  beforeEach(() => mocks.authFetch.mockReset())

  it('renders order tracking, delivery, items, and payment details', async () => {
    mocks.authFetch.mockResolvedValue(response(order))
    render(<OrderDetailPage orderId="5" />)
    expect(screen.getByRole('heading', { name: /Loading order/ })).toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: /on its way/ })).toBeInTheDocument()
    expect(screen.getByText('Test Set')).toBeInTheDocument()
    expect(screen.getByRole('heading', { name: 'Payment summary' })).toBeInTheDocument()
    expect(mocks.authFetch).toHaveBeenCalledWith('/orders/5/')
  })

  it('renders delivered and cancelled order variants', async () => {
    mocks.authFetch.mockResolvedValueOnce(response({ ...order, status: 'delivered', status_label: 'Delivered' }))
    const view = render(<OrderDetailPage orderId="5" />)
    expect(await screen.findByRole('heading', { name: /Delivered with care/ })).toBeInTheDocument()
    view.unmount()
    mocks.authFetch.mockResolvedValueOnce(response({ ...order, status: 'cancelled', status_label: 'Cancelled' }))
    render(<OrderDetailPage orderId="6" />)
    expect(await screen.findByText(/reserved inventory was returned/)).toBeInTheDocument()
  })

  it('shows an order-not-found state', async () => {
    mocks.authFetch.mockResolvedValue(response({}, 404))
    render(<OrderDetailPage orderId="missing order" />)
    expect(await screen.findByRole('heading', { name: 'Order not found' })).toBeInTheDocument()
    expect(mocks.authFetch).toHaveBeenCalledWith('/orders/missing%20order/')
  })

  it('shows an error and retries successfully', async () => {
    mocks.authFetch
      .mockRejectedValueOnce(new Error('offline'))
      .mockResolvedValueOnce(response(order))
    const tester = userEvent.setup()
    render(<OrderDetailPage orderId="5" />)
    await tester.click(await screen.findByRole('button', { name: 'Try again' }))
    expect(await screen.findByText('Test Set')).toBeInTheDocument()
    expect(mocks.authFetch).toHaveBeenCalledTimes(2)
  })
})
