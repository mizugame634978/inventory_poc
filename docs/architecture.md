# アーキテクチャと設計思想

> 浅く広いトップダウン文書。全体像を最短で掴むためのもので、網羅は目的としない。
> 詳細はコードと `issues/` を参照。

## 1. 全体構成

```
┌─────────────┐   HTTP(JSON)    ┌──────────────────────────┐
│  WPF client  │ ───────────────▶│  FastAPI server          │
│ (MVVM)       │ ◀───────────────│                          │
│ 表示・入力のみ │   OpenAPI契約    │  ┌────────────────────┐  │
└─────────────┘                 │  │ api層 (main.py)     │  │  ← HTTPの受け口
                                │  ├────────────────────┤  │
                                │  │ domain層 (domain.py)│  │  ← 業務ルール(純粋Python)
                                │  ├────────────────────┤  │
                                │  │ repository層        │  │  ← 永続化(今はメモリ)
                                │  └────────────────────┘  │
                                └──────────────────────────┘
```

## 2. 設計思想(なぜこうするか)

- **ロジックをサーバの domain 層に集約する。** GUI(WPF)は自己検証が難しい層なので、
  正しさを判定すべきロジックを GUI に置かない。domain を純粋 Python に保てば pytest で
  高速・確定的に検証でき、Claude が人手なしで「実装→テスト→自己検証」のループを回せる。
- **層は内側ほど依存が少ない。** domain は api/repository/HTTP を import しない。
  これにより domain 単体テストがサーバ起動なしで動く(現状 0.2 秒以下)。
- **不変条件はテストで表現する。** 「在庫は負にならない」などの業務ルールは、文章ではなく
  実行可能なテストにする。テストが仕様書を兼ね、デグレを機械的に防ぐ。

## 3. レイヤの責務

| 層 | ファイル | 責務 | 依存してよい先 |
|---|---|---|---|
| api | `server/app/main.py` | HTTPの入出力、DTO変換 | domain, repository |
| domain | `server/app/domain.py` | 業務ルール・不変条件 | (なし=純粋Python) |
| repository | `server/app/repository.py` | 保管・取得(抽象 `ProductRepository` + InMemory/SQLite 実装) | domain |

抽象 `ProductRepository`(ABC)に api 層が依存し、実装(メモリ/SQLite)を `Depends` で差し込む。
#0007 で InMemory→SQLite に差し替えたが **domain.py は無変更** で済んだ(レイヤ分離の実証)。
注意: SQLite 実装は接続をオペレーション毎に開閉する(スレッドプール実行で安全。`:memory:` は使えない)。
在庫変更後は `repo.update(product)` で永続化する(メモリ参照に依存しない正しい形)。

## 4. 機能全体図(ロードマップ)

- [x] 商品の在庫を入荷/出荷する(在庫非負の不変条件) … issue #0001
- [x] 商品の登録・一覧 API … issue #0002
- [x] WPF クライアントから登録・一覧を表示 … issue #0003
- [x] WPF UI バインディング健全性テスト … issue #0004
- [x] 入荷/出荷の API と UI … issue #0006
- [x] 永続化を SQLite に差し替え(domain 非依存で実証) … issue #0007
- [x] APIクライアント↔サーバの契約テスト … issue #0013
- [x] 発注 → 入荷 の受発注フロー(サーバ + 契約テスト) … issue #0014
- [x] 発注 → 入荷 の WPF UI(商品/発注のタブ) … issue #0015
- [ ] (backlog) memory スナップショットスクリプト … issue #0012(後回し)

## 5. クライアント(WPF)の構成と思想

テスト容易性のため 3 プロジェクトに分割している(`client/`)。

| プロジェクト | TFM | 役割 | WPF依存 |
|---|---|---|---|
| `InventoryClient.Core` | net10.0 | ViewModel・APIクライアント・DTO | なし |
| `InventoryClient` | net10.0-windows | View(XAML)・App | あり(薄い) |
| `InventoryClient.Tests` | net10.0 | ViewModel のユニットテスト(高速・本命) | なし |
| `InventoryClient.UiTests` | net10.0-windows | UI バインディング健全性テスト | あり |
| `InventoryClient.ContractTests` | net10.0 | 実サーバ相手の契約テスト(明示実行・python/uv必要) | なし |

思想: ロジックを WPF 非依存の Core に集約し、ViewModel をテストする。ViewModel は具象 HttpClient ではなく
`IProductApiClient` に依存する(依存性逆転)ので、テストではモックに差し替えてネットワーク無しで検証できる。
View は「バインドするだけの薄い層」に保つ。

UI のデグレ(XAMLバインディング切れ)は ViewModel テストでは捕まらないため、`InventoryClient.UiTests` で
in-process に Window を `Show()` してバインディングエラーが出ないことを検証する(`Xunit.StaFact`)。
ただし別プロセス起動の UI 自動化(FlaUI 等)はやらない — 重く脆く、上記で大半のデグレを捕まえられる。

## 6. 技術選定

- **client: WPF (MVVM)** — Windows ネイティブGUI。大規模化に強い。Web技術より情報が少なく研究価値が高い。
- **server: FastAPI** — POCなので認証/メール/並列処理は入れない。シンプルで素早い。
