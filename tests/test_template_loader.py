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
