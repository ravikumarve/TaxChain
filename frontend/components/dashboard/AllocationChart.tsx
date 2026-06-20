'use client'

import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

const CHAIN_COLORS: Record<string, string> = {
  eth: '#627EEA',
  bnb: '#F3BA2F',
  polygon: '#8247E5',
  sol: '#9945FF',
  arbitrum: '#28A0F0',
  optimism: '#FF0420',
  base: '#0052FF',
  btc: '#F7931A',
}

const TOKEN_COLORS = [
  '#6366F1', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
  '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#14B8A6',
]

interface ChainItem {
  chain: string
  value_usd: number
  percentage: number
}

interface TokenItem {
  token_symbol: string
  value_usd: number
  percentage: number
  quantity: number
}

interface AllocationChartProps {
  chainBreakdown: ChainItem[]
  tokenBreakdown: TokenItem[]
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(value)
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null
  const data = payload[0].payload
  return (
    <div className="bg-surface border border-border-dim rounded-lg px-3 py-2 text-xs shadow-lg">
      <p className="text-main font-medium">{data.name || data.chain || data.token_symbol}</p>
      <p className="text-muted">{formatCurrency(data.value_usd)}</p>
      <p className="text-faint">{data.percentage}%</p>
    </div>
  )
}

function renderLegend(props: any) {
  const { payload } = props
  return (
    <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2 justify-center">
      {payload.map((entry: any, index: number) => (
        <div key={`legend-${index}`} className="flex items-center gap-1.5 text-xs">
          <span
            className="w-2 h-2 rounded-full flex-shrink-0"
            style={{ backgroundColor: entry.color }}
          />
          <span className="text-muted">{entry.value}</span>
        </div>
      ))}
    </div>
  )
}

export function AllocationChart({ chainBreakdown, tokenBreakdown }: AllocationChartProps) {
  const chainData = chainBreakdown.map((item) => ({
    name: item.chain.toUpperCase(),
    chain: item.chain,
    value_usd: item.value_usd,
    percentage: item.percentage,
    fill: CHAIN_COLORS[item.chain] || '#64748B',
  }))

  // Token breakdown: top 5 + "Other"
  const sortedTokens = [...tokenBreakdown].sort((a, b) => b.value_usd - a.value_usd)
  let tokenData: any[]
  if (sortedTokens.length > 5) {
    const top5 = sortedTokens.slice(0, 5)
    const otherValue = sortedTokens.slice(5).reduce((sum, t) => sum + t.value_usd, 0)
    tokenData = top5.map((item, i) => ({
      name: item.token_symbol,
      value_usd: item.value_usd,
      percentage: item.percentage,
      fill: TOKEN_COLORS[i],
    }))
    if (otherValue > 0) {
      tokenData.push({
        name: 'Other',
        value_usd: otherValue,
        percentage: parseFloat(
          ((otherValue / sortedTokens.reduce((s, t) => s + t.value_usd, 0)) * 100).toFixed(1)
        ),
        fill: '#64748B',
      })
    }
  } else {
    tokenData = sortedTokens.map((item, i) => ({
      name: item.token_symbol,
      value_usd: item.value_usd,
      percentage: item.percentage,
      fill: TOKEN_COLORS[i],
    }))
  }

  if (!chainBreakdown.length && !tokenBreakdown.length) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card className="bg-panel border-border-dim">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted">
              Allocation by Chain
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-faint text-center py-8">
              No wallet data to display
            </p>
          </CardContent>
        </Card>
        <Card className="bg-panel border-border-dim">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted">
              Allocation by Token
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-faint text-center py-8">
              No wallet data to display
            </p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* By Chain */}
      <Card className="bg-panel border-border-dim">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted">
            Allocation by Chain
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={chainData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value_usd"
              >
                {chainData.map((entry, index) => (
                  <Cell key={`chain-cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend content={renderLegend} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* By Token */}
      <Card className="bg-panel border-border-dim">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium text-muted">
            Allocation by Token
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={tokenData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value_usd"
              >
                {tokenData.map((entry, index) => (
                  <Cell key={`token-cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend content={renderLegend} />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}
