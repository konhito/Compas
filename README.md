# Job Compass

Job Compass is an LLM-powered job search app. Tell it what you want to build, set your preferences, and refine the results in a follow-up. The UI and API are served by FastAPI.

| Capability | Implementation |
| --- | --- |
| Tool use and memory | The model calls a typed search tool. PostgreSQL retains the profile and six recent exchanges per session, including IDs and titles from earlier recommendations. |
| Search at scale | pgvector HNSW retrieves semantic candidates and a GIN index supports PostgreSQL full-text search. Reciprocal rank fusion merges the results, then matched skills adjust the ordering. Remote and salary filters apply before reranking. |
| Changing listings | Submit feed batches with stable IDs and increasing revisions. Older updates are ignored and inactive revisions remove listings from search without allowing stale events to resurrect them. |
| LLM quality | The service validates recommendation IDs, retries malformed output once, and falls back to ranked listings. Job cards take facts from the index. Tests cover personalization and unsupported recommendations. |
| Reliability | Docker Compose, a database readiness route, bounded connection pooling and timeouts, a non-root API container, and optimistic concurrency for session writes. |

## Run locally

1. Copy `.env.example` to `.env`. Set a random `APP_TOKEN` of at least 24 characters and your `OPENAI_API_KEY`.
2. Run `docker compose up --build`.
3. Import the included fictional listings. In a PowerShell session, set `$env:APP_TOKEN` to the same token you wrote to `.env`, then run:

```powershell
curl.exe -X POST http://localhost:8000/jobs -H "Authorization: Bearer $env:APP_TOKEN" -H "Content-Type: application/json" --data-binary "@fixtures/jobs.json"
```

4. Open `http://localhost:8000` and enter the application token. Try searching for "Python data pipelines" and follow up with "Which of those involve AI?"

The API is documented at `/docs`. `POST /jobs` takes up to 50 entries per request. Use it from a trusted source connector or scheduled feed job. To close a listing, resend the record with a higher revision and `active: false`. Salary is an annual USD figure from the feed. A salary filter excludes listings without disclosed pay.

## Verification and deployment

Run `python -m unittest discover -s tests -v` for the deterministic quality checks. They use synthetic records and require no API key. GitHub Actions also checks Python syntax.

The included deployment is designed for a trusted single-operator instance. The app token grants both chat and ingestion access. For a public deployment, add user authentication with per-user session authorization, separate ingestion permissions, TLS, and request rate limits. Set up database backups and use migrations for schema changes on an existing database. Monitor provider latency, fallback rate, and retrieval recall before tuning ranking weights or serving a larger dataset.

Reference: [pgvector indexing and filtered scans](https://github.com/pgvector/pgvector#filtering) · [OpenAI Chat Completions](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)

## Ranking evaluation

Run `python -m evals.ranking` to compare semantic-only retrieval against hybrid retrieval plus personalization using fixed candidate lists and human-authored relevance labels. It reports mean reciprocal rank at three (MRR@3) and exits nonzero if a case returns the wrong first result. These fixtures check ranking behavior in isolation. To measure retrieval quality on a live corpus, capture candidate lists from representative queries and label them before tuning weights.
