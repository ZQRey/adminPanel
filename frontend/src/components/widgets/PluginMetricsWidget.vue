<template>
  <div class="hud-glass-panel hud-chamfer p-4 w-full h-full flex flex-col justify-between select-none">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2 mb-2">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-purple-400 animate-pulse"></span>
        <span class="text-xs font-mono font-bold tracking-widest text-cyan-300">
          PYTHON MESH PROBE // PLUGIN
        </span>
      </div>
      <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-950/80 border border-purple-500/40 text-purple-300 font-bold">
        ISOLATED SUBPROCESS
      </span>
    </div>

    <!-- Dynamic Metrics Display -->
    <div v-if="hasData" class="space-y-2 my-1 text-xs font-mono">
      <div v-for="(pluginData, pluginName) in plugins" :key="pluginName" class="space-y-1.5">
        <div class="flex items-center justify-between text-[11px] text-purple-300 font-bold">
          <span>{{ pluginName.toUpperCase() }}</span>
          <span class="text-emerald-400 text-[10px]">
            {{ pluginData?.status || 'ACTIVE' }}
          </span>
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div class="p-2 rounded bg-slate-950/60 border border-purple-500/20">
            <div class="text-[9px] text-cyan-400/60">PLATFORM / ARCH</div>
            <div class="text-xs font-bold text-cyan-100 truncate mt-0.5">
              {{ pluginData?.platform || 'HOST' }}
            </div>
          </div>
          <div class="p-2 rounded bg-slate-950/60 border border-purple-500/20">
            <div class="text-[9px] text-cyan-400/60">QUANTUM ENTROPY</div>
            <div class="text-xs font-bold text-emerald-400 mt-0.5">
              {{ pluginData?.quantum_entropy || 98.4 }}%
            </div>
          </div>
        </div>

        <div class="p-1.5 rounded bg-slate-950/40 border border-cyan-500/10 flex items-center justify-between text-[10px]">
          <span class="text-cyan-400/70">PROBE LATENCY:</span>
          <span class="text-cyan-200 font-bold">
            {{ pluginData?.probe_duration_ms || 3.4 }} ms
          </span>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-4 text-xs font-mono text-cyan-500/50">
      WAITING FOR PYTHON PLUGIN TELEMETRY STREAM...
    </div>

    <!-- Footer -->
    <div class="mt-1 pt-2 border-t border-cyan-900/40 flex items-center justify-between text-[10px] font-mono text-cyan-500/60">
      <span>DIR: backend/plugins/*.py</span>
      <span>TIMEOUT: 4.0s STRICT</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  plugins: {
    type: Object,
    default: () => ({})
  }
})

const hasData = computed(() => {
  return props.plugins && Object.keys(props.plugins).length > 0
})
</script>
