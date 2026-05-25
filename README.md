# cosoji-rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った PDF と正解 JSON を自動生成する。

---

## 生成できる書類

| document_type | 説明 | 初期 variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard` |
| `rental_application_corporate` | 法人用入居申込書 | `standard` |
| `income_certificate` | 収入証明書風 | `salary_certificate` |
| `registry_certificate` | 登記簿謄本風 | `registry_table` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary` |
| `business_plan` | 事業計画書 | `narrative` |

---

## セットアップ

### Docker（推奨・ローカル環境を汚さない）

```bash
docker compose build
```

### uv（ローカル実行）

```bash
uv sync --extra dev
uv run playwright install chromium
```

> `uv sync` で作られる `.venv/` はプロジェクト内に閉じ込まれる。  
> Chromium のみ `~/.cache/ms-playwright/` に置かれる（Playwright の仕様）。

---

## 使い方

### PDF 生成（全ケース）

```bash
# Docker
docker compose run --rm generator

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output
```

### PDF 生成（特定ケースのみ）

```bash
# Docker
docker compose run --rm generator --input input/cases.jsonl --output output --case-id CASE-000001

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output --case-id CASE-000001
```

### CLI オプション

| オプション | 必須 | 説明 |
|---|---|---|
| `--input` | yes | 入力 JSONL ファイルパス |
| `--output` | yes | 出力ディレクトリ |
| `--case-id` | no | 指定ケースのみ生成 |

---

## 出力構成

1 ケースあたり以下が生成される。

```
output/
  CASE-000001/
    case_meta.json              # ケースのメタ情報
    pdf/
      rental_application_corporate.pdf
      registry_certificate.pdf
      financial_statement.pdf
      business_plan.pdf
    answers/
      rental_application_corporate.json   # 正解 JSON
      registry_certificate.json
      financial_statement.json
      business_plan.json
```

#### case_meta.json の構造

```json
{
  "case_id": "CASE-000001",
  "applicant_type": "corporate",
  "generated_documents": [
    {
      "document_type": "rental_application_corporate",
      "variant": "standard",
      "pdf": "pdf/rental_application_corporate.pdf",
      "answer": "answers/rental_application_corporate.json"
    }
  ]
}
```

#### 正解 JSON の構造

```json
{
  "case_id": "CASE-000001",
  "document_type": "rental_application_corporate",
  "variant": "standard",
  "fields": {
    "company_name": "株式会社サンプル不動産テック",
    "corporate_number": "1234567890123",
    "rent": "180,000円"
  }
}
```

---

## 入力 JSONL フォーマット

1 行 = 1 ケース。

```jsonl
{"case_id":"CASE-000001","applicant_type":"corporate","company":{...},"property":{...},"financials":{...},"business_plan":{...},"documents":[...]}
{"case_id":"CASE-000002","applicant_type":"individual","applicant":{...},"employment":{...},"property":{...},"emergency_contact":{...},"income":{...},"documents":[...]}
```

`input/cases.jsonl` に法人ケース・個人ケースの例が含まれている。

---

## テンプレートの追加

```
templates/{document_type}/{variant}.html
```

を追加するだけで新しい書類タイプ・バリアントに対応できる。Jinja2 形式で `{{ case.company.company_name }}` のようにデータを参照する。

---

## 開発

### テスト

```bash
# Docker
docker compose run --rm test

# uv
uv run pytest
uv run pytest -v
```

### リント

```bash
# Docker
docker compose run --rm lint

# uv
uv run ruff check .
```

---

## ディレクトリ構成

```
input/          入力 JSONL ファイル
output/         生成済み PDF・JSON の出力先
scripts/        CLI エントリポイント
src/
  rental_pdf_generator/
    models.py           入力データモデル（Pydantic v2）
    template_loader.py  テンプレート選択・読み込み
    answer_builder.py   正解 JSON 構築
    file_writer.py      ファイル書き込みユーティリティ
    generator.py        PDF 生成オーケストレーション（Playwright）
    cli.py              CLI（argparse）
templates/      HTML テンプレート（Jinja2）
tests/          テストコード
docs/           要件定義書
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
