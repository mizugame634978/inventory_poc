"""発注→入荷フローのテスト(#0014)。

api テストは各テスト独立の InMemory リポジトリ(商品・発注の両方)に差し替える。
"""

import pytest
from fastapi.testclient import TestClient

from app.domain import (
    AlreadyReceivedError,
    InvalidOrderStateError,
    PurchaseOrder,
    PurchaseOrderStatus,
)
from app.main import app, get_po_repository, get_repository
from app.repository import (
    InMemoryProductRepository,
    InMemoryPurchaseOrderRepository,
)
from app.domain import Product


@pytest.fixture
def client():
    products = InMemoryProductRepository()
    orders = InMemoryPurchaseOrderRepository()
    app.dependency_overrides[get_repository] = lambda: products
    app.dependency_overrides[get_po_repository] = lambda: orders
    yield TestClient(app), products
    app.dependency_overrides.clear()


# --- domain ---
def test_mark_received_twice_raises():
    po = PurchaseOrder(id="x", sku="A-1", quantity=3)
    po.mark_received()
    assert po.status is PurchaseOrderStatus.RECEIVED
    with pytest.raises(AlreadyReceivedError):
        po.mark_received()


def test_purchase_order_quantity_must_be_positive():
    with pytest.raises(ValueError):
        PurchaseOrder(id="x", sku="A-1", quantity=0)


def test_cancel_sets_cancelled():
    po = PurchaseOrder(id="x", sku="A-1", quantity=3)
    po.cancel()
    assert po.status is PurchaseOrderStatus.CANCELLED


def test_cancel_received_raises():
    po = PurchaseOrder(id="x", sku="A-1", quantity=3)
    po.mark_received()
    with pytest.raises(InvalidOrderStateError):
        po.cancel()


def test_receive_cancelled_raises():
    po = PurchaseOrder(id="x", sku="A-1", quantity=3)
    po.cancel()
    with pytest.raises(InvalidOrderStateError):
        po.mark_received()


# --- api ---
def _register_product(products, sku="A-1", quantity=0):
    products.add(Product(sku=sku, name="ねじ", quantity=quantity))


def test_create_order_returns_201_ordered(client):
    c, products = client
    _register_product(products)
    res = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 5})
    assert res.status_code == 201
    body = res.json()
    assert body["sku"] == "A-1"
    assert body["quantity"] == 5
    assert body["status"] == "ordered"
    assert body["id"]


def test_create_order_for_unknown_sku_is_404(client):
    c, _ = client
    res = c.post("/purchase-orders", json={"sku": "NOPE", "quantity": 1})
    assert res.status_code == 404


def test_create_order_zero_quantity_is_422(client):
    c, products = client
    _register_product(products)
    res = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 0})
    assert res.status_code == 422


def test_receive_increases_stock_and_sets_received(client):
    c, products = client
    _register_product(products, quantity=2)
    order_id = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 5}).json()["id"]

    res = c.post(f"/purchase-orders/{order_id}/receive")
    assert res.status_code == 200
    assert res.json()["status"] == "received"
    # 在庫が発注数だけ増えている
    assert products.get("A-1").quantity == 7


def test_double_receive_is_409(client):
    c, products = client
    _register_product(products, quantity=0)
    order_id = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 3}).json()["id"]
    assert c.post(f"/purchase-orders/{order_id}/receive").status_code == 200

    res = c.post(f"/purchase-orders/{order_id}/receive")
    assert res.status_code == 409
    # 二重入荷は弾かれ、在庫は二度増えない
    assert products.get("A-1").quantity == 3


def test_receive_unknown_order_is_404(client):
    c, _ = client
    res = c.post("/purchase-orders/UNKNOWN/receive")
    assert res.status_code == 404


def test_cancel_order_200(client):
    c, products = client
    _register_product(products)
    order_id = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 3}).json()["id"]
    res = c.post(f"/purchase-orders/{order_id}/cancel")
    assert res.status_code == 200
    assert res.json()["status"] == "cancelled"


def test_cancel_received_is_409(client):
    c, products = client
    _register_product(products, quantity=0)
    order_id = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 3}).json()["id"]
    c.post(f"/purchase-orders/{order_id}/receive")
    assert c.post(f"/purchase-orders/{order_id}/cancel").status_code == 409


def test_receive_cancelled_is_409(client):
    c, products = client
    _register_product(products, quantity=0)
    order_id = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 3}).json()["id"]
    c.post(f"/purchase-orders/{order_id}/cancel")
    assert c.post(f"/purchase-orders/{order_id}/receive").status_code == 409


def test_cancel_unknown_is_404(client):
    c, _ = client
    assert c.post("/purchase-orders/UNKNOWN/cancel").status_code == 404


def test_get_single_order_returns_it(client):
    c, products = client
    _register_product(products)
    order = c.post("/purchase-orders", json={"sku": "A-1", "quantity": 3}).json()
    res = c.get(f"/purchase-orders/{order['id']}")
    assert res.status_code == 200
    body = res.json()
    assert body["id"] == order["id"]
    assert body["sku"] == "A-1"
    assert body["quantity"] == 3
    assert body["status"] == "ordered"


def test_get_unknown_order_is_404(client):
    c, _ = client
    assert c.get("/purchase-orders/UNKNOWN").status_code == 404


def test_list_orders(client):
    c, products = client
    _register_product(products)
    c.post("/purchase-orders", json={"sku": "A-1", "quantity": 1})
    c.post("/purchase-orders", json={"sku": "A-1", "quantity": 2})
    res = c.get("/purchase-orders")
    assert res.status_code == 200
    assert len(res.json()) == 2
