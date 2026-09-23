<template>
  <div class="space-y-6 select-none font-mono text-xs">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-3">
      <div>
        <div class="text-sm font-bold text-cyan-300">SMART BOOKMARKS & ORBITAL LAYOUT</div>
        <div class="text-[10px] text-cyan-500/80">
          MANAGE APPLICATIONS, ORBITAL NODES & GROUPING COMPOSITION
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <button 
          @click="showAddModal = true"
          class="px-3 py-1.5 rounded bg-cyan-950/80 border border-cyan-400 text-cyan-300 hover:bg-cyan-900 font-bold transition-all shadow-[0_0_10px_rgba(0,243,255,0.3)]"
        >
          ＋ ADD APPLICATION
        </button>
      </div>
    </div>

    <!-- 1. GROUPING / LAYOUT TOGGLE («КОМПАНОВКА КНОПОК») -->
    <div class="p-4 rounded hud-glass-panel border border-cyan-400/50 space-y-3 shadow-[0_0_20px_rgba(0,243,255,0.15)]">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-3">
          <span class="text-lg">📁</span>
          <div>
            <div class="text-sm font-bold text-cyan-200">
              РЕЖИМ КОМПАНОВКИ И ГРУППИРОВКИ КНОПОК
            </div>
            <div class="text-[10px] text-cyan-400/70">
              Предотвращает путаницу: объединяет приложения и интеграции в орбитальные группы
            </div>
          </div>
        </div>

        <button 
          @click="toggleGrouping(!isGroupingEnabled)"
          class="px-4 py-1.5 rounded font-bold transition-all border text-xs"
          :class="isGroupingEnabled ? 'bg-emerald-950 border-emerald-400 text-emerald-300 shadow-[0_0_15px_rgba(0,255,102,0.4)]' : 'bg-slate-900 border-slate-700 text-slate-400'"
        >
          {{ isGroupingEnabled ? '✔ КОМПАНОВКА ВКЛЮЧЕНА' : '✖ ВЫКЛЮЧЕНА' }}
        </button>
      </div>

      <!-- Groups Management Sub-Panel (Visible when Grouping is ON) -->
      <div v-if="isGroupingEnabled" class="pt-3 border-t border-cyan-900/40 space-y-3 animate-fade-in">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-cyan-300">МЕНЮ НАСТРОЙКИ ГРУПП:</span>
          <button 
            @click="showAddGroupModal = true"
            class="px-2.5 py-1 rounded bg-purple-950 hover:bg-purple-900 border border-purple-400 text-purple-300 text-[10px] font-bold"
          >
            ＋ СОЗДАТЬ ГРУППУ
          </button>
        </div>

        <!-- Groups Chips / List -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          <div 
            v-for="grp in groups" 
            :key="grp.id"
            class="p-2.5 rounded bg-slate-950/80 border flex items-center justify-between group hover:scale-[1.02] transition-all"
            :style="{ borderColor: grp.color || '#00f3ff' }"
          >
            <div class="flex items-center space-x-2">
              <span class="text-base">{{ grp.icon || '📁' }}</span>
              <div>
                <div class="font-bold text-cyan-100 truncate max-w-[90px]">{{ grp.name }}</div>
                <div class="text-[9px] text-emerald-400">{{ getAppsCountInGroup(grp.name) }} элементов</div>
              </div>
            </div>
            <button 
              v-if="groups.length > 1"
              @click="deleteGroup(grp.id)"
              class="text-red-400/50 hover:text-red-300 text-xs px-1"
              title="Delete group"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. APPLICATIONS GRID -->
    <div class="space-y-2">
      <div class="text-xs font-bold text-cyan-300">СПИСОК ПРИЛОЖЕНИЙ И ССЫЛОК ({{ apps.length }}):</div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          v-for="app in apps" 
          :key="app.id"
          class="hud-glass-panel p-4 rounded border border-cyan-500/30 hover:border-cyan-400 transition-all flex items-center justify-between"
        >
          <div class="flex items-center space-x-3">
            <div 
              class="w-10 h-10 rounded-full border border-cyan-400 flex items-center justify-center text-sm shadow-[0_0_10px_rgba(0,243,255,0.3)]"
              :style="{ backgroundColor: app.color ? `${app.color}22` : 'rgba(0,243,255,0.1)' }"
            >
              <span class="text-cyan-300">
                {{ app.icon === 'server' ? '🖥' : app.icon === 'activity' ? '📈' : app.icon === 'shield' ? '🛡' : '⚡' }}
              </span>
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <span class="text-sm font-bold text-cyan-200">{{ app.title }}</span>
                <span 
                  v-if="isGroupingEnabled && app.group_name" 
                  class="text-[9px] px-1.5 py-0.2 rounded bg-purple-950/80 border border-purple-500/40 text-purple-300"
                >
                  📁 {{ app.group_name }}
                </span>
              </div>
              <div class="text-[10px] text-cyan-400/60">{{ app.description || 'Quick launch app' }}</div>
              <div class="text-[9px] text-emerald-400 mt-0.5 truncate max-w-[200px]">{{ app.url }}</div>
            </div>
          </div>

          <div class="flex flex-col items-end space-y-1.5">
            <!-- Group assignment dropdown if grouping is active -->
            <select
              v-if="isGroupingEnabled"
              :value="app.group_name || 'Инфраструктура'"
              @change="updateAppGroup(app, $event.target.value)"
              class="bg-slate-900 border border-cyan-500/30 rounded px-1.5 py-0.5 text-[10px] text-cyan-300 focus:outline-none focus:border-cyan-400"
            >
              <option v-for="g in groups" :key="g.id" :value="g.name">
                {{ g.name }}
              </option>
            </select>

            <div class="flex items-center space-x-1.5">
              <a 
                :href="app.url" 
                :target="app.target || '_blank'"
                class="px-2 py-0.5 rounded bg-cyan-950/60 hover:bg-cyan-900 border border-cyan-400/50 text-cyan-300 text-[10px]"
              >
                TEST ↗
              </a>
              <button 
                @click="deleteApp(app.id)"
                class="px-2 py-0.5 rounded bg-red-950/50 hover:bg-red-900 border border-red-500/50 text-red-300 text-[10px]"
              >
                DELETE
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Group Modal -->
    <div v-if="showAddGroupModal" class="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-sm space-y-4 border border-purple-400">
        <div class="flex items-center justify-between border-b border-purple-500/40 pb-2">
          <div class="text-sm font-bold text-purple-300">СОЗДАНИЕ НОВОЙ ГРУППЫ</div>
          <button @click="showAddGroupModal = false" class="text-purple-400 hover:text-white">✕</button>
        </div>

        <form @submit.prevent="createGroup" class="space-y-3">
          <div>
            <label class="block text-[10px] text-purple-300/80 mb-1">НАЗВАНИЕ ГРУППЫ</label>
            <input 
              v-model="newGroup.name" 
              type="text" 
              required
              placeholder="e.g. Кластерные базы данных"
              class="w-full bg-slate-950 border border-purple-500/40 rounded px-2.5 py-1.5 text-purple-100 font-mono text-xs focus:outline-none focus:border-purple-400"
            />
          </div>

          <div class="grid grid-cols-2 gap-2">
            <div>
              <label class="block text-[10px] text-purple-300/80 mb-1">ИКОНКА / СИМВОЛ</label>
              <select 
                v-model="newGroup.icon" 
                class="w-full bg-slate-950 border border-purple-500/40 rounded px-2.5 py-1.5 text-purple-100 font-mono text-xs focus:outline-none focus:border-purple-400"
              >
                <option value="🖥">🖥 Инфра</option>
                <option value="📈">📈 Мониторинг</option>
                <option value="🛡">🛡 Защита</option>
                <option value="⚡">⚡ Сервисы</option>
                <option value="🌐">🌐 Сеть</option>
                <option value="💾">💾 Хранилище</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] text-purple-300/80 mb-1">НЕОНОВЫЙ ЦВЕТ</label>
              <input 
                v-model="newGroup.color" 
                type="color" 
                class="w-full h-8 bg-slate-950 border border-purple-500/40 rounded cursor-pointer"
              />
            </div>
          </div>

          <div class="flex items-center justify-end space-x-2 pt-3 border-t border-purple-900/40">
            <button 
              type="button" 
              @click="showAddGroupModal = false"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              ОТМЕНА
            </button>
            <button 
              type="submit"
              class="px-4 py-1.5 rounded bg-purple-950 border border-purple-400 text-purple-200 hover:bg-purple-900 font-bold"
            >
              ДОБАВИТЬ ГРУППУ
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add App Modal -->
    <div v-if="showAddModal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300">REGISTER NEW RADIAL APP</div>
          <button @click="showAddModal = false" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <form @submit.prevent="createApp" class="space-y-3">
          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">APP TITLE / DISPLAY NAME</label>
            <input 
              v-model="newApp.title" 
              type="text" 
              required
              placeholder="e.g. Nextcloud Hub"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">DESCRIPTION</label>
            <input 
              v-model="newApp.description" 
              type="text" 
              placeholder="Internal cloud storage"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label class="block text-[10px] text-cyan-400/80 mb-1">DESTINATION URL</label>
            <input 
              v-model="newApp.url" 
              type="url" 
              required
              placeholder="https://nextcloud.local"
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            />
          </div>

          <!-- Group Assignment Field -->
          <div v-if="isGroupingEnabled">
            <label class="block text-[10px] text-cyan-400/80 mb-1">ПРИВЯЗКА К ГРУППЕ КОМПАНОВКИ</label>
            <select 
              v-model="newApp.group_name" 
              class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
            >
              <option v-for="g in groups" :key="g.id" :value="g.name">
                {{ g.name }}
              </option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-[10px] text-cyan-400/80 mb-1">NEON GLYPH ICON</label>
              <select 
                v-model="newApp.icon" 
                class="w-full bg-slate-950 border border-cyan-500/40 rounded px-2.5 py-1.5 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400"
              >
                <option value="server">🖥 Server Node</option>
                <option value="activity">📈 Telemetry Chart</option>
                <option value="shield">🛡 Security Shield</option>
                <option value="box">⚡ Core Utility</option>
              </select>
            </div>
            <div>
              <label class="block text-[10px] text-cyan-400/80 mb-1">ACCENT COLOR</label>
              <input 
                v-model="newApp.color" 
                type="color" 
                class="w-full h-8 bg-slate-950 border border-cyan-500/40 rounded cursor-pointer"
              />
            </div>
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
              ATTACH TO RADIAL ORBIT
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
import { useGrouping } from '@/composables/useGrouping'

const emit = defineEmits(['apps-updated'])
const { authFetch } = useAuth()
const { isGroupingEnabled, groups, toggleGrouping, addGroup, deleteGroup } = useGrouping()

const apps = ref([])
const showAddModal = ref(false)
const showAddGroupModal = ref(false)

const newGroup = ref({
  name: '',
  icon: '📁',
  color: '#00f3ff'
})

const newApp = ref({
  title: '',
  description: '',
  url: '',
  icon: 'server',
  color: '#00f3ff',
  group_name: 'Инфраструктура',
  target: '_blank'
})

const getAppsCountInGroup = (groupName) => {
  return apps.value.filter(a => a.group_name === groupName).length
}

const fetchApps = async () => {
  try {
    const res = await authFetch('/api/apps')
    if (res.ok) {
      apps.value = await res.json()
      // If any apps have default group null, default them
      emit('apps-updated', apps.value)
    }
  } catch (e) {
    console.error('Failed to fetch apps:', e)
  }
}

const updateAppGroup = async (app, newGroupName) => {
  try {
    const res = await authFetch(`/api/apps/${app.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_name: newGroupName })
    })
    if (res.ok) {
      app.group_name = newGroupName
      emit('apps-updated', apps.value)
    }
  } catch (e) {
    alert('Failed to update group: ' + e.message)
  }
}

const createGroup = () => {
  if (!newGroup.value.name.trim()) return
  addGroup(newGroup.value)
  newGroup.value = { name: '', icon: '📁', color: '#00f3ff' }
  showAddGroupModal.value = false
}

const createApp = async () => {
  try {
    const res = await authFetch('/api/apps', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newApp.value)
    })
    if (res.ok) {
      showAddModal.value = false
      newApp.value = { title: '', description: '', url: '', icon: 'server', color: '#00f3ff', group_name: 'Инфраструктура', target: '_blank' }
      fetchApps()
    }
  } catch (e) {
    alert('Create app error: ' + e.message)
  }
}

const deleteApp = async (id) => {
  if (!confirm('Remove this application from radial orbit?')) return
  try {
    const res = await authFetch(`/api/apps/${id}`, { method: 'DELETE' })
    if (res.ok) {
      fetchApps()
    }
  } catch (e) {
    alert('Delete error: ' + e.message)
  }
}

onMounted(() => {
  fetchApps()
})
</script>
