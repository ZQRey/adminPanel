<template>
  <div class="relative w-screen h-screen overflow-hidden cyber-background-container font-hud">
    <!-- Animated Cyber Canvas Background (Particles, Radar Sweep, Circuit Nodes) -->
    <CyberAnimatedBackground />

    <!-- CRT Scanline overlay effect -->
    <div class="absolute inset-0 scanline-overlay z-40"></div>

    <!-- 1. AUTHENTICATION VIEW (STAGE 1) -->
    <div v-if="!isAuthenticated" class="relative z-30 w-full h-full">
      <MorphingLoginForm @authenticated="handleAuthenticated" />
    </div>

    <!-- 2. MAIN DASHBOARD VIEW (STAGES 2, 3, 4) -->
    <div v-else class="relative z-30 w-full h-full flex flex-col justify-between">
      <!-- TOP HUD NAV / TELEMETRY BAR -->
      <header class="w-full px-6 py-3 border-b border-cyan-500/30 bg-slate-950/80 backdrop-blur-md flex items-center justify-between z-30 shadow-[0_4px_20px_rgba(0,243,255,0.15)]">
        <!-- Logo & Active Panel Switcher -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-cyan-400 shadow-[0_0_10px_#00f3ff] animate-pulse"></div>
            <span class="text-sm font-black tracking-widest text-cyan-200 text-glow-cyan">
              CYBER//HUD
            </span>
          </div>

          <!-- Active Panel Selector -->
          <div class="hidden sm:flex items-center space-x-2 pl-4 border-l border-cyan-900/60 font-mono text-xs">
            <span class="text-cyan-500/70 text-[10px]">ACTIVE PANEL:</span>
            <select 
              v-model="activePanelId" 
              class="bg-slate-900 border border-cyan-500/40 rounded px-2 py-0.5 text-cyan-200 focus:outline-none focus:border-cyan-400 text-xs"
            >
              <option v-for="p in userPanels" :key="p.id" :value="p.id">
                {{ p.name }} {{ p.is_system_template ? '[TEMPLATE]' : '' }}
              </option>
            </select>
          </div>
        </div>

        <!-- Telemetry Status & Operator Profile & Controls -->
        <div class="flex items-center space-x-3 font-mono text-xs">
          <!-- Live Telemetry Pill -->
          <div 
            class="flex items-center space-x-1.5 px-2.5 py-1 rounded-full border text-[10px]"
            :class="isConnected ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300' : 'bg-amber-950/80 border-amber-500/50 text-amber-300'"
          >
            <span class="w-2 h-2 rounded-full" :class="isConnected ? 'bg-emerald-400 animate-ping' : 'bg-amber-400'"></span>
            <span>{{ isConnected ? 'TELEMETRY: LIVE WS' : 'CONNECTING WS...' }}</span>
          </div>

          <!-- Operator Info -->
          <div class="hidden md:flex items-center space-x-2 px-3 py-1 rounded bg-slate-900/80 border border-cyan-500/30 text-[11px]">
            <span class="text-cyan-500/70">OPERATOR:</span>
            <span class="font-bold text-cyan-200">{{ user?.username }}</span>
            <span 
              class="text-[9px] px-1.5 py-0.2 rounded font-bold"
              :class="user?.role === 'superadmin' ? 'bg-amber-950 text-amber-300 border border-amber-500/40' : 'bg-cyan-950 text-cyan-400'"
            >
              {{ user?.role?.toUpperCase() }}
            </span>
          </div>

          <!-- Settings Button -->
          <button
            @click="openSettings('panels')"
            class="p-1.5 rounded bg-cyan-950/60 hover:bg-cyan-900 border border-cyan-500/40 hover:border-cyan-300 text-cyan-300 shadow-[0_0_10px_rgba(0,243,255,0.2)] transition-all"
            title="System Settings & Administration"
          >
            ⚙
          </button>

          <!-- Logout Button -->
          <button
            @click="logout"
            class="px-2.5 py-1 rounded bg-red-950/50 hover:bg-red-900 border border-red-500/40 text-red-300 text-[10px] font-bold transition-all"
            title="Terminate Session"
          >
            LOGOUT
          </button>
        </div>
      </header>

      <!-- MAIN CONTENT VIEWPORT (CENTER RADIAL MENU + PERIPHERAL WIDGETS) -->
      <main class="relative flex-1 w-full h-full flex items-center justify-center overflow-hidden">
        <!-- PERIPHERAL HUD WIDGET GRID (Backdrop-blurred when radial menu open) -->
        <div class="absolute inset-0 z-10">
          <WidgetGrid 
            :is-menu-open="isRadialMenuOpen"
            :proxmox="proxmox"
            :nut="nut"
            :plugins="plugins"
          />
        </div>

        <!-- CENTER RADIAL MENU WITH 360° SPIN & DYNAMIC PCB TRACES -->
        <div class="relative z-20 pointer-events-auto">
          <RadialMenu 
            :apps="registeredApps"
            @menu-toggled="handleRadialMenuToggle"
            @action="handleRadialAction"
          />
        </div>
      </main>

      <!-- FOOTER STATUS STRIP -->
      <footer class="w-full px-6 py-1.5 border-t border-cyan-500/20 bg-slate-950/90 flex items-center justify-between text-[10px] font-mono text-cyan-500/60 z-30">
        <div class="flex items-center space-x-3">
          <span>SEC//NODE: ACTIVE</span>
          <span>ENCRYPTION: FERNET/AES-GCM</span>
          <span>AUTH: AD PRIORITY + LOCAL FALLBACK</span>
        </div>
        <div>
          <span>SCI-FI HUD HOMMAR CONSOLE</span>
        </div>
      </footer>
    </div>

    <!-- SETTINGS & ADMINISTRATION MODAL (STAGE 3) -->
    <SettingsModal 
      v-if="showSettingsModal"
      :initial-tab="settingsInitialTab"
      @close="showSettingsModal = false"
      @apps-updated="handleAppsUpdated"
    />

    <!-- FORCED PASSWORD RESET MODAL FOR ONE-TIME TEMPORARY PASSWORDS -->
    <ChangePasswordModal 
      v-if="mustChangePassword && isAuthenticated"
      @updated="mustChangePassword = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useTelemetry } from '@/composables/useTelemetry'
import CyberAnimatedBackground from '@/components/hud/CyberAnimatedBackground.vue'
import MorphingLoginForm from '@/components/auth/MorphingLoginForm.vue'
import ChangePasswordModal from '@/components/auth/ChangePasswordModal.vue'
import RadialMenu from '@/components/hud/RadialMenu.vue'
import WidgetGrid from '@/components/widgets/WidgetGrid.vue'
import SettingsModal from '@/components/settings/SettingsModal.vue'

const { isAuthenticated, user, mustChangePassword, logout, authFetch } = useAuth()
const { isConnected, proxmox, nut, plugins, connect, disconnect } = useTelemetry()

const isRadialMenuOpen = ref(false)
const showSettingsModal = ref(false)
const settingsInitialTab = ref('panels')
const registeredApps = ref([])
const userPanels = ref([])
const activePanelId = ref(null)

const handleAuthenticated = () => {
  connect()
  loadInitialData()
}

const handleRadialMenuToggle = (isOpen) => {
  isRadialMenuOpen.value = isOpen
}

const handleRadialAction = (action) => {
  if (action === 'open_settings') {
    openSettings('panels')
  } else if (action === 'open_add_module') {
    openSettings('integrations')
  } else if (action === 'open_users') {
    openSettings('users')
  }
}

const openSettings = (tab = 'panels') => {
  settingsInitialTab.value = tab
  showSettingsModal.value = true
}

const handleAppsUpdated = (apps) => {
  registeredApps.value = apps
}

const loadInitialData = async () => {
  if (!isAuthenticated.value) return

  // Load apps
  try {
    const res = await authFetch('/api/apps')
    if (res.ok) {
      registeredApps.value = await res.json()
    }
  } catch (e) {
    console.error('Error fetching apps:', e)
  }

  // Load panels
  try {
    const res = await authFetch('/api/panels')
    if (res.ok) {
      userPanels.value = await res.json()
      if (userPanels.value.length > 0) {
        activePanelId.value = userPanels.value[0].id
      }
    }
  } catch (e) {
    console.error('Error fetching panels:', e)
  }
}

onMounted(() => {
  if (isAuthenticated.value) {
    connect()
    loadInitialData()
  }
})

onUnmounted(() => {
  disconnect()
})
</script>
