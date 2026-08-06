import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AuthPage from './AuthPage'

const login = vi.fn()
vi.mock('../useAuth', () => ({ useAuth: () => ({ login }) }))

describe('AuthPage', () => {
  it('validates registration fields accessibly before submission', async () => {
    const tester = userEvent.setup()
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)
    render(<AuthPage mode="register" />)
    await tester.type(screen.getByLabelText(/Username/), 'buyer')
    await tester.type(screen.getByLabelText(/^Email/), 'bad-email')
    await tester.type(screen.getByLabelText(/^Password/), 'short')
    await tester.type(screen.getByLabelText(/Confirm password/), 'different')
    await tester.click(screen.getByRole('button', { name: 'Register' }))
    expect(screen.getByRole('alert')).toHaveTextContent(/valid email/)
    expect(fetchMock).not.toHaveBeenCalled()
  })

  it('shows backend login errors without exposing credentials', async () => {
    const tester = userEvent.setup()
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({ detail: 'Invalid username or password.' }), { status: 400 })))
    render(<AuthPage mode="login" />)
    await tester.type(screen.getByLabelText(/Username/), 'buyer')
    await tester.type(screen.getByLabelText(/Password/), 'wrong-password')
    await tester.click(screen.getByRole('button', { name: 'Log in' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid username or password.')
    expect(login).not.toHaveBeenCalled()
  })
})
