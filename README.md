# cosoji-rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った PDF と正解 JSON を自動生成する。

---

## 生成できる書類

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like` |
| `income_certificate` | 収入証明書風（在職証明兼） | `salary_certificate` |
| `registry_certificate` | 登記簿謄本風 | `registry_table` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary` |
| `business_plan` | 事業計画書 | `narrative` |
| `identity_document` | 本人確認書類 | `drivers_license`, `my_number_card`, `passport` |

### 各書類の特徴

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット
- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **収入証明書** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **財務サマリー** — 2期比較列・経営指標欄付き
- **事業計画書** — 3ヵ年計画表・資金調達計画・SWOT 分析欄付き
- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート（いずれも顔写真ダミー入り）

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

1 ケースあたり以下が生成される。ファイル名は `{document_type}_{variant}` 形式なので、同一書類タイプの複数 variant を同一ケースに含めても衝突しない。

```
output/
  CASE-000001/
    case_meta.json              # ケースのメタ情報
    pdf/
      rental_application_corporate_standard.pdf
      rental_application_corporate_handwritten_like.pdf
      registry_certificate_registry_table.pdf
      financial_statement_financial_summary.pdf
      business_plan_narrative.pdf
    answers/
      rental_application_corporate_standard.json   # 正解 JSON
      rental_application_corporate_handwritten_like.json
      ...
  CASE-000002/
    pdf/
      rental_application_individual_standard.pdf
      rental_application_individual_handwritten_like.pdf
      income_certificate_salary_certificate.pdf
      identity_document_drivers_license.pdf
      identity_document_my_number_card.pdf
      identity_document_passport.pdf
    answers/
      ...
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
      "pdf": "pdf/rental_application_corporate_standard.pdf",
      "answer": "answers/rental_application_corporate_standard.json"
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
templates/
  rental_application_individual/
    standard.html          個人申込書（標準）
    handwritten_like.html  個人申込書（手書き風）
  rental_application_corporate/
    standard.html          法人申込書（標準）
    handwritten_like.html  法人申込書（手書き風）
  income_certificate/
    salary_certificate.html
  registry_certificate/
    registry_table.html
  financial_statement/
    financial_summary.html
  business_plan/
    narrative.html
  identity_document/
    drivers_license.html   運転免許証風
    my_number_card.html    マイナンバーカード風
    passport.html          パスポート風
tests/          テストコード
docs/           要件定義書
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
