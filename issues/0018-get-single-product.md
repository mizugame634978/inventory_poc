# #0018 単一商品取得 API (GET /products/{sku})

- status: done
- created: 2026-06-21

## 目的 / 背景
SKU 指定で 1 件の商品を取得するエンドポイントを追加する。小さく明確で、サーバ側のみ・
pytest で完全に検証できる(外側ループの自走対象として適切)。

## スコープ
- server `app/main.py`: `GET /products/{sku}` を追加
  - 存在すれば `ProductOut` を 200 で返す
  - 存在しなければ 404(既存の `_get_or_404` を再利用)
- やらないこと: client / UI

## テスト内容(完了条件)
`server/tests/test_api.py` に追記:
- `test_get_single_product_returns_it`: 登録済み SKU を GET → 200 かつ sku/name/quantity 一致
- `test_get_unknown_product_is_404`: 未登録 SKU を GET → 404

検証: `pwsh -File scripts/check.ps1` が緑

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `GET /products/{sku}` を追加(_get_or_404 再利用)。test_api.py に 200/404 の2件追加。
  server pytest 33件・check.ps1 緑。外側ループの1サイクル監視デモとして手動実行。
- commits: ブランチ issue-0018-get-single-product
