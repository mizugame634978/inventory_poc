"""在庫の保管場所(リポジトリ)。

domain 層から永続化の都合を切り離すための抽象 `ProductRepository` を置き、
その下に実装(メモリ / SQLite)をぶら下げる。api 層はこの抽象だけに依存するので、
実装を差し替えても domain.py は一切変わらない(#0007 で実証)。
"""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from contextlib import closing

from app.domain import Product, PurchaseOrder, PurchaseOrderStatus


class ProductNotFoundError(Exception):
    """指定された SKU の商品が存在しないときに送出する。"""


class PurchaseOrderNotFoundError(Exception):
    """指定された ID の発注が存在しないときに送出する。"""


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


class PurchaseOrderRepository(ABC):
    """発注の保管契約。"""

    @abstractmethod
    def add(self, order: PurchaseOrder) -> None: ...

    @abstractmethod
    def get(self, order_id: str) -> PurchaseOrder:
        """ID で 1 件取得。無ければ PurchaseOrderNotFoundError。"""

    @abstractmethod
    def list_all(self) -> list[PurchaseOrder]: ...

    @abstractmethod
    def update(self, order: PurchaseOrder) -> None: ...


class InMemoryPurchaseOrderRepository(PurchaseOrderRepository):
    def __init__(self) -> None:
        self._orders: dict[str, PurchaseOrder] = {}

    def add(self, order: PurchaseOrder) -> None:
        self._orders[order.id] = order

    def get(self, order_id: str) -> PurchaseOrder:
        if order_id not in self._orders:
            raise PurchaseOrderNotFoundError(order_id)
        return self._orders[order_id]

    def list_all(self) -> list[PurchaseOrder]:
        return list(self._orders.values())

    def update(self, order: PurchaseOrder) -> None:
        self._orders[order.id] = order


class SqlitePurchaseOrderRepository(PurchaseOrderRepository):
    """発注を SQLite に保管。Product と同じ DB ファイルの別テーブルを使う。"""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._db_path)

    def _ensure_schema(self) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS purchase_orders (
                    id TEXT PRIMARY KEY,
                    sku TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def add(self, order: PurchaseOrder) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT INTO purchase_orders (id, sku, quantity, status) VALUES (?, ?, ?, ?)",
                (order.id, order.sku, order.quantity, order.status.value),
            )
            conn.commit()

    def get(self, order_id: str) -> PurchaseOrder:
        with closing(self._connect()) as conn:
            row = conn.execute(
                "SELECT id, sku, quantity, status FROM purchase_orders WHERE id = ?",
                (order_id,),
            ).fetchone()
        if row is None:
            raise PurchaseOrderNotFoundError(order_id)
        return PurchaseOrder(
            id=row[0], sku=row[1], quantity=row[2], status=PurchaseOrderStatus(row[3])
        )

    def list_all(self) -> list[PurchaseOrder]:
        with closing(self._connect()) as conn:
            rows = conn.execute(
                "SELECT id, sku, quantity, status FROM purchase_orders ORDER BY id"
            ).fetchall()
        return [
            PurchaseOrder(id=r[0], sku=r[1], quantity=r[2], status=PurchaseOrderStatus(r[3]))
            for r in rows
        ]

    def update(self, order: PurchaseOrder) -> None:
        with closing(self._connect()) as conn:
            conn.execute(
                "UPDATE purchase_orders SET sku = ?, quantity = ?, status = ? WHERE id = ?",
                (order.sku, order.quantity, order.status.value, order.id),
            )
            conn.commit()
