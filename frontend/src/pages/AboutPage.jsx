function StackItem({ lang, detail, color }) {
  return (
    <div className="stack-item">
      <span className="stack-lang" style={{ color }}>{lang}</span>
      <span className="stack-detail">{detail}</span>
    </div>
  )
}

export default function AboutPage() {
  return (
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
  )
}
