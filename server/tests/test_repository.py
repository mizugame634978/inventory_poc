"""リポジトリ実装のテスト(主に SQLite)と、差し替え可能性の証明。

`:memory:` は接続毎に別DBになり、本実装(接続毎に開閉)では使えないため、
一時ファイル(tmp_path)を使う。
"""

import pytest
from fastapi.testclient import TestClient

from app.domain import Product
from app.main import app, get_repository
from app.repository import (
    ProductNotFoundError,
    SqliteProductRepository,
)


def test_sqlite_add_and_get_roundtrip(tmp_path):
    repo = SqliteProductRepository(str(tmp_path / "t.db"))
    repo.add(Product(sku="A-1", name="ねじ", quantity=2))

    got = repo.get("A-1")
    assert got == Product(sku="A-1", name="ねじ", quantity=2)


def test_sqlite_list_all(tmp_path):
    repo = SqliteProductRepository(str(tmp_path / "t.db"))
    repo.add(Product(sku="A-1", name="ねじ"))
    repo.add(Product(sku="B-2", name="ボルト"))

    assert {p.sku for p in repo.list_all()} == {"A-1", "B-2"}


def test_sqlite_update_is_persisted_to_file(tmp_path):
    db = str(tmp_path / "t.db")
    repo = SqliteProductRepository(db)
    repo.add(Product(sku="A-1", name="ねじ", quantity=2))

    product = repo.get("A-1")
    product.receive(3)
    repo.update(product)

    # 別インスタンスで開き直しても変更が残っている = ファイルに永続化されている
    reopened = SqliteProductRepository(db)
    assert reopened.get("A-1").quantity == 5


def test_sqlite_get_missing_raises(tmp_path):
    repo = SqliteProductRepository(str(tmp_path / "t.db"))
    with pytest.raises(ProductNotFoundError):
        repo.get("NOPE")


def test_api_works_against_sqlite_implementation(tmp_path):
    """api 層をそのままに、保管だけ SQLite に差し替えても業務フローが通る(差し替え可能性の証明)。"""
    repo = SqliteProductRepository(str(tmp_path / "api.db"))
    app.dependency_overrides[get_repository] = lambda: repo
    try:
        client = TestClient(app)
        assert client.post("/products", json={"sku": "A-1", "name": "ねじ", "quantity": 2}).status_code == 201
        assert client.post("/products/A-1/receive", json={"amount": 3}).json()["quantity"] == 5
        assert client.post("/products/A-1/ship", json={"amount": 4}).json()["quantity"] == 1
        assert client.post("/products/A-1/ship", json={"amount": 5}).status_code == 409  # 在庫不足
    finally:
        app.dependency_overrides.clear()
