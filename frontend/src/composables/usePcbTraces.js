/**
 * Computes authentic PCB printed circuit board trace paths
 * with orthogonal (45° and 90°) corners and circular solder pad terminals.
 */
export function generatePcbTracePath(x0, y0, x1, y1, mode = '45deg') {
  const dx = x1 - x0
  const dy = y1 - y0
  const absDx = Math.abs(dx)
  const absDy = Math.abs(dy)
  const signX = Math.sign(dx) || 1
  const signY = Math.sign(dy) || 1

  if (mode === '45deg') {
    // PCB 45-degree chamfered trace
    const radialExit = 55 // distance from center node before angle break
    const exitX = x0 + (dx / Math.hypot(dx, dy || 1)) * radialExit
    const exitY = y0 + (dy / Math.hypot(dx, dy || 1)) * radialExit

    if (absDx > absDy) {
      const diagonalDist = absDy
      const corner1X = exitX + signX * 20
      const corner1Y = exitY
      const corner2X = corner1X + signX * diagonalDist
      const corner2Y = y1
      return `M ${x0} ${y0} L ${exitX} ${exitY} L ${corner1X} ${corner1Y} L ${corner2X} ${corner2Y} L ${x1} ${y1}`
    } else {
      const diagonalDist = absDx
      const corner1X = exitX
      const corner1Y = exitY + signY * 20
      const corner2X = x1
      const corner2Y = corner1Y + signY * diagonalDist
      return `M ${x0} ${y0} L ${exitX} ${exitY} L ${corner1X} ${corner1Y} L ${corner2X} ${corner2Y} L ${x1} ${y1}`
    }
  }

  // Pure 90-degree orthogonal PCB bus routing
  const midX = x0 + dx * 0.5
  return `M ${x0} ${y0} L ${midX} ${y0} L ${midX} ${y1} L ${x1} ${y1}`
}

/**
 * Computes coordinates for satellite orbital buttons
 */
export function calculateOrbitPositions(count, radius = 230, centerX = 400, centerY = 400, startAngle = -Math.PI / 2) {
  const items = []
  const angleStep = (2 * Math.PI) / (count || 1)

  for (let i = 0; i < count; i++) {
    const angle = startAngle + i * angleStep
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)
    items.push({ x, y, angle: (angle * 180) / Math.PI })
  }

  return items
}
