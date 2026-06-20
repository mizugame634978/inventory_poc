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
