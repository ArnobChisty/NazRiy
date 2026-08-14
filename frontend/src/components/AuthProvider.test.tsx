import { useState } from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import AuthProvider from './AuthProvider'
import { useAuth } from '../useAuth'
import { user } from '../test/fixtures'

function AuthHarness() {
  const auth = useAuth()
  return <span>{auth.restoring ? 'restoring' : auth.user?.username || 'guest'}</span>
}

function AuthActionHarness() {
  const auth = useAuth()
  const [result, setResult] = useState('idle')
  return <div>
    <span>{auth.user?.username || 'guest'}</span>
    <button onClick={() => auth.login('new-token', user)}>Login action</button>
    <button onClick={() => void auth.authFetch('/secure/', { headers: { 'X-Test': 'yes' } }).then(response => setResult(String(response.status)))}>Fetch action</button>
    <button onClick={() => void auth.refreshUser().then(next => setResult(next?.username || 'none'))}>Refresh action</button>
    <output>{result}</output>
  </div>
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

  it('ignores malformed stored user JSON', () => {
    localStorage.setItem('nazriy-user', '{broken')
    render(<AuthProvider><AuthHarness /></AuthProvider>)
    expect(screen.getByText('guest')).toBeInTheDocument()
  })

  it('stores a login and sends authenticated requests with merged headers', async () => {
    const fetchMock = vi.fn().mockImplementation(() => Promise.resolve(
      new Response(JSON.stringify(user), { status: 200 }),
    ))
    vi.stubGlobal('fetch', fetchMock)
    const tester = userEvent.setup()
    render(<AuthProvider><AuthActionHarness /></AuthProvider>)

    await tester.click(screen.getByRole('button', { name: 'Login action' }))
    expect(screen.getByText('buyer')).toBeInTheDocument()
    expect(localStorage.getItem('nazriy-token')).toBe('new-token')
    await tester.click(screen.getByRole('button', { name: 'Fetch action' }))
    expect(await screen.findByText('200')).toBeInTheDocument()

    const request = fetchMock.mock.calls.at(-1)
    const headers = request?.[1]?.headers as Headers
    expect(headers.get('Authorization')).toBe('Token new-token')
    expect(headers.get('X-Test')).toBe('yes')
  })

  it('clears the session when an authenticated request is forbidden', async () => {
    localStorage.setItem('nazriy-token', 'valid-token')
    localStorage.setItem('nazriy-user', JSON.stringify(user))
    vi.stubGlobal('fetch', vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify(user), { status: 200 }))
      .mockResolvedValueOnce(new Response('{}', { status: 403 })))
    const tester = userEvent.setup()
    render(<AuthProvider><AuthActionHarness /></AuthProvider>)
    await screen.findByText('buyer')
    await tester.click(screen.getByRole('button', { name: 'Fetch action' }))
    expect(await screen.findByText('403')).toBeInTheDocument()
    expect(localStorage.getItem('nazriy-token')).toBeNull()
    expect(screen.getByText('guest')).toBeInTheDocument()
  })

  it('refreshes a stored user and returns none without a token', async () => {
    const tester = userEvent.setup()
    const view = render(<AuthProvider><AuthActionHarness /></AuthProvider>)
    await tester.click(screen.getByRole('button', { name: 'Refresh action' }))
    expect(await screen.findByText('none')).toBeInTheDocument()

    view.unmount()
    localStorage.setItem('nazriy-token', 'valid-token')
    localStorage.setItem('nazriy-user', JSON.stringify(user))
    const updated = { ...user, username: 'updated-buyer' }
    vi.stubGlobal('fetch', vi.fn().mockImplementation(() => Promise.resolve(
      new Response(JSON.stringify(updated), { status: 200 }),
    )))
    render(<AuthProvider><AuthActionHarness /></AuthProvider>)
    await screen.findByText('updated-buyer')
    await tester.click(screen.getByRole('button', { name: 'Refresh action' }))
    expect(await screen.findByText('updated-buyer', { selector: 'output' })).toBeInTheDocument()
  })

  it('clears a stored session after a restoration network failure', async () => {
    localStorage.setItem('nazriy-token', 'network-token')
    localStorage.setItem('nazriy-user', JSON.stringify(user))
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('offline')))
    render(<AuthProvider><AuthHarness /></AuthProvider>)
    await screen.findByText('guest')
    expect(localStorage.getItem('nazriy-token')).toBeNull()
  })
})
