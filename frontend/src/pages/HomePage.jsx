import SimulationCard from '../components/SimulationCard'

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="feature-card">
      <span className="feature-icon">{icon}</span>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  )
}

const STEPS = [
  "Set up your profile — age, risk level, interests & holdings",
  "Ask anything investment-related — market trends, strategies, specific assets",
  "Get a portfolio grounded in real data & investment strategy",
  "See how it would have performed — with historical simulation",
]

const DEMO_HOLDINGS_SIM = {
  label: "Your Current Portfolio",
  allocations: [
    { ticker: "TLT", name: "US Long-Term Bonds", weight: 40, color: "#6366f1" },
    { ticker: "BND", name: "US Bonds",           weight: 30, color: "#8b5cf6" },
    { ticker: "VNQ", name: "Real Estate",        weight: 20, color: "#a78bfa" },
    { ticker: "IWM", name: "Small Cap",          weight: 10, color: "#c4b5fd" },
  ],
  performance: {
    data_points: [
      { date: "2023-04", value: 100 },
      { date: "2023-06", value: 97 },
      { date: "2023-08", value: 103 },
      { date: "2023-10", value: 96 },
      { date: "2023-12", value: 104 },
      { date: "2024-02", value: 107 },
      { date: "2024-04", value: 103 },
      { date: "2024-06", value: 106 },
      { date: "2024-08", value: 109 },
      { date: "2024-10", value: 105 },
      { date: "2025-01", value: 108 },
      { date: "2025-04", value: 110.1 },
    ],
    total_return_pct: 10.1,
    annualized_return_pct: 4.9,
    period: "2y",
  },
}

const DEMO_SIM = {
  label: "Recommended Portfolio",
  allocations: [
    { ticker: "VTI",  name: "US Total Market", weight: 60, color: "#6366f1" },
    { ticker: "VXUS", name: "International",   weight: 30, color: "#8b5cf6" },
    { ticker: "BND",  name: "US Bonds",        weight: 10, color: "#a78bfa" },
  ],
  performance: {
    data_points: [
      { date: "2023-04", value: 100 },
      { date: "2023-06", value: 104 },
      { date: "2023-08", value: 108 },
      { date: "2023-10", value: 103 },
      { date: "2023-12", value: 112 },
      { date: "2024-02", value: 118 },
      { date: "2024-04", value: 116 },
      { date: "2024-06", value: 121 },
      { date: "2024-08", value: 124 },
      { date: "2024-10", value: 120 },
      { date: "2025-01", value: 126 },
      { date: "2025-04", value: 130.1 },
    ],
    total_return_pct: 30.1,
    annualized_return_pct: 14.1,
    period: "2y",
  },
}

export default function HomePage({ onNavigate }) {
  return (
    <>
      <main className="hero">
        <div className="hero-content">
          <div className="badge">AI-Powered Robo-Advisor</div>
          <h1>
            Smart investing,<br />
            <span className="highlight">built around you.</span>
          </h1>
          <p className="subtitle">
            Tell us your goals. Our AI analyzes market data, builds a
            personalized ETF portfolio, and explains every decision in plain language.
          </p>
          <div className="hero-actions">
            <button className="btn-primary btn-lg" onClick={() => onNavigate('chat')}>Meet Your AI Financial Advisor</button>
          </div>
          <div className="how-steps">
            {STEPS.map((text, i) => (
              <div className="step" key={i}>
                <div className="step-indicator">
                  <div className="step-dot" />
                  {i < STEPS.length - 1 && <div className="step-line" />}
                </div>
                <div className="step-body">
                  <span className="step-num">Step {i + 1}</span>
                  <span className="step-text">{text}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="demo-window">
          <div className="demo-label">Sample conversation — see what Aivestia can do</div>
          <div className="bubble-wrap user">
            <div className="bubble-content">
              <div className="bubble user">
                What&apos;s a good ETF for long-term growth?
              </div>
            </div>
            <div className="avatar">U</div>
          </div>
          <div className="bubble-wrap">
            <div className="avatar">A</div>
            <div className="bubble-content">
              <div className="bubble assistant">
                VTI (Vanguard Total Market) is a strong choice — broad US exposure, low 0.03% expense ratio, and a consistent long-term track record.
              </div>
            </div>
          </div>
          <div className="bubble-wrap user">
            <div className="bubble-content">
              <div className="bubble user">
                I&apos;m 30, medium risk. I hold AAPL &amp; TSLA. What do you recommend?
              </div>
            </div>
            <div className="avatar">U</div>
          </div>
          <div className="bubble-wrap">
            <div className="avatar">A</div>
            <div className="bubble-content">
              <div className="bubble assistant">
                Your holdings are concentrated in tech. Here&apos;s how a diversified ETF portfolio compares historically:
              </div>
              <div className="simulation-group">
                <SimulationCard simulation={DEMO_HOLDINGS_SIM} />
                <SimulationCard simulation={DEMO_SIM} />
              </div>
            </div>
          </div>
        </div>
      </main>

      <section className="features">
        <FeatureCard
          icon="🎯"
          title="Personalized to you"
          desc="Your age, risk tolerance, interests, and current holdings all shape your portfolio — not a generic template."
        />
        <FeatureCard
          icon="🔎"
          title="Transparent decisions"
          desc="Every recommendation comes with a clear explanation. No black-box AI, no guesswork."
        />
        <FeatureCard
          icon="📊"
          title="Backed by real data"
          desc="Live market prices, recent news, and historical simulations — so you can see exactly what you're getting into."
        />
      </section>
    </>
  )
}
