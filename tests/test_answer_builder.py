import pytest

from rental_pdf_generator.answer_builder import UnsupportedDocumentTypeError, build_answer


def test_build_answer_corporate(corporate_case):
    answer = build_answer(corporate_case, "rental_application_corporate", "standard")
    assert answer["case_id"] == corporate_case.case_id
    assert answer["document_type"] == "rental_application_corporate"
    assert answer["variant"] == "standard"
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["corporate_number"] == "9999999999999"
    assert "property_name" in answer["fields"]
    assert "representative_name" in answer["fields"]


def test_build_answer_registry(corporate_case):
    answer = build_answer(corporate_case, "registry_certificate", "registry_table")
    assert answer["case_id"] == corporate_case.case_id
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["corporate_number"] == "9999999999999"
    assert "established_date" in answer["fields"]
    assert "capital" in answer["fields"]
    assert "annual_income" not in answer["fields"]


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


def test_build_answer_business_license_application(corporate_extended_case):
    answer = build_answer(
        corporate_extended_case, "business_license_application", "restaurant"
    )
    assert answer["fields"]["company_name"] == "テスト商事株式会社"
    assert answer["fields"]["applicant_name"] == "テスト商事株式会社"
    assert answer["fields"]["receipt_number"] == "TEST-AP-99999"
    assert answer["fields"]["status_note"] == "申請中につき許可書未交付"
    assert answer["fields"]["issuing_authority"] == "テスト保健所"


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
