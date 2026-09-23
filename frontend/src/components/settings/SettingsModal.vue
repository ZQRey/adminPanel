<template>
  <div class="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
    <div class="hud-glass-panel hud-chamfer-lg w-full max-w-4xl h-[85vh] flex flex-col overflow-hidden border border-cyan-400 shadow-[0_0_40px_rgba(0,243,255,0.4)]">
      <!-- Modal Header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-cyan-500/30 bg-slate-950/70">
        <div class="flex items-center space-x-3">
          <div class="w-3 h-3 rounded-full bg-cyan-400 animate-ping"></div>
          <span class="text-sm font-mono font-bold tracking-widest text-cyan-200">
            SYSTEM CONTROL CONSOLE // SETTINGS & ADMINISTRATION
          </span>
        </div>
        <button 
          @click="$emit('close')"
          class="text-cyan-400/80 hover:text-white px-2 py-1 rounded hover:bg-cyan-900/40 font-mono text-sm"
        >
          ✕ CLOSE [ESC]
        </button>
      </div>

      <!-- Navigation Tabs Bar -->
      <div class="flex items-center space-x-2 px-6 py-2.5 bg-slate-950/90 border-b border-cyan-500/20 overflow-x-auto">
        <button
          v-for="tab in availableTabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          class="px-3.5 py-1.5 rounded font-mono text-xs font-bold transition-all flex items-center space-x-2 whitespace-nowrap"
          :class="activeTab === tab.id ? 'bg-cyan-950 text-cyan-300 border border-cyan-400 shadow-[0_0_12px_rgba(0,243,255,0.4)]' : 'text-cyan-500/70 hover:text-cyan-300 hover:bg-slate-900'"
        >
          <span>{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
        </button>
      </div>

      <!-- Tab Content Area -->
      <div class="flex-1 p-6 overflow-y-auto bg-slate-950/40">
        <UserManagementTab v-if="activeTab === 'users'" />
        <PanelManagementTab v-else-if="activeTab === 'panels'" />
        <IntegrationTab v-else-if="activeTab === 'integrations'" />
        <AppBookmarksTab v-else-if="activeTab === 'apps'" @apps-updated="$emit('apps-updated', $event)" />
        <PluginsTab v-else-if="activeTab === 'plugins'" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import UserManagementTab from './UserManagementTab.vue'
import PanelManagementTab from './PanelManagementTab.vue'
import IntegrationTab from './IntegrationTab.vue'
import AppBookmarksTab from './AppBookmarksTab.vue'
import PluginsTab from './PluginsTab.vue'

const props = defineProps({
  initialTab: { type: String, default: 'panels' }
})

defineEmits(['close', 'apps-updated'])

const { isAdmin, canManageIntegrations, canManageApps, canManagePanels } = useAuth()
const activeTab = ref(props.initialTab)

const allTabs = [
  { id: 'panels', label: 'Панели Дашборда', icon: '◫', requiredPerm: canManagePanels },
  { id: 'apps', label: 'Приложения & Компановка', icon: '📁', requiredPerm: canManageApps },
  { id: 'integrations', label: 'Интеграции (Proxy)', icon: '🔒', requiredPerm: canManageIntegrations },
  { id: 'plugins', label: 'Python Плагины', icon: '🐍', requiredPerm: isAdmin },
  { id: 'users', label: 'Пользователи & Права', icon: '👥', requiredPerm: isAdmin }
]

const availableTabs = computed(() => {
  return allTabs.filter(t => t.requiredPerm.value !== false)
})
</script>
