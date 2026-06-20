# #0005 ドキュメント: UI自動テストの比較(WPF vs React)と課題整理

- status: done
- created: 2026-06-21

## 目的 / 背景
「軽く自動テストしたい」という要望に対し、WPF だと in-process でも実描画(Show)が要るなど
ハードルが高いことが分かった。React(jsdom / Playwright)と明示的に比較した結果を文書化し、
WPF の課題と改善の方向性を後から辿れるようにする。

## スコープ
- やること: `docs/ui-testing-comparison.md` を新規作成(比較表・課題・改善の種)
- やらないこと: 実装変更・テスト追加(別issue)

## 完了条件
- `docs/ui-testing-comparison.md` がある
- architecture.md または CLAUDE.md から辿れる(ポインタ)

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `docs/ui-testing-comparison.md` を作成。FlaUI≒Playwright の同格比較、jsdom層の不在という
  WPF の根本課題、自律実行との相性、見えた課題(軽いUIテストがやりにくい等)と改善の種(View を薄く・
  バインディングエラーのゲート化・FlaUI限定導入 等)をまとめた。CLAUDE.md からポインタを追加。
- commits: ブランチ issue-0005-doc-ui-testing-comparison
