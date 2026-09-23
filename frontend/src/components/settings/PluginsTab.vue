<template>
  <div class="space-y-6 select-none font-mono text-xs">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-cyan-500/30 pb-3">
      <div>
        <div class="text-sm font-bold text-cyan-300">CUSTOM PYTHON TELEMETRY PLUGINS</div>
        <div class="text-[10px] text-cyan-500/80">
          EXECUTED IN STRICTLY ISOLATED ASYNC SUBPROCESSES WITH TIMEOUT GUARDS
        </div>
      </div>
      <button 
        @click="openNewPluginModal"
        class="px-3 py-1.5 rounded bg-purple-950/80 border border-purple-400 text-purple-300 hover:bg-purple-900 font-bold transition-all shadow-[0_0_10px_rgba(168,85,247,0.3)]"
      >
        ＋ NEW PYTHON PROBE
      </button>
    </div>

    <!-- Active Plugins List -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div 
        v-for="p in plugins" 
        :key="p.filename"
        class="hud-glass-panel p-4 rounded border border-purple-500/30 hover:border-purple-400 transition-all flex flex-col justify-between space-y-3"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="w-2.5 h-2.5 rounded-full bg-purple-400 animate-pulse"></span>
            <span class="text-sm font-bold text-cyan-200">{{ p.name }}</span>
          </div>
          <span class="text-[10px] text-purple-300 bg-purple-950/80 px-2 py-0.5 rounded border border-purple-500/40">
            {{ p.filename }}
          </span>
        </div>

        <div class="text-[10px] text-cyan-400/60">
          Size: {{ p.size_bytes }} bytes // Path: backend/plugins/{{ p.filename }}
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-cyan-900/40">
          <button 
            @click="editPlugin(p.filename)"
            class="px-2.5 py-1 rounded bg-slate-900 hover:bg-cyan-950 border border-cyan-500/40 text-cyan-300 text-[10px]"
          >
            EDIT SCRIPT
          </button>
          <div class="space-x-2">
            <button 
              @click="runPluginTest(p.filename)"
              :disabled="runningPlugin === p.filename"
              class="px-2.5 py-1 rounded bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-400 text-emerald-300 font-bold text-[10px]"
            >
              {{ runningPlugin === p.filename ? 'EXECUTING...' : '⚡ TEST RUN' }}
            </button>
            <button 
              v-if="p.filename !== 'system_telemetry.py'"
              @click="deletePlugin(p.filename)"
              class="px-2 py-1 rounded bg-red-950/50 hover:bg-red-900 border border-red-500/50 text-red-300 text-[10px]"
            >
              DELETE
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Execution Terminal Output Modal / Drawer -->
    <div v-if="testResult" class="p-4 rounded hud-glass-panel border border-emerald-400/60 space-y-2 animate-fade-in">
      <div class="flex items-center justify-between">
        <span class="font-bold text-emerald-400">
          SUBPROCESS EXECUTION RESULTS: [{{ testResult.plugin }}] (EXIT: {{ testResult.exit_code }})
        </span>
        <button @click="testResult = null" class="text-cyan-400 hover:text-white">✕</button>
      </div>
      <div class="p-3 rounded bg-slate-950 border border-cyan-500/30 overflow-x-auto max-h-48 text-[11px] text-emerald-300 font-mono">
        <pre>{{ JSON.stringify(testResult.metrics || testResult, null, 2) }}</pre>
      </div>
      <div v-if="testResult.stderr" class="p-2 rounded bg-red-950/40 border border-red-500/30 text-red-300 text-[10px]">
        STDERR: {{ testResult.stderr }}
      </div>
    </div>

    <!-- Script Editor Modal -->
    <div v-if="editingPlugin" class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="hud-glass-panel hud-chamfer p-6 w-full max-w-2xl space-y-4 max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between border-b border-cyan-500/30 pb-2">
          <div class="text-sm font-bold text-cyan-300">
            PYTHON PROBE SCRIPT: {{ editingPlugin.filename }}
          </div>
          <button @click="editingPlugin = null" class="text-cyan-400 hover:text-white">✕</button>
        </div>

        <div class="text-[10px] text-cyan-400/70">
          Script must output valid JSON or key-values to stdout. Subprocesses are isolated and subject to a 4.0s timeout.
        </div>

        <div class="flex-1 flex flex-col min-h-[300px]">
          <textarea
            v-model="editingPlugin.code"
            class="flex-1 w-full bg-slate-950 border border-cyan-500/40 rounded p-3 text-cyan-100 font-mono text-xs focus:outline-none focus:border-cyan-400 leading-relaxed resize-none"
            spellcheck="false"
          ></textarea>
        </div>

        <div class="flex items-center justify-between pt-2 border-t border-cyan-900/40">
          <button 
            @click="runPluginTest(editingPlugin.filename)"
            :disabled="runningPlugin === editingPlugin.filename"
            class="px-3 py-1.5 rounded bg-emerald-950 border border-emerald-400 text-emerald-300 font-bold"
          >
            ⚡ RUN SUBPROCESS TEST
          </button>
          <div class="space-x-3">
            <button 
              @click="editingPlugin = null"
              class="px-3 py-1.5 rounded border border-slate-700 text-slate-400 hover:text-white"
            >
              CLOSE
            </button>
            <button 
              @click="savePlugin"
              class="px-4 py-1.5 rounded bg-purple-950 border border-purple-400 text-purple-200 hover:bg-purple-900 font-bold"
            >
              SAVE PROBE SCRIPT
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'

const { authFetch } = useAuth()

const plugins = ref([])
const editingPlugin = ref(null)
const runningPlugin = ref(null)
const testResult = ref(null)

const fetchPlugins = async () => {
  try {
    const res = await authFetch('/api/plugins')
    if (res.ok) {
      plugins.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to list plugins:', e)
  }
}

const editPlugin = async (filename) => {
  try {
    const res = await authFetch(`/api/plugins/${filename}`)
    if (res.ok) {
      const data = await res.json()
      editingPlugin.value = { filename: data.filename, code: data.code }
    }
  } catch (e) {
    alert('Failed to load plugin: ' + e.message)
  }
}

const openNewPluginModal = () => {
  editingPlugin.value = {
    filename: `custom_probe_${Date.now().toString().slice(-4)}.py`,
    code: `#!/usr/bin/env python3
import json
import time

# Custom Telemetry Probe
data = {
    "status": "ONLINE",
    "mesh_entropy": 99.2,
    "probe_timestamp": time.time()
}
print(json.dumps(data))
`
  }
}

const savePlugin = async () => {
  try {
    const res = await authFetch('/api/plugins', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(editingPlugin.value)
    })
    if (res.ok) {
      alert('Plugin script saved!')
      editingPlugin.value = null
      fetchPlugins()
    }
  } catch (e) {
    alert('Save plugin error: ' + e.message)
  }
}

const runPluginTest = async (filename) => {
  runningPlugin.value = filename
  testResult.value = null
  try {
    const res = await authFetch(`/api/plugins/${filename}/run`, { method: 'POST' })
    if (res.ok) {
      testResult.value = await res.json()
    }
  } catch (e) {
    testResult.value = { error: e.message, plugin: filename }
  } finally {
    runningPlugin.value = null
  }
}

const deletePlugin = async (filename) => {
  if (!confirm(`Permanently delete plugin ${filename}?`)) return
  try {
    const res = await authFetch(`/api/plugins/${filename}`, { method: 'DELETE' })
    if (res.ok) {
      fetchPlugins()
    }
  } catch (e) {
    alert('Delete plugin error: ' + e.message)
  }
}

onMounted(() => {
  fetchPlugins()
})
</script>
