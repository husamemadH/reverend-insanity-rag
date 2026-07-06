import json
import time
import requests
from pathlib import Path

# OpenRouter config
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
SUMMARY_MODEL = "meta-llama/llama-3.3-70b-instruct"

SUMMARY_PROMPT = """Summarize this chapter of Reverend Insanity in 3-5 sentences.
Focus on: key plot events, Gu worms used or obtained, characters involved, faction developments.
Be specific with names. Do not editorialize. Do not start with "In this chapter"."""


def generate_summary(chapter_num: int, chapter_text: str, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": SUMMARY_MODEL,
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": f"{SUMMARY_PROMPT}\n\nChapter {chapter_num}:\n{chapter_text[:6000]}"
            }
        ]
    }
    response = None
    for _ in range(6):
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        if response.ok:
            return response.json()["choices"][0]["message"]["content"].strip()
        if response.status_code == 429:
            wait = int(response.headers.get("Retry-After", 20)) + 2
            print(f" rate limited, waiting {wait}s...", end=" ", flush=True)
            time.sleep(wait)
        else:
            response.raise_for_status()
    assert response is not None
    response.raise_for_status()
    raise RuntimeError("failed after 6 attempts")


def load_or_generate_summaries(chapters: dict, api_key: str,
                                cache_path: str = "summaries.json") -> dict:
    """
    Load summaries from cache if they exist, generate missing ones.
    Saves after each chapter so a crash doesn't lose progress.
    chapters: {chapter_num: chapter_text}
    """
    cache = {}
    if Path(cache_path).exists():
        with open(cache_path) as f:
            cache = json.load(f)
        print(f"Loaded {len(cache)} cached summaries")

    for num, text in sorted(chapters.items()):
        key = str(num)
        if key in cache:
            print(f"  chapter {num}: cached")
            continue
        print(f"  chapter {num}: generating...", end=" ", flush=True)
        cache[key] = generate_summary(num, text, api_key)
        print("done")
        time.sleep(4)
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)

    return {int(k): v for k, v in cache.items()}
