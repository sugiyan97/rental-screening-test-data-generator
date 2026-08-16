# rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った書類ファイルと正解 JSON を自動生成する。
出力形式は PDF に加えて **PNG / JPG / XLSX / DOCX / CSV / PPTX** に対応しており、抽出システムの対応ファイル形式の検証にも使える。

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

### 出力形式を指定して生成

書類ごとの出力形式は JSONL の `output_format` で指定する（省略時は `pdf`）。
`--output-format` を付けると、全書類の形式をまとめて上書きできる（同一ケースを画像版で作り直したいときなどに使う）。

```bash
# Docker
docker compose run --rm generator --input input/cases.jsonl --output output --output-format jpg

# uv
uv run python scripts/generate_case_pdfs.py --input input/cases.jsonl --output output --output-format jpg
```

対応形式は `pdf` / `png` / `jpg` / `xlsx` / `docx` / `csv` / `pptx` の7種。

| 出力形式 | 生成方法 | 用途 |
|---|---|---|
| `pdf` | Playwright の PDF 出力（A4） | 標準。帳票レイアウトをそのまま保持 |
| `png` | Playwright のフルページスクリーンショット | 画像入力・スキャン相当の検証 |
| `jpg` | 同上（JPEG・quality 90） | 画像入力・スキャン相当の検証（圧縮あり） |
| `xlsx` | DOM から見出し・段落・表を抽出し openpyxl で再構成 | 表計算ファイル入力の検証 |
| `docx` | 同抽出結果を python-docx で再構成 | Word ファイル入力の検証 |
| `csv` | 同抽出結果をフラットな行に展開 | テキスト/表形式入力の検証 |
| `pptx` | 同抽出結果を python-pptx でスライド化 | PowerPoint ファイル入力の検証 |

> PDF・PNG・JPG はテンプレートの見た目を保持する。XLSX / DOCX / CSV / PPTX は
> 「同じ内容を別形式で持つ」ことの検証用で、レイアウトは簡略化される（正解 JSON は形式に関わらず同一）。

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
| `--output-format` | no | 全書類の出力形式を上書き（`pdf` / `png` / `jpg` / `xlsx` / `docx` / `csv` / `pptx`） |

---

## 生成できる書類

31 種類の `document_type` × 61 種類の variant に対応している。
書類タイプ／variant の一覧と各書類の詳細な特徴は [docs/DOCUMENTS.md](docs/DOCUMENTS.md) を参照。

- **入居申込書** — 個人用／法人用（居住・SOHO・事務所・社宅・店舗など用途別 variant、手書き風・印刷手書き混在あり）
- **収入・所得** — 給与証明・確定申告書・源泉徴収票（前職／当年分）・多年度／複数年まとめ
- **会社の登記・財務** — 履歴事項全部証明書風（株主名簿付・公表商号あり）・決算書・複数期決算書・合計残高試算表
- **資金・実績・計画** — 開業届・預貯金残高証明書・資金エビデンス・支払実績確約書・事業計画書
- **本人確認** — 運転免許証・マイナンバーカード・パスポート・在留カード・学生証
- **連帯保証人／親会社** — 保証人の収入証明・本人確認・印鑑証明・住民票、代表者連帯保証契約書、親会社保証書一式
- **許認可・その他** — 営業許可証／申請書・業態変更誓約書・保証会社申込書・内定通知書

---

## 収録ケース一覧

`input/cases.jsonl` には現在 65 ケースが収録されている。既存会社／新規（新設）会社／個人事業／個人（給与所得者）／E2E異常系検証用など、区分別の一覧は [docs/CASES.md](docs/CASES.md) を参照。

---

## 出力構成

1 ケースあたり以下が生成される。ファイル名は `{document_type}_{variant}` 形式なので、同一書類タイプの複数 variant を同一ケースに含めても衝突しない。
`label` を指定した書類は `{document_type}_{variant}_{label}` になり、**同一 document_type / variant の書類を1ケースに複数含めても**衝突しない（正解 JSON のファイル名にも同じ label が付く）。
書類ファイルは**出力形式ごとのサブディレクトリ**（`pdf/` `png/` `jpg/` `xlsx/` `docx/` `csv/` `pptx/`）に出力され、正解 JSON は形式に関わらず `answers/` にまとめられる。

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
  CASE-000047/                  # 非 PDF 形式を含むケース
    case_meta.json
    pdf/
      rental_application_corporate_standard.pdf
    png/
      rental_application_corporate_standard.png
    jpg/
      rental_application_corporate_standard.jpg
    xlsx/
      registry_certificate_registry_table.xlsx
    csv/
      financial_statement_financial_summary.csv
    docx/
      business_plan_narrative.docx
    pptx/
      business_plan_narrative.pptx
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
      "output_format": "pdf",
      "file": "pdf/rental_application_corporate_standard.pdf",
      "pdf": "pdf/rental_application_corporate_standard.pdf",
      "answer": "answers/rental_application_corporate_standard.json"
    },
    {
      "document_type": "business_plan",
      "variant": "narrative",
      "output_format": "docx",
      "file": "docx/business_plan_narrative.docx",
      "answer": "answers/business_plan_narrative.json"
    },
    {
      "document_type": "rental_application_individual",
      "variant": "standard",
      "output_format": "pdf",
      "file": "pdf/rental_application_individual_standard_applicant_b.pdf",
      "label": "applicant_b",
      "pdf": "pdf/rental_application_individual_standard_applicant_b.pdf",
      "answer": "answers/rental_application_individual_standard_applicant_b.json"
    },
    {
      "document_type": "rental_application_individual",
      "variant": "standard",
      "output_format": "pdf",
      "file": "pdf/rental_application_individual_standard.pdf",
      "pdf": "pdf/rental_application_individual_standard.pdf",
      "pdf_password": "cosoji-test-2026",
      "answer": "answers/rental_application_individual_standard.json"
    }
  ]
}
```

生成ファイルのパスは `file`、形式は `output_format` で取得する。
`pdf` キーは既存の利用側との互換のため、`output_format` が `pdf` の書類にのみ `file` と同じ値で残している。
`label` / `pdf_password` は JSONL で指定した書類にのみ出力される。`pdf_password` は
「パスワード保護されていて開けない書類」の期待値として利用側が参照できるようにするためのもの。

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

`documents` の各要素は以下。

| 項目 | 必須 | 説明 |
|---|---|---|
| `document_type` | yes | 書類タイプ（`templates/{document_type}/` に対応） |
| `variant` | yes | テンプレート variant（`{variant}.html` に対応） |
| `output_format` | no | 出力形式。省略時は `pdf` |
| `label` | no | 同一 `document_type` / `variant` を1ケースに複数含めるときの識別ラベル |
| `overrides` | no | この書類にのみ適用するケースデータの部分上書き（再帰的な deep merge） |
| `pdf_password` | no | PDF にパスワード保護をかける（`output_format` が `pdf` の場合のみ） |

```jsonl
{"document_type":"business_plan","variant":"narrative","output_format":"docx"}
```

同一の `document_type` / `variant` を形式だけ変えて複数指定すれば、同じ内容を複数形式で出力できる（CASE-000047 参照）。
`input/cases.jsonl` の収録ケース一覧は [docs/CASES.md](docs/CASES.md) を参照。

#### `pdf_password` — 開けないPDFを作る（異常系）

指定すると、PDF を生成した後に **user / owner 両方のパスワード**で暗号化する（`pikepdf`・AES-256 / R=6）。
パスワードなしでは開けないため、「読み取れませんでした／要確認」と記録されるかの検証に使う。
`output_format` が `pdf` 以外の書類に指定した場合（`--output-format` での上書きを含む）は
`PdfPasswordNotSupportedError` を送出する。指定値は `case_meta.json` の該当エントリに `pdf_password` として記録される。

```jsonl
{"document_type":"rental_application_individual","variant":"standard","pdf_password":"cosoji-test-2026"}
```

#### `label` / `overrides` — 名義違いなど同一種別の書類を複数出す

`label` を付けるとファイル名・正解 JSON 名が `{document_type}_{variant}_{label}` になるため、
**同じ書類タイプ・同じ variant の書類を1ケースに複数含めても上書きされない**。
`overrides` はその書類だけに適用するケースデータの部分上書きで、`Case` を dict 化したものに対して
再帰的な deep merge を行い、再バリデーションしたうえでレンダリングと正解 JSON 生成に使う
（指定しなかった項目は元のケースデータのまま）。両者を組み合わせると、
「同一種別の申込書2通が名義違い」といった異常データを1ケースで表現できる（CASE-000049 参照）。

```jsonl
{"document_type":"rental_application_individual","variant":"standard","label":"applicant_a"}
{"document_type":"rental_application_individual","variant":"standard","label":"applicant_b","overrides":{"applicant":{"name":"田村 悠真","kana":"タムラ ユウマ"}}}
```

`overrides` は「同一ケース内で書類ごとに値を食い違わせる」用途にも使う。
CASE-000032-V2（再アップロード用 value-variant）では、ケースデータ本体を round1 と同一に保ったまま
**謄本と決算書だけ**に `overrides` を付け、申込書には旧値を残している（詳細は [docs/CASES.md](docs/CASES.md) の区分F参照）。

```jsonl
{"document_type":"registry_certificate","variant":"registry_table","overrides":{"company":{"head_office_address":"東京都千代田区神田駿河台2-9-9 サンプル駿河台ビル8階","head_office_transfer_date":"2026年07月10日"}}}
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
- CASE-000048〜000050 は E2E 異常系検証のための**意図的な異常データ**です（開けないPDF・名義違いの申込書2通・判読困難な手書き項目）。パスワード保護PDFのパスワードは固定値 `cosoji-test-2026` です。

---

## ドキュメント

| ドキュメント | 内容 |
|---|---|
| [docs/DOCUMENTS.md](docs/DOCUMENTS.md) | 生成できる書類タイプ／variant の一覧と各書類の特徴 |
| [docs/CASES.md](docs/CASES.md) | `input/cases.jsonl` の収録ケース一覧（区分別） |
| [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) | 開発者向け（ディレクトリ構成・テンプレートの追加・テスト／リント） |
| [docs/requirements.md](docs/requirements.md) | 要件定義書 |
