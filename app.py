import json
import os
import sys

import requests
from dotenv import load_dotenv

from retriever import retrieve

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-haiku-4-5"

SYSTEM_PROMPT = """You are an expert on the web novel Reverend Insanity.
Answer questions using only the provided context passages.
If the context doesn't contain enough information, say so clearly.

Give complete, well-explained answers — go beyond just stating facts, but stay focused and don't ramble.

Respond with valid JSON only, in this exact format:
{
  "answer": "your answer here",
  "citations": [
    {"chapter": 2, "quote": "exact sentence or phrase from the context that supports your answer"}
  ]
}

Rules:
- citations must be verbatim excerpts from the context, not paraphrases
- only include quotes you actually used — max 3
- if nothing was used, citations should be an empty array
- no markdown, no extra keys, valid JSON only"""


def format_context(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        parts.append(f"[Chapter {c['chapter']}, Chunk {c['chunk_index']}]\n{c['body']}")
    return "\n\n".join(parts)


def print_retrieved_chunks(chunks: list[dict]) -> None:
    print("\n--- Retrieved Chunks ---")
    for i, c in enumerate(chunks):
        preview = c["body"][:100].replace("\n", " ")
        print(
            f"  [{i + 1}] Ch{c['chapter']} chunk {c['chunk_index']} ({c['token_count']} tokens): {preview}..."
        )
    print("------------------------\n")


def ask(query: str, api_key: str, debug: bool = False, model: str = DEFAULT_MODEL) -> tuple[str, list[dict], list[str], list[dict]]:
    chunks, queries = retrieve(query, api_key, top_k=8)
    if debug:
        print(f"\n--- Rewritten Queries ---\n" + "\n".join(f"  {q}" for q in queries) + "\n")
        print_retrieved_chunks(chunks)
    context = format_context(chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {query}",
        },
    ]
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": model, "messages": messages, "max_tokens": 1000, "temperature": 0.7}
    response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    data = response.json()
    if "choices" not in data:
        raise RuntimeError(f"Unexpected API response: {data}")

    raw = data["choices"][0]["message"]["content"].strip()
    # strip markdown code fences if the model wraps its JSON
    clean = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        parsed = json.loads(clean)
        answer = parsed.get("answer", raw)
        citations = parsed.get("citations", [])
    except json.JSONDecodeError:
        answer = raw
        citations = []

    return answer, citations, queries, chunks


if __name__ == "__main__":
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    debug = "--debug" in sys.argv
    while True:
        query = input("\nAsk a question (or 'quit'): ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        answer, _, _, _ = ask(query, api_key, debug=debug)
        print("\n" + answer)
