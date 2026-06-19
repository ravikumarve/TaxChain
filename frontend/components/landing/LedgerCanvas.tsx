'use client'

import { useEffect, useRef } from 'react'

interface Block {
  col: number
  row: number
  angle: number
  yOffset: number
  radius: number
  speed: number
  active: boolean
}

interface Projected {
  x: number
  y: number
  z: number
  scale: number
  active: boolean
  col: number
  row: number
}

/**
 * LedgerCanvas — 3D isometric data stream animation.
 * Ported from TaxChain.html Canvas2D implementation.
 * Renders a cylindrical "tunnel" of connected nodes representing blockchain data flow.
 */
export default function LedgerCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let width = 0
    let height = 0
    let time = 0
    let mouseX = 0
    let mouseY = 0
    let animationId: number

    // Determine density based on screen width (performance)
    const isMobile = () => window.innerWidth < 768
    const numCols = isMobile() ? 8 : 15
    const numRows = isMobile() ? 12 : 25
    const spacing = 80

    // Build blocks
    const blocks: Block[] = []
    for (let r = 0; r < numRows; r++) {
      for (let c = 0; c < numCols; c++) {
        blocks.push({
          col: c,
          row: r,
          angle: (c / numCols) * Math.PI * 2,
          yOffset: (r - numRows / 2) * spacing,
          radius: 300 + Math.random() * 50,
          speed: 0.5 + Math.random() * 1.5,
          active: Math.random() > 0.8,
        })
      }
    }

    function handleResize() {
      width = canvas!.width = window.innerWidth
      height = canvas!.height = window.innerHeight
    }

    function handleMouseMove(e: MouseEvent) {
      mouseX += ((e.clientX - width / 2) * 0.05 - mouseX) * 0.1
      mouseY += ((e.clientY - height / 2) * 0.05 - mouseY) * 0.1
    }

    window.addEventListener('resize', handleResize)
    window.addEventListener('mousemove', handleMouseMove)
    handleResize()

    function animate() {
      animationId = requestAnimationFrame(animate)
      ctx!.clearRect(0, 0, width, height)

      time += 0.005
      const centerX = width / 2
      const centerY = height / 2
      const fov = 800

      // Project blocks to 3D space
      const projected: Projected[] = blocks.map((b) => {
        let currentY = b.yOffset - (time * 100 * b.speed) % (numRows * spacing)
        if (currentY < -numRows * spacing / 2) currentY += numRows * spacing

        let x = b.radius * Math.cos(b.angle + time * 0.2)
        let z = b.radius * Math.sin(b.angle + time * 0.2)
        let y = currentY

        const tiltX = mouseY * 0.02
        const tiltY = mouseX * 0.02

        // Rotate X
        const y1 = y * Math.cos(tiltX) - z * Math.sin(tiltX)
        const z1 = y * Math.sin(tiltX) + z * Math.cos(tiltX)

        // Rotate Y
        const x2 = x * Math.cos(tiltY) + z1 * Math.sin(tiltY)
        const z2 = -x * Math.sin(tiltY) + z1 * Math.cos(tiltY)

        const z3d = z2 + 800
        const scale = fov / z3d

        return {
          x: x2 * scale + centerX,
          y: y1 * scale + centerY,
          z: z3d,
          scale,
          active: b.active,
          col: b.col,
          row: b.row,
        }
      })

      // Sort by depth
      projected.sort((a, b) => b.z - a.z)

      // Draw connections (vertical streams within same column)
      ctx!.lineWidth = 1
      for (let i = 0; i < projected.length; i++) {
        const p = projected[i]
        if (p.z < 0) continue

        const opacity = Math.max(0.02, Math.min(0.4, 1000 / p.z - 0.5))

        // Draw node dot
        ctx!.beginPath()
        ctx!.arc(p.x, p.y, 2 * p.scale, 0, Math.PI * 2)
        ctx!.fillStyle = p.active
          ? `rgba(99, 102, 241, ${opacity * 2})`
          : `rgba(255, 255, 255, ${opacity})`
        ctx!.fill()

        // Connect to next node in same column
        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j]
          if (p.col === p2.col && Math.abs(p.row - p2.row) === 1) {
            ctx!.beginPath()
            ctx!.moveTo(p.x, p.y)
            ctx!.lineTo(p2.x, p2.y)

            const streamOpacity = p.active || p2.active
              ? opacity * 1.5
              : opacity * 0.3

            ctx!.strokeStyle = p.active || p2.active
              ? `rgba(99, 102, 241, ${streamOpacity})`
              : `rgba(255, 255, 255, ${streamOpacity})`

            ctx!.stroke()
            break
          }
        }
      }
    }

    animate()

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMouseMove)
      cancelAnimationFrame(animationId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      id="ledger-canvas"
      className="fixed top-0 left-0 w-screen h-screen z-0 pointer-events-none"
      style={{ mixBlendMode: 'screen', opacity: 0.85 }}
    />
  )
}
