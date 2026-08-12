# rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った書類ファイルと正解 JSON を自動生成する。
出力形式は PDF に加えて **PNG / JPG / XLSX / DOCX / CSV / PPTX** に対応しており、抽出システムの対応ファイル形式の検証にも使える。

---

## 収録ケース一覧

`input/cases.jsonl` には現在 65 ケースが収録されている。既存会社／新規（新設）会社／個人事業／個人（給与所得者）／E2E異常系検証用など、区分別の一覧は [docs/CASES.md](docs/CASES.md) を参照。

---

## 生成できる書類

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like`, `residential`, `soho`, `print_handwriting_mixed`, `joint_application` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like`, `office`, `housing`, `store`, `joint_representative`, `sole_proprietor` |
| `income_certificate` | 収入証明書風 | `salary_certificate`, `tax_return`, `tax_return_prior`, `tax_return_multi_year`, `withholding_slip`, `withholding_slip_current` |
| `registry_certificate` | 履歴事項全部証明書風 | `registry_table`, `registry_table_with_shareholders`, `registry_table_public_company_name` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary`, `financial_summary_prior`, `multi_period`, `multi_period_report_form` |
| `trial_balance` | 合計残高試算表風（月次） | `monthly_summary` |
| `business_opening_notice` | 個人事業の開業・廃業等届出書（開業届）写し風 | `individual` |
| `bank_balance_certificate` | 預貯金残高証明書風（金融機関発行） | `standard` |
| `funding_evidence` | 資金エビデンス（資金調達証明書） | `standard` |
| `payment_track_record_pledge` | 支払実績確約書（既存事業者の賃料支払実績） | `standard` |
| `business_plan` | 事業計画書 | `narrative`, `individual_startup`, `corporate_startup` |
| `identity_document` | 本人確認書類（申込者） | `drivers_license`, `my_number_card`, `passport`, `residence_card` |
| `guarantor_income_certificate` | 連帯保証人用収入証明書 | `salary_certificate` |
| `guarantor_identity_document` | 連帯保証人用本人確認書類 | `drivers_license` |
| `guarantor_2_income_certificate` | 第2連帯保証人用収入証明書 | `salary_certificate` |
| `guarantor_2_identity_document` | 第2連帯保証人用本人確認書類 | `drivers_license` |
| `guarantor_seal_certificate` | 連帯保証人用 印鑑登録証明書 | `standard` |
| `guarantor_residence_certificate` | 連帯保証人用 住民票の写し | `standard` |
| `guarantor_2_seal_certificate` | 第2連帯保証人用 印鑑登録証明書 | `standard` |
| `guarantor_2_residence_certificate` | 第2連帯保証人用 住民票の写し | `standard` |
| `corporate_guarantee_contract` | 代表者連帯保証契約書（法人賃貸借契約附属） | `standard` |
| `parent_company_guarantee_letter` | 親会社保証書（グループ保証） | `standard` |
| `parent_company_registry_certificate` | 親会社登記簿謄本風 | `registry_table` |
| `parent_company_financial_statement` | 親会社財務サマリー | `financial_summary` |
| `parent_company_identity_document` | 親会社（法人保証人）代表者の本人確認書類 | `residence_card` |
| `business_license` | 営業許可証風 | `restaurant`, `entertainment_business` |
| `business_license_application` | 営業許可申請書（受付済証明）風 | `restaurant` |
| `business_use_pledge` | 業態変更誓約書（許可不要宣言） | `no_license_required` |
| `guarantee_company_application` | 家賃保証会社申込書 | `standard` |
| `offer_letter` | 内定通知書 | `standard` |
| `student_id` | 学生証カード型 | `standard` |

### 各書類の特徴

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット。`case.guarantor_2` `case.student` が設定された場合は第2保証人・同居人セクションが自動表示される
- **法人申込書の代表者情報** — 全 variant（standard/handwritten_like/office/housing/store）で代表者の氏名・フリガナ（`representative_kana`）・生年月日・年齢（`representative_age`）・性別（`representative_gender`）・住所を表示。`case.guarantor` / `case.guarantor_2` が設定された場合は法人申込書にも連帯保証人①②セクション（氏名・フリガナ・生年月日・年齢・性別・続柄・住所・勤務先・年収）が自動表示される
- **法人申込書の業種欄** — `case.company.business_type`（業種）で全 variant の「業種」欄が埋まる。`standard` は従来空欄だった業種セルが、`store`/`housing`/`handwritten_like` は業種行が（値が設定されたケースのみ）表示され、`office` の「業種カテゴリ」は未設定時のみ従来の既定値にフォールバックする。`business_description`（事業内容）とは別項目
- **法人申込書の申込区分欄** — `case.property.application_category`（「新規申込者」「既存入居者」）で全 variant（`sole_proprietor` 含む）の「申込区分」欄のチェックが出し分けられる。未設定時、`sole_proprietor` は「新規申込者」にフォールバックし、他 variant は欄自体が非表示（`standard`/`handwritten_like` は両方 `□` のまま表示）になる
- **郵便番号** — 物件所在地・法人本店・代表者住所・申込者住所・緊急連絡先・連帯保証人住所に 〒XXX-XXXX 形式の仮郵便番号を表示（`postal_code` 系フィールド）。エリア（区市）に応じた実在しそうなプレフィクスを使用
- **性別・年齢** — 申込者に加え、代表者・連帯保証人①②にも性別（`gender`）・年齢（`age`）を表示
- **入居申込書 用途バリアント** — `residential`（居住用、世帯構成重視）、`soho`（居住SOHO兼用、業種・面積割合・看板）、`office`（事務所用、従業員数・営業時間・来客）、`housing`（社宅用、入居者情報・家賃補助率）、`store`（店舗用、業態・営業時間・騒音匂い・設備工事）の 5 variant。各 variant は用途固有のセクションを持つ
- **多年度書類** — 決算書の `financial_summary_prior`（前年度版）、確定申告書の `tax_return_prior`（前年度版）。`case.previous_financials` / `case.previous_income` を参照
- **複数期を1ファイルにまとめた書類** — `financial_statement/multi_period`（複数期決算書を1ファイルで横並び比較）、`income_certificate/tax_return_multi_year`（複数年の確定申告を1ファイルで横並び比較）。`case.financials_multi` / `case.income_multi`（リスト）を参照し、正解 JSON は `periods` 配列で各期を保持
- **合計残高試算表** — 月次の科目別残高表（資産・負債・純資産・損益）
- **開業届** — 個人事業の開業・廃業等届出書写し風。新規個人事業（業歴1期未満）で確定申告書の代替として提出
- **預貯金残高証明書** — 金融機関発行の残高証明書風。新規法人・新規個人事業で自己資金の証明に使用
- **資金エビデンス（資金調達証明書）** — 自己資金（資本金）・金融機関融資・VC等の出資・補助金の調達内訳を 1 枚にまとめ、月額賃料に対する支払能力を裏付ける書類。資金調達済スタートアップ向け
- **支払実績確約書** — 既存事業者が現在賃借中の物件における過去の賃料支払実績（契約物件・支払実績期間・月額賃料・延滞履歴／延滞回数・賃料支払総額・完済状況・支払方法・照会先）を示し、今後も遅滞なく支払うことを確約する書類。業歴のある法人向け（新規向けの資金エビデンスと対をなす）。延滞回数・賃料支払総額・完済状況は値が設定されたケースのみ行が表示される
- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **印刷＋手書き混在バリアント**（`rental_application_individual/print_handwriting_mixed`）— 印刷された枠・ラベルはそのままで、記入値の一部を手書き風（Klee One・青インク・行ごとの微傾斜）にした様式。ページ全体に軽いスキャン風の質感（用紙の傾き・コントラスト調整）を与えている。さらに一部の記入項目を意図的に**判読困難**（`opacity` によるかすれ／`blur` によるにじみ／`rotate` を伴う擦れ）にしてあり、「読めた項目のみ登録・読めない項目は不足記載」という挙動の検証に使う。判読困難にしているのは **携帯電話番号（にじみ）／メールアドレス（インクかすれ）／年収（税込）（擦れ＋傾きで判読不能）／連帯保証人の電話番号（インクかすれ）** の4項目で、それ以外（氏名・フリガナ・生年月日・現住所・緊急連絡先・勤務先情報など）は判読可能。スキャン相当のため `output_format` は `jpg` を想定（CASE-000050 参照）
- **収入証明書（給与所得）** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **収入証明書（確定申告）** — 事業収入・必要経費・事業所得の計算式を含む確定申告書第一表風フォーマット
- **収入証明書（源泉徴収票・前職）** — `withholding_slip`。転職者の前職源泉徴収票風で `case.previous_employment` を参照。支払金額・源泉徴収税額・社会保険料・退職日を表示
- **収入証明書（源泉徴収票・本人当年分）** — `withholding_slip_current`。申込者本人（給与所得者）の当年分源泉徴収票風で `case.income` を参照。支払金額・給与所得控除額・給与所得控除後の金額・社会保険料等の金額・所得控除の額の合計額・課税給与所得金額・源泉徴収税額を表示し、金額の計算式も併記するため「支払金額」の抽出検証に使える
- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **登記簿謄本風（株主名簿付）** — `registry_certificate/registry_table_with_shareholders`。謄本本体（1 ページ目）に加え、2 ページ目に VC・ファンド等を含む「株主名簿（参考添付）」（株主名／種別／持株数／議決権比率／取得日／備考＋株主構成の要約）を綴じ込んだ variant。`case.shareholders`（リスト）を参照し、発行済株式の総数・株式の種類ごとの内訳・議決権比率合計はテンプレート側で自動集計する。正解 JSON には `shareholders` 配列と `total_shares` / `vc_shareholder_names` / `vc_shares_total` / `vc_voting_ratio_total` / `founder_voting_ratio_total` などの集計値が入り、「VC の持株比率合計」を直接検証できる（`shareholders` 未指定のケースでは従来どおり株主情報を出力しない）。**制度上、登記事項証明書に株主は記載されない**ため、株主名簿は別書類をテスト目的で同一ファイルに参考添付したものである旨をテンプレート内に明記している
- **登記簿謄本風（公表商号）** — `registry_certificate/registry_table_public_company_name`。`registry_table` と同一レイアウトで、注記のみ「商号・会社法人等番号・本店所在地は国税庁法人番号公表サイトの公表情報／代表者・財務・物件・申込者は架空」に差し替えた variant。法人番号 API の応答（閉鎖法人の検出など）を実際に発火させるために公表情報の商号を載せるケース（CASE-000061）で使う
- **財務サマリー** — 2期比較列・経営指標欄付き
- **事業計画書** — 既存 `narrative` に加え、開業時向けの 2 variant を用意：
  - `individual_startup`：個人事業主・フリーランス開業向け。屋号・開業資金・代表者経歴・3 ヵ年売上計画・想定顧客層を含む
  - `corporate_startup`：新設法人・スタートアップ向け。創業メンバー経歴・市場分析・3 ヵ年計画・資金調達計画（VC 調達等）・SWOT 観点のリスク分析を含む
- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート・在留カード（いずれも顔写真ダミー入り）。有効期限は赤字で強調表示され、在留カードは在留資格・在留期間・在留カード番号も表示する。期限接近（残1か月内）・高齢（70歳以上）などのアラート検証用ケースは [docs/CASES.md](docs/CASES.md) の D 表を参照
- **個人申込書の国籍欄** — `case.identity_document.nationality` が設定されている場合はその国籍を表示（未設定時は従来どおり「日本」）。外国籍ケースで在留カード・パスポートの国籍と申込書の記載が一致する
- **連帯保証人書類** — 保証人用の収入証明書・本人確認書類（書類上部に「連帯保証人用」バッジを表示）。第2保証人用には別途 `guarantor_2_*` 系を使用
- **連帯保証人の個人証明書** — 印鑑登録証明書（`guarantor_seal_certificate`：実印の印影プレースホルダー・登録番号・自治体長印）・住民票の写し（`guarantor_residence_certificate`：世帯主・続柄・本籍・住民となった年月日）。連帯保証人が個人の場合に実務で要求される証明書一式
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
    generator.py        書類生成オーケストレーション（Playwright）
    renderers.py        出力形式ごとのレンダラー（pdf/png/jpg/xlsx/docx/csv/pptx）
    cli.py              CLI（argparse）
templates/
  rental_application_individual/
    standard.html          個人申込書（標準）
    handwritten_like.html  個人申込書（手書き風）
    residential.html       個人申込書（居住用）
    soho.html              個人申込書（居住SOHO兼用）
    print_handwriting_mixed.html 個人申込書（印刷＋手書き混在・一部判読困難）
    joint_application.html 個人申込書（共同申込・申込者2名）
  rental_application_corporate/
    standard.html          法人申込書（標準）
    handwritten_like.html  法人申込書（手書き風）
    office.html            法人申込書（事務所用）
    housing.html           法人申込書（社宅用）
    store.html             法人申込書（店舗用）
    joint_representative.html 法人申込書（共同代表・代表者2名）
  income_certificate/
    salary_certificate.html  給与所得者向け在職証明兼年収証明書
    tax_return.html          自営業者向け確定申告書第一表風
    tax_return_prior.html    前年度確定申告書（多年度書類用）
    tax_return_multi_year.html 複数年確定申告書（複数年を1ファイルに集約）
    withholding_slip.html    前職源泉徴収票風（転職者用）
    withholding_slip_current.html 申込者本人の当年分源泉徴収票風（給与所得者用）
  registry_certificate/
    registry_table.html                  登記簿謄本（履歴事項全部証明書風）
    registry_table_with_shareholders.html 登記簿謄本＋株主名簿（参考添付・VC株主対応）
  financial_statement/
    financial_summary.html       当期決算書
    financial_summary_prior.html 前年度決算書（多年度書類用）
    multi_period.html            複数期決算書（複数期を1ファイルに集約）
    multi_period_report_form.html 複数期決算書・報告式BS（貸借対照表を資産→負債→純資産の縦並びで表示）
  trial_balance/
    monthly_summary.html         月次合計残高試算表
  business_opening_notice/
    individual.html              個人事業の開業届写し
  bank_balance_certificate/
    standard.html                預貯金残高証明書
  funding_evidence/
    standard.html                資金エビデンス（資金調達証明書）
  payment_track_record_pledge/
    standard.html                支払実績確約書（既存事業者向け）
  business_plan/
    narrative.html               事業計画書（一般・既存事業向け）
    individual_startup.html      事業計画書（個人事業主の開業向け）
    corporate_startup.html       事業計画書（新設法人・スタートアップ向け）
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
  guarantor_seal_certificate/
    standard.html            連帯保証人用 印鑑登録証明書
  guarantor_residence_certificate/
    standard.html            連帯保証人用 住民票の写し
  guarantor_2_seal_certificate/
    standard.html            第2連帯保証人用 印鑑登録証明書
  guarantor_2_residence_certificate/
    standard.html            第2連帯保証人用 住民票の写し
  corporate_guarantee_contract/
    standard.html            代表者連帯保証契約書（法人賃貸用）
  parent_company_guarantee_letter/
    standard.html            親会社保証書（グループ保証用）
  parent_company_registry_certificate/
    registry_table.html      親会社登記簿謄本
  parent_company_financial_statement/
    financial_summary.html   親会社決算書
  parent_company_identity_document/
    residence_card.html      親会社（法人保証人）代表者の在留カード風（外国籍代表）
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
docs/
  requirements.md 要件定義書
  CASES.md        収録ケース一覧（区分別）
```

---

## 注意事項

- 本ツールが生成する書類はすべて架空のテスト用サンプルです。実在する個人・法人の情報は使用していません。
- メールアドレスは `example.test` ドメインを使用しています。
- 登記簿謄本風書類には「テスト用サンプル」の旨を明記しており、公的書類として使用することはできません。
- CASE-000048〜000050 は E2E 異常系検証のための**意図的な異常データ**です（開けないPDF・名義違いの申込書2通・判読困難な手書き項目）。パスワード保護PDFのパスワードは固定値 `cosoji-test-2026` です。
