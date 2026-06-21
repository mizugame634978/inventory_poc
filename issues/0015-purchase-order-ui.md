# #0015 発注→入荷フローの WPF UI

- status: done
- created: 2026-06-21

## 目的 / 背景
#0014 でサーバ側の発注→入荷フローと最小の PO クライアントができた。これを WPF から操作できるようにする。

## やること(着手時)
- ViewModel: 発注一覧の表示、新規発注(sku+数量)、選択発注の入荷。失敗は ErrorMessage に。
  - `IPurchaseOrderApiClient`(#0014で追加済み)を DI。
- View: 発注一覧の DataGrid + 発注フォーム + 入荷ボタン(薄く配線)。
- テスト: ViewModel ユニットテスト(発注作成→一覧再読込 / 入荷→商品在庫の再取得 / 二重入荷の
  エラー表示)。UIバインディング健全性テストに新画面を追加。
- 商品一覧と発注一覧をどう同一画面に同居させるか(タブ等)は着手時に決める。

## 完了条件(着手時)
- `dotnet test`(VM/UI)緑、`scripts/check.ps1` 緑
- 発注→入荷が画面操作で通る(実起動確認は別途)

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: `PurchaseOrderViewModel`(一覧/発注作成/入荷、失敗時は再読込しない)と、両VMを束ねる
  `MainViewModel` を追加。MainWindow を TabControl(商品/発注タブ)化し ctor を MainViewModel 受け取りに変更。
  ViewModel テスト 13件(PO分6件)、UIバインディング健全性テストは両タブを巡回して検査するよう更新し、
  発注タブの列バインディングをわざと壊して検出することも確認(teeth-check)。check.ps1 緑・全体ビルド成功。
- 同居方法: タブ。商品/発注を別タブに分離。
- 既知の割り切り: 発注入荷後に商品タブの在庫は自動更新しない(商品タブで「読み込み」が必要)。
- commits: ブランチ issue-0015-purchase-order-ui
