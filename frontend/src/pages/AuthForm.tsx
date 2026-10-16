import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth'

const MIN_PASSWORD_LENGTH = 8

/** Log in and Create account forms, backed by /api/auth. */
export default function AuthForm({ mode }: { mode: 'login' | 'signup' }) {
  const signup = mode === 'signup'
  const auth = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    const form = e.currentTarget
    const data = Object.fromEntries(new FormData(form)) as Record<string, string>
    const confirm = form.elements.namedItem('confirm_password') as HTMLInputElement | null
    confirm?.setCustomValidity(confirm.value !== data.password ? 'Passwords do not match' : '')
    if (!form.reportValidity()) return

    setBusy(true)
    setError(null)
    try {
      if (signup) {
        await auth.signup({
          first_name: data.first_name,
          last_name: data.last_name,
          email: data.email,
          password: data.password,
          confirm_password: data.confirm_password,
        })
      } else {
        await auth.login(data.email, data.password)
      }
      navigate('/')
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setBusy(false)
    }
  }

  if (auth.user) {
    return (
      <section className="section auth">
        <h1>You're logged in</h1>
        <p>Signed in as <strong>{auth.user.email}</strong>.</p>
        <button className="button" onClick={() => auth.logout()}>Log out</button>
      </section>
    )
  }

  return (
    <section className="section auth">
      <h1>{signup ? 'Create account' : 'Log in'}</h1>
      <form className="auth__form" onSubmit={submit} noValidate>
        {signup && (
          <div className="auth__row">
            <label>First name<input name="first_name" autoComplete="given-name" maxLength={60} required /></label>
            <label>Last name<input name="last_name" autoComplete="family-name" maxLength={60} required /></label>
          </div>
        )}
        <label>Email<input type="email" name="email" autoComplete="email" required /></label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete={signup ? 'new-password' : 'current-password'}
            minLength={signup ? MIN_PASSWORD_LENGTH : undefined}
            maxLength={128}
            required
          />
          {signup && <small className="field-hint">At least {MIN_PASSWORD_LENGTH} characters.</small>}
        </label>
        {signup && (
          <label>
            Confirm password
            <input
              type="password"
              name="confirm_password"
              autoComplete="new-password"
              required
              onInput={(e) => e.currentTarget.setCustomValidity('')}
            />
          </label>
        )}
        {error && <p className="error" role="alert">{error}</p>}
        <button type="submit" className="button" disabled={busy}>
          {busy ? 'Please wait…' : signup ? 'Create account' : 'Log in'}
        </button>
      </form>
      <p className="auth__switch">
        {signup ? <>Already have an account? <Link to="/login">Log in</Link></> : <>New here? <Link to="/create-account">Create an account</Link></>}
      </p>
    </section>
  )
}
