import pytest

from rental_pdf_generator.template_loader import TemplateLoader, TemplateNotFoundError


def test_load_valid_template_corporate():
    loader = TemplateLoader()
    template = loader.load(
        case_id="CASE-TEST",
        document_type="rental_application_corporate",
        variant="standard",
    )
    assert template is not None


def test_load_valid_template_individual():
    loader = TemplateLoader()
    template = loader.load(
        case_id="CASE-TEST",
        document_type="rental_application_individual",
        variant="standard",
    )
    assert template is not None


def test_load_all_initial_templates():
    loader = TemplateLoader()
    templates = [
        ("rental_application_corporate", "standard"),
        ("registry_certificate", "registry_table"),
        ("financial_statement", "financial_summary"),
        ("business_plan", "narrative"),
        ("rental_application_individual", "standard"),
        ("income_certificate", "salary_certificate"),
        ("income_certificate", "withholding_slip"),
        ("income_certificate", "withholding_slip_current"),
        ("payment_track_record_pledge", "standard"),
        ("business_license", "entertainment_business"),
        ("registry_certificate", "registry_table_with_shareholders"),
        # Issue #76: 多言語（英語）決算書・資金エビデンス対応
        ("financial_statement", "us_gaap_en"),
        ("financial_statement", "singapore_hk_en"),
        ("financial_statement", "ifrs_consolidated_en"),
        ("bank_balance_certificate", "standard_en"),
        ("bank_balance_certificate", "standard_en_scan_degraded"),
        ("time_deposit_statement", "standard_en"),
        # Issue #79: 多言語（韓国語）決算書・資金エビデンス対応
        ("financial_statement", "kr_nts_standard"),
        ("financial_statement", "kr_kifrs_audited"),
        ("financial_statement", "kr_sme_simple"),
        ("financial_statement", "kr_kgaap_bracket_minus"),
        ("bank_balance_certificate", "kr_standard"),
        ("time_deposit_statement", "kr_standard"),
    ]
    for document_type, variant in templates:
        template = loader.load(case_id="CASE-TEST", document_type=document_type, variant=variant)
        assert template is not None, f"テンプレートが読み込めない: {document_type}/{variant}"


def test_registry_table_with_shareholders_renders(corporate_extended_case):
    loader = TemplateLoader()
    template = loader.load(
        case_id=corporate_extended_case.case_id,
        document_type="registry_certificate",
        variant="registry_table_with_shareholders",
    )
    html = template.render(case=corporate_extended_case)
    # 謄本本体
    assert "履 歴 事 項 全 部 証 明 書" in html
    assert "テスト商事株式会社" in html
    # 株主名簿（参考添付）の表と集計
    assert "株 主 名 簿（参考添付）" in html
    assert "テストベンチャーキャピタル1号投資事業有限責任組合" in html
    assert "テスト従業員持株会" in html
    assert "3,000株" in html
    assert "30.0%" in html
    assert "発行済株式の総数　10,000株" in html
    assert "55.0%" in html  # VC・ファンド等の議決権比率合計
    # 「謄本とは別書類だがテスト用に参考添付している」旨の注記
    assert "株主は記載されません" in html
    assert "参考添付" in html


def test_registry_table_without_shareholders_still_renders(corporate_case):
    """shareholders 未指定でも既存 variant はそのまま描画できる。"""
    loader = TemplateLoader()
    template = loader.load(
        case_id=corporate_case.case_id,
        document_type="registry_certificate",
        variant="registry_table",
    )
    html = template.render(case=corporate_case)
    assert "テスト商事株式会社" in html
    assert "株 主 名 簿" not in html
    # 本店移転していない謄本は「本店」欄の原因日付が設立日
    assert "2020年01月01日移転" in html


def test_registry_table_uses_head_office_transfer_date(corporate_case):
    """head_office_transfer_date を指定すると「本店」欄の原因日付が移転日になる。"""
    corporate_case.company.head_office_transfer_date = "2026年07月10日"
    loader = TemplateLoader()
    template = loader.load(
        case_id=corporate_case.case_id,
        document_type="registry_certificate",
        variant="registry_table",
    )
    html = template.render(case=corporate_case)
    assert "2026年07月10日移転" in html
    assert "2020年01月01日移転" not in html
    # 商号・会社成立年月日は設立日のまま（移転で変わらない）
    assert "2020年01月01日登記" in html

def test_load_withholding_slip_current_template():
    """申込者本人の当年分源泉徴収票 variant が既存 variant と別に存在する。"""
    loader = TemplateLoader()
    template = loader.load(
        case_id="CASE-TEST",
        document_type="income_certificate",
        variant="withholding_slip_current",
    )
    assert template is not None
    available = loader._list_available("income_certificate")
    assert "withholding_slip" in available
    assert "withholding_slip_current" in available


def test_load_multi_period_report_form_template(corporate_extended_case):
    """報告式BS（縦並び）の様式バリアントがロード＆レンダリングできる。"""
    loader = TemplateLoader()
    template = loader.load(
        case_id=corporate_extended_case.case_id,
        document_type="financial_statement",
        variant="multi_period_report_form",
    )
    assert template is not None
    available = loader._list_available("financial_statement")
    assert "multi_period" in available
    assert "multi_period_report_form" in available

    html = template.render(case=corporate_extended_case)
    # 報告式＝資産の部→負債の部→純資産の部を縦に並べる section 見出し
    assert "【資産の部】" in html
    assert "【負債の部】" in html
    assert "【純資産の部】" in html
    # 各期の数値（既存 multi_period と同じ器違いなので値は一致）
    assert "15,000,000円" in html  # 第1期 資産合計
    assert "テスト商事株式会社" in html


# --- Issue #76: 多言語（英語）決算書・資金エビデンス対応 ---

import re  # noqa: E402

from rental_pdf_generator.models import Case as _Case  # noqa: E402


def _ml_bank_balance_case(variant: str) -> _Case:
    return _Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-BAL",
            "applicant_type": "corporate",
            "company": {"company_name": "Sample Singapore Holdings Pte. Ltd."},
            "bank_balance_certificate": {
                "account_holder": "Sample Singapore Holdings Pte. Ltd.",
                "bank_name": "Sample Bank of Singapore",
                "branch_name": "Marina Bay Branch",
                "account_type": "Current Account",
                "account_number": "001-234567-8",
                "balance_as_of_date": "2026-06-30",
                "balance_amount": "S$2,450,000",
                "issue_date": "2026-07-05",
                "issuer_staff": "Tan Wei Ming",
                "source_currency": "SGD",
            },
            "documents": [{"document_type": "bank_balance_certificate", "variant": variant}],
        }
    )


def test_bank_balance_certificate_scan_degraded_renders():
    """P0-1: スキャン画質劣化・公印重なりの疑似演出がCSS/SVGで出力され、値自体は変わらない。"""
    case = _ml_bank_balance_case("standard_en_scan_degraded")
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id,
        document_type="bank_balance_certificate",
        variant="standard_en_scan_degraded",
    )
    html = template.render(case=case)
    assert "scan-noise-overlay" in html
    assert "degraded-stamp" in html
    assert "feTurbulence" in html
    # 劣化演出があっても金額の値自体は変わらず出力される
    assert "S$2,450,000" in html


def test_singapore_hk_en_currency_label_not_adjacent_to_numbers():
    """P0-2: 通貨単位表記がヘッダー注記に1回だけあり、金額数字には隣接しない。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-HK",
            "applicant_type": "corporate",
            "company": {"company_name": "Sample HK Trading Ltd."},
            "financials": {
                "fiscal_year": "FY2025",
                "sales": "128,450",
                "operating_income": "18,220",
                "ordinary_income": "17,600",
                "net_income": "13,900",
                "total_assets": "312,000",
                "total_liabilities": "150,000",
                "net_assets": "162,000",
                "source_currency": "HKD",
                "unit_multiplier": 1000,
                "accounting_standard": "HKFRS",
            },
            "documents": [
                {"document_type": "financial_statement", "variant": "singapore_hk_en"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="financial_statement", variant="singapore_hk_en"
    )
    html = template.render(case=case)
    # 通貨表記はヘッダー注記中に1回だけ出現する
    assert html.count("HK$") == 1
    # 表中の金額の値そのものには通貨記号が付与されていない（直前直後に $ がない）
    for value in ("128,450", "18,220", "17,600", "13,900", "312,000", "150,000", "162,000"):
        assert value in html
        assert re.search(r"\$\s*" + re.escape(value), html) is None
        assert re.search(re.escape(value) + r"\s*\$", html) is None


def test_ifrs_consolidated_en_renders_two_periods_with_continental_format():
    """P1: IFRS連結決算書は2期比較・大陸式桁区切り・括弧マイナスをそのまま出力する。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-IFRS",
            "applicant_type": "corporate",
            "company": {"company_name": "Sample Europe Holdings GmbH"},
            "financials_multi": [
                {
                    "fiscal_year": "FY2024",
                    "sales": "8.450.000,00",
                    "operating_income": "620.000,00",
                    "ordinary_income": "580.000,00",
                    "net_income": "(120.000,00)",
                    "total_assets": "22.000.000,00",
                    "total_liabilities": "9.500.000,00",
                    "net_assets": "12.500.000,00",
                    "source_currency": "EUR",
                    "unit_multiplier": 1,
                    "accounting_standard": "IFRS",
                },
                {
                    "fiscal_year": "FY2025",
                    "sales": "9.120.000,00",
                    "operating_income": "980.000,00",
                    "ordinary_income": "910.000,00",
                    "net_income": "710.000,00",
                    "total_assets": "24.500.000,00",
                    "total_liabilities": "10.100.000,00",
                    "net_assets": "14.400.000,00",
                    "source_currency": "EUR",
                    "unit_multiplier": 1,
                    "accounting_standard": "IFRS",
                },
            ],
            "documents": [
                {"document_type": "financial_statement", "variant": "ifrs_consolidated_en"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="financial_statement", variant="ifrs_consolidated_en"
    )
    html = template.render(case=case)
    assert "FY2024" in html
    assert "FY2025" in html
    assert "9.120.000,00" in html
    assert "(120.000,00)" in html
    assert "Profit before tax" in html


# --- Issue #79: 多言語（韓国語）決算書・資金エビデンス対応 ---


def _kr_detail_row(label, amount=None, code=None, key=None, emphasis=None, contra=False):
    row = {"label": label}
    if amount is not None:
        row["amount"] = amount
    if code is not None:
        row["code"] = code
    if key is not None:
        row["key"] = key
    if emphasis is not None:
        row["emphasis"] = emphasis
    if contra:
        row["contra"] = True
    return row


def _kr_nts_standard_case() -> _Case:
    return _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-NTS",
            "applicant_type": "corporate",
            "company": {
                "company_name": "주식회사 샘플테크코리아",
                "corporate_number": "000-00-00000",
                "representative_name": "김도윤",
            },
            "financials_detail": {
                "fiscal_year": "2025년 사업연도",
                "fiscal_period": "2025.01.01 ~ 2025.12.31",
                "unit_label": "원",
                "balance_sheet_rows": [
                    _kr_detail_row("현금및현금성자산", "350,000,000", code="011"),
                    _kr_detail_row(
                        "자산총계",
                        "1,700,000,000",
                        code="099",
                        key="total_assets",
                        emphasis="total",
                    ),
                ],
                "profit_loss_rows": [
                    _kr_detail_row("매출액", "2,400,000,000", code="311", key="sales"),
                ],
                "source_currency": "KRW",
                "unit_multiplier": 1,
                "accounting_standard": "NTS_STANDARD",
            },
            "documents": [
                {"document_type": "financial_statement", "variant": "kr_nts_standard"}
            ],
        }
    )


def test_kr_nts_standard_renders_code_numbers_and_three_pages():
    """コード番号付き・表紙/貸借対照表/損益計算書の3ページ構成であることを検証する。"""
    case = _kr_nts_standard_case()
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="financial_statement", variant="kr_nts_standard"
    )
    html = template.render(case=case)
    assert "011" in html
    assert "099" in html
    assert "311" in html
    assert "표준재무제표증명" in html
    assert "대 차 대 조 표" in html
    assert "손 익 계 산 서" in html
    # 3ページ構成（表紙・貸借対照表・損益計算書の3つの .page ブロックがあり、
    # 隣接ページ間に page-break-before が適用される）
    assert html.count('class="page"') == 3
    assert "page-break-before" in html


def test_kr_kifrs_audited_renders_two_periods():
    """K-IFRS2期比較は両期の決算年度表記が出力される。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-IFRS",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플글로벌코리아"},
            "financials_multi": [
                {
                    "fiscal_year": "제25기(2025)",
                    "sales": "125,400,000",
                    "total_assets": "210,000,000",
                    "source_currency": "KRW",
                    "unit_multiplier": 1000,
                    "accounting_standard": "K-IFRS",
                },
                {
                    "fiscal_year": "제24기(2024)",
                    "sales": "108,700,000",
                    "total_assets": "190,000,000",
                    "source_currency": "KRW",
                    "unit_multiplier": 1000,
                    "accounting_standard": "K-IFRS",
                },
            ],
            "documents": [
                {"document_type": "financial_statement", "variant": "kr_kifrs_audited"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="financial_statement", variant="kr_kifrs_audited"
    )
    html = template.render(case=case)
    assert "제25기" in html
    assert "제24기" in html
    assert "125,400,000" in html
    assert "108,700,000" in html


def test_kr_sme_simple_prints_label_variants_not_canonical_terms():
    """簡易様式は印字labelの表記ゆれをそのまま出力し、コード番号付き様式の正規表記は印字しない。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-SME",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플테크코리아"},
            "financials_detail": {
                "balance_sheet_rows": [
                    _kr_detail_row("외상매출금", "420,000,000"),
                    _kr_detail_row(
                        "자산 합계",
                        "1,700,000,000",
                        key="total_assets",
                        emphasis="total",
                    ),
                ],
                "profit_loss_rows": [
                    _kr_detail_row("매출", "2,400,000,000", key="sales"),
                ],
            },
            "documents": [
                {"document_type": "financial_statement", "variant": "kr_sme_simple"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="financial_statement", variant="kr_sme_simple"
    )
    html = template.render(case=case)
    # 表記ゆれの印字labelはそのまま出る
    assert "외상매출금" in html
    assert "매출" in html
    # コード番号なし（コード番号付き様式の正規表記「매출채권」「매출액」は印字されない）
    assert "매출채권" not in html
    assert "매출액" not in html
    assert "<td>코드</td>" not in html


def test_kr_kgaap_bracket_minus_coexists_with_contra_account_brackets():
    """括弧マイナスと控除科目名自体の括弧が同一書類に同居することを検証する。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-KGAAP",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플코리아홀딩스"},
            "financials_detail": {
                "balance_sheet_rows": [
                    _kr_detail_row("매출채권", "450,000,000"),
                    _kr_detail_row("대손충당금", "(15,000,000)", contra=True),
                    _kr_detail_row(
                        "자산총계", "1,255,000,000", key="total_assets", emphasis="total"
                    ),
                ],
                "profit_loss_rows": [
                    _kr_detail_row(
                        "당기순손실", "(68,000,000)", key="net_income", emphasis="total"
                    ),
                ],
            },
            "documents": [
                {"document_type": "financial_statement", "variant": "kr_kgaap_bracket_minus"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id,
        document_type="financial_statement",
        variant="kr_kgaap_bracket_minus",
    )
    html = template.render(case=case)
    # 控除科目名自体の括弧（科目名ラベルが括弧で括られる）
    assert "(대손충당금)" in html
    # 金額の括弧マイナス
    assert "(15,000,000)" in html
    assert "(68,000,000)" in html
    # 両ルールを明記した凡例
    assert "차감(공제)" in html


def test_kr_bank_balance_certificate_renders_amount_in_words():
    """잔액증명서は한글大字金額(amount_in_words)を併記できる。"""
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-BAL",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플무역코리아"},
            "bank_balance_certificate": {
                "account_holder": "주식회사 샘플무역코리아",
                "bank_name": "샘플은행",
                "balance_amount": "1,245,600,000원",
                "source_currency": "KRW",
                "amount_in_words": "금 일십이억사천오백육십만원정",
            },
            "documents": [
                {"document_type": "bank_balance_certificate", "variant": "kr_standard"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="bank_balance_certificate", variant="kr_standard"
    )
    html = template.render(case=case)
    assert "금 일십이억사천오백육십만원정" in html
    assert "1,245,600,000원" in html


def test_kr_time_deposit_statement_renders():
    case = _Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-TD",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플무역코리아"},
            "time_deposit_statement": {
                "account_holder": "주식회사 샘플무역코리아",
                "bank_name": "샘플은행",
                "principal_amount": "500,000,000원",
                "deposit_term": "12개월",
                "source_currency": "KRW",
            },
            "documents": [
                {"document_type": "time_deposit_statement", "variant": "kr_standard"}
            ],
        }
    )
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id, document_type="time_deposit_statement", variant="kr_standard"
    )
    html = template.render(case=case)
    assert "정 기 예 금 증 명 서" in html
    assert "500,000,000원" in html
    assert "12개월" in html


@pytest.mark.parametrize(
    "document_type,variant",
    [
        ("bank_balance_certificate", "kr_standard"),
        ("financial_statement", "kr_kifrs_audited"),
        ("financial_statement", "kr_nts_standard"),
        ("financial_statement", "kr_sme_simple"),
        ("financial_statement", "kr_kgaap_bracket_minus"),
        ("time_deposit_statement", "kr_standard"),
    ],
)
def test_kr_templates_declare_font_import_and_korean_lang(document_type, variant):
    """テンプレート原文にNoto Sans KRのCDN読み込みとlang="ko"宣言があることの回帰ガード。

    generator.py のブラウザコンテキストが locale="ja-JP" のため、lang 未指定だと
    CJK統合漢字が日本語字形で選ばれてしまう（Issue #79 設計方針）。
    """
    template_path = (
        Path(__file__).parent.parent / "templates" / document_type / f"{variant}.html"
    )
    source = template_path.read_text(encoding="utf-8")
    assert 'lang="ko"' in source
    assert "Noto+Sans+KR" in source


def test_load_invalid_document_type_raises():
    loader = TemplateLoader()
    with pytest.raises(TemplateNotFoundError) as exc_info:
        loader.load(
            case_id="CASE-TEST-999",
            document_type="nonexistent_type",
            variant="standard",
        )
    msg = str(exc_info.value)
    assert "CASE-TEST-999" in msg
    assert "nonexistent_type" in msg
    assert "standard" in msg


def test_load_invalid_variant_raises():
    loader = TemplateLoader()
    with pytest.raises(TemplateNotFoundError) as exc_info:
        loader.load(
            case_id="CASE-TEST-999",
            document_type="rental_application_corporate",
            variant="nonexistent_variant",
        )
    msg = str(exc_info.value)
    assert "CASE-TEST-999" in msg
    assert "nonexistent_variant" in msg
    assert "standard" in msg


def test_list_available_variants():
    loader = TemplateLoader()
    available = loader._list_available("rental_application_corporate")
    assert "standard" in available


def test_list_available_unknown_type_returns_empty():
    loader = TemplateLoader()
    available = loader._list_available("totally_unknown_type")
    assert available == []


# --- Issue #37: 申込者特定 異常系の様式（共同申込 / 共同代表 / 親会社代表の在留カード） ---

import json  # noqa: E402
from pathlib import Path  # noqa: E402

from rental_pdf_generator.models import Case  # noqa: E402

_CASES_JSONL = Path(__file__).parent.parent / "input" / "cases.jsonl"


def _load_case(case_id: str) -> Case:
    for line in _CASES_JSONL.read_text(encoding="utf-8").splitlines():
        if line.strip() and json.loads(line)["case_id"] == case_id:
            return Case.model_validate(json.loads(line))
    raise AssertionError(f"{case_id} が cases.jsonl に存在しない")


def test_joint_application_template_renders_both_applicants():
    case = _load_case("CASE-000057")
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id,
        document_type="rental_application_individual",
        variant="joint_application",
    )
    html = template.render(case=case)
    assert "共同申込" in html
    assert "申込者②" in html
    assert "田中 良太" in html  # 申込者①
    assert "田中 美咲" in html  # 申込者②
    assert "joint_application" in loader._list_available("rental_application_individual")


def test_joint_representative_template_renders_both_representatives():
    case = _load_case("CASE-000058")
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id,
        document_type="rental_application_corporate",
        variant="joint_representative",
    )
    html = template.render(case=case)
    assert "共同代表" in html
    assert "代表者②" in html
    assert "大崎 剛" in html  # 代表者①
    assert "五反田 舞" in html  # 代表者②


def test_parent_company_residence_card_template_renders_foreign_rep():
    case = _load_case("CASE-000059")
    loader = TemplateLoader()
    template = loader.load(
        case_id=case.case_id,
        document_type="parent_company_identity_document",
        variant="residence_card",
    )
    html = template.render(case=case)
    assert "在 留 カ ー ド" in html
    assert "リー・ジャンウェイ" in html  # 親会社代表（外国籍）
    assert "中国" in html  # 国籍
    assert "AB12345678CD" in html  # 在留カード番号
    assert "法人保証人" in html
