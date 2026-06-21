"""api 層: HTTP の受け口。

責務は「HTTPの入出力」と「DTO(Pydantic) ↔ domain の変換」だけ。
業務ルールは domain 層に置く。リポジトリは Depends で差し込み、テストで差し替える。
"""

from __future__ import annotations

import os

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from uuid import uuid4

from app.domain import (
    AlreadyReceivedError,
    InsufficientStockError,
    Product,
    PurchaseOrder,
)
from app.repository import (
    ProductNotFoundError,
    ProductRepository,
    PurchaseOrderNotFoundError,
    PurchaseOrderRepository,
    SqliteProductRepository,
    SqlitePurchaseOrderRepository,
)

app = FastAPI(title="inventory_poc")

# 既定の保管先は SQLite ファイル。fastapi dev は server/ から起動するのでそこに作られる。
# 契約テスト等では INVENTORY_DB でテスト用 DB に差し替えられる。
DB_PATH = os.environ.get("INVENTORY_DB", "inventory.db")
_repository: ProductRepository | None = None
_po_repository: PurchaseOrderRepository | None = None


def get_repository() -> ProductRepository:
    """リポジトリの依存(抽象に依存する)。テストでは app.dependency_overrides で差し替える。"""
    global _repository
    if _repository is None:
        _repository = SqliteProductRepository(DB_PATH)
    return _repository


def get_po_repository() -> PurchaseOrderRepository:
    """発注リポジトリの依存。テストでは差し替える。"""
    global _po_repository
    if _po_repository is None:
        _po_repository = SqlitePurchaseOrderRepository(DB_PATH)
    return _po_repository


# --- DTO(API の入出力スキーマ。domain とは別物として定義する) ---
class ProductCreate(BaseModel):
    sku: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(default=0, ge=0)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # domain Product から変換できる

    sku: str
    name: str
    quantity: int


class StockChange(BaseModel):
    # 数量は 1 以上。0 以下は domain に届く前にここで 422 として弾く。
    amount: int = Field(ge=1)


# --- エンドポイント ---
@app.post("/products", response_model=ProductOut, status_code=201)
def register_product(
    body: ProductCreate,
    repo: ProductRepository = Depends(get_repository),
) -> Product:
    # 「同一 SKU は重複登録しない」業務ルール。
    if any(p.sku == body.sku for p in repo.list_all()):
        raise HTTPException(status_code=409, detail=f"SKU '{body.sku}' は既に存在します")
    product = Product(sku=body.sku, name=body.name, quantity=body.quantity)
    repo.add(product)
    return product


@app.get("/products", response_model=list[ProductOut])
def list_products(
    repo: ProductRepository = Depends(get_repository),
) -> list[Product]:
    return repo.list_all()


def _get_or_404(repo: ProductRepository, sku: str) -> Product:
    try:
        return repo.get(sku)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' は存在しません")


@app.post("/products/{sku}/receive", response_model=ProductOut)
def receive_stock(
    sku: str,
    body: StockChange,
    repo: ProductRepository = Depends(get_repository),
) -> Product:
    product = _get_or_404(repo, sku)
    product.receive(body.amount)
    repo.update(product)  # 変更を永続化(メモリ参照に依存しない)
    return product


@app.post("/products/{sku}/ship", response_model=ProductOut)
def ship_stock(
    sku: str,
    body: StockChange,
    repo: ProductRepository = Depends(get_repository),
) -> Product:
    product = _get_or_404(repo, sku)
    try:
        product.ship(body.amount)
    except InsufficientStockError as e:
        # 在庫不足は「現在の状態と衝突」なので 409 Conflict。
        raise HTTPException(status_code=409, detail=str(e))
    repo.update(product)  # 変更を永続化(メモリ参照に依存しない)
    return product


# --- 発注(PurchaseOrder)#0014 ---
class PurchaseOrderCreate(BaseModel):
    sku: str = Field(min_length=1)
    quantity: int = Field(ge=1)


class PurchaseOrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sku: str
    quantity: int
    status: str


def _get_po_or_404(po_repo: PurchaseOrderRepository, order_id: str) -> PurchaseOrder:
    try:
        return po_repo.get(order_id)
    except PurchaseOrderNotFoundError:
        raise HTTPException(status_code=404, detail=f"発注 '{order_id}' は存在しません")


@app.post("/purchase-orders", response_model=PurchaseOrderOut, status_code=201)
def create_purchase_order(
    body: PurchaseOrderCreate,
    repo: ProductRepository = Depends(get_repository),
    po_repo: PurchaseOrderRepository = Depends(get_po_repository),
) -> PurchaseOrder:
    _get_or_404(repo, body.sku)  # 発注は登録済み商品に対してのみ
    order = PurchaseOrder(id=uuid4().hex, sku=body.sku, quantity=body.quantity)
    po_repo.add(order)
    return order


@app.get("/purchase-orders", response_model=list[PurchaseOrderOut])
def list_purchase_orders(
    po_repo: PurchaseOrderRepository = Depends(get_po_repository),
) -> list[PurchaseOrder]:
    return po_repo.list_all()


@app.post("/purchase-orders/{order_id}/receive", response_model=PurchaseOrderOut)
def receive_purchase_order(
    order_id: str,
    repo: ProductRepository = Depends(get_repository),
    po_repo: PurchaseOrderRepository = Depends(get_po_repository),
) -> PurchaseOrder:
    order = _get_po_or_404(po_repo, order_id)
    product = _get_or_404(repo, order.sku)
    # 状態遷移を先に検証(二重入荷を弾く)してから在庫を増やす=副作用前に失敗させる。
    try:
        order.mark_received()
    except AlreadyReceivedError:
        raise HTTPException(status_code=409, detail="既に入荷済みです")
    product.receive(order.quantity)
    repo.update(product)
    po_repo.update(order)
    return order
