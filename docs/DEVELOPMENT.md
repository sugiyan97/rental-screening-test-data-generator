# 開発者向けガイド

[← README に戻る](../README.md)

## ディレクトリ構成

```
input/          入力 JSONL ファイル
output/         生成済み書類・正解 JSON の出力先
scripts/        CLI エントリポイント
src/
  rental_pdf_generator/
    models.py           入力データモデル（Pydantic v2）
    template_loader.py  テンプレート選択・読み込み
    answer_builder.py   正解 JSON 構築
    file_writer.py      ファイル書き込みユーティリティ
    generator.py        書類生成オーケストレーション（Playwright）
    renderers.py        出力形式ごとのレンダラー（pdf/png/jpg/xlsx/docx/csv/pptx）
    cli.py              CLI（argparse）
templates/      HTML テンプレート（31 の document_type ディレクトリ／61 variant）
                └ 一覧は [docs/DOCUMENTS.md](DOCUMENTS.md) を参照
tests/          テストコード
docs/
  DOCUMENTS.md    生成できる書類の一覧・特徴
  CASES.md        収録ケース一覧（区分別）
  DEVELOPMENT.md  開発者向けガイド（本ファイル）
  requirements.md 要件定義書
```

---

## テンプレートの追加

```
templates/{document_type}/{variant}.html
```

を追加するだけで新しい書類タイプ・バリアントに対応できる。Jinja2 形式で `{{ case.company.company_name }}` のようにデータを参照する。

追加したら [docs/DOCUMENTS.md](DOCUMENTS.md) の書類タイプ一覧にも 1 行（または variant を）追記すること。

---

## 出力形式の追加

`src/rental_pdf_generator/renderers.py` の `_RENDERERS` にレンダラー関数を追加し、
`models.py` の `OutputFormat` に形式名を追加する。

---

## テスト

```bash
# Docker
docker compose run --rm test

# uv
uv run pytest
uv run pytest -v
```

---

## リント

```bash
# Docker
docker compose run --rm lint

# uv
uv run ruff check .
```

---

## ドキュメントの更新ルール

- ケースを追加・変更したら [docs/CASES.md](CASES.md) を更新する
- 書類タイプ・variant を追加したら [docs/DOCUMENTS.md](DOCUMENTS.md) の一覧表と特徴を更新する
- CLI オプション・出力形式を変えたら README「使い方」と `CLAUDE.md` を更新する
