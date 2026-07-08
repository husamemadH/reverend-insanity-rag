# Reverend Insanity RAG

A RAG (Retrieval-Augmented Generation) chatbot for the web novel **Reverend Insanity**.
Ask questions about the novel and get answers with cited passages.

The index is pre-built and included in the repo — if you're using this for Reverend Insanity,
you don't need to touch anything. Just add your OpenRouter key and run it.

---

## Quick Start (Reverend Insanity)

```bash
# 1. Install dependencies
uv sync
cd frontend && npm install && cd ..

# 2. Add your OpenRouter key
echo "OPENROUTER_API_KEY=your_key_here" > .env

# 3. Run
./dev.sh
```

Open http://localhost:5173

---

## Using With a Different Novel

The pipeline is generic and works with any novel in PDF format. Three things need updating:

**`summarizer.py`** — change the summary prompt to reference your novel and its key terms
```python
SUMMARY_PROMPT = """Summarize this chapter of [Your Novel] in 3-5 sentences.
Focus on: key plot events, characters involved, important items or abilities.
Be specific with names. Do not editorialize."""
```

**`retriever.py`** — update the query rewrite prompt to reflect your novel's domain
```python
REWRITE_PROMPT = """You are helping search a database of passages from [Your Novel].
Generate 2 alternative search queries to retrieve relevant passages for this question.
..."""
```

**`app.py`** — update the system prompt
```python
SYSTEM_PROMPT = """You are an expert on the web novel [Your Novel].
Answer questions using only the provided context passages..."""
```

Then drop your PDF in `data/`, update `PDF_PATHS` in `pipeline.py`, and rebuild the index:
```bash
python pipeline.py
```

---

## Project Structure

```
├── extract.py       PDF → chapter text
├── chunker.py       chapter text → chunks with overlap
├── summarizer.py    chapter text → summary (prepended to each chunk for better retrieval)
├── indexer.py       chunks → ChromaDB vector index + BM25 index
├── retriever.py     query → relevant chunks (hybrid search + query rewriting + RRF)
├── app.py           query → answer (retrieval + generation)
├── api.py           FastAPI server
├── pipeline.py      run once to build the full index
├── chunks.json      pre-built chunk index
├── bm25_index.pkl   pre-built BM25 index
├── chroma_db/       pre-built vector store
├── summaries.json   cached chapter summaries
└── frontend/        React + Vite UI
```

## Stack

- **Retrieval**: ChromaDB (vector search) + BM25 (keyword search) merged with RRF
- **Embeddings**: `openai/text-embedding-3-small` via OpenRouter
- **Query rewriting**: `anthropic/claude-haiku-4-5` via OpenRouter
- **Summarization**: `google/gemini-2.5-flash` via OpenRouter
- **Generation**: selectable in the UI (9 models available)
- **Frontend**: React, TypeScript, Vite
