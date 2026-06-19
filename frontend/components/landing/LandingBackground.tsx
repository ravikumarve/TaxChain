import LedgerCanvas from './LedgerCanvas'
import DotMatrix from './DotMatrix'
import AmbientCore from './AmbientCore'

/**
 * LandingBackground — Composes all background layers for the marketing site.
 * Order: canvas (z-0) → ambient glow (z-0) → dot matrix (z-1).
 * All pointer-events-none so they don't interfere with content.
 */
export default function LandingBackground() {
  return (
    <>
      <LedgerCanvas />
      <AmbientCore />
      <DotMatrix />
    </>
  )
}
