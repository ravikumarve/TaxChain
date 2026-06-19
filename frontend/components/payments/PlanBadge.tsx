'use client'

interface PlanBadgeProps {
  currentPlan: string
  showUpgradeButton?: boolean
  onUpgradeClick?: () => void
}

const planLabels: Record<string, string> = {
  free: 'Free',
  starter: 'Starter',
  pro: 'Pro',
}

const planColors: Record<string, string> = {
  free: 'bg-gray-100 text-gray-700 border-gray-200',
  starter: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  pro: 'bg-emerald-50 text-emerald-700 border-emerald-200',
}

/**
 * PlanBadge — Displays the current plan with optional upgrade button.
 * Used in the dashboard sidebar to show plan status and trigger upgrades.
 */
export default function PlanBadge({ currentPlan, showUpgradeButton, onUpgradeClick }: PlanBadgeProps) {
  return (
    <div className="flex items-center gap-2">
      <span
        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
          planColors[currentPlan] || planColors.free
        }`}
      >
        {planLabels[currentPlan] || 'Free'}
      </span>
      {showUpgradeButton && onUpgradeClick && (
        <button
          onClick={onUpgradeClick}
          className="text-xs text-indigo-400 hover:text-indigo-300 underline underline-offset-2 transition-colors"
        >
          Upgrade
        </button>
      )}
    </div>
  )
}
