"""api 層: HTTP の受け口。

責務は「HTTPの入出力」と「DTO(Pydantic) ↔ domain の変換」だけ。
業務ルールは domain 層に置く。リポジトリは Depends で差し込み、テストで差し替える。
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from app.domain import InsufficientStockError, Product
from app.repository import InMemoryProductRepository, ProductNotFoundError

app = FastAPI(title="inventory_poc")

# POC なのでプロセス内のメモリ保管を 1 つだけ持つ。
_repository = InMemoryProductRepository()


def get_repository() -> InMemoryProductRepository:
    """リポジトリの依存。テストでは app.dependency_overrides で差し替える。"""
    return _repository


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
    repo: InMemoryProductRepository = Depends(get_repository),
) -> Product:
    # 「同一 SKU は重複登録しない」業務ルール。
    if any(p.sku == body.sku for p in repo.list_all()):
        raise HTTPException(status_code=409, detail=f"SKU '{body.sku}' は既に存在します")
    product = Product(sku=body.sku, name=body.name, quantity=body.quantity)
    repo.add(product)
    return product


@app.get("/products", response_model=list[ProductOut])
def list_products(
    repo: InMemoryProductRepository = Depends(get_repository),
) -> list[Product]:
    return repo.list_all()


def _get_or_404(repo: InMemoryProductRepository, sku: str) -> Product:
    try:
        return repo.get(sku)
    except ProductNotFoundError:
        raise HTTPException(status_code=404, detail=f"SKU '{sku}' は存在しません")


@app.post("/products/{sku}/receive", response_model=ProductOut)
def receive_stock(
    sku: str,
    body: StockChange,
    repo: InMemoryProductRepository = Depends(get_repository),
) -> Product:
    product = _get_or_404(repo, sku)
    product.receive(body.amount)
    return product


@app.post("/products/{sku}/ship", response_model=ProductOut)
def ship_stock(
    sku: str,
    body: StockChange,
    repo: InMemoryProductRepository = Depends(get_repository),
) -> Product:
    product = _get_or_404(repo, sku)
    try:
        product.ship(body.amount)
    except InsufficientStockError as e:
        # 在庫不足は「現在の状態と衝突」なので 409 Conflict。
        raise HTTPException(status_code=409, detail=str(e))
    return product
