import pickle

import chromadb
import requests
from rank_bm25 import BM25Okapi  # noqa: F401 — used via pickle load

from indexer import CHROMA_DIR, COLLECTION_NAME, EMBEDDING_MODEL, BM25_PATH

OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_EMBED_URL = "https://openrouter.ai/api/v1/embeddings"
REWRITE_MODEL = "anthropic/claude-haiku-4-5"
RRF_K = 60

REWRITE_PROMPT = """You are helping search a database of passages from the novel Reverend Insanity.
The main character Fang Yuan is a reincarnator who lived 500 years in a past life before being reborn.
Characters may have hidden histories, past lives, and cultivation backgrounds not obvious from surface-level questions.

Generate 2 alternative search queries to retrieve relevant passages for this question.
Consider both the surface meaning AND deeper context (backstory, past life, history, origin).
Return only the 2 queries, one per line, no numbering or explanation.

Question: {query}"""


def load_indexes() -> tuple:
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    with open(BM25_PATH, "rb") as f:
        saved = pickle.load(f)
    return collection, saved["bm25"], saved["chunks"]


def _embed_query(query: str, api_key: str) -> list[float]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": EMBEDDING_MODEL, "input": [query]}
    response = requests.post(OPENROUTER_EMBED_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def _rewrite_query(query: str, api_key: str) -> list[str]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": REWRITE_MODEL,
        "max_tokens": 80,
        "temperature": 0,
        "messages": [{"role": "user", "content": REWRITE_PROMPT.format(query=query)}],
    }
    response = requests.post(OPENROUTER_CHAT_URL, headers=headers, json=payload)
    response.raise_for_status()
    lines = response.json()["choices"][0]["message"]["content"].strip().split("\n")
    rewrites = [l.strip() for l in lines if l.strip()][:2]
    return [query] + rewrites  # original always first


def _rrf(ranked_lists: list[list[str]], weights: list[float], k: int = RRF_K) -> list[str]:
    scores: dict[str, float] = {}
    for ranked, weight in zip(ranked_lists, weights):
        for rank, doc_id in enumerate(ranked):
            scores[doc_id] = scores.get(doc_id, 0.0) + weight / (k + rank + 1)
    return sorted(scores, key=lambda x: scores[x], reverse=True)


ORIGINAL_GUARANTEED = 3  # slots always reserved for the original query


def retrieve(query: str, api_key: str, top_k: int = 8) -> tuple[list[dict], list[str]]:
    collection, bm25, chunks = load_indexes()
    candidate_k = top_k * 2
    chunk_by_id = {f"ch{c['chapter']}_c{c['chunk_index']}": c for c in chunks}

    queries = _rewrite_query(query, api_key)

    # guaranteed slots: top results from original query always included
    original_embedding = _embed_query(query, api_key)
    original_results = collection.query(
        query_embeddings=[original_embedding],
        n_results=ORIGINAL_GUARANTEED,
        include=["metadatas", "distances"],
    )
    guaranteed_ids = original_results["ids"][0][:ORIGINAL_GUARANTEED]

    # rewrite-based retrieval fills remaining slots via RRF
    rewrite_lists = []
    for q in queries[1:]:  # skip original, already handled above
        embedding = _embed_query(q, api_key)
        results = collection.query(
            query_embeddings=[embedding],
            n_results=candidate_k,
            include=["metadatas", "distances"],
        )
        rewrite_lists.append(results["ids"][0])

    # BM25 on original query
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_top_idx = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:candidate_k]
    bm25_ids = [f"ch{chunks[i]['chapter']}_c{chunks[i]['chunk_index']}" for i in bm25_top_idx]

    rewrite_weight = 0.7 / max(len(rewrite_lists), 1)
    all_lists = rewrite_lists + [bm25_ids]
    all_weights = [rewrite_weight] * len(rewrite_lists) + [0.3]

    rewrite_fused = _rrf(all_lists, all_weights)

    # merge: guaranteed first, then fill remaining slots from rewrite RRF
    seen = set(guaranteed_ids)
    final_ids = list(guaranteed_ids)
    for cid in rewrite_fused:
        if cid not in seen and len(final_ids) < top_k:
            final_ids.append(cid)
            seen.add(cid)

    return [chunk_by_id[cid] for cid in final_ids if cid in chunk_by_id], queries
