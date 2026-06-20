# 【人間向け】Claude Code の設定は「起動したディレクトリ」から読まれる

> これは Claude Code の挙動に関する、ハマりやすい注意書き。人間の運用者が読む前提。
> このプロジェクトの自走ハーネス(Stop hook・権限など)を効かせるために必要な知識。

## 結論(1行)
**Claude Code は `.claude/settings.json` を「起動したディレクトリ(作業ルート)」から読む。
サブディレクトリにある設定は自動では読み込まれない。**

なので、このプロジェクトのハーネスを効かせたいなら **`inventory_poc` の中で `claude` を起動する**。
親フォルダ(例 `…/source/repos`)から起動すると、`inventory_poc/.claude/settings.json` は無視される。

## どこに何があるか
```
source/repos/                     ← ここで claude を起動すると…
├─ .claude/settings.local.json    … これは読まれる(repos が作業ルート)
└─ inventory_poc/
   ├─ .claude/settings.json       … ★ここのハーネス設定は「読まれない」★
   ├─ scripts/check.ps1
   └─ scripts/stop-check.ps1
```

## 効く / 効かない(起動ディレクトリ別)
| claude を起動した場所 | `inventory_poc/.claude/settings.json` は有効? |
|---|---|
| `…/source/repos`(親) | ❌ 読まれない(= Stop hook も権限も効かない) |
| `…/source/repos/inventory_poc` | ✅ 読まれる(ハーネスが効く) |

## 正しい起動のしかた
PowerShell で:
```powershell
cd C:\Users\ryout\source\repos\inventory_poc
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
Claude Code の設定の優先順位は **ユーザ設定(`~/.claude`) < プロジェクト設定(作業ルートの `.claude`)
< ローカル(`.claude/settings.local.json`)**。「プロジェクト設定」は **起動時の作業ルート**を基準に
読まれ、その配下のサブフォルダにある `.claude/settings.json` までは降りて探さない。

このプロジェクトでも実際に観測している: 以前 `inventory_poc/.claude/settings.json` に
`outputStyle: default` を置いたが、`repos` から起動していたため反映されず、`/config` が
`repos/.claude/settings.local.json` に書いて初めて効いた。サブフォルダの設定は読まれていなかった。

## もし親フォルダから起動し続けたい場合(非推奨)
- 設定を `repos/.claude/settings.json` 側に置く手もあるが、**兄弟プロジェクト全部に影響**し、
  `scripts/...` の相対パスも合わなくなる。プロジェクト単位で完結させたいなら、素直に
  `inventory_poc` から起動するのが正解。

## 関連
- ハーネスの設計: `docs/autonomy-harness.md`
- プロジェクトの方針: `CLAUDE.md`
