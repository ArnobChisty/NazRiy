import { useState, type FormEvent } from 'react'
import { useAuth } from '../useAuth'
import './AuthPage.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const errorMessage = (data: Record<string, unknown>) => {
  if (typeof data.detail === 'string') return data.detail
  return Object.values(data).flat().filter(value => typeof value === 'string').join(' ') || 'Unable to continue.'
}

export default function AuthPage({ mode }: { mode: 'login' | 'register' }) {
  const { login } = useAuth()
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const requested = new URLSearchParams(window.location.search).get('next')
  const destination = requested?.startsWith('/') && !requested.startsWith('//') ? requested : '/account'

  const submit = async (event: FormEvent) => {
    event.preventDefault(); setError(''); setSuccess('')
    if (!form.username.trim() || !form.password) { setError('Enter your username and password.'); return }
    if (mode === 'register' && (!/^\S+@\S+\.\S+$/.test(form.email) || form.password.length < 8 || form.password !== form.confirm)) {
      setError('Use a valid email, an 8+ character password, and matching passwords.'); return
    }
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/auth/${mode}/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) { setError(errorMessage(data)); return }
      login(data.token, data.user)
      setSuccess(mode === 'login' ? 'Login successful.' : 'Account created successfully.')
      window.setTimeout(() => { window.location.href = destination }, 450)
    } catch { setError('The authentication server is unavailable. Start the Django backend and try again.') }
    finally { setLoading(false) }
  }

  return <main id="main-content" className="auth-page noir-auth-page"><a className="auth-brand" href="/">NAZRIY</a><div className="auth-visual" aria-hidden="true"><img src="/banners/nazriy-look-1.jpeg" alt=""/><span>NAZRIY · APPAREL</span></div><form className="auth-card" onSubmit={submit} noValidate>
    <p className="auth-eyebrow">Private account</p><h1>{mode === 'login' ? 'Login' : 'Register'}</h1>
    <label>Username *<input autoComplete="username" required value={form.username} onChange={event => setForm({...form, username: event.target.value})}/></label>
    {mode === 'register' && <label>Email *<input type="email" autoComplete="email" required value={form.email} onChange={event => setForm({...form, email: event.target.value})}/></label>}
    <label>Password *<input type="password" autoComplete={mode === 'login' ? 'current-password' : 'new-password'} required value={form.password} onChange={event => setForm({...form, password: event.target.value})}/></label>
    {mode === 'login' && <a className="auth-forgot-link" href="/forgot-password">Forgot your password?</a>}
    {mode === 'register' && <label>Confirm password *<input type="password" autoComplete="new-password" required value={form.confirm} onChange={event => setForm({...form, confirm: event.target.value})}/></label>}
    {error && <p className="auth-error" role="alert">{error}</p>}{success && <p className="auth-success" role="status">{success}</p>}
    <button className="auth-submit" disabled={loading}>{loading ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Register'}</button>
    <a className="auth-switch" href={mode === 'login' ? '/register' : '/login'}>{mode === 'login' ? 'Need an account? Register' : 'Already registered? Log in'}</a>
  </form></main>
}
