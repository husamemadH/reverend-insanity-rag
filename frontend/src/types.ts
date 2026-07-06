export interface Citation {
  chapter: number
  quote: string
}

export interface Chunk {
  chapter: number
  chunk_index: number
  preview: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  queries?: string[]
  chunks?: Chunk[]
  loading?: boolean
}
