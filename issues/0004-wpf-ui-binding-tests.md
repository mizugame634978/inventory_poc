# #0004 WPF UI テスト(バインディング健全性)

- status: done
- created: 2026-06-20

## 目的 / 背景
ロジック(ViewModel)が正しくても、XAML のバインディング切れ(プロパティ改名・パス誤字・
コントロール削除)で UI はデグレする。この種の劣化を機械的に捕まえる軽量な UI テストを追加する。

開発・実行とも Windows 専用前提(WPFはWindowsのみ)。このPCはWindowsなので支障なし。

## 方針(どこまでやるか)
- in-process で `MainWindow` を生成し、テスト用 ViewModel を DataContext に注入してレイアウトを評価する。
- 検証は2点に絞る:
  1. **バインディングエラーが発生しないこと**(WPF の DataBinding トレースを TraceListener で捕捉)
  2. **DataGrid に期待行数が出ること**(ItemsSource バインディングが生きている証拠)
- 別プロセス起動の UI 自動化(FlaUI 等)はやらない。重く・脆く、上記で大半のデグレを捕まえられるため。
- 速度を保つため、UI テストは fast な ViewModel テストとは別プロジェクト `InventoryClient.UiTests` に置く。

## 実装メモ
- `Xunit.StaFact` の `[WpfFact]` で STA + Dispatcher を確保。
- `MainWindow` を ViewModel 注入可能にリファクタ(既定の実サーバ構成も維持)。
- 表示(Show)せず Measure/Arrange でレイアウトを走らせ、非対話セッションでも動くようにする。

## テスト内容(完了条件)
`InventoryClient.UiTests` を `dotnet test` で:
- 一覧読込後、DataGrid の行数がモック商品数と一致する
- 上記の過程でバインディングエラーが 0 件
- (劣化検出の妥当性確認として)わざと壊した場合に落ちることを手元で確認

検証コマンド: `cd client && dotnet test`(VMテスト + UIテストすべて緑) / `cd server && uv run pytest -q`(回帰)

## 結果(完了時に追記)
- done: 2026-06-20
- 要点: `InventoryClient.UiTests`(net10.0-windows / UseWPF)を新設。`Xunit.StaFact` の `[WpfFact]` で
  STA+Dispatcher を確保し、in-process で `MainWindow` を生成→`Show()`→`LoadAsync`→バインディング検証。
  `MainWindow` を ViewModel 注入可能にリファクタ(実行時の実サーバ構成は維持)。
  DataGrid に `x:Name="ProductsGrid"` を付与。UIテスト1件 約0.6秒で緑。
- 重要な学び:
  - **DataGrid のセル(行内)バインディングは `Show()` しないと実体化せず評価されない。**
    当初 Measure/Arrange だけで試したが、列の誤字 `{Binding Skuu}` を見逃した。`Show()` に変えたら
    `'Skuu' property not found` を検出できた(壊して落ちることを確認済み=テストに効力がある)。
  - 画面外(Left/Top=-10000, ShowInTaskbar=false)に表示して邪魔を減らし、finally で Close。
- commits: ブランチ issue-0004-wpf-ui-binding-tests
