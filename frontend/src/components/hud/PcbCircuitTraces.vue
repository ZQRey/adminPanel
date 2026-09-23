<template>
  <svg 
    class="absolute inset-0 w-full h-full pointer-events-none z-10" 
    :viewBox="`0 0 ${width} ${height}`"
    preserveAspectRatio="xMidYMid meet"
  >
    <defs>
      <!-- Glow filter for PCB traces -->
      <filter id="pcb-glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="3" result="blur" />
        <feMerge>
          <feMergeNode in="blur" />
          <feMergeNode in="SourceGraphic" />
        </feMerge>
      </filter>

      <!-- Gradient for energy pulses -->
      <linearGradient id="pulse-grad-cyan" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#00f3ff" stop-opacity="1" />
        <stop offset="100%" stop-color="#00ff66" stop-opacity="0.8" />
      </linearGradient>
    </defs>

    <!-- Concentric Center PCB Solder Ring -->
    <circle 
      :cx="centerX" 
      :cy="centerY" 
      r="48" 
      stroke="#00f3ff" 
      stroke-width="1.5" 
      fill="none" 
      stroke-opacity="0.4"
      stroke-dasharray="4, 4" 
    />
    <circle 
      :cx="centerX" 
      :cy="centerY" 
      r="58" 
      stroke="#00ff66" 
      stroke-width="1" 
      fill="none" 
      stroke-opacity="0.25" 
    />

    <!-- Render Dynamic PCB Copper Traces to each satellite -->
    <g v-for="(satellite, index) in satellites" :key="index">
      <!-- Background Copper Track -->
      <path
        :d="satellite.pathD"
        fill="none"
        stroke="rgba(0, 243, 255, 0.25)"
        stroke-width="3"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <!-- Glowing Core Track -->
      <path
        :d="satellite.pathD"
        fill="none"
        stroke="#00f3ff"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        filter="url(#pcb-glow)"
      />

      <!-- Running Electron Energy Pulses -->
      <path
        :d="satellite.pathD"
        fill="none"
        stroke="url(#pulse-grad-cyan)"
        stroke-width="2.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="pcb-pulse-active"
        :style="{ animationDelay: `${index * 0.25}s` }"
      />

      <!-- Terminal Solder Pad (Orbital End) -->
      <circle
        :cx="satellite.x"
        :cy="satellite.y"
        r="28"
        fill="none"
        stroke="#00f3ff"
        stroke-width="1"
        stroke-opacity="0.4"
        stroke-dasharray="2, 4"
      />
      <circle
        :cx="satellite.x"
        :cy="satellite.y"
        r="6"
        fill="rgba(6, 12, 24, 0.9)"
        stroke="#00ff66"
        stroke-width="2"
      />

      <!-- Solder Joint Vias along 45°/90° elbows -->
      <circle
        v-if="satellite.elbow"
        :cx="satellite.elbow.x"
        :cy="satellite.elbow.y"
        r="3"
        fill="#00f3ff"
        opacity="0.8"
      />
    </g>
  </svg>
</template>

<script setup>
defineProps({
  width: { type: Number, default: 800 },
  height: { type: Number, default: 800 },
  centerX: { type: Number, default: 400 },
  centerY: { type: Number, default: 400 },
  satellites: { type: Array, default: () => [] }
})
</script>
