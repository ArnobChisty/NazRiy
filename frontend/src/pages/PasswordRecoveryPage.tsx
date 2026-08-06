import { useEffect, useState, type FormEvent } from 'react'
import './AuthPage.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

const apiError = (data: Record<string, unknown>) => {
  if (typeof data.detail === 'string') return data.detail
  const messages = Object.values(data).flatMap(value => Array.isArray(value) ? value : [value])
  return messages.filter(value => typeof value === 'string').join(' ') || 'Unable to continue. Please try again.'
}

type RecoveryMode = 'request' | 'confirm'
type LinkState = 'checking' | 'valid' | 'invalid'

export default function PasswordRecoveryPage({ mode }: { mode: RecoveryMode }) {
  const query = new URLSearchParams(window.location.search)
  const uid = query.get('uid') || ''
  const token = query.get('token') || ''
  const [email, setEmail] = useState('')
  const [passwords, setPasswords] = useState({ newPassword: '', confirmPassword: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [linkState, setLinkState] = useState<LinkState>(
    mode === 'confirm' ? (uid && token ? 'checking' : 'invalid') : 'valid',
  )

  useEffect(() => {
    if (mode !== 'confirm' || !uid || !token) return
    const validateLink = async () => {
      try {
        const params = new URLSearchParams({ uid, token })
        const response = await fetch(`${API_BASE}/auth/password/reset/confirm/?${params}`)
        setLinkState(response.ok ? 'valid' : 'invalid')
      } catch {
        setError('The authentication server is unavailable. Please try again shortly.')
        setLinkState('invalid')
      }
    }
    void validateLink()
  }, [mode, token, uid])

  const requestReset = async (event: FormEvent) => {
    event.preventDefault(); setError(''); setSuccess('')
    if (!/^\S+@\S+\.\S+$/.test(email.trim())) { setError('Enter a valid email address.'); return }
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/auth/password/reset/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ email: email.trim() }),
      })
      const data = await response.json().catch(() => ({})) as Record<string, unknown>
      if (!response.ok) { setError(apiError(data)); return }
      setSuccess(typeof data.detail === 'string' ? data.detail : 'If an account uses that email address, reset instructions have been sent.')
      setEmail('')
    } catch { setError('The authentication server is unavailable. Please try again shortly.') }
    finally { setLoading(false) }
  }

  const confirmReset = async (event: FormEvent) => {
    event.preventDefault(); setError(''); setSuccess('')
    if (passwords.newPassword.length < 8) { setError('Use a password with at least 8 characters.'); return }
    if (passwords.newPassword !== passwords.confirmPassword) { setError('The new passwords do not match.'); return }
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE}/auth/password/reset/confirm/`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ uid, token, new_password: passwords.newPassword, confirm_password: passwords.confirmPassword }),
      })
      const data = await response.json().catch(() => ({})) as Record<string, unknown>
      if (!response.ok) { setError(apiError(data)); return }
      setSuccess(typeof data.detail === 'string' ? data.detail : 'Your password has been reset successfully.')
      setPasswords({ newPassword: '', confirmPassword: '' })
    } catch { setError('The authentication server is unavailable. Please try again shortly.') }
    finally { setLoading(false) }
  }

  const isRequest = mode === 'request'
  return <main id="main-content" className="auth-page noir-auth-page">
    <a className="auth-brand" href="/">NAZRIY</a>
    <div className="auth-visual" aria-hidden="true"><img src="/banners/nazriy-look-1.jpeg" alt=""/><span>NAZRIY · PRIVATE ACCESS</span></div>
    <form className="auth-card recovery-card" onSubmit={isRequest ? requestReset : confirmReset} noValidate>
      <p className="auth-eyebrow">Account recovery</p>
      <h1>{isRequest ? 'Forgot password' : 'New password'}</h1>
      <p className="auth-recovery-copy">{isRequest
        ? 'Enter the email connected to your account. We will send a secure, one-time recovery link if the account exists.'
        : 'Choose a strong new password for your NazRiy account. Your recovery link can only be used once.'}</p>

      {isRequest ? <label>Email address *<input type="email" autoComplete="email" required value={email} onChange={event => setEmail(event.target.value)}/></label> : <>
        {linkState === 'checking' && <p className="auth-recovery-status" role="status">Checking your secure recovery link…</p>}
        {linkState === 'invalid' && <p className="auth-recovery-status auth-recovery-invalid" role="alert">This recovery link is invalid or has expired. Request a new link to continue.</p>}
        {linkState === 'valid' && !success && <>
          <label>New password *<input type="password" autoComplete="new-password" required value={passwords.newPassword} onChange={event => setPasswords({...passwords, newPassword: event.target.value})}/></label>
          <label>Confirm new password *<input type="password" autoComplete="new-password" required value={passwords.confirmPassword} onChange={event => setPasswords({...passwords, confirmPassword: event.target.value})}/></label>
          <div className="auth-password-help" aria-label="Password requirements"><span>At least 8 characters</span><span>Avoid common or entirely numeric passwords</span><span>Do not reuse personal information</span></div>
        </>}
      </>}

      {error && <p className="auth-error" role="alert">{error}</p>}
      {success && <p className="auth-recovery-status" role="status">{success}</p>}
      <div className="auth-recovery-actions">
        {isRequest && !success && <button className="auth-submit" disabled={loading}>{loading ? 'Sending secure link…' : 'Send reset link'}</button>}
        {!isRequest && linkState === 'valid' && !success && <button className="auth-submit" disabled={loading}>{loading ? 'Updating password…' : 'Reset password'}</button>}
        {(!isRequest && (linkState === 'invalid' || success)) && <a className="auth-submit auth-secondary-action" href={success ? '/login' : '/forgot-password'}>{success ? 'Continue to login' : 'Request a new link'}</a>}
        <a className="auth-secondary-action" href="/login">Back to login</a>
      </div>
    </form>
  </main>
}
