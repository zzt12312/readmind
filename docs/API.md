# API Reference

ReadMind exposes its backend under `/api`. The frontend uses these endpoints through `frontend/src/api/modules/*`.

## Error Format

New and refactored endpoints should return structured errors:

```json
{
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "Book not found",
    "detail": ""
  }
}
```

Frontend requests normalize this shape into `ApiError` in `frontend/src/api/client.ts`.

## Core Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/dashboard/overview` | Dashboard metrics, recent books, review summary |
| `GET` | `/api/books` | Book list |
| `GET` | `/api/books/:id` | Book detail and cached summary |
| `GET` | `/api/books/:id/summary` | Get or enqueue AI summary |
| `POST` | `/api/books/:id/summary/regenerate` | Regenerate book summary |
| `GET` | `/api/notes` | Filtered notes, facets, insight summary |
| `POST` | `/api/notes/summarize` | Enqueue note insight generation |
| `POST` | `/api/qa/ask` | Non-streaming QA response |
| `POST` | `/api/qa/stream` | SSE streaming QA response |
| `GET` | `/api/review/today` | Due review cards |
| `POST` | `/api/review/rate` | Save review result |
| `GET` | `/api/import/jobs` | Import/sync job history |
| `POST` | `/api/import/jobs` | Demo-only upload preview; real mode returns `UPLOAD_IMPORT_UNAVAILABLE` |
| `POST` | `/api/import/sync-local` | Enqueue local Vault sync |
| `GET` | `/api/jobs` | Background job list |
| `GET` | `/api/jobs/:id` | Background job detail |
| `POST` | `/api/jobs/:id/retry` | Retry a failed job |
| `GET` | `/api/llm/health` | LLM and embedding status |

## Streaming QA

`POST /api/qa/stream` emits SSE events:

| Event | Payload |
| --- | --- |
| `meta` | Question, references, retrieval mode, query rewrite, evidence summary |
| `status` | Current generation phase, label, detail |
| `delta` | Incremental answer text |
| `done` | Final QA response |

The frontend parser lives in `frontend/src/services/qaStreamClient.ts`.
