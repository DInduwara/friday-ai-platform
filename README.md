# FRIDAY – Intelligent Conversational AI Platform

> A production-grade, multi-agent AI platform built to explore reasoning, orchestration, and real-world system design.


FRIDAY is a **production-grade, full-stack AI chat platform** built to **understand, experiment with, and showcase multi-agent AI behavior** in a real-world system.

The project is intentionally designed and implemented with **enterprise engineering practices** -authentication, persistence, streaming, pagination, cloud deployment, and observability  while keeping the core goal educational: **learning how multi-agent systems reason, route, and collaborate**.

This project is built to demonstrate system design, backend engineering, frontend architecture, and AI integration skills.

https://friday-ai-platform.vercel.app

---

## Core Objective

- Learn and implement multi-agent AI orchestration
- Build a ChatGPT-like UX with real persistence
- Understand streaming AI responses (SSE)
- Practice production-ready backend patterns
- Deploy a real-world cloud architecture (Vercel, Render, Neon, Azure Redis)
- Showcase enterprise-level code quality in a portfolio project

---

## Key Features

### AI & Agent System

- Multi-agent supervisor pattern
- Agent step tracing and visualization
- Streaming AI responses via Server-Sent Events (SSE)
- Pluggable memory backend (Redis / in-memory)
- First-message auto conversation title generation

### Chat System

- Conversation sidebar with search
- Auto-renamed conversations
- Message pagination (load older messages)
- Conversation deletion
- Message history persistence per user

### Authentication

- Clerk authentication (JWT-based)
- Secure backend verification using Clerk JWKS
- Per-user conversation isolation

### Backend (FastAPI)

- Async FastAPI + SQLAlchemy 2.0
- PostgreSQL (Neon)
- Redis-based memory backend (Azure Redis)
- Robust CORS handling
- Environment-driven configuration
- Automatic DB schema creation on startup
- OpenAPI with Bearer authentication support

### Frontend (React + Vite)

- Modern dark enterprise UI
- Real-time streaming responses
- Agent flow inspection panel
- Fully authenticated API communication
- Deployed on Vercel

---

##  What FRIDAY Can Do

FRIDAY is designed as a **general-purpose, multi-agent AI assistant**.
Its capabilities are driven by an internal **agent supervisor** that dynamically routes user requests to the most appropriate agent or tool.

### Conversational AI

- Answer general questions across a wide range of topics
- Maintain conversation context across messages
- Stream responses in real time

### Creative Generation

- Generate poems, short stories, and creative text
- Rewrite or rephrase content
- Brainstorm ideas and outlines
- Explain concepts in simple or technical terms

### Weather Information

- Fetch and present weather reports for user-specified locations
- Answer questions like:
> - “What’s the weather in Colombo today?”
> - “Will it rain tomorrow?”
- Uses a tool-based agent rather than static responses

### Task-Oriented Reasoning

- Break down complex questions into steps
- Route tasks through multiple agents when needed
- Show intermediate reasoning steps in the Agent Flow panel

### Tool Usage (Agent-Driven)

Depending on the request, FRIDAY can:
- Decide when to use external tools
- Decide when pure reasoning is sufficient
- Combine tool results with natural language explanations
Examples:
- Weather lookup + explanation
- Data-style answers + reasoning
- Structured output when appropriate

### Memory & Context Awareness

- Stores conversation history per user
- Uses recent messages as short-term context
- Supports pluggable memory backends (Redis or in-memory)
- Automatically limits memory size for performance

### Multi-Agent Behavior (Core Learning Goal)

- Supervisor agent decides:
> - Which agent should handle the task
> - Whether tools are required
> - When the final response is ready
- Each step is observable in the UI:
> - Routing decisions
> - Tool calls
> - Final answer generation

This makes FRIDAY useful not only as a chatbot, but also as a **learning and inspection platform for multi-agent AI systems**.

---

## Tech Stack

### Frontend

- React (Vite)
- Tailwind CSS
- Clerk (Authentication)
- Framer Motion
- Deployed on **Vercel**

### Backend

- Python 3.11
- FastAPI
- SQLAlchemy (Async)
- Uvicorn
- Deployed on Render

### Infrastructure

- **PostgreSQL**: Neon (Serverless)
- **Redis**: Azure Cache for Redis
- **Authentication**: Clerk
- **Containerization**: Docker (local development)

---

## High-Level Architecture

```
┌────────────┐        ┌──────────────┐
│  Frontend  │──────▶ │   FastAPI    │
│  (Vercel)  │        │   Backend    │
└────────────┘        └──────┬───────┘
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
   │  Neon Postgres│     │ Azure Redis │     │   Clerk     │
   │  Conversations│     │ AI Memory   │     │ Auth / JWT  │
   └─────────────┘     └─────────────┘     └─────────────┘

```

### Project Structure

```
FRIDAY/
├── backend/
│   ├── src/friday/
│   │   ├── api/            # REST & streaming endpoints
│   │   ├── core/           # Auth, config, logging, errors
│   │   ├── engine/         # AI supervisor & agent orchestration
│   │   ├── llm/            # LLM clients & adapters
│   │   ├── memory/         # Redis / in-memory context store
│   │   ├── models/         # AI domain models
│   │   ├── tools/          # Tool-augmented agents
│   │   ├── db/             # SQLAlchemy models & repositories
│   │   └── main.py         # FastAPI application entry point
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Backend container image
│   └── pyproject.toml      # Python dependencies & tooling
│
├── client/
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── App.jsx         # App shell
│   │   ├── main.jsx        # React bootstrap
│   │   └── index.css       # Global styles
│   ├── public/             # Static assets
│   ├── vite.config.js      # Vite configuration
│   ├── tailwind.config.js  # Tailwind CSS config
│   └── package.json        # Frontend dependencies
│
├── docker-compose.yml      # Local dev orchestration
├── README.md               # Project documentation
└── LICENSE                 # Project license
```

---

## Environment Configuration

### Backend .env (Render / Local)

```
FRIDAY_ENV=production
FRIDAY_LOG_LEVEL=INFO

FRIDAY_ALLOWED_ORIGINS=http://localhost:5173,https://your-vercel-domain.vercel.app

FRIDAY_DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<host>/<db>

FRIDAY_MEMORY_BACKEND=redis
FRIDAY_REDIS_URL=redis://:<password>@<host>:6380/0

FRIDAY_CLERK_ISSUER=https://<your-clerk-domain>
FRIDAY_CLERK_JWKS_URL=https://<your-clerk-domain>/.well-known/jwks.json

FRIDAY_DB_AUTO_CREATE=true
```

### Frontend .env
```
VITE_API_BASE=https://your-backend.onrender.com
VITE_CLERK_PUBLISHABLE_KEY=pk_live_xxxxxxxxx

```
### Running Locally (Docker)
```
docker compose up --build
```
Services:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Postgres: localhost:5432
- Redis: localhost:6379

---

## Running Locally (Without Docker)

### Backend

```
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn friday.main:app --reload
```

### Frontend

```
cd client
npm install
npm run dev
```

---

## API Overview

### Conversations

- GET /api/v1/conversations
- POST /api/v1/conversations
- DELETE /api/v1/conversations/{id}

### Messages

- GET /api/v1/conversations/{id}/messages
- Pagination supported

### Chat

- POST /api/v1/chat
- POST /api/v1/chat/stream (SSE)
All endpoints require **Bearer JWT (Clerk)**.

---

## Security Notes

- JWT verification via Clerk JWKS
- No frontend secrets exposed
- CORS restricted by environment
- Per-user data isolation enforced at DB level

---

## Why This Project Matters

This project demonstrates:
- Real understanding of multi-agent AI systems
- Ability to design production-grade architectures
- Experience with cloud deployments
- Strong backend engineering discipline
- Clean, scalable frontend architecture
This is not a tutorial project - it is a **learning-driven, system-level implementation**.

---

## License

### MIT License

Chosen to allow reuse, learning, and demonstration while keeping attribution.

---

## Author

**Dinuka Induwara Bandara**  
Software Engineering Intern · AI Developer  
[LinkedIn](https://www.linkedin.com/in/dinuka-induwara) | [Portfolio](https://dinuka-induwara-portfolio.vercel.app)


