<template>
  <div class="hud-glass-panel hud-chamfer p-4 w-full h-full flex flex-col justify-between select-none">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2 mb-2">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
        <span class="text-xs font-mono font-bold tracking-widest text-cyan-300">
          PROXMOX VE // CLUSTER
        </span>
      </div>
      <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-400">
        {{ data?.node ? data.node.toUpperCase() : 'NODE-01' }}
      </span>
    </div>

    <!-- Telemetry Gauges Grid -->
    <div class="grid grid-cols-3 gap-2 my-2 text-center">
      <!-- CPU -->
      <div class="p-2 rounded bg-slate-950/60 border border-cyan-500/20 flex flex-col items-center">
        <span class="text-[10px] font-mono text-cyan-400/70">CPU LOAD</span>
        <span class="text-lg font-mono font-bold text-cyan-300 text-glow-cyan mt-1">
          {{ data?.cpu_pct ?? 0 }}%
        </span>
        <div class="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-1.5 border border-cyan-500/30">
          <div 
            class="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500" 
            :style="{ width: `${data?.cpu_pct ?? 0}%` }"
          ></div>
        </div>
      </div>

      <!-- RAM -->
      <div class="p-2 rounded bg-slate-950/60 border border-cyan-500/20 flex flex-col items-center">
        <span class="text-[10px] font-mono text-cyan-400/70">RAM USAGE</span>
        <span class="text-lg font-mono font-bold text-cyan-300 text-glow-cyan mt-1">
          {{ data?.mem_pct ?? 0 }}%
        </span>
        <div class="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-1.5 border border-cyan-500/30">
          <div 
            class="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500" 
            :style="{ width: `${data?.mem_pct ?? 0}%` }"
          ></div>
        </div>
      </div>

      <!-- DISK -->
      <div class="p-2 rounded bg-slate-950/60 border border-cyan-500/20 flex flex-col items-center">
        <span class="text-[10px] font-mono text-cyan-400/70">ROOTFS</span>
        <span class="text-lg font-mono font-bold text-cyan-300 text-glow-cyan mt-1">
          {{ data?.disk_pct ?? 0 }}%
        </span>
        <div class="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-1.5 border border-cyan-500/30">
          <div 
            class="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 transition-all duration-500" 
            :style="{ width: `${data?.disk_pct ?? 0}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Active VMs & Uptime Footer -->
    <div class="mt-1 pt-2 border-t border-cyan-900/40 flex items-center justify-between text-[11px] font-mono">
      <div class="flex items-center space-x-2">
        <span class="text-cyan-400">VM/LXC RUNNING:</span>
        <span class="font-bold text-emerald-400 text-glow-emerald">
          {{ data?.vms_running ?? 0 }} / {{ data?.vms_total ?? 8 }} ACTIVE
        </span>
      </div>
      <div class="text-cyan-500/70 text-[10px]">
        PROXY: FASTAPI // WS
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  data: {
    type: Object,
    default: () => ({})
  }
})
</script>
