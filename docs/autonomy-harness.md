# 自走ハーネスとループ

> このプロジェクトの主目的(Claudeの自律開発研究)を支える「足場」と「反復の駆動」の設計。
> (issue #0008 / 2026-06-21)

## 1. 用語
- **ハーネス**: エージェントが人手なしで「行動→結果観測→自己修正」できる足場。
  ツール・**オラクル(テスト)**・知識の永続化・権限・ガードレール。
- **ループ**:
  - 内側: 編集→テスト→直す(1ターン内)
  - 外側: issue を1つ片付け→検証→マージ→次(ターン/セッション跨ぎ)
  - トリガ: hook / `/loop` / cron で自動起動

## 2. このリポジトリのハーネス構成
| 要素 | 実体 |
|---|---|
| ツール | Claude Code(編集/シェル/git) |
| オラクル | `scripts/check.ps1`(server pytest + client ViewModel テストを1発) |
| 自動トリガ | Stop hook(`scripts/stop-check.ps1`)= ターン終了時に check |
| 知識の永続化 | `CLAUDE.md` / `docs/` / `issues/` / memory |
| 権限 | `.claude/settings.json` の allow リスト(承認待ちを削減) |
| ガードレール | issue ブランチ・テストゲート・git revert・不可逆操作は手動 |

## 3. 閉じた品質ループ(Stop hook)
1. 私(Claude)が作業を終え、停止しようとする。
2. Stop hook が `scripts/stop-check.ps1` を実行 → `check.ps1`(高速テスト)を回す。
3. 赤なら exit 2 で停止をブロックし、失敗内容を私に返す → 私が直す。
4. 緑なら exit 0 → 停止が許可される。
- 無限ループ防止: 入力 JSON の `stop_hook_active` が true のときは即 exit 0。

## 4. 統一チェックの方針
- **含む**: server `uv run pytest`、client `dotnet test InventoryClient.Tests`(ViewModel)。
  どちらもヘッドレス・決定的・高速。
- **含めない**: `InventoryClient.UiTests`(`Show()` がデスクトップ依存。無人ループだと不安定 → #0004)。
  UIテストは人がいるときに明示実行する。

## 4.5 受け入れテスト必須ルール(#0025〜)

外側ループで issue に着手する前に、**その issue に「テスト内容(完了条件)」セクションと具体的な
テスト名があるか**を確認する。無ければ**実装に着手せず**、その issue に
`blocked: 受け入れテスト未定義` を追記して次の候補へ進む。

狙い: 「曖昧な issue で止まる」を agent の判断依存(=保証が弱い)から、**チェック可能な構造的ルール**に
格上げする(ループ実験 #0023 の知見 → `docs/loop-experiment-findings.md`)。これにより、仕様が
固まっていない作業を無断で実装する「暴走」を機械的に防ぐ。

## 5. 効かせる前提(重要)
- これらの設定は `inventory_poc/.claude/settings.json` にある。**`inventory_poc` から claude を
  起動したときだけ有効**(設定は launch root から読まれるため)。親 `repos` から起動すると無効。
- 自走研究としてアプリを触るときは、**`inventory_poc` を作業ルートにして claude を起動する**こと。
- なぜ起動ディレクトリで効き方が変わるのか(人間向けの詳しい説明)は
  `docs/claude-code-settings-scope.md` を参照。

## 6. まだ入れていない / 今後
- **外側ループの自動駆動**(`/loop` で open issue を連続処理)は未導入。Stop hook で内側ループが
  安定してから段階的に試す。
- cron(定時リモート実行)は「夜間に1イシュー進める」等が欲しくなったら検討。
- 不可逆・外向き操作(リモート push、データ削除、外部公開)は引き続き人間のゲートを残す。
