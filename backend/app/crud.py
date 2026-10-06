from typing import Optional
from .database import get_connection
from .models import ExpenseCreate, ExpenseUpdate

def create_expense(data: ExpenseCreate) -> dict:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO expenses (description, amount, category, date, paid_by) "
            "VALUES (?, ?, ?, ?, ?)",
            (data.description, data.amount, data.category,
             data.date.isoformat(), data.paid_by),
        )
        conn.commit()
        return get_expense(cur.lastrowid)

def get_expense(expense_id: int) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM expenses WHERE id = ?", (expense_id,)
        ).fetchone()
        return dict(row) if row else None

def list_expenses(category: Optional[str] = None,
                  sort_by: str = "date",
                  order: str = "desc") -> list[dict]:
    sort_col = {"date": "date", "amount": "amount"}.get(sort_by, "date")
    order_dir = "ASC" if order.lower() == "asc" else "DESC"

    sql = "SELECT * FROM expenses"
    params: list = []
    if category:
        sql += " WHERE category = ?"
        params.append(category)
    sql += f" ORDER BY {sort_col} {order_dir}"

    with get_connection() as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]

def update_expense(expense_id: int, data: ExpenseUpdate) -> Optional[dict]:
    existing = get_expense(expense_id)
    if not existing:
        return None
    fields = data.model_dump(exclude_unset=True)
    if not fields:
        return existing
    if "date" in fields and fields["date"] is not None:
        fields["date"] = fields["date"].isoformat()

    set_clause = ", ".join(f"{k} = ?" for k in fields)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE expenses SET {set_clause} WHERE id = ?",
            (*fields.values(), expense_id),
        )
        conn.commit()
    return get_expense(expense_id)

def delete_expense(expense_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        return cur.rowcount > 0

def get_summary() -> dict:
    with get_connection() as conn:
        by_cat = conn.execute(
            "SELECT category, SUM(amount) AS total, COUNT(*) AS count "
            "FROM expenses GROUP BY category ORDER BY total DESC"
        ).fetchall()
        by_person = conn.execute(
            "SELECT paid_by, SUM(amount) AS total, COUNT(*) AS count "
            "FROM expenses GROUP BY paid_by ORDER BY total DESC"
        ).fetchall()
    return {
        "by_category": [dict(r) for r in by_cat],
        "by_person": [dict(r) for r in by_person],
    }