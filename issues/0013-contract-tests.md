# #0013 APIクライアント↔サーバの契約テスト

- status: done
- created: 2026-06-21

## 目的 / 背景
C# の `ProductApiClient` と Python の FastAPI サーバの間の「契約」(JSONのフィールド名・型・
HTTPステータス)が一致していることを、実サーバ相手に検証する。ViewModel テストはモックなので
契約ズレ(camelCase の対応、404/409 など)を捕まえられない。ここを自動で守れるようにする。

## 方針(どこまで / どこに置くか)
- 実際の FastAPI を**サブプロセスで起動**し、本物の `ProductApiClient` で叩く統合テスト。
- python/uv 依存・サーバ起動で重く・やや不安定なので、**高速ループ(check.ps1)からは分離**した
  専用プロジェクト `InventoryClient.ContractTests` に置く(UIテストと同じ扱い=明示実行)。
- テスト分離のため、サーバの DB パスを環境変数で差し替え可能にする(`INVENTORY_DB`)。

## スコープ
- server: `DB_PATH` を `os.environ.get("INVENTORY_DB", "inventory.db")` に
- 新規 `client/InventoryClient.ContractTests`:
  - フィクスチャで空きポートを取り、temp DB を指定して uvicorn を起動 → ready を待つ → 終了時に kill
  - `ProductApiClient` で実HTTPを叩く

## テスト内容(完了条件)
- 登録の往復(返ってきた DTO の sku/name/quantity が一致 = 双方向シリアライズOK)
- 入荷/出荷で quantity が期待どおり(在庫エンドポイントの契約)
- 在庫不足(409)でクライアントが例外を投げる(エラー契約)
- 一覧に登録分が出る

検証コマンド: `cd client && dotnet test InventoryClient.ContractTests`
（高速ループ `scripts/check.ps1` には含めない）

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `InventoryClient.ContractTests`(Core参照)を新設。`ServerFixture`(IClassFixture)が空きポート+
  temp DB(INVENTORY_DB)で uvicorn をサブプロセス起動し ready 待ち、終了時に kill。出力は非同期で吸い出し
  パイプ詰まりを回避。本物の `ProductApiClient` で登録往復/入荷出荷/在庫不足409/一覧を検証。契約4件緑(約0.6秒)。
  server は DB_PATH を `INVENTORY_DB` で差し替え可能に。高速ループ(check.ps1)には含めない。
- commits: ブランチ issue-0013-contract-tests
