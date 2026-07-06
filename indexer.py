import pickle
import time

import chromadb
import requests
from rank_bm25 import BM25Okapi

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/embeddings"
EMBEDDING_MODEL = "openai/text-embedding-3-small"
CHROMA_DIR = "./chroma_db"
COLLECTION_NAME = "ri_chunks"
BM25_PATH = "bm25_index.pkl"
EMBED_BATCH_SIZE = 10


def embed_texts(texts: list[str], api_key: str) -> list[list[float]]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    embeddings = []
    for i in range(0, len(texts), EMBED_BATCH_SIZE):
        batch = texts[i: i + EMBED_BATCH_SIZE]
        payload = {"model": EMBEDDING_MODEL, "input": batch}
        response = None
        for _ in range(5):
            response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
            if response.ok:
                data = response.json()["data"]
                data.sort(key=lambda x: x["index"])
                embeddings.extend([d["embedding"] for d in data])
                break
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 10)) + 2
                print(f"  rate limited, waiting {wait}s...", end=" ", flush=True)
                time.sleep(wait)
            else:
                response.raise_for_status()
        else:
            assert response is not None
            response.raise_for_status()
        print(f"  embedded {min(i + EMBED_BATCH_SIZE, len(texts))}/{len(texts)}", flush=True)
        time.sleep(1)
    return embeddings


def build_vector_index(chunks: list[dict], api_key: str) -> None:
    print(f"  embedding {len(chunks)} chunks...")
    texts = [c["full_text"] for c in chunks]
    embeddings = embed_texts(texts, api_key)

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    # wipe and recreate so re-runs are idempotent
    client.delete_collection(COLLECTION_NAME) if COLLECTION_NAME in [c.name for c in client.list_collections()] else None
    collection = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    ids = [f"ch{c['chapter']}_c{c['chunk_index']}" for c in chunks]
    documents = [c["body"] for c in chunks]
    metadatas = [
        {"chapter": c["chapter"], "chunk_index": c["chunk_index"], "token_count": c["token_count"]}
        for c in chunks
    ]

    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    print(f"  upserted {len(chunks)} vectors into ChromaDB at {CHROMA_DIR}")


def build_bm25_index(chunks: list[dict]) -> None:
    corpus = [c["body"].lower().split() for c in chunks]
    bm25 = BM25Okapi(corpus)
    with open(BM25_PATH, "wb") as f:
        pickle.dump({"bm25": bm25, "chunks": chunks}, f)
    print(f"  BM25 index saved to {BM25_PATH}")
