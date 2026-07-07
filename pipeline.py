"""
Run this once to build the full index.
Orchestrates: extract → summarize → chunk → index

Usage:
    python pipeline.py
"""

import json
import os

from dotenv import load_dotenv

load_dotenv()

from extract import extract_chapters
from summarizer import load_or_generate_summaries
from chunker import chunk_chapter
from indexer import build_vector_index, build_bm25_index

# --- config ---
PDF_PATHS = [
    "data/RI_vol1.pdf",
]
SUMMARIES_CACHE = "summaries.json"
TOKEN_BUDGET = 900
OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]


def run():
    # step 1: extract all chapters from all PDFs
    print("=== EXTRACTING ===")
    all_chapters = {}
    for pdf_path in PDF_PATHS:
        chapters = extract_chapters(pdf_path)
        all_chapters.update(chapters)

    # step 2: generate summaries (cached)
    print("\n=== SUMMARIZING ===")
    summaries = load_or_generate_summaries(
        all_chapters, api_key=OPENROUTER_API_KEY, cache_path=SUMMARIES_CACHE
    )

    # step 3: chunk every chapter
    print("\n=== CHUNKING ===")
    all_chunks = []
    for num in sorted(all_chapters.keys()):
        text = all_chapters[num]
        summary = summaries.get(num, "")
        chunks = chunk_chapter(num, text, summary, token_budget=TOKEN_BUDGET)
        all_chunks.extend(chunks)
        print(f"  chapter {num}: {len(chunks)} chunks")
    print(f"Total chunks: {len(all_chunks)}")

    with open("chunks.json", "w") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print("Saved chunks to chunks.json")

    # step 4: embed and index
    print("\n=== INDEXING ===")
    build_vector_index(all_chunks, OPENROUTER_API_KEY)
    build_bm25_index(all_chunks)
    print("Indexing complete.")


if __name__ == "__main__":
    run()
