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

外国語版の書類は、`document_type` ディレクトリを言語別に分けず、**言語プレフィックス付きの variant 名**
（例: `us_gaap_en`, `standard_en`, `kr_standard`）で既存の document_type に追加する（Issue #76 / #79）。
入力ケースも既存の日本語ケース（`input/cases.jsonl`）とは混在させず、対象書類種が限定的な場合は
`input/cases_multilingual.jsonl` のような専用ファイルに分離する。

コード番号付き明細行・科目名の表記ゆれ・控除科目の括弧などフラットな `Financials` では表現できない
決算書 variant を追加する場合は `Case.financials_detail`（`FinancialStatementDetail`／
`FinancialStatementRow`）を使い、`src/rental_pdf_generator/answer_builder.py` の
`_DETAIL_ROW_VARIANTS` に variant 名を追記すること（追記しないと `_build_financial_statement` が
明細行ではなくフラットな `case.financials` を参照してしまう）。

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
