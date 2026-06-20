# #0006 入荷/出荷の API と UI

- status: done
- created: 2026-06-21

## 目的 / 背景
domain の `Product.receive` / `ship`(#0001)を API で公開し、WPF から在庫操作できるようにする。
在庫の入出庫という業務の核を、画面まで貫通させる。

## スコープ
- server:
  - `POST /products/{sku}/receive` 本文 `{amount}` → 在庫を増やす
  - `POST /products/{sku}/ship` 本文 `{amount}` → 在庫を減らす
  - HTTP マッピング: 数量 < 1 は 422(DTOで `Field(ge=1)`) / 商品なし 404 / 在庫不足 409
- client(Core): `IProductApiClient` に `ReceiveAsync` / `ShipAsync` を追加し実装
- client(ViewModel): 選択商品 + 数量入力 + 入荷/出荷コマンド。失敗は ErrorMessage に出す
- client(View): DataGrid の選択行 + 数量 TextBox + 入荷/出荷ボタン(薄く配線)
- やらないこと: 入出庫履歴の記録、永続化

## テスト内容(完了条件)
- server `tests/test_api.py`:
  - receive で在庫が増える / ship で減る
  - 在庫不足の ship は 409
  - 存在しない SKU は 404
  - amount=0 は 422
- client `InventoryClient.Tests`(ViewModel):
  - ReceiveCommand が API を呼び一覧を再読込する
  - 商品未選択での操作は API を呼ばずエラーにする
  - ship 失敗(API例外)時に ErrorMessage が出て一覧は壊れない
- client `InventoryClient.UiTests`: 既存のバインディング健全性テストが緑(新バインディング込み)

検証コマンド: `cd server && uv run pytest -q` と `cd client && dotnet test`

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: server に receive/ship エンドポイント追加(数量<1=422 を DTO `Field(ge=1)` で、404/409 を例外マッピング)。
  Core の `IProductApiClient` に Receive/Ship を追加。ViewModel に SelectedProduct/OperationAmount と
  Receive/Ship コマンド(選択・数量検証→API→再読込、失敗時は再読込しない)。View に在庫操作の行を追加。
  テスト: server 17件、ViewModel 7件、UI 1件すべて緑。UIテストは新バインディングの健全性も担保。
- commits: ブランチ issue-0006-receive-ship-api-ui
