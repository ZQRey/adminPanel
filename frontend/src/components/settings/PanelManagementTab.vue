<template>
  <div class="space-y-6 select-none font-mono text-xs">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-3">
      <div>
        <div class="text-sm font-bold text-cyan-300">MULTI-TENANT DASHBOARD PANELS</div>
        <div class="text-[10px] text-cyan-500/80">SYSTEM TEMPLATES // PERSONAL USER PROFILES // CLONING</div>
      </div>
      <button 
        @click="showCreateModal = true"
        class="px-3 py-1.5 rounded bg-cyan-950/80 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 font-bold transition-all shadow-[0_0_10px_rgba(0,243,255,0.3)]"
      >
        ＋ INITIALIZE NEW PANEL
      </button>
    </div>

    <!-- Panels Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="panel in panels" 
        :key="panel.id"
        class="hud-glass-panel p-4 rounded border border-cyan-500/30 hover:border-cyan-400 transition-all flex flex-col justify-between space-y-3"
      >
        <div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-bold text-cyan-200">{{ panel.name }}</span>
            <span 
              class="text-[9px] px-1.5 py-0.5 rounded font-bold"
              :class="panel.is_system_template ? 'bg-amber-950 text-amber-300 border border-amber-500/50' : 'bg-cyan-950 text-cyan-300 border border-cyan-500/50'"
            >
              {{ panel.is_system_template ? 'SYSTEM TEMPLATE' : 'USER DASHBOARD' }}
            </span>
          </div>
          <p class="text-[11px] text-cyan-400/70 mt-1">{{ panel.description || 'No description provided' }}</p>
        </div>

        <!-- Widgets in this panel breakdown (System vs User) -->
        <div class="p-2.5 rounded bg-slate-950/60 border border-cyan-500/20 space-y-1">
          <div class="text-[10px] text-cyan-400/80 font-bold flex justify-between">
            <span>ATTACHED WIDGETS ({{ panel.widgets?.length || 0 }}):</span>
            <span class="text-emerald-400">
              {{ panel.widgets?.filter(w => w.is_system).length || 0 }} LOCKED SYSTEM
            </span>
          </div>
          <div class="flex flex-wrap gap-1.5 pt-1">
            <span 
              v-for="w in panel.widgets" 
              :key="w.id"
              class="text-[10px] px-1.5 py-0.5 rounded flex items-center space-x-1"
              :class="w.is_system ? 'bg-slate-900 border border-amber-500/40 text-amber-300' : 'bg-cyan-950/60 border border-cyan-500/30 text-cyan-300'"
            >
              <span>{{ w.is_system ? '🔒' : '⚙' }}</span>
              <span>{{ w.title }}</span>
            </span>
          </div>
        </div>

        <!-- Panel Actions -->
        <div class="flex items-center justify-between pt-2 border-t border-cyan-900/40">
          <span class="text-[10px] text-cyan-500/60">ID: #{{ panel.id }}</span>
          <div class="space-x-2">
            <button 
              @click="openCloneModal(panel)"
              class="px-2.5 py-1 rounded bg-purple-950/60 hover:bg-purple-900 border border-purple-400/60 text-purple-300 font-bold text-[10px]"
            >
              ⧉ CLONE PANEL
            </button>
            <button 
              v-if="!panel.is_system_template || isAdmin"
              @click="deletePanel(panel.id)"
              class="px-2.5 py-1 rounded bg-red-950/50 hover:bg-red-900 border border-red-500/50 text-red-300 text-[10px]"
            >
              DELETE
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Clone Modal -->
    <div v-if="cloningPanel" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300">CLONE DASHBOARD PANEL</div>
          <button @click="cloningPanel = null" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <div class="text-[11px] text-cyan-400/80">
          Creates a cloned replicate of <span class="text-white font-bold">{{ cloningPanel.name }}</span> including all widget definitions and system locks.
        </div>

        <form @submit.prevent="executeClone" class="space-y-3">
          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">NEW PANEL NAME</label>
            <input 
              v-model="cloneForm.new_panel_name" 
              type="text" 
              required
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t border-cyan-900/40">
            <button 
              type="button" 
              @click="cloningPanel = null"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              CANCEL
            </button>
            <button 
              type="submit"
              class="px-4 py-1.5 rounded bg-purple-950 border border-purple-400 text-purple-200 hover:bg-purple-900 font-bold"
            >
              EXECUTE CLONE
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Create Panel Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300">INITIALIZE NEW PANEL</div>
          <button @click="showCreateModal = false" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <form @submit.prevent="createPanel" class="space-y-3">
          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">PANEL NAME</label>
            <input 
              v-model="newPanel.name" 
              type="text" 
              required
              placeholder="e.g. Infrastructure Cockpit"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">DESCRIPTION</label>
            <input 
              v-model="newPanel.description" 
              type="text" 
              placeholder="Panel role / mission scope"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div class="flex items-center justify-end space-x-3 pt-4 border-t border-cyan-900/40">
            <button 
              type="button" 
              @click="showCreateModal = false"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              CANCEL
            </button>
            <button 
              type="submit"
              class="px-4 py-1.5 rounded bg-cyan-950 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 font-bold"
            >
              CREATE PANEL
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

const { authFetch, isAdmin } = useAuth()

const panels = ref([])
const showCreateModal = ref(false)
const cloningPanel = ref(null)

const newPanel = ref({
  name: '',
  description: '',
  is_default: false
})

const cloneForm = ref({
  new_panel_name: ''
})

const fetchPanels = async () => {
  try {
    const res = await authFetch('/api/panels')
    if (res.ok) {
      panels.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to fetch panels:', e)
  }
}

const createPanel = async () => {
  try {
    const res = await authFetch('/api/panels', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newPanel.value)
    })
    if (res.ok) {
      showCreateModal.value = false
      newPanel.value = { name: '', description: '', is_default: false }
      fetchPanels()
    }
  } catch (e) {
    alert('Create panel error: ' + e.message)
  }
}

const openCloneModal = (panel) => {
  cloningPanel.value = panel
  cloneForm.value.new_panel_name = `${panel.name} (Copy)`
}

const executeClone = async () => {
  try {
    const res = await authFetch(`/api/panels/${cloningPanel.value.id}/clone`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cloneForm.value)
    })
    if (res.ok) {
      cloningPanel.value = null
      fetchPanels()
    }
  } catch (e) {
    alert('Clone panel error: ' + e.message)
  }
}

const deletePanel = async (id) => {
  if (!confirm('Delete this dashboard panel?')) return
  try {
    const res = await authFetch(`/api/panels/${id}`, { method: 'DELETE' })
    if (res.ok) {
      fetchPanels()
    }
  } catch (e) {
    alert('Delete error: ' + e.message)
  }
}

onMounted(() => {
  fetchPanels()
})
</script>
