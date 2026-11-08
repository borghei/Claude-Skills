"""Hand-written tests for the sample Users API (input for coverage_analyzer.py)."""
import httpx

BASE_URL = "http://localhost:8000"


def test_list_users_returns_users():
    response = httpx.get(f"{BASE_URL}/users")
    assert response.status_code == 200
    assert response.json()[0]["email"]


def test_get_user_by_id():
    response = httpx.get(f"{BASE_URL}/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_create_user_status_only():
    response = httpx.post(f"{BASE_URL}/users", json={"email": "new@example.com"},
                          headers={"Authorization": "Bearer test-token"})
    assert response.status_code == 201
