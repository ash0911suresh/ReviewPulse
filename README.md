# ReviewPulse 🔍

> AI-powered review intelligence for independent authors. Know what your readers think — without refreshing Amazon all day.

**Live demo:** https://review-pulse-six.vercel.app  
**API docs:** https://reviewpulse-4xkw.onrender.com/docs  
**GitHub:** https://github.com/ash0911suresh/ReviewPulse

---

## What it does

Independent authors live and die by Amazon reviews. A single review can shift daily sales by 20-40%. ReviewPulse gives authors a real-time intelligence layer on top of their reviews — without scraping Amazon or paying for enterprise tools.

- **Ingests reviews** for multiple books per author (synthetic mode via Groq/Llama 3.1)
- **LLM analysis** on every review: sentiment, themes, AI-detection, actionability, one-sentence summary
- **Semantic search** across your entire catalog using pgvector — "find reviews mentioning my main character"
- **Trend metrics** — sentiment over time per book, top themes rising or falling
- **AI Highlights** — synthesizes all reviews into 3 insights: what readers loved, main complaint, fix for next book
- **"Since last login"** — surfaces new review activity since your last visit
- **Cost tracking** — tokens used and USD spent per book, visible in the dashboard
- **Async pipeline** — dashboard never blocks on ingestion; jobs run in background

---

## Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLAlchemy 2.0 + asyncpg |
| Database | Supabase (PostgreSQL + pgvector) |
| LLM | Groq (Llama 3.1) via provider-agnostic adapter |
| Frontend | React + Vite + Recharts |
| Deploy | Render (backend) + Vercel (frontend) |

Matches the Tweeds stack exactly: FastAPI + SQLAlchemy + pgvector on the backend, React + Vite on the frontend.

---

## Running locally

### Prerequisites
- Python 3.11+
- Node 18+
- A Supabase project (free tier)
- A Groq API key (free tier)

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@db.YOUR_PROJECT.supabase.co:5432/postgres
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
GROQ_API_KEY=your_groq_key
LLM_PROVIDER=groq

Run migrations and start:
```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API available at `http://localhost:8000` — docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard at `http://localhost:5173`

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/authors/` | Register an author |
| POST | `/books/` | Add book + trigger ingestion |
| GET | `/jobs/{id}` | Poll job status |
| GET | `/reviews/book/{id}` | List reviews with filters |
| GET | `/reviews/trends/{id}` | Sentiment over time |
| POST | `/authors/{id}/search` | Semantic search across catalog |
| GET | `/authors/{id}/whats-new` | New activity since last login |
| GET | `/books/{id}/highlights` | AI highlights (P1 feature) |
| GET | `/metrics` | System observability |

---

## What works / what doesn't / what's next

**Works:** Full ingestion pipeline, LLM analysis, pgvector semantic search, dashboard with charts, trend metrics, AI highlights, cost tracking, multi-tenant isolation, async jobs, structured logging.

**Doesn't work:** Real auth (hardcoded author_id), tests, webhooks, scheduled re-ingest, cross-book comparison UI.

**Next:** Real embeddings (OpenAI text-embedding-3-small), Supabase Auth JWT middleware, Celery + Redis for durable background jobs, response draft generation for actionable reviews.

---

## Architecture decisions

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full design notes.

---

## Hours spent

~9 hours with AI assistance (Claude).
