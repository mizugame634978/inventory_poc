# #0021 商品の削除 (DELETE /products/{sku})

- status: done
- created: 2026-06-21

## スコープ
- repository: `ProductRepository` に `delete(sku)` を追加し、InMemory / SQLite 両方に実装。
  - 存在しない sku の delete は `ProductNotFoundError`。
- server `app/main.py`: `DELETE /products/{sku}` → 成功 204(本文なし) / 商品なし → 404。
- やらないこと: client / UI、発注が紐づく商品の削除制約(POCでは考えない)。

## テスト内容(完了条件)
- `server/tests/test_repository.py`: SqliteProductRepository の delete 後に get が ProductNotFoundError。
- `server/tests/test_api.py`:
  - `test_delete_product_then_404`: 登録→DELETE 204→GET 404。
  - `test_delete_unknown_is_404`: 未登録 DELETE → 404。
検証: `pwsh -File scripts/check.ps1` 緑。

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: ProductRepositoryにdelete追加(InMemory/SQLite両実装, rowcountで404)。DELETE /products/{sku}=204。test3件。server pytest 41件緑。/loop自走。
- commits: ブランチ issue-0021-delete-product
