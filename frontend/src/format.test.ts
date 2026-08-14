import { describe, expect, it } from 'vitest'
import { formatPrice } from './format'

describe('formatPrice', () => {
  it('formats numeric and string prices using Bangladeshi grouping', () => {
    expect(formatPrice(1250)).toContain('1,250')
    expect(formatPrice('2000.00')).toContain('2,000')
  })
})
