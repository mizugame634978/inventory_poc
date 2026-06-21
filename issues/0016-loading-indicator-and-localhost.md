# #0016 接続先を127.0.0.1に + ローディング表示

- status: done
- created: 2026-06-21

## 目的 / 背景
実起動で API 呼び出しに 1〜2 秒待たされる体感があった。原因の最有力は `localhost` の名前解決
(IPv6 ::1 を試してから IPv4 へフォールバックする際の待ち)。curl で 127.0.0.1 直叩きは一瞬だった。
あわせて、待ち時間が見えるようローディング表示を入れる(ViewModel の IsLoading は実装済み)。

## スコープ
- client: `MainWindow` の BaseAddress を `http://localhost:8000` → `http://127.0.0.1:8000`
- client: 両タブに IsIndeterminate な ProgressBar を置き、`IsLoading` にバインド
  (BooleanToVisibilityConverter で表示/非表示)
- やらないこと: タブ表示時の自動読み込み(#0017)、ボタンの無効化(必要なら別途)

## 完了条件
- BaseAddress が 127.0.0.1
- 処理中に ProgressBar が出る(IsLoading バインド)
- UI バインディング健全性テスト緑(新バインディング込み) / check.ps1 緑 / 全体ビルド成功
- 速度改善は実起動でユーザが体感確認(自動テスト対象外)

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: BaseAddress を 127.0.0.1 に変更(localhost の IPv6 フォールバック待ち回避が狙い)。
  Window.Resources に BooleanToVisibilityConverter、両タブに IsIndeterminate な ProgressBar を
  IsLoading にバインド。全体ビルド成功・UIテスト緑(新バインディング健全)・check.ps1 緑。
- 速度改善の体感はユーザの実起動で確認予定(自動テスト対象外)。
- commits: ブランチ issue-0016-loading-indicator-and-localhost
