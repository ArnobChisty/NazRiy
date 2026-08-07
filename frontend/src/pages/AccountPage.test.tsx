import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AccountPage from './AccountPage'
import { user } from '../test/fixtures'

const authFetch = vi.fn()
vi.mock('../components/Navbar', () => ({ default: () => <nav>Navbar</nav> }))
vi.mock('../useAuth', () => ({
  useAuth: () => ({ user, token: 'token', login: vi.fn(), authFetch }),
}))

describe('AccountPage', () => {
  it('validates password changes before calling the API', async () => {
    const tester = userEvent.setup()
    render(<AccountPage />)
    await tester.type(screen.getByLabelText(/Current password/), 'current')
    await tester.type(screen.getByLabelText(/^New password/), 'new-pass-1')
    await tester.type(screen.getByLabelText(/Confirm new password/), 'different')
    await tester.click(screen.getByRole('button', { name: 'Update password' }))
    expect(screen.getByRole('alert')).toHaveTextContent(/matching new passwords/)
    expect(authFetch).not.toHaveBeenCalled()
  })
})
