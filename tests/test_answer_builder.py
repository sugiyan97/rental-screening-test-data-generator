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


def test_build_answer_individual(individual_case):
    answer = build_answer(individual_case, "rental_application_individual", "standard")
    assert answer["case_id"] == individual_case.case_id
    assert answer["fields"]["name"] == "テスト 花子"
    assert answer["fields"]["employer_name"] == "テスト株式会社"
    assert "emergency_contact_name" in answer["fields"]


def test_build_answer_income(individual_case):
    answer = build_answer(individual_case, "income_certificate", "salary_certificate")
    assert answer["fields"]["name"] == "テスト 花子"
    assert answer["fields"]["annual_income"] == "4,000,000円"
    assert answer["fields"]["issue_date"] == "2026年05月01日"


def test_build_answer_none_fields_when_no_data(corporate_case):
    corporate_case.financials = None
    answer = build_answer(corporate_case, "financial_statement", "financial_summary")
    assert answer["fields"]["sales"] is None
    assert answer["fields"]["net_income"] is None


def test_build_answer_unsupported_type_raises(corporate_case):
    with pytest.raises(UnsupportedDocumentTypeError):
        build_answer(corporate_case, "unknown_document_type", "standard")
