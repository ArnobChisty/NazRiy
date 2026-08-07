import { describe, expect, it } from 'vitest'
import { cartItemKey, clampQuantity } from './cart'

describe('cart business rules', () => {
  it('creates a stable key for a product option', () => {
    expect(cartItemKey(4, 'M', 'Red')).toBe('4:M:Red')
    expect(cartItemKey(4, '', '')).toBe('4:default:default')
  })

  it('clamps quantity between one and available stock', () => {
    expect(clampQuantity(0, 5)).toBe(1)
    expect(clampQuantity(3.9, 5)).toBe(3)
    expect(clampQuantity(9, 5)).toBe(5)
    expect(clampQuantity(2, 0)).toBe(1)
  })
})
