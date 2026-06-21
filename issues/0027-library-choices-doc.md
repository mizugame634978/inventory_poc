# #0027 ドキュメント: ライブラリ/技術選定の振り返り

- status: done
- created: 2026-06-21

## 目的
ユーザが指定した WPF / FastAPI 以外の、私(Claude)が選んだライブラリ・技術の選定理由を
`docs/library-choices.md` にまとめる。CommunityToolkit.Mvvm vs Prism、TabControl直書き vs
Prism region の比較も含める。

## スコープ
- やること: 選定理由の文書化。CLAUDE.md から導線。
- やらないこと: コード変更。

## 完了条件
- 文書がある(指定vs選定、各選定理由、あえて入れなかったもの、Prism比較、判定)
- check.ps1 緑(回帰なし)

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: docs/library-choices.md を作成(指定vs選定、各選定理由表、あえて入れなかったもの、CommunityToolkit.Mvvm vs Prism、TabControl直書き vs Prism region、総括)。CLAUDE.mdから導線。
- commits: ブランチ issue-0027-library-choices-doc
