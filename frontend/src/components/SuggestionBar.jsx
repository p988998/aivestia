const EMPTY_STATE_SUGGESTIONS = [
  "Build a portfolio for a medium risk investor",
  "Analyze today's financial market",
  "What should I invest in right now?",
]

export default function SuggestionBar({ suggestions, isEmptyState, visible, onSelect }) {
  if (!visible) return null
  const chips = isEmptyState ? EMPTY_STATE_SUGGESTIONS : suggestions
  if (chips.length === 0) return null
  return (
    <div className="suggestion-bar">
      <span className="suggestion-label">You can ask questions like</span>
      {chips.map((s, i) => (
        <button key={i} className="suggestion-chip" onClick={() => onSelect(s)}>
          {s}
        </button>
      ))}
    </div>
  )
}
