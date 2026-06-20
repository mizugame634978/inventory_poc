"""在庫ドメインモデル。

ここはアプリの「業務ルール」を表す層。FastAPI や DB の都合からは独立させ、
純粋な Python だけで完結させる。こうしておくと pytest で高速に検証でき、
私(エージェント)が自分で正誤を確認しながら自走できる。
"""

from __future__ import annotations

from dataclasses import dataclass


class InsufficientStockError(Exception):
    """在庫を超える出荷を要求されたときに送出する。"""


@dataclass
class Product:
    """在庫を持つ商品。

    不変条件(invariant): quantity は常に 0 以上でなければならない。
    この不変条件こそが、テストで機械的に検証できる「オラクル」になる。
    """

    sku: str
    name: str
    quantity: int = 0

    def receive(self, amount: int) -> None:
        """入荷: 在庫を amount だけ増やす。"""
        if amount <= 0:
            raise ValueError("入荷数は正の整数である必要があります")
        self.quantity += amount

    def ship(self, amount: int) -> None:
        """出荷: 在庫を amount だけ減らす。

        在庫を下回る出荷は不変条件 (quantity >= 0) を壊すため拒否する。
        """
        # 検証を先に全て済ませてから quantity を変更する。
        # こうすることで、例外で抜けた場合に在庫が中途半端に減らない(不変条件を守る)。
        if amount <= 0:
            raise ValueError("出荷数は正の整数である必要があります")
        if amount > self.quantity:
            raise InsufficientStockError(
                f"在庫不足: 在庫 {self.quantity} に対し {amount} の出荷を要求されました"
            )
        self.quantity -= amount
