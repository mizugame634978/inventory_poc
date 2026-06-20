# #0003 WPF クライアント(商品の一覧・登録)+ ViewModel テスト

- status: done
- created: 2026-06-20

## 目的 / 背景
#0002 の API を WPF から使い、商品一覧の表示と登録ができる最初の「動くアプリ」にする。
同時に、WPF を自走可能にするためのテスト土台(ViewModel ユニットテスト)を確立する。

## 設計判断: テスト容易性のための 3 プロジェクト分割
- `client/InventoryClient.Core` (net10.0, **WPF非依存**): `IProductApiClient` / `ProductApiClient` /
  DTO / ViewModel。CommunityToolkit.Mvvm を使う。
- `client/InventoryClient` (net10.0-windows, WPF): View(XAML) と App のみ。Core を参照。
- `client/InventoryClient.Tests` (net10.0): Core を参照し ViewModel をテスト(xUnit + NSubstitute)。

ViewModel を WPF 非依存の Core に置くことで、テストは Windows GUI を起動せず高速・確定的に回せる。

## テスト戦略(どこまでやるか)
- ◎ ViewModel: 手厚く(状態遷移・コマンド・エラー処理・APIクライアント呼び出し)
- ○ APIクライアント↔サーバ契約: 軽く(別issueで検討可)
- ✕ View(XAML)/画面操作の UI 自動化: やらない(POCではROIが低い)。View を薄く保つことで代替。

## スコープ
- やること: 一覧表示(LoadCommand)・新規登録(RegisterCommand)・読み込み中/エラー状態
- やらないこと: 入荷/出荷UI、永続化

## テスト内容(完了条件)
`InventoryClient.Tests` を `dotnet test` で:
- LoadCommand が API 結果を Products に反映する
- API 例外時に ErrorMessage が設定され、Products は壊れない
- RegisterCommand が登録 API を呼び、その後一覧を再読込する
- 入力が不正(sku 空)なら登録 API を呼ばない

検証コマンド: `cd client && dotnet test`(全緑) かつ `cd server && uv run pytest -q`(回帰)

## 結果(完了時に追記)
- done: 2026-06-20
- 要点: 3プロジェクト分割(Core/WPF/Tests)を構築。ViewModel は `IProductApiClient` に依存し、
  NSubstitute でモック差し替え。ViewModel テスト4件(一覧反映・エラー時の堅牢性・登録後再読込・
  不正入力でAPI未呼出)が `dotnet test` で緑。WPF View は薄い層として DataGrid + 登録フォームを配線。
  ソリューション全体ビルド成功。サーバ回帰 pytest 12件も緑。
  UI自動化テストは方針どおり不採用。
- commits: ブランチ issue-0003-wpf-product-list
- 補足: 実画面での疎通(サーバ起動→WPF起動)は GUI 表示が必要なため未実施。次issue候補:
  APIクライアント↔サーバの契約テスト(実サーバ起動 or モックHTTP)。
