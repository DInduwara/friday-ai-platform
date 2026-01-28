# FRIDAY – Intelligent Conversational AI Platform

FRIDAY is an industrial‑grade conversational AI platform inspired by ChatGPT‑style experiences. It provides authenticated, multi‑conversation chat with persistent history, real‑time streaming responses, tool‑augmented reasoning, and a modern dark UI.

The system is designed with clean architecture, production‑ready patterns, and clear separation between frontend, backend, AI orchestration, and persistence layers.

---

## Key Features

### Authentication & User Management

* Clerk‑based authentication (JWT verified on backend)
* Per‑user isolation using Clerk `user_id`
* Secure API access with bearer tokens

### Conversation Management

* Create unlimited conversations per user
* Sidebar conversation list (ChatGPT‑style)
* Auto‑load last selected conversation
* Conversation metadata (title, timestamps)
* Backend‑enforced user ownership

### Message Persistence

* PostgreSQL persistence for all messages
* Messages linked to conversations and users
* Full history reload on refresh
* Ordered, timestamped message storage

### Real‑time AI Chat

* Streaming responses via Server‑Sent Events (SSE)
* Token‑by‑token UI updates
* Graceful recovery on partial streams
* Assistant and user message separation

### AI Engine & Tooling

* Supervisor‑based orchestration layer
* Tool‑augmented agents (math, weather, todo, launch vehicle, etc.)
* Pluggable LLM backend (Groq / LLaMA)
* Redis‑backed short‑term memory with TTL

### Modern UI/UX

* Dark, glass‑morphism inspired interface
* Responsive layout
* Animated message bubbles
* Agent reasoning panel
* Sidebar chat navigation

### Infrastructure

* Docker Compose‑based local environment
* PostgreSQL for persistence
* Redis for memory + caching
* Async FastAPI backend
* Vite + React frontend

---

## Architecture Overview

```
┌────────────┐       ┌──────────────┐       ┌───────────────┐
│  Frontend  │  API  │   Backend    │  DB   │  PostgreSQL  │
│ (React)   ├──────▶│ (FastAPI)    ├──────▶│  Conversations│
└─────┬──────┘       └─────┬────────┘       └───────────────┘
      │                    │
      │ SSE                │ Redis
      ▼                    ▼
┌────────────┐       ┌──────────────┐
│ Streaming  │       │  AI Engine   │
│ UI Updates │       │  + Tools     │
└────────────┘       └──────────────┘
```

---

## Tech Stack

### Frontend

* React 18
* Vite
* Tailwind CSS
* Framer Motion
* Clerk React SDK

### Backend

* Python 3.11
* FastAPI (async)
* SQLAlchemy (async)
* Pydantic v2
* Uvicorn

### AI & Memory

* Groq API (LLaMA models)
* Supervisor‑based orchestration
* Redis memory backend

### Infrastructure

* Docker & Docker Compose
* PostgreSQL 16
* Redis 7

---

## Project Structure

```
FRIDAY/
├── backend/
│   ├── src/friday/
│   │   ├── api/                # REST & streaming endpoints
│   │   ├── core/               # Auth, config, logging, errors
│   │   ├── engine/             # AI supervisor & orchestration
│   │   ├── llm/                # LLM clients
│   │   ├── memory/             # Redis / in‑memory context
│   │   ├── models/             # AI data models
│   │   ├── tools/              # Tool‑augmented agents
│   │   ├── db/                 # SQLAlchemy models & repos
│   │   └── main.py             # FastAPI app entry
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
│
├── client/
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── App.jsx             # App shell
│   │   ├── main.jsx            # React bootstrap
│   │   └── index.css
│   ├── public/
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── package.json
│
├── docker-compose.yml
├── README.md
└── LICENSE
```

---

## Environment Configuration

### Frontend (`client/.env`)

```
VITE_API_BASE=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxx
```

### Backend (`backend/.env`)

```
FRIDAY_DATABASE_URL=postgresql+asyncpg://friday:friday@postgres:5432/friday
FRIDAY_REDIS_URL=redis://redis:6379/0
FRIDAY_CLERK_ISSUER=https://clerk.yourdomain.com
FRIDAY_CLERK_JWKS_URL=https://clerk.yourdomain.com/.well-known/jwks.json
FRIDAY_GROQ_API_KEY=your_groq_key
```

---

## Running Locally (Docker)

### Prerequisites

* Docker Desktop
* Node.js (optional, Docker handles frontend)

### Start the system

```
docker compose up --build
```

### Access

* Frontend: [http://localhost:5173](http://localhost:5173)
* Backend API: [http://localhost:8000](http://localhost:8000)

---

## Database Inspection

### Via Docker Exec

```
docker exec -it friday-postgres-1 psql -U friday -d friday
```

Useful commands:

```
\dt
SELECT * FROM users;
SELECT * FROM conversations;
SELECT * FROM messages;
```

---

## API Overview

### Conversations

* `GET /api/v1/conversations`
* `POST /api/v1/conversations`
* `GET /api/v1/conversations/{id}/messages`

### Chat

* `POST /api/v1/chat`
* `POST /api/v1/chat/stream`

All endpoints require a valid Clerk JWT.

---

## Design Principles

* Clean architecture & separation of concerns
* Async‑first backend
* Stateless API with persistent storage
* Streaming‑friendly interfaces
* Production‑ready Docker setup

---

## Roadmap

* Conversation auto‑renaming from first user message
* Conversation deletion & archiving
* Pagination for large chat histories
* Conversation search
* Analytics dashboard
* Role‑based access (teams / orgs)
* Vector memory integration

---

## License

MIT License

---

## Author

FRIDAY is built as a production‑grade AI engineering project focusing on scalability, clarity, and real‑world architecture patterns.
