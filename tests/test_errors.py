import pytest
from tests.conftest import client, test_user

def test_404_error(client):
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    data = response.json()
    assert data["error"] == True
    assert "message" in data

def test_validation_error(client, auth_headers):
    product_data = {
        "name": "",
        "description": "This is a test product",
        "price": -10,
        "stock": -5
    }
    response = client.post("/products", json=product_data, headers=auth_headers)
    assert response.status_code in [400, 422]
    data = response.json()
    assert data["error"] == True

def test_unauthorized_access(client):
    response = client.get("/users")
    assert response.status_code == 401

def test_forbidden_access(client, test_user, auth_headers):
    response = client.get("/users", headers=auth_headers)
    assert response.status_code == 403
