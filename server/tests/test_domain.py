"""ドメイン層のテスト = 自走ループの「オラクル(正解判定器)」。

このテストが緑になることが、ship() の実装が正しいことの機械的な証拠になる。
私はこのテストを繰り返し回して、人手の確認なしに正誤を判断する。
"""

import pytest

from app.domain import InsufficientStockError, Product


def test_receive_increases_quantity():
    p = Product(sku="A-1", name="ねじ", quantity=0)
    p.receive(10)
    assert p.quantity == 10


def test_receive_rejects_non_positive():
    p = Product(sku="A-1", name="ねじ")
    with pytest.raises(ValueError):
        p.receive(0)


def test_ship_decreases_quantity():
    p = Product(sku="A-1", name="ねじ", quantity=10)
    p.ship(3)
    assert p.quantity == 7


def test_ship_rejects_non_positive():
    p = Product(sku="A-1", name="ねじ", quantity=10)
    with pytest.raises(ValueError):
        p.ship(0)


def test_ship_rejects_when_insufficient_stock():
    p = Product(sku="A-1", name="ねじ", quantity=5)
    with pytest.raises(InsufficientStockError):
        p.ship(6)


def test_ship_keeps_invariant_nonnegative():
    """不変条件: 出荷が失敗しても在庫は減らない。"""
    p = Product(sku="A-1", name="ねじ", quantity=5)
    with pytest.raises(InsufficientStockError):
        p.ship(6)
    assert p.quantity == 5  # 失敗時に在庫を触ってはいけない
