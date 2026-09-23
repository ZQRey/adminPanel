<template>
  <div class="relative w-full max-w-md mx-auto py-6 px-4 z-20 flex flex-col items-center">
    <!-- Center Hub Button at Top -->
    <div 
      @click="$emit('toggle')"
      class="cursor-pointer relative z-30 flex items-center space-x-3 px-5 py-3 rounded-full bg-slate-950/90 border border-cyan-400 shadow-[0_0_20px_rgba(0,243,255,0.4)] hover:scale-105 active:scale-95 transition-all"
    >
      <div class="w-8 h-8 rounded-full bg-cyan-950 border border-cyan-300 flex items-center justify-center text-cyan-300 animate-spin" style="animation-duration: 10s;">
        ⚙
      </div>
      <div>
        <div class="text-xs font-mono font-bold tracking-widest text-cyan-300">
          CENTRAL BUS // {{ isOpen ? 'COLLAPSE' : 'EXPAND' }}
        </div>
        <div class="text-[10px] font-mono text-emerald-400">
          [ 90° ORTHOGONAL PCB TRUNK ]
        </div>
      </div>
    </div>

    <!-- Vertical PCB Bus line with branches -->
    <div v-if="isOpen" class="relative w-full mt-4 flex flex-col items-center">
      <!-- Central vertical copper spine -->
      <div class="absolute top-0 bottom-0 w-1 bg-gradient-to-b from-cyan-400 via-emerald-400 to-cyan-400 shadow-[0_0_10px_#00f3ff]"></div>

      <div class="w-full space-y-4 pt-4">
        <div 
          v-for="(item, idx) in items" 
          :key="idx"
          class="relative flex items-center"
          :class="idx % 2 === 0 ? 'justify-start pl-4' : 'justify-end pr-4'"
        >
          <!-- Horizontal 90° PCB Branch Line connecting center spine to node -->
          <div 
            class="absolute top-1/2 h-0.5 bg-cyan-400 shadow-[0_0_8px_#00f3ff]"
            :style="{
              left: idx % 2 === 0 ? 'calc(50% - 2px)' : 'auto',
              right: idx % 2 === 1 ? 'calc(50% - 2px)' : 'auto',
              width: 'calc(50% - 20px)'
            }"
          ></div>

          <!-- Solder pad at junction -->
          <div class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-emerald-400 border border-slate-950 shadow-[0_0_8px_#00ff66] z-10"></div>

          <!-- Satellite Card Button -->
          <button
            @click="$emit('select-item', item)"
            class="relative z-20 w-[42%] hud-glass-panel p-3 rounded text-left border border-cyan-500/50 hover:border-cyan-300 hover:scale-105 active:scale-95 transition-all duration-200 group"
          >
            <div class="flex items-center space-x-2">
              <span class="text-cyan-400 group-hover:text-emerald-400 text-sm">▶</span>
              <span class="text-xs font-mono font-bold tracking-wider text-cyan-200 group-hover:text-cyan-100 truncate">
                {{ item.label }}
              </span>
            </div>
            <div v-if="item.sub" class="text-[10px] font-mono text-cyan-500/70 truncate mt-0.5">
              {{ item.sub }}
            </div>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  isOpen: { type: Boolean, default: true },
  items: { type: Array, default: () => [] }
})

defineEmits(['toggle', 'select-item'])
</script>
