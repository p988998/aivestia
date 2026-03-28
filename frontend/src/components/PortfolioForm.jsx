import { useState } from 'react'

const INTERESTS = [
  { label: 'Tech & Growth',         tooltip: 'High-growth tech & innovation stocks (e.g. QQQ, VGT)' },
  { label: 'Dividend Income',       tooltip: 'Stocks paying regular dividends for steady income (e.g. VYM, SCHD)' },
  { label: 'ESG / Sustainable',     tooltip: 'Companies screened for environmental & social responsibility (e.g. ESGV)' },
  { label: 'International Markets', tooltip: 'Exposure to stocks outside the US, developed & emerging (e.g. VXUS, EFA)' },
  { label: 'REITs / Real Estate',   tooltip: 'Real estate investment trusts — own property, pay high dividends (e.g. VNQ)' },
  { label: 'Bonds & Fixed Income',  tooltip: 'Lower-risk debt instruments that stabilize a portfolio (e.g. BND, AGG)' },
  { label: 'Value Investing',       tooltip: 'Stocks trading below intrinsic value — Buffett-style approach (e.g. VTV)' },
  { label: 'Small & Mid Cap',       tooltip: 'Smaller companies with higher growth potential and more volatility (e.g. VB)' },
]

export default function PortfolioForm({ onSaveForChat, savedProfile }) {
  const [form, setForm] = useState({
    age: savedProfile?.age ?? '',
    riskLevel: savedProfile?.riskLevel ?? 'medium',
    horizon: savedProfile?.horizon ?? '',
    interests: savedProfile?.interests ?? [],
    holdings: savedProfile?.holdings ?? [],
  })

  function toggleInterest(interest) {
    setForm(f => ({
      ...f,
      interests: f.interests.includes(interest)
        ? f.interests.filter(i => i !== interest)
        : [...f.interests, interest],
    }))
  }

  function addHolding() {
    setForm(f => ({ ...f, holdings: [...f.holdings, { ticker: '', raw: '' }] }))
  }

  function removeHolding(i) {
    setForm(f => ({ ...f, holdings: f.holdings.filter((_, idx) => idx !== i) }))
  }

  function updateHolding(i, field, value) {
    setForm(f => {
      const holdings = [...f.holdings]
      holdings[i] = { ...holdings[i], [field]: value }
      return { ...f, holdings }
    })
  }

  const rawSum = form.holdings.reduce((s, h) => s + (parseFloat(h.raw) || 0), 0)

  function handleSave() {
    const validHoldings = form.holdings.filter(h => h.ticker.trim() && parseFloat(h.raw) > 0)
    const vSum = validHoldings.reduce((s, h) => s + parseFloat(h.raw), 0)
    const cleanHoldings = validHoldings.map(h => ({
      ticker: h.ticker.trim().toUpperCase(),
      weight: Math.round(parseFloat(h.raw) / vSum * 100),
    }))
    const holdingsText = cleanHoldings.length ? ` · ${cleanHoldings.length} holding${cleanHoldings.length > 1 ? 's' : ''}` : ''
    onSaveForChat({ ...form, holdings: cleanHoldings, _holdingsText: holdingsText })
  }

  function handleClear() {
    setForm({ age: '', riskLevel: 'medium', horizon: '', interests: [], holdings: [] })
  }

  const canSave = form.age && form.horizon
  const hasContent = form.age || form.horizon || form.interests.length > 0 || form.holdings.length > 0

  return (
    <div className="portfolio-form-wrap">
      <div className="portfolio-form">
        <h2 className="form-title">My Investor Profile</h2>
        <label className="form-label">
          Age
          <input type="number" min="18" max="100" value={form.age}
            onChange={e => setForm(f => ({ ...f, age: e.target.value }))} />
        </label>
        <div className="form-label">
          Risk Level
          <div className="risk-pills">
            {[
              { value: 'low',    label: 'Low',    tooltip: 'Focuses on capital preservation with minimal volatility. Lower expected returns but more stable performance. Suitable for short-term goals or risk-averse investors.' },
              { value: 'medium', label: 'Medium', tooltip: 'Balances growth and stability with a mix of equities and bonds. Moderate returns with manageable fluctuations. Suitable for mid-term horizons (3–7 years).' },
              { value: 'high',   label: 'High',   tooltip: 'Targets long-term growth through equity-heavy exposure. Higher return potential with significant short-term volatility. Suitable for long-term investors (7+ years).' },
            ].map(({ value, label, tooltip }) => (
              <button
                key={value}
                type="button"
                className={`risk-pill risk-pill-${value} ${form.riskLevel === value ? 'risk-pill-active' : ''}`}
                onClick={() => setForm(f => ({ ...f, riskLevel: value }))}
                data-tooltip={tooltip}
              >{label}</button>
            ))}
          </div>
        </div>
        <label className="form-label">
          Investment Horizon (years)
          <input type="number" min="1" max="50" value={form.horizon}
            onChange={e => setForm(f => ({ ...f, horizon: e.target.value }))} />
        </label>
        <div className="interest-section">
          <div className="interest-label">Select your investment preferences <span className="interest-optional">(optional)</span></div>
          <div className="interest-hint">Select up to 3 · first pick has stronger influence</div>
          <div className="interest-pills">
            {INTERESTS.map(({ label, tooltip }) => {
              const selIdx = form.interests.indexOf(label)
              const isSelected = selIdx >= 0
              return (
                <button
                  key={label}
                  type="button"
                  className={`interest-pill ${isSelected ? 'interest-pill-active' : ''}`}
                  onClick={() => toggleInterest(label)}
                  disabled={form.interests.length >= 3 && !isSelected}
                  data-tooltip={tooltip}
                >
                  {isSelected && <span className={`pill-order ${selIdx === 0 ? 'pill-order-primary' : ''}`}>{selIdx + 1}</span>}
                  {label}
                </button>
              )
            })}
          </div>
        </div>
        <div className="holdings-section">
          <div className="holdings-label">Current Holdings <span className="interest-optional">(optional)</span></div>
          {form.holdings.map((h, i) => {
            const pct = rawSum > 0 ? Math.round((parseFloat(h.raw) || 0) / rawSum * 100) : 0
            return (
              <div className="holding-row" key={i}>
                <input
                  className="holding-ticker-input"
                  placeholder="Ticker"
                  value={h.ticker}
                  onChange={e => updateHolding(i, 'ticker', e.target.value.toUpperCase())}
                  maxLength={6}
                />
                <input
                  className="holding-raw-input"
                  type="number"
                  min="0"
                  placeholder="Amount"
                  value={h.raw}
                  onChange={e => updateHolding(i, 'raw', e.target.value)}
                />
                <span className="holding-pct">{h.raw ? `→ ${pct}%` : '→ –'}</span>
                <button className="holding-delete" type="button" onClick={() => removeHolding(i)}>×</button>
              </div>
            )
          })}
          <button className="btn-add-holding" type="button" onClick={addHolding}>+ Add Holding</button>
        </div>
        <div className="form-actions">
          <button type="button" className="btn-clear" onClick={handleClear} disabled={!hasContent}>
            Clear All
          </button>
          <button type="button" className="btn-save-context" onClick={handleSave} disabled={!canSave}>
            Save for Chat
          </button>
        </div>
      </div>
    </div>
  )
}
