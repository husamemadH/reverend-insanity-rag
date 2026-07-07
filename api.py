import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv()

from app import ask, DEFAULT_MODEL

server = FastAPI()
server.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    query: str
    model: str = DEFAULT_MODEL


class Citation(BaseModel):
    chapter: int
    quote: str


class Chunk(BaseModel):
    chapter: int
    chunk_index: int
    preview: str


class ChatResponse(BaseModel):
    answer: str
    citations: list[Citation]
    queries: list[str]
    chunks: list[Chunk]


@server.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set")
    answer, citations_raw, queries, raw_chunks = ask(req.query, api_key, model=req.model)
    citations = [
        Citation(chapter=c.get("chapter", 0), quote=c.get("quote", ""))
        for c in citations_raw
        if c.get("quote")
    ]
    chunks = [
        Chunk(chapter=c["chapter"], chunk_index=c["chunk_index"], preview=c["body"])
        for c in raw_chunks
    ]
    return ChatResponse(answer=answer, citations=citations, queries=queries, chunks=chunks)
