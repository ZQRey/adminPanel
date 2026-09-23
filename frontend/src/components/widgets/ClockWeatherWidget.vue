<template>
  <div class="hud-glass-panel hud-chamfer p-4 w-full h-full flex flex-col justify-between select-none">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2 mb-2">
      <div class="flex items-center space-x-2">
        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
        <span class="text-xs font-mono font-bold tracking-widest text-cyan-300">
          SYS//CHRONO & SENSORS
        </span>
      </div>
      <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-400">
        GPS-LOCKED
      </span>
    </div>

    <!-- Time & Date Readout -->
    <div class="my-2">
      <div class="text-3xl lg:text-4xl font-mono font-black tracking-wider text-cyan-300 text-glow-cyan">
        {{ currentTime }}
      </div>
      <div class="text-xs font-mono tracking-widest text-emerald-400 mt-1">
        {{ currentDate }}
      </div>
    </div>

    <!-- Sensors / Micro Weather Section -->
    <div class="mt-2 pt-2 border-t border-cyan-900/40 grid grid-cols-2 gap-2 text-xs font-mono">
      <div class="p-2 rounded bg-slate-950/60 border border-cyan-500/20">
        <div class="text-[10px] text-cyan-400/60">ZONE ATMOSPHERE</div>
        <div class="text-sm font-bold text-cyan-200 mt-0.5">22.4°C // 48% RH</div>
        <div class="text-[9px] text-emerald-400">OPTIMAL RANGE</div>
      </div>
      <div class="p-2 rounded bg-slate-950/60 border border-cyan-500/20">
        <div class="text-[10px] text-cyan-400/60">SYSTEM UPTIME</div>
        <div class="text-sm font-bold text-cyan-200 mt-0.5">{{ uptimeFormatted }}</div>
        <div class="text-[9px] text-cyan-400">ZERO CRITICAL FAULTS</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const currentTime = ref('')
const currentDate = ref('')
const uptimeSeconds = ref(120450)

let timer = null

const updateClock = () => {
  const now = new Date()
  currentTime.value = now.toTimeString().split(' ')[0]
  
  const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }
  currentDate.value = now.toLocaleDateString('en-US', options).toUpperCase()
  
  uptimeSeconds.value += 1
}

const uptimeFormatted = ref('1d 09h 27m')

onMounted(() => {
  updateClock()
  timer = setInterval(updateClock, 1000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>
