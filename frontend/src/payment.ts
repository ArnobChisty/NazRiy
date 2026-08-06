import type { PaymentInfo } from './types'

export type PaymentAction = 'submit' | 'cancel'

export const createRequestId = () => {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return `00000000-0000-4000-8000-${Math.random().toString(16).slice(2).padEnd(12, '0').slice(0, 12)}`
}

export const paymentFeedback = (payment: PaymentInfo) => {
  if (payment.status === 'paid') {
    return `bKash payment verified. Transaction ID ${payment.provider_reference}.`
  }
  if (payment.status === 'failed') {
    return payment.failure_reason || 'The submitted bKash transaction could not be verified.'
  }
  if (payment.status === 'cancelled') return 'The payment and order were cancelled.'
  if (payment.method === 'cash_on_delivery') {
    return 'Payment will be collected when the order is delivered.'
  }
  if (payment.provider_reference) {
    return `bKash transaction ${payment.provider_reference} was submitted and is awaiting verification.`
  }
  return 'Submit your bKash transaction ID to continue.'
}

export const parsePayment = async (response: Response): Promise<PaymentInfo> => {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    const payment = data as Partial<PaymentInfo>
    if (payment.status === 'failed') return payment as PaymentInfo
    throw new Error(typeof data.detail === 'string' ? data.detail : 'Unable to submit the bKash payment.')
  }
  return data as PaymentInfo
}
