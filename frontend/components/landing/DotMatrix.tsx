/**
 * DotMatrix — Fixed background dot grid overlay.
 * Uses CSS radial-gradient for zero-cost rendering (no canvas).
 * Centered vignette mask fades dots out toward edges.
 */
export default function DotMatrix() {
  return <div className="dot-matrix" aria-hidden="true" />
}
