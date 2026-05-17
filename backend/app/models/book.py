from sqlalchemy import Column, String, ForeignKey, DateTime, Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone
from app.database import Base

class Book(Base):
    __tablename__ = "books"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    author_id = Column(UUID(as_uuid=True), ForeignKey("authors.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    isbn = Column(String, nullable=True)
    amazon_url = Column(String, nullable=True)
    total_llm_cost_usd = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    author = relationship("Author", back_populates="books")
    reviews = relationship("Review", back_populates="book", cascade="all, delete")
    jobs = relationship("IngestionJob", back_populates="book", cascade="all, delete")
