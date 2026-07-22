import { useEffect, type ReactNode } from 'react'
import { useAuth } from '../useAuth'

export default function ProtectedRoute({ children }: { children: ReactNode }) {
  const { user, restoring } = useAuth()
  useEffect(() => {
    if (!restoring && !user) {
      const destination = `${window.location.pathname}${window.location.search}`
      window.location.replace(`/login?next=${encodeURIComponent(destination)}`)
    }
  }, [restoring, user])
  if (restoring) return <main id="main-content" className="s4-route-state" aria-live="polite"><span className="s4-spinner" aria-hidden="true"/><p>Restoring your account…</p></main>
  if (!user) return <main id="main-content" className="s4-route-state" aria-live="polite"><p>Redirecting to login…</p></main>
  return children
}
