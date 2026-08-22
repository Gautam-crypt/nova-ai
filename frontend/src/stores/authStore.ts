"use client"
import { create } from "zustand"
import { persist } from "zustand/middleware"
import { authAPI, userAPI } from "@/api/client"

interface User {
  id: string
  email: string
  full_name: string
  role: "admin" | "user"
  plan_id: string
  nova_name: string
  subscription_status: string
}

interface AuthStore {
  user:     User | null
  token:    string | null
  loading:  boolean
  error:    string | null

  setUser:  (user: User) => void
  setToken: (token: string) => void
  setError: (error: string | null) => void

  loginSequence: (email: string, password: string) => Promise<"admin" | "user">
  logout:        () => void
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user:    null,
      token:   null,
      loading: false,
      error:   null,

      setUser:  (user)  => set({ user }),
      setToken: (token) => set({ token }),
      setError: (error) => set({ error }),

      loginSequence: async (email, password) => {
        set({ loading: true, error: null })
        try {
          // Step 1 — Get token
          const loginRes = await authAPI.login({ email, password })
          const token = loginRes.data.access_token
          
          // Step 2 — Save token
          set({ token })
          localStorage.setItem("nova_token", token)
          document.cookie = `nova_token=${token}; path=/; max-age=86400`
          
          // Step 3 — Get user profile
          const userRes = await userAPI.getMe()
          const user = userRes.data
          
          // Step 4 — Save user
          set({ user, loading: false })
          localStorage.setItem("nova_user", JSON.stringify(user))
          document.cookie = `nova_user=${encodeURIComponent(JSON.stringify(user))}; path=/; max-age=86400`
          
          // Step 5 — Return role for redirect
          return user.role
          
        } catch (err: any) {
          let msg = "Login failed"
          const detail = err.response?.data?.detail
          if (typeof detail === 'string') {
            msg = detail
          } else if (Array.isArray(detail) && detail.length > 0) {
            msg = detail[0].msg
          }
          
          set({ error: msg, loading: false })
          throw new Error(msg)
        }
      },

      logout: () => {
        // Full purge — no session leakage
        set({ user: null, token: null, error: null })
        localStorage.removeItem("nova_token")
        localStorage.removeItem("nova_user")
        localStorage.removeItem("nova_auth")  // zustand persist key
        document.cookie = 'nova_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
        document.cookie = 'nova_user=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
        window.location.href = "/login"
      }
    }),
    {
      name: "nova_auth",
      partialize: (state) => ({
        token: state.token,
        user:  state.user
      })
    }
  )
)
