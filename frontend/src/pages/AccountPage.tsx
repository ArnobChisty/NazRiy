import { useState, type FormEvent } from 'react'
import Navbar from '../components/Navbar'
import { useAuth } from '../useAuth'
import './Sprint4.css'

const readError = (data: Record<string, unknown>) => typeof data.detail === 'string' ? data.detail : Object.values(data).flat().filter(value => typeof value === 'string').join(' ') || 'Unable to save your changes.'

export default function AccountPage() {
  const { user, token, login, authFetch } = useAuth()
  const [profile, setProfile] = useState({ first_name: user?.first_name || '', last_name: user?.last_name || '', email: user?.email || '' })
  const [passwords, setPasswords] = useState({ current_password: '', new_password: '', confirm_password: '' })
  const [profileState, setProfileState] = useState<'idle'|'loading'|'success'|'error'>('idle')
  const [passwordState, setPasswordState] = useState<'idle'|'loading'|'success'|'error'>('idle')
  const [profileMessage, setProfileMessage] = useState('')
  const [passwordMessage, setPasswordMessage] = useState('')

  const saveProfile = async (event: FormEvent) => {
    event.preventDefault(); setProfileState('loading'); setProfileMessage('')
    try {
      const response = await authFetch('/auth/profile/', { method: 'PATCH', headers: {'Content-Type':'application/json'}, body: JSON.stringify(profile) })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(readError(data))
      if (token) login(token, data)
      setProfileState('success'); setProfileMessage('Your profile has been updated.')
    } catch (error) { setProfileState('error'); setProfileMessage(error instanceof Error ? error.message : 'Unable to update your profile.') }
  }

  const changePassword = async (event: FormEvent) => {
    event.preventDefault(); setPasswordState('loading'); setPasswordMessage('')
    if (!passwords.current_password || passwords.new_password.length < 8 || passwords.new_password !== passwords.confirm_password) {
      setPasswordState('error'); setPasswordMessage('Enter your current password and matching new passwords of at least eight characters.'); return
    }
    try {
      const response = await authFetch('/auth/password/change/', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(passwords) })
      const data = await response.json().catch(() => ({}))
      if (!response.ok) throw new Error(readError(data))
      if (user) login(data.token, user)
      setPasswords({ current_password:'', new_password:'', confirm_password:'' })
      setPasswordState('success'); setPasswordMessage('Password changed. Your secure session has been renewed.')
    } catch (error) { setPasswordState('error'); setPasswordMessage(error instanceof Error ? error.message : 'Unable to change your password.') }
  }

  return <div className="site-shell"><Navbar activePage="account"/><main id="main-content" className="s4-page">
    <nav className="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><span>Account</span></nav>
    <header className="s4-heading"><div><p className="eyebrow">Your NazRiy account</p><h1>Profile and security</h1></div><a href="/orders">View order history →</a></header>
    <div className="s4-account-grid">
      <form className="s4-card s4-form" onSubmit={saveProfile} noValidate><div className="s4-card-heading"><span>01</span><div><h2>Profile details</h2><p>Keep your delivery contact information current.</p></div></div>
        <label>Username<input value={user?.username || ''} disabled aria-describedby="username-note"/></label><small id="username-note">Usernames cannot be changed.</small>
        <div className="s4-field-row"><label>First name<input autoComplete="given-name" value={profile.first_name} onChange={event => setProfile({...profile,first_name:event.target.value})}/></label><label>Last name<input autoComplete="family-name" value={profile.last_name} onChange={event => setProfile({...profile,last_name:event.target.value})}/></label></div>
        <label>Email address *<input type="email" required autoComplete="email" value={profile.email} onChange={event => setProfile({...profile,email:event.target.value})}/></label>
        {profileMessage && <p className={`s4-feedback ${profileState}`} role={profileState==='error'?'alert':'status'}>{profileMessage}</p>}
        <button className="s4-submit" disabled={profileState==='loading'}>{profileState==='loading'?'Saving…':'Save profile'}</button>
      </form>
      <form className="s4-card s4-form" onSubmit={changePassword} noValidate><div className="s4-card-heading"><span>02</span><div><h2>Change password</h2><p>Choose a strong password you do not use elsewhere.</p></div></div>
        <label>Current password *<input type="password" required autoComplete="current-password" value={passwords.current_password} onChange={event => setPasswords({...passwords,current_password:event.target.value})}/></label>
        <label>New password *<input type="password" required autoComplete="new-password" value={passwords.new_password} onChange={event => setPasswords({...passwords,new_password:event.target.value})}/></label>
        <label>Confirm new password *<input type="password" required autoComplete="new-password" value={passwords.confirm_password} onChange={event => setPasswords({...passwords,confirm_password:event.target.value})}/></label>
        {passwordMessage && <p className={`s4-feedback ${passwordState}`} role={passwordState==='error'?'alert':'status'}>{passwordMessage}</p>}
        <button className="s4-submit" disabled={passwordState==='loading'}>{passwordState==='loading'?'Updating…':'Update password'}</button>
      </form>
    </div>
  </main></div>
}
