import AllocationRow from '../components/AllocationRow'

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="feature-card">
      <span className="feature-icon">{icon}</span>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  )
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
            <button className="btn-primary btn-lg" onClick={() => onNavigate('chat')}>Build My Portfolio</button>
            <button className="btn-ghost" onClick={() => onNavigate('how-it-works')}>See how it works →</button>
          </div>
        </div>

        <div className="hero-card">
          <div className="card-label">Sample Portfolio · Medium Risk</div>
          <div className="allocation-list">
            <AllocationRow ticker="VTI" name="US Total Market" weight={60} color="#6366f1" />
            <AllocationRow ticker="VXUS" name="International" weight={30} color="#8b5cf6" />
            <AllocationRow ticker="BND" name="US Bonds" weight={10} color="#a78bfa" />
          </div>
          <div className="card-footer">
            <div className="card-stat">
              <span className="stat-label">Amount</span>
              <span className="stat-value">$10,000</span>
            </div>
            <div className="card-stat">
              <span className="stat-label">Horizon</span>
              <span className="stat-value">5 years</span>
            </div>
            <div className="card-stat">
              <span className="stat-label">Risk</span>
              <span className="stat-value risk-medium">Medium</span>
            </div>
          </div>
        </div>
      </main>

      <section className="features">
        <FeatureCard
          icon="⚙️"
          title="Rule-based allocation"
          desc="Portfolio logic is deterministic and transparent — no AI involvement in investment decisions."
        />
        <FeatureCard
          icon="🤖"
          title="LangGraph Agent"
          desc="A ReAct agent autonomously calls tools to gather market data and news context before generating its explanation."
        />
        <FeatureCard
          icon="🔍"
          title="RAG pipeline"
          desc="Live news from Yahoo Finance is embedded into a FAISS vector store and retrieved to ground the AI's reasoning."
        />
      </section>
    </>
  )
}
