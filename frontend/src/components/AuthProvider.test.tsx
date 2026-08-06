import { render, screen, waitFor } from '@testing-library/react'
import AuthProvider from './AuthProvider'
import { useAuth } from '../useAuth'
import { user } from '../test/fixtures'

function AuthHarness() {
  const auth = useAuth()
  return <span>{auth.restoring ? 'restoring' : auth.user?.username || 'guest'}</span>
}

describe('AuthProvider', () => {
  it('restores a valid stored session', async () => {
    localStorage.setItem('nazriy-token', 'valid-token')
    localStorage.setItem('nazriy-user', JSON.stringify(user))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify(user), { status: 200 })))
    render(<AuthProvider><AuthHarness /></AuthProvider>)
    expect(screen.getByText('restoring')).toBeInTheDocument()
    await screen.findByText('buyer')
  })

  it('clears an expired session', async () => {
    localStorage.setItem('nazriy-token', 'expired-token')
    localStorage.setItem('nazriy-user', JSON.stringify(user))
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response('{}', { status: 403 })))
    render(<AuthProvider><AuthHarness /></AuthProvider>)
    await screen.findByText('guest')
    await waitFor(() => expect(localStorage.getItem('nazriy-token')).toBeNull())
  })
})
