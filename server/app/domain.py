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
        # TODO(human): 出荷ロジックを実装する。
        #   - amount が 0 以下なら ValueError を送出
        #   - amount が現在の在庫 quantity を超えるなら InsufficientStockError を送出
        #   - 問題なければ quantity を減らす
        raise NotImplementedError
