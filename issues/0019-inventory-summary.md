# #0019 在庫サマリ API (GET /products/summary)

- status: done
- created: 2026-06-21

## 目的 / 背景
商品点数と在庫合計を返すサマリを追加する。小さく明確で、サーバ側のみ・pytest で完全検証できる
(外側ループの自走対象として適切)。

## スコープ
- server `app/main.py`: `GET /products/summary` を追加
  - レスポンス: `{ "product_count": <商品数>, "total_quantity": <在庫数の合計> }`
  - Pydantic の応答モデル(例 `InventorySummaryOut`)を定義する
- 注意: ルート登録順に注意(`/products/{sku}` より前に `/products/summary` を置く。後だと
  "summary" が sku として解釈され得る)。
- やらないこと: client / UI

## テスト内容(完了条件)
`server/tests/test_api.py` に追記:
- `test_summary_empty_is_zero`: 何も登録していないと `{product_count:0, total_quantity:0}`
- `test_summary_counts_and_sums`: 2商品(在庫 2 と 3)登録 → `{product_count:2, total_quantity:5}`

検証: `pwsh -File scripts/check.ps1` が緑

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `GET /products/summary`(InventorySummaryOut)を `/products/{sku}` より前に登録(route順の罠回避)。
  空=0/0、2商品(2,3)=count2/total5 のテスト2件。server pytest 35件・check.ps1 緑。
  /loop 自己ペースの自走サイクルで実装。
- commits: ブランチ issue-0019-inventory-summary
