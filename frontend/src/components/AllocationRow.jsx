export default function AllocationRow({ ticker, name, weight, color }) {
  return (
    <div className="allocation-row">
      <div className="ticker-info">
        <span className="ticker" style={{ color }}>{ticker}</span>
        <span className="ticker-name">{name}</span>
      </div>
      <div className="bar-wrap">
        <div className="bar" style={{ width: `${weight}%`, background: color }} />
      </div>
      <span className="weight">{weight}%</span>
    </div>
  )
}
