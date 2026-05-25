# cosoji-rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った PDF と正解 JSON を自動生成する。

---

## 収録ケース一覧

`input/cases.jsonl` に以下の 6 ケースが収録されている。

| ケースID | 申込者区分 | シナリオ | 生成書類 |
|---|---|---|---|
| CASE-000001 | 法人 | **法人契約・標準** — 業歴3年以上・決算書あり・社宅利用 | 法人申込書（standard/手書き風）・登記簿謄本・決算書・事業計画書 |
| CASE-000002 | 個人（給与所得者） | **個人・保証会社利用**（保証人なし）— 会社員が保証会社審査のみで申込む最もシンプルなパターン。本人確認3種バリアント付き | 個人申込書（standard/手書き風）・収入証明書・運転免許証・マイナンバーカード・パスポート |
| CASE-000003 | 個人（給与所得者） | **個人・連帯保証人書類提出あり** — 申込者と保証人の双方が収入証明書・本人確認書類を提出するパターン（保証会社なし） | 個人申込書・収入証明書・本人確認書類（申込者）・収入証明書（保証人）・本人確認書類（保証人） |
| CASE-000004 | 個人（自営業者） | **個人・自営業者/フリーランス** — 個人事業主が確定申告書で収入証明するパターン | 個人申込書・確定申告書風・マイナンバーカード |
| CASE-000005 | 法人（新設） | **法人・新設会社（決算書なし）** — 第1期未終了のため決算書なし。事業計画書と代表者個人IDで審査を受けるスタートアップ向けパターン | 法人申込書・登記簿謄本・事業計画書・代表者運転免許証 |
| CASE-000006 | 個人（外国籍） | **個人・外国籍（就労ビザ保有者）** — 在留カード＋パスポートで本人確認。外国籍申込者向け標準書類セット | 個人申込書・収入証明書・パスポート・在留カード |

---

## 生成できる書類

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like` |
| `income_certificate` | 収入証明書風（在職証明兼） | `salary_certificate`, `tax_return` |
| `registry_certificate` | 登記簿謄本風 | `registry_table` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary` |
| `business_plan` | 事業計画書 | `narrative` |
| `identity_document` | 本人確認書類（申込者） | `drivers_license`, `my_number_card`, `passport`, `residence_card` |
| `guarantor_income_certificate` | 連帯保証人用収入証明書 | `salary_certificate` |
| `guarantor_identity_document` | 連帯保証人用本人確認書類 | `drivers_license` |

### 各書類の特徴

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット
- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **収入証明書（給与所得）** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **収入証明書（確定申告）** — 事業収入・必要経費・事業所得の計算式を含む確定申告書第一表風フォーマット
- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **財務サマリー** — 2期比較列・経営指標欄付き
- **事業計画書** — 3ヵ年計画表・資金調達計画・SWOT 分析欄付き
- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート・在留カード（いずれも顔写真ダミー入り）
- **連帯保証人書類** — 保証人用の収入証明書・本人確認書類（書類上部に「連帯保証人用」バッジを表示）

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
{"case_id":"CASE-000001","description":"法人契約・標準 — 業歴3年以上...","applicant_type":"corporate","company":{...},"documents":[...]}
{"case_id":"CASE-000002","description":"個人・給与所得者・保証会社利用...","applicant_type":"individual","applicant":{...},"income":{...},"documents":[...]}
{"case_id":"CASE-000003","description":"個人・連帯保証人書類提出あり...","applicant_type":"individual","guarantor":{...},"guarantor_income":{...},"guarantor_identity_document":{...},"documents":[...]}
{"case_id":"CASE-000004","description":"個人・自営業者/フリーランス...","applicant_type":"sole_proprietor","income":{"income_type":"事業所得","business_income":"...","deductible_expenses":"...","taxable_income":"..."},"documents":[...]}
```

`applicant_type` は `"corporate"` / `"individual"` / `"sole_proprietor"` の3種。
`input/cases.jsonl` に6ケースの例が収録されている（上記「収録ケース一覧」参照）。

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
    salary_certificate.html  給与所得者向け在職証明兼年収証明書
    tax_return.html          自営業者向け確定申告書第一表風
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
    residence_card.html    在留カード風
  guarantor_income_certificate/
    salary_certificate.html  連帯保証人用在職証明兼年収証明書
  guarantor_identity_document/
    drivers_license.html     連帯保証人用運転免許証風
tests/          テストコード
docs/           要件定義書
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
