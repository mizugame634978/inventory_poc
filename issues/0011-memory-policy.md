# #0011 memory 方針の確定(個人開発者向け)とパス規約

- status: done
- created: 2026-06-21

## 目的 / 背景
POC の主対象を「個人開発者」と決定。memory は無効化せず**有効のまま使う**(自動蓄積・関連想起の
価値を活かす)。使い分けの方針と、環境依存パス禁止の規約を明文化する。

## 決定事項
- memory は有効。`autoMemoryEnabled: false` は入れない。
- 使い分け: 共有・再現に効く知識は in-repo(CLAUDE.md/docs/issues)。個人的・環境的・カジュアルな
  運用知/好みは memory。durable で共有価値が出たら docs へ昇格。
- 起動は `inventory_poc` 固定(memory がこのプロジェクト専用キーになり、兄弟と隔離される)。
- ドキュメント/コードに特定環境の絶対パス(ユーザ名入りフルパス等)を書かない。

## スコープ
- CLAUDE.md に「memory 方針」と「パス規約」を追記
- ホームの memory を整理: 親(repos)キーにある inventory 用 memory を inventory_poc キーへ移し、
  内容から絶対パスを除去。親キーの重複は削除(リポジトリ外操作・git対象外)
- やらないこと: snapshot スクリプト(必要なら別issue #0012)

## 完了条件
- CLAUDE.md に方針とパス規約がある
- inventory_poc キーの memory に絶対パスが無い / 親キーの inventory 用 memory が無い
- 統一チェックが緑(回帰なし)

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: 対象=個人開発者に確定。memory は有効のまま(無効化しない)。CLAUDE.md に「memory 方針」と
  「絶対パス禁止」のパス規約を追記。ホーム memory を inventory_poc キーへ移動し内容の絶対パスを除去、
  親(repos)キーの重複を削除。check.ps1 緑。
- snapshot スクリプトは未実装(必要なら #0012)。
- commits: ブランチ issue-0011-memory-policy
