from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class AnalysisResult:
    sentiment: str
    sentiment_confidence: float
    themes: list
    is_ai_generated: bool
    ai_generated_confidence: float
    summary: str
    is_actionable: bool
    tokens_used: int
    cost_usd: float

class BaseLLMAdapter(ABC):
    @abstractmethod
    async def analyze_review(self, review_text: str) -> AnalysisResult:
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> list:
        pass

    @abstractmethod
    async def generate_synthetic_reviews(self, book_title: str, count: int) -> list:
        pass
