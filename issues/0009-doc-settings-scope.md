# #0009 ドキュメント(人間向け): Claude Code の設定スコープと起動ディレクトリ

- status: done
- created: 2026-06-21

## 目的 / 背景
このプロジェクトの自走ハーネス(Stop hook・権限)は `inventory_poc/.claude/settings.json` にある。
ところが **Claude Code はプロジェクト設定を「起動ルート」から読み、サブディレクトリの設定は
読み込まない**。そのため `inventory_poc` の親(例: `repos`)から起動するとハーネスが効かない。
この挙動は一般的でなく、人間が知らないとハマるので、人間向けに明文化する。

## スコープ
- やること: `docs/claude-code-settings-scope.md`(人間が読む前提)を新規作成
- やらないこと: 設定変更・コード変更

## 完了条件
- 上記ドキュメントがあり、起動ルール・効く/効かない例・正しい起動法・確認方法が書かれている
- `docs/autonomy-harness.md` から人間向けに導線がある

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `docs/claude-code-settings-scope.md`(人間向け)を作成。結論(設定は起動ルートから読まれ
  サブディレクトリは読まれない)・効く/効かない表・正しい起動法(cd inventory_poc && claude)・
  確認方法(/hooks、わざと赤テスト)・背景(本PJで観測した outputStyle の例)を記載。
  autonomy-harness.md から導線を追加。
- commits: ブランチ issue-0009-doc-settings-scope
