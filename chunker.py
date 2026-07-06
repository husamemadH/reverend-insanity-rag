import re


def count_tokens(text: str) -> int:
    # rough estimate: ~0.75 words per token
    return len(text.split()) * 4 // 3


def rejoin_paragraphs(raw_text: str) -> list[str]:
    """
    PDF extraction gives soft-wrapped lines. This rejoins them into
    real paragraphs by detecting sentence-ending punctuation.
    """
    lines = raw_text.split('\n')
    paras = []
    current = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        current.append(line)
        # paragraph ends at sentence-closing punctuation
        if re.search(r'[.!?…\u201d\u2019"]\s*$', line) or line == '……':
            paras.append(' '.join(current))
            current = []

    if current:
        paras.append(' '.join(current))

    return paras


def chunk_chapter(chapter_num: int, chapter_text: str, summary: str,
                  token_budget: int = 600) -> list[dict]:
    """
    Splits a chapter into paragraph-boundary chunks with overlap.
    Prepends the chapter summary to every chunk.

    Returns a list of chunk dicts:
    {
        chapter, chunk_index, summary,
        body,        <- paragraph text only
        full_text,   <- what gets embedded: summary + body
        token_count,
        paragraph_count
    }
    """
    paragraphs = rejoin_paragraphs(chapter_text)
    summary_tokens = count_tokens(summary)
    effective_budget = token_budget - summary_tokens

    chunks = []
    current_paras = []
    current_tokens = 0

    def make_chunk(paras):
        body = "\n\n".join(paras)
        full_text = f"[CHAPTER {chapter_num} SUMMARY: {summary}]\n\n{body}"
        return {
            "chapter": chapter_num,
            "chunk_index": len(chunks),
            "summary": summary,
            "body": body,
            "full_text": full_text,
            "token_count": count_tokens(full_text),
            "paragraph_count": len(paras),
        }

    for para in paragraphs:
        para_tokens = count_tokens(para)

        if current_tokens + para_tokens > effective_budget and current_paras:
            chunks.append(make_chunk(current_paras))
            last_para = current_paras[-1]
            # overlap: carry last paragraph into next chunk
            current_paras = [last_para, para]
            current_tokens = count_tokens(last_para) + para_tokens
        else:
            current_paras.append(para)
            current_tokens += para_tokens

    if current_paras:
        chunks.append(make_chunk(current_paras))

    return chunks
