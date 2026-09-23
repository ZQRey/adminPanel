<template>
  <div class="space-y-6 select-none font-mono text-xs">
    <!-- Header & Action Button -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-3">
      <div>
        <div class="text-sm font-bold text-cyan-300">USER ROSTER & SECURITY PERMISSIONS</div>
        <div class="text-[10px] text-cyan-500/80">RBAC HIERARCHY: SUPERADMIN / ADMIN / USER // AD DOMAIN INTEGRATION</div>
      </div>
      <button 
        @click="showAddModal = true"
        class="px-3 py-1.5 rounded bg-cyan-950/80 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 shadow-[0_0_10px_rgba(0,243,255,0.3)] font-bold transition-all"
      >
        ＋ ENROLL OPERATOR
      </button>
    </div>

    <!-- Temporary Password Reset Notification Alert if recently triggered -->
    <div 
      v-if="tempPasswordNotice" 
      class="p-3 rounded bg-amber-950/70 border border-amber-400 text-amber-200 flex items-start justify-between animate-fade-in"
    >
      <div>
        <div class="font-bold text-amber-400">TEMPORARY ONE-TIME SECURITY KEY GENERATED:</div>
        <div class="text-sm font-bold mt-1 text-white bg-slate-950 px-2 py-1 rounded inline-block border border-amber-500">
          {{ tempPasswordNotice.temporary_password }}
        </div>
        <div class="text-[10px] text-amber-300/80 mt-1">
          User [{{ tempPasswordNotice.username }}] must update credentials immediately upon login.
        </div>
      </div>
      <button @click="tempPasswordNotice = null" class="text-amber-400 hover:text-white">✕</button>
    </div>

    <!-- Users Table -->
    <div class="overflow-x-auto rounded border border-cyan-500/30">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-950/80 text-[10px] text-cyan-400/80 border-b border-cyan-500/30">
            <th class="p-2.5">ID</th>
            <th class="p-2.5">USERNAME</th>
            <th class="p-2.5">SOURCE</th>
            <th class="p-2.5">ROLE</th>
            <th class="p-2.5">PERMISSIONS (INT / APP / PNL)</th>
            <th class="p-2.5">STATUS</th>
            <th class="p-2.5 text-right">ACTIONS</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-cyan-900/30">
          <tr v-for="user in users" :key="user.id" class="hover:bg-cyan-950/20 transition-colors">
            <td class="p-2.5 text-cyan-500/60">#{{ user.id }}</td>
            <td class="p-2.5 font-bold text-cyan-200">{{ user.username }}</td>
            <td class="p-2.5">
              <span 
                class="px-1.5 py-0.5 rounded text-[10px]"
                :class="user.auth_source === 'ad' ? 'bg-purple-950 text-purple-300 border border-purple-500/50' : 'bg-cyan-950 text-cyan-300 border border-cyan-500/50'"
              >
                {{ user.auth_source.toUpperCase() }}
              </span>
            </td>
            <td class="p-2.5">
              <span 
                class="px-1.5 py-0.5 rounded text-[10px] font-bold"
                :class="user.role === 'superadmin' ? 'text-amber-400 bg-amber-950/60 border border-amber-500/60' : user.role === 'admin' ? 'text-cyan-300 bg-cyan-950/60' : 'text-slate-300'"
              >
                {{ user.role.toUpperCase() }}
              </span>
            </td>
            <td class="p-2.5">
              <div class="flex items-center space-x-1">
                <span :class="user.can_manage_integrations ? 'text-emerald-400' : 'text-slate-600'" title="Integrations">INT</span>
                <span class="text-slate-600">/</span>
                <span :class="user.can_manage_apps ? 'text-emerald-400' : 'text-slate-600'" title="Apps">APP</span>
                <span class="text-slate-600">/</span>
                <span :class="user.can_manage_panels ? 'text-emerald-400' : 'text-slate-600'" title="Panels">PNL</span>
              </div>
            </td>
            <td class="p-2.5">
              <span v-if="user.must_change_password" class="text-amber-400 text-[10px]">PWD RESET REQ</span>
              <span v-else class="text-emerald-400 text-[10px]">ACTIVE</span>
            </td>
            <td class="p-2.5 text-right space-x-1.5">
              <!-- Edit Role & Permissions Button -->
              <button 
                @click="openEditModal(user)"
                class="px-2 py-0.5 rounded bg-cyan-950/70 hover:bg-cyan-900 border border-cyan-400 text-cyan-200 text-[10px] font-bold shadow-[0_0_8px_rgba(0,243,255,0.3)]"
                title="Edit role and granular permissions"
              >
                ⚙ ПРАВА
              </button>

              <!-- Only show RESET KEY if user is local (not AD domain user) -->
              <button 
                v-if="user.auth_source !== 'ad'"
                @click="resetUserPassword(user.id)"
                class="px-2 py-0.5 rounded bg-amber-950/50 hover:bg-amber-900 border border-amber-500/50 text-amber-300 text-[10px]"
                title="Issue temporary single-use password"
              >
                RESET KEY
              </button>

              <button 
                v-if="user.role !== 'superadmin'"
                @click="deleteUser(user.id)"
                class="px-2 py-0.5 rounded bg-red-950/50 hover:bg-red-900 border border-red-500/50 text-red-300 text-[10px]"
              >
                TERMINATE
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit User & Permissions Modal -->
    <div v-if="editingUser" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4 border border-cyan-400 shadow-[0_0_25px_rgba(0,243,255,0.4)]">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300 flex items-center space-x-2">
            <span>OPERATOR PERMISSIONS // {{ editingUser.username }}</span>
          </div>
          <button @click="editingUser = null" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <div class="p-2 rounded bg-slate-950/80 border border-cyan-500/20 text-[11px] text-cyan-300/80 flex items-center justify-between">
          <span>AUTHENTICATION DOMAIN:</span>
          <span 
            class="px-2 py-0.5 rounded font-bold"
            :class="editingUser.auth_source === 'ad' ? 'bg-purple-950 text-purple-300 border border-purple-500' : 'bg-cyan-950 text-cyan-300 border border-cyan-500'"
          >
            {{ editingUser.auth_source === 'ad' ? 'ACTIVE DIRECTORY (AD LDAP)' : 'LOCAL SYSTEM DATABASE' }}
          </span>
        </div>

        <form @submit.prevent="saveUserPermissions" class="space-y-4">
          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">SYSTEM ROLE HIERARCHY</label>
            <select 
              v-model="editForm.role" 
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            >
              <option value="user">USER (Standard Operator)</option>
              <option value="admin">ADMIN (System Administrator)</option>
              <option value="superadmin">SUPERADMIN (Master Root Controller)</option>
            </select>
          </div>

          <!-- Granular Permissions Toggles -->
          <div class="pt-2 border-t border-cyan-900/40 space-y-2.5">
            <div class="text-[10px] text-cyan-400/90 font-bold tracking-wider">GRANULAR ACCESS PERMISSIONS:</div>
            
            <label class="flex items-center space-x-2 text-cyan-200 cursor-pointer p-1.5 rounded hover:bg-cyan-950/40 border border-transparent hover:border-cyan-500/30 transition-all">
              <input type="checkbox" v-model="editForm.can_manage_integrations" class="accent-cyan-400 w-4 h-4" />
              <div>
                <span class="font-bold text-xs">Manage Integrations</span>
                <div class="text-[10px] text-cyan-400/60">Configure AD LDAP, Proxmox VE, and NUT Power proxies</div>
              </div>
            </label>

            <label class="flex items-center space-x-2 text-cyan-200 cursor-pointer p-1.5 rounded hover:bg-cyan-950/40 border border-transparent hover:border-cyan-500/30 transition-all">
              <input type="checkbox" v-model="editForm.can_manage_apps" class="accent-cyan-400 w-4 h-4" />
              <div>
                <span class="font-bold text-xs">Manage Applications & Bookmarks</span>
                <div class="text-[10px] text-cyan-400/60">Add, edit, or remove smart bookmarks and radial orbit apps</div>
              </div>
            </label>

            <label class="flex items-center space-x-2 text-cyan-200 cursor-pointer p-1.5 rounded hover:bg-cyan-950/40 border border-transparent hover:border-cyan-500/30 transition-all">
              <input type="checkbox" v-model="editForm.can_manage_panels" class="accent-cyan-400 w-4 h-4" />
              <div>
                <span class="font-bold text-xs">Manage Dashboards & Widgets</span>
                <div class="text-[10px] text-cyan-400/60">Create personal dashboards, arrange widgets, clone templates</div>
              </div>
            </label>

            <label class="flex items-center space-x-2 text-cyan-200 cursor-pointer p-1.5 rounded hover:bg-cyan-950/40 border border-transparent hover:border-cyan-500/30 transition-all">
              <input type="checkbox" v-model="editForm.is_active" class="accent-cyan-400 w-4 h-4" />
              <div>
                <span class="font-bold text-xs">Account Active Status</span>
                <div class="text-[10px] text-cyan-400/60">Uncheck to lock operator from authenticating</div>
              </div>
            </label>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t border-cyan-900/40">
            <button 
              type="button" 
              @click="editingUser = null"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              CANCEL
            </button>
            <button 
              type="submit"
              class="px-4 py-1.5 rounded bg-cyan-950 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 font-bold shadow-[0_0_12px_rgba(0,243,255,0.4)]"
            >
              UPDATE PERMISSIONS
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Enroll Operator Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300">NEW OPERATOR ENROLLMENT</div>
          <button @click="showAddModal = false" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <form @submit.prevent="createUser" class="space-y-3">
          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">USERNAME</label>
            <input 
              v-model="newUser.username" 
              type="text" 
              required 
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">INITIAL PASSWORD (BLANK FOR AUTO-TEMP)</label>
            <input 
              v-model="newUser.password" 
              type="password" 
              placeholder="Leave blank for one-time code"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">SECURITY ROLE</label>
            <select 
              v-model="newUser.role" 
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            >
              <option value="user">USER (Standard Operator)</option>
              <option value="admin">ADMIN (System Administrator)</option>
              <option value="superadmin">SUPERADMIN (Master Root)</option>
            </select>
          </div>

          <!-- Granular Permissions Toggles -->
          <div class="pt-2 border-t border-cyan-900/40 space-y-2">
            <div class="text-[10px] text-cyan-400/80 font-bold">GRANULAR ACCESS DELEGATION:</div>
            <label class="flex items-center space-x-2 text-cyan-200">
              <input type="checkbox" v-model="newUser.can_manage_integrations" class="accent-cyan-400" />
              <span>Can Configure Integrations (AD / Proxmox / NUT)</span>
            </label>
            <label class="flex items-center space-x-2 text-cyan-200">
              <input type="checkbox" v-model="newUser.can_manage_apps" class="accent-cyan-400" />
              <span>Can Configure Smart Bookmark Applications</span>
            </label>
            <label class="flex items-center space-x-2 text-cyan-200">
              <input type="checkbox" v-model="newUser.can_manage_panels" class="accent-cyan-400" />
              <span>Can Create & Modify Dashboards</span>
            </label>
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t border-cyan-900/40">
            <button 
              type="button" 
              @click="showAddModal = false"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              CANCEL
            </button>
            <button 
              type="submit"
              class="px-4 py-1.5 rounded bg-cyan-950 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 font-bold"
            >
              CONFIRM ENROLLMENT
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { authFetch } = useAuth()

const users = ref([])
const showAddModal = ref(false)
const tempPasswordNotice = ref(null)

const editingUser = ref(null)
const editForm = ref({
  role: 'user',
  can_manage_integrations: false,
  can_manage_apps: false,
  can_manage_panels: false,
  is_active: true
})

const newUser = ref({
  username: '',
  password: '',
  role: 'user',
  can_manage_integrations: false,
  can_manage_apps: false,
  can_manage_panels: true
})

const fetchUsers = async () => {
  try {
    const res = await authFetch('/api/users')
    if (res.ok) {
      users.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to fetch users:', e)
  }
}

const openEditModal = (user) => {
  editingUser.value = user
  editForm.value = {
    role: user.role,
    can_manage_integrations: user.can_manage_integrations,
    can_manage_apps: user.can_manage_apps,
    can_manage_panels: user.can_manage_panels,
    is_active: user.is_active
  }
}

const saveUserPermissions = async () => {
  if (!editingUser.value) return
  try {
    const res = await authFetch(`/api/users/${editingUser.value.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editForm.value)
    })
    if (res.ok) {
      alert(`Permissions updated successfully for ${editingUser.value.username}!`)
      editingUser.value = null
      fetchUsers()
    } else {
      const err = await res.json().catch(() => ({}))
      alert('Update failed: ' + (err.detail || 'Access restricted'))
    }
  } catch (e) {
    alert('Update error: ' + e.message)
  }
}

const createUser = async () => {
  try {
    const res = await authFetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newUser.value)
    })
    if (res.ok) {
      showAddModal.value = false
      newUser.value = {
        username: '',
        password: '',
        role: 'user',
        can_manage_integrations: false,
        can_manage_apps: false,
        can_manage_panels: true
      }
      fetchUsers()
    }
  } catch (e) {
    alert('User enrollment failed: ' + e.message)
  }
}

const resetUserPassword = async (userId) => {
  if (!confirm('Issue temporary single-use password for this user?')) return
  try {
    const res = await authFetch(`/api/users/${userId}/reset-password`, { method: 'POST' })
    if (res.ok) {
      tempPasswordNotice.value = await res.json()
      fetchUsers()
    }
  } catch (e) {
    alert('Reset failed: ' + e.message)
  }
}

const deleteUser = async (userId) => {
  if (!confirm('Confirm operator termination?')) return
  try {
    const res = await authFetch(`/api/users/${userId}`, { method: 'DELETE' })
    if (res.ok) {
      fetchUsers()
    }
  } catch (e) {
    alert('Delete failed: ' + e.message)
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
