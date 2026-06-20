'use client'

import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

interface TimelinePoint {
  date: string
  value_usd: number
}

interface PnlTimelineChartProps {
  data: TimelinePoint[]
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-surface border border-border-dim rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-faint">{label}</p>
      <p className="text-main font-bold font-mono">
        {formatCurrency(payload[0].value)}
      </p>
    </div>
  )
}

function formatDate(dateStr: string): string {
  // Convert "2026-01-01" to "Jan '26"
  const d = new Date(dateStr)
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
  ]
  return `${months[d.getMonth()]} '${d.getFullYear().toString().slice(2)}`
}

export function PnlTimelineChart({ data }: PnlTimelineChartProps) {
  if (!data.length) {
    return (
      <Card className="bg-panel border-border-dim">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted">
            Portfolio Value Over Time
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-xs text-faint text-center py-8">
            No historical data available
          </p>
        </CardContent>
      </Card>
    )
  }

  const formattedData = data.map((pt) => ({
    ...pt,
    label: formatDate(pt.date),
  }))

  const minValue = Math.min(...data.map((d) => d.value_usd))
  const maxValue = Math.max(...data.map((d) => d.value_usd))
  const yDomainMin = minValue - (maxValue - minValue) * 0.1
  const yDomainMax = maxValue + (maxValue - minValue) * 0.1

  return (
    <Card className="bg-panel border-border-dim">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted">
          Portfolio Value Over Time
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart
            data={formattedData}
            margin={{ top: 5, right: 10, left: 10, bottom: 5 }}
          >
            <defs>
              <linearGradient id="pnlGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#6366F1" stopOpacity={0.3} />
                <stop offset="100%" stopColor="#6366F1" stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="label"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 11 }}
              dy={8}
            />
            <YAxis
              domain={[yDomainMin, yDomainMax]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#64748B', fontSize: 11 }}
              tickFormatter={(val: number) => `$${(val / 1000).toFixed(0)}k`}
              dx={-4}
              width={50}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="value_usd"
              stroke="#6366F1"
              strokeWidth={2}
              fill="url(#pnlGradient)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
