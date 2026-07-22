import { createContext } from 'react'
import type { CartContextValue } from './cart'

export const CartContext = createContext<CartContextValue | null>(null)
