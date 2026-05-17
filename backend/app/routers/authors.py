from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.author import Author
from pydantic import BaseModel
import uuid

router = APIRouter()

class AuthorCreate(BaseModel):
    email: str
    supabase_user_id: str

@router.post("/")
async def create_author(data: AuthorCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Author).where(Author.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Author already exists")
    author = Author(email=data.email, supabase_user_id=data.supabase_user_id)
    db.add(author)
    await db.commit()
    await db.refresh(author)
    return {"id": str(author.id), "email": author.email}

@router.get("/{author_id}")
async def get_author(author_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).where(Author.id == uuid.UUID(author_id)))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return {"id": str(author.id), "email": author.email}

from datetime import datetime, timezone
from sqlalchemy import update

@router.get("/{author_id}/whats-new")
async def whats_new(author_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Author).where(Author.id == uuid.UUID(author_id)))
    author = result.scalar_one_or_none()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    
    last_login = author.last_login_at
    now = datetime.now(timezone.utc)

    # Update last login
    author.last_login_at = now
    await db.commit()

    if not last_login:
        return {"message": "Welcome! No previous login found.", "new_reviews": []}

    # Find reviews since last login
    result = await db.execute(
        select(Review).where(
            Review.author_id == uuid.UUID(author_id),
            Review.created_at > last_login
        ).order_by(Review.created_at.desc()).limit(10)
    )
    new_reviews = result.scalars().all()
    return {
        "since": str(last_login),
        "new_review_count": len(new_reviews),
        "new_reviews": [
            {"id": str(r.id), "summary": r.summary, "sentiment": r.sentiment, "book_id": str(r.book_id)}
            for r in new_reviews
        ]
    }

from app.models.review import Review

@router.post("/{author_id}/search")
async def semantic_search(author_id: str, body: dict, db: AsyncSession = Depends(get_db)):
    from app.services.llm import get_llm_adapter
    from sqlalchemy import text
    query = body.get("query", "")
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    adapter = get_llm_adapter()
    embedding = await adapter.generate_embedding(query)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
    result = await db.execute(
        text("""
            SELECT r.id, r.review_text, r.summary, r.sentiment, r.book_id,
                   1 - (r.embedding <=> cast(:embedding as vector)) as score
            FROM reviews r
            WHERE r.author_id = :author_id
            ORDER BY r.embedding <=> cast(:embedding as vector)
            LIMIT 5
        """),
        {"embedding": embedding_str, "author_id": author_id}
    )
    rows = result.all()
    return [{"id": str(r.id), "summary": r.summary, "sentiment": r.sentiment,
             "book_id": str(r.book_id), "score": float(r.score),
             "review_text": r.review_text[:200]} for r in rows]
