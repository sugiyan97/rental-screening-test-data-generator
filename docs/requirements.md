# 不動産入居審査向け PDF テストデータ生成ツール 要件定義書

## 1. 概要

### 1.1 目的

本ツールは、不動産管理業界における入居審査時の提出書類を想定した PDF テストデータを生成するためのツールである。

OCR、LLM、Document AI、帳票抽出システムなどの検証に利用するため、実在書類や実在個人情報を使わずに、仮フォーマット・架空データからテスト用 PDF を生成する。

### 1.2 背景

入居審査では、申込者の属性によって提出書類が異なる。主な例は以下である。

- **個人入居者**
  - 入居申込書
  - 収入証明書
- **法人入居者**
  - 法人用入居申込書
  - 登記簿謄本風書類
  - 決算書風書類
  - 事業計画書
- **個人事業主・小規模法人**
  - 入居申込書
  - 収入証明書風書類
  - 事業計画書
  - 決算書風書類

実際には、書類作成者・管理会社・保証会社・法人規模によってフォーマットが異なるため、複数のテンプレート variant を扱える必要がある。

### 1.3 スコープ

本ツールの対象は、PDF テストデータの生成までとする。

#### 対象に含めるもの

- HTML テンプレートから PDF を生成する
- 入力 JSON / JSONL から値を差し込む
- 1ケースから複数書類 PDF を生成する
- 書類タイプごとにテンプレートを切り替える
- 同一書類タイプ内で variant を切り替える
- PDF と同時に正解データ JSON を出力する
- ケースごとにメタ情報を出力する

#### 対象に含めないもの

- OCR 処理
- LLM 抽出処理
- 抽出結果との比較評価
- 実在する公的書類の完全再現
- 実在個人情報・実在法人情報の利用
- Web UI
- 認証・認可
- データベース保存

---

## 2. 基本方針

### 2.1 生成単位

本ツールでは、1申込者または1法人を「1ケース」として扱う。

```text
1ケース = 1申込者または1法人
1ケース = 複数の提出書類 PDF を持つ
```

#### 例

```text
CASE-000001 法人
  - 法人用入居申込書
  - 登記簿謄本風書類
  - 決算書風書類
  - 事業計画書

CASE-000002 個人
  - 個人用入居申込書
  - 収入証明書風書類
```

### 2.2 入力データ

入力データは `input/cases.jsonl` を基本とする。1行 = 1ケースとする。

```json
{"case_id":"CASE-000001","applicant_type":"corporate","documents":[{"document_type":"rental_application_corporate","variant":"standard"}]}
{"case_id":"CASE-000002","applicant_type":"individual","documents":[{"document_type":"rental_application_individual","variant":"standard"}]}
```

### 2.3 出力データ

各ケースごとに以下を出力する。

```text
output/
  CASE-000001/
    case_meta.json
    pdf/
      rental_application_corporate.pdf
      registry_certificate.pdf
      financial_statement.pdf
      business_plan.pdf
    answers/
      rental_application_corporate.json
      registry_certificate.json
      financial_statement.json
      business_plan.json
```

### 2.4 テンプレート方式

- テンプレートは HTML + CSS で作成する
- PDF 生成は Playwright を利用する

テンプレートの配置は以下とする。

```text
templates/
  {document_type}/
    {variant}.html
```

#### 例

```text
templates/
  rental_application_individual/
    standard.html
    compact.html
    handwritten_like.html

  financial_statement/
    summary.html
    profit_loss.html
    balance_sheet.html
```

---

## 3. 対象書類

### 3.1 個人用 入居申込書

- **document_type**: `rental_application_individual`
- **目的**: 個人入居者の入居申込書を模した PDF を生成する。

#### 主な項目

申込ID / 申込日 / 物件名 / 号室 / 物件所在地 / 賃料 / 管理費 / 入居希望日 / 氏名 / フリガナ / 生年月日 / 年齢 / 性別 / 現住所 / 電話番号 / メールアドレス / 本人確認書類種別 / 勤務先名 / 部署 / 役職 / 勤続年数 / 年収 / 勤務先電話番号 / 勤務先所在地 / 緊急連絡先氏名 / 続柄 / 緊急連絡先電話番号 / 緊急連絡先住所 / 保証会社利用有無 / 同意チェック / 署名

#### 初期 variant

| variant | 説明 |
|---|---|
| `standard` | 標準的な縦型帳票 |
| `compact` | 1ページに項目を詰めた帳票 |
| `handwritten_like` | 氏名、住所、署名欄を手書き風に見せる帳票 |

---

### 3.2 法人用 入居申込書

- **document_type**: `rental_application_corporate`
- **目的**: 法人契約・社宅契約・事務所利用などを想定した入居申込書 PDF を生成する。

#### 主な項目

申込ID / 申込日 / 物件名 / 号室 / 物件所在地 / 賃料 / 管理費 / 入居希望日 / 利用目的 / 会社名 / 会社名フリガナ / 法人番号 / 本店所在地 / 電話番号 / メールアドレス / 代表者名 / 代表者生年月日 / 代表者住所 / 設立年月日 / 資本金 / 従業員数 / 事業内容 / 担当者名 / 担当部署 / 担当者メール / 請求先情報 / 保証会社利用有無 / 反社会的勢力でないことの確認 / 個人情報取扱い同意 / 代表者署名 / 押印欄

#### 初期 variant

| variant | 説明 |
|---|---|
| `standard` | 法人情報と物件情報を分けた標準型 |
| `company_profile_like` | 会社概要書に近い構成 |
| `seal_required` | 押印欄を強調した構成 |

---

### 3.3 収入証明書風書類

- **document_type**: `income_certificate`
- **目的**: 個人入居者の収入確認に使う書類を想定した PDF を生成する。
- **注意**: 実在の源泉徴収票や課税証明書を完全再現するのではなく、抽出検証用の収入証明書風帳票とする。

#### 主な項目

証明書ID / 発行日 / 氏名 / 住所 / 対象年 / 勤務先名 / 勤務先住所 / 雇用形態 / 勤続年数 / 年収 / 月収 / 賞与 / 発行者名 / 発行者部署 / 発行者電話番号 / 発行者印

#### 初期 variant

| variant | 説明 |
|---|---|
| `salary_certificate` | 会社発行の年収証明書風 |
| `income_summary` | 年収・月収・賞与の要約表 |
| `payslip_summary` | 給与明細に近い要約形式 |

---

### 3.4 登記簿謄本風書類

- **document_type**: `registry_certificate`
- **目的**: 法人入居審査で提出される登記事項証明書に近い構造のテスト用 PDF を生成する。
- **注意**: 実在の登記簿謄本を完全再現しない。タイトルには「サンプル」「テスト用」「登記事項証明書風」などを含める。

#### 主な項目

会社法人等番号 / 商号 / 本店所在地 / 会社成立年月日 / 目的 / 資本金の額 / 発行可能株式総数 / 役員に関する事項 / 代表取締役 / 登記記録に関する事項 / 発行日

#### 初期 variant

| variant | 説明 |
|---|---|
| `registry_table` | 項目名と値の表形式 |
| `registry_vertical` | 縦に長い証明書風 |
| `registry_dense` | 文字量が多い形式 |

---

### 3.5 決算書風書類

- **document_type**: `financial_statement`
- **目的**: 法人入居審査で確認される財務情報を想定した PDF を生成する。詳細な会計基準の再現ではなく、抽出検証に必要な財務項目を持つ決算書風帳票とする。

#### 主な項目

会社名 / 決算期 / 会計期間 / 売上高 / 売上総利益 / 営業利益 / 経常利益 / 当期純利益 / 総資産 / 流動資産 / 固定資産 / 総負債 / 流動負債 / 固定負債 / 純資産 / 資本金 / 利益剰余金

#### 初期 variant

| variant | 説明 |
|---|---|
| `financial_summary` | 財務サマリー |
| `profit_loss` | 損益計算書風 |
| `balance_sheet` | 貸借対照表風 |
| `two_year_comparison` | 前期・当期比較形式 |

---

### 3.6 事業計画書

- **document_type**: `business_plan`
- **目的**: 創業直後法人、個人事業主、小規模法人の入居審査で提出される事業計画書を想定した PDF を生成する。

#### 主な項目

会社名 / 代表者名 / 作成日 / 計画期間 / 事業概要 / 提供サービス / ターゲット顧客 / 売上計画 / 費用計画 / 採用計画 / 資金計画 / リスク / 備考

#### 初期 variant

| variant | 説明 |
|---|---|
| `narrative` | 文章中心 |
| `table_based` | 売上計画・費用計画を表で表示 |
| `one_page_summary` | 1ページ要約 |
| `multi_page` | 複数ページ形式 |

---

## 4. 入力JSON仕様

### 4.1 共通項目

各ケースは以下の共通項目を持つ。

```json
{
  "case_id": "CASE-000001",
  "applicant_type": "corporate",
  "documents": []
}
```

| 項目 | 型 | 必須 | 説明 |
|---|---|---|---|
| `case_id` | string | yes | ケースID |
| `applicant_type` | string | yes | `individual` / `corporate` / `sole_proprietor` |
| `documents` | array | yes | 生成対象書類の一覧 |

### 4.2 documents

```json
{
  "document_type": "rental_application_corporate",
  "variant": "standard"
}
```

| 項目 | 型 | 必須 | 説明 |
|---|---|---|---|
| `document_type` | string | yes | 書類タイプ |
| `variant` | string | yes | テンプレート variant |

### 4.3 法人ケース例

```json
{
  "case_id": "CASE-000001",
  "applicant_type": "corporate",
  "company": {
    "company_name": "株式会社サンプル不動産テック",
    "company_kana": "カブシキガイシャサンプルフドウサンテック",
    "corporate_number": "1234567890123",
    "head_office_address": "東京都千代田区丸の内1-1-1",
    "representative_name": "山田 太郎",
    "representative_birth_date": "1985年04月10日",
    "representative_address": "東京都新宿区西新宿1-2-3",
    "phone": "03-1234-5678",
    "email": "contact@example.test",
    "established_date": "2018年04月01日",
    "capital": "10,000,000円",
    "business_description": "不動産管理システムの企画、開発、運営",
    "employee_count": "12名",
    "fiscal_year_end": "3月31日"
  },
  "property": {
    "property_name": "プロキシットレジデンス新宿",
    "room_number": "305",
    "property_address": "東京都新宿区西新宿1-1-1",
    "rent": "180,000円",
    "management_fee": "15,000円",
    "desired_move_in_date": "2026年06月15日",
    "usage_purpose": "社宅"
  },
  "financials": {
    "fiscal_year": "2025年度",
    "sales": "85,000,000円",
    "operating_income": "8,200,000円",
    "ordinary_income": "7,900,000円",
    "net_income": "5,100,000円",
    "total_assets": "42,000,000円",
    "total_liabilities": "18,000,000円",
    "net_assets": "24,000,000円"
  },
  "business_plan": {
    "plan_period": "2026年度",
    "business_overview": "既存の不動産管理SaaSに加え、入居審査支援機能を追加予定。",
    "revenue_plan": "月額利用料および初期導入費により売上拡大を見込む。",
    "hiring_plan": "開発担当2名、カスタマーサクセス1名を採用予定。",
    "risk_factors": "大手競合サービスとの差別化、導入初期のサポート負荷。"
  },
  "documents": [
    {"document_type": "rental_application_corporate", "variant": "standard"},
    {"document_type": "registry_certificate", "variant": "registry_table"},
    {"document_type": "financial_statement", "variant": "financial_summary"},
    {"document_type": "business_plan", "variant": "narrative"}
  ]
}
```

### 4.4 個人ケース例

```json
{
  "case_id": "CASE-000002",
  "applicant_type": "individual",
  "applicant": {
    "name": "佐藤 花子",
    "kana": "サトウ ハナコ",
    "birth_date": "1994年09月22日",
    "age": "31",
    "gender": "女性",
    "current_address": "東京都杉並区高円寺南1-1-1",
    "phone": "090-1234-5678",
    "email": "hanako.sato@example.test",
    "id_document_type": "運転免許証"
  },
  "employment": {
    "employer_name": "株式会社サンプルシステム",
    "department": "開発部",
    "job_title": "エンジニア",
    "years_employed": "4年",
    "annual_income": "5,600,000円",
    "employer_phone": "03-1111-2222",
    "employer_address": "東京都渋谷区渋谷1-1-1"
  },
  "property": {
    "property_name": "サンプルハイツ渋谷",
    "room_number": "102",
    "property_address": "東京都渋谷区道玄坂2-2-2",
    "rent": "120,000円",
    "management_fee": "10,000円",
    "desired_move_in_date": "2026年07月01日",
    "usage_purpose": "居住用"
  },
  "emergency_contact": {
    "name": "佐藤 一郎",
    "relation": "父",
    "phone": "090-2222-3333",
    "address": "埼玉県さいたま市浦和区1-2-3"
  },
  "income": {
    "income_year": "2025年",
    "annual_income": "5,600,000円",
    "monthly_income": "466,000円",
    "income_type": "給与所得",
    "issuer_name": "株式会社サンプルシステム",
    "issue_date": "2026年05月01日"
  },
  "documents": [
    {"document_type": "rental_application_individual", "variant": "standard"},
    {"document_type": "income_certificate", "variant": "salary_certificate"}
  ]
}
```

---

## 5. 機能要件

### 5.1 PDF生成

- HTMLテンプレートに入力JSONの値を差し込めること
- PlaywrightでPDFを生成できること
- A4サイズを基本とすること
- 日本語フォントで文字化けしないこと
- 1ケースから複数PDFを生成できること
- PDFファイル名は `document_type` を基本とすること

### 5.2 正解JSON生成

- PDFごとに正解JSONを生成すること
- 正解JSONには、そのPDFに表示した値を含めること
- 正解JSONは `answers/{document_type}.json` に出力すること

### 5.3 case_meta.json生成

各ケースに `case_meta.json` を生成すること。

#### 例

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

### 5.4 テンプレート選択

- `document_type` と `variant` からテンプレートHTMLを選択できること
- 存在しないテンプレートが指定された場合はエラーにすること
- エラー時は、対象の `case_id`、`document_type`、`variant` を表示すること

### 5.5 CLI

以下のCLIを用意する。

```bash
python scripts/generate_case_pdfs.py \
  --input input/cases.jsonl \
  --output output
```

任意で以下を指定できること。

```bash
python scripts/generate_case_pdfs.py \
  --input input/cases.jsonl \
  --output output \
  --case-id CASE-000001
```

#### オプション

| オプション | 必須 | 説明 |
|---|---|---|
| `--input` | yes | 入力 JSONL パス |
| `--output` | yes | 出力ディレクトリ |
| `--case-id` | no | 指定ケースのみ生成 |

---

## 6. 非機能要件

### 6.1 実行環境

- Python 3.12 以上
- Playwright
- Jinja2
- pytest
- ruff
- mypy は任意

### 6.2 文字コード

- 入力JSONLは UTF-8 とする
- 出力JSONは UTF-8 とする
- JSON出力では `ensure_ascii=False` とする

### 6.3 個人情報・安全性

- 実在個人情報を使わない
- 実在法人の情報を使わない
- メールアドレスは `example.test` を利用する
- 電話番号はテスト用の値を使う
- 登記簿謄本風書類には「サンプル」「テスト用」などの文言を入れる
- 公的書類を本物と誤認させる表現は避ける

### 6.4 拡張性

- 書類タイプ追加時は `templates/{document_type}/{variant}.html` を追加すればよい構造にする
- 入力JSONのルート構造を大きく変えずに新書類を追加できること
- `document_type` ごとのデータ抽出処理は関数またはクラスで分離すること

---

## 7. 推奨ディレクトリ構成

```text
rental-screening-test-data-generator/
  README.md
  pyproject.toml
  AGENTS.md
  CLAUDE.md

  docs/
    requirements.md
    implementation_guide_for_ai.md

  input/
    cases.jsonl

  output/
    .gitkeep

  scripts/
    generate_case_pdfs.py

  src/
    rental_pdf_generator/
      __init__.py
      cli.py
      generator.py
      models.py
      template_loader.py
      answer_builder.py
      file_writer.py

  templates/
    rental_application_individual/
      standard.html
      compact.html
      handwritten_like.html

    rental_application_corporate/
      standard.html
      company_profile_like.html
      seal_required.html

    income_certificate/
      salary_certificate.html
      income_summary.html
      payslip_summary.html

    registry_certificate/
      registry_table.html
      registry_vertical.html
      registry_dense.html

    financial_statement/
      financial_summary.html
      profit_loss.html
      balance_sheet.html
      two_year_comparison.html

    business_plan/
      narrative.html
      table_based.html
      one_page_summary.html
      multi_page.html

  tests/
    test_generate_case_pdfs.py
    test_template_loader.py
    test_answer_builder.py
```

---

## 8. 初期実装対象

初期実装では、以下の最小セットを作成する。

### 8.1 対象テンプレート

#### 法人ケース

- `rental_application_corporate/standard.html`
- `registry_certificate/registry_table.html`
- `financial_statement/financial_summary.html`
- `business_plan/narrative.html`

#### 個人ケース

- `rental_application_individual/standard.html`
- `income_certificate/salary_certificate.html`

### 8.2 初期入力データ

`input/cases.jsonl` に以下を用意する。

- 法人ケース 1件
- 個人ケース 1件

### 8.3 初期出力

合計6PDFを生成する。

```text
CASE-000001 法人
  - rental_application_corporate.pdf
  - registry_certificate.pdf
  - financial_statement.pdf
  - business_plan.pdf

CASE-000002 個人
  - rental_application_individual.pdf
  - income_certificate.pdf
```

---

## 9. 受け入れ条件

以下を満たすこと。

- [ ] `python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output` で実行できる
- [ ] `output/CASE-000001/pdf/` に4つのPDFが生成される
- [ ] `output/CASE-000002/pdf/` に2つのPDFが生成される
- [ ] 各PDFに対応する `answers/*.json` が生成される
- [ ] 各ケースに `case_meta.json` が生成される
- [ ] PDF内で日本語が文字化けしない
- [ ] 存在しない `document_type` / `variant` を指定した場合にわかりやすいエラーが出る
- [ ] `pytest` が成功する
- [ ] `ruff check .` が成功する

---

## 10. 将来拡張

将来的に以下を追加できる構造とする。

- スキャン風PDF生成
- 傾き・ノイズ・かすれ加工
- 手書き風フォントの切り替え
- 同一ケースで複数variantを生成
- 個人事業主ケース
- 赤字法人ケース
- 創業直後法人ケース
- 複数年度の決算書
- 複数ページ事業計画書
- 添付書類一覧表
