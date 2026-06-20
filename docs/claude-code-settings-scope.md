# 【人間向け】Claude Code の設定は「起動したディレクトリ」から読まれる

> これは Claude Code の挙動に関する、ハマりやすい注意書き。人間の運用者が読む前提。
> このプロジェクトの自走ハーネス(Stop hook・権限など)を効かせるために必要な知識。
> パスは環境によって変わるので、ここでは**位置関係**で説明する(フルパスは各自の環境に読み替え)。

## 結論(1行)
**Claude Code は `.claude/settings.json` を「起動したディレクトリ(作業ルート)直下」からのみ読む。
作業ルートより下の階層にある設定は読み込まれない。**

このプロジェクトのハーネス設定は `inventory_poc/.claude/settings.json` にある。
よって **`inventory_poc` を作業ルートにして `claude` を起動**しないと効かない。
その親(1つ上の階層)を作業ルートにして起動すると、`inventory_poc/.claude/settings.json` は
「作業ルートの1階層下」になるため読まれない。

## 位置関係(これが全体像)
```
<親ディレクトリ>/                 … 例: source/repos など
├─ .claude/
│  └─ settings.(local.)json       … 「親」を作業ルートに起動すると、これが読まれる
└─ inventory_poc/                 ← ★ここを作業ルートにして起動するのが正解★
   ├─ .claude/
   │  └─ settings.json            … ハーネス設定。読まれるのは inventory_poc 起動時だけ
   ├─ scripts/
   │  ├─ check.ps1                … 統一チェック(server pytest + client VMテスト)
   │  └─ stop-check.ps1           … Stop hook 本体
   ├─ server/
   ├─ client/
   └─ docs/
```
ポイント: **「作業ルート直下の `.claude/`」しか読まれない**。
上の図で `inventory_poc/.claude/` は、親を作業ルートにすると 1 階層下なので無視される。

## 効く / 効かない(作業ルート別)
| `claude` を起動した場所 | `inventory_poc/.claude/settings.json` は有効? |
|---|---|
| `inventory_poc` の親(1つ上) | ❌ 読まれない(Stop hook も権限も効かない) |
| `inventory_poc` 自身 | ✅ 読まれる(ハーネスが効く) |

## 正しい起動のしかた
PowerShell で、**`inventory_poc` に入ってから**起動する(パスは各自の環境に読み替え):
```powershell
cd <inventory_poc までのパス>\inventory_poc
claude
```
こうして起動したセッションでは:
- 出力スタイルが `default`(このプロジェクトは Learning を切っている)
- `permissions.allow` により pytest / dotnet test / git などの承認待ちが減る
- **Stop hook** が有効になり、ターン終了時に `scripts/check.ps1` が自動で走る
  (テストが赤なら停止がブロックされ、Claude が直してから終わる)

## ちゃんと効いているかの確認方法
起動後、セッション内で:
- `/hooks` を開く → Stop に `scripts/stop-check.ps1` が出ていれば有効。
- もしくは、わざとテストを1つ赤くして Claude にターンを終えさせる → 自動チェックが
  失敗を検知して継続する(=ループが効いている)。確認後は必ず元に戻す。

## なぜこうなるのか(背景)
Claude Code の設定の優先順位は **ユーザ設定(ホームの `~/.claude`) < プロジェクト設定(作業ルート直下の
`.claude`) < ローカル(同じく `.claude/settings.local.json`)**。「プロジェクト設定」は
**起動時の作業ルート直下**を見るだけで、その配下のサブフォルダにある `.claude/settings.json` までは
降りて探さない。

このプロジェクトでも実際に観測している: 以前 `inventory_poc/.claude/settings.json` に
`outputStyle: default` を置いたが、親を作業ルートに起動していたため反映されず、`/config` が
親側の `.claude/settings.local.json` に書いて初めて効いた。サブフォルダの設定は読まれていなかった。

## もし親フォルダから起動し続けたい場合(非推奨)
- 設定を親側の `.claude/settings.json` に置く手もあるが、**親配下の兄弟プロジェクト全部に影響**し、
  `scripts/...` の相対パスも合わなくなる。プロジェクト単位で完結させたいなら、素直に
  `inventory_poc` を作業ルートにして起動するのが正解。

## 関連
- ハーネスの設計: `docs/autonomy-harness.md`
- プロジェクトの方針: `CLAUDE.md`
