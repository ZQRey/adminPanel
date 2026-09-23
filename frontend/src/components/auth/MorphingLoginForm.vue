<template>
  <div class="relative flex items-center justify-center min-h-screen">
    <!-- Perimeter Flash Container -->
    <PerimeterFlash ref="perimeterRef" />

    <!-- Central Morphing Container -->
    <div
      ref="containerRef"
      class="relative z-20 flex flex-col items-center justify-center transition-shadow select-none overflow-hidden"
      :class="[
        isExpanded 
          ? 'hud-glass-panel hud-chamfer-lg p-8 w-[380px] sm:w-[420px] max-w-[95vw]' 
          : 'w-48 h-48 sm:w-56 sm:h-56 rounded-full cursor-pointer hover:scale-105 active:scale-95'
      ]"
      @click="handleContainerClick"
    >
      <!-- STATE 1: Pulsing Central Circular Button (Unexpanded) -->
      <div 
        v-if="!isExpanded"
        class="relative w-full h-full flex flex-col items-center justify-center"
      >
        <!-- Concentric Rotating Cyber Rings -->
        <div class="absolute inset-0 rounded-full border-2 border-cyan-400/40 animate-spin" style="animation-duration: 20s;"></div>
        <div class="absolute inset-2 rounded-full border border-dashed border-emerald-400/50 animate-spin" style="animation-duration: 12s; animation-direction: reverse;"></div>
        <div class="absolute inset-6 rounded-full border border-cyan-300/30"></div>
        <div class="absolute inset-0 rounded-full bg-cyan-500/10 backdrop-blur-md shadow-[0_0_35px_rgba(0,243,255,0.4)]"></div>

        <!-- Center Node Icon & Text -->
        <div class="relative z-10 flex flex-col items-center text-center p-3">
          <div class="w-12 h-12 rounded-full bg-cyan-950/80 border border-cyan-400 flex items-center justify-center shadow-[0_0_15px_#00f3ff]">
            <svg class="w-6 h-6 text-cyan-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3" />
              <path d="M12 2v3m0 14v3M2 12h3m14 0h3m-3.5-6.5l-2.1 2.1m-8.8 8.8l-2.1 2.1m0-13l2.1 2.1m8.8 8.8l2.1 2.1" />
            </svg>
          </div>
          <span class="mt-2 text-xs font-mono font-bold tracking-widest text-cyan-300 text-glow-cyan">
            CYBER CORE
          </span>
          <span class="text-[10px] font-mono tracking-wider text-emerald-400/80 animate-pulse">
            [ CLICK TO ENTER ]
          </span>
        </div>
      </div>

      <!-- STATE 2: Morphing Login Form -->
      <div 
        v-else-if="!isSuccess"
        ref="formContentRef" 
        class="w-full opacity-0"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-3 mb-4">
          <div class="flex items-center space-x-2">
            <div class="w-2.5 h-2.5 bg-cyan-400 rounded-full animate-ping"></div>
            <span class="font-mono text-xs tracking-widest text-cyan-300 font-bold">
              SYS//AUTH PORTAL
            </span>
          </div>
          <div class="flex items-center space-x-2">
            <span class="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/40 text-cyan-400">
              AD // LOCAL
            </span>
            <button 
              @click.stop="collapseForm"
              class="text-cyan-400/60 hover:text-cyan-200 text-sm font-mono px-1.5 py-0.5 rounded hover:bg-cyan-900/40"
              title="Close form"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- Feedback error readout if any -->
        <div 
          v-if="errorMessage" 
          class="mb-4 p-2.5 rounded bg-red-950/50 border border-red-500/60 text-red-300 font-mono text-xs flex items-center space-x-2 animate-shake"
        >
          <span class="text-red-400 font-bold">⚠</span>
          <span class="truncate">{{ errorMessage }}</span>
        </div>

        <!-- Input Fields -->
        <form @submit.prevent="handleLoginSubmit" class="space-y-4">
          <div>
            <label class="block text-[11px] font-mono tracking-widest text-cyan-300/80 mb-1">
              OPERATOR ID / USERNAME:
            </label>
            <div class="relative">
              <input 
                ref="usernameInputRef"
                v-model="username" 
                type="text" 
                required 
                placeholder="admin or ad_user"
                class="w-full bg-slate-950/80 border border-cyan-500/40 rounded px-3 py-2 text-cyan-100 font-mono text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 shadow-inner"
              />
              <span class="absolute right-2.5 top-2.5 text-cyan-500/40 text-xs font-mono">USR</span>
            </div>
          </div>

          <div>
            <label class="block text-[11px] font-mono tracking-widest text-cyan-300/80 mb-1">
              SECURITY KEY / PASSWORD:
            </label>
            <div class="relative">
              <input 
                v-model="password" 
                :type="showPassword ? 'text' : 'password'" 
                required 
                placeholder="••••••••••••"
                class="w-full bg-slate-950/80 border border-cyan-500/40 rounded px-3 py-2 text-cyan-100 font-mono text-sm focus:outline-none focus:border-cyan-400 focus:ring-1 focus:ring-cyan-400 shadow-inner"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword"
                class="absolute right-2.5 top-2 text-cyan-400/60 hover:text-cyan-200 text-xs font-mono"
              >
                {{ showPassword ? 'HIDE' : 'SHOW' }}
              </button>
            </div>
          </div>

          <!-- Submit Button -->
          <button 
            type="submit" 
            :disabled="isLoading"
            class="w-full mt-2 relative group overflow-hidden bg-cyan-950/80 hover:bg-cyan-900 border border-cyan-400/80 hover:border-cyan-300 text-cyan-300 font-mono font-bold tracking-widest py-2.5 px-4 rounded shadow-[0_0_15px_rgba(0,243,255,0.3)] transition-all duration-200 flex items-center justify-center space-x-2"
          >
            <div class="absolute inset-0 w-1/3 h-full bg-gradient-to-r from-transparent via-cyan-400/20 to-transparent -skew-x-12 -translate-x-full group-hover:translate-x-[400%] transition-transform duration-1000"></div>
            <span v-if="isLoading" class="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></span>
            <span>{{ isLoading ? 'AUTHENTICATING...' : 'INITIATE SESSION' }}</span>
          </button>
        </form>

        <div class="mt-4 pt-3 border-t border-cyan-900/40 flex items-center justify-between text-[10px] font-mono text-cyan-500/60">
          <span>PRIORITY: AD LDAP > LOCAL</span>
          <span>DEFAULT: admin / admin123</span>
        </div>
      </div>

      <!-- STATE 3: Success Vector Glyph Segue -->
      <div v-else class="w-full flex items-center justify-center animate-fade-in">
        <CyberRobotGlyph />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import gsap from 'gsap'
import { useAuth } from '@/composables/useAuth'
import PerimeterFlash from './PerimeterFlash.vue'
import CyberRobotGlyph from './CyberRobotGlyph.vue'

const emit = defineEmits(['authenticated'])

const { login } = useAuth()

const isExpanded = ref(false)
const isLoading = ref(false)
const isSuccess = ref(false)
const showPassword = ref(false)
const username = ref('admin')
const password = ref('admin123')
const errorMessage = ref('')

const containerRef = ref(null)
const formContentRef = ref(null)
const perimeterRef = ref(null)
const usernameInputRef = ref(null)

const handleContainerClick = () => {
  if (!isExpanded.value) {
    expandForm()
  }
}

const expandForm = () => {
  isExpanded.value = true
  errorMessage.value = ''
  
  nextTick(() => {
    // GSAP fast morph animation (< 600ms requirement)
    if (containerRef.value && formContentRef.value) {
      gsap.fromTo(
        containerRef.value,
        { scale: 0.85, opacity: 0.8 },
        { scale: 1, opacity: 1, duration: 0.45, ease: 'power2.out' }
      )
      gsap.to(formContentRef.value, {
        opacity: 1,
        duration: 0.35,
        delay: 0.1,
        ease: 'power1.out',
        onComplete: () => {
          usernameInputRef.value?.focus()
        }
      })
    }
  })
}

const collapseForm = () => {
  if (formContentRef.value && containerRef.value) {
    gsap.to(formContentRef.value, {
      opacity: 0,
      duration: 0.2,
      onComplete: () => {
        isExpanded.value = false
        nextTick(() => {
          gsap.fromTo(
            containerRef.value,
            { scale: 1.1 },
            { scale: 1, duration: 0.35, ease: 'back.out(1.5)' }
          )
        })
      }
    })
  } else {
    isExpanded.value = false
  }
}

const handleLoginSubmit = async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    await login(username.value, password.value)

    // Requirements:
    // Success: 300-400ms white perimeter pulse, then form morphs in ~500ms into robot glyph ^_^, then segue to dashboard
    if (perimeterRef.value) {
      perimeterRef.value.triggerFlash('success')
    }

    // Animate morph into Robot Glyph (~500ms)
    gsap.to(formContentRef.value, {
      opacity: 0,
      scale: 0.9,
      duration: 0.25,
      onComplete: () => {
        isSuccess.value = true
        // Segue into dashboard after glyph presentation
        setTimeout(() => {
          emit('authenticated')
        }, 850)
      }
    })

  } catch (err) {
    // Requirements:
    // Error (401): 300-400ms red pulsing contour on screen perimeter
    if (perimeterRef.value) {
      perimeterRef.value.triggerFlash('error')
    }
    errorMessage.value = err.message || 'Access Denied: Invalid Security Credentials'

    // Micro shake animation on form
    if (containerRef.value) {
      gsap.fromTo(
        containerRef.value,
        { x: -8 },
        { x: 8, duration: 0.08, repeat: 4, yoyo: true, ease: 'power1.inOut' }
      )
    }
  } finally {
    isLoading.value = false
  }
}
</script>
