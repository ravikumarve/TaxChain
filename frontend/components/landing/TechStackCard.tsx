const stack = [
  ['Frontend', 'Next.js 14 + Tailwind'],
  ['Backend', 'FastAPI (Python 3.12+)'],
  ['Database', 'PostgreSQL 15+'],
  ['Background', 'APScheduler'],
  ['Payments', 'Lemon Squeezy + Razorpay'],
  ['Oracles', 'CoinGecko + open.er-api'],
]

/**
 * TechStackCard — Dark surface card with glow border showing the full tech stack.
 */
export default function TechStackCard() {
  return (
    <div className="bg-surface border border-indigo-500/20 rounded-xl p-5">
      <div className="font-mono text-[10px] tracking-widest text-indigo-400 uppercase mb-4">
        Tech Stack
      </div>
      <div className="space-y-2">
        {stack.map(([layer, tech]) => (
          <div key={layer} className="flex items-center justify-between text-xs">
            <span className="text-faint font-mono">{layer}</span>
            <span className="text-main">{tech}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
