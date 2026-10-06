from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import crud
from .database import init_db
from .models import Expense, ExpenseCreate, ExpenseUpdate

app = FastAPI(title="Team Expense Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/expenses", response_model=list[Expense])
def list_expenses(
    category: str | None = None,
    sort_by: str = Query("date", pattern="^(date|amount)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
):
    return crud.list_expenses(category=category, sort_by=sort_by, order=order)

@app.post("/expenses", response_model=Expense, status_code=201)
def create_expense(payload: ExpenseCreate):
    return crud.create_expense(payload)

@app.get("/expenses/{expense_id}", response_model=Expense)
def get_expense(expense_id: int):
    exp = crud.get_expense(expense_id)
    if not exp:
        raise HTTPException(404, "Expense not found")
    return exp

@app.patch("/expenses/{expense_id}", response_model=Expense)
def update_expense(expense_id: int, payload: ExpenseUpdate):
    exp = crud.update_expense(expense_id, payload)
    if not exp:
        raise HTTPException(404, "Expense not found")
    return exp

@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int):
    if not crud.delete_expense(expense_id):
        raise HTTPException(404, "Expense not found")

@app.get("/summary")
def summary():
    return crud.get_summary()