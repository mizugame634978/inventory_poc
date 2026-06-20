# inventory_poc — 在庫・受発注管理 POC

## このプロジェクトの目的(最重要)

これは **「Claude(私)がどこまで自律的に・人手の介入を減らして開発できるか」を研究する POC**。
売る製品を作るのが目的ではない。したがって:

- **人間への実装依頼(Learn by Doing)はしない。私が実装し、私がテストで検証する。**
- セッションは毎回リセットされる前提で動く。**知識は必ずファイルに残す**(このCLAUDE.md / `docs/` / `issues/` / memory)。
- 「動いた」と言う前に、必ずテストを通した事実で裏取りする。

## 自走のための知識の置き場所(セッションを跨ぐための約束)

| 種類 | 置き場所 | 用途 |
|---|---|---|
| 常時ロードの入口 | この `CLAUDE.md` | 目的・ルール・各docへのポインタ |
| 浅く広い全体像 | `docs/architecture.md` | アーキテクチャ・思想・機能全体図 |
| データモデル | `docs/data-model.md` | ER・エンティティ・不変条件 |
| 開発手順 | `docs/workflow.md` | issue→ブランチ→マージの手順 |
| UIテスト考察 | `docs/ui-testing-comparison.md` | WPF vs React のUI自動テスト比較と課題・改善の種 |
| 作業単位の記録 | `issues/NNNN-*.md` | 1機能=1issue。目的・スコープ・テスト・完了条件 |

新しいセッションで作業を始めるときは、**まず `docs/` を読み、次に対象の `issues/` を読む**こと。
コードをボトムアップに追うのは最後の手段(時間がかかる)。

## 開発ワークフロー(詳細は docs/workflow.md)

1. 作業は必ず issue から。`issues/NNNN-slug.md` を書く(目的・スコープ・テスト内容・完了条件)。
2. `issue-NNNN-slug` ブランチを切る。
3. 実装 + テスト。`cd server && uv run pytest -q` が緑になることが完了条件。
4. コミットメッセージ冒頭に `#NNNN` を付ける。`--no-ff` で main にマージ(issue単位の履歴を残す)。
5. issueファイルに結果(完了日・要点)を追記する。

## コーディングルール(軽量)

- **ロジックはサーバ(FastAPI)側、特に `server/app/domain.py` に寄せる**。WPF は表示と入力だけ。理由: ドメインが純粋なら pytest で高速・確実に自己検証でき、私が自走できる。
- ドメイン層は FastAPI / DB / HTTP に依存しない(import しない)。
- 不変条件(例: 在庫は負にならない)は **必ずテストで表現する**。テストが実行可能な仕様書になる。
- 日本語コメント可。業務ルールの「なぜ」を残す。

## よく使うコマンド

```bash
cd server && uv run pytest -q        # サーバのテスト(自己検証の中心)
cd server && uv run fastapi dev app/main.py   # 開発サーバ(http://localhost:8000)
cd client && dotnet test             # WPF の ViewModel テスト
cd client && dotnet build            # クライアント全体のビルド
```

## クライアント(WPF)のテスト方針

詳細は `issues/0003-wpf-product-list.md` と `issues/0004-wpf-ui-binding-tests.md`。要点だけ:
- ロジックは WPF 非依存の `client/InventoryClient.Core`(ViewModel/APIクライアント)に置く。
- **ViewModel をユニットテスト**(`InventoryClient.Tests`, xUnit + NSubstitute)。ここが本命・高速。
- **UI バインディング健全性テスト**(`InventoryClient.UiTests`, `Xunit.StaFact` の `[WpfFact]`)。
  in-process で Window を `Show()` し、バインディングエラーが出ないことを検証する。XAML のパス誤字など
  ViewModel テストで捕まらない UI デグレを捕捉する。
  - 注意: DataGrid の行(セル)を実体化させるには `Show()` が必須。Measure/Arrange だけではセル
    バインディングが評価されず、列の誤字を見逃す(#0004で確認済み)。
- 別プロセス起動の UI 自動化(FlaUI/WinAppDriver 等)は**やらない**(重く脆くROIが低い)。
