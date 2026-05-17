import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import authors, books, reviews, jobs

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","msg":"%(message)s"}'
)

app = FastAPI(title="ReviewPulse API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authors.router, prefix="/authors", tags=["authors"])
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/health")
async def health():
    return {"status": "ok"}

from sqlalchemy import text
from app.database import AsyncSessionLocal

@app.get("/metrics")
async def metrics():
    async with AsyncSessionLocal() as db:
        authors = await db.execute(text("SELECT COUNT(*) FROM authors"))
        books = await db.execute(text("SELECT COUNT(*) FROM books"))
        reviews = await db.execute(text("SELECT COUNT(*) FROM reviews"))
        cost = await db.execute(text("SELECT COALESCE(SUM(analysis_cost_usd),0) FROM reviews"))
        jobs = await db.execute(text("SELECT status, COUNT(*) FROM ingestion_jobs GROUP BY status"))
        return {
            "authors": authors.scalar(),
            "books": books.scalar(),
            "reviews": reviews.scalar(),
            "total_llm_cost_usd": float(cost.scalar()),
            "jobs_by_status": {row[0]: row[1] for row in jobs.all()}
        }
