import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import OrdersPage from './OrdersPage'

const authFetch = vi.fn()
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../useAuth', () => ({ useAuth: () => ({ authFetch }) }))

describe('OrdersPage', () => {
  it('shows a helpful empty state', async () => {
    authFetch.mockResolvedValue(new Response('[]', { status: 200 }))
    render(<OrdersPage />)
    expect(await screen.findByRole('heading', { name: 'No orders yet' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Explore products/ })).toHaveAttribute('href', '/products')
  })

  it('announces errors and retries', async () => {
    const tester = userEvent.setup()
    authFetch.mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(new Response('[]', { status: 200 }))
    render(<OrdersPage />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/could not load/)
    await tester.click(screen.getByRole('button', { name: 'Try again' }))
    expect(await screen.findByRole('heading', { name: 'No orders yet' })).toBeInTheDocument()
    expect(authFetch).toHaveBeenCalledTimes(2)
  })
})
