<template>
  <canvas 
    ref="canvasRef" 
    class="absolute inset-0 w-full h-full pointer-events-none z-[2]"
  ></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animationFrameId = null

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')

  let width = (canvas.width = window.innerWidth)
  let height = (canvas.height = window.innerHeight)

  const handleResize = () => {
    width = canvas.width = window.innerWidth
    height = canvas.height = window.innerHeight
    initParticles()
  }
  window.addEventListener('resize', handleResize)

  // Cyber dust particles
  const particleCount = 45
  let particles = []

  const initParticles = () => {
    particles = []
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        radius: Math.random() * 1.8 + 0.8,
        speedX: (Math.random() - 0.5) * 0.4,
        speedY: (Math.random() - 0.5) * 0.4 - 0.1, // slight upward float
        alpha: Math.random() * 0.4 + 0.15,
        color: Math.random() > 0.4 ? '#00f3ff' : '#00ff66',
        pulseSpeed: Math.random() * 0.02 + 0.01,
        angle: Math.random() * Math.PI * 2
      })
    }
  }

  initParticles()

  // Radar scanning angle
  let scanAngle = 0

  // Pulsing circuit nodes
  const nodes = [
    { relX: 0.22, relY: 0.28, phase: 0 },
    { relX: 0.78, relY: 0.25, phase: 1.5 },
    { relX: 0.18, relY: 0.72, phase: 3.0 },
    { relX: 0.82, relY: 0.75, phase: 4.5 },
    { relX: 0.5, relY: 0.15, phase: 2.0 },
    { relX: 0.5, relY: 0.85, phase: 0.8 }
  ]

  const animate = () => {
    ctx.clearRect(0, 0, width, height)

    const centerX = width / 2
    const centerY = height / 2

    // 1. Soft Rotating Center Radar Sweep
    scanAngle += 0.008
    const maxRadius = Math.hypot(width, height) * 0.48

    ctx.save()
    ctx.translate(centerX, centerY)
    ctx.rotate(scanAngle)

    // Soft conic sweep gradient
    const sweepGrad = ctx.createLinearGradient(0, 0, maxRadius, 0)
    sweepGrad.addColorStop(0, 'rgba(0, 243, 255, 0.12)')
    sweepGrad.addColorStop(0.7, 'rgba(0, 255, 102, 0.04)')
    sweepGrad.addColorStop(1, 'rgba(0, 243, 255, 0)')

    ctx.beginPath()
    ctx.moveTo(0, 0)
    ctx.arc(0, 0, maxRadius, -0.3, 0.05)
    ctx.closePath()
    ctx.fillStyle = sweepGrad
    ctx.fill()

    // Leading crisp scan ray
    ctx.beginPath()
    ctx.moveTo(0, 0)
    ctx.lineTo(maxRadius, 0)
    ctx.strokeStyle = 'rgba(0, 243, 255, 0.25)'
    ctx.lineWidth = 1.2
    ctx.stroke()

    ctx.restore()

    // 2. Faint Pulsing Digital Circuit Nodes
    const time = Date.now() * 0.002
    for (const node of nodes) {
      const nx = node.relX * width
      const ny = node.relY * height
      const pulse = (Math.sin(time + node.phase) + 1) * 0.5 // 0 to 1
      const alpha = 0.1 + pulse * 0.35

      // Glow halo
      ctx.beginPath()
      ctx.arc(nx, ny, 8 + pulse * 6, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(0, 243, 255, ${alpha * 0.3})`
      ctx.fill()

      // Core point
      ctx.beginPath()
      ctx.arc(nx, ny, 2.5, 0, Math.PI * 2)
      ctx.fillStyle = `rgba(0, 255, 102, ${alpha})`
      ctx.fill()
    }

    // 3. Floating Cyber Dust Particles
    for (const p of particles) {
      p.x += p.speedX
      p.y += p.speedY
      p.angle += p.pulseSpeed

      // Wrap around edges
      if (p.x < 0) p.x = width
      if (p.x > width) p.x = 0
      if (p.y < 0) p.y = height
      if (p.y > height) p.y = 0

      const currentAlpha = p.alpha * (0.6 + 0.4 * Math.sin(p.angle))

      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fillStyle = p.color
      ctx.globalAlpha = currentAlpha
      ctx.shadowColor = p.color
      ctx.shadowBlur = 6
      ctx.fill()
      ctx.shadowBlur = 0
      ctx.globalAlpha = 1.0
    }

    animationFrameId = requestAnimationFrame(animate)
  }

  animate()

  onUnmounted(() => {
    if (animationFrameId) cancelAnimationFrame(animationFrameId)
    window.removeEventListener('resize', handleResize)
  })
})
</script>
