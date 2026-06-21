# データモデル(ER)

> 浅く広いトップダウン文書。現状のエンティティと不変条件の一覧。

## エンティティ

現状はメモリ上の単一エンティティのみ。

```
┌────────────────────────────┐
│ Product (商品)              │
├────────────────────────────┤
│ sku      : str  (識別子/PK) │
│ name     : str              │
│ quantity : int  (在庫数)    │
└────────────────────────────┘
```

```
┌────────────────────────────────┐
│ PurchaseOrder (発注) #0014       │
├────────────────────────────────┤
│ id       : str  (識別子/PK)      │
│ sku      : str  (対象商品)       │
│ quantity : int  (発注数 > 0)     │
│ status   : ordered | received    │
└────────────────────────────────┘
```
PurchaseOrder.sku は Product.sku を参照(発注は登録済み商品に対してのみ)。

将来(予定):

```
Product 1 ──< StockMovement (入出庫履歴)
```

## 不変条件(invariants)

エンティティが常に満たすべき条件。**それぞれ対応するテストを持つ**こと。

| 不変条件 | 対象 | テスト | 関連issue |
|---|---|---|---|
| `quantity >= 0`(在庫は負にならない) | Product | `test_ship_keeps_invariant_nonnegative` | #0001 |
| 入荷数は正 | Product.receive | `test_receive_rejects_non_positive` | #0001 |
| 出荷数は正 | Product.ship | `test_ship_rejects_non_positive` | #0001 |

## 操作

| 操作 | メソッド | 効果 | 失敗条件 |
|---|---|---|---|
| 入荷 | `Product.receive(amount)` | quantity += amount | amount <= 0 → ValueError |
| 出荷 | `Product.ship(amount)` | quantity -= amount | amount <= 0 → ValueError / 在庫超過 → InsufficientStockError |

## API エンドポイント(#0002)

| メソッド | パス | 用途 | 失敗 |
|---|---|---|---|
| POST | `/products` | 商品登録 | 重複SKU → 409 / 空sku・負quantity → 422 |
| GET | `/products` | 商品一覧 | — |
| POST | `/products/{sku}/receive` | 入荷(在庫+) | 商品なし → 404 / amount<1 → 422 |
| POST | `/products/{sku}/ship` | 出荷(在庫-) | 商品なし → 404 / 在庫不足 → 409 / amount<1 → 422 |
| POST | `/purchase-orders` | 発注(#0014) | 商品なし → 404 / quantity<1 → 422 |
| GET | `/purchase-orders` | 発注一覧 | — |
| POST | `/purchase-orders/{id}/receive` | 入荷(在庫+・status=received) | 発注/商品なし → 404 / 二重入荷 → 409 |
