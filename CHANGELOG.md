# Changelog

このファイルは版ごとの主な変更点をまとめる(要点のみ。詳細は `issues/` と git 履歴を参照)。

## [1.1.0] - 2026-06-21

### 追加 (API)
- `GET /products/{sku}` 単一商品取得 (#0018)
- `GET /products/summary` 在庫サマリ(商品数・在庫合計) (#0019)
- `PUT /products/{sku}` 商品名の変更 (#0020)
- `DELETE /products/{sku}` 商品の削除 (#0021)
- `POST /purchase-orders/{id}/cancel` 発注のキャンセル(状態: ordered→cancelled) (#0022)
- `GET /purchase-orders/{id}` 単一発注取得 (#0025)

### 追加 (自走ハーネス / 研究)
- 外側ループ(`/loop`)の実験と結果記録 (`docs/loop-experiment-findings.md`)
- 受け入れテスト必須ルール: 受け入れテスト見出しの無い issue には着手しない
  (`docs/autonomy-harness.md` 4.5)

### 備考
- 上記 API の多くは `/loop` による自走ループで実装・マージされた(自律開発の実験)。
- テスト: server pytest 50 / ViewModel 13 / UI binding 2 / 契約 6(全緑)。
- 保留(blocked)中の backlog: #0012(memoryスナップショット), #0023(在庫僅少=業務判断待ち),
  #0026(受け入れテスト未定義)。

## [1.0.0] - 2026-06-21

### 追加
- 商品の登録・一覧・入荷・出荷(在庫は負にならない不変条件) (#0001, #0002, #0006)
- 発注 → 入荷 フロー(二重入荷の禁止) (#0014)
- 永続化を SQLite に(domain 非依存で差し替え可能) (#0007)
- WPF クライアント: 商品/発注タブ・タブ自動読み込み・ローディング表示
  (#0003, #0015, #0016, #0017)
- 多層テスト: domain/api(pytest)・ViewModel(xUnit)・UIバインディング(StaFact)・契約(実サーバ)
  (#0004, #0013)
- 自走ハーネス(統一チェック `scripts/check.ps1`・Stop hook・権限)と運用ドキュメント一式 (#0008)
