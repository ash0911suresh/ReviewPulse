import json
import time
import asyncio
import logging
from groq import Groq
from app.services.llm.base import BaseLLMAdapter, AnalysisResult
from app.config import settings

logger = logging.getLogger(__name__)

class GroqAdapter(BaseLLMAdapter):
    def __init__(self):
        self.client = Groq(api_key=settings.groq_api_key)
        self.model = "llama-3.1-8b-instant"
        self.cost_per_token = 0.0000001

    async def analyze_review(self, review_text: str) -> AnalysisResult:
        prompt = f"""Analyze this book review and respond with ONLY a JSON object, no other text:

Review: {review_text}

JSON format:
{{
  "sentiment": "positive" or "mixed" or "negative",
  "sentiment_confidence": 0.0 to 1.0,
  "themes": ["list", "of", "themes", "from: pacing, characters, ending, cover, narration, plot, writing_style, world_building"],
  "is_ai_generated": true or false,
  "ai_generated_confidence": 0.0 to 1.0,
  "summary": "one sentence summary",
  "is_actionable": true or false
}}"""

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=300,
                    temperature=0.1,
                )
                text = response.choices[0].message.content.strip()
                text = text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
                tokens = response.usage.total_tokens
                return AnalysisResult(
                    sentiment=data.get("sentiment", "mixed"),
                    sentiment_confidence=float(data.get("sentiment_confidence", 0.8)),
                    themes=data.get("themes", []),
                    is_ai_generated=data.get("is_ai_generated", False),
                    ai_generated_confidence=float(data.get("ai_generated_confidence", 0.1)),
                    summary=data.get("summary", ""),
                    is_actionable=data.get("is_actionable", False),
                    tokens_used=tokens,
                    cost_usd=tokens * self.cost_per_token,
                )
            except Exception as e:
                logger.error(f'{{"msg": "LLM analyze error", "attempt": {attempt}, "error": "{str(e)}"}}')
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
        raise Exception("LLM analysis failed after 3 attempts")

    async def generate_embedding(self, text: str) -> list[float]:
        # Groq doesn't support embeddings, use a simple hash-based fallback
        # In production, swap to OpenAI/Cohere embeddings
        import hashlib
        import math
        hash_bytes = hashlib.sha256(text.encode()).digest()
        embedding = []
        for i in range(0, min(len(hash_bytes) * 8, 1536)):
            byte_idx = (i // 8) % len(hash_bytes)
            bit_idx = i % 8
            val = (hash_bytes[byte_idx] >> bit_idx) & 1
            embedding.append(float(val) * 0.1 + math.sin(i * 0.1) * 0.01)
        while len(embedding) < 1536:
            embedding.append(0.0)
        return embedding[:1536]

    async def generate_synthetic_reviews(self, book_title: str, count: int) -> list[dict]:
        prompt = f"""Generate {count} realistic Amazon book reviews for a book called "{book_title}".
Respond with ONLY a JSON array, no other text:
[
  {{
    "reviewer_name": "name",
    "rating": 1-5,
    "review_text": "review text (2-4 sentences)",
    "review_date": "2024-01-15"
  }}
]
Make them varied: different ratings, sentiments, and topics."""

        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=4000,
                    temperature=0.8,
                )
                text = response.choices[0].message.content.strip()
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except Exception as e:
                logger.error(f'{{"msg": "synthetic generation error", "attempt": {attempt}, "error": "{str(e)}"}}')
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
        raise Exception("Synthetic review generation failed")
