<template>
  <div
    v-if="activeFlash"
    class="fixed inset-0 pointer-events-none z-50 transition-all duration-300"
    :class="flashClass"
  ></div>
</template>

<script setup>
import { ref } from 'vue'

const activeFlash = ref(false)
const flashType = ref('') // 'error' or 'success'
const flashClass = ref('')

let timeoutId = null

const triggerFlash = (type) => {
  if (timeoutId) clearTimeout(timeoutId)
  
  flashType.value = type
  activeFlash.value = true
  flashClass.value = type === 'error' ? 'perimeter-pulse-error' : 'perimeter-pulse-success'

  // Requirement: exactly 300-400ms
  timeoutId = setTimeout(() => {
    activeFlash.value = false
    flashType.value = ''
    flashClass.value = ''
  }, 380)
}

defineExpose({
  triggerFlash
})
</script>
