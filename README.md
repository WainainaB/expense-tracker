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
