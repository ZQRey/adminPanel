<template>
  <div 
    class="w-full h-full pointer-events-none transition-all duration-500"
    :class="[
      isMenuOpen 
        ? 'opacity-25 filter blur-[4px] scale-[0.98]' 
        : 'opacity-100 filter blur-0 scale-100'
    ]"
  >
    <!-- Peripheral HUD Layout Container (Left & Right Flanks) -->
    <div class="max-w-7xl mx-auto h-full px-4 py-6 flex flex-col justify-between">
      <!-- Main Columns Flanking the Center -->
      <div class="grid grid-cols-1 md:grid-cols-12 gap-6 h-full items-center">
        <!-- Left Flank Widgets (Col 1-3) -->
        <div class="md:col-span-3 space-y-6 pointer-events-auto">
          <ClockWeatherWidget />
          <PluginMetricsWidget :plugins="plugins" />
        </div>

        <!-- Center Void (Col 4-9) - Reserved for Radial Menu & PCB Traces -->
        <div class="md:col-span-6 hidden md:block"></div>

        <!-- Right Flank Widgets (Col 10-12) -->
        <div class="md:col-span-3 space-y-6 pointer-events-auto">
          <ProxmoxWidget :data="proxmox" />
          <NutUpsWidget :data="nut" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import ClockWeatherWidget from './ClockWeatherWidget.vue'
import ProxmoxWidget from './ProxmoxWidget.vue'
import NutUpsWidget from './NutUpsWidget.vue'
import PluginMetricsWidget from './PluginMetricsWidget.vue'

defineProps({
  isMenuOpen: { type: Boolean, default: false },
  proxmox: { type: Object, default: () => ({}) },
  nut: { type: Object, default: () => ({}) },
  plugins: { type: Object, default: () => ({}) }
})
</script>
