import ReactMarkdown from 'react-markdown'
import type { Message as MsgType } from '../types'
import { SourceQuotes } from './SourceQuotes'
import { DebugPanel } from './DebugPanel'

interface Props {
  message: MsgType
  debugMode: boolean
}

export function Message({ message, debugMode }: Props) {
  const isUser = message.role === 'user'

  return (
    <div className={`message ${isUser ? 'message-user' : 'message-assistant'}`}>
      <div className="message-role">{isUser ? 'You' : 'Gu Oracle'}</div>
      <div className="message-bubble">
        {message.loading ? (
          <div className="loading-dots">
            <span /><span /><span />
          </div>
        ) : (
          <ReactMarkdown>{message.content}</ReactMarkdown>
        )}
      </div>
      {!isUser && !message.loading && message.citations && message.citations.length > 0 && (
        <SourceQuotes citations={message.citations} />
      )}
      {!isUser && !message.loading && debugMode && message.queries && (
        <DebugPanel queries={message.queries} chunks={message.chunks ?? []} />
      )}
    </div>
  )
}
