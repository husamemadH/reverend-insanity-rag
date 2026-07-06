import type { Citation } from '../types'

interface Props {
  citations: Citation[]
}

export function SourceQuotes({ citations }: Props) {
  return (
    <div className="sources">
      {citations.map((c, i) => (
        <div key={i} className="source-card">
          <div className="source-label">Chapter {c.chapter}</div>
          <blockquote className="source-excerpt">"{c.quote}"</blockquote>
        </div>
      ))}
    </div>
  )
}
