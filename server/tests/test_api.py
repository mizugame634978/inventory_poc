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


# --- 商品の削除 (#0021) ---
def test_delete_product_then_404(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ"})
    assert client.delete("/products/A-1").status_code == 204
    assert client.get("/products/A-1").status_code == 404


def test_delete_unknown_is_404(client):
    assert client.delete("/products/NOPE").status_code == 404


# --- 商品名の変更 (#0020) ---
def test_rename_product_updates_name(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": 1})
    res = client.put("/products/A-1", json={"name": "なべ"})
    assert res.status_code == 200
    assert res.json()["name"] == "なべ"


def test_rename_unknown_is_404(client):
    res = client.put("/products/NOPE", json={"name": "x"})
    assert res.status_code == 404


def test_rename_empty_name_is_422(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ"})
    res = client.put("/products/A-1", json={"name": ""})
    assert res.status_code == 422


# --- 在庫サマリ (#0019) ---
def test_summary_empty_is_zero(client):
    res = client.get("/products/summary")
    assert res.status_code == 200
    assert res.json() == {"product_count": 0, "total_quantity": 0}


def test_summary_counts_and_sums(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": 2})
    client.post("/products", json={"sku": "B-2", "name": "ボルト", "quantity": 3})
    res = client.get("/products/summary")
    assert res.json() == {"product_count": 2, "total_quantity": 5}


# --- 単一商品取得 (#0018) ---
def test_get_single_product_returns_it(client):
    client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": 4})
    res = client.get("/products/A-1")
    assert res.status_code == 200
    assert res.json() == {"sku": "A-1", "name": "ねじ", "quantity": 4}


def test_get_unknown_product_is_404(client):
    res = client.get("/products/NOPE")
    assert res.status_code == 404


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
