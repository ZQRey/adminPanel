<template>
  <div class="relative flex items-center justify-center select-none">
    <!-- Responsive Switch: Desktop 360° Radial vs Mobile Vertical Bus Fallback -->
    <div v-if="isMobileView" class="w-full">
      <VerticalBusFallback 
        :is-open="isOpen"
        :items="allMenuItems"
        @toggle="toggleMenu"
        @select-item="handleItemClick"
      />
    </div>

    <!-- Desktop 360° Radial Menu -->
    <div 
      v-else
      class="relative w-[650px] h-[650px] lg:w-[750px] lg:h-[750px] flex items-center justify-center"
    >
      <!-- Dynamic PCB Circuit Traces SVG Layer -->
      <PcbCircuitTraces 
        v-if="isOpen"
        :width="svgSize"
        :height="svgSize"
        :center-x="centerCoord"
        :center-y="centerCoord"
        :satellites="satelliteRoutes"
      />

      <!-- Center Node Button (360° Spin on Click) -->
      <div
        ref="centerBtnRef"
        @click="handleCenterButtonClick"
        class="relative z-30 w-28 h-28 lg:w-32 lg:h-32 rounded-full cursor-pointer flex flex-col items-center justify-center transition-transform hover:scale-105 active:scale-95 group"
      >
        <!-- Concentric Cyber Glow Rings -->
        <div 
          class="absolute inset-0 rounded-full border-2 border-cyan-400 shadow-[0_0_30px_rgba(0,243,255,0.6)] group-hover:border-emerald-400 group-hover:shadow-[0_0_35px_rgba(0,255,102,0.6)] transition-colors"
        ></div>
        <div class="absolute inset-1.5 rounded-full border border-dashed border-cyan-300/40 animate-spin" style="animation-duration: 25s;"></div>
        <div class="absolute inset-3 rounded-full bg-slate-950/90 backdrop-blur-md flex flex-col items-center justify-center p-2 text-center">
          
          <!-- When inside a group: show Back indicator in center -->
          <template v-if="activeGroup && isOpen">
            <div class="w-8 h-8 rounded-full bg-purple-950 border border-purple-400 flex items-center justify-center text-purple-300 shadow-[0_0_10px_#a855f7]">
              ◀
            </div>
            <span class="mt-1 text-[9px] font-mono font-bold tracking-wider text-purple-200 truncate max-w-full">
              {{ activeGroup.name }}
            </span>
            <span class="text-[8px] font-mono text-emerald-400">
              [ НАЗАД ]
            </span>
          </template>

          <!-- Normal Root state -->
          <template v-else>
            <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-400/80 flex items-center justify-center text-cyan-300 shadow-[0_0_10px_#00f3ff]">
              <svg class="w-5 h-5 transition-transform duration-500" :class="{ 'rotate-180 text-emerald-400': isOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
              </svg>
            </div>
            <span class="mt-1 text-[10px] font-mono font-bold tracking-wider text-cyan-300 text-glow-cyan">
              {{ isOpen ? 'SYSTEM' : 'CORE' }}
            </span>
            <span class="text-[8px] font-mono text-emerald-400">
              {{ isOpen ? 'OPEN' : 'STANDBY' }}
            </span>
          </template>

        </div>
      </div>

      <!-- Orbital Satellite Buttons (Displayed around 360° orbit) -->
      <div 
        v-if="isOpen"
        class="absolute inset-0 pointer-events-none z-20"
      >
        <div
          v-for="(sat, idx) in satelliteRoutes"
          :key="idx"
          class="absolute pointer-events-auto transform -translate-x-1/2 -translate-y-1/2 transition-all duration-300"
          :style="{ left: `${(sat.x / svgSize) * 100}%`, top: `${(sat.y / svgSize) * 100}%` }"
        >
          <button
            @click="handleItemClick(sat.item)"
            class="group relative flex flex-col items-center justify-center p-3 rounded-lg hud-glass-panel hud-chamfer hover:scale-110 active:scale-95 transition-all duration-200 border shadow-[0_0_15px_rgba(0,243,255,0.3)] w-28 lg:w-32 text-center"
            :class="[
              sat.item.isGroup 
                ? 'border-purple-400/80 hover:border-purple-300 hover:shadow-[0_0_25px_rgba(168,85,247,0.6)]' 
                : sat.item.isBack
                ? 'border-amber-400/80 hover:border-amber-300 hover:shadow-[0_0_25px_rgba(255,170,0,0.6)]'
                : 'border-cyan-400/50 hover:border-emerald-400 hover:shadow-[0_0_25px_rgba(0,255,102,0.5)]'
            ]"
          >
            <!-- Glowing Orbit Icon -->
            <div 
              class="w-8 h-8 rounded-full border flex items-center justify-center mb-1 transition-colors"
              :class="sat.item.isGroup ? 'border-purple-400' : sat.item.isBack ? 'border-amber-400' : 'border-cyan-400 group-hover:border-emerald-400'"
              :style="{ backgroundColor: sat.item.color ? `${sat.item.color}25` : 'rgba(0,243,255,0.1)' }"
            >
              <span 
                class="text-xs font-mono"
                :class="sat.item.isGroup ? 'text-purple-300' : sat.item.isBack ? 'text-amber-300' : 'text-cyan-300 group-hover:text-emerald-300'"
              >
                {{ sat.item.iconSymbol || '⬡' }}
              </span>
            </div>

            <!-- Label -->
            <span class="text-[11px] font-mono font-bold tracking-wider text-cyan-200 group-hover:text-white truncate max-w-full">
              {{ sat.item.label }}
            </span>
            <span v-if="sat.item.sub" class="text-[9px] font-mono text-cyan-400/60 truncate max-w-full">
              {{ sat.item.sub }}
            </span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import gsap from 'gsap'
import PcbCircuitTraces from './PcbCircuitTraces.vue'
import VerticalBusFallback from './VerticalBusFallback.vue'
import { generatePcbTracePath, calculateOrbitPositions } from '@/composables/usePcbTraces'
import { useGrouping } from '@/composables/useGrouping'

const props = defineProps({
  apps: { type: Array, default: () => [] }
})

const emit = defineEmits(['menu-toggled', 'action'])

const { isGroupingEnabled, groups } = useGrouping()

const isOpen = ref(false)
const centerBtnRef = ref(null)
const isMobileView = ref(false)
const activeGroup = ref(null) // null = root view, or { id, name, icon, ... }

const svgSize = 800
const centerCoord = 400
const orbitRadius = 260

const checkViewport = () => {
  isMobileView.value = window.innerWidth < 768
}

onMounted(() => {
  checkViewport()
  window.addEventListener('resize', checkViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkViewport)
})

// Requirement 3: Users button REMOVED from default radial menu items
const rootDefaultItems = [
  { id: 'settings', label: 'Настройка панели', sub: 'Dash Config', action: 'open_settings', iconSymbol: '⚙' },
  { id: 'add_item', label: 'Добавить модуль', sub: 'Add Int/App', action: 'open_add_module', iconSymbol: '＋' }
]

// Dynamic calculation of orbital menu items (supporting Grouping Mode)
const allMenuItems = computed(() => {
  // 1. IF GROUPING IS ENABLED:
  if (isGroupingEnabled.value) {
    // If inside a specific group: show member apps + Back button
    if (activeGroup.value) {
      const groupApps = props.apps
        .filter(a => (a.group_name || 'Инфраструктура') === activeGroup.value.name)
        .map(app => ({
          id: `app_${app.id}`,
          label: app.title,
          sub: app.description || 'External Link',
          url: app.url,
          target: app.target || '_blank',
          action: 'open_app',
          iconSymbol: app.icon === 'server' ? '🖥' : app.icon === 'activity' ? '📈' : app.icon === 'shield' ? '🛡' : '⚡',
          color: app.color || activeGroup.value.color || '#00f3ff'
        }))

      const backItem = {
        id: 'back_btn',
        label: '◀ НАЗАД',
        sub: 'В меню групп',
        action: 'back_to_root',
        iconSymbol: '↩',
        isBack: true,
        color: '#ffaa00'
      }

      return [backItem, ...groupApps]
    }

    // Root level in grouping mode: show default actions + Group orbital nodes
    const groupNodes = groups.value.map(grp => {
      const count = props.apps.filter(a => (a.group_name || 'Инфраструктура') === grp.name).length
      return {
        id: `grp_${grp.id}`,
        label: grp.name,
        sub: `${count} элементов`,
        group: grp,
        action: 'enter_group',
        iconSymbol: grp.icon || '📁',
        isGroup: true,
        color: grp.color || '#a855f7'
      }
    })

    return [...rootDefaultItems, ...groupNodes]
  }

  // 2. IF GROUPING IS DISABLED: flat list of all apps
  const flatApps = props.apps.map(app => ({
    id: `app_${app.id}`,
    label: app.title,
    sub: app.description || 'External Link',
    url: app.url,
    target: app.target || '_blank',
    action: 'open_app',
    iconSymbol: app.icon === 'server' ? '🖥' : app.icon === 'activity' ? '📈' : app.icon === 'shield' ? '🛡' : '⚡',
    color: app.color || '#00f3ff'
  }))

  return [...rootDefaultItems, ...flatApps]
})

// Satellite routes with authentic 45-degree PCB trace paths
const satelliteRoutes = computed(() => {
  const items = allMenuItems.value
  const positions = calculateOrbitPositions(items.length, orbitRadius, centerCoord, centerCoord)
  
  return items.map((item, idx) => {
    const pos = positions[idx]
    const pathD = generatePcbTracePath(centerCoord, centerCoord, pos.x, pos.y, '45deg')
    return {
      item,
      x: pos.x,
      y: pos.y,
      pathD
    }
  })
})

const spinCenterButton = () => {
  if (centerBtnRef.value) {
    gsap.to(centerBtnRef.value, {
      rotation: '+=360',
      duration: 0.55,
      ease: 'power2.inOut'
    })
  }
}

const handleCenterButtonClick = () => {
  if (activeGroup.value && isOpen.value) {
    // If inside a group and clicking center, return to root
    spinCenterButton()
    activeGroup.value = null
  } else {
    toggleMenu()
  }
}

const toggleMenu = () => {
  isOpen.value = !isOpen.value
  activeGroup.value = null // reset to root when toggling
  spinCenterButton()
  emit('menu-toggled', isOpen.value)
}

const handleItemClick = (item) => {
  if (item.action === 'enter_group') {
    spinCenterButton()
    activeGroup.value = item.group
  } else if (item.action === 'back_to_root') {
    spinCenterButton()
    activeGroup.value = null
  } else if (item.action === 'open_app' && item.url) {
    window.open(item.url, item.target || '_blank')
  } else {
    emit('action', item.action)
  }
}
</script>
