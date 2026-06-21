# #0017 タブ表示時の自動読み込み

- status: done
- created: 2026-06-21

## 目的 / 背景
タブ切り替えのたびに手で「読み込み」を押すのは一般的でない。起動時・タブ表示時に自動で
読み込むようにする。手動「読み込み」ボタンは補助として残す。
これにより「発注の入荷後、商品タブの在庫が古いまま」(#0015の割り切り)も解消する
(商品タブに切り替えた瞬間に再取得されるため)。

## 実装
- Core: `IRefreshableViewModel { Task LoadAsync() }` を定義し、ProductListViewModel /
  PurchaseOrderViewModel に実装(両者とも既に LoadAsync を持つ)。
- View(MainWindow): 起動時(Loaded)と TabControl.SelectionChanged で、選択タブの
  DataContext を IRefreshableViewModel として LoadAsync を fire-and-forget で呼ぶ。

## テスト
- UIテスト追加: 起動時に商品タブが自動ロードされる(手押しなしで Products が埋まる) /
  発注タブに切り替えると発注が自動ロードされる(orderApi.ListOrdersAsync が呼ばれる)。

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: IRefreshableViewModel を導入し両VMに実装。MainWindow が起動時+タブ切替で選択タブを自動ロード。
  UIテスト2件(バインディング健全性 + 自動ロード)緑、check.ps1 緑、全体ビルド成功。#0015の在庫古い問題も解消。
- commits: ブランチ issue-0017-auto-load-on-tab
