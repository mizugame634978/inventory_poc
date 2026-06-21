  # harness-template/ 設計ブループリント

  > 目的: 別セッションの Claude が、この1ファイルを読むだけで `harness-template/` ディレクトリを
  > 再生成できるようにする自己完結の設計書。自走ハーネスを新規プロジェクトへ再利用するための雛形。

  ## 設計方針
  1. スタック依存なのは `scripts/check.ps1` の中身だけ。他は汎用 → リテラルで固定。
  2. install 時に置き換える箇所は `{{PLACEHOLDER}}` で明示し、末尾に一覧を置く。
  3. ドット始まりは copy 時に消えやすいので `dot-claude/` に収め、install 時に `.claude/` へリネーム。
  4. README に bootstrap チェックリスト(コピー対応表＋穴埋め＋検証)を置く＝再生成の起点。

  ## ディレクトリツリー
  ```
  harness-template/
  ├── README.md                          # 使い方=bootstrapチェックリスト
  ├── MANIFEST.md                        # コピー対応表 + プレースホルダ一覧
  ├── dot-claude/
  │   └── settings.json                  # install先: <project>/.claude/settings.json  [placeholder]
  ├── scripts/
  │   ├── check.ps1                      # 統一オラクル [structure=verbatim / body=placeholder]
  │   └── stop-check.ps1                 # Stop hook本体 [verbatim]
  ├── CLAUDE.md.tmpl                     # install先: <project>/CLAUDE.md  [placeholder]
  ├── docs/
  │   ├── workflow.md                    # issue→branch→merge [verbatim]
  │   ├── autonomy-harness.md            # 設計+受け入れテスト必須ルール [near-verbatim]
  │   └── claude-code-settings-scope.md  # 起動ルール注意 [verbatim]
  ├── issues/
  │   └── _TEMPLATE.md                   # issue雛形 [verbatim]
  └── loop-prompt.txt                    # /loop プロンプト(受け入れテスト必須版) [verbatim]
  ```

  ## ファイル内容

  ### scripts/stop-check.ps1 — [verbatim]
  ```
  #!/usr/bin/env pwsh
  # Stop hook 用。stdin の JSON を受け取り、stop_hook_active 中なら何もしない(無限ループ防止)。
  # それ以外は check.ps1 を実行し、赤(非0)なら exit 2 で停止をブロックして失敗内容を返す。
  $ErrorActionPreference = 'Continue'
  $raw = [Console]::In.ReadToEnd()
  try { $payload = $raw | ConvertFrom-Json } catch { $payload = $null }
  if ($payload -and $payload.stop_hook_active) { exit 0 }
  $out = & (Join-Path $PSScriptRoot 'check.ps1') 2>&1
  if ($LASTEXITCODE -ne 0) {
      [Console]::Error.WriteLine("自動チェックが失敗しました。緑にしてから終了してください:`n" + ($out -join "`n"))
      exit 2
  }
  exit 0
  ```

  ### scripts/check.ps1 — [structure=verbatim / body=placeholder]
  ```
  #!/usr/bin/env pwsh
  # 統一オラクル: fast・決定的・ヘッドレスなテストだけを1コマンドで実行し、失敗で非0を返す。
  # $PSScriptRoot 起点で cwd 非依存。UI等デスクトップ依存・重いテストはここに入れない。
  $ErrorActionPreference = 'Continue'
  $root = Split-Path $PSScriptRoot -Parent
  $failed = $false

  # ===== {{PROJECT_CHECKS}} : このプロジェクトのテストコマンドに置き換える =====
  # 参考(置換して使う):
  #   Write-Host '=== server ==='
  #   Push-Location (Join-Path $root 'server'); uv run pytest -q
  #   if ($LASTEXITCODE -ne 0) { $failed = $true }; Pop-Location
  #   Write-Host '=== client unit ==='
  #   Push-Location (Join-Path $root 'client'); dotnet test {{UNIT_TEST_PROJECT}}
  #   if ($LASTEXITCODE -ne 0) { $failed = $true }; Pop-Location
  # ===== /{{PROJECT_CHECKS}} =====

  if ($failed) { Write-Host 'CHECK: FAILED'; exit 1 }
  Write-Host 'CHECK: OK'; exit 0
  ```

  ### dot-claude/settings.json — [placeholder]
  ```
  {
    "outputStyle": "default",
    "permissions": {
      "allow": [ {{ALLOW_RULES}} ]
    },
    "hooks": {
      "Stop": [
        { "hooks": [ {
          "type": "command",
          "shell": "powershell",
          "command": "pwsh -NoProfile -File scripts/stop-check.ps1",
          "timeout": 120,
          "statusMessage": "自動チェック実行中..."
        } ] }
      ]
    }
  }
  ```
  {{ALLOW_RULES}} 例(新スタックのコマンドに合わせる):
  "Bash(uv run pytest*)","Bash(dotnet test*)","Bash(dotnet build*)","Bash(git status*)","Bash(git diff*)","Bash(git add*)","Bash(git commit*)","Bash(git switch*)","Bash(git merge*)"

  ### issues/_TEMPLATE.md — [verbatim]
  ```
  # #NNNN タイトル

  - status: open
  - created: YYYY-MM-DD

  ## 目的 / 背景
  ## スコープ
  ## テスト内容(完了条件)   ← 必須。無いと「受け入れテスト必須ルール」で自走ループは着手しない
  ## 結果(完了時に追記)
  - done:
  - 要点:
  - commits:
  ```

  ### loop-prompt.txt — [verbatim]
  ```
  自走サイクルを1回実行する。issues/ で「status: open かつ blocked 行なし」の最小番号 issue を選ぶ。
  着手前にその issue へ「## テスト内容(完了条件)」見出しがあるか確認し、無ければ実装せず
  blocked: 受け入れテスト未定義 を追記して次へ進む(受け入れテスト必須ルール)。
  対象が無ければ「バックログ空」と報告してループ終了。着手時は docs/workflow.md に従い branch→実装→
  pwsh -File scripts/check.ps1 が緑→issue追記→--no-ff マージ。範囲外を発明しない。各サイクルを3行で報告。
  ```

  ### CLAUDE.md.tmpl — [placeholder]（節構成は固定、{{...}}を埋める）
  - 見出し `# {{PROJECT_NAME}}`
  - `## このプロジェクトの目的`: {{PURPOSE}}（自律研究/製品か、人間への実装依頼の要否）
  - `## 知識の置き場所`: 表(入口=CLAUDE.md / 全体像=docs/architecture.md,data-model.md /
    手順=docs/workflow.md / ハーネス=docs/autonomy-harness.md / 作業単位=issues/NNNN-*.md)
  - `## 開発ワークフロー`: issue→issue-NNNN ブランチ→`pwsh -File scripts/check.ps1` 緑→issue追記→`--no-ff` マージ
  - `## コーディングルール`: ロジックをテスト可能な層へ寄せる / 不変条件はテストで表現 /
    特定環境の絶対パス禁止 / {{STACK_SPECIFIC_RULES}}
  - `## memory 方針`: {{MEMORY_POLICY}}（個人開発なら有効・durableはdocs昇格 等）
  - `## よく使うコマンド`: コードフェンスで `pwsh -File scripts/check.ps1`(統一チェック) と {{RUN_COMMANDS}} を列挙
  - 末尾に「起動はプロジェクト直下から claude（設定/hook/CLAUDE.mdが読まれる条件。
    docs/claude-code-settings-scope.md）」

  ### docs/workflow.md — [verbatim]（骨子から再生成可）
  - 手順: ①issue作成(先に完了条件を書く) ②`issue-NNNN-slug` ブランチ ③実装+`check.ps1`緑
    ④コミット冒頭に `#NNNN` ⑤`--no-ff` で main マージ ⑥issueに結果追記
  - issueテンプレ(= issues/_TEMPLATE.md)
  - 「なぜ: git blame→#NNNN→issue文書で背景まで辿れる/1issueを小さく保つ」

  ### docs/autonomy-harness.md — [near-verbatim]（骨子）
  - 用語: ハーネス(オラクル/知識永続化/権限/ガードレール) と ループ(内側=編集→テスト→直す /
    外側=issue反復 / トリガ=hook,/loop,cron)
  - 構成表(ツール/オラクル=check.ps1/自動トリガ=Stop hook/知識=CLAUDE.md,docs,issues,memory/権限/ガードレール)
  - 閉じた品質ループ: ターン終了→stop-check→check→赤ならexit2でブロック→直す。stop_hook_activeで無限ループ防止
  - 統一チェック方針: 含む=fast/決定的(unit,api)、含めない=UI(デスクトップ依存)・重い統合
  - 4.5 受け入れテスト必須ルール: 着手前に issue へ「## テスト内容(完了条件)」見出しが無ければ
    実装せず `blocked: 受け入れテスト未定義` を追記。曖昧で止まるを判断依存→構造的ルールに格上げ
  - 効かせる前提: プロジェクト直下から claude 起動(launch-root依存)

  ### docs/claude-code-settings-scope.md — [verbatim]（骨子）
  - 結論: 設定/hook は「起動した作業ルート直下の .claude」しか読まれない。サブフォルダは無視
  - 効く/効かない表(親から起動=✕ / プロジェクト直下から起動=○)
  - 正しい起動法(cd <project> して claude)・確認方法(/hooks に出る、わざと赤にして停止ブロック)
  - パスは環境依存なので位置関係で説明(フルパスを書かない)

  ## MANIFEST.md

  コピー対応表:
  | テンプレ内 | install先 |
  |---|---|
  | dot-claude/settings.json | .claude/settings.json |
  | scripts/* | scripts/* |
  | CLAUDE.md.tmpl | CLAUDE.md |
  | docs/* | docs/* |
  | issues/_TEMPLATE.md | issues/_TEMPLATE.md |
  | loop-prompt.txt | (貼り付け用。リポジトリに置くかは任意) |

  プレースホルダ一覧:
  | トークン | 意味 | 例 |
  |---|---|---|
  | {{PROJECT_NAME}} | プロジェクト名 | inventory_poc |
  | {{PURPOSE}} | 目的 | 自律開発の研究POC |
  | {{PROJECT_CHECKS}} | checkのテスト実行行 | pytest / dotnet test |
  | {{UNIT_TEST_PROJECT}} | 高速ユニットテスト対象 | InventoryClient.Tests |
  | {{ALLOW_RULES}} | 権限allow | Bash(uv run pytest*) 等 |
  | {{RUN_COMMANDS}} | 起動/開発コマンド | uv run fastapi dev … |
  | {{STACK_SPECIFIC_RULES}} | スタック固有規約 | ドメインはWPF非依存 等 |
  | {{MEMORY_POLICY}} | memory方針 | 個人開発・durableはdocs昇格 |

  ## README.md = bootstrap チェックリスト
  ```
  1. 新リポジトリで git init。作業ルート=プロジェクト直下に固定。
  2. MANIFEST.md の対応表どおりコピー(dot-claude→.claude、CLAUDE.md.tmpl→CLAUDE.md)。
  3. ★まずオラクルを通す: check.ps1 の {{PROJECT_CHECKS}} を新スタックのテストに置換。
     テスト0件でも pwsh -File scripts/check.ps1 が exit 0 になることを確認。
  4. .claude/settings.json の {{ALLOW_RULES}} を新スタックに合わせる。
  5. CLAUDE.md の各 {{...}} を埋める。
  6. プロジェクト直下から claude 起動 → /hooks に Stop が出るか確認。
     わざとテストを赤にして停止がブロックされることを確認(=ループが効く)。
  7. 以降は issue 駆動。必要なら loop-prompt.txt を /loop で投入して自走。
  8. docs/architecture.md, docs/data-model.md は新規に書く(プロジェクト固有)。
  ```

  ## 補足(再生成時の注意)
  - OS差: 非Windowsなら check.ps1/stop-check.ps1 を bash 移植し、settings の shell を bash に。構造は同一。
  - 最優先は手順3(オラクル): これが緑にならないと他は意味を持たない。
  - launch-root 規律は README と CLAUDE.md の両方に明示(最頻のハマり所)。

