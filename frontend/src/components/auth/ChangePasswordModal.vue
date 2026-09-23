<template>
  <div class="fixed inset-0 z-50 bg-black/90 backdrop-blur-md flex items-center justify-center p-4">
    <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-md space-y-4 border border-amber-400 shadow-[0_0_30px_rgba(255,170,0,0.5)]">
      <div class="border-b border-amber-500/40 pb-3">
        <div class="text-sm font-mono font-bold text-amber-400">
          ⚠ ONE-TIME CREDENTIAL DETECTED
        </div>
        <div class="text-[10px] font-mono text-amber-200/70 mt-1">
          Security protocol mandates defining a permanent security key before continuing.
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4 font-mono text-xs">
        <div>
          <label class="block text-[10px] text-amber-300/80 mb-1">NEW SECURITY PASSWORD</label>
          <input 
            v-model="newPassword" 
            type="password" 
            required 
            placeholder="At least 6 characters"
            class="w-full bg-slate-950 border border-amber-500/40 rounded px-3 py-2 text-amber-100 font-mono text-sm focus:outline-none focus:border-amber-400"
          />
        </div>

        <div>
          <label class="block text-[10px] text-amber-300/80 mb-1">CONFIRM NEW PASSWORD</label>
          <input 
            v-model="confirmPassword" 
            type="password" 
            required 
            placeholder="Repeat password"
            class="w-full bg-slate-950 border border-amber-500/40 rounded px-3 py-2 text-amber-100 font-mono text-sm focus:outline-none focus:border-amber-400"
          />
        </div>

        <div v-if="errorMsg" class="p-2 rounded bg-red-950/60 border border-red-500/50 text-red-300 text-[11px]">
          {{ errorMsg }}
        </div>

        <button 
          type="submit" 
          :disabled="isSubmitting"
          class="w-full py-2.5 px-4 rounded bg-amber-950 border border-amber-400 hover:bg-amber-900 text-amber-200 font-bold tracking-widest transition-all shadow-[0_0_15px_rgba(255,170,0,0.3)]"
        >
          {{ isSubmitting ? 'UPDATING KEY...' : 'UPDATE SECURITY CREDENTIALS' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'

const emit = defineEmits(['updated'])
const { changePassword } = useAuth()

const newPassword = ref('')
const confirmPassword = ref('')
const errorMsg = ref('')
const isSubmitting = ref(false)

const handleSubmit = async () => {
  if (newPassword.value.length < 6) {
    errorMsg.value = 'Password must be at least 6 characters'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    errorMsg.value = 'Passwords do not match'
    return
  }

  isSubmitting.value = true
  errorMsg.value = ''

  try {
    await changePassword('', newPassword.value)
    alert('Security key updated successfully!')
    emit('updated')
  } catch (e) {
    errorMsg.value = e.message || 'Failed to update password'
  } finally {
    isSubmitting.value = false
  }
}
</script>
