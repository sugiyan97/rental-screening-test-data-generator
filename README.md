# cosoji-rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った PDF と正解 JSON を自動生成する。

---

## 収録ケース一覧

`input/cases.jsonl` に以下の 18 ケースが収録されている。

| ケースID | 申込者区分 | シナリオ | 生成書類 |
|---|---|---|---|
| CASE-000001 | 法人 | **法人契約・標準** — 業歴3年以上・決算書あり・社宅利用 | 法人申込書（standard/手書き風）・登記簿謄本・決算書・事業計画書 |
| CASE-000002 | 個人（給与所得者） | **個人・保証会社利用**（保証人なし）— 会社員が保証会社審査のみで申込む最もシンプルなパターン。本人確認3種バリアント付き | 個人申込書（standard/手書き風）・収入証明書・運転免許証・マイナンバーカード・パスポート |
| CASE-000003 | 個人（給与所得者） | **個人・連帯保証人書類提出あり** — 申込者と保証人の双方が収入証明書・本人確認書類を提出するパターン（保証会社なし） | 個人申込書・収入証明書・本人確認書類（申込者）・収入証明書（保証人）・本人確認書類（保証人） |
| CASE-000004 | 個人（自営業者） | **個人・自営業者/フリーランス** — 個人事業主が確定申告書で収入証明するパターン | 個人申込書・確定申告書風・マイナンバーカード |
| CASE-000005 | 法人（新設） | **法人・新設会社（決算書なし）** — 第1期未終了のため決算書なし。事業計画書と代表者個人IDで審査を受けるスタートアップ向けパターン | 法人申込書・登記簿謄本・事業計画書・代表者運転免許証 |
| CASE-000006 | 個人（外国籍） | **個人・外国籍（就労ビザ保有者）** — 在留カード＋パスポートで本人確認。外国籍申込者向け標準書類セット | 個人申込書・収入証明書・パスポート・在留カード |
| CASE-000007 | 法人 | **法人・代表者連帯保証付き** — 中小企業オーナー（代表者）個人が連帯保証する最も一般的な法人パターン | 法人申込書・登記簿・決算書・代表者ID・代表者収入証明・連帯保証契約書 |
| CASE-000008 | 法人（子会社） | **法人・親会社グループ保証** — 子会社が賃借人、親会社が連帯保証するグループ企業契約 | 法人申込書・子会社登記簿・親会社登記簿・親会社決算書・親会社保証書 |
| CASE-000009 | 法人 | **法人・店舗用物件契約** — 飲食店経営法人による事業用物件賃貸、営業許可証付き | 法人申込書・登記簿・決算書・事業計画書・営業許可証 |
| CASE-000010 | 法人 | **法人・上場企業/大手企業** — 業歴20年以上・売上規模100億円超の大企業による社宅契約。決算書のみで審査完結 | 法人申込書・登記簿・決算書 |
| CASE-000011 | 個人（給与所得者） | **個人・連帯保証人2名（両親保証）** — 高額物件で両親（父・母）が共に連帯保証するパターン | 個人申込書・本人収入・本人ID・保証人1収入・保証人1ID・保証人2収入・保証人2ID |
| CASE-000012 | 個人（給与所得者） | **個人・保証会社＋連帯保証人併用** — 厳格審査で保証会社と連帯保証人の両方を要求するパターン | 個人申込書・本人収入・本人ID・保証人収入・保証人ID・保証会社申込書 |
| CASE-000013 | 個人（給与所得者） | **個人・転職直後** — 内定通知書と前職源泉徴収票で年収を証明する入社前住居確保パターン | 個人申込書・内定通知書・源泉徴収票・本人ID |
| CASE-000014 | 個人（給与所得者） | **個人・学生（親が契約者）** — 親が契約者、学生は同居人。親の収入証明＋学生証を提出する大学生向け賃貸 | 個人申込書・親収入証明・親ID・学生証 |
| CASE-000015 | 法人 | **法人・個人連帯保証人付き（シンプル版）** — 法人＋既存 guarantor_* テンプレートで個人連帯保証人書類を提出する標準的な中小企業パターン | 法人申込書・登記簿・決算書・保証人収入証明・保証人ID |
| CASE-000016 | 法人 | **法人・営業許可申請中** — 開業前で許可未交付、申請受付済証明書を許可書の代替として提出するパターン | 法人申込書・登記簿・決算書・事業計画書・営業許可申請書 |
| CASE-000017 | 法人 | **法人・業態変更で営業許可不要** — テイクアウト専門業態へ変更し営業許可が不要となった旨を誓約するパターン | 法人申込書・登記簿・決算書・事業計画書・業態変更誓約書 |
| CASE-000018 | 法人 | **法人・営業許可関連書類なし** — 事業計画書に「営業開始までに取得予定」と記載のみで、許可関連書類を一切提出しない最もシンプルなパターン | 法人申込書・登記簿・決算書・事業計画書 |

---

## 生成できる書類

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like` |
| `income_certificate` | 収入証明書風 | `salary_certificate`, `tax_return`, `withholding_slip` |
| `registry_certificate` | 登記簿謄本風 | `registry_table` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary` |
| `business_plan` | 事業計画書 | `narrative` |
| `identity_document` | 本人確認書類（申込者） | `drivers_license`, `my_number_card`, `passport`, `residence_card` |
| `guarantor_income_certificate` | 連帯保証人用収入証明書 | `salary_certificate` |
| `guarantor_identity_document` | 連帯保証人用本人確認書類 | `drivers_license` |
| `guarantor_2_income_certificate` | 第2連帯保証人用収入証明書 | `salary_certificate` |
| `guarantor_2_identity_document` | 第2連帯保証人用本人確認書類 | `drivers_license` |
| `corporate_guarantee_contract` | 代表者連帯保証契約書（法人賃貸借契約附属） | `standard` |
| `parent_company_guarantee_letter` | 親会社保証書（グループ保証） | `standard` |
| `parent_company_registry_certificate` | 親会社登記簿謄本風 | `registry_table` |
| `parent_company_financial_statement` | 親会社財務サマリー | `financial_summary` |
| `business_license` | 営業許可証風 | `restaurant` |
| `business_license_application` | 営業許可申請書（受付済証明）風 | `restaurant` |
| `business_use_pledge` | 業態変更誓約書（許可不要宣言） | `no_license_required` |
| `guarantee_company_application` | 家賃保証会社申込書 | `standard` |
| `offer_letter` | 内定通知書 | `standard` |
| `student_id` | 学生証カード型 | `standard` |

### 各書類の特徴

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット。`case.guarantor_2` `case.student` が設定された場合は第2保証人・同居人セクションが自動表示される
- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **収入証明書（給与所得）** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **収入証明書（確定申告）** — 事業収入・必要経費・事業所得の計算式を含む確定申告書第一表風フォーマット
- **収入証明書（源泉徴収票）** — 前職源泉徴収票風。支払金額・源泉徴収税額・社会保険料・退職日を表示
- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **財務サマリー** — 2期比較列・経営指標欄付き
- **事業計画書** — 3ヵ年計画表・資金調達計画・SWOT 分析欄付き
- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート・在留カード（いずれも顔写真ダミー入り）
- **連帯保証人書類** — 保証人用の収入証明書・本人確認書類（書類上部に「連帯保証人用」バッジを表示）。第2保証人用には別途 `guarantor_2_*` 系を使用
- **代表者連帯保証契約書** — 法人代表者個人が連帯保証する契約書フォーマット（被保証会社／連帯保証人／対象物件／保証条件／署名捺印欄）
- **親会社系書類** — グループ保証用の親会社登記簿・親会社決算書・親会社保証書セット（書類上部に「親会社用」バッジを表示）
- **営業許可証** — 飲食店営業許可証風（食品衛生法基準、保健所発行スタイル）
- **営業許可申請書（受付済証明）** — 許可書未交付状態を示す申請書のコピー。受付印・受付番号・予定交付日付き
- **業態変更誓約書** — イートイン併設業態→テイクアウト専門業態への変更宣言と「営業許可不要」の誓約。変更前後の対比表付き
- **保証会社申込書** — 家賃保証委託申込書（プラン詳細・保証料・反社確認）
- **内定通知書** — 採用会社・職位・入社予定日・予定年収を記載した転職者向け書類
- **学生証** — カード型（学籍番号・学校名・学部・有効期限）。同居人として学生がいる場合に使用

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
    withholding_slip.html    前職源泉徴収票風（転職者用）
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
  guarantor_2_income_certificate/
    salary_certificate.html  第2連帯保証人用収入証明書
  guarantor_2_identity_document/
    drivers_license.html     第2連帯保証人用運転免許証風
  corporate_guarantee_contract/
    standard.html            代表者連帯保証契約書（法人賃貸用）
  parent_company_guarantee_letter/
    standard.html            親会社保証書（グループ保証用）
  parent_company_registry_certificate/
    registry_table.html      親会社登記簿謄本
  parent_company_financial_statement/
    financial_summary.html   親会社決算書
  business_license/
    restaurant.html          飲食店営業許可証
  business_license_application/
    restaurant.html          営業許可申請書（受付済証明）
  business_use_pledge/
    no_license_required.html 業態変更誓約書（許可不要宣言）
  guarantee_company_application/
    standard.html            家賃保証会社申込書
  offer_letter/
    standard.html            内定通知書
  student_id/
    standard.html            学生証
tests/          テストコード
docs/           要件定義書
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
