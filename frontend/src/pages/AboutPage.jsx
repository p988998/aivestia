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
              <StackItem lang="Python" detail="FastAPI · LangGraph · LangChain · OpenAI GPT-4o / GPT-4o-mini" color="#3b82f6" />
              <StackItem lang="React" detail="Vite · Recharts · SSE streaming" color="#61dafb" />
              <StackItem lang="PostgreSQL" detail="Chat history · Conversation state persistence · psycopg3" color="#336791" />
              <StackItem lang="Pinecone" detail="Vector store · RAG pipeline · text-embedding-3-small" color="#22c55e" />
              <StackItem lang="AWS" detail="Planned deployment · EC2 / RDS / S3" color="#f59e0b" />
            </div>
          </div>

          <div className="stack-section">
            <div className="stack-label">Architecture</div>
            <div className="arch-flow">
              <span className="arch-node">React</span>
              <span className="arch-arrow">→</span>
              <span className="arch-node">FastAPI</span>
              <span className="arch-arrow">→</span>
              <span className="arch-node">LangGraph</span>
              <span className="arch-arrow">→</span>
              <span className="arch-node">Chat / Portfolio Agent</span>
              <span className="arch-arrow">→</span>
              <span className="arch-node">Final LLM</span>
            </div>
            <p className="arch-note">
              Portfolio allocation is fully deterministic — no AI involvement in investment decisions. The LangGraph agent autonomously calls tools (<strong>market data</strong>, <strong>news</strong>, <strong>RAG retrieval</strong>, <strong>portfolio simulation</strong>), then a hallucination check validates the answer before the final LLM generates a polished response.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
