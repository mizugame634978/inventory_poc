# #0020 商品名の変更 (PUT /products/{sku})

- status: open
- created: 2026-06-21

## スコープ
- server `app/main.py`: `PUT /products/{sku}` 本文 `{name}`(min_length=1)で商品名を変更。
  - 商品なし → 404 / name 空 → 422 / 成功 → 200 で更新後 ProductOut。
  - 既存の repo.get + repo.update を使う(新メソッド不要)。
- やらないこと: client / UI。

## テスト内容(完了条件) — server/tests/test_api.py に追記
- `test_rename_product_updates_name`: 登録→PUTで name 変更→200 かつ name が新しい。
- `test_rename_unknown_is_404`: 未登録 SKU の PUT → 404。
- `test_rename_empty_name_is_422`: name 空 → 422。
検証: `pwsh -File scripts/check.ps1` 緑。

## 結果(完了時に追記)
- done:
- 要点:
- commits:
