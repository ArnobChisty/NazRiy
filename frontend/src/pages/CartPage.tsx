import { useEffect, useRef, useState, type FormEvent } from 'react'
import Navbar from '../components/Navbar'
import PaymentStatusPanel from '../components/PaymentStatusPanel'
import ProductArtwork from '../components/ProductArtwork'
import { formatPrice } from '../format'
import { createRequestId, parsePayment } from '../payment'
import type { CustomerOrder, PaymentInfo } from '../types'
import { useAuth } from '../useAuth'
import { useCart } from '../useCart'
import './Sprint3.css'
import { trackEvent, trackItemEvent } from '../analytics'

type CheckoutState = 'idle' | 'creating' | 'processing' | 'failed' | 'complete' | 'cancelled'
type PaymentMethod = 'bkash' | 'cash_on_delivery'

const validEmail = /^\S+@\S+\.\S+$/
const validPhone = /^[+\d][\d\s-]{7,}$/
const validBkashTransaction = /^[A-Za-z0-9]{8,32}$/
const bkashMerchantNumber = import.meta.env.VITE_BKASH_MERCHANT_NUMBER
  || (import.meta.env.MODE === 'test' ? '01700000000' : '')
const bkashAvailable = Boolean(bkashMerchantNumber)

export default function CartPage() {
  const { items, itemCount, subtotal, updateQuantity, removeItem, clearCart } = useCart()
  const { user, authFetch } = useAuth()
  const checkout = window.location.pathname.replace(/\/$/, '') === '/checkout'
  const delivery = items.length === 0 || subtotal >= 2000 ? 0 : 80
  const total = subtotal + delivery
  const [form, setForm] = useState({
    name: user?.full_name || '',
    email: user?.email || '',
    phone: '',
    address: '',
    city: '',
    postal_code: '',
  })
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>(bkashAvailable ? 'bkash' : 'cash_on_delivery')
  const [bkashTransactionId, setBkashTransactionId] = useState('')
  const [state, setState] = useState<CheckoutState>('idle')
  const [message, setMessage] = useState('')
  const [order, setOrder] = useState<CustomerOrder | null>(null)
  const [payment, setPayment] = useState<PaymentInfo | null>(null)
  const statusRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (state !== 'idle') statusRef.current?.focus()
  }, [state])

  const submitBkash = async (orderId: number, transactionId: string) => {
    setState('processing')
    setMessage('Submitting your bKash transaction ID for verification…')
    try {
      const response = await authFetch(`/orders/${orderId}/payment/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'submit',
          transaction_id: transactionId.trim(),
          request_id: createRequestId(),
        }),
      })
      const result = await parsePayment(response)
      setPayment(result)
      setState('complete')
      setMessage('')
    } catch (error) {
      const failure = error instanceof Error ? error.message : 'Unable to submit the bKash payment.'
      setPayment((current) => current ? {
        ...current,
        status: 'failed',
        status_label: 'Failed',
        failure_reason: failure,
      } : current)
      setState('failed')
      setMessage(failure)
    }
  }

  const cancelPayment = async () => {
    if (!order) return
    setState('processing')
    setMessage('Cancelling your order…')
    try {
      const response = await authFetch(`/orders/${order.id}/payment/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'cancel', request_id: createRequestId() }),
      })
      const result = await parsePayment(response)
      setPayment(result)
      setState('cancelled')
      setMessage('')
    } catch (error) {
      const failure = error instanceof Error ? error.message : 'Unable to cancel this payment.'
      setState('failed')
      setMessage(failure)
    }
  }

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setMessage('')
    const missing = Object.values(form).some((value) => !value.trim())
    const invalidBkash = paymentMethod === 'bkash' && !validBkashTransaction.test(bkashTransactionId.trim())
    if (missing || !validEmail.test(form.email) || !validPhone.test(form.phone) || invalidBkash) {
      setState('failed')
      setMessage(
        invalidBkash
          ? 'Enter the 8–32 character transaction ID from your bKash confirmation.'
          : 'Enter valid information in every required field.',
      )
      return
    }
    if (!user) {
      setState('failed')
      setMessage('Log in before placing your order.')
      return
    }

    setState('creating')
    trackEvent('begin_checkout', { currency: 'BDT', value: total, items: JSON.stringify(items.map(item => ({ item_id: String(item.product.id), item_name: item.product.name, price: Number(item.product.price), quantity: item.quantity }))) })
    try {
      const response = await authFetch('/orders/checkout/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          payment_method: paymentMethod,
          idempotency_key: createRequestId(),
          items: items.map((item) => ({
            product_id: item.product.id,
            quantity: item.quantity,
            size: item.size,
            color: item.color,
          })),
        }),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        throw new Error(typeof data.detail === 'string' ? data.detail : 'Unable to create the order.')
      }
      const nextOrder = data as CustomerOrder
      setOrder(nextOrder)
      setPayment(nextOrder.payment)
      trackEvent('purchase', { transaction_id: String(nextOrder.id), currency: 'BDT', value: Number(nextOrder.total), items: JSON.stringify(items.map(item => ({ item_id: String(item.product.id), item_name: item.product.name, price: Number(item.product.price), quantity: item.quantity }))) })
      clearCart()
      if (paymentMethod === 'cash_on_delivery') {
        setState('complete')
      } else {
        await submitBkash(nextOrder.id, bkashTransactionId)
      }
    } catch (error) {
      setState('failed')
      setMessage(error instanceof Error ? error.message : 'Unable to create the order.')
    }
  }

  if (order && payment) {
    return (
      <div className="site-shell">
        <Navbar activePage="cart" />
        <main id="main-content" className="s3-state s5-payment-page" ref={statusRef} tabIndex={-1}>
          {state === 'processing' ? (
            <section className="s5-payment-result pending" aria-live="assertive">
              <span className="s4-spinner" aria-hidden="true" />
              <h1>Updating bKash payment</h1>
              <p>{message}</p>
            </section>
          ) : (
            <PaymentStatusPanel orderId={order.id} payment={payment} busy={false} onCancel={cancelPayment} />
          )}
        </main>
      </div>
    )
  }

  if (items.length === 0) {
    return (
      <div className="site-shell">
        <Navbar activePage="cart" />
        <main id="main-content" className="s3-state">
          <span>0</span><h1>Your cart is empty</h1>
          <p>Explore the collection and add a piece to continue.</p>
          <a className="primary-button" href="/products">Browse products →</a>
        </main>
      </div>
    )
  }

  const busy = state === 'creating' || state === 'processing'
  return (
    <div className="site-shell">
      <Navbar activePage="cart" />
      <main id="main-content" className={checkout ? 'cart-page checkout-active' : 'cart-page'}>
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          <a href="/">Home</a><span>/</span><span>{checkout ? 'Checkout' : 'Cart'}</span>
        </nav>
        <header className="cart-page-heading">
          <div>
            <p className="eyebrow">{checkout ? 'Secure checkout' : 'Your selection'}</p>
            <h1>{checkout ? 'Delivery and payment' : 'Shopping cart'}</h1>
          </div>
          {!checkout && <button onClick={clearCart}>Clear cart</button>}
        </header>
        <div className="cart-layout">
          <section className={checkout ? 'delivery-form-panel' : 'cart-items'}>
            {checkout ? (
              <form className="s3-delivery-form" onSubmit={submit} noValidate aria-describedby="bkash-notice">
                <div className="s3-field-grid">
                  {([
                    ['name', 'Full name', 'text', 'name'],
                    ['email', 'Email', 'email', 'email'],
                    ['phone', 'Phone number', 'tel', 'tel'],
                    ['address', 'Address', 'text', 'street-address'],
                    ['city', 'City', 'text', 'address-level2'],
                    ['postal_code', 'Postal code', 'text', 'postal-code'],
                  ] as const).map(([key, label, type, autocomplete]) => (
                    <label htmlFor={`checkout-${key}`} key={key}>
                      {label} *
                      <input
                        id={`checkout-${key}`}
                        name={key}
                        type={type}
                        autoComplete={autocomplete}
                        required
                        disabled={busy}
                        aria-invalid={state === 'failed' && !form[key].trim()}
                        value={form[key]}
                        onChange={(event) => setForm({ ...form, [key]: event.target.value })}
                      />
                    </label>
                  ))}
                </div>

                <fieldset className="s5-payment-methods">
                  <legend>Payment method</legend>
                  <label>
                    <input type="radio" name="payment_method" value="bkash" disabled={!bkashAvailable} checked={paymentMethod === 'bkash'} onChange={() => setPaymentMethod('bkash')} />
                    <span>
                      <strong>bKash</strong>
                      <small>{bkashAvailable ? 'Send Money and submit the transaction ID for verification.' : 'Temporarily unavailable until the merchant number is configured.'}</small>
                    </span>
                  </label>
                  <label>
                    <input type="radio" name="payment_method" value="cash_on_delivery" checked={paymentMethod === 'cash_on_delivery'} onChange={() => setPaymentMethod('cash_on_delivery')} />
                    <span><strong>Cash on delivery</strong><small>Payment remains pending until delivery.</small></span>
                  </label>
                </fieldset>

                {paymentMethod === 'bkash' && (
                  <section className="s5-bkash-details" aria-labelledby="bkash-payment-title">
                    <h2 id="bkash-payment-title">Pay with bKash</h2>
                    <ol>
                      <li>Open bKash and choose <strong>Send Money</strong>.</li>
                      <li>Send <strong>{formatPrice(total)}</strong> to <strong>{bkashMerchantNumber}</strong>.</li>
                      <li>Enter the transaction ID from the confirmation message below.</li>
                    </ol>
                    <label htmlFor="bkash-transaction-id">
                      bKash transaction ID *
                      <input
                        id="bkash-transaction-id"
                        name="bkash_transaction_id"
                        autoComplete="off"
                        inputMode="text"
                        maxLength={32}
                        required
                        disabled={busy}
                        aria-invalid={state === 'failed' && !validBkashTransaction.test(bkashTransactionId.trim())}
                        value={bkashTransactionId}
                        onChange={(event) => setBkashTransactionId(event.target.value.toUpperCase())}
                      />
                    </label>
                  </section>
                )}

                <p id="bkash-notice" className="s5-bkash-notice">
                  Your order remains pending until NazRiy verifies the transaction ID against the merchant account.
                  Never share your bKash PIN or verification code.
                </p>
                {message && <p className="s3-error" role="alert">{message}</p>}
                {!user && (
                  <p className="s3-login-note">
                    Already have an account? <a href={`/login?next=${encodeURIComponent('/checkout')}`}>Log in</a> before placing your order.
                  </p>
                )}
                <button className="s3-place-order" disabled={busy}>
                  {busy ? 'Creating secure order…' : `Place order · ${formatPrice(total)}`}
                </button>
              </form>
            ) : items.map((item) => (
              <article className="cart-item" key={item.key}>
                <a className="cart-item-image" href={`/products/${item.product.slug}`}><ProductArtwork product={item.product} /></a>
                <div className="cart-item-info">
                  <p>{item.product.category.name}</p>
                  <h2><a href={`/products/${item.product.slug}`}>{item.product.name}</a></h2>
                  <div className="cart-item-options">
                    {item.size && <span>Size: {item.size}</span>}
                    {item.color && <span>Colour: {item.color}</span>}
                  </div>
                  <button className="remove-item" onClick={() => { trackItemEvent('remove_from_cart', item.product, item.quantity); removeItem(item.key) }}>Remove</button>
                </div>
                <div className="cart-item-controls">
                  <div className="cart-quantity" aria-label={`Quantity for ${item.product.name}`}>
                    <button onClick={() => updateQuantity(item.key, item.quantity - 1)} aria-label="Decrease quantity">−</button>
                    <strong>{item.quantity}</strong>
                    <button disabled={item.quantity >= item.product.stock_quantity} onClick={() => updateQuantity(item.key, item.quantity + 1)} aria-label="Increase quantity">+</button>
                  </div>
                  <strong>{formatPrice(Number(item.product.price) * item.quantity)}</strong>
                  <small>{item.product.stock_quantity} in stock</small>
                </div>
              </article>
            ))}
          </section>

          <aside className="order-summary">
            <p className="eyebrow">Checkout</p><h2>Order summary</h2>
            <dl>
              <div><dt>Items ({itemCount})</dt><dd>{formatPrice(subtotal)}</dd></div>
              <div><dt>Delivery</dt><dd>{delivery === 0 ? 'Free' : formatPrice(delivery)}</dd></div>
              <div className="order-total"><dt>Total</dt><dd>{formatPrice(total)}</dd></div>
            </dl>
            {subtotal < 2000 && <p className="delivery-progress">Add {formatPrice(2000 - subtotal)} more for free delivery.</p>}
            {checkout
              ? <a className="s3-summary-action" href="/cart">← Edit cart</a>
              : <a className="s3-summary-action" href="/checkout">Continue to checkout</a>}
            <a href="/products">← Continue shopping</a>
          </aside>
        </div>
      </main>
    </div>
  )
}
