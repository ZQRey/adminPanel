<template>
  <div class="hud-glass-panel hud-chamfer p-4 w-full h-full flex flex-col justify-between select-none">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2 mb-2">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
        <span class="text-xs font-mono font-bold tracking-widest text-cyan-300">
          NUT // POWER MATRIX
        </span>
      </div>
      <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 font-bold">
        {{ data?.status || 'OL (ONLINE)' }}
      </span>
    </div>

    <!-- Battery & Load Telemetry -->
    <div class="grid grid-cols-2 gap-3 my-2">
      <!-- Battery Gauge -->
      <div class="p-2.5 rounded bg-slate-950/60 border border-cyan-500/20 flex flex-col items-center">
        <div class="text-[10px] font-mono text-cyan-400/70">BATTERY CHARGE</div>
        <div class="text-2xl font-mono font-black text-emerald-400 text-glow-emerald mt-1">
          {{ data?.battery_charge_pct ?? 100 }}%
        </div>
        <div class="text-[10px] font-mono text-cyan-400/80 mt-1">
          RUNTIME: {{ data?.battery_runtime_min ?? 52 }} MIN
        </div>
        <div class="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-2 border border-emerald-500/30">
          <div 
            class="h-full bg-emerald-400 transition-all duration-500" 
            :style="{ width: `${data?.battery_charge_pct ?? 100}%` }"
          ></div>
        </div>
      </div>

      <!-- UPS Load Gauge -->
      <div class="p-2.5 rounded bg-slate-950/60 border border-cyan-500/20 flex flex-col items-center">
        <div class="text-[10px] font-mono text-cyan-400/70">UPS LOAD</div>
        <div class="text-2xl font-mono font-black text-amber-400 text-glow-amber mt-1">
          {{ data?.ups_load_pct ?? 0 }}%
        </div>
        <div class="text-[10px] font-mono text-amber-400/80 mt-1">
          OUTPUT: ~{{ data?.wattage ?? 216 }} W
        </div>
        <div class="w-full bg-slate-900 h-1.5 rounded-full overflow-hidden mt-2 border border-amber-500/30">
          <div 
            class="h-full bg-amber-400 transition-all duration-500" 
            :style="{ width: `${data?.ups_load_pct ?? 0}%` }"
          ></div>
        </div>
      </div>
    </div>

    <!-- Footer Model & AC Voltage -->
    <div class="mt-1 pt-2 border-t border-cyan-900/40 flex items-center justify-between text-[11px] font-mono">
      <div class="text-cyan-400/80 truncate max-w-[60%]">
        {{ data?.ups_model || 'APC SMART-UPS' }}
      </div>
      <div class="text-cyan-300 font-bold">
        INPUT: {{ data?.input_voltage ?? 230 }} V
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
