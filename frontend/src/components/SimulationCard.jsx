import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import AllocationRow from './AllocationRow'

function PerformanceChart({ performance }) {
  if (!performance) return null
  const { data_points, total_return_pct, annualized_return_pct, period } = performance
  const periodLabel = { '1y': '1 Year', '2y': '2 Years', '5y': '5 Years' }[period] || period
  const isPositive = total_return_pct >= 0
  const lineColor = isPositive ? '#22c55e' : '#f87171'
  const step = Math.max(1, Math.floor(data_points.length / 120))
  const chartData = data_points.filter((_, i) => i % step === 0 || i === data_points.length - 1)
  return (
    <div className="perf-section">
      <div className="perf-header">Historical Simulation · {periodLabel}</div>
      <ResponsiveContainer width="100%" height={130}>
        <LineChart data={chartData} margin={{ top: 4, right: 4, bottom: 0, left: 0 }}>
          <XAxis dataKey="date" hide />
          <YAxis domain={['auto', 'auto']} hide />
          <Tooltip
            formatter={(v) => [`${v.toFixed(1)}`, 'Index']}
            contentStyle={{ background: '#1e1e2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, fontSize: 11 }}
            labelStyle={{ color: '#64748b', fontSize: 10 }}
          />
          <Line type="monotone" dataKey="value" stroke={lineColor} dot={false} strokeWidth={1.5} />
        </LineChart>
      </ResponsiveContainer>
      <div className="perf-stats">
        <div className="perf-stat">
          <span className="perf-stat-label">Total Return</span>
          <span className="perf-stat-value" style={{ color: lineColor }}>{isPositive ? '+' : ''}{total_return_pct.toFixed(1)}%</span>
        </div>
        <div className="perf-stat">
          <span className="perf-stat-label">Annualized</span>
          <span className="perf-stat-value" style={{ color: lineColor }}>{isPositive ? '+' : ''}{annualized_return_pct.toFixed(1)}% / yr</span>
        </div>
      </div>
    </div>
  )
}

export default function SimulationCard({ simulation }) {
  if (!simulation) return null
  const { label, allocations, performance } = simulation
  return (
    <div className="simulation-card">
      {label && <div className="simulation-label">{label}</div>}
      {allocations?.length > 0 && (
        <div className="simulation-allocs">
          {allocations.map((a, i) => <AllocationRow key={a.ticker ?? i} {...a} />)}
        </div>
      )}
      <PerformanceChart performance={performance} />
    </div>
  )
}
