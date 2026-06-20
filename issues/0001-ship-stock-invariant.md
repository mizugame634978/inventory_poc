# #0001 出荷時の在庫非負チェックを実装する

- status: open
- created: 2026-06-20

## 目的 / 背景
在庫ドメインの中核となる不変条件「在庫数は負にならない (quantity >= 0)」を、
出荷操作 `Product.ship` に実装する。この不変条件は今後の受発注フロー全体の土台であり、
テストで機械的に守れるオラクルになる。

現状 `server/app/domain.py` の `Product.ship` は未実装 (`NotImplementedError`) で、
関連テストが赤になっている。これを緑にするのがゴール。

## スコープ
- やること: `Product.ship(amount)` の実装
  - `amount <= 0` → `ValueError`
  - `amount > quantity` → `InsufficientStockError`(在庫不足)
  - それ以外 → `quantity -= amount`
  - **失敗時は quantity を一切変更しない**(検証を先に済ませてから減算する)
- やらないこと: API層・WPF・永続化(別issue)

## テスト内容(完了条件)
`server/tests/test_domain.py` の以下が全て緑になること:
- `test_ship_decreases_quantity`
- `test_ship_rejects_non_positive`
- `test_ship_rejects_when_insufficient_stock`
- `test_ship_keeps_invariant_nonnegative`(失敗時に在庫が減らないこと)

検証コマンド: `cd server && uv run pytest -q`(全6件緑)

## 結果(完了時に追記)
- done:
- 要点:
- commits:
