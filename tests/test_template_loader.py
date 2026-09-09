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
