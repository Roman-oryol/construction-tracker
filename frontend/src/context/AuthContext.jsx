import { createContext, useContext, useState } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  const login = async (accessToken) => {
    localStorage.setItem('token', accessToken)
    setToken(accessToken)

    try {
      const response = await client.get('/auth/me')
      const user = response.data
      // Сохраняем displayName: имя если есть, иначе email
      const displayName = user.name || user.email
      localStorage.setItem('userDisplayName', displayName)
    } catch {
      // Если запрос не удался — ничего страшного, сайдбар просто
      // покажет заглушку "Пользователь"
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('userDisplayName')
    setToken(null)
  }

  return <AuthContext.Provider value={{ token, login, logout }}>{children}</AuthContext.Provider>
}

export function useAuth() {
  return useContext(AuthContext)
}
