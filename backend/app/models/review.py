from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Boolean, Text, Integer
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Review(Base):
    __tablename__ = "reviews"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String, nullable=True, unique=True)
    reviewer_name = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    review_text = Column(Text, nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    sentiment = Column(String, nullable=True)
    sentiment_confidence = Column(Float, nullable=True)
    themes = Column(ARRAY(String), nullable=True)
    is_ai_generated = Column(Boolean, nullable=True)
    ai_generated_confidence = Column(Float, nullable=True)
    summary = Column(String, nullable=True)
    is_actionable = Column(Boolean, nullable=True)
    embedding = Column(Vector(1536), nullable=True)
    analysis_tokens_used = Column(Integer, nullable=True)
    analysis_cost_usd = Column(Float, nullable=True)
    analyzed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    book = relationship("Book", back_populates="reviews")
