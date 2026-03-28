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

export default function HowItWorksPage() {
  return (
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
  )
}
