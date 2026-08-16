import pytest
from unittest.mock import patch, MagicMock
import app as app_module


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    # Reset inventory before each test so tests don't affect each other
    app_module.inventory = [
        {
            "id": 1,
            "product_name": "Layers Mash 50kg",
            "brands": "Unga Farm Care",
            "ingredients_text": "Maize germ, soya, limestone, vitamins",
            "price": 3200,
            "stock": 15
        },
        {
            "id": 2,
            "product_name": "Broiler Starter Feed 50kg",
            "brands": "Sigma Feeds",
            "ingredients_text": "Maize, soybean meal, fish meal, premix",
            "price": 3450,
            "stock": 10
        }
    ]
    with app_module.app.test_client() as test_client:
        yield test_client


def test_get_all_inventory(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]["product_name"] == "Layers Mash 50kg"


def test_get_single_item_found(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1


def test_get_single_item_not_found(client):
    response = client.get("/inventory/999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_add_item(client):
    new_item = {
        "product_name": "Dewormer Tablets",
        "brands": "Agrivet",
        "ingredients_text": "Albendazole",
        "price": 300,
        "stock": 40
    }
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201
    data = response.get_json()
    assert data["product_name"] == "Dewormer Tablets"
    assert data["id"] == 3


def test_add_item_missing_name(client):
    response = client.post("/inventory", json={"brands": "Agrivet"})
    assert response.status_code == 400


def test_update_item(client):
    response = client.patch("/inventory/1", json={"price": 3500, "stock": 20})
    assert response.status_code == 200
    data = response.get_json()
    assert data["price"] == 3500
    assert data["stock"] == 20
    assert data["product_name"] == "Layers Mash 50kg"  # unchanged


def test_update_item_not_found(client):
    response = client.patch("/inventory/999", json={"price": 100})
    assert response.status_code == 404


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200

    # Confirm it's actually gone
    check = client.get("/inventory/2")
    assert check.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/999")
    assert response.status_code == 404


@patch("app.requests.get")
def test_search_external_product_by_name(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "products": [
            {"product_name": "Almond Milk", "brands": "Silk", "ingredients_text": "Almonds, water"}
        ]
    }
    mock_get.return_value = mock_response

    response = client.get("/products/search?name=almond milk")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["product_name"] == "Almond Milk"


@patch("app.requests.get")
def test_search_external_product_not_found(mock_get, client):
    mock_response = MagicMock()
    mock_response.json.return_value = {"products": []}
    mock_get.return_value = mock_response

    response = client.get("/products/search?name=nonexistentproduct")
    assert response.status_code == 404