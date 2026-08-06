import { useCallback, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { getProduct } from '../api'
import { CartContext } from '../cart-context'
import { cartItemKey, clampQuantity } from '../cart'
import type { CartItem } from '../cart'
import type { Product } from '../types'

const STORAGE_KEY = 'nazriy-cart-v1'

const loadStoredCart = (): CartItem[] => {
  try {
    const parsed: unknown = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]')
    if (!Array.isArray(parsed)) return []
    return parsed.filter((item): item is CartItem => Boolean(
      item && typeof item === 'object' && 'key' in item && 'product' in item && 'quantity' in item,
    ))
  } catch {
    return []
  }
}

const CartProvider = ({ children }: { children: ReactNode }) => {
  const [items, setItems] = useState<CartItem[]>(loadStoredCart)

  useEffect(() => {
    let cancelled = false
    const storedItems = loadStoredCart()
    if (!storedItems.length) return () => { cancelled = true }

    const refreshProducts = async () => {
      const refreshed = await Promise.all(storedItems.map(async (item) => {
        try {
          const product = await getProduct(item.product.slug)
          return {
            ...item,
            product,
            quantity: clampQuantity(item.quantity, product.stock_quantity),
          }
        } catch {
          return item
        }
      }))
      if (cancelled) return
      const byKey = new Map(refreshed.map((item) => [item.key, item]))
      setItems((current) => current.map((item) => byKey.get(item.key) || item))
    }

    void refreshProducts()
    return () => { cancelled = true }
  }, [])

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(items))
  }, [items])

  const addItem = useCallback((product: Product, size: string, color: string, quantity: number) => {
    const key = cartItemKey(product.id, size, color)
    setItems((current) => {
      const existing = current.find((item) => item.key === key)
      if (existing) {
        return current.map((item) => item.key === key
          ? { ...item, product, quantity: clampQuantity(item.quantity + quantity, product.stock_quantity) }
          : item)
      }
      return [...current, { key, product, size, color, quantity: clampQuantity(quantity, product.stock_quantity) }]
    })
  }, [])

  const updateQuantity = useCallback((key: string, quantity: number) => {
    setItems((current) => current.map((item) => item.key === key
      ? { ...item, quantity: clampQuantity(quantity, item.product.stock_quantity) }
      : item))
  }, [])

  const removeItem = useCallback((key: string) => {
    setItems((current) => current.filter((item) => item.key !== key))
  }, [])

  const clearCart = useCallback(() => setItems([]), [])
  const itemCount = useMemo(() => items.reduce((total, item) => total + item.quantity, 0), [items])
  const subtotal = useMemo(() => items.reduce((total, item) => total + Number(item.product.price) * item.quantity, 0), [items])
  const value = useMemo(() => ({ items, itemCount, subtotal, addItem, updateQuantity, removeItem, clearCart }), [items, itemCount, subtotal, addItem, updateQuantity, removeItem, clearCart])

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>
}

export default CartProvider
