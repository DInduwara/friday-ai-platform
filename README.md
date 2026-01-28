# FRIDAY (Industrial Edition)

FRIDAY is a modular multi-agent assistant built with **FastAPI** + **LangGraph Supervisor**.

## Features
- Multi-agent routing (math, poem, weather, launch vehicle, todoist)
- Streaming endpoint (SSE) for step-by-step traces
- Production-ish structure: typed config, error handling, versioned APIs, CI, Docker

## Quickstart (local)

### 1) Backend
```bash
cd backend
cp .env.example .env
# add GROQ_API_KEY (required for chat)
python -m pip install -U pip
pip install ".[dev]"
uvicorn friday.main:app --reload --port 8000
```

Health:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/health/ready

Chat:
- POST http://127.0.0.1:8000/api/v1/chat
- POST http://127.0.0.1:8000/api/v1/chat/stream (SSE)

Payload:
```json
{ "prompt": "What is 12 * 7?" }
```

### 2) Docker
```bash
cp backend/.env.example backend/.env
# set GROQ_API_KEY
docker compose up --build
```

## API Contract

### POST `/api/v1/chat`
Returns a single final reply.

### POST `/api/v1/chat/stream`
SSE stream:
- `done=false` intermediate steps
- `done=true` final supervisor reply

## Security notes
- Never commit real API keys. Use `backend/.env`.
- Keep CORS origins strict in production.

## Roadmap
- Add proper auth (JWT) if exposing externally
- Add persistent conversation state (Redis/Postgres)
- Add structured tool-call telemetry + tracing
- Add frontend streaming UI + deployment pipeline
