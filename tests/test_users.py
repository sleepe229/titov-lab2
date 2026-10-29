import pytest
from fastapi.testclient import TestClient

from app.main import app, storage

client = TestClient(app)

ALICE = {"name": "Alice", "email": "alice@example.com", "age": 30}
BOB = {"name": "Bob", "email": "bob@example.com"}


@pytest.fixture(autouse=True)
def clean_storage():
    storage.clear()
    yield
    storage.clear()


def create(payload):
    response = client.post("/users", json=payload)
    assert response.status_code == 201
    return response.json()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_user_returns_id_and_fields():
    user = create(ALICE)
    assert user["id"] == 1
    assert user["name"] == "Alice"
    assert user["email"] == "alice@example.com"
    assert "created_at" in user


def test_create_user_duplicate_email_conflict():
    create(ALICE)
    response = client.post("/users", json={**BOB, "email": "ALICE@example.com"})
    assert response.status_code == 409


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "email": "x@example.com"},
        {"name": "X", "email": "not-an-email"},
        {"name": "X", "email": "x@example.com", "age": -1},
        {"email": "x@example.com"},
    ],
)
def test_create_user_validation_error(payload):
    assert client.post("/users", json=payload).status_code == 422


def test_list_users():
    create(ALICE)
    create(BOB)
    users = client.get("/users").json()
    assert [u["name"] for u in users] == ["Alice", "Bob"]


def test_get_user():
    user = create(ALICE)
    response = client.get(f"/users/{user['id']}")
    assert response.status_code == 200
    assert response.json() == user


def test_get_missing_user_404():
    assert client.get("/users/42").status_code == 404


def test_update_user_partial():
    user = create(ALICE)
    response = client.patch(f"/users/{user['id']}", json={"age": 31})
    assert response.status_code == 200
    assert response.json()["age"] == 31
    assert response.json()["name"] == "Alice"


def test_update_user_email_conflict():
    create(ALICE)
    bob = create(BOB)
    response = client.patch(f"/users/{bob['id']}", json={"email": ALICE["email"]})
    assert response.status_code == 409


def test_update_missing_user_404():
    assert client.patch("/users/42", json={"age": 1}).status_code == 404


def test_delete_user():
    user = create(ALICE)
    assert client.delete(f"/users/{user['id']}").status_code == 204
    assert client.get(f"/users/{user['id']}").status_code == 404


def test_delete_missing_user_404():
    assert client.delete("/users/42").status_code == 404


def test_list_users_search_by_name_and_email():
    create(ALICE)
    create(BOB)
    create({"name": "Carol", "email": "carol@test.org"})
    assert [u["name"] for u in client.get("/users?search=ali").json()] == ["Alice"]
    assert [u["name"] for u in client.get("/users?search=EXAMPLE").json()] == ["Alice", "Bob"]


def test_list_users_pagination():
    for i in range(5):
        create({"name": f"U{i}", "email": f"u{i}@example.com"})
    page = client.get("/users?limit=2&offset=2").json()
    assert [u["name"] for u in page] == ["U2", "U3"]


def test_list_users_invalid_limit():
    assert client.get("/users?limit=0").status_code == 422


def test_health_reports_version():
    from app import __version__

    assert client.get("/health").json()["version"] == __version__ == "1.0.1"


def test_count_users():
    create(ALICE)
    create(BOB)
    assert client.get("/users/count").json() == {"count": 2}
    assert client.get("/users/count?search=bob").json() == {"count": 1}
