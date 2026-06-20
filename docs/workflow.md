# 開発ワークフロー(ローカル issue 駆動)

> GitLab/GitHub の issue+ブランチ運用を、リモート無しのローカル git で再現する。
> 目的: 「なぜこの変更をしたか」を後から `git blame` / `git log` で issue 単位に辿れるようにし、
> issue ファイル自体を小さなドキュメントとして残すこと。

## 手順

### 1. issue を書く
`issues/NNNN-slug.md` を作る(NNNN は4桁連番)。テンプレートは下記。
**先にテスト内容と完了条件を書く**(何が緑になれば終わりかを定義してから実装する)。

### 2. ブランチを切る
```bash
git switch -c issue-NNNN-slug
```
ブランチ名に issue 番号を必ず入れる。

### 3. 実装してテストを通す
```bash
cd server && uv run pytest -q
```
**完了条件 = 関連テストが全て緑**。緑にならないうちはマージしない。

### 4. コミット
コミットメッセージの冒頭に `#NNNN` を付ける(後で grep / blame で辿れる)。
```bash
git commit -m "#NNNN 出荷時の在庫非負チェックを実装"
```

### 5. main にマージ
issue 単位の塊を履歴に残すため `--no-ff`(fast-forward させない)。
```bash
git switch main
git merge --no-ff issue-NNNN-slug -m "Merge #NNNN: <要約>"
```

### 6. issue を締める
issue ファイルの末尾に「完了日 / 実装の要点 / 関連コミット」を追記する。

## issue テンプレート

```markdown
# #NNNN タイトル

- status: open | done
- created: YYYY-MM-DD

## 目的 / 背景
なぜこれをやるか。

## スコープ
やること / やらないこと。

## テスト内容(完了条件)
どのテストが緑になれば完了か。ファイルとテスト名で書く。

## 結果(完了時に追記)
- done: YYYY-MM-DD
- 要点:
- commits:
```

## なぜこの運用か(自走の観点)

- セッションが切り替わっても、`issues/` を読めば「何を・なぜ・どう検証して」やったかが分かる。
- `git blame` で行→コミット→`#NNNN`→issue文書、と背景まで一気に辿れる。
- 1 issue を小さく保てば、巨大なコード変更を読み解く負荷を避けられる。
