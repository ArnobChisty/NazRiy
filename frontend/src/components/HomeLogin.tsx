import { useState, type FormEvent } from 'react'
import { useAuth } from '../useAuth'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const getError = (data: Record<string, unknown>) => {
  if (typeof data.detail === 'string') return data.detail
  return 'Check your username and password, then try again.'
}

export default function HomeLogin() {
  const { user, login } = useAuth()
  const [form, setForm] = useState({ username: '', password: '' })
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setMessage('')
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/auth/login/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) {
        setMessage(getError(data))
        return
      }
      login(data.token, data.user)
      setMessage('Welcome back to NazRiy.')
    } catch {
      setMessage('The login service is temporarily unavailable.')
    } finally {
      setLoading(false)
    }
  }

  return <section className="home-login">
    <div className="home-login-image"><img src="/banners/nazriy-look-1.jpeg" alt="NazRiy apparel campaign"/><span>PRIVATE ACCESS · NAZRIY</span></div>
    <div className="home-login-panel">
      <p className="eyebrow">Private account</p>
      <h2>{user ? 'Welcome' : 'Login'}</h2>
      {user
        ? <div className="home-login-welcome"><p>You are signed in as <strong>{user.full_name || user.username}</strong>.</p><a href="/account">Open your account <span>→</span></a></div>
        : <form onSubmit={submit}>
            <label>Username<input autoComplete="username" value={form.username} onChange={event => setForm({ ...form, username: event.target.value })} required/></label>
            <label>Password<input type="password" autoComplete="current-password" value={form.password} onChange={event => setForm({ ...form, password: event.target.value })} required/></label>
            {message && <p className="home-login-message" role="status">{message}</p>}
            <div className="home-login-options">
              <span>Secure customer access</span>
              <div className="home-login-account-links">
                <a className="home-login-forgot" href="/forgot-password">Forgot password?</a>
                <a href="/register">Create account</a>
              </div>
            </div>
            <button type="submit" disabled={loading}>{loading ? 'Please wait…' : 'Log in'} <span>→</span></button>
          </form>}
    </div>
  </section>
}
