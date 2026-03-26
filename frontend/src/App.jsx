import { useState, useRef, useEffect } from 'react'
import './App.css'

function renderMarkdown(text) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // strip [text](url) → text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br />')
}


async function fetchAIResponse(message, sessionId, userProfile = null) {
  const res = await fetch('http://localhost:8000/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, session_id: sessionId, user_profile: userProfile ?? {} }),
  })
  if (!res.ok) throw new Error('AI service error')
  const data = await res.json()
  return { answer: data.answer, sources: data.sources || [] }
}

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
          <a href="#" className={page === 'how-it-works' ? 'nav-active' : ''} onClick={e => { e.preventDefault(); setPage('how-it-works') }}>How it works</a>
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
                <button className="btn-primary btn-lg" onClick={() => setPage('chat')}>Build My Portfolio</button>
                <button className="btn-ghost" onClick={() => setPage('how-it-works')}>See how it works →</button>
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
      )}

      {page === 'how-it-works' && (
        <section className="how-it-works">
          <div className="hiw-header">
            <div className="badge">How it works</div>
            <h2>Three steps to your AI-powered portfolio.</h2>
          </div>
          <div className="hiw-steps">
            <StepCard
              number="01"
              title="Set your parameters"
              desc="Enter your investment amount, risk tolerance (low / medium / high), and time horizon. These inputs drive every decision downstream."
              detail="Amount · Risk Level · Duration"
            />
            <div className="hiw-connector" />
            <StepCard
              number="02"
              title="Portfolio is generated"
              desc="A deterministic rule engine maps your risk level to a fixed ETF allocation. No AI is involved at this stage — the logic is transparent and auditable."
              detail="VTI · VXUS · BND"
            />
            <div className="hiw-connector" />
            <StepCard
              number="03"
              title="Agent reasons with live context"
              desc="A LangGraph ReAct agent autonomously fetches market data and news via Yahoo Finance, retrieves relevant context from a FAISS vector store (RAG), then generates a plain-language explanation and rebalancing suggestion."
              detail="LangGraph · RAG · FAISS · GPT-4o"
            />
          </div>
        </section>
      )}

      {page === 'chat' && <ChatPage onBack={() => setPage('home')} />}

      {page === 'about' && (
        <section className="about">
          <div className="about-inner">
            <div className="about-left">
              <div className="badge">About this project</div>
              <h2>Where AI meets<br />disciplined financial reasoning.</h2>
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
                  <StackItem lang="Python" detail="FastAPI · LangGraph · LangChain · OpenAI LLM · RAG · FAISS" color="#3b82f6" />
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
                  <span className="arch-node">LangGraph Agent</span>
                  <span className="arch-arrow">→</span>
                  <span className="arch-node">GPT-4o</span>
                </div>
                <p className="arch-note">Portfolio allocation is fully deterministic (Java). The LangGraph agent autonomously calls tools — <strong>get_market_data</strong>, <strong>get_recent_news</strong>, <strong>search_financial_context</strong> (RAG) — before generating its final explanation.</p>
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

function StepCard({ number, title, desc, detail }) {
  return (
    <div className="step-card">
      <div className="step-number">{number}</div>
      <h3 className="step-title">{title}</h3>
      <p className="step-desc">{desc}</p>
      <div className="step-detail">{detail}</div>
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

function ChatPage({ onBack }) {
  const [mode, setMode] = useState('chat')
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm your Aivestia advisor. Ask me anything about investing, ETFs, risk levels, or portfolio strategies.", sources: [] }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [portfolioContext, setPortfolioContext] = useState(null)
  const [sessionId] = useState(() => crypto.randomUUID())
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleSend() {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: text, sources: [] }])
    setLoading(true)
    try {
      const { answer, sources } = await fetchAIResponse(text, sessionId, portfolioContext)
      setMessages(prev => [...prev, { role: 'assistant', content: answer, sources }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, the AI service is unavailable. Please make sure it is running on port 8000.', sources: [] }])
    } finally {
      setLoading(false)
    }
  }

  function handleSaveForChat({ age, riskLevel, horizon, interests }) {
    const label = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)
    setPortfolioContext({ age, riskLevel, horizon, interests })
    const interestText = interests?.length ? ` · ${interests.join(', ')}` : ''
    setMessages(prev => [...prev, {
      role: 'system',
      content: `Age: ${age} · Risk: ${label} · Horizon: ${horizon} yr${interestText}`,
      sources: [],
    }])
    setMode('chat')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className="chat-page">
      <div className="chat-header">
        <button className="chat-back" onClick={onBack}>← Back</button>
        <div className="chat-tabs">
          <button className={`tab ${mode === 'chat' ? 'tab-active' : ''}`} onClick={() => setMode('chat')}>Chat</button>
          <button className={`tab ${mode === 'portfolio' ? 'tab-active' : ''}`} onClick={() => setMode('portfolio')}>My Profile</button>
        </div>
        <div className="chat-status"><span className="status-dot" />AI ready</div>
      </div>

      {mode === 'chat' && (
        <>
          <div className="chat-messages">
            {messages.map((msg, i) => (
              msg.role === 'system'
                ? <div key={i} className="system-notice">{msg.content}</div>
                : (
                  <div key={i} className={`bubble-wrap ${msg.role}`}>
                    {msg.role === 'assistant' && <div className="avatar">◈</div>}
                    <div className="bubble-content">
                      {msg.type === 'portfolio'
                        ? <PortfolioResult {...msg.portfolio} />
                        : <div className={`bubble ${msg.role}`} dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }} />
                      }
                      {msg.sources?.length > 0 && (
                        <SourcesPanel sources={msg.sources} />
                      )}
                    </div>
                  </div>
                )
            ))}
            {loading && (
              <div className="bubble-wrap assistant">
                <div className="avatar">◈</div>
                <div className="bubble assistant typing">
                  <span /><span /><span />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          <div className="chat-input-bar">
            <textarea
              className="chat-input"
              placeholder="Ask about ETFs, risk, rebalancing..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button className="chat-send" onClick={handleSend} disabled={!input.trim() || loading}>
              Send →
            </button>
          </div>
        </>
      )}

      {mode === 'portfolio' && <PortfolioForm onSaveForChat={handleSaveForChat} savedProfile={portfolioContext} />}
    </div>
  )
}

const INTERESTS = [
  'Tech & Growth',
  'Dividend Income',
  'ESG / Sustainable',
  'International Markets',
  'REITs / Real Estate',
  'Bonds & Fixed Income',
  'Value Investing',
  'Small & Mid Cap',
]

function PortfolioForm({ onSaveForChat, savedProfile }) {
  const [form, setForm] = useState({
    age: savedProfile?.age ?? '',
    riskLevel: savedProfile?.riskLevel ?? 'medium',
    horizon: savedProfile?.horizon ?? '',
    interests: savedProfile?.interests ?? [],
  })

  function toggleInterest(interest) {
    setForm(f => ({
      ...f,
      interests: f.interests.includes(interest)
        ? f.interests.filter(i => i !== interest)
        : [...f.interests, interest],
    }))
  }

  function handleSave() {
    onSaveForChat({ ...form })
  }

  function handleClear() {
    setForm({ age: '', riskLevel: 'medium', horizon: '', interests: [] })
  }

  const canSave = form.age && form.horizon
  const hasContent = form.age || form.horizon || form.interests.length > 0

  return (
    <div className="portfolio-form-wrap">
      <div className="portfolio-form">
        <h2 className="form-title">My Investor Profile</h2>
        <label className="form-label">
          Age
          <input type="number" min="18" max="100" value={form.age}
            onChange={e => setForm(f => ({ ...f, age: e.target.value }))} />
        </label>
        <label className="form-label">
          Risk Level
          <select value={form.riskLevel} onChange={e => setForm(f => ({ ...f, riskLevel: e.target.value }))}>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </label>
        <label className="form-label">
          Investment Horizon (years)
          <input type="number" min="1" max="50" value={form.horizon}
            onChange={e => setForm(f => ({ ...f, horizon: e.target.value }))} />
        </label>
        <div className="interest-section">
          <div className="interest-label">Interests <span className="interest-optional">(optional)</span></div>
          <div className="interest-pills">
            {INTERESTS.map(interest => (
              <button
                key={interest}
                type="button"
                className={`interest-pill ${form.interests.includes(interest) ? 'interest-pill-active' : ''}`}
                onClick={() => toggleInterest(interest)}
              >
                {interest}
              </button>
            ))}
          </div>
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

function PortfolioResult({ allocations, age, riskLevel, horizon }) {
  const riskColor = { low: '#22c55e', medium: '#fbbf24', high: '#f87171' }[riskLevel]
  const label = riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)
  return (
    <div className="portfolio-result">
      <div className="card-label">Your Portfolio · {label} Risk</div>
      <div className="allocation-list">
        {allocations.map(a => <AllocationRow key={a.ticker} {...a} />)}
      </div>
      <div className="card-footer">
        <div className="card-stat">
          <span className="stat-label">Age</span>
          <span className="stat-value">{age}</span>
        </div>
        <div className="card-stat">
          <span className="stat-label">Horizon</span>
          <span className="stat-value">{horizon} yr</span>
        </div>
        <div className="card-stat">
          <span className="stat-label">Risk</span>
          <span className="stat-value" style={{ color: riskColor }}>{label}</span>
        </div>
      </div>
    </div>
  )
}

function SourcesPanel({ sources }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="sources-panel">
      <button className="sources-toggle" onClick={() => setOpen(o => !o)}>
        {open ? '▾' : '▸'} Sources ({sources.length})
      </button>
      {open && (
        <ul className="sources-list">
          {sources.map((s, i) => (
            <li key={i}>
              <a href={s} target="_blank" rel="noreferrer">{s}</a>
            </li>
          ))}
        </ul>
      )}
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
