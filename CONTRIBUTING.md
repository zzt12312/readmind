# Contributing

ReadMind is a local-first reading workflow app for Obsidian and WeChat Reading notes. Contributions are welcome, especially around parser compatibility, retrieval quality, frontend component cleanup, and documentation.

## Development Setup

Backend:

```bash
cd backend
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Quality Checks

Run these before opening a pull request:

```bash
cd backend
. .venv/bin/activate
pytest
ruff check .
python -m compileall app run.py
```

```bash
cd frontend
npm run typecheck
npm run build
```

## Project Boundaries

- Keep route handlers thin: parse HTTP input, call a service, return a response.
- Put pure business rules in `backend/app/services/*` so they can be tested without Flask or SQLite.
- Prefer explicit payload builders over assembling large response dictionaries in routes.
- Keep frontend pages as composition shells where possible; move reusable logic into composables and reusable UI into components.
- Avoid hardcoding personal local paths or private reading data in reusable modules.

## Testing Priorities

- Markdown parser fixtures for WeChat Reading exports.
- Search ranking and query rewrite behavior.
- Review scheduling and mastery score rules.
- API response contracts for books, notes, QA, and review endpoints.
- Frontend store/composable behavior for polling and streaming.

