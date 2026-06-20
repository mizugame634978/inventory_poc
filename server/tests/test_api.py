"""api 層のテスト。

各テストは独立した空のリポジトリを使う(dependency_overrides で差し替え)。
これにより前のテストの登録結果が次に漏れない。
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app, get_repository
from app.repository import InMemoryProductRepository


@pytest.fixture
def client():
    repo = InMemoryProductRepository()
    app.dependency_overrides[get_repository] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_register_returns_201_with_body(client):
    res = client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": 5})
    assert res.status_code == 201
    assert res.json() == {"sku": "A-1", "name": "ねじ", "quantity": 5}


def test_register_defaults_quantity_to_zero(client):
    res = client.post("/products", json={"sku": "A-1", "name": "ねじ"})
    assert res.status_code == 201
    assert res.json()["quantity"] == 0


def test_list_returns_registered_products(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ"})
    client.post("/products", json={"sku": "B-2", "name": "ボルト"})
    res = client.get("/products")
    assert res.status_code == 200
    skus = {p["sku"] for p in res.json()}
    assert skus == {"A-1", "B-2"}


def test_duplicate_sku_is_rejected_with_409(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ"})
    res = client.post("/products", json={"sku": "A-1", "name": "別のねじ"})
    assert res.status_code == 409


def test_empty_sku_is_422(client):
    res = client.post("/products", json={"sku": "", "name": "ねじ"})
    assert res.status_code == 422


def test_negative_quantity_is_422(client):
    res = client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": -1})
    assert res.status_code == 422


# --- 入荷 / 出荷 (#0006) ---
def _register(client, sku="A-1", name="ねじ", quantity=0):
    client.post("/products", json={"sku": sku, "name": name, "quantity": quantity})


def test_receive_increases_quantity(client):
    _register(client, quantity=2)
    res = client.post("/products/A-1/receive", json={"amount": 3})
    assert res.status_code == 200
    assert res.json()["quantity"] == 5


def test_ship_decreases_quantity(client):
    _register(client, quantity=5)
    res = client.post("/products/A-1/ship", json={"amount": 2})
    assert res.status_code == 200
    assert res.json()["quantity"] == 3


def test_ship_insufficient_stock_is_409(client):
    _register(client, quantity=1)
    res = client.post("/products/A-1/ship", json={"amount": 2})
    assert res.status_code == 409


def test_operation_on_unknown_sku_is_404(client):
    res = client.post("/products/NOPE/receive", json={"amount": 1})
    assert res.status_code == 404


def test_amount_zero_is_422(client):
    _register(client, quantity=5)
    res = client.post("/products/A-1/ship", json={"amount": 0})
    assert res.status_code == 422
