# Adaptive RAG Orchestrator

A cost-aware AI inference system that automatically decides which strategy to use for each incoming question — cache, small LLM, large LLM, or RAG — based on question complexity and tenant type.

## What It Does

Most AI systems treat every question the same way: always use the same model, always follow the same path. This is slow and expensive.

This system is smarter. When a question comes in:

1. Checks cache first — if the same question was asked before, returns instantly without calling any LLM
2. Classifies the question — simple or complex, based on keywords and word count
3. Selects the right model — small fast model for simple questions, large powerful model for complex ones
4. Decides if RAG is needed — if complex, searches Qdrant for relevant documents and gives them to the LLM as context
5. Logs everything — every request is stored in PostgreSQL for metrics and analysis

## Architecture

```
Incoming Request
      ↓
Rate Limit Check (tenant_service.py)
      ↓
Cache Lookup (Redis)
  → Hit: return instantly
  → Miss: continue
      ↓
Question Classifier (router_service.py)
  → simple / complex
      ↓
Model Selection
  → free + simple   → llama-3.1-8b-instant
  → free + complex  → llama-3.3-70b-versatile
  → premium         → llama-3.3-70b-versatile always
      ↓
RAG Decision (rag_service.py)
  → complex: search Qdrant for relevant documents
  → simple: skip RAG
      ↓
LLM Call (llm_service.py → Groq)
      ↓
Save to Cache + Log to PostgreSQL
      ↓
Return Response
```

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | REST API framework |
| Groq | LLM provider (Llama models) |
| Qdrant | Vector database for semantic search |
| SentenceTransformers | Text to vector embedding |
| Redis (Upstash) | Semantic cache |
| PostgreSQL | Request logging and metrics |
| SQLAlchemy | ORM for PostgreSQL |
| Docker | Containerization |

## Models

- **llama-3.1-8b-instant** — Fast, lightweight model for simple questions
- **llama-3.3-70b-versatile** — Powerful model for complex questions requiring reasoning

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/v1/health | Health check |
| POST | /api/v1/ask | Ask a question |
| POST | /api/v1/documents | Add a document to vector DB |
| GET | /api/v1/metrics | System metrics and statistics |
| GET | /api/v1/eval | Run automated evaluation pipeline |

## Request Example

```json
POST /api/v1/ask
{
  "question": "What is the return policy?",
  "tenant": "free"
}
```

Response:

```json
{
  "question": "What is the return policy?",
  "answer": "Products can be returned within 30 days...",
  "model": "llama-3.3-70b-versatile",
  "tokens_used": 294,
  "duration_ms": 3174,
  "strategy": "rag"
}
```

## Tenant Types

| Tenant | Model | Rate Limit | Max Tokens |
|---|---|---|---|
| free | llama-3.1-8b-instant | 10 req/min | 512 |
| premium | llama-3.3-70b-versatile | 100 req/min | 2048 |
| enterprise | llama-3.3-70b-versatile | 1000 req/min | 4096 |

## Strategy Types

- **cache_hit** — Returned from Redis cache, 0 tokens used
- **simple_llm** — Answered by small model directly
- **complex_llm** — Answered by large model directly
- **rag** — Documents retrieved from Qdrant, large model used with context

## Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with your API keys
6. Run: `python -m uvicorn app.main:app --reload`

## Environment Variables

```
GROQ_API_KEY=
DATABASE_URL=
UPSTASH_REDIS_URL=
UPSTASH_REDIS_TOKEN=
QDRANT_URL=
QDRANT_API_KEY=
DEBUG=True
```