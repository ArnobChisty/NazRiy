import type { Product } from './types'

export interface CartItem {
  key: string
  product: Product
  size: string
  color: string
  quantity: number
}

export interface CartContextValue {
  items: CartItem[]
  itemCount: number
  subtotal: number
  addItem: (product: Product, size: string, color: string, quantity: number) => void
  updateQuantity: (key: string, quantity: number) => void
  removeItem: (key: string) => void
  clearCart: () => void
}

export const cartItemKey = (productId: number, size: string, color: string) =>
  `${productId}:${size || 'default'}:${color || 'default'}`

export const clampQuantity = (quantity: number, stock: number) =>
  Math.max(1, Math.min(Math.floor(quantity), Math.max(1, stock)))
