import { useState, type KeyboardEvent } from 'react'
import { MODELS } from '../models'

interface Props {
  onSend: (query: string) => void
  disabled: boolean
  debugMode: boolean
  onToggleDebug: () => void
  model: string
  onModelChange: (model: string) => void
}

export function InputBar({ onSend, disabled, debugMode, onToggleDebug, model, onModelChange }: Props) {
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

  const current = MODELS.find(m => m.id === model) ?? MODELS[0]

  return (
    <div className="input-bar">
      <div className="model-selector-row">
        <select
          className="model-select"
          value={model}
          onChange={e => onModelChange(e.target.value)}
          disabled={disabled}
        >
          {MODELS.map(m => (
            <option key={m.id} value={m.id}>
              {m.label} — {m.tag}
            </option>
          ))}
        </select>
        <span className="model-tag">{current.tag}</span>
      </div>

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
