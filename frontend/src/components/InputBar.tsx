import { useState, type KeyboardEvent } from 'react'

interface Props {
  onSend: (query: string) => void
  disabled: boolean
  debugMode: boolean
  onToggleDebug: () => void
}

export function InputBar({ onSend, disabled, debugMode, onToggleDebug }: Props) {
  const [value, setValue] = useState('')

  const handleSend = () => {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  const handleKey = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="input-bar">
      <div className="input-wrap">
        <textarea
          className="input-field"
          placeholder="Ask about Reverend Insanity..."
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={handleKey}
          rows={1}
          disabled={disabled}
        />
        <div className="input-actions">
          <button
            className={`debug-toggle ${debugMode ? 'debug-active' : ''}`}
            onClick={onToggleDebug}
            title="Toggle debug mode"
          >
            🔍
          </button>
          <button
            className="send-btn"
            onClick={handleSend}
            disabled={disabled || !value.trim()}
          >
            Send
          </button>
        </div>
      </div>
      <p className="input-hint">Enter to send · Shift+Enter for new line</p>
    </div>
  )
}
