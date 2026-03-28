import { useState } from 'react'

export default function SourcesPanel({ sources }) {
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
