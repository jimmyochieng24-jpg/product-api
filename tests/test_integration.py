import pytest
from tests.conftest import client, test_user

def test_full_crud_flow(client, test_user):
    """Test the full CRUD flow from registration to deletion."""
    # Register user
    client.post("/register", json=test_user)
    # Login
    login_resp = client.post(
        "/login",
        data={"username": test_user["username"], "password": test_user["password"]}
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product
    prod_data = {"name": "Integration Product", "price": 49.99, "stock": 5}
    create_resp = client.post("/products", json=prod_data, headers=headers)
    assert create_resp.status_code == 201
    prod_id = create_resp.json()["id"]

    # Get product
    get_resp = client.get(f"/products/{prod_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Integration Product"

    # Update product
    update_data = {"price": 59.99}
    patch_resp = client.patch(f"/products/{prod_id}", json=update_data, headers=headers)
    assert patch_resp.status_code == 200
    assert patch_resp.json()["price"] == 59.99

    # Delete product
    del_resp = client.delete(f"/products/{prod_id}", headers=headers)
    assert del_resp.status_code == 204

    # Verify deletion
    get_again = client.get(f"/products/{prod_id}", headers=headers)
    assert get_again.status_code == 404
