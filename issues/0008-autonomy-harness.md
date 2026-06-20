# #0008 自走ハーネス: 統一チェック + 権限許可 + Stop hook

- status: done
- created: 2026-06-21

## 目的 / 背景
自律開発(このPJの主目的)の「閉じた品質ループ」をリポジトリに備える。
変更したら自動でテストが回り、赤なら自分で直してから終了する状態を作る。

## スコープ
1. **統一チェック** `scripts/check.ps1`: server pytest + client ViewModel テストを1発実行し、
   失敗で非0を返す。**UIテストは含めない**(デスクトップ依存=無人ループで不安定, #0004参照)。
2. **Stop hook** `scripts/stop-check.ps1`: ターン終了時に check を実行し、赤なら exit 2 で停止を
   ブロックして失敗内容を返す。無限ループ防止に `stop_hook_active` を尊重。
3. **権限許可リスト**: pytest / dotnet test / dotnet build / 主要 git を allow にし承認待ちを減らす。
4. 設定は `inventory_poc/.claude/settings.json`(リポジトリ同梱)に置く。

## 前提・制約
- 設定が効くのは **inventory_poc から claude を起動したとき**(launch root 依存)。
- UIテストは自動ループ外。明示的に `dotnet test` で回す。
- 不可逆・外向き操作は自律ループに入れない(ガードレール)。

## 完了条件
- `scripts/check.ps1` 単体実行で全テスト緑 → exit 0
- `scripts/stop-check.ps1` に `{}` を渡すと check が走り、緑なら exit 0
  / `{"stop_hook_active":true}` を渡すと即 exit 0(ループ防止)
- `.claude/settings.json` が妥当な JSON で hooks.Stop と permissions.allow を含む
- 設計を docs に記載(`docs/autonomy-harness.md`)し CLAUDE.md から辿れる

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `scripts/check.ps1`(server22+VM7を1発, exit0)と `scripts/stop-check.ps1`(stdin JSON,
  stop_hook_active ガード, 赤で exit2)を作成。`.claude/settings.json` に permissions.allow と
  hooks.Stop をマージ(JSON妥当性確認済み)。`docs/autonomy-harness.md` に設計を記載、CLAUDE.md から導線。
- 検証: check.ps1 単体で全緑 exit0、stop-check.ps1 を `{}` で緑→0 / `{"stop_hook_active":true}` で即0 を確認。
- 既知の前提: Stop hook は inventory_poc から claude を起動したときだけ有効(launch root 依存)。
  現セッションは repos 起動のため、このセッションでは hook 未ロード。次回 inventory_poc 起動で発火する。
- commits: ブランチ issue-0008-autonomy-harness
