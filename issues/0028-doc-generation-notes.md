# #0028 ドキュメント: API/ER 自動生成の方針と製品化時の推奨

- status: done
- created: 2026-06-21

## 目的
「API/ER 図を自動生成しなかった理由」と、製品化時の推奨(SQLAlchemy + FK制約 + ER自動生成)を
`docs/library-choices.md` に追記する。

## スコープ
- やること: library-choices.md に「ドキュメント自動生成(API/ER)について」節を追加。
- やらないこと: コード変更。

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: API は FastAPI 内蔵 Swagger＋手書き表で充足。ER は ORM/FK 無し・小規模のため手書き
  (自動生成は外部依存＋FK未宣言で関係も描けない)。手書きERは乖離し得るのが弱点。
  製品化時は SQLAlchemy + FK制約 + ER自動生成を推奨(軽量案として Mermaid erDiagram)。
- commits: ブランチ issue-0028-doc-generation-notes
