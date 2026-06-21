 # inventory_poc — 在庫・受発注管理 POC

  WPF(クライアント) + FastAPI(サーバ) で作った在庫・受発注管理のPOC。
  製品化が目的ではなく、**「Claude(AI)がどこまで自律的に・人手少なく開発できるか」を研究する場**を兼ねる。
  (現在: v1.1.0 / CHANGELOG.md 参照)

  ## 技術スタック
  - クライアント: WPF (.NET / MVVM, CommunityToolkit.Mvvm) — `client/`
  - サーバ: FastAPI (Python, uv 管理, SQLite 永続化) — `server/`

  ## 必要なもの
  - Python 3.12+ と uv
  - .NET 10 SDK（WPF 実行には Windows + WindowsDesktop ランタイム）

  ## 動かし方
  ターミナルを2つ使う。

  サーバ:
  ```
  cd server
  uv run fastapi dev app/main.py      # http://127.0.0.1:8000  (/docs で API も見られる)
  ```

  クライアント:
  ```
  cd client
  dotnet run --project InventoryClient
  ```
  アプリは「商品」「発注」タブ構成。商品の登録・入荷・出荷、発注→入荷→キャンセルが操作できる。
  (在庫は負にならない／二重入荷は拒否、などの業務ルール付き)

  ## テスト
  ```
  pwsh -File scripts/check.ps1        # 高速チェック: サーバ pytest + ViewModel テスト(自走の合図)
  cd client && dotnet test            # 全テスト(UI・契約テスト含む。UIはデスクトップ、契約はpython/uv必要)
  ```

  ## リポジトリ構成
  ```
  server/    FastAPI(domain / api / repository) と pytest
  client/    WPF。Core(VM・APIクライアント, WPF非依存) / WPF(View) / Tests / UiTests / ContractTests
  docs/      設計・振り返りドキュメント(下記索引)
  issues/    issue駆動の作業記録(1機能=1ファイル)
  scripts/   check.ps1(統一テスト) / stop-check.ps1(自走ループ用)
  .claude/   このプロジェクト用の Claude Code 設定(起動はこの直下から)
  ```

  ## ドキュメント索引
  - `docs/architecture.md` — 全体構成・設計思想・機能ロードマップ
  - `docs/data-model.md` — エンティティ・不変条件・APIエンドポイント
  - `docs/workflow.md` — issue→ブランチ→マージの開発手順
  - `docs/testing-strategy.md` — テスト構成の総括・製品化時の指針
  - `docs/library-choices.md` — 指定外ライブラリの選定理由(Prism比較など)
  - `docs/ui-testing-comparison.md` — WPF vs React のUI自動テスト比較
  - `docs/autonomy-harness.md` — 自走ハーネス(統一チェック・Stop hook・権限)の設計
  - `docs/loop-experiment-findings.md` — 自走ループ(/loop)の実験結果と限界
  - `docs/claude-code-settings-scope.md` — Claude Code 設定が起動ディレクトリ依存である注意
  - `docs/harness-template-design.md` — ハーネスを他プロジェクトへ再利用する雛形の設計
  - `CLAUDE.md` — エージェント(Claude)向けの作業規約・知識地図

  ## 補足
  - 自走ハーネス(Stop hook 等)を有効にするには、**このフォルダを作業ルートにして** Claude Code を起動する
    (理由: `docs/claude-code-settings-scope.md`)。
