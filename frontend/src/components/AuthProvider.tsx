import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { AuthContext } from '../auth-context'
import type { AccountUser } from '../types'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'
const TOKEN_KEY = 'nazriy-token'
const USER_KEY = 'nazriy-user'

const readStoredUser = (): AccountUser | null => {
  try { return JSON.parse(localStorage.getItem(USER_KEY) || 'null') as AccountUser | null }
  catch { return null }
}

export default function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<AccountUser | null>(readStoredUser)
  const [restoring, setRestoring] = useState(Boolean(token))

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY); localStorage.removeItem(USER_KEY)
    setToken(null); setUser(null)
  }, [])

  const login = useCallback((nextToken: string, nextUser: AccountUser) => {
    localStorage.setItem(TOKEN_KEY, nextToken); localStorage.setItem(USER_KEY, JSON.stringify(nextUser))
    setToken(nextToken); setUser(nextUser)
  }, [])

  const authFetch = useCallback(async (path: string, init: RequestInit = {}) => {
    const activeToken = localStorage.getItem(TOKEN_KEY)
    const headers = new Headers(init.headers)
    if (activeToken) headers.set('Authorization', `Token ${activeToken}`)
    const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
    if (response.status === 401 || response.status === 403) clearSession()
    return response
  }, [clearSession])

  const refreshUser = useCallback(async () => {
    const activeToken = localStorage.getItem(TOKEN_KEY)
    if (!activeToken) { clearSession(); return null }
    try {
      const response = await authFetch('/auth/me/')
      if (!response.ok) return null
      const nextUser = await response.json() as AccountUser
      localStorage.setItem(USER_KEY, JSON.stringify(nextUser)); setUser(nextUser)
      return nextUser
    } catch { return null }
  }, [authFetch, clearSession])

  useEffect(() => {
    if (!token) return
    let active = true
    fetch(`${API_BASE}/auth/me/`, { headers: { Authorization: `Token ${token}` } })
      .then(async response => {
        if (!active) return
        if (!response.ok) { clearSession(); return }
        const nextUser = await response.json() as AccountUser
        if (!active) return
        localStorage.setItem(USER_KEY, JSON.stringify(nextUser)); setUser(nextUser)
      })
      .catch(() => { if (active) clearSession() })
      .finally(() => { if (active) setRestoring(false) })
    return () => { active = false }
  }, [clearSession, token])

  const logout = useCallback(() => {
    if (token) fetch(`${API_BASE}/auth/logout/`, { method: 'POST', headers: { Authorization: `Token ${token}` } }).catch(() => undefined)
    clearSession()
    window.location.href = '/'
  }, [clearSession, token])

  const value = useMemo(() => ({ user, restoring, token, login, logout, refreshUser, authFetch }), [user, restoring, token, login, logout, refreshUser, authFetch])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
