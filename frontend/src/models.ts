export interface Model {
  id: string
  label: string
  tag: string
}

export const MODELS: Model[] = [
  { id: 'anthropic/claude-opus-4-5',         label: 'Claude Opus 4.5',     tag: '~$15 / $75 per MTok' },
  { id: 'anthropic/claude-sonnet-4-5',       label: 'Claude Sonnet 4.5',   tag: '~$3 / $15 per MTok' },
  { id: 'openai/gpt-4o',                     label: 'GPT-4o',              tag: '~$2.50 / $10 per MTok' },
  { id: 'google/gemini-2.5-pro',             label: 'Gemini 2.5 Pro',      tag: '~$1.25 / $10 per MTok' },
  { id: 'anthropic/claude-haiku-4-5',        label: 'Claude Haiku 4.5',    tag: '~$0.80 / $4 per MTok' },
  { id: 'openai/gpt-4o-mini',                label: 'GPT-4o mini',         tag: '~$0.15 / $0.60 per MTok' },
  { id: 'google/gemini-2.5-flash',           label: 'Gemini 2.5 Flash',    tag: '~$0.15 / $0.60 per MTok' },
  { id: 'deepseek/deepseek-chat-v3',         label: 'DeepSeek V3',         tag: '~$0.14 / $0.28 per MTok' },
  { id: 'meta-llama/llama-3.3-70b-instruct', label: 'Llama 3.3 70B',       tag: '~$0.12 / $0.30 per MTok' },
]

export const DEFAULT_MODEL_ID = 'anthropic/claude-haiku-4-5'
