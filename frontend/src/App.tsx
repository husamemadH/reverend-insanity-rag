import { useState, useRef, useEffect } from 'react'
import type { Message as MsgType, Citation, Chunk } from './types'
import { Message } from './components/Message'
import { InputBar } from './components/InputBar'
import './App.css'

let msgId = 0
const nextId = () => String(++msgId)

export default function App() {
  const [messages, setMessages] = useState<MsgType[]>([])
  const [loading, setLoading] = useState(false)
  const [debugMode, setDebugMode] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendQuery = async (query: string) => {
    const userMsg: MsgType = { id: nextId(), role: 'user', content: query }
    const placeholderId = nextId()
    const placeholder: MsgType = { id: placeholderId, role: 'assistant', content: '', loading: true }

    setMessages(prev => [...prev, userMsg, placeholder])
    setLoading(true)

    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      })
      if (!res.ok) throw new Error(`API error ${res.status}`)
      const data = await res.json()

      setMessages(prev =>
        prev.map(m =>
          m.id === placeholderId
            ? {
                ...m,
                content: data.answer,
                citations: data.citations as Citation[],
                queries: data.queries as string[],
                chunks: data.chunks as Chunk[],
                loading: false,
              }
            : m
        )
      )
    } catch {
      setMessages(prev =>
        prev.map(m =>
          m.id === placeholderId
            ? { ...m, content: 'Error: could not reach the server.', loading: false }
            : m
        )
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-title">
          <span className="header-icon">☯</span>
          Reverend Insanity — Gu Oracle
        </div>
        {debugMode && <span className="debug-badge">Debug ON</span>}
      </header>

      <main className="chat-window">
        {messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">🐛</div>
            <p>Ask anything about the novel.</p>
          </div>
        )}
        {messages.map(m => (
          <Message key={m.id} message={m} debugMode={debugMode} />
        ))}
        <div ref={bottomRef} />
      </main>

      <InputBar
        onSend={sendQuery}
        disabled={loading}
        debugMode={debugMode}
        onToggleDebug={() => setDebugMode(d => !d)}
      />
    </div>
  )
}
