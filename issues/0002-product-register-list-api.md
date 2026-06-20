# #0002 商品の登録・一覧 API

- status: done
- created: 2026-06-20

## 目的 / 背景
domain 層(Product)を HTTP に繋ぐ api 層を作る。WPF クライアントが叩く最初の
エンドポイントであり、ここで OpenAPI スキーマが確定する(WPF との契約になる)。

## スコープ
- やること:
  - `POST /products` 商品登録(sku, name, quantity?)
  - `GET /products` 商品一覧
  - api層は DTO(Pydantic)を domain(Product)から分離する
  - リポジトリは DI(`Depends`)で差し込み、テストで差し替え可能にする
- 業務ルール: 同一 SKU の重複登録は 409 で拒否
- やらないこと: 入荷/出荷エンドポイント(別issue)、永続化(別issue)、WPF(#0003)

## テスト内容(完了条件)
`server/tests/test_api.py`(新規)を FastAPI TestClient で:
- 登録が 201 + 登録内容を返す
- 一覧が登録済み商品を返す
- 重複 SKU は 409
- 空 sku / 負の quantity は 422(バリデーション)

検証コマンド: `cd server && uv run pytest -q`(既存6件 + 新規が全て緑)

## 結果(完了時に追記)
- done: 2026-06-20
- 要点: DTO(Pydantic) を domain から分離。リポジトリを `Depends(get_repository)` で
  DI し、テストは `dependency_overrides` で各テスト独立の空リポジトリに差し替え。
  重複SKUは409、バリデーション違反は422。pytest 全12件緑、OpenAPI出力確認済み。
- commits: ブランチ issue-0002-product-register-list-api
