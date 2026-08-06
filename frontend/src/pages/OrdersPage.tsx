import { useCallback, useEffect, useState } from 'react'
import Navbar from '../components/Navbar'
import { formatPrice } from '../format'
import type { CustomerOrder } from '../types'
import { useAuth } from '../useAuth'
import './Sprint4.css'

export default function OrdersPage() {
  const { authFetch } = useAuth()
  const [orders, setOrders] = useState<CustomerOrder[]>([])
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading')

  const load = useCallback(() => {
    authFetch('/orders/')
      .then(async (response) => {
        if (!response.ok) throw new Error()
        setOrders(await response.json())
        setState('ready')
      })
      .catch(() => setState('error'))
  }, [authFetch])

  useEffect(load, [load])

  const retry = () => {
    setState('loading')
    load()
  }

  return (
    <div className="site-shell">
      <Navbar activePage="orders" />
      <main id="main-content" className="s4-page">
        <nav className="breadcrumbs" aria-label="Breadcrumb">
          <a href="/">Home</a><span>/</span><span>Orders</span>
        </nav>
        <header className="s4-heading">
          <div><p className="eyebrow">Post-purchase care</p><h1>Your orders</h1></div>
          <p>Follow each order from payment through delivery.</p>
        </header>

        {state === 'loading' && (
          <div className="s4-list-state" aria-live="polite">
            <span className="s4-spinner" /><h2>Loading your orders</h2>
          </div>
        )}
        {state === 'error' && (
          <div className="s4-list-state" role="alert">
            <span>!</span><h2>We could not load your orders.</h2>
            <p>Check your connection and try again.</p><button onClick={retry}>Try again</button>
          </div>
        )}
        {state === 'ready' && orders.length === 0 && (
          <div className="s4-list-state">
            <span>0</span><h2>No orders yet</h2>
            <p>Your confirmed purchases will appear here.</p>
            <a className="primary-button" href="/products">Explore products →</a>
          </div>
        )}
        {state === 'ready' && orders.length > 0 && (
          <section className="s4-orders" aria-label="Order history">
            {orders.map((order) => (
              <article className="s4-order-card" key={order.id}>
                <div className="s4-order-top">
                  <div><p>Order</p><h2>#{order.id}</h2></div>
                  <div className="s4-order-badges">
                    <span className={`s4-payment-status ${order.payment.status}`}>
                      {order.payment.status_label}
                    </span>
                    <span className={`s4-status ${order.status}`}>{order.status_label}</span>
                  </div>
                </div>
                <dl>
                  <div><dt>Placed</dt><dd>{new Intl.DateTimeFormat('en-BD', { dateStyle: 'medium' }).format(new Date(order.created_at))}</dd></div>
                  <div><dt>Items</dt><dd>{order.items.reduce((sum, item) => sum + item.quantity, 0)}</dd></div>
                  <div><dt>Total</dt><dd>{formatPrice(Number(order.total))}</dd></div>
                </dl>
                <div className="s4-order-preview">
                  {order.items.slice(0, 3).map((item) => (
                    <span key={`${item.product_slug}-${item.size}-${item.color}`}>{item.product_name} × {item.quantity}</span>
                  ))}
                </div>
                <a className="s4-detail-link" href={`/orders/${order.id}`}>View order and tracking →</a>
              </article>
            ))}
          </section>
        )}
      </main>
    </div>
  )
}
