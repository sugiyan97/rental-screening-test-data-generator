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
