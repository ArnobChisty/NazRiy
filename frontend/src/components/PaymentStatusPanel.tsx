import type { PaymentInfo } from '../types'
import { paymentFeedback } from '../payment'

interface PaymentStatusPanelProps {
  orderId: number
  payment: PaymentInfo
  busy?: boolean
  onCancel?: () => void
}

export default function PaymentStatusPanel({
  orderId,
  payment,
  busy = false,
  onCancel,
}: PaymentStatusPanelProps) {
  const complete = payment.status === 'paid' || payment.method === 'cash_on_delivery'
  const pendingBkash = payment.status === 'pending' && payment.method === 'bkash'
  const title = complete
    ? 'Order confirmed'
    : pendingBkash
      ? 'bKash payment submitted'
      : payment.status === 'failed'
        ? 'Payment needs attention'
        : payment.status === 'cancelled'
          ? 'Payment cancelled'
          : 'Payment update'

  return (
    <section className={`s5-payment-result ${payment.status}`} aria-labelledby="payment-result-title" aria-live="polite">
      <span className="s5-payment-icon" aria-hidden="true">
        {complete || pendingBkash ? '✓' : payment.status === 'failed' ? '!' : payment.status === 'cancelled' ? '×' : '…'}
      </span>
      <p className="eyebrow">Order #{orderId}</p>
      <h1 id="payment-result-title" tabIndex={-1}>{title}</h1>
      <p>{paymentFeedback(payment)}</p>

      {(pendingBkash || payment.status === 'failed') && (
        <div className="hero-actions">
          <a className="primary-button" href={`/orders/${orderId}`}>View order</a>
          <button className="secondary-button" type="button" disabled={busy} onClick={onCancel}>
            {busy ? 'Cancelling…' : 'Cancel order'}
          </button>
        </div>
      )}

      {(complete || payment.status === 'cancelled') && (
        <div className="hero-actions">
          <a className="primary-button" href={`/orders/${orderId}`}>View order</a>
          <a className="secondary-button" href="/products">Continue shopping</a>
        </div>
      )}
    </section>
  )
}
