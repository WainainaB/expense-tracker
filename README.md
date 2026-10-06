# Team Expense Tracker

A small web app to log and review shared team expenses.

## Stack
- **Backend:** Python 3.12, FastAPI, SQLite
- **Frontend:** vanilla HTML/CSS/JavaScript (no build step)
- **Tests:** pytest

## How to run locally

### 1. Backend

    cd backend
    python -m venv .venv

    # Windows:
    .venv\Scripts\activate
    # Mac/Linux:
    source .venv/bin/activate

    pip install -r requirements.txt
    uvicorn app.main:app --reload

The API runs at http://localhost:8000. Interactive docs at http://localhost:8000/docs.

### 2. Frontend (in a new terminal)

    cd frontend
    python -m http.server 5500

Open http://localhost:5500 in your browser.

### 3. Run the tests

    cd backend
    pytest -v

## Key decisions

- **FastAPI + SQLite.** FastAPI gives us validation and interactive docs "for free" through
  Pydantic; SQLite gives us real, file-based persistence with zero setup. Switching to
  Postgres later would only mean changing `app/database.py`.

- **Validation on both ends.** Pydantic enforces types and ranges on the server (returning
  HTTP 422 with field-level messages). The frontend mirrors the same rules so users get
  instant feedback without a round-trip.

- **Vanilla JS frontend.** No build tools means anyone can open the folder and start editing.
  The list, summary, and form share a single `api()` helper so error handling is consistent.

## What I'd do next

- Pagination and text search on `/expenses`
- Swap `@app.on_event("startup")` for the modern FastAPI lifespan handler
- Alembic migrations instead of `CREATE TABLE IF NOT EXISTS`
- Docker Compose so `docker compose up` runs everything
- A Chart.js visualisation on the summary view