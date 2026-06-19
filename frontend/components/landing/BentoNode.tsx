interface BentoNodeProps {
  span: 4 | 6 | 8 | 12
  index: string
  label: string
  title: string
  children: React.ReactNode
}

/** CSS class map for column spans */
const spanClasses: Record<number, string> = {
  4: 'lg:col-span-4',
  6: 'lg:col-span-6',
  8: 'lg:col-span-8',
  12: 'lg:col-span-12',
}

/**
 * BentoNode — Single bento grid item with hover glow effect.
 * Uses the .bento-node CSS class from globals.css.
 * Supports 12-column fractional spans.
 */
export default function BentoNode({ span, index, label, title, children }: BentoNodeProps) {
  return (
    <div className={`bento-node ${spanClasses[span] || 'lg:col-span-4'} col-span-12`}>
      <div className="relative z-10">
        {/* Index + label row */}
        <div className="flex items-center gap-3 mb-6 text-xs">
          <span className="font-mono text-indigo-400 tracking-wider">{index} //</span>
          <span className="font-mono text-faint tracking-widest uppercase">{label}</span>
        </div>

        {/* Title */}
        <h3 className="text-2xl font-semibold text-main mb-4">{title}</h3>

        {/* Content */}
        <div className="text-muted text-sm leading-relaxed space-y-2">
          {children}
        </div>
      </div>
    </div>
  )
}
