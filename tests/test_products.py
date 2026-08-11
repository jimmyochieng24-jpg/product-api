import pytest

def test_create_product(client, auth_headers):
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    response = client.post("/products", json=product_data, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == product_data["name"]
    assert data["price"] == product_data["price"]

def test_list_products(client, auth_headers):
    # Create a product with unique name
    product_data = {
        "name": "List Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    assert create_response.status_code == 201
    created_product = create_response.json()
    # List products
    response = client.get("/products", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    # Find the product we just created
    found = any(p["name"] == "List Test Product" for p in data)
    assert found

def test_get_product(client, auth_headers):
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    product_id = create_response.json()["id"]
    response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == product_data["name"]

def test_get_product_not_found(client, auth_headers):
    response = client.get("/products/99999", headers=auth_headers)
    assert response.status_code == 404

def test_update_product(client, auth_headers):
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    product_id = create_response.json()["id"]
    update_data = {"name": "Updated Product", "price": 149.99}
    response = client.patch(f"/products/{product_id}", json=update_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]
    assert response.json()["price"] == update_data["price"]

def test_delete_product(client, auth_headers):
    product_data = {
        "name": "Test Product",
        "description": "This is a test product",
        "price": 99.99,
        "stock": 10
    }
    create_response = client.post("/products", json=product_data, headers=auth_headers)
    product_id = create_response.json()["id"]
    response = client.delete(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 204
    response = client.get(f"/products/{product_id}", headers=auth_headers)
    assert response.status_code == 404
