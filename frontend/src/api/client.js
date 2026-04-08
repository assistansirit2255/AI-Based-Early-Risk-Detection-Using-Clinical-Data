/**
 * Centralized Axios instance.
 * All requests use the same base URL and include credentials.
 */
import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
  timeout: 15000,
})

// Response interceptor: unwrap the standard envelope { status, data }
client.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalise error message for display
    const msg =
      error?.response?.data?.message ||
      error?.response?.data?.detail ||
      error?.message ||
      'An unexpected error occurred.'
    const enhanced = new Error(msg)
    enhanced.status = error?.response?.status
    enhanced.data = error?.response?.data
    return Promise.reject(enhanced)
  }
)

export default client
