import json
from pathlib import Path

import pytest

from rental_pdf_generator.answer_builder import UnsupportedDocumentTypeError, build_answer
from rental_pdf_generator.models import Case

CASES_JSONL = Path(__file__).parent.parent / "input" / "cases.jsonl"


def load_case_from_jsonl(case_id: str) -> Case:
    """input/cases.jsonl から指定ケースを読み込む。"""
    for line in CASES_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        if data["case_id"] == case_id:
            return Case.model_validate(data)
    raise AssertionError(f"{case_id} が cases.jsonl に存在しない")


def test_build_answer_corporate(corporate_case):
    answer = build_answer(corporate_case, "rental_application_corporate", "standard")
    assert answer["case_id"] == corporate_case.case_id
    assert answer["document_type"] == "rental_application_corporate"
    assert answer["variant"] == "standard"
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["corporate_number"] == "9999999999999"
    assert answer["fields"]["business_type"] == "IT・サービス業"
    assert "property_name" in answer["fields"]
    assert answer["fields"]["representative_name"] == "テスト 太郎"
    assert answer["fields"]["representative_kana"] == "テスト タロウ"
    assert answer["fields"]["representative_birth_date"] == "1980年01月01日"
    assert answer["fields"]["representative_age"] == "46"
    assert answer["fields"]["representative_gender"] == "男性"
    assert answer["fields"]["representative_address"] == "東京都千代田区テスト町2-2-2"
    assert answer["fields"]["postal_code"] == "100-0001"
    assert answer["fields"]["representative_postal_code"] == "100-0002"


def test_build_answer_corporate_no_guarantor(corporate_case):
    answer = build_answer(corporate_case, "rental_application_corporate", "standard")
    assert answer["fields"]["guarantor_name"] is None
    assert answer["fields"]["guarantor_kana"] is None


def test_build_answer_corporate_move_in_reason_defaults_to_none(corporate_case):
    """move_in_reason / new_business_reason 未設定の既存ケースは None のまま（挙動不変）。"""
    answer = build_answer(corporate_case, "rental_application_corporate", "office")
    assert answer["fields"]["move_in_reason"] is None
    assert answer["fields"]["new_business_reason"] is None


def test_build_answer_corporate_new_business_reason(corporate_case_data):
    """入居理由=新規開業・開業理由/背景欄の設定が正解JSONに反映される。"""
    corporate_case_data["property"]["move_in_reason"] = "新規開業"
    corporate_case_data["company"]["new_business_reason"] = "独立開業のため。"
    case = Case.model_validate(corporate_case_data)
    answer = build_answer(case, "rental_application_corporate", "office")
    assert answer["fields"]["move_in_reason"] == "新規開業"
    assert answer["fields"]["new_business_reason"] == "独立開業のため。"


def test_build_answer_corporate_application_category_defaults_to_none(corporate_case):
    """application_category 未設定の既存ケースは None のまま（挙動不変）。"""
    answer = build_answer(corporate_case, "rental_application_corporate", "office")
    assert answer["fields"]["application_category"] is None


def test_build_answer_corporate_application_category_existing_tenant(corporate_case_data):
    """申込区分=既存入居者が正解JSONに反映される。"""
    corporate_case_data["property"]["application_category"] = "既存入居者"
    case = Case.model_validate(corporate_case_data)
    answer = build_answer(case, "rental_application_corporate", "office")
    assert answer["fields"]["application_category"] == "既存入居者"


def test_build_answer_corporate_application_type_defaults_to_none(corporate_case):
    """application_type 未設定の既存ケースは None のまま（挙動不変）。"""
    answer = build_answer(corporate_case, "rental_application_corporate", "office")
    assert answer["fields"]["application_type"] is None


def test_build_answer_corporate_application_type_reflected(corporate_case_data):
    """申込種類=事務所が正解JSONに反映される。"""
    corporate_case_data["property"]["application_type"] = "事務所"
    case = Case.model_validate(corporate_case_data)
    answer = build_answer(case, "rental_application_corporate", "office")
    assert answer["fields"]["application_type"] == "事務所"


def test_build_answer_corporate_with_guarantor(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "rental_application_corporate", "office"
    )
    assert answer["fields"]["guarantor_name"] == "テスト 連帯"
    assert answer["fields"]["guarantor_kana"] == "テスト レンタイ"
    assert answer["fields"]["guarantor_birth_date"] == "1982年02月02日"
    assert answer["fields"]["guarantor_age"] == "44"
    assert answer["fields"]["guarantor_gender"] == "男性"
    assert answer["fields"]["guarantor_relationship"] == "代表取締役の配偶者"
    assert answer["fields"]["guarantor_postal_code"] == "100-0003"
    assert answer["fields"]["guarantor_annual_income"] == "9,000,000円"


def test_build_answer_guarantor_2_seal_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_2_seal_certificate", "standard"
    )
    assert answer["fields"]["name"] == "テスト 二郎"
    assert answer["fields"]["registration_number"] == "テスト2-第88888号"
    assert answer["fields"]["issuing_municipality"] == "東京都テスト2区"


def test_build_answer_guarantor_2_residence_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_2_residence_certificate", "standard"
    )
    assert answer["fields"]["name"] == "テスト 二郎"
    assert answer["fields"]["head_of_household"] == "テスト 二郎"
    assert answer["fields"]["resident_since"] == "2015年04月01日"


def test_build_answer_individual_guarantor_gender_age_postal(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "rental_application_individual", "standard"
    )
    # guarantor (テスト 一郎) gender/age/postal は INDIVIDUAL_CASE_DATA 由来で None の場合あり
    assert "guarantor_gender" in answer["fields"]
    assert "guarantor_age" in answer["fields"]
    assert "guarantor_postal_code" in answer["fields"]
    assert "guarantor_2_gender" in answer["fields"]
    assert "guarantor_2_postal_code" in answer["fields"]
    assert "postal_code" in answer["fields"]
    assert "emergency_contact_postal_code" in answer["fields"]


def test_build_answer_registry(corporate_case):
    answer = build_answer(corporate_case, "registry_certificate", "registry_table")
    assert answer["case_id"] == corporate_case.case_id
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["corporate_number"] == "9999999999999"
    assert "established_date" in answer["fields"]
    assert "capital" in answer["fields"]
    assert "annual_income" not in answer["fields"]


def test_build_answer_registry_without_shareholders(corporate_case):
    """shareholders 未指定のケースでは従来の出力（株主情報なし）が維持される。"""
    answer = build_answer(corporate_case, "registry_certificate", "registry_table")
    assert set(answer["fields"]) == {
        "company_name",
        "corporate_number",
        "head_office_address",
        "representative_name",
        "established_date",
        "capital",
        "business_description",
        "fiscal_year_end",
    }
    assert "shareholders" not in answer["fields"]
    assert "vc_voting_ratio_total" not in answer["fields"]


def test_build_answer_registry_with_head_office_transfer_date(corporate_case):
    """本店移転を登記した謄本では移転日が正解 JSON に載る（再アップロード検証用）。"""
    corporate_case.company.head_office_address = "東京都中央区テスト銀座3-3-3"
    corporate_case.company.head_office_transfer_date = "2026年07月10日"
    answer = build_answer(corporate_case, "registry_certificate", "registry_table")
    assert answer["fields"]["head_office_address"] == "東京都中央区テスト銀座3-3-3"
    assert answer["fields"]["head_office_transfer_date"] == "2026年07月10日"


def test_build_answer_registry_with_shareholders(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "registry_certificate", "registry_table_with_shareholders"
    )
    fields = answer["fields"]
    # 謄本本体の項目は従来どおり
    assert fields["company_name"] == "テスト商事株式会社"
    assert fields["corporate_number"] == "9999999999999"
    # 株主名簿の明細
    shareholders = fields["shareholders"]
    assert len(shareholders) == 4
    assert fields["shareholder_count"] == 4
    assert shareholders[0]["name"] == "テストベンチャーキャピタル1号投資事業有限責任組合"
    assert shareholders[0]["shareholder_type"] == "VC（投資事業有限責任組合）"
    assert shareholders[0]["share_class"] == "A種優先株式"
    assert shareholders[0]["shares"] == "3,000株"
    assert shareholders[0]["voting_ratio"] == "30.0%"
    assert shareholders[0]["acquired_date"] == "2024年06月20日"
    assert shareholders[0]["note"] == "シリーズA リード投資家"
    # 株主構成の集計（VC の持株比率合計が検証できる粒度）
    assert fields["total_shares"] == "10,000株"
    assert fields["vc_shareholder_count"] == 2
    assert fields["vc_shareholder_names"] == [
        "テストベンチャーキャピタル1号投資事業有限責任組合",
        "テストグロースファンド2号投資事業組合",
    ]
    assert fields["vc_shares_total"] == "5,500株"
    assert fields["vc_voting_ratio_total"] == "55.0%"
    assert fields["founder_voting_ratio_total"] == "35.0%"


def test_build_answer_registry_shareholders_empty_list(corporate_extended_case):
    """空リストの場合は株主情報を出力しない（None 指定と同じ扱い）。"""
    corporate_extended_case.shareholders = []
    answer = build_answer(
        corporate_extended_case, "registry_certificate", "registry_table_with_shareholders"
    )
    assert "shareholders" not in answer["fields"]


def test_build_answer_financial(corporate_case):
    answer = build_answer(corporate_case, "financial_statement", "financial_summary")
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["sales"] == "50,000,000円"
    assert answer["fields"]["net_income"] == "3,000,000円"
    assert answer["fields"]["total_assets"] == "20,000,000円"


def test_build_answer_business_plan(corporate_case):
    answer = build_answer(corporate_case, "business_plan", "narrative")
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["business_overview"] == "テスト事業の拡大を計画しています。"
    assert "plan_period" in answer["fields"]


def test_build_answer_business_plan_corporate_startup(corporate_case):
    answer = build_answer(corporate_case, "business_plan", "corporate_startup")
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["trade_name"] == "テスト屋号"
    assert answer["fields"]["opening_date"] == "2026年04月01日"
    assert answer["fields"]["initial_capital"] == "5,000,000円"
    assert answer["fields"]["founder_background"] == "テスト経歴"


def test_build_answer_business_plan_individual_startup(individual_case):
    individual_case.business_plan = corporate_case_business_plan()
    answer = build_answer(individual_case, "business_plan", "individual_startup")
    assert answer["fields"]["applicant_name"] == "テスト 花子"
    assert answer["fields"]["trade_name"] == "テスト屋号"
    assert answer["fields"]["business_category"] == "テスト業種"
    assert answer["fields"]["monthly_revenue_target"] == "500,000円"


def corporate_case_business_plan():
    from rental_pdf_generator.models import BusinessPlan
    return BusinessPlan(
        plan_period="2026年度",
        business_overview="テスト",
        revenue_plan="テスト",
        hiring_plan="テスト",
        risk_factors="テスト",
        trade_name="テスト屋号",
        opening_date="2026年04月01日",
        business_category="テスト業種",
        target_customers="テスト顧客",
        initial_capital="5,000,000円",
        funding_plan="自己資金のみ",
        monthly_revenue_target="500,000円",
        monthly_cost_estimate="200,000円",
        founder_background="テスト経歴",
        competitive_advantage="テスト優位性",
        marketing_strategy="テスト戦略",
    )


def test_build_answer_individual(individual_case):
    answer = build_answer(individual_case, "rental_application_individual", "standard")
    assert answer["case_id"] == individual_case.case_id
    assert answer["fields"]["name"] == "テスト 花子"
    assert answer["fields"]["employer_name"] == "テスト株式会社"
    assert "emergency_contact_name" in answer["fields"]
    assert answer["fields"]["guarantor_name"] == "テスト 一郎"
    assert answer["fields"]["guarantor_relationship"] == "父"
    assert answer["fields"]["guarantor_employer_name"] == "テスト製造株式会社"


def test_build_answer_individual_no_guarantor(individual_case):
    individual_case.guarantor = None
    answer = build_answer(individual_case, "rental_application_individual", "standard")
    assert answer["fields"]["guarantor_name"] is None
    assert answer["fields"]["guarantor_annual_income"] is None


def test_build_answer_individual_new_fields_default_to_none(individual_case):
    """residence_type / move_in_reason / application_category / 緊急連絡先フリガナ・生年月日は
    未設定の既存ケースでは None のまま（挙動不変）。"""
    answer = build_answer(individual_case, "rental_application_individual", "standard")
    assert answer["fields"]["residence_type"] is None
    assert answer["fields"]["move_in_reason"] is None
    assert answer["fields"]["application_category"] is None
    assert answer["fields"]["emergency_contact_kana"] is None
    assert answer["fields"]["emergency_contact_birth_date"] is None


def test_build_answer_individual_new_fields_reflected(individual_case_data):
    """住居種類・入居理由・申込区分・緊急連絡先フリガナ/生年月日が正解JSONに反映される。"""
    individual_case_data["applicant"]["residence_type"] = "賃貸"
    individual_case_data["applicant"]["move_in_reason"] = "移転"
    individual_case_data["property"]["application_category"] = "新規申込者"
    individual_case_data["emergency_contact"]["kana"] = "テスト イチロウ"
    individual_case_data["emergency_contact"]["birth_date"] = "1965年01月01日"
    case = Case.model_validate(individual_case_data)
    answer = build_answer(case, "rental_application_individual", "standard")
    assert answer["fields"]["residence_type"] == "賃貸"
    assert answer["fields"]["move_in_reason"] == "移転"
    assert answer["fields"]["application_category"] == "新規申込者"
    assert answer["fields"]["emergency_contact_kana"] == "テスト イチロウ"
    assert answer["fields"]["emergency_contact_birth_date"] == "1965年01月01日"


def test_build_answer_individual_application_type_defaults_to_none(individual_case):
    """application_type 未設定の既存ケースは None のまま（挙動不変）。"""
    answer = build_answer(individual_case, "rental_application_individual", "standard")
    assert answer["fields"]["application_type"] is None


def test_build_answer_individual_application_type_reflected(individual_case_data):
    """申込種類=事務所が正解JSONに反映される。"""
    individual_case_data["property"]["application_type"] = "事務所"
    case = Case.model_validate(individual_case_data)
    answer = build_answer(case, "rental_application_individual", "standard")
    assert answer["fields"]["application_type"] == "事務所"


def test_build_answer_income(individual_case):
    answer = build_answer(individual_case, "income_certificate", "salary_certificate")
    assert answer["fields"]["name"] == "テスト 花子"
    assert answer["fields"]["annual_income"] == "4,000,000円"
    assert answer["fields"]["issue_date"] == "2026年05月01日"
    assert answer["fields"]["base_salary"] == "270,000円"
    assert answer["fields"]["bonus"] == "600,000円"
    assert answer["fields"]["certificate_expiry"] == "2026年08月01日"


def test_build_answer_identity_document(individual_case):
    answer = build_answer(individual_case, "identity_document", "drivers_license")
    assert answer["case_id"] == individual_case.case_id
    assert answer["document_type"] == "identity_document"
    assert answer["variant"] == "drivers_license"
    assert answer["fields"]["name"] == "テスト 花子"
    assert answer["fields"]["license_number"] == "999999999999"
    assert answer["fields"]["expiry"] == "2028年06月15日"
    assert answer["fields"]["birth_date"] == "1995年06月15日"


def test_build_answer_none_fields_when_no_data(corporate_case):
    corporate_case.financials = None
    answer = build_answer(corporate_case, "financial_statement", "financial_summary")
    assert answer["fields"]["sales"] is None
    assert answer["fields"]["net_income"] is None


def test_build_answer_unsupported_type_raises(corporate_case):
    with pytest.raises(UnsupportedDocumentTypeError):
        build_answer(corporate_case, "unknown_document_type", "standard")


def test_build_answer_corporate_guarantee_contract(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "corporate_guarantee_contract", "standard"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["guarantor_name"] == "テスト 太郎"
    assert answer["fields"]["relationship_to_company"] == "代表取締役"
    assert answer["fields"]["guarantee_amount"] == "3,600,000円（賃料36ヶ月分）"


def test_build_answer_parent_company_guarantee_letter(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "parent_company_guarantee_letter", "standard"
    )
    assert answer["fields"]["subsidiary_name"] == "テスト商事株式会社"
    assert answer["fields"]["parent_company_name"] == "テストホールディングス株式会社"
    assert answer["fields"]["parent_company_capital"] == "100,000,000円"
    assert answer["fields"]["relationship"] == "100%親会社"


def test_build_answer_parent_company_registry_certificate(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "parent_company_registry_certificate", "registry_table"
    )
    assert answer["fields"]["company_name"] == "テストホールディングス株式会社"
    assert answer["fields"]["corporate_number"] == "1111111111111"
    assert answer["fields"]["representative_name"] == "親会社 代表"


def test_build_answer_parent_company_financial_statement(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "parent_company_financial_statement", "financial_summary"
    )
    assert answer["fields"]["company_name"] == "テストホールディングス株式会社"
    assert answer["fields"]["sales"] == "500,000,000円"
    assert answer["fields"]["net_income"] == "40,000,000円"


def test_build_answer_parent_company_financial_statement_expected_foreign_currency_flag_false(
    corporate_extended_case,
):
    # 外国親会社が関与していても、決算書自体がJPY表記なら真陰性（false）になる。
    answer = build_answer(
        corporate_extended_case, "parent_company_financial_statement", "financial_summary"
    )
    assert answer["fields"]["expected_foreign_currency_flag"] is False
    assert "source_currency" not in answer["fields"]


def test_build_answer_business_license(corporate_extended_case):
    answer = build_answer(corporate_extended_case, "business_license", "restaurant")
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["license_name"] == "飲食店営業許可"
    assert answer["fields"]["license_number"] == "TEST-XYZ-12345"
    assert answer["fields"]["issuing_authority"] == "テスト保健所"


def test_build_answer_guarantor_2_income_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_2_income_certificate", "salary_certificate"
    )
    assert answer["fields"]["name"] == "テスト 二郎"
    assert answer["fields"]["relationship"] == "叔父"
    assert answer["fields"]["annual_income"] == "7,000,000円"
    assert answer["fields"]["employer_name"] == "テスト保証株式会社"


def test_build_answer_guarantor_seal_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_seal_certificate", "standard"
    )
    assert answer["fields"]["name"] == "テスト 一郎"
    assert answer["fields"]["registration_number"] == "テスト-第99999号"
    assert answer["fields"]["issuing_municipality"] == "東京都テスト区"


def test_build_answer_guarantor_residence_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_residence_certificate", "standard"
    )
    assert answer["fields"]["name"] == "テスト 一郎"
    assert answer["fields"]["gender"] == "男性"
    assert answer["fields"]["head_of_household"] == "テスト 一郎"
    assert answer["fields"]["resident_since"] == "2018年04月01日"


def test_build_answer_guarantor_2_identity_document(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantor_2_identity_document", "drivers_license"
    )
    assert answer["fields"]["name"] == "テスト 二郎"
    assert answer["fields"]["license_number"] == "888888888888"
    assert answer["fields"]["relationship"] == "叔父"


def test_build_answer_guarantee_company_application(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "guarantee_company_application", "standard"
    )
    assert answer["fields"]["applicant_name"] == "テスト 花子"
    assert answer["fields"]["guarantee_company_name"] == "テスト家賃保証株式会社"
    assert answer["fields"]["plan_name"] == "テストプラン"
    assert answer["fields"]["coverage_amount"] == "1,920,000円"


def test_build_answer_offer_letter(individual_extended_case):
    answer = build_answer(individual_extended_case, "offer_letter", "standard")
    assert answer["fields"]["applicant_name"] == "テスト 花子"
    assert answer["fields"]["employer_name"] == "テスト新会社株式会社"
    assert answer["fields"]["start_date"] == "2026年09月01日"
    assert answer["fields"]["expected_annual_income"] == "6,500,000円"


def test_build_answer_student_id(individual_extended_case):
    answer = build_answer(individual_extended_case, "student_id", "standard")
    assert answer["fields"]["name"] == "テスト 学生"
    assert answer["fields"]["school_name"] == "テスト大学"
    assert answer["fields"]["student_number"] == "T260123-456"
    assert answer["fields"]["relationship_to_applicant"] == "長男"


def test_build_answer_individual_with_guarantor_2(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "rental_application_individual", "standard"
    )
    assert answer["fields"]["guarantor_2_name"] == "テスト 二郎"
    assert answer["fields"]["guarantor_2_relationship"] == "叔父"
    assert answer["fields"]["cohabitant_student_name"] == "テスト 学生"
    assert answer["fields"]["cohabitant_student_school_name"] == "テスト大学"


def test_build_answer_income_with_previous_employment(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "income_certificate", "withholding_slip"
    )
    assert answer["fields"]["previous_employer_name"] == "テスト前職株式会社"
    assert answer["fields"]["previous_gross_income"] == "4,000,000円"
    assert answer["fields"]["previous_end_date"] == "2026年08月31日"


def test_build_answer_income_withholding_slip_current(individual_case):
    """申込者本人の当年分源泉徴収票の正解JSONに支払金額と各控除額が含まれる。"""
    answer = build_answer(
        individual_case, "income_certificate", "withholding_slip_current"
    )
    assert answer["variant"] == "withholding_slip_current"
    fields = answer["fields"]
    assert fields["name"] == "テスト 花子"
    assert fields["payment_amount"] == "4,000,000円"
    assert fields["salary_income_deduction"] == "1,240,000円"
    assert fields["income_after_deduction"] == "2,760,000円"
    assert fields["social_insurance"] == "596,000円"
    assert fields["total_deductions"] == "1,076,000円"
    assert fields["taxable_income"] == "1,684,000円"
    assert fields["withholding_tax"] == "85,900円"
    assert fields["dependents_count"] == "0人"
    assert fields["spouse_status"] == "無"
    # 支払金額は申込書・在職証明の年収と一致する
    assert fields["payment_amount"] == fields["annual_income"]
    # 支払者（勤務先）情報も抽出できる
    assert fields["employer_name"] == "テスト株式会社"
    assert fields["employer_address"] == "東京都渋谷区テスト2-2-2"
    # 前職源泉徴収票（既存 variant）のフィールドは本人版では未設定
    assert fields["previous_employer_name"] is None


def test_build_answer_income_withholding_slip_current_amount_consistency():
    """CASE-000054 の源泉徴収票の金額が計算式どおり整合している。"""
    target = load_case_from_jsonl("CASE-000054")
    answer = build_answer(target, "income_certificate", "withholding_slip_current")
    fields = answer["fields"]

    def yen(value: str) -> int:
        return int(value.replace(",", "").replace("円", ""))

    assert yen(fields["payment_amount"]) - yen(fields["salary_income_deduction"]) == yen(
        fields["income_after_deduction"]
    )
    assert yen(fields["income_after_deduction"]) - yen(fields["total_deductions"]) == yen(
        fields["taxable_income"]
    )
    assert (
        yen(fields["social_insurance"])
        + yen(fields["basic_deduction"])
        + yen(fields["life_insurance_deduction"])
        == yen(fields["total_deductions"])
    )
    assert fields["payment_amount"] == fields["annual_income"]


def test_build_answer_business_license_application(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "business_license_application", "restaurant"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["applicant_name"] == "テスト商事株式会社"
    assert answer["fields"]["receipt_number"] == "TEST-AP-99999"
    assert answer["fields"]["status_note"] == "申請中につき許可書未交付"
    assert answer["fields"]["issuing_authority"] == "テスト保健所"


def test_build_answer_payment_track_record_pledge(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "payment_track_record_pledge", "standard"
    )
    assert answer["fields"]["pledger_name"] == "テスト商事株式会社"
    assert answer["fields"]["representative_name"] == "テスト 太郎"
    assert answer["fields"]["delinquency_record"] == "延滞なし"
    assert answer["fields"]["payment_period"] == "2014年04月〜2026年08月"
    assert answer["fields"]["current_lease_rent"] == "300,000円/月"
    assert answer["fields"]["delinquency_count"] == "0回"
    assert answer["fields"]["total_paid_amount"] == "44,400,000円"
    assert answer["fields"]["settlement_status"] == "完済（未払残高 0円）"


def test_build_answer_payment_track_record_pledge_same_applicant():
    """CASE-000056 の確約者・代表者が申込法人・代表者と一致する（同一申込者版）。"""
    case = load_case_from_jsonl("CASE-000056")
    answer = build_answer(case, "payment_track_record_pledge", "standard")
    fields = answer["fields"]
    assert fields["pledger_name"] == fields["company_name"]
    assert fields["pledger_name"] == case.company.company_name
    assert fields["representative_name"] == case.company.representative_name
    # 契約物件 / 期間 / 月額 / 遅延 / 完済 がすべて抽出できる
    for key in (
        "current_lease_property",
        "payment_period",
        "current_lease_rent",
        "delinquency_record",
        "delinquency_count",
        "settlement_status",
    ):
        assert fields[key], f"{key} が空"


def test_case_000056_outputs_pledge_in_pdf_and_docx():
    """支払実績確約書を PDF と Word の2形式で出力するよう定義されている。"""
    case = load_case_from_jsonl("CASE-000056")
    formats = {
        doc.output_format
        for doc in case.documents
        if doc.document_type == "payment_track_record_pledge"
    }
    assert formats == {"pdf", "docx"}


def test_case_000055_financials_are_consistent():
    """CASE-000055 は売上約10億円で、総資産 = 負債 + 純資産 が成立する。"""
    case = load_case_from_jsonl("CASE-000055")
    answer = build_answer(case, "financial_statement", "financial_summary")
    fields = answer["fields"]

    def yen(value: str) -> int:
        return int(value.replace(",", "").replace("円", ""))

    assert fields["sales"] == "1,024,000,000円"
    assert 900_000_000 <= yen(fields["sales"]) <= 1_100_000_000
    assert yen(fields["total_assets"]) == yen(fields["total_liabilities"]) + yen(
        fields["net_assets"]
    )
    assert yen(fields["operating_income"]) > yen(fields["ordinary_income"])
    assert yen(fields["ordinary_income"]) > yen(fields["net_income"])

    prior = build_answer(case, "financial_statement", "financial_summary_prior")["fields"]
    assert yen(prior["total_assets"]) == yen(prior["total_liabilities"]) + yen(
        prior["net_assets"]
    )
    # 前期純資産 + 当期純利益 = 当期純資産（配当なし）
    assert yen(prior["net_assets"]) + yen(fields["net_income"]) == yen(fields["net_assets"])


def test_build_answer_funding_evidence(corporate_extended_case):
    answer = build_answer(corporate_extended_case, "funding_evidence", "standard")
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["own_capital"] == "20,000,000円"
    assert answer["fields"]["bank_loan"] == "30,000,000円"
    assert answer["fields"]["investment"] == "120,000,000円"
    assert answer["fields"]["total_funding"] == "175,000,000円"
    assert answer["fields"]["investor_name"] == "テストVC"


def test_build_answer_funding_evidence_expected_foreign_currency_flag_false(
    corporate_extended_case,
):
    answer = build_answer(corporate_extended_case, "funding_evidence", "standard")
    assert answer["fields"]["expected_foreign_currency_flag"] is False


def test_build_answer_business_use_pledge(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "business_use_pledge", "no_license_required"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["pledger_name"] == "テスト商事株式会社"
    assert answer["fields"]["representative_name"] == "テスト 太郎"
    assert answer["fields"]["original_business_type"] == "飲食店営業（イートイン併設）"
    assert answer["fields"]["changed_business_type"] == "テイクアウト専門"
    assert answer["fields"]["license_required"] == "不要"


def test_build_answer_financial_statement_multi_period(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "financial_statement", "multi_period"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    periods = answer["fields"]["periods"]
    assert len(periods) == 3
    assert periods[0]["fiscal_year"] == "2023年度"
    assert periods[2]["fiscal_year"] == "2025年度"
    assert periods[2]["sales"] == "50,000,000円"


def test_build_answer_financial_statement_report_form_matches_multi_period(
    corporate_extended_case,
):
    """報告式BS は器（レイアウト）違いなので answer は multi_period と完全一致（labels 不変）。"""
    report_form = build_answer(
        corporate_extended_case, "financial_statement", "multi_period_report_form"
    )
    multi_period = build_answer(
        corporate_extended_case, "financial_statement", "multi_period"
    )
    assert report_form["fields"] == multi_period["fields"]


def test_build_answer_income_certificate_multi_year(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "income_certificate", "tax_return_multi_year"
    )
    assert answer["fields"]["name"] == "テスト 花子"
    periods = answer["fields"]["periods"]
    assert len(periods) == 2
    assert periods[0]["income_year"] == "2023年"
    assert periods[1]["annual_income"] == "4,000,000円"


def test_build_answer_financial_statement_prior(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "financial_statement", "financial_summary_prior"
    )
    assert answer["fields"]["fiscal_year"] == "2024年度"
    assert answer["fields"]["sales"] == "40,000,000円"
    assert answer["fields"]["net_income"] == "2,400,000円"


def test_build_answer_financial_statement_current_still_works(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "financial_statement", "financial_summary"
    )
    assert answer["fields"]["fiscal_year"] == "2025年度"
    assert answer["fields"]["sales"] == "50,000,000円"


def test_build_answer_financial_statement_expected_foreign_currency_flag_false(
    corporate_extended_case,
):
    answer = build_answer(corporate_extended_case, "financial_statement", "financial_summary")
    assert answer["fields"]["expected_foreign_currency_flag"] is False
    assert "source_currency" not in answer["fields"]


def test_build_answer_financial_statement_multi_period_expected_foreign_currency_flag_false(
    corporate_extended_case,
):
    answer = build_answer(corporate_extended_case, "financial_statement", "multi_period")
    assert answer["fields"]["expected_foreign_currency_flag"] is False


def test_build_answer_income_certificate_prior(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "income_certificate", "tax_return_prior"
    )
    assert answer["fields"]["income_year"] == "2024年"
    assert answer["fields"]["annual_income"] == "3,800,000円"
    assert answer["fields"]["base_salary"] == "260,000円"


def test_build_answer_trial_balance(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "trial_balance", "monthly_summary"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["fiscal_period"] == "2026年10月度（月次）"
    assert answer["fields"]["total_assets"] == "22,500,000円"
    assert answer["fields"]["operating_profit"] == "2,600,000円"


def test_build_answer_trial_balance_expected_foreign_currency_flag_false(
    corporate_extended_case,
):
    answer = build_answer(corporate_extended_case, "trial_balance", "monthly_summary")
    assert answer["fields"]["expected_foreign_currency_flag"] is False


def test_build_answer_corporate_with_housing_usage(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "rental_application_corporate", "housing"
    )
    assert answer["fields"]["housing_occupant_name"] == "テスト 役員"
    assert answer["fields"]["housing_contract_name"] == "法人契約"


def test_build_answer_corporate_with_store_usage(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "rental_application_corporate", "store"
    )
    assert answer["fields"]["store_business_format"] == "飲食店（カフェ業態）"
    assert answer["fields"]["store_operating_hours"] == "8:00〜22:00"


def test_build_answer_individual_with_soho_usage(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "rental_application_individual", "soho"
    )
    assert answer["fields"]["soho_business_type"] == "Webデザイン"
    assert answer["fields"]["soho_residential_ratio"] == "60%"
    assert answer["fields"]["soho_has_signboard"] == "なし"


def test_build_answer_business_opening_notice(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "business_opening_notice", "individual"
    )
    assert answer["fields"]["owner_name"] == "テスト 花子"
    assert answer["fields"]["trade_name"] == "テスト屋号"
    assert answer["fields"]["issuing_tax_office"] == "テスト税務署"
    assert answer["fields"]["opening_date"] == "2026年06月01日"
    assert answer["fields"]["employs_others"] == "なし"


def test_build_answer_bank_balance_certificate(individual_extended_case):
    answer = build_answer(
        individual_extended_case, "bank_balance_certificate", "standard"
    )
    assert answer["fields"]["account_holder"] == "テスト 花子"
    assert answer["fields"]["bank_name"] == "テストメガバンク"
    assert answer["fields"]["branch_name"] == "テスト支店"
    assert answer["fields"]["balance_amount"] == "3,500,000円"


def test_build_answer_bank_balance_certificate_expected_foreign_currency_flag_false(
    individual_extended_case,
):
    answer = build_answer(individual_extended_case, "bank_balance_certificate", "standard")
    assert answer["fields"]["expected_foreign_currency_flag"] is False
    assert "source_currency" not in answer["fields"]


# --- Issue #76: 多言語（英・中・韓）決算書・資金エビデンス対応の通貨メタ情報 ---


def test_build_answer_financial_statement_with_source_currency_is_foreign():
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-001",
            "applicant_type": "corporate",
            "company": {"company_name": "Sample US Holdings Inc."},
            "financials": {
                "fiscal_year": "FY2025",
                "sales": "$12,345,000",
                "source_currency": "USD",
                "unit_multiplier": 1000,
                "accounting_standard": "US_GAAP",
            },
            "documents": [{"document_type": "financial_statement", "variant": "us_gaap_en"}],
        }
    )
    answer = build_answer(case, "financial_statement", "us_gaap_en")
    assert answer["fields"]["expected_foreign_currency_flag"] is True
    assert answer["fields"]["source_currency"] == "USD"
    assert answer["fields"]["unit_multiplier"] == 1000
    assert answer["fields"]["accounting_standard"] == "US_GAAP"


def test_build_answer_time_deposit_statement():
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-002",
            "applicant_type": "corporate",
            "company": {"company_name": "Sample HK Trading Ltd."},
            "time_deposit_statement": {
                "account_holder": "Sample HK Trading Ltd.",
                "bank_name": "Sample Bank of Hong Kong",
                "branch_name": "Central Branch",
                "account_number": "HK-001-234567",
                "principal_amount": "500,000",
                "interest_rate": "2.5% p.a.",
                "deposit_date": "2026-01-15",
                "maturity_date": "2027-01-15",
                "deposit_term": "12 months",
                "issue_date": "2026-01-16",
                "issuer_staff": "Chan Tai Man",
                "source_currency": "HKD",
                "unit_multiplier": 1,
            },
            "documents": [
                {"document_type": "time_deposit_statement", "variant": "standard_en"}
            ],
        }
    )
    answer = build_answer(case, "time_deposit_statement", "standard_en")
    assert answer["fields"]["account_holder"] == "Sample HK Trading Ltd."
    assert answer["fields"]["principal_amount"] == "500,000"
    assert answer["fields"]["maturity_date"] == "2027-01-15"
    assert answer["fields"]["expected_foreign_currency_flag"] is True
    assert answer["fields"]["source_currency"] == "HKD"


# --- Issue #78: 多言語（中国語：本土・台湾・香港）決算書・資金エビデンス対応 ---


@pytest.mark.parametrize(
    "variant,source_currency,unit_multiplier,accounting_standard",
    [
        ("cn_mainland_account_style", "CNY", 1, "CAS"),
        ("cn_taiwan_report_form", "TWD", 1000, "TIFRS"),
        ("cn_hk_bilingual", "HKD", 1000, "HKFRS"),
        ("cn_mainland_en_translated", "CNY", 1000, "CAS"),
        ("cn_taiwan_en_translated", "TWD", 1000, "TIFRS"),
    ],
)
def test_build_answer_cn_financial_statement_currency_meta(
    variant, source_currency, unit_multiplier, accounting_standard
):
    """中国語（本土・台湾・香港）決算書 variant は通貨・単位・会計基準の3メタ情報が
    正しく正解JSONへ展開され、expected_foreign_currency_flag が true になる。"""
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-CN-001",
            "applicant_type": "corporate",
            "company": {"company_name": "样品测试有限公司"},
            "financials": {
                "fiscal_year": "2025年度",
                "sales": "100,000",
                "operating_income": "10,000",
                "ordinary_income": "9,000",
                "net_income": "7,000",
                "total_assets": "300,000",
                "total_liabilities": "120,000",
                "net_assets": "180,000",
                "source_currency": source_currency,
                "unit_multiplier": unit_multiplier,
                "accounting_standard": accounting_standard,
            },
            "documents": [{"document_type": "financial_statement", "variant": variant}],
        }
    )
    answer = build_answer(case, "financial_statement", variant)
    assert answer["fields"]["expected_foreign_currency_flag"] is True
    assert answer["fields"]["source_currency"] == source_currency
    assert answer["fields"]["unit_multiplier"] == unit_multiplier
    assert answer["fields"]["accounting_standard"] == accounting_standard
    assert answer["fields"]["total_assets"] == "300,000"


@pytest.mark.parametrize(
    "variant",
    [
        "cn_mainland_account_style",
        "cn_taiwan_report_form",
        "cn_hk_bilingual",
        "cn_mainland_en_translated",
        "cn_taiwan_en_translated",
    ],
)
def test_build_answer_cn_financial_statement_not_routed_to_multi_period(variant):
    """cn_* variant は 'multi' で始まらず '_prior' でも終わらないため、
    financials_multi 分岐（periods キー）に誤ルーティングされず単一期の financials 分岐を使う
    （既存の _MULTI_PERIOD_VARIANTS_PREFIX / _EXTRA ルーティングとの衝突回帰テスト）。"""
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-CN-ROUTE",
            "applicant_type": "corporate",
            "company": {"company_name": "样品测试有限公司"},
            "financials": {
                "fiscal_year": "2025年度",
                "total_assets": "300,000",
                "source_currency": "CNY",
                "unit_multiplier": 1,
                "accounting_standard": "CAS",
            },
            "documents": [{"document_type": "financial_statement", "variant": variant}],
        }
    )
    answer = build_answer(case, "financial_statement", variant)
    assert "periods" not in answer["fields"]
    assert answer["fields"]["total_assets"] == "300,000"


@pytest.mark.parametrize(
    "variant,source_currency",
    [
        ("cn_mainland_deposit_certificate", "CNY"),
        ("cn_trad_deposit_certificate", "TWD"),
        ("cn_trad_deposit_certificate", "HKD"),
    ],
)
def test_build_answer_cn_deposit_certificate_currency_meta(variant, source_currency):
    """存款证明书（簡体字／繁体字）も既存の bank_balance_certificate builder で
    source_currency/expected_foreign_currency_flag が正しく展開される。"""
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-ML-CN-DEP",
            "applicant_type": "corporate",
            "company": {"company_name": "样品测试有限公司"},
            "bank_balance_certificate": {
                "account_holder": "样品测试有限公司",
                "bank_name": "样本银行",
                "branch_name": "测试分行",
                "account_type": "帐户",
                "account_number": "0000000000",
                "balance_as_of_date": "2026年06月30日",
                "balance_amount": "1,280,000元",
                "issue_date": "2026年07月02日",
                "issuer_staff": "测试",
                "source_currency": source_currency,
                "unit_multiplier": 1,
            },
            "documents": [{"document_type": "bank_balance_certificate", "variant": variant}],
        }
    )
    answer = build_answer(case, "bank_balance_certificate", variant)
    assert answer["fields"]["expected_foreign_currency_flag"] is True
    assert answer["fields"]["source_currency"] == source_currency
    assert answer["fields"]["balance_amount"] == "1,280,000元"


# --- Issue #37: 申込者特定 異常系（共同申込 / 共同代表 / 外国籍親会社代表 / 保証人=本人） ---


def test_build_answer_joint_application_has_applicant_2():
    """TC-1-070 共同申込: 申込者②のキーが answer に出る。"""
    case = load_case_from_jsonl("CASE-000057")
    fields = build_answer(case, "rental_application_individual", "joint_application")[
        "fields"
    ]
    assert fields["name"] == "田中 良太"
    assert fields["applicant_2_name"] == "田中 美咲"
    assert fields["applicant_2_kana"] == "タナカ ミサキ"
    assert fields["applicant_2_birth_date"] == "1990年03月20日"
    # 申込者①と②は別人（共同申込であることが labels から判定できる）
    assert fields["name"] != fields["applicant_2_name"]


def test_build_answer_joint_representative_has_representative_2():
    """TC-1-071 共同代表: 代表者②のキーが answer に出る。"""
    case = load_case_from_jsonl("CASE-000058")
    fields = build_answer(
        case, "rental_application_corporate", "joint_representative"
    )["fields"]
    assert fields["representative_name"] == "大崎 剛"
    assert fields["representative_2_name"] == "五反田 舞"
    assert fields["representative_2_gender"] == "女性"
    assert fields["representative_name"] != fields["representative_2_name"]


def test_build_answer_parent_company_identity_document_residence_card():
    """TC-1-094 外国籍の親会社代表: 在留カードの名義人・国籍・カード番号が answer に出る。"""
    case = load_case_from_jsonl("CASE-000059")
    fields = build_answer(
        case, "parent_company_identity_document", "residence_card"
    )["fields"]
    assert fields["name"] == "リー・ジャンウェイ"
    assert fields["nationality"] == "中国"
    assert fields["residence_card_number"] == "AB12345678CD"
    assert fields["visa_type"] == "経営・管理"
    # 名義人は親会社（法人保証人）代表であり、申込法人の代表者とは別人
    assert fields["name"] != case.company.representative_name


def test_build_answer_guarantor_equals_applicant():
    """TC-1-095 保証人=本人: 申込者と連帯保証人が同一人物として answer に出る。"""
    case = load_case_from_jsonl("CASE-000060")
    fields = build_answer(case, "rental_application_individual", "standard")["fields"]
    assert fields["name"] == fields["guarantor_name"] == "山本 大輔"
    assert fields["birth_date"] == fields["guarantor_birth_date"]
    assert fields["current_address"] == fields["guarantor_current_address"]
    assert fields["guarantor_relationship"] == "本人（申込者と同一）"


SOLE_PROPRIETOR_CORPORATE_FORM_CASE: dict = {
    "case_id": "CASE-TEST-SP-001",
    "applicant_type": "sole_proprietor",
    "applicant": {
        "name": "テスト 事業",
        "kana": "テスト ジギョウ",
        "birth_date": "1983年03月22日",
        "age": "43",
        "gender": "男性",
        "postal_code": "166-0003",
        "current_address": "東京都杉並区テスト南5-6-7",
        "phone": "090-0000-0001",
        "email": "sp@example.test",
        "id_document_type": "運転免許証",
    },
    "employment": {
        "employer_name": "テスト木工デザイン",
        "employer_address": "東京都杉並区テスト南5-6-7",
        "years_employed": "8年",
        "annual_income": "6,200,000円",
    },
    "company": {
        "company_name": "テスト木工デザイン",
        "company_kana": "テストモッコウデザイン",
        "business_description": "オーダー家具の設計・製作",
        "employee_count": "1名",
    },
    "income": {"annual_income": "6,200,000円", "income_type": "事業所得（個人事業主）"},
    "emergency_contact": {
        "name": "テスト 花子",
        "relation": "姉",
        "phone": "090-0000-0002",
        "postal_code": "166-0004",
        "address": "東京都杉並区テスト北1-2-3",
    },
    "documents": [{"document_type": "rental_application_corporate", "variant": "sole_proprietor"}],
}


def test_build_answer_corporate_sole_proprietor_has_applicant_block():
    """TC-1-092 個人が法人様式で申込。

    商号は屋号（法人格なし）で、《申込者》欄の本人情報が answer に出る。
    """
    case = Case.model_validate(SOLE_PROPRIETOR_CORPORATE_FORM_CASE)
    fields = build_answer(case, "rental_application_corporate", "sole_proprietor")["fields"]
    # 商号＝屋号。法人格（株式会社等）を含まず、法人固有項目は空（個人事業のため存在しない）
    assert fields["company_name"] == "テスト木工デザイン"
    assert "株式会社" not in fields["company_name"]
    assert fields["corporate_number"] is None
    assert fields["established_date"] is None
    assert fields["capital"] is None
    assert fields["representative_name"] is None
    # 《申込者（賃借人）》欄＝実態は個人
    assert fields["applicant_name"] == "テスト 事業"
    assert fields["applicant_birth_date"] == "1983年03月22日"
    assert fields["applicant_current_address"] == "東京都杉並区テスト南5-6-7"
    assert fields["applicant_occupation"] == "自営業"
    assert fields["applicant_residence_type"] == "賃貸"
    assert fields["applicant_annual_income"] == "6,200,000円"
    assert fields["trade_name"] == "テスト木工デザイン"
    assert fields["years_in_business"] == "8年"
    assert fields["move_in_reason"] == "新規開業"
    assert fields["application_category"] == "新規申込者"


def test_build_answer_corporate_sole_proprietor_application_category_overridable():
    """sole_proprietor variant も case.property.application_category で既存入居者に切替できる。"""
    data = {
        **SOLE_PROPRIETOR_CORPORATE_FORM_CASE,
        "property": {"application_category": "既存入居者"},
    }
    case = Case.model_validate(data)
    fields = build_answer(case, "rental_application_corporate", "sole_proprietor")["fields"]
    assert fields["application_category"] == "既存入居者"
    assert fields["application_kind"] == "事務所"
    assert fields["emergency_contact_name"] == "テスト 花子"


def test_build_answer_corporate_other_variants_have_no_applicant_block():
    """他の法人様式（standard/office）の正解 JSON は従来どおり《申込者》欄を持たない。"""
    case = Case.model_validate(SOLE_PROPRIETOR_CORPORATE_FORM_CASE)
    for variant in ("standard", "office"):
        fields = build_answer(case, "rental_application_corporate", variant)["fields"]
        assert "applicant_name" not in fields
        assert "trade_name" not in fields


# --- Issue #79: 多言語（韓国語）決算書・資金エビデンス対応 ---


def _kr_detail_case(**overrides) -> Case:
    base = {
        "case_id": "CASE-TEST-KR-DETAIL",
        "applicant_type": "corporate",
        "company": {"company_name": "주식회사 샘플테크코리아"},
        "financials_detail": {
            "fiscal_year": "2025년 사업연도",
            "fiscal_period": "2025.01.01 ~ 2025.12.31",
            "unit_label": "원",
            "balance_sheet_rows": [
                {"label": "현금및현금성자산", "code": "011", "amount": "350,000,000"},
                {
                    "label": "자산총계",
                    "code": "099",
                    "amount": "1,700,000,000",
                    "key": "total_assets",
                    "emphasis": "total",
                },
            ],
            "profit_loss_rows": [
                {"label": "매출액", "code": "311", "amount": "2,400,000,000", "key": "sales"},
            ],
            "source_currency": "KRW",
            "unit_multiplier": 1,
            "accounting_standard": "NTS_STANDARD",
        },
        "documents": [{"document_type": "financial_statement", "variant": "kr_nts_standard"}],
    }
    base.update(overrides)
    return Case.model_validate(base)


def test_build_answer_financial_statement_detail_row_variant_expands_flat_keys():
    """明細行の key から導出した正規キーが正解JSONへフラット展開される。"""
    case = _kr_detail_case()
    fields = build_answer(case, "financial_statement", "kr_nts_standard")["fields"]
    assert fields["company_name"] == "주식회사 샘플테크코리아"
    assert fields["total_assets"] == "1,700,000,000"
    assert fields["sales"] == "2,400,000,000"
    # 行データ自体（code/label/contra を含む）もそのまま保持される
    assert fields["balance_sheet_rows"][0]["code"] == "011"
    assert fields["balance_sheet_rows"][0]["label"] == "현금및현금성자산"
    assert fields["balance_sheet_rows"][0]["contra"] is False
    assert fields["profit_loss_rows"][0]["key"] == "sales"
    # 通貨・単位・会計基準メタ情報（unit_label含む）
    assert fields["expected_foreign_currency_flag"] is True
    assert fields["source_currency"] == "KRW"
    assert fields["unit_label"] == "원"
    assert fields["accounting_standard"] == "NTS_STANDARD"


def test_build_answer_kr_sme_simple_keeps_both_printed_label_and_canonical_key():
    """表記ゆれケースでも印字labelと正規キーの両方が正解JSONに保持される。"""
    case = _kr_detail_case(
        financials_detail={
            "balance_sheet_rows": [
                {
                    "label": "자산 합계",
                    "amount": "1,700,000,000",
                    "key": "total_assets",
                    "emphasis": "total",
                },
            ],
            "profit_loss_rows": [
                {"label": "매출", "amount": "2,400,000,000", "key": "sales"},
            ],
        },
        documents=[{"document_type": "financial_statement", "variant": "kr_sme_simple"}],
    )
    fields = build_answer(case, "financial_statement", "kr_sme_simple")["fields"]
    # 正規キーで採点できる
    assert fields["total_assets"] == "1,700,000,000"
    assert fields["sales"] == "2,400,000,000"
    # 印字labelの表記ゆれも保持される
    assert fields["balance_sheet_rows"][0]["label"] == "자산 합계"
    assert fields["profit_loss_rows"][0]["label"] == "매출"


def test_build_answer_kr_kgaap_bracket_minus_keeps_contra_flag():
    """控除科目（contra）フラグと括弧マイナス金額がそのまま正解JSONに保持される。"""
    case = _kr_detail_case(
        financials_detail={
            "balance_sheet_rows": [
                {"label": "매출채권", "amount": "450,000,000"},
                {"label": "대손충당금", "amount": "(15,000,000)", "contra": True},
                {
                    "label": "자산총계",
                    "amount": "1,255,000,000",
                    "key": "total_assets",
                    "emphasis": "total",
                },
            ],
            "profit_loss_rows": [],
        },
        documents=[
            {"document_type": "financial_statement", "variant": "kr_kgaap_bracket_minus"}
        ],
    )
    fields = build_answer(case, "financial_statement", "kr_kgaap_bracket_minus")["fields"]
    assert fields["balance_sheet_rows"][1]["label"] == "대손충당금"
    assert fields["balance_sheet_rows"][1]["contra"] is True
    assert fields["balance_sheet_rows"][1]["amount"] == "(15,000,000)"
    assert fields["total_assets"] == "1,255,000,000"


def test_build_answer_kr_kifrs_audited_multi_period_has_periods_and_meta():
    """K-IFRS2期比較は periods 配列と通貨・単位・会計基準メタ情報を持つ。"""
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-IFRS",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플글로벌코리아"},
            "financials_multi": [
                {
                    "fiscal_year": "제25기(2025)",
                    "sales": "125,400,000",
                    "source_currency": "KRW",
                    "unit_multiplier": 1000,
                    "accounting_standard": "K-IFRS",
                },
                {
                    "fiscal_year": "제24기(2024)",
                    "sales": "108,700,000",
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
    fields = build_answer(case, "financial_statement", "kr_kifrs_audited")["fields"]
    assert [p["fiscal_year"] for p in fields["periods"]] == ["제25기(2025)", "제24기(2024)"]
    assert fields["expected_foreign_currency_flag"] is True
    assert fields["source_currency"] == "KRW"
    assert fields["unit_multiplier"] == 1000
    assert fields["accounting_standard"] == "K-IFRS"


def test_build_answer_bank_balance_certificate_amount_in_words_conditional():
    """amount_in_words は設定時のみ正解JSONに出力される。"""
    case = Case.model_validate(
        {
            "case_id": "CASE-TEST-KR-BAL",
            "applicant_type": "corporate",
            "company": {"company_name": "주식회사 샘플무역코리아"},
            "bank_balance_certificate": {
                "account_holder": "주식회사 샘플무역코리아",
                "balance_amount": "1,245,600,000원",
                "source_currency": "KRW",
                "amount_in_words": "금 일십이억사천오백육십만원정",
            },
            "documents": [
                {"document_type": "bank_balance_certificate", "variant": "kr_standard"}
            ],
        }
    )
    fields = build_answer(case, "bank_balance_certificate", "kr_standard")["fields"]
    assert fields["amount_in_words"] == "금 일십이억사천오백육십만원정"


def test_build_answer_bank_balance_certificate_amount_in_words_omitted_when_unset(
    individual_extended_case,
):
    """amount_in_words 未設定の既存ケースは正解JSONにキーが出ない（既存ケースへの無影響確認）。"""
    fields = build_answer(
        individual_extended_case, "bank_balance_certificate", "standard"
    )["fields"]
    assert "amount_in_words" not in fields
