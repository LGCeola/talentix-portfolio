import router from '../router/index.js'

const TOKEN_KEY = 'talentix_token'
const USER_KEY = 'talentix_user'

export function getCurrentUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY))
  } catch {
    return null
  }
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

function errorMessage(data, fallback) {
  if (typeof data?.detail === 'string') return data.detail
  if (Array.isArray(data?.detail)) return data.detail[0]?.msg?.replace(/^Value error, /, '') || fallback
  return fallback
}

export async function apiFetch(path, options = {}) {
  const headers = { ...options.headers }
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) headers.Authorization = `Bearer ${token}`

  const response = await fetch(path, { ...options, headers })

  if (response.status === 401) {
    clearSession()
    router.push({ name: 'Login' })
    throw new Error('Sua sessão expirou. Faça login novamente.')
  }

  if (response.status === 204) return null

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    throw new Error(errorMessage(data, 'Ocorreu um erro inesperado. Tente novamente.'))
  }
  return data
}
