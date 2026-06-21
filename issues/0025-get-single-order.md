# #0025 単一発注取得 (GET /purchase-orders/{id})

- status: open
- created: 2026-06-21

## スコープ
- server `app/main.py`: `GET /purchase-orders/{id}` → 存在すれば 200 で PurchaseOrderOut、
  無ければ 404(既存 `_get_po_or_404` 再利用)。
- やらないこと: client / UI。

## テスト内容(完了条件) — server/tests/test_purchase_orders.py に追記
- `test_get_single_order_returns_it`: 商品登録→発注作成→GET /purchase-orders/{id} → 200 かつ
  id/sku/quantity/status 一致。
- `test_get_unknown_order_is_404`: 未知 id を GET → 404。
検証: `pwsh -File scripts/check.ps1` 緑。

## 結果(完了時に追記)
- done:
- 要点:
- commits:
