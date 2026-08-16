# 生成できる書類

[← README に戻る](../README.md)

本ツールが生成できる書類は 31 種類の `document_type`、合計 61 種類の variant。
テンプレートは `templates/{document_type}/{variant}.html` に 1:1 で対応しており、
JSONL の `documents[].document_type` / `variant` で指定する（→ README「入力 JSONL フォーマット」）。

## 書類タイプ一覧

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like`, `residential`, `soho`, `print_handwriting_mixed`, `joint_application` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like`, `office`, `housing`, `store`, `joint_representative`, `sole_proprietor` |
| `income_certificate` | 収入証明書風 | `salary_certificate`, `salary_certificate_prior`, `tax_return`, `tax_return_prior`, `tax_return_multi_year`, `withholding_slip`, `withholding_slip_current` |
| `registry_certificate` | 履歴事項全部証明書風 | `registry_table`, `registry_table_with_shareholders`, `registry_table_public_company_name`, `registry_table_co_representative` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary`, `financial_summary_prior`, `multi_period`, `multi_period_report_form` |
| `trial_balance` | 合計残高試算表風 | `monthly_summary`, `annual_summary` |
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

## 各書類の特徴

### A. 入居申込書（個人・法人）

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット。`case.guarantor_2` `case.student` が設定された場合は第2保証人・同居人セクションが自動表示される
- **法人申込書の代表者情報** — 全 variant（standard/handwritten_like/office/housing/store）で代表者の氏名・フリガナ（`representative_kana`）・生年月日・年齢（`representative_age`）・性別（`representative_gender`）・住所を表示。`case.guarantor` / `case.guarantor_2` が設定された場合は法人申込書にも連帯保証人①②セクション（氏名・フリガナ・生年月日・年齢・性別・続柄・住所・勤務先・年収）が自動表示される
- **法人申込書の業種欄** — `case.company.business_type`（業種）で全 variant の「業種」欄が埋まる。`standard` は従来空欄だった業種セルが、`store`/`housing`/`handwritten_like` は業種行が（値が設定されたケースのみ）表示され、`office` の「業種カテゴリ」は未設定時のみ従来の既定値にフォールバックする。`business_description`（事業内容）とは別項目
- **法人申込書の申込区分欄** — `case.property.application_category`（「新規申込者」「既存入居者」）で全 variant（`sole_proprietor` 含む）の「申込区分」欄のチェックが出し分けられる。未設定時、`sole_proprietor` は「新規申込者」にフォールバックし、他 variant は欄自体が非表示（`standard`/`handwritten_like` は両方 `□` のまま表示）になる
- **郵便番号** — 物件所在地・法人本店・代表者住所・申込者住所・緊急連絡先・連帯保証人住所に 〒XXX-XXXX 形式の仮郵便番号を表示（`postal_code` 系フィールド）。エリア（区市）に応じた実在しそうなプレフィクスを使用
- **性別・年齢** — 申込者に加え、代表者・連帯保証人①②にも性別（`gender`）・年齢（`age`）を表示
- **入居申込書 用途バリアント** — `residential`（居住用、世帯構成重視）、`soho`（居住SOHO兼用、業種・面積割合・看板）、`office`（事務所用、従業員数・営業時間・来客）、`housing`（社宅用、入居者情報・家賃補助率）、`store`（店舗用、業態・営業時間・騒音匂い・設備工事）の 5 variant。各 variant は用途固有のセクションを持つ
- **個人申込書の国籍欄** — `case.identity_document.nationality` が設定されている場合はその国籍を表示（未設定時は従来どおり「日本」）。外国籍ケースで在留カード・パスポートの国籍と申込書の記載が一致する

### B. 収入・所得の証明

- **収入証明書（給与所得）** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **収入証明書（確定申告）** — 事業収入・必要経費・事業所得の計算式を含む確定申告書第一表風フォーマット
- **収入証明書（源泉徴収票・前職）** — `withholding_slip`。転職者の前職源泉徴収票風で `case.previous_employment` を参照。支払金額・源泉徴収税額・社会保険料・退職日を表示
- **収入証明書（源泉徴収票・本人当年分）** — `withholding_slip_current`。申込者本人（給与所得者）の当年分源泉徴収票風で `case.income` を参照。支払金額・給与所得控除額・給与所得控除後の金額・社会保険料等の金額・所得控除の額の合計額・課税給与所得金額・源泉徴収税額を表示し、金額の計算式も併記するため「支払金額」の抽出検証に使える

### C. 会社の登記・財務

- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **登記簿謄本風（株主名簿付）** — `registry_certificate/registry_table_with_shareholders`。謄本本体（1 ページ目）に加え、2 ページ目に VC・ファンド等を含む「株主名簿（参考添付）」（株主名／種別／持株数／議決権比率／取得日／備考＋株主構成の要約）を綴じ込んだ variant。`case.shareholders`（リスト）を参照し、発行済株式の総数・株式の種類ごとの内訳・議決権比率合計はテンプレート側で自動集計する。正解 JSON には `shareholders` 配列と `total_shares` / `vc_shareholder_names` / `vc_shares_total` / `vc_voting_ratio_total` / `founder_voting_ratio_total` などの集計値が入り、「VC の持株比率合計」を直接検証できる（`shareholders` 未指定のケースでは従来どおり株主情報を出力しない）。**制度上、登記事項証明書に株主は記載されない**ため、株主名簿は別書類をテスト目的で同一ファイルに参考添付したものである旨をテンプレート内に明記している
- **登記簿謄本風（公表商号）** — `registry_certificate/registry_table_public_company_name`。`registry_table` と同一レイアウトで、注記のみ「商号・会社法人等番号・本店所在地は国税庁法人番号公表サイトの公表情報／代表者・財務・物件・申込者は架空」に差し替えた variant。法人番号 API の応答（閉鎖法人の検出など）を実際に発火させるために公表情報の商号を載せるケース（CASE-000061）で使う
- **財務サマリー** — 2期比較列・経営指標欄付き
- **多年度書類** — 決算書の `financial_summary_prior`（前年度版）、確定申告書の `tax_return_prior`（前年度版）。`case.previous_financials` / `case.previous_income` を参照
- **複数期を1ファイルにまとめた書類** — `financial_statement/multi_period`（複数期決算書を1ファイルで横並び比較）、`income_certificate/tax_return_multi_year`（複数年の確定申告を1ファイルで横並び比較）。`case.financials_multi` / `case.income_multi`（リスト）を参照し、正解 JSON は `periods` 配列で各期を保持
- **合計残高試算表** — 月次・年次の科目別残高表（資産・負債・純資産・損益）

### D. 資金・支払実績・事業計画

- **開業届** — 個人事業の開業・廃業等届出書写し風。新規個人事業（業歴1期未満）で確定申告書の代替として提出
- **預貯金残高証明書** — 金融機関発行の残高証明書風。新規法人・新規個人事業で自己資金の証明に使用
- **資金エビデンス（資金調達証明書）** — 自己資金（資本金）・金融機関融資・VC等の出資・補助金の調達内訳を 1 枚にまとめ、月額賃料に対する支払能力を裏付ける書類。資金調達済スタートアップ向け
- **支払実績確約書** — 既存事業者が現在賃借中の物件における過去の賃料支払実績（契約物件・支払実績期間・月額賃料・延滞履歴／延滞回数・賃料支払総額・完済状況・支払方法・照会先）を示し、今後も遅滞なく支払うことを確約する書類。業歴のある法人向け（新規向けの資金エビデンスと対をなす）。延滞回数・賃料支払総額・完済状況は値が設定されたケースのみ行が表示される
- **事業計画書** — 既存 `narrative` に加え、開業時向けの 2 variant を用意：
  - `individual_startup`：個人事業主・フリーランス開業向け。屋号・開業資金・代表者経歴・3 ヵ年売上計画・想定顧客層を含む
  - `corporate_startup`：新設法人・スタートアップ向け。創業メンバー経歴・市場分析・3 ヵ年計画・資金調達計画（VC 調達等）・SWOT 観点のリスク分析を含む

### E. 本人確認書類

- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート・在留カード（いずれも顔写真ダミー入り）。有効期限は赤字で強調表示され、在留カードは在留資格・在留期間・在留カード番号も表示する。期限接近（残1か月内）・高齢（70歳以上）などのアラート検証用ケースは [CASES.md](CASES.md) の D 表を参照
- **学生証** — カード型（学籍番号・学校名・学部・有効期限）。同居人として学生がいる場合に使用

### F. 連帯保証人・親会社関連

- **連帯保証人書類** — 保証人用の収入証明書・本人確認書類（書類上部に「連帯保証人用」バッジを表示）。第2保証人用には別途 `guarantor_2_*` 系を使用
- **連帯保証人の個人証明書** — 印鑑登録証明書（`guarantor_seal_certificate`：実印の印影プレースホルダー・登録番号・自治体長印）・住民票の写し（`guarantor_residence_certificate`：世帯主・続柄・本籍・住民となった年月日）。連帯保証人が個人の場合に実務で要求される証明書一式
- **代表者連帯保証契約書** — 法人代表者個人が連帯保証する契約書フォーマット（被保証会社／連帯保証人／対象物件／保証条件／署名捺印欄）
- **親会社系書類** — グループ保証用の親会社登記簿・親会社決算書・親会社保証書セット（書類上部に「親会社用」バッジを表示）

### G. 許認可・その他

- **営業許可証** — 飲食店営業許可証風（食品衛生法基準、保健所発行スタイル）
- **営業許可申請書（受付済証明）** — 許可書未交付状態を示す申請書のコピー。受付印・受付番号・予定交付日付き
- **業態変更誓約書** — イートイン併設業態→テイクアウト専門業態への変更宣言と「営業許可不要」の誓約。変更前後の対比表付き
- **保証会社申込書** — 家賃保証委託申込書（プラン詳細・保証料・反社確認）
- **内定通知書** — 採用会社・職位・入社予定日・予定年収を記載した転職者向け書類

### H. 様式・表現のバリアント

- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **印刷＋手書き混在バリアント**（`rental_application_individual/print_handwriting_mixed`）— 印刷された枠・ラベルはそのままで、記入値の一部を手書き風（Klee One・青インク・行ごとの微傾斜）にした様式。ページ全体に軽いスキャン風の質感（用紙の傾き・コントラスト調整）を与えている。さらに一部の記入項目を意図的に**判読困難**（`opacity` によるかすれ／`blur` によるにじみ／`rotate` を伴う擦れ）にしてあり、「読めた項目のみ登録・読めない項目は不足記載」という挙動の検証に使う。判読困難にしているのは **携帯電話番号（にじみ）／メールアドレス（インクかすれ）／年収（税込）（擦れ＋傾きで判読不能）／連帯保証人の電話番号（インクかすれ）** の4項目で、それ以外（氏名・フリガナ・生年月日・現住所・緊急連絡先・勤務先情報など）は判読可能。スキャン相当のため `output_format` は `jpg` を想定（CASE-000050 参照）

---

各書類がどのケースで使われているかは [収録ケース一覧](CASES.md) を参照。
テンプレートの追加方法は [開発者向けガイド](DEVELOPMENT.md) を参照。
