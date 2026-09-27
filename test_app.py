"""Automated tests for Second Closet (run with: pytest -v)."""
import pytest

from app import app, items, reset_store

VALID = {
    "name": "Black leather boots",
    "seller": "Varadh",
    "category": "Footwear",
    "size": "Free Size",
    "condition": "Good",
    "price": "1500",
}


@pytest.fixture
def client():
    app.config["TESTING"] = True
    reset_store(seed=False)  # start every test with an empty store
    with app.test_client() as c:
        yield c


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["status"] == "ok"


def test_home_page_renders(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Second Closet" in res.data
    assert b"commit" in res.data


def test_add_valid_item(client):
    res = client.post("/items", data=VALID)
    assert res.status_code == 302
    listed = client.get("/api/items").json
    assert len(listed) == 1
    assert listed[0]["name"] == "Black leather boots"
    assert listed[0]["price"] == 1500
    assert listed[0]["status"] == "Available"


def test_negative_price_rejected(client):
    res = client.post("/items", data={**VALID, "price": "-50"})
    assert res.status_code == 400
    assert items == []


def test_missing_name_rejected(client):
    res = client.post("/items", data={**VALID, "name": "   "})
    assert res.status_code == 400


def test_invalid_condition_rejected(client):
    res = client.post("/items", data={**VALID, "condition": "Brand new!!"})
    assert res.status_code == 400


def test_buy_marks_item_sold(client):
    client.post("/items", data=VALID)
    res = client.post("/items/1/buy")
    assert res.status_code == 302
    assert client.get("/api/items").json[0]["status"] == "Sold"


def test_cannot_buy_sold_item_twice(client):
    client.post("/items", data=VALID)
    client.post("/items/1/buy")
    res = client.post("/items/1/buy")
    assert res.status_code == 409


def test_buy_missing_item_returns_404(client):
    assert client.post("/items/999/buy").status_code == 404


def test_filter_by_category_and_price(client):
    client.post("/items", data=VALID)
    client.post("/items", data={**VALID, "name": "Linen shirt", "category": "Tops", "price": "300"})
    tops = client.get("/api/items?category=Tops").json
    assert [i["name"] for i in tops] == ["Linen shirt"]
    cheap = client.get("/api/items?max_price=500").json
    assert len(cheap) == 1


def test_invalid_max_price_rejected(client):
    assert client.get("/api/items?max_price=abc").status_code == 400
