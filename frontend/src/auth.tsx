import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface SignupData {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

interface AuthState {
  user: User | null
  checking: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (data: SignupData) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

async function post<T>(url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    const detail = data?.detail
    // FastAPI validation errors arrive as a list; show the first readable message.
    const message = Array.isArray(detail)
      ? String(detail[0]?.msg ?? 'Please check the form').replace(/^Value error, /, '')
      : detail ?? `Request failed (${res.status})`
    throw new Error(message)
  }
  return res.status === 204 ? (undefined as T) : res.json()
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [checking, setChecking] = useState(true)

  useEffect(() => {
    fetch('/api/auth/me', { credentials: 'same-origin' })
      .then((r) => (r.ok ? r.json() : null))
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  const value: AuthState = {
    user,
    checking,
    login: async (email, password) => setUser(await post<User>('/api/auth/login', { email, password })),
    signup: async (data) => setUser(await post<User>('/api/auth/signup', data)),
    logout: async () => {
      await post('/api/auth/logout')
      setUser(null)
    },
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
