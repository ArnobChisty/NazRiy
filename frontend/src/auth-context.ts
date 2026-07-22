import { createContext } from 'react'
import type { AccountUser } from './types'

export interface AuthContextValue {
  user: AccountUser | null
  restoring: boolean
  token: string | null
  login: (token: string, user: AccountUser) => void
  logout: () => void
  refreshUser: () => Promise<AccountUser | null>
  authFetch: (path: string, init?: RequestInit) => Promise<Response>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
