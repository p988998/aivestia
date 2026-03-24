import { useState } from 'react'
import './App.css'

export default function App() {
  const [page, setPage] = useState('home')

  return (
    <div className="app">
      <header className="header">
        <div className="logo" onClick={() => setPage('home')} style={{ cursor: 'pointer' }}>
          <span className="logo-icon">◈</span>
          <span className="logo-text">Aivestia</span>
        </div>
        <nav className="nav">
          <a href="#" className={page === 'home' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); setPage('home') }}>How it works</a>
          <a href="#" className={page === 'about' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); setPage('about') }}>About</a>
          <button className="btn-primary">Get Started</button>
        </nav>
      </header>

      {page === 'home' && (
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
                <button className="btn-primary btn-lg">Build My Portfolio</button>
                <button className="btn-ghost">See how it works →</button>
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
              desc="Portfolio logic is deterministic and transparent — no black box investment decisions."
            />
            <FeatureCard
              icon="🤖"
              title="AI-powered explanations"
              desc="GPT-4 reasoning explains why each ETF fits your risk profile and market conditions."
            />
            <FeatureCard
              icon="📊"
              title="Live market data"
              desc="Real-time ETF prices and volatility metrics fetched directly from Yahoo Finance."
            />
          </section>
        </>
      )}

      {page === 'about' && (
        <section className="about">
          <div className="about-inner">
            <div className="about-left">
              <div className="badge">About this project</div>
              <h2>Built to demonstrate<br />real-world system design.</h2>
              <p className="about-desc">
                Aivestia is an educational demo of an AI-powered robo-advisor.
                It is not a licensed financial product. All portfolio suggestions
                are for demonstration purposes only and do not constitute
                investment advice.
              </p>
              <div className="disclaimer">
                ⚠️ Demo only — not financial advice
              </div>
            </div>

            <div className="about-right">
              <div className="stack-section">
                <div className="stack-label">Tech Stack</div>
                <div className="stack-list">
                  <StackItem lang="Java" detail="Spring Boot 3 · REST API · Business logic & orchestration" color="#f89820" />
                  <StackItem lang="Python" detail="FastAPI · OpenAI · LLM explanation & RAG pipeline" color="#3b82f6" />
                  <StackItem lang="React" detail="Vite · UI display only · No business logic" color="#61dafb" />
                </div>
              </div>

              <div className="stack-section">
                <div className="stack-label">Architecture</div>
                <div className="arch-flow">
                  <span className="arch-node">React</span>
                  <span className="arch-arrow">→</span>
                  <span className="arch-node">Spring Boot</span>
                  <span className="arch-arrow">→</span>
                  <span className="arch-node">FastAPI</span>
                  <span className="arch-arrow">→</span>
                  <span className="arch-node">GPT-4o</span>
                </div>
                <p className="arch-note">Services communicate via HTTP. Portfolio allocation is fully deterministic — AI is used only for explanation and reasoning.</p>
              </div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}

function AllocationRow({ ticker, name, weight, color }) {
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

function StackItem({ lang, detail, color }) {
  return (
    <div className="stack-item">
      <span className="stack-lang" style={{ color }}>{lang}</span>
      <span className="stack-detail">{detail}</span>
    </div>
  )
}

function FeatureCard({ icon, title, desc }) {
  return (
    <div className="feature-card">
      <span className="feature-icon">{icon}</span>
      <h3>{title}</h3>
      <p>{desc}</p>
    </div>
  )
}
