# rental-screening-test-data-generator

不動産入居審査向けPDFテストデータ生成ツール。

## セットアップ

### Docker（推奨）

```bash
docker compose build
```

### uv（ローカル）

```bash
uv sync
uv run playwright install chromium
```

> **注意**: `uv sync` で作られる `.venv/` はプロジェクト内に閉じ込まれる。
> Chromiumのみ `~/.cache/ms-playwright/` に置かれる（Playwright の仕様）。

## 実行コマンド

### PDF生成

```bash
# Docker
docker compose run --rm generator

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output
```

### 出力形式の指定

書類ごとの形式は JSONL の `documents[].output_format`（省略時 `pdf`）で指定する。
対応形式は `pdf` / `png` / `jpg` / `xlsx` / `docx` / `csv` / `pptx`。
`--output-format` で全書類の形式をまとめて上書きできる。

```bash
# Docker
docker compose run --rm generator --input input/cases.jsonl --output output --output-format jpg

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output --output-format jpg
```

出力先は形式ごとのサブディレクトリ（`output/{case_id}/{形式}/{document_type}_{variant}.{拡張子}`）。
正解 JSON は形式に関わらず `answers/` に出力される。

### 特定ケースのみ生成

```bash
# Docker（フルコマンドを指定）
docker compose run --rm generator --input input/cases.jsonl --output output --case-id CASE-000001

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output --case-id CASE-000001
```

### テスト

```bash
# Docker
docker compose run --rm test

# uv
uv run pytest
uv run pytest -v  # 詳細表示
```

### リント

```bash
# Docker
docker compose run --rm lint

# uv
uv run ruff check .
```

## ディレクトリ構成

```
input/          入力JSONLファイル
output/         生成済みPDF・JSONの出力先
scripts/        CLIエントリポイント
src/            Pythonソースコード
templates/      HTMLテンプレート
tests/          テストコード
```

## テンプレートの追加

```
templates/{document_type}/{variant}.html
```

を追加するだけで新しい書類タイプ・バリアントに対応できる。

## 出力形式の追加

`src/rental_pdf_generator/renderers.py` の `_RENDERERS` にレンダラー関数を追加し、
`models.py` の `OutputFormat` に形式名を追加する。
