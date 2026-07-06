import { useState } from 'react'
import type { Chunk } from '../types'

interface Props {
  queries: string[]
  chunks: Chunk[]
}

export function DebugPanel({ queries, chunks }: Props) {
  const [chunksOpen, setChunksOpen] = useState(false)

  return (
    <div className="debug-panel">
      <div className="debug-section">
        <div className="debug-label">🔍 Query Expansion</div>
        <ul className="debug-queries">
          {queries.map((q, i) => (
            <li key={i} className={i === 0 ? 'query-original' : 'query-rewrite'}>
              {i === 0 ? '◆ original' : `◇ rewrite ${i}`}: {q}
            </li>
          ))}
        </ul>
      </div>

      {chunks.length > 0 && (
        <div className="debug-section">
          <button className="debug-chunks-toggle" onClick={() => setChunksOpen(o => !o)}>
            {chunksOpen ? '▾' : '▸'} Retrieved Chunks ({chunks.length})
          </button>
          {chunksOpen && (
            <div className="debug-chunks-list">
              {chunks.map((c, i) => (
                <div key={i} className="debug-chunk-card">
                  <div className="debug-chunk-label">Ch{c.chapter} · Chunk {c.chunk_index}</div>
                  <div className="debug-chunk-preview">{c.preview}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
