import { render, screen } from '@testing-library/react'
import ProtectedRoute from './ProtectedRoute'
import { user } from '../test/fixtures'

const authState = vi.hoisted(() => ({ user: null as typeof user | null, restoring: false }))
vi.mock('../useAuth', () => ({ useAuth: () => authState }))

describe('ProtectedRoute', () => {
  it('announces session restoration', () => {
    authState.restoring = true
    render(<ProtectedRoute><p>Private</p></ProtectedRoute>)
    expect(screen.getByText(/Restoring your account/)).toBeInTheDocument()
  })

  it('renders protected content for an authenticated customer', () => {
    authState.restoring = false
    authState.user = user
    render(<ProtectedRoute><p>Private</p></ProtectedRoute>)
    expect(screen.getByText('Private')).toBeInTheDocument()
  })
})
