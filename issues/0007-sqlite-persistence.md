# #0007 永続化を SQLite に(リポジトリ差し替えが domain 非依存で済む実証)

- status: done
- created: 2026-06-21

## 目的 / 背景
保管をメモリから SQLite に差し替える。狙いは機能追加そのものより、
**「リポジトリ実装を替えても domain 層は一切変えずに済む」というレイヤ分離の実証**。

## スコープ
- repository に抽象 `ProductRepository`(ABC)を導入し、`add/get/list_all/update` を定義
- `InMemoryProductRepository` を抽象の実装にし、`update` を追加
- `SqliteProductRepository`(stdlib `sqlite3`、追加依存なし)を実装
- `main.py` の依存型を具象から抽象 `ProductRepository` に変更し、既定を SQLite に
  - 在庫変更(receive/ship)後は `repo.update(product)` で永続化(メモリ参照に依存しない正しい形)
- やらないこと: マイグレーション基盤、入出庫履歴

## 制約・設計メモ
- 接続はオペレーション毎に開閉(FastAPI のスレッドプール実行でも安全)。
  → `:memory:` は接続毎に別DBになるため、テストは一時ファイルを使う。
- domain.py は**1行も変更しない**(完了時に `git diff` で確認)。

## テスト内容(完了条件)
- 既存 `tests/test_api.py`(InMemory 差し替え)が緑のまま(InMemory.update 追加後も回帰なし)
- 新規 `tests/test_repository.py`:
  - SqliteProductRepository: add→get 往復 / list_all / update が永続化される / 不明SKUで ProductNotFoundError
  - API を SQLite 実装に差し替えても登録→入荷→出荷が通る(差し替え可能性の証明)
- `git diff` で `app/domain.py` に変更が無いこと

検証コマンド: `cd server && uv run pytest -q`

## 結果(完了時に追記)
- done: 2026-06-21
- 要点: 抽象 `ProductRepository`(ABC, add/get/list_all/update)を導入。InMemory と SQLite の2実装。
  main.py は抽象に依存(既定SQLite, 遅延初期化)。在庫変更後は `repo.update` で永続化。
  接続はオペレーション毎に開閉。
- **実証**: `git diff main -- server/app/domain.py` が空 = domain.py 無変更で永続化を差し替えられた。
  変更は main.py(配線) と repository.py のみ。
- テスト: server 22件緑(test_repository.py で SQLite の永続化を別インスタンス読み直しで確認、
  かつ API を SQLite 実装に差し替えても登録→入荷→出荷→在庫不足が通ることを確認)。
- commits: ブランチ issue-0007-sqlite-persistence
