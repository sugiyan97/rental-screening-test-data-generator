# cosoji-rental-screening-test-data-generator

不動産入居審査で提出される書類（入居申込書・収入証明書・登記簿謄本風書類など）を模した PDF テストデータを生成するツール。

OCR・LLM・Document AI などの抽出システムを検証するため、**架空データ**を使った PDF と正解 JSON を自動生成する。

---

## 収録ケース一覧

`input/cases.jsonl` に以下の 40 ケースが収録されている。申込時点で「既存会社」か「新規（新設）会社」かが審査内容を大きく左右するため、**法人ケースは既存／新規で表を分け**、個人ケース（自営業／給与所得者）も別表で整理した。会社名・個人名は実在しないサンプル名で、新規／既存の区別が一目で分かるよう命名している。

### A. 既存会社（法人・業歴あり） — 17 ケース

業歴があり決算書で財務を裏付けるパターン。多年度決算書・支払実績確約書・連帯保証人など、既存事業者ならではの書類組合せを検証。

| ケースID | 区分 | 会社名 | シナリオ | 提出書類 |
|---|---|---|---|---|
| CASE-000001 | 既存・法人 | 株式会社サンプル不動産テック | 業歴3年以上・社宅利用の典型的な法人審査パターン | 申込書＋登記簿＋決算書＋事業計画書＋代表者ID |
| CASE-000007 | 既存・法人 | 株式会社サンプルクラフトワークス | 中小企業オーナーが個人として連帯保証 | 申込書＋登記簿＋決算書＋代表者ID＋代表者収入＋連帯保証契約書 |
| CASE-000008 | 既存・法人（子会社） | 株式会社サンプルロジスティクスジャパン | 親会社が子会社契約を連帯保証 | 申込書＋子会社登記簿＋親会社登記簿＋親会社決算書＋親会社保証書＋代表者ID |
| CASE-000009 | 既存・法人（店舗） | 株式会社サンプルダイニングカンパニー | 飲食店経営法人。営業許可証提出パターン | 申込書＋登記簿＋決算書＋事業計画書＋営業許可証＋代表者ID |
| CASE-000010 | 既存・法人（大手） | サンプル総合商事株式会社 | 業歴20年以上・売上100億円超。決算書のみで審査完結 | 申込書＋登記簿＋決算書＋代表者ID |
| CASE-000015 | 既存・法人 | 株式会社サンプルテクニカルサービス | 代表者個人保証・シンプル版（既存 guarantor_* 流用） | 申込書＋登記簿＋決算書＋保証人収入＋保証人ID＋代表者ID |
| CASE-000016 | 既存・法人 | 株式会社サンプル和食ダイニング | 営業許可申請中（受付済証明を代替提出） | 申込書＋登記簿＋決算書＋事業計画書＋営業許可申請書＋代表者ID |
| CASE-000017 | 既存・法人 | 株式会社サンプルキッチンラボ | 業態変更で営業許可不要（誓約書） | 申込書＋登記簿＋決算書＋事業計画書＋業態変更誓約書＋代表者ID |
| CASE-000018 | 既存・法人 | 株式会社サンプル焼肉プロジェクト | 営業許可関連書類なし | 申込書＋登記簿＋決算書＋事業計画書＋代表者ID |
| CASE-000021 | 既存・法人 | 株式会社サンプルフィンテックラボ | 事務所用＋多年度決算書＋残高試算表（厳格審査） | 申込書office＋登記簿＋当期決算＋前期決算＋残高試算表＋代表者ID |
| CASE-000022 | 既存・法人 | サンプル商事株式会社 | 大手商社の役員社宅（housing variant） | 申込書housing＋登記簿＋決算書＋代表者ID |
| CASE-000029 | 既存・法人 | 株式会社サンプルロジテックパートナーズ | 業歴10年の既存事業＋新事業展開のための事業計画書付き | 申込書office＋登記簿＋当期決算＋前期決算＋事業計画書＋代表者ID |
| CASE-000033 | 既存・法人＋個人連帯保証人2名 | 株式会社サンプルメカトロニクス | CASE-000032 の既存企業版（業歴13年）。複数年度決算書＋支払実績確約書を提出。連帯保証人2名は個人証明書一式 | 申込書office＋登記簿＋当期決算＋前期決算＋支払実績確約書＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（15書類） |
| CASE-000037 | 既存・法人（設立4年目）＋個人連帯保証人2名 | 株式会社サンプルバイオセンシング | CASE-000036 をベースにした設立4年目の成長企業版。過去3期分の決算書（1ファイル）を提出 | 申込書office＋登記簿＋**複数期決算書（3期・1ファイル）**＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（13書類） |
| CASE-000038 | 既存・法人（設立4年目）＋個人連帯保証人2名 | 株式会社サンプルフィエスタアパレル | 設立4年目の D2C アパレルブランド。3期分決算書を1ファイルで提出 | 申込書office＋登記簿＋複数期決算書（3期・1ファイル）＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（13書類） |
| CASE-000039 | 既存・法人（設立4年目）＋個人連帯保証人2名 | 株式会社サンプルクラウドラボ | 設立4年目の B2B クラウド人事 SaaS。3期分決算書を1ファイルで提出 | 申込書office＋登記簿＋複数期決算書（3期・1ファイル）＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（13書類） |
| CASE-000040 | 既存・法人（業歴11年・拡大計画）＋個人連帯保証人2名 | 株式会社サンプル医療機器ホールディングス | 業歴11年の医療機器商社。当期＋前期決算書＋新事業展開のための事業計画書を提出。連帯保証人2名は個人証明書一式 | 申込書office＋登記簿＋当期決算＋前期決算＋事業計画書＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（15書類） |

### B. 新規（新設）会社（法人・申込時点で新規） — 9 ケース

申込時点で設立間もない（〜数年）会社。決算書がない／少ないため、**事業計画書・資金エビデンス・預貯金残高証明書**などで賃料支払能力を示すパターン。

| ケースID | 区分 | 会社名 | シナリオ | 提出書類 |
|---|---|---|---|---|
| CASE-000005 | 新規・法人 | 株式会社サンプルAIスタジオ | 設立1年未満・決算書なし。事業計画書＋代表者IDで審査 | 申込書＋登記簿＋事業計画書＋代表者ID |
| CASE-000025 | 新規・法人 | 株式会社サンプルクライメイトテック | 設立 6 ヶ月以内の新設スタートアップ | 申込書office＋登記簿＋事業計画書＋代表者ID |
| CASE-000026 | 新規・法人 | 株式会社サンプルバイオベンチャー | 新設法人の役員社宅契約（決算書なし、預貯金残高証明書で代替） | 申込書housing＋登記簿＋事業計画書＋残高証明書＋代表者ID |
| CASE-000027 | 新規・法人 | 株式会社サンプルエデュテック | 新設法人の事務所契約（決算書なし、預貯金残高証明書で代替） | 申込書office＋登記簿＋事業計画書＋残高証明書＋代表者ID |
| CASE-000030 | 新規・法人 | 株式会社サンプルロボティクスラボ | 資金調達済スタートアップ。資金エビデンス（自己資金＋融資＋VC出資＋補助金）と事業計画書で支払能力を裏付け | 申込書office＋登記簿＋事業計画書＋資金エビデンス＋代表者ID |
| CASE-000031 | 新規・法人＋個人連帯保証人 | 株式会社サンプルロボティクスラボ | CASE-000030 と同様の資金調達済スタートアップに代表者の配偶者が個人連帯保証人として参加。第1期決算書＋連帯保証人の個人証明書一式 | 申込書office＋登記簿＋決算書＋事業計画書＋資金エビデンス＋代表者ID＋連帯保証契約書＋保証人収入＋保証人ID＋保証人印鑑証明＋保証人住民票（11書類） |
| CASE-000032 | 新規・法人＋個人連帯保証人2名 | 株式会社サンプルネクストロボティクス | 設立6ヶ月以内の新設スタートアップ。代表者の配偶者＋実父が連帯保証人。両保証人とも個人証明書一式を提出 | 申込書office＋登記簿＋決算書＋事業計画書＋資金エビデンス＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（15書類） |
| CASE-000034 | 新規・法人（成長期） | 株式会社サンプルグロースワークス | 設立3年の新興 SaaS 企業。過去3期分の決算書を1ファイルにまとめた「複数期決算書」で売上成長を提示 | 申込書office＋登記簿＋**複数期決算書（3期・1ファイル）**＋代表者ID |
| CASE-000036 | 新規・法人＋個人連帯保証人2名 | 株式会社サンプルメドテックラボ | CASE-000033（既存企業版）の新規企業版。設立4ヶ月の新設法人が事業計画書・資金エビデンスを提出。連帯保証人2名は個人証明書一式を提出 | 申込書office＋登記簿＋事業計画書＋資金エビデンス＋代表者ID＋連帯保証契約書＋保証人1の4書類＋保証人2の4書類（14書類） |

### C. 個人事業（自営業者・フリーランス） — 6 ケース

確定申告書を収入証明として提出するパターン。開業前後・業歴別の書類組合せを検証。

| ケースID | 区分 | 個人名 | シナリオ | 提出書類 |
|---|---|---|---|---|
| CASE-000004 | 既存・個人事業 | 鈴木 誠 | 個人事業主が確定申告書（5期目）で収入証明 | 申込書＋確定申告書＋本人ID |
| CASE-000020 | 既存・個人事業 | 宮本 麻衣 | 居住SOHO兼用 variant（業歴6年） | 申込書soho＋確定申告書＋本人ID |
| CASE-000023 | 既存・個人事業 | 藤井 雅人 | 複数年度確定申告書（2 期分） | 申込書＋当期確定申告＋前期確定申告＋本人ID |
| CASE-000024 | 新規・個人事業 | 津田 海斗 | 独立開業（前職給与あり）。事業計画書付き | 申込書soho＋事業計画書＋本人ID |
| CASE-000028 | 新規・個人事業 | 島田 凛 | 業歴1期未満。確定申告書なし、開業届＋事業計画書＋残高証明書で代替 | 申込書soho＋開業届＋事業計画書＋残高証明書＋本人ID |
| CASE-000035 | 新規・個人事業（成長期） | 桐谷 さくら | 開業3年のフリーランスデザイナー。過去3年分の確定申告書を1ファイルにまとめた「複数年確定申告書」で所得の安定成長を提示 | 申込書soho＋**複数年確定申告書（3年・1ファイル）**＋本人ID |

### D. 個人（給与所得者・その他） — 8 ケース

給与所得者・外国籍・転職者・学生など、給与収入や本人確認バリアントを軸とするパターン。

| ケースID | 区分 | 個人名 | シナリオ | 提出書類 |
|---|---|---|---|---|
| CASE-000002 | 個人（給与） | 佐藤 花子 | 保証会社利用（保証人なし）。本人確認3種バリアント付き | 申込書＋収入証明＋運転免許証/マイナンバー/パスポート |
| CASE-000003 | 個人（給与） | 田中 健太 | 連帯保証人書類提出あり（保証会社なし） | 申込書＋本人収入＋本人ID＋保証人収入＋保証人ID |
| CASE-000006 | 個人（外国籍） | 李 珊珊 | 在留カード＋パスポートで本人確認 | 申込書＋収入証明＋パスポート＋在留カード |
| CASE-000011 | 個人（給与） | 中島 大輔 | 連帯保証人2名（両親）、厳格審査 | 申込書＋本人収入＋本人ID＋保証人1＋保証人2 |
| CASE-000012 | 個人（給与） | 森田 拓海 | 保証会社＋連帯保証人併用、厳格審査 | 申込書＋本人収入＋本人ID＋保証人収入＋保証人ID＋保証会社申込書 |
| CASE-000013 | 個人（給与） | 石川 翔太 | 転職直後。内定通知書＋前職源泉徴収票 | 申込書＋内定通知書＋源泉徴収票＋本人ID |
| CASE-000014 | 個人（給与） | 横山 直樹（親）／横山 大輔（学生） | 学生（親が契約者）。親の収入証明＋学生証 | 申込書＋親収入＋親ID＋学生証 |
| CASE-000019 | 個人（給与） | 西村 翔平 | 居住用 variant（世帯構成・転居理由重視） | 申込書residential＋収入証明＋本人ID |

---

## 生成できる書類

| document_type | 説明 | 利用可能な variant |
|---|---|---|
| `rental_application_individual` | 個人用入居申込書 | `standard`, `handwritten_like`, `residential`, `soho` |
| `rental_application_corporate` | 法人用入居申込書 | `standard`, `handwritten_like`, `office`, `housing`, `store` |
| `income_certificate` | 収入証明書風 | `salary_certificate`, `tax_return`, `tax_return_prior`, `tax_return_multi_year`, `withholding_slip` |
| `registry_certificate` | 履歴事項全部証明書風 | `registry_table` |
| `financial_statement` | 決算書風（財務サマリー） | `financial_summary`, `financial_summary_prior`, `multi_period` |
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
| `business_license` | 営業許可証風 | `restaurant` |
| `business_license_application` | 営業許可申請書（受付済証明）風 | `restaurant` |
| `business_use_pledge` | 業態変更誓約書（許可不要宣言） | `no_license_required` |
| `guarantee_company_application` | 家賃保証会社申込書 | `standard` |
| `offer_letter` | 内定通知書 | `standard` |
| `student_id` | 学生証カード型 | `standard` |

### 各書類の特徴

- **入居申込書**（個人・法人）— 保証人欄・同居者欄・担当者欄・反社確認文言等を含む業務品質フォーマット。`case.guarantor_2` `case.student` が設定された場合は第2保証人・同居人セクションが自動表示される
- **法人申込書の代表者情報** — 全 variant（standard/handwritten_like/office/housing/store）で代表者の氏名・フリガナ（`representative_kana`）・生年月日・年齢（`representative_age`）・性別（`representative_gender`）・住所を表示。`case.guarantor` / `case.guarantor_2` が設定された場合は法人申込書にも連帯保証人①②セクション（氏名・フリガナ・生年月日・年齢・性別・続柄・住所・勤務先・年収）が自動表示される
- **郵便番号** — 物件所在地・法人本店・代表者住所・申込者住所・緊急連絡先・連帯保証人住所に 〒XXX-XXXX 形式の仮郵便番号を表示（`postal_code` 系フィールド）。エリア（区市）に応じた実在しそうなプレフィクスを使用
- **性別・年齢** — 申込者に加え、代表者・連帯保証人①②にも性別（`gender`）・年齢（`age`）を表示
- **入居申込書 用途バリアント** — `residential`（居住用、世帯構成重視）、`soho`（居住SOHO兼用、業種・面積割合・看板）、`office`（事務所用、従業員数・営業時間・来客）、`housing`（社宅用、入居者情報・家賃補助率）、`store`（店舗用、業態・営業時間・騒音匂い・設備工事）の 5 variant。各 variant は用途固有のセクションを持つ
- **多年度書類** — 決算書の `financial_summary_prior`（前年度版）、確定申告書の `tax_return_prior`（前年度版）。`case.previous_financials` / `case.previous_income` を参照
- **複数期を1ファイルにまとめた書類** — `financial_statement/multi_period`（複数期決算書を1ファイルで横並び比較）、`income_certificate/tax_return_multi_year`（複数年の確定申告を1ファイルで横並び比較）。`case.financials_multi` / `case.income_multi`（リスト）を参照し、正解 JSON は `periods` 配列で各期を保持
- **合計残高試算表** — 月次の科目別残高表（資産・負債・純資産・損益）
- **開業届** — 個人事業の開業・廃業等届出書写し風。新規個人事業（業歴1期未満）で確定申告書の代替として提出
- **預貯金残高証明書** — 金融機関発行の残高証明書風。新規法人・新規個人事業で自己資金の証明に使用
- **資金エビデンス（資金調達証明書）** — 自己資金（資本金）・金融機関融資・VC等の出資・補助金の調達内訳を 1 枚にまとめ、月額賃料に対する支払能力を裏付ける書類。資金調達済スタートアップ向け
- **支払実績確約書** — 既存事業者が現在賃借中の物件における過去の賃料支払実績（延滞なき期間・支払方法・照会先）を示し、今後も遅滞なく支払うことを確約する書類。業歴のある法人向け（新規向けの資金エビデンスと対をなす）
- **手書き風バリアント** — Klee One フォント（Google Fonts / OFL）で記入欄をレンダリング
- **収入証明書（給与所得）** — 給与内訳（基本給・残業手当・通勤手当・賞与）・証明有効期限付き
- **収入証明書（確定申告）** — 事業収入・必要経費・事業所得の計算式を含む確定申告書第一表風フォーマット
- **収入証明書（源泉徴収票）** — 前職源泉徴収票風。支払金額・源泉徴収税額・社会保険料・退職日を表示
- **登記簿謄本風** — 法務局形式に近い原因・日付・登記事項の列構成
- **財務サマリー** — 2期比較列・経営指標欄付き
- **事業計画書** — 既存 `narrative` に加え、開業時向けの 2 variant を用意：
  - `individual_startup`：個人事業主・フリーランス開業向け。屋号・開業資金・代表者経歴・3 ヵ年売上計画・想定顧客層を含む
  - `corporate_startup`：新設法人・スタートアップ向け。創業メンバー経歴・市場分析・3 ヵ年計画・資金調達計画（VC 調達等）・SWOT 観点のリスク分析を含む
- **本人確認書類** — 運転免許証・マイナンバーカード・パスポート・在留カード（いずれも顔写真ダミー入り）
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
    residential.html       個人申込書（居住用）
    soho.html              個人申込書（居住SOHO兼用）
  rental_application_corporate/
    standard.html          法人申込書（標準）
    handwritten_like.html  法人申込書（手書き風）
    office.html            法人申込書（事務所用）
    housing.html           法人申込書（社宅用）
    store.html             法人申込書（店舗用）
  income_certificate/
    salary_certificate.html  給与所得者向け在職証明兼年収証明書
    tax_return.html          自営業者向け確定申告書第一表風
    tax_return_prior.html    前年度確定申告書（多年度書類用）
    tax_return_multi_year.html 複数年確定申告書（複数年を1ファイルに集約）
    withholding_slip.html    前職源泉徴収票風（転職者用）
  registry_certificate/
    registry_table.html
  financial_statement/
    financial_summary.html       当期決算書
    financial_summary_prior.html 前年度決算書（多年度書類用）
    multi_period.html            複数期決算書（複数期を1ファイルに集約）
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
