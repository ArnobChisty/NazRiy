import { useCallback, useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { formatPrice } from '../format'
import type { CustomerOrder } from '../types'
import { useAuth } from '../useAuth'
import './Sprint4.css'

const steps = ['confirmed', 'shipped', 'delivered'] as const

export default function OrderDetailPage({ orderId }: { orderId: string }) {
  const { authFetch } = useAuth()
  const [order, setOrder] = useState<CustomerOrder | null>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'error' | 'missing'>('loading')

  const load = useCallback(() => {
    authFetch(`/orders/${encodeURIComponent(orderId)}/`)
      .then(async (response) => {
        if (response.status === 404) {
          setState('missing')
          return
        }
        if (!response.ok) throw new Error()
        setOrder(await response.json())
        setState('ready')
      })
      .catch(() => setState('error'))
  }, [authFetch, orderId])

  useEffect(load, [load])

  const retry = () => {
    setState('loading')
    load()
  }

  if (state !== 'ready' || !order) {
    return (
      <div className="site-shell">
        <Navbar activePage="orders" />
        <main id="main-content" className="s4-page">
          <div className="s4-list-state" role={state === 'error' ? 'alert' : undefined}>
            <span className={state === 'loading' ? 's4-spinner' : ''}>
              {state === 'missing' ? '?' : state === 'error' ? '!' : ''}
            </span>
            <h1>{state === 'loading' ? 'Loading order…' : state === 'missing' ? 'Order not found' : 'We could not load this order.'}</h1>
            {state === 'error' && <button onClick={retry}>Try again</button>}
            {state === 'missing' && <a href="/orders">Return to your orders</a>}
          </div>
        </main>
      </div>
    )
  }

  const activeIndex = steps.indexOf(order.status as typeof steps[number])

  return (
    <div className="site-shell">
      <Navbar activePage="orders" />
      <main id="main-content" className="s4-page">
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          <a href="/">Home</a><span>/</span><a href="/orders">Orders</a><span>/</span><span>#{order.id}</span>
        </nav>
        <header className="s4-heading">
          <div>
            <p className="eyebrow">Order #{order.id}</p>
            <h1>{order.status === 'delivered' ? 'Delivered with care.' : order.status === 'cancelled' ? 'Order cancelled.' : 'Your order is on its way.'}</h1>
          </div>
          <div className="s4-order-badges">
            <span className={`s4-payment-status ${order.payment.status}`}>{order.payment.status_label}</span>
            <span className={`s4-status ${order.status}`}>{order.status_label}</span>
          </div>
        </header>
        <section className={`s4-tracking ${order.status === 'cancelled' ? 'cancelled' : ''}`} aria-label="Order tracking">
          <h2>Order progress</h2>
          {order.status === 'cancelled' ? (
            <p>This order has been cancelled and its reserved inventory was returned.</p>
          ) : (
            <ol>
              {steps.map((step, index) => (
                <li className={index <= activeIndex ? 'complete' : ''} key={step}>
                  <span aria-hidden="true">{index < activeIndex ? '✓' : index + 1}</span>
                  <div>
                    <strong>{step === 'confirmed' ? 'Confirmed' : step === 'shipped' ? 'Shipped' : 'Delivered'}</strong>
                    <small>{step === 'confirmed' ? 'We received your order.' : step === 'shipped' ? 'Your pieces are travelling to you.' : 'Order complete.'}</small>
                  </div>
                </li>
              ))}
            </ol>
          )}
        </section>
        <div className="s4-detail-grid">
          <section className="s4-card">
            <div className="s4-card-heading">
              <span>01</span>
              <div>
                <h2>Ordered pieces</h2>
                <p>{new Intl.DateTimeFormat('en-BD', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(order.created_at))}</p>
              </div>
            </div>
            <div className="s4-items">
              {order.items.map((item, index) => (
                <article key={`${item.product_slug}-${index}`}>
                  <div>{item.product_image ? <img src={item.product_image} alt="" loading="lazy" decoding="async" /> : <span aria-hidden="true">N</span>}</div>
                  <section>
                    <h3><a href={`/products/${item.product_slug}`}>{item.product_name}</a></h3>
                    <p>{[item.size && `Size: ${item.size}`, item.color && `Colour: ${item.color}`].filter(Boolean).join(' · ') || 'Standard option'}</p>
                    <small>{item.quantity} × {formatPrice(Number(item.unit_price))}</small>
                  </section>
                  <strong>{formatPrice(Number(item.line_total))}</strong>
                </article>
              ))}
            </div>
          </section>
          <aside className="s4-detail-side">
            <section className="s4-card">
              <h2>Delivery details</h2>
              <address>
                <strong>{order.name}</strong><span>{order.address}</span>
                <span>{order.city} {order.postal_code}</span><span>{order.phone}</span><span>{order.email}</span>
              </address>
            </section>
            <section className="s4-card s4-payment">
              <h2>Payment summary</h2>
              <dl>
                <div><dt>Method</dt><dd>{order.payment.method_label}</dd></div>
                <div><dt>Status</dt><dd>{order.payment.status_label}</dd></div>
                <div><dt>Subtotal</dt><dd>{formatPrice(Number(order.subtotal))}</dd></div>
                <div><dt>Delivery</dt><dd>{Number(order.delivery_charge) === 0 ? 'Free' : formatPrice(Number(order.delivery_charge))}</dd></div>
                {Number(order.discount_amount) > 0 && <div><dt>Promo ({order.discount_code})</dt><dd>−{formatPrice(Number(order.discount_amount))}</dd></div>}
                <div><dt>Total</dt><dd>{formatPrice(Number(order.total))}</dd></div>
              </dl>
            </section>
          </aside>
        </div>
      </main>
    </div>
  )
}
