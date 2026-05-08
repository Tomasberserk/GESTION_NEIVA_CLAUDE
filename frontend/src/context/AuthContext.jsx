import { createContext, useContext, useState, useEffect } from 'react'
import authService from '../services/authService'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const verificar = async () => {
      try {
        const token = authService.getToken()
        if (token) {
          const user = await authService.getMe()
          setUsuario(user)
        }
      } catch {
        authService.clearToken()
      } finally {
        setCargando(false)
      }
    }
    verificar()
  }, [])

  const login = async (email, password) => {
    const data = await authService.login(email, password)
    setUsuario(data.usuario)
    return data
  }

  const registrar = async (payload) => {
    const data = await authService.registro(payload)
    setUsuario(data.usuario)
    return data
  }

  const logout = () => {
    authService.logout()
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, registrar, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth fuera de AuthProvider')
  return ctx
}
