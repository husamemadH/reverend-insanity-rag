import fitz
import re


def extract_chapters(pdf_path: str) -> dict:
    """
    Extracts all chapters from a Reverend Insanity PDF.
    Returns {chapter_num: chapter_text}
    """
    doc = fitz.open(pdf_path)
    full_text = "".join(page.get_text() for page in doc)

    pattern = r'(?:^|\n)Chapter (\d+)\s*[–:\-]+\s*[^\n]+\n'
    parts = re.split(pattern, full_text)

    chapters = {}
    for i in range(1, len(parts) - 1, 2):
        num = int(parts[i])
        text = parts[i + 1].strip()
        # strip stray annotation lines e.g. "Chapter 7!!"
        text = re.sub(r'^Chapter \d+[^\n]*\n', '', text)
        chapters[num] = text

    print(f"Extracted {len(chapters)} chapters from {pdf_path}")
    return chapters
