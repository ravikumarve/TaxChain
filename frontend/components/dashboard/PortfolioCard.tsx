'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

interface PortfolioCardProps {
  title: string
  value: number
  valuePrefix?: string
  subtitle: string
  trend?: {
    value: number
    isPositive: boolean
  }
  isLoading?: boolean
}

export function PortfolioCard({
  title,
  value,
  valuePrefix = '$',
  subtitle,
  trend,
  isLoading = false,
}: PortfolioCardProps) {
  const formatValue = (val: number) => {
    if (val >= 1000000) return `${valuePrefix}${(val / 1000000).toFixed(2)}M`
    if (val >= 1000) return `${valuePrefix}${(val / 1000).toFixed(2)}K`
    return `${valuePrefix}${val.toFixed(2)}`
  }

  const valueColor = title.includes('Gain/Loss')
    ? value >= 0 ? 'text-gain' : 'text-loss'
    : 'text-indigo-400'

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <div className="h-4 bg-surface rounded w-1/2 animate-pulse" />
        </CardHeader>
        <CardContent>
          <div className="h-8 bg-surface rounded w-3/4 animate-pulse mb-2" />
          <div className="h-4 bg-surface rounded w-1/2 animate-pulse" />
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${valueColor}`}>
          {formatValue(value)}
        </div>
        <p className="text-sm text-faint mt-1">{subtitle}</p>
        {trend && (
          <div className={`text-xs mt-1 ${trend.isPositive ? 'text-gain' : 'text-loss'}`}>
            {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value).toFixed(2)}%
          </div>
        )}
      </CardContent>
    </Card>
  )
}
