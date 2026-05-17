# ReviewPulse

AI-powered review intelligence for independent authors.

**Live:** https://review-pulse-six.vercel.app  
**API:** https://reviewpulse-4xkw.onrender.com/docs

## Stack
- Backend: FastAPI + SQLAlchemy + Supabase (pgvector)
- LLM: Groq (Llama 3.1) with provider-agnostic adapter
- Frontend: React + Vite + Recharts
- Deploy: Render + Vercel

## Run locally
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
cp .env.example .env  # fill in your keys
alembic upgrade head
uvicorn app.main:app --reload

cd frontend && npm install && npm run dev
