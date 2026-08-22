import axios from "axios"

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080",
  headers: { "Content-Type": "application/json" }
})

// Auto attach token
api.interceptors.request.use(config => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("nova_token")
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 401 → redirect to login
api.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("nova_token")
      localStorage.removeItem("nova_user")
      window.location.href = "/login"
    }
    return Promise.reject(err)
  }
)

export default api

// Auth APIs
export const authAPI = {
  login:    (data: { email: string; password: string }) =>
              api.post("/auth/login", data),
  register: (data: { email: string; password: string; full_name: string }) =>
              api.post("/auth/register", data),
  refresh:  (token: string) =>
              api.post("/auth/refresh", { token }),
  logout:   () =>
              api.post("/auth/logout"),
}

// User APIs
export const userAPI = {
  getMe:    () => api.get("/users/me"),
  getUsage: () => api.get("/users/me/usage"),
  getAPIKeys: () => api.get("/users/me/api-keys"),
  createAPIKey: (name: string) => api.post("/users/me/api-keys", { name }),
  deleteAPIKey: (id: string) => api.delete(`/users/me/api-keys/${id}`),
}

// Billing APIs
export const billingAPI = {
  getPlans:   () => api.get("/billing/plans"),
  subscribe:  (data: { plan_id: string; billing_cycle: string }) =>
                api.post("/billing/subscribe", data),
  cancel:     () => api.post("/billing/cancel"),
  getInvoices:() => api.get("/billing/invoices"),
  getPortal:  () => api.get("/billing/portal"),
}

// Admin APIs
export const adminAPI = {
  getStats:    () => api.get("/admin/stats"),
  getUsers:    (page = 1, limit = 20) =>
                 api.get(`/admin/users?page=${page}&limit=${limit}`),
  updateUser:  (id: string, data: any) =>
                 api.patch(`/admin/users/${id}`, data),
  getPlans:    () => api.get("/billing/plans"),
  createPlan:  (data: any) => api.post("/admin/plans", data),
  updatePlan:  (id: string, data: any) => api.put(`/admin/plans/${id}`, data),
  getLogs:     () => api.get("/admin/system/logs"),
  getErrors:   (status = "open") => api.get(`/admin/errors?status=${status}`),
  updateError: (id: number, status: string) =>
                 api.patch(`/admin/errors/${id}`, { status }),
}
