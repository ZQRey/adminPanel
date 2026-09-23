<template>
  <div class="flex flex-col items-center justify-center p-6 select-none">
    <!-- Schematic Neon Vector HUD Robot Glyph -->
    <svg 
      class="w-32 h-32 text-cyan-400 drop-shadow-[0_0_20px_rgba(0,243,255,0.8)] animate-pulse" 
      viewBox="0 0 120 120" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
    >
      <!-- Cyber Antennas with Nodes -->
      <path d="M 60 25 L 60 10" stroke="#00f3ff" stroke-width="3" stroke-linecap="round" />
      <circle cx="60" cy="8" r="4" fill="#ffffff" stroke="#00f3ff" stroke-width="2" />
      
      <path d="M 40 28 L 30 15" stroke="#00f3ff" stroke-width="2" stroke-linecap="round" />
      <circle cx="28" cy="13" r="3" fill="#00ff66" />
      
      <path d="M 80 28 L 90 15" stroke="#00f3ff" stroke-width="2" stroke-linecap="round" />
      <circle cx="92" cy="13" r="3" fill="#00ff66" />

      <!-- Outer Hex/Octagonal Chassis -->
      <polygon 
        points="30,28 90,28 106,55 98,92 60,105 22,92 14,55" 
        stroke="#00f3ff" 
        stroke-width="3" 
        fill="rgba(6, 12, 24, 0.9)" 
        stroke-linejoin="round"
      />
      
      <!-- Inner Visor Frame -->
      <rect 
        x="26" 
        y="42" 
        width="68" 
        height="36" 
        rx="6" 
        fill="rgba(0, 243, 255, 0.08)" 
        stroke="#00f3ff" 
        stroke-width="2" 
      />

      <!-- Vector Schematic ^_^ Eye Glyph -->
      <!-- Left Eye ^ -->
      <path 
        d="M 36 64 L 46 50 L 54 64" 
        stroke="#ffffff" 
        stroke-width="3.5" 
        stroke-linecap="round" 
        stroke-linejoin="round" 
      />
      <!-- Right Eye ^ -->
      <path 
        d="M 66 64 L 74 50 L 84 64" 
        stroke="#ffffff" 
        stroke-width="3.5" 
        stroke-linecap="round" 
        stroke-linejoin="round" 
      />
      <!-- Cyber Smile _ -->
      <path 
        d="M 52 72 L 68 72" 
        stroke="#00ff66" 
        stroke-width="3" 
        stroke-linecap="round" 
      />

      <!-- Ear Transceivers -->
      <rect x="9" y="48" width="5" height="18" rx="2" fill="#00f3ff" />
      <rect x="106" y="48" width="5" height="18" rx="2" fill="#00f3ff" />

      <!-- PCB circuit marks on cheek -->
      <path d="M 30 84 L 42 84 L 46 90" stroke="#00f3ff" stroke-width="1.5" stroke-linecap="round" />
      <circle cx="46" cy="90" r="1.5" fill="#00ff66" />
      <path d="M 90 84 L 78 84 L 74 90" stroke="#00f3ff" stroke-width="1.5" stroke-linecap="round" />
      <circle cx="74" cy="90" r="1.5" fill="#00ff66" />
    </svg>

    <div class="mt-4 text-center">
      <div class="text-sm font-mono tracking-widest text-emerald-400 text-glow-emerald">
        [ AUTHENTICATION VERIFIED ]
      </div>
      <div class="text-xs font-mono text-cyan-300/70 tracking-wider mt-1 animate-pulse">
        ACCESS GRANTED // INITIALIZING HUD CONSOLE...
      </div>
    </div>
  </div>
</template>

<script setup>
// Pure schematic vector HUD robot glyph ^_^
</script>
