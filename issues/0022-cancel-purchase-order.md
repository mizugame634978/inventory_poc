# #0022 発注のキャンセル (POST /purchase-orders/{id}/cancel)

- status: open
- created: 2026-06-21

## ドメイン設計
- `PurchaseOrderStatus` に `CANCELLED = "cancelled"` を追加。
- `PurchaseOrder.cancel()`: ordered のときのみ cancelled にできる。received/cancelled からは不可
  (新しい例外 `NotCancellableError` を送出)。
- `PurchaseOrder.mark_received()`: ordered 以外(received/cancelled)からは不可にする
  (現状は received のみ弾く → 「ordered でなければ AlreadyReceivedError」に拡張)。

## スコープ
- domain: 上記。repository: 変更不要(status を保存済み)。
- api: `POST /purchase-orders/{id}/cancel` → 200 で status=cancelled / 発注なし 404 /
  キャンセル不可(received等) → 409。
  既存 receive: cancelled を入荷しようとしたら 409(mark_received が弾く)。

## テスト内容(完了条件)
- domain(test_purchase_orders.py): cancel 後 status=cancelled / received を cancel すると例外 /
  cancelled を mark_received すると例外。
- api(test_purchase_orders.py): cancel ordered→200 cancelled / cancel received→409 /
  receive cancelled→409 / cancel 不明→404。
検証: `pwsh -File scripts/check.ps1` 緑。

## 結果(完了時に追記)
- done:
- 要点:
- commits:
