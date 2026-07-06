#!/usr/bin/env bash
trap 'kill 0' EXIT

uv run uvicorn api:server --reload --port 8000 &
cd frontend && npm run dev &

wait
