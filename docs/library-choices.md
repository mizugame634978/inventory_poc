# ライブラリ/技術選定の振り返り

> ユーザが指定したのは **WPF(client) と FastAPI(server)** の2つだけ。それ以外は Claude が選定した。
> その選定理由・代替案・トレードオフを記録する。判断の軸は一貫して
> **「追加依存を最小化し、ロジックを速く・決定的にテストできる(=自走に効く)」**。(2026-06-21)

## サーバ側 (Python)
| 選定 | 役割 | 理由 | 代替案 | 正直度 |
|---|---|---|---|---|
| uv | パッケージ/環境管理 | 既存・高速・ロックで再現性。自走の検証を速くする | pip+venv / Poetry / pdm | 強い |
| pytest | テスト | 軽い記述(assert/fixture)、FastAPIと定番 | 標準unittest | 強い |
| stdlib sqlite3(ORMなし) | 永続化 | 追加依存ゼロ=故障要因が少ない。リポジトリ層を明示できる | SQLAlchemy等ORM | 中〜強(規模増でORM検討) |
| 接続をオペレーション毎に開閉 | DB接続 | スレッドプール実行でも安全 | 単一接続+ロック | 中(代償: :memory:不可) |

補足: pydantic / uvicorn / httpx は選定ではなく `fastapi[standard]` に同梱されてきたもの。

## クライアント側 (.NET / WPF)
| 選定 | 役割 | 理由 | 代替案 | 正直度 |
|---|---|---|---|---|
| CommunityToolkit.Mvvm | MVVM部品 | UIフレームワーク非依存→VMをWPF非依存に保てる(テスト容易性の要)。ソース生成で定型減 | Prism / ReactiveUI / 手書き | 強い |
| xUnit | C#テスト | .NET標準的、dotnet testと好相性 | NUnit / MSTest | 中(慣習デフォルト) |
| NSubstitute | モック | 構文が素直。MoqはSponsorLink騒動を避けた | Moq / FakeItEasy | 中〜強 |
| Xunit.StaFact([WpfFact]) | UIテストのSTA+Dispatcher | in-process でWindow生成しバインディング検証するのに必要。重いFlaUIを避ける | 手書きSTA / FlaUI | 強い |
| 3プロジェクト分割(Core/WPF/Tests) | 構成 | VMをWPF非参照のCoreに隔離→テストが速く決定的 | 単一プロジェクト | 強い |

補足: API通信は標準の System.Net.Http.Json。外部HTTPライブラリは不使用。

## あえて入れなかったもの(これも選定)
- 認証/メール/並列処理: 指示どおり除外(POCで不要)。
- ORM(SQLAlchemy): 依存を増やさず明示的に。規模拡大時は再検討。
- DIコンテナ(Microsoft.Extensions.DependencyInjection): ViewModelは手組み。この規模では過剰。
- FluentAssertions: 近年ライセンスが商用寄り。素のxUnit assertで十分。
- ログ基盤/設定管理: POC範囲外。

## 深掘り: CommunityToolkit.Mvvm を選び Prism を選ばなかった理由
両者は「層」が違う。CommunityToolkit.Mvvm は **MVVMの最小部品**、Prism は
**アプリ全体フレームワーク**(MVVM＋DIコンテナ・region ナビゲーション・モジュール・
DialogService・EventAggregator・ViewModelLocator)。

このPOCで CommunityToolkit にした理由:
1. VMをWPF非依存に保つ目的に最適(テスト容易性の要)。
   - 補足: Prism.Core(BindableBase/DelegateCommand)もUI非依存だが、Prismの価値の大半は
     アプリ層(region/navigation/module/DI)。それらを使わないなら重さだけ背負う。
2. 最小依存・最小概念(自走・速い決定的テストの軸に合う)。
3. DIコンテナ/Bootstrapperを強制されない(今回は手組みが最単純、テストも `new VM(mock)` で済む)。
4. ソース生成でボイラープレート減。
5. ライセンス: CommunityToolkitは無料・Microsoft系。近年のPrism(9系)は商用寄り。

Prism が勝る場面: 画面数が多くナビゲーションが複雑 / モジュール分割 / 決まった作法一式を
チームに敷きたい。→ 本アプリが多画面ERPに育つなら Prism 導入は合理的。
(両者は排他でなく、Prismアプリ内でCommunityToolkitのソース生成を併用することも多い。)

## 深掘り: TabControl直書き vs Prism region(画面同居/遷移)
| 観点 | 今回(TabControl直書き) | Prism region |
|---|---|---|
| 画面追加 | TabItem＋MainVMにプロパティ＋配線 | Viewをregionに登録するだけ(Shellは中身を知らない) |
| 結合度 | MainVMが子VMを直接参照(密) | View自己登録で疎結合(モジュール向き) |
| 自動読み込み | code-behindのSelectionChanged＋自作IRefreshableViewModel | OnNavigatedTo が標準提供(自前コード不要) |
| DI | newで手組み | コンテナが解決 |
| VMの外部依存 | CommunityToolkitのみ(Prism非依存) | INavigationAware等でVMがPrismに依存 |

最も効く差分は**自動読み込み**: 自前の `SelectionChanged`＋`IRefreshableViewModel` は、
Prismなら `OnNavigatedTo` 標準フックで賄え、code-behindも自作interfaceも不要(ここはPrismが上)。
ただし代償として **VMがPrism型に依存**する。今回はVMの依存ゼロ(自作の極小interface)を優先した。

判定: **2タブのPOCでは直書きが妥当**(コード/概念最小・VM依存ゼロ)。画面遷移の複雑さ・
モジュール性・画面ライフサイクル多用が出た瞬間に Prism region のレバレッジが効き始める。
今回は OnNavigatedTo 相当を約10行の自前コードで賄えてしまう規模だった。

## 深掘り: ドキュメント自動生成(API/ER)について

### API ドキュメント — 別途生成しなかった(=不要だった)
- FastAPI が **OpenAPI + Swagger UI(`/docs`)・ReDoc(`/redoc`) を内蔵生成**。サーバ起動で常に最新が
  見られ、コードと乖離しない。追加作業ゼロ。
- 加えて `docs/data-model.md` に**手書きのエンドポイント表**(人間向けトップダウン要約)。
- → 「自動(Swagger)＋人間向け要約(手書き)」で揃い、別生成の対象が無かった。

### ER 図 — 自動生成しなかった理由
1. **OpenAPIと違い、DBスキーマには内蔵生成が無い**。ER自動生成は外部に頼る必要がある。
2. **ORMなし(生sqlite3)** のため、モデルからの生成(SQLAlchemy + eralchemy 等)が使えない。
   稼働DBから生成する手もあるが外部ツール＋DB実体が要る＝重い。
3. **FK制約を宣言していない**(`PurchaseOrder.sku`→`Product.sku` は規約のみ)。よって自動生成しても
   関係線が描かれない。むしろ手書きER(`data-model.md`)の方が概念関係を表現できた。
4. 2テーブルの小規模POCで、手書きで十分だった。
- 弱点(正直に): **手書きERはスキーマと乖離し得る**(FK未宣言で強制もされない)。

### 製品化時の推奨(結論)
実際に導入する段階では:
- **SQLAlchemy(ORM)を採用**し、**FK制約を宣言**する。
- それを基に **ER図を自動生成**(例: eralchemy/sqlalchemy-schemadisplay、またはスキーマから)し、
  コードとの乖離を無くす。
- 軽量な中間案として、手書きでも **Mermaid `erDiagram`**(依存ゼロ・GitHubが描画)にしておくと
  ASCIIより保守しやすい。

## 総括(正直な自己評価)
- 強い理由で選定: uv / CommunityToolkit.Mvvm / Xunit.StaFact / stdlib sqlite / 3分割。
- 慣習デフォルト寄り(どれでも可): xUnit / NSubstitute。
- 規模が増えたら見直す: ORMなしの生SQL(定型増) / 手組みDI(配線が煩雑に)。
  製品化なら SQLAlchemy / DIコンテナ導入が妥当。
