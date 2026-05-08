import { createContext, useContext, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const login = (accessToken, email) => {
    localStorage.setItem('token', accessToken)
    if (email) localStorage.setItem('userEmail', email) // новая строка
    setToken(accessToken)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userEmail') // новая строка
    setToken(null)
  }

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
