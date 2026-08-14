import { lazy, Suspense, useEffect, useState } from 'react'
import { Analytics } from '@vercel/analytics/react'
import AuthProvider from './components/AuthProvider'
import CartProvider from './components/CartProvider'
import ProtectedRoute from './components/ProtectedRoute'
import WebsiteThemeProvider from './components/WebsiteThemeProvider'
import SitePromotions from './components/SitePromotions'
import HomePage from './pages/HomePage'
import { trackPageView } from './analytics'

const AccountPage = lazy(() => import('./pages/AccountPage'))
const AuthPage = lazy(() => import('./pages/AuthPage'))
const CartPage = lazy(() => import('./pages/CartPage'))
const OrderDetailPage = lazy(() => import('./pages/OrderDetailPage'))
const OrdersPage = lazy(() => import('./pages/OrdersPage'))
const PasswordRecoveryPage = lazy(() => import('./pages/PasswordRecoveryPage'))
const ProductDetailsPage = lazy(() => import('./pages/ProductDetailsPage'))
const ProductListingPage = lazy(() => import('./pages/ProductListingPage'))

function AppContent() {
  const [path, setPath] = useState(window.location.pathname.replace(/\/$/, '') || '/')
  useEffect(() => {
    const updatePath = () => setPath(window.location.pathname.replace(/\/$/, '') || '/')
    window.addEventListener('popstate', updatePath)
    return () => window.removeEventListener('popstate', updatePath)
  }, [])
  useEffect(() => { trackPageView(window.location.pathname) }, [path])
  if (path === '/login') return <AuthPage mode="login" />
  if (path === '/register') return <AuthPage mode="register" />
  if (path === '/forgot-password') return <PasswordRecoveryPage mode="request" />
  if (path === '/reset-password') return <PasswordRecoveryPage mode="confirm" />
  if (path === '/account') return <ProtectedRoute><AccountPage /></ProtectedRoute>
  if (path === '/orders') return <ProtectedRoute><OrdersPage /></ProtectedRoute>
  if (path.startsWith('/orders/')) return <ProtectedRoute><OrderDetailPage orderId={decodeURIComponent(path.split('/')[2] || '')}/></ProtectedRoute>
  if (path === '/products') return <ProductListingPage />
  if (path.startsWith('/products/')) return <ProductDetailsPage slug={decodeURIComponent(path.split('/')[2] || '')} />
  if (path === '/checkout') return <ProtectedRoute><CartPage /></ProtectedRoute>
  if (path === '/cart') return <CartPage />
  return <HomePage />
}

export default function App() {
  return (
    <WebsiteThemeProvider>
      <AuthProvider>
        <CartProvider>
          <SitePromotions />
          <Suspense fallback={<main className="route-loading" aria-label="Loading page" aria-busy="true" />}><AppContent /></Suspense>
          <Analytics />
        </CartProvider>
      </AuthProvider>
    </WebsiteThemeProvider>
  )
}
