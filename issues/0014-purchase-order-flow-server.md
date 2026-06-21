# #0014 発注→入荷フロー(サーバ側 + 契約テスト)

- status: done
- created: 2026-06-21

## 目的 / 背景
受発注の核を実装する。発注(PurchaseOrder)を作り、入荷でその発注を受け入れて在庫を増やす。
WPF UI は #0015 に分ける(本issueはサーバ + 最小の契約テストまで)。

## ドメイン設計
- `PurchaseOrder(id, sku, quantity, status)`、status は ordered → received。
- 不変条件: 発注数 > 0 / 二重入荷の禁止(received の再入荷は不可) / 入荷時は対象商品が存在。
- 状態遷移(mark_received)は domain、PO入荷→在庫増のクロス操作の調整は api 層。

## スコープ
- domain: PurchaseOrder / PurchaseOrderStatus / AlreadyReceivedError
- repository: PurchaseOrderRepository(抽象 + InMemory + SQLite, 同一DBに別テーブル)
- api: `POST /purchase-orders`(発注, 商品なし404, 数量<1=422) / `GET /purchase-orders` /
  `POST /purchase-orders/{id}/receive`(入荷: 二重入荷409, PO/商品なし404)
- client(Core, 契約テスト用の最小): PurchaseOrderDto / IPurchaseOrderApiClient / 実装
- やらないこと: ViewModel / View(#0015)

## テスト内容(完了条件)
- pytest: 発注作成/一覧/入荷で在庫増+status received/二重入荷409/不明PO 404/不明sku 404/数量0 422
- domain: mark_received の二重呼び出しで AlreadyReceivedError
- 契約テスト: 発注→入荷で商品在庫が増える / 二重入荷で例外
- 高速ループ(check.ps1)は従来どおり(server pytest + client VMテスト)で緑

検証: `cd server && uv run pytest -q` / `cd client && dotnet test InventoryClient.ContractTests`

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: domain に PurchaseOrder/PurchaseOrderStatus/AlreadyReceivedError(発注数>0, 二重入荷禁止)。
  repository に PO 用(抽象+InMemory+SQLite, 別テーブル)。api に 発注/一覧/入荷の3エンドポイント
  (入荷は mark_received を先に検証して副作用前に409を弾き、その後 product.receive→両者を永続化)。
  Core に最小の PO クライアント(契約テスト用)。
- テスト: server pytest 31件(PO分9件: domain二重入荷/数量0, api 201/404/422/在庫増+received/二重入荷409/
  不明PO404/一覧)、契約テスト 6件(PO 2件: 入荷で在庫増/二重入荷で例外)すべて緑。check.ps1 緑。
- 次: WPF UI は #0015。
- commits: ブランチ issue-0014-purchase-order-flow-server
