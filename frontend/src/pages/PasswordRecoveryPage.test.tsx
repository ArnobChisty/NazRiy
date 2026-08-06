import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import PasswordRecoveryPage from './PasswordRecoveryPage'

describe('PasswordRecoveryPage', () => {
  it('requests a reset without revealing whether the account exists', async () => {
    const tester = userEvent.setup()
    const detail = 'If an active account uses that email address, password reset instructions have been sent.'
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)

    render(<PasswordRecoveryPage mode="request" />)
    await tester.type(screen.getByLabelText(/Email address/), 'buyer@example.com')
    await tester.click(screen.getByRole('button', { name: 'Send reset link' }))

    expect(await screen.findByRole('status')).toHaveTextContent(detail)
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/auth/password/reset/'), expect.objectContaining({ method: 'POST' }))
  })

  it('validates the link and resets the password', async () => {
    window.history.pushState({}, '', '/reset-password?uid=encoded-user&token=secure-token')
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ valid: true }), { status: 200 }))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'Your password has been reset successfully. You can now log in.' }), { status: 200 }))
    vi.stubGlobal('fetch', fetchMock)
    const tester = userEvent.setup()

    render(<PasswordRecoveryPage mode="confirm" />)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Reset password' })).toBeInTheDocument())
    await tester.type(screen.getByLabelText(/^New password/), 'ReplacementStrong!42')
    await tester.type(screen.getByLabelText(/Confirm new password/), 'ReplacementStrong!42')
    await tester.click(screen.getByRole('button', { name: 'Reset password' }))

    expect(await screen.findByRole('status')).toHaveTextContent('reset successfully')
    expect(fetchMock).toHaveBeenLastCalledWith(expect.stringContaining('/auth/password/reset/confirm/'), expect.objectContaining({ method: 'POST' }))
  })

  it('shows an expired-link recovery action', async () => {
    window.history.pushState({}, '', '/reset-password?uid=bad&token=expired')
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ valid: false }), { status: 400 })))

    render(<PasswordRecoveryPage mode="confirm" />)
    expect(await screen.findByRole('alert')).toHaveTextContent('invalid or has expired')
    expect(screen.getByRole('link', { name: 'Request a new link' })).toHaveAttribute('href', '/forgot-password')
  })
})
