"""在庫の保管場所(リポジトリ)。

POC なので DB は使わず、まずはメモリ上の辞書で持つ。
ドメイン層から永続化の都合を切り離しておくと、後で SQLite などに
差し替えても domain.py / main.py をほとんど変えずに済む。
"""

from __future__ import annotations

from app.domain import Product


class ProductNotFoundError(Exception):
    """指定された SKU の商品が存在しないときに送出する。"""


class InMemoryProductRepository:
    def __init__(self) -> None:
        self._products: dict[str, Product] = {}

    def add(self, product: Product) -> None:
        self._products[product.sku] = product

    def get(self, sku: str) -> Product:
        if sku not in self._products:
            raise ProductNotFoundError(sku)
        return self._products[sku]

    def list_all(self) -> list[Product]:
        return list(self._products.values())
