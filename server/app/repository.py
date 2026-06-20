"""在庫の保管場所(リポジトリ)。

domain 層から永続化の都合を切り離すための抽象 `ProductRepository` を置き、
その下に実装(メモリ / SQLite)をぶら下げる。api 層はこの抽象だけに依存するので、
実装を差し替えても domain.py は一切変わらない(#0007 で実証)。
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from contextlib import closing

from app.domain import Product


class ProductNotFoundError(Exception):
    """指定された SKU の商品が存在しないときに送出する。"""


class ProductRepository(ABC):
    """商品の保管契約。実装はこの 4 メソッドを満たせばよい。"""

    @abstractmethod
    def add(self, product: Product) -> None:
        """新規の商品を保存する。"""

    @abstractmethod
    def get(self, sku: str) -> Product:
        """SKU で 1 件取得する。無ければ ProductNotFoundError。"""

    @abstractmethod
    def list_all(self) -> list[Product]:
        """全件を返す。"""

    @abstractmethod
    def update(self, product: Product) -> None:
        """既存商品の変更(在庫数など)を保存する。"""


class InMemoryProductRepository(ProductRepository):
    """プロセス内メモリ保管。テストや起動直後の動作確認向き。"""

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

    def update(self, product: Product) -> None:
        # メモリでは同一参照を保持しているため実質 no-op だが、契約として明示しておく。
        self._products[product.sku] = product


class SqliteProductRepository(ProductRepository):
    """SQLite ファイルに保管する。追加依存なし(stdlib sqlite3)。

    接続はオペレーション毎に開閉する。FastAPI は同期エンドポイントをスレッドプールで
    実行するため、接続を使い回すとスレッド跨ぎになる。毎回開閉すればその問題を避けられる。
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    sku TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    def add(self, product: Product) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT INTO products (sku, name, quantity) VALUES (?, ?, ?)",
                (product.sku, product.name, product.quantity),
            )
            conn.commit()

    def get(self, sku: str) -> Product:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT sku, name, quantity FROM products WHERE sku = ?", (sku,)
            ).fetchone()
        if row is None:
            raise ProductNotFoundError(sku)
        return Product(sku=row[0], name=row[1], quantity=row[2])

    def list_all(self) -> list[Product]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT sku, name, quantity FROM products ORDER BY sku"
            ).fetchall()
        return [Product(sku=r[0], name=r[1], quantity=r[2]) for r in rows]

    def update(self, product: Product) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "UPDATE products SET name = ?, quantity = ? WHERE sku = ?",
                (product.name, product.quantity, product.sku),
            )
            conn.commit()
