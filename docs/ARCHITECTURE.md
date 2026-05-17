# Architecture

## Key decisions

**Groq instead of Anthropic:** No free credits available. Adapter pattern means swapping is one config line.

**BackgroundTasks instead of Celery:** Simpler setup for a demo. With real time I'd use Celery + Redis for durability.

**Hash-based embeddings:** Groq doesn't support embeddings. Works for demo but I'd use OpenAI text-embedding-3-small in production.

**Multi-tenant isolation:** Every table has author_id. Every query filters by it. Author A cannot see Author B's data.

## What I cut
- N6 tests: would add mock LLM unit test + isolation test
- N11 real auth: hardcoded author_id; would use Supabase Auth JWT
- F9 cron: would use Render cron for daily re-ingest
- N10 webhooks: would add HMAC-signed POST on job completion
- F6 cross-book comparison: cut to ship dashboard faster

## P1 feature: AI Highlights
Synthesizes all reviews into 3 insights: what readers loved, main complaint, fix for next book. Authors don't have time to read 20 reviews — they need the 3 things that matter in 2 seconds.
