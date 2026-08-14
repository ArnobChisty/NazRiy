import { describe, expect, it, vi } from 'vitest'
import { createRequestId, parsePayment, paymentFeedback } from './payment'
import { order } from './test/fixtures'

describe('bKash payment helpers', () => {
  it('creates an idempotency-compatible request id', () => {
    vi.spyOn(crypto, 'randomUUID').mockReturnValue('11111111-1111-4111-8111-111111111111')
    expect(createRequestId()).toBe('11111111-1111-4111-8111-111111111111')
  })

  it('creates a fallback request id when randomUUID is unavailable', () => {
    vi.stubGlobal('crypto', undefined)
    vi.spyOn(Math, 'random').mockReturnValue(0.5)
    expect(createRequestId()).toMatch(/^00000000-0000-4000-8000-[a-f0-9]{12}$/)
    vi.unstubAllGlobals()
  })

  it('describes verified, failed, pending, and cash-on-delivery states', () => {
    expect(paymentFeedback({ ...order.payment, status: 'paid', provider_reference: 'BK7A1B2C3D' })).toContain('BK7A1B2C3D')
    expect(paymentFeedback({ ...order.payment, status: 'failed', failure_reason: 'Not verified' })).toBe('Not verified')
    expect(paymentFeedback({ ...order.payment, status: 'failed', failure_reason: '' })).toContain('could not be verified')
    expect(paymentFeedback({ ...order.payment, status: 'cancelled' })).toContain('cancelled')
    expect(paymentFeedback({ ...order.payment, method: 'cash_on_delivery' })).toContain('delivered')
    expect(paymentFeedback({ ...order.payment, provider_reference: 'BK7A1B2C3D' })).toContain('awaiting verification')
    expect(paymentFeedback(order.payment)).toContain('transaction ID')
  })

  it('returns structured failed payment responses', async () => {
    const response = new Response(JSON.stringify({ ...order.payment, status: 'failed' }), { status: 402 })
    await expect(parsePayment(response)).resolves.toMatchObject({ status: 'failed' })
  })

  it('throws useful API errors', async () => {
    const response = new Response(JSON.stringify({ detail: 'Transaction ID already used.' }), { status: 409 })
    await expect(parsePayment(response)).rejects.toThrow('Transaction ID already used.')
  })

  it('uses a safe fallback error for invalid response bodies', async () => {
    const response = new Response('not-json', { status: 500 })
    await expect(parsePayment(response)).rejects.toThrow('Unable to submit the bKash payment.')
  })

  it('parses successful payment responses', async () => {
    const response = new Response(JSON.stringify(order.payment), { status: 200 })
    await expect(parsePayment(response)).resolves.toEqual(order.payment)
  })
})
