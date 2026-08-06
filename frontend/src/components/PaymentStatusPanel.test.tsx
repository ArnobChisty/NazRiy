import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PaymentStatusPanel from './PaymentStatusPanel'
import { order } from '../test/fixtures'

describe('PaymentStatusPanel', () => {
  it('shows accessible verified-payment evidence', () => {
    render(
      <PaymentStatusPanel
        orderId={5}
        payment={{ ...order.payment, status: 'paid', status_label: 'Paid', provider_reference: 'BK7A1B2C3D' }}
      />,
    )
    expect(screen.getByRole('heading', { name: 'Order confirmed' })).toBeInTheDocument()
    expect(screen.getByText(/BK7A1B2C3D/)).toBeInTheDocument()
    expect(screen.getByRole('link', { name: 'View order' })).toHaveAttribute('href', '/orders/5')
  })

  it('shows pending verification and permits cancellation', async () => {
    const cancel = vi.fn()
    const user = userEvent.setup()
    render(
      <PaymentStatusPanel
        orderId={5}
        payment={{ ...order.payment, provider_reference: 'BK7A1B2C3D' }}
        onCancel={cancel}
      />,
    )
    expect(screen.getByRole('heading', { name: 'bKash payment submitted' })).toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Cancel order' }))
    expect(cancel).toHaveBeenCalledOnce()
  })

  it('shows administrator rejection without offering a fake retry', () => {
    render(
      <PaymentStatusPanel
        orderId={5}
        payment={{ ...order.payment, status: 'failed', status_label: 'Failed', failure_reason: 'Not verified' }}
      />,
    )
    expect(screen.getByRole('heading', { name: 'Payment needs attention' })).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /retry/i })).not.toBeInTheDocument()
  })
})
