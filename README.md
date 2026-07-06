# Reverend Insanity RAG

## Project structure

```
ri_rag/
├── extract.py       PDF → chapter text
├── chunker.py       chapter text → chunks  
├── summarizer.py    chapter text → summary (OpenRouter)
├── indexer.py       chunks → vector DB + BM25  [TODO]
├── retriever.py     query → relevant chunks    [TODO]
├── app.py           chatbot interface          [TODO]
├── pipeline.py      run once to build index
├── summaries.json   cached chapter summaries (generated)
├── requirements.txt
└── data/
    └── Reverend_Insanity_vol_1.pdf
```

## Setup
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your OpenRouter key
3. Put PDFs in `data/`
4. Run `python pipeline.py` to build the index
5. Run `python app.py` to query

## Status
- [x] extract.py
- [x] chunker.py
- [x] summarizer.py
- [ ] indexer.py
- [ ] retriever.py
- [ ] app.py
