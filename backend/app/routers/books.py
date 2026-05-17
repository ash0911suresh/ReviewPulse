from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.book import Book
from app.models.job import IngestionJob
from app.services.ingestion import run_ingestion_job
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

router = APIRouter()

class BookCreate(BaseModel):
    author_id: str
    title: str
    isbn: Optional[str] = None
    amazon_url: Optional[str] = None

@router.post("/")
async def create_book(data: BookCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    book = Book(
        author_id=uuid.UUID(data.author_id),
        title=data.title,
        isbn=data.isbn,
        amazon_url=data.amazon_url,
    )
    db.add(book)
    await db.commit()
    await db.refresh(book)

    # Create ingestion job
    job = IngestionJob(
        author_id=uuid.UUID(data.author_id),
        book_id=book.id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Run ingestion in background
    background_tasks.add_task(
        run_ingestion_job,
        str(job.id), str(book.id), data.author_id, db
    )

    return {
        "id": str(book.id),
        "title": book.title,
        "author_id": data.author_id,
        "job_id": str(job.id)
    }

@router.get("/author/{author_id}")
async def get_books(author_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).where(Book.author_id == uuid.UUID(author_id)))
    books = result.scalars().all()
    return [{"id": str(b.id), "title": b.title, "review_count": b.review_count, "total_llm_cost_usd": b.total_llm_cost_usd} for b in books]

@router.get("/{book_id}/highlights")
async def get_highlights(book_id: str, author_id: str, db: AsyncSession = Depends(get_db)):
    import json
    from app.services.llm import get_llm_adapter
    from groq import Groq
    from app.config import settings

    # Get reviews for this book
    result = await db.execute(
        select(Book).where(Book.id == uuid.UUID(book_id), Book.author_id == uuid.UUID(author_id))
    )
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    from app.models.review import Review
    reviews_result = await db.execute(
        select(Review).where(
            Review.book_id == uuid.UUID(book_id),
            Review.author_id == uuid.UUID(author_id)
        ).limit(20)
    )
    reviews = reviews_result.scalars().all()
    if not reviews:
        return {"loved": "No reviews yet", "complaint": "No reviews yet", "fix": "No reviews yet"}

    summaries = " | ".join([r.summary for r in reviews if r.summary])

    client = Groq(api_key=settings.groq_api_key)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"""Based on these book review summaries, give 3 insights for the author.
Respond with ONLY a JSON object:
{{
  "loved": "one sentence: what readers loved most",
  "complaint": "one sentence: the main complaint",
  "fix": "one sentence: one specific thing to improve in next book"
}}

Reviews: {summaries}"""}],
        max_tokens=200,
        temperature=0.3,
    )
    text = response.choices[0].message.content.strip().replace("```json","").replace("```","")
    data = json.loads(text)
    return data
