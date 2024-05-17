from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == [
        "Hello to our store center, here you can store your items"
    ]


def test_add_new_item():
    response = client.post(
        "/items/", json={"name": "test", "price": "150", "is_offer": "false"}
    )
    assert response.status_code == 200
    assert response.json() == {"item_id": 1, "item_name": "test"}


def test_add_item_with_offer():
    new_offer = 10
    response_set_offer = client.put(f"/offer/{new_offer}")
    assert response_set_offer.status_code == 200
    check_offer = client.get("/offer")
    assert check_offer.json()["offer"] == new_offer
    response = client.post(
        "/items/", json={"name": "test", "price": "150", "is_offer": "true"}
    )
    assert response.status_code == 200
    id = response.json()["item_id"]
    item = client.get(f"/items/{id}").json()
    assert item["price"] == 150 - (150 / new_offer)


def test_change_offer_recalculate_price_from_old_price():
    old_price = 150
    new_offer = 10
    response = client.post(
        "/items/", json={"name": "test", "price": f"{old_price}", "is_offer": "true"}
    )
    assert response.status_code == 200
    response_set_offer = client.put(f"/offer/{new_offer}")
    assert response_set_offer.status_code == 200
    check_offer = client.get("/offer")
    assert check_offer.json()["offer"] == new_offer
    id = response.json()["item_id"]
    item = client.get(f"/items/{id}").json()
    assert item["price"] == old_price - (old_price / new_offer)
