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
        <h2>Four steps to your AI-powered portfolio.</h2>
      </div>
      <div className="hiw-steps">
        <StepCard
          number="01"
          title="Set up your profile"
          desc="Tell us your age, risk tolerance, interests, and current holdings."
          detail="Age · Risk Level · Interests · Holdings"
        />
        <div className="hiw-connector" />
        <StepCard
          number="02"
          title="Ask anything"
          desc="Chat freely about market trends, investment strategies, or specific assets."
          detail="Market Data · News · RAG"
        />
        <div className="hiw-connector" />
        <StepCard
          number="03"
          title="Get your portfolio"
          desc="Receive a personalized ETF allocation grounded in real data and investment strategy."
          detail="Rule-based · GPT-4o · Strategy"
        />
        <div className="hiw-connector" />
        <StepCard
          number="04"
          title="See the simulation"
          desc="Compare your recommended portfolio vs. current holdings with historical performance charts."
          detail="Historical Simulation · Performance"
        />
      </div>
    </section>
  )
}
