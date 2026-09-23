import { ref, computed } from 'vue'

const token = ref(localStorage.getItem('cyber_token') || '')
const user = ref(JSON.parse(localStorage.getItem('cyber_user') || 'null'))
const mustChangePassword = ref(localStorage.getItem('cyber_must_change_pwd') === 'true')

export function useAuth() {
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isSuperAdmin = computed(() => user.value?.role === 'superadmin')
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'superadmin')
  const canManageIntegrations = computed(() => isAdmin.value || user.value?.can_manage_integrations)
  const canManageApps = computed(() => isAdmin.value || user.value?.can_manage_apps)
  const canManagePanels = computed(() => isAdmin.value || user.value?.can_manage_panels)

  const login = async (username, password) => {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Authentication failed (401)')
    }

    const data = await res.json()
    token.value = data.access_token
    user.value = data.user
    mustChangePassword.value = data.must_change_password

    localStorage.setItem('cyber_token', data.access_token)
    localStorage.setItem('cyber_user', JSON.stringify(data.user))
    localStorage.setItem('cyber_must_change_pwd', data.must_change_password ? 'true' : 'false')

    return data
  }

  const changePassword = async (currentPassword, newPassword) => {
    const res = await fetch('/api/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token.value}`
      },
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword
      })
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || 'Failed to update password')
    }

    mustChangePassword.value = false
    localStorage.setItem('cyber_must_change_pwd', 'false')
    return await res.json()
  }

  const logout = () => {
    token.value = ''
    user.value = null
    mustChangePassword.value = false
    localStorage.removeItem('cyber_token')
    localStorage.removeItem('cyber_user')
    localStorage.removeItem('cyber_must_change_pwd')
  }

  const authFetch = async (url, options = {}) => {
    const headers = options.headers || {}
    if (token.value) {
      headers['Authorization'] = `Bearer ${token.value}`
    }
    const res = await fetch(url, { ...options, headers })
    if (res.status === 401) {
      logout()
      throw new Error('Session expired. Please log in again.')
    }
    return res
  }

  return {
    token,
    user,
    mustChangePassword,
    isAuthenticated,
    isSuperAdmin,
    isAdmin,
    canManageIntegrations,
    canManageApps,
    canManagePanels,
    login,
    changePassword,
    logout,
    authFetch
  }
}
