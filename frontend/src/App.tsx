import { useEffect, useState } from 'react'
import AuthProvider from './components/AuthProvider'
import CartProvider from './components/CartProvider'
import ProtectedRoute from './components/ProtectedRoute'
import AccountPage from './pages/AccountPage'
import AuthPage from './pages/AuthPage'
import CartPage from './pages/CartPage'
import HomePage from './pages/HomePage'
import OrderDetailPage from './pages/OrderDetailPage'
import OrdersPage from './pages/OrdersPage'
import PasswordRecoveryPage from './pages/PasswordRecoveryPage'
import ProductDetailsPage from './pages/ProductDetailsPage'
import ProductListingPage from './pages/ProductListingPage'
import { trackPageView } from './analytics'

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
  return <AuthProvider><CartProvider><AppContent /></CartProvider></AuthProvider>
}
