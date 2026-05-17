from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.review import Review
from typing import Optional
import uuid

router = APIRouter()

@router.get("/book/{book_id}")
async def get_reviews(
    book_id: str,
    author_id: str = Query(...),
    sentiment: Optional[str] = None,
    is_actionable: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db)
):
    query = select(Review).where(
        Review.book_id == uuid.UUID(book_id),
        Review.author_id == uuid.UUID(author_id)  # multi-tenant isolation
    )
    if sentiment:
        query = query.where(Review.sentiment == sentiment)
    if is_actionable is not None:
        query = query.where(Review.is_actionable == is_actionable)
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    reviews = result.scalars().all()
    return [{"id": str(r.id), "review_text": r.review_text, "sentiment": r.sentiment,
             "themes": r.themes, "summary": r.summary, "rating": r.rating,
             "is_actionable": r.is_actionable, "review_date": str(r.review_date)} for r in reviews]

from sqlalchemy import func, cast
from sqlalchemy.types import Date

@router.get("/trends/{book_id}")
async def get_trends(book_id: str, author_id: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(
            cast(Review.review_date, Date).label("date"),
            Review.sentiment,
            func.count(Review.id).label("count")
        ).where(
            Review.book_id == uuid.UUID(book_id),
            Review.author_id == uuid.UUID(author_id)
        ).group_by(cast(Review.review_date, Date), Review.sentiment)
        .order_by(cast(Review.review_date, Date))
    )
    rows = result.all()
    return [{"date": str(r.date), "sentiment": r.sentiment, "count": r.count} for r in rows]
