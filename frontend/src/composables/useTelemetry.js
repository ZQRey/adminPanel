import { ref, onMounted, onUnmounted } from 'vue'

const isConnected = ref(false)
const lastTimestamp = ref(Date.now())
const proxmox = ref({
  status: 'connecting',
  cpu_pct: 0,
  mem_pct: 0,
  disk_pct: 0,
  vms_running: 0,
  is_simulated: false
})
const nut = ref({
  status: 'connecting',
  battery_charge_pct: 100,
  ups_load_pct: 0,
  wattage: 0,
  input_voltage: 230,
  battery_runtime_min: 0,
  is_simulated: false
})
const plugins = ref({})

let socket = null
let reconnectTimer = null

export function useTelemetry() {
  const connect = () => {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      return
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}/ws/telemetry`

    socket = new WebSocket(wsUrl)

    socket.onopen = () => {
      isConnected.value = true
      if (reconnectTimer) {
        clearInterval(reconnectTimer)
        reconnectTimer = null
      }
    }

    socket.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'telemetry_update' && msg.data) {
          lastTimestamp.value = msg.timestamp * 1000
          if (msg.data.proxmox) proxmox.value = msg.data.proxmox
          if (msg.data.nut) nut.value = msg.data.nut
          if (msg.data.plugins) plugins.value = msg.data.plugins
        }
      } catch (e) {
        console.error('Error parsing WebSocket telemetry:', e)
      }
    }

    socket.onclose = () => {
      isConnected.value = false
      socket = null
      if (!reconnectTimer) {
        reconnectTimer = setInterval(() => {
          connect()
        }, 3000)
      }
    }

    socket.onerror = () => {
      isConnected.value = false
    }
  }

  const disconnect = () => {
    if (reconnectTimer) {
      clearInterval(reconnectTimer)
      reconnectTimer = null
    }
    if (socket) {
      socket.close()
      socket = null
    }
    isConnected.value = false
  }

  return {
    isConnected,
    lastTimestamp,
    proxmox,
    nut,
    plugins,
    connect,
    disconnect
  }
}
