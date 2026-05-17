import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.review import Review
from app.models.book import Book
from app.models.job import IngestionJob
from app.services.llm import get_llm_adapter

logger = logging.getLogger(__name__)

async def run_ingestion_job(job_id: str, book_id: str, author_id: str, db: AsyncSession):
    adapter = get_llm_adapter()

    # Update job to running
    job_result = await db.execute(select(IngestionJob).where(IngestionJob.id == uuid.UUID(job_id)))
    job = job_result.scalar_one()
    job.status = "running"
    await db.commit()

    try:
        # Get book title
        book_result = await db.execute(select(Book).where(Book.id == uuid.UUID(book_id)))
        book = book_result.scalar_one()

        # Generate synthetic reviews
        logger.info(f'{{"msg": "generating reviews", "book_id": "{book_id}", "title": "{book.title}"}}')
        raw_reviews = await adapter.generate_synthetic_reviews(book.title, 20)

        processed = 0
        total_cost = 0.0

        for raw in raw_reviews:
            # Idempotency: skip if external_id already exists
            ext_id = f"{book_id}-{raw.get('reviewer_name', '')}-{raw.get('review_date', '')}"
            existing = await db.execute(select(Review).where(Review.external_id == ext_id))
            if existing.scalar_one_or_none():
                logger.info(f'{{"msg": "skipping duplicate", "external_id": "{ext_id}"}}')
                continue

            review_text = raw.get("review_text", "")

            # Analyze with LLM
            analysis = await adapter.analyze_review(review_text)
            embedding = await adapter.generate_embedding(review_text)

            review = Review(
                author_id=uuid.UUID(author_id),
                book_id=uuid.UUID(book_id),
                external_id=ext_id,
                reviewer_name=raw.get("reviewer_name"),
                rating=float(raw.get("rating", 3)),
                review_text=review_text,
                review_date=datetime.now(timezone.utc),
                sentiment=analysis.sentiment,
                sentiment_confidence=analysis.sentiment_confidence,
                themes=analysis.themes,
                is_ai_generated=analysis.is_ai_generated,
                ai_generated_confidence=analysis.ai_generated_confidence,
                summary=analysis.summary,
                is_actionable=analysis.is_actionable,
                embedding=embedding,
                analysis_tokens_used=analysis.tokens_used,
                analysis_cost_usd=analysis.cost_usd,
                analyzed_at=datetime.now(timezone.utc),
            )
            db.add(review)
            total_cost += analysis.cost_usd
            processed += 1
            job.reviews_processed = processed
            await db.commit()
            logger.info(f'{{"msg": "review saved", "book_id": "{book_id}", "processed": {processed}}}')

        # Update book stats
        book.review_count = processed
        book.total_llm_cost_usd += total_cost
        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc)
        await db.commit()
        logger.info(f'{{"msg": "ingestion complete", "book_id": "{book_id}", "processed": {processed}, "cost": {total_cost}}}')

    except Exception as e:
        logger.error(f'{{"msg": "ingestion failed", "job_id": "{job_id}", "error": "{str(e)}"}}')
        job.status = "failed"
        job.error_message = str(e)
        await db.commit()
        raise
