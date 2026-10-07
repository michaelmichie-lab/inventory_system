from unittest.mock import patch
import app
import pytest


@pytest.fixture
def client():
  app.app.config["TESTING"] = True
  with app.app.test_client() as client:

    app.inventory = [
        {
            "id": 1,
            "barcode": "123456",
            "product_name": "Test Snack",
            "brands": "TestBrand",
            "quantity": 10,
            "price": 2.50,
            "ingredients_text": "Flour, water",
        }
    ]
    yield client


def test_get_inventory(client):
  response = client.get("/inventory")
  assert response.status_code == 200
  data = response.get_json()
  assert len(data) == 1
  assert data[0]["product_name"] == "Test Snack"


def test_get_single_item(client):
  response = client.get("/inventory/1")
  assert response.status_code == 200
  assert response.get_json()["brands"] == "TestBrand"

  response_404 = client.get("/inventory/999")
  assert response_404.status_code == 404


@patch("app.requests.get")
def test_add_item_with_mock_api(mock_get, client):
  mock_get.return_value.status_code = 200
  mock_get.return_value.json.return_value = {
      "status": 1,
      "product": {
          "product_name": "Mocked Organic Juice",
          "brands": "MockBrand",
          "ingredients_text": "Water, apples",
      },
  }

  payload = {"barcode": "999888777", "quantity": 15, "price": 4.50}
  response = client.post("/inventory", json=payload)
  assert response.status_code == 201
  data = response.get_json()
  assert data["product_name"] == "Mocked Organic Juice"
  assert data["quantity"] == 15


def test_update_item(client):
  response = client.patch(
      "/inventory/1", json={"quantity": 25, "price": 3.00}
  )
  assert response.status_code == 200
  data = response.get_json()
  assert data["quantity"] == 25
  assert data["price"] == 3.00


def test_delete_item(client):
  response = client.delete("/inventory/1")
  assert response.status_code == 200
  assert len(app.inventory) == 0

  response_404 = client.delete("/inventory/999")
  assert response_404.status_code == 404