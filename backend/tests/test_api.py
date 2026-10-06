import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch, tmp_path):
    db_file = tmp_path / "test.db"
    monkeypatch.setattr("app.database.DB_PATH", db_file)

    from app.main import app
    from app.database import init_db
    init_db()
    with TestClient(app) as c:
        yield c


SAMPLE = {
    "description": "Team lunch",
    "amount": 42.50,
    "category": "food",
    "date": "2025-01-15",
    "paid_by": "Alice",
}


def test_create_and_list_expense(client):
    r = client.post("/expenses", json=SAMPLE)
    assert r.status_code == 201
    body = r.json()
    assert body["description"] == "Team lunch"
    assert body["id"] > 0

    r = client.get("/expenses")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_reject_negative_amount(client):
    bad = {**SAMPLE, "amount": -5}
    r = client.post("/expenses", json=bad)
    assert r.status_code == 422
    assert "amount" in r.text


def test_reject_blank_description(client):
    bad = {**SAMPLE, "description": "   "}
    r = client.post("/expenses", json=bad)
    assert r.status_code == 422


def test_summary_totals(client):
    client.post("/expenses", json=SAMPLE)
    client.post("/expenses", json={**SAMPLE, "amount": 10, "category": "travel", "paid_by": "Bob"})
    client.post("/expenses", json={**SAMPLE, "amount": 7.5, "paid_by": "Bob"})

    r = client.get("/summary")
    data = r.json()

    by_cat = {row["category"]: row["total"] for row in data["by_category"]}
    assert by_cat["food"] == 50.0
    assert by_cat["travel"] == 10.0

    by_person = {row["paid_by"]: row["total"] for row in data["by_person"]}
    assert by_person["Alice"] == 42.5
    assert by_person["Bob"] == 17.5


def test_update_and_delete(client):
    exp_id = client.post("/expenses", json=SAMPLE).json()["id"]

    r = client.patch(f"/expenses/{exp_id}", json={"amount": 99})
    assert r.status_code == 200
    assert r.json()["amount"] == 99

    assert client.delete(f"/expenses/{exp_id}").status_code == 204
    assert client.get(f"/expenses/{exp_id}").status_code == 404