import pytest

from rental_pdf_generator.models import Case

CORPORATE_CASE_DATA: dict = {
    "case_id": "CASE-TEST-001",
    "applicant_type": "corporate",
    "company": {
        "company_name": "テスト商事株式会社",
        "company_kana": "テストショウジカブシキガイシャ",
        "corporate_number": "9999999999999",
        "head_office_address": "東京都千代田区テスト町1-1-1",
        "representative_name": "テスト 太郎",
        "representative_birth_date": "1980年01月01日",
        "representative_address": "東京都千代田区テスト町2-2-2",
        "phone": "03-9999-0001",
        "email": "test@example.test",
        "established_date": "2020年01月01日",
        "capital": "5,000,000円",
        "business_description": "テスト用事業の運営",
        "employee_count": "5名",
        "fiscal_year_end": "12月31日",
    },
    "property": {
        "property_name": "テストマンション",
        "room_number": "101",
        "property_address": "東京都新宿区テスト1-1-1",
        "rent": "100,000円",
        "management_fee": "5,000円",
        "desired_move_in_date": "2026年07月01日",
        "usage_purpose": "社宅",
    },
    "financials": {
        "fiscal_year": "2025年度",
        "sales": "50,000,000円",
        "operating_income": "5,000,000円",
        "ordinary_income": "4,800,000円",
        "net_income": "3,000,000円",
        "total_assets": "20,000,000円",
        "total_liabilities": "8,000,000円",
        "net_assets": "12,000,000円",
    },
    "business_plan": {
        "plan_period": "2026年度",
        "business_overview": "テスト事業の拡大を計画しています。",
        "revenue_plan": "新規顧客の獲得により売上を20%増加予定。",
        "hiring_plan": "エンジニア2名採用予定。",
        "risk_factors": "市場競争の激化。",
    },
    "documents": [
        {"document_type": "rental_application_corporate", "variant": "standard"},
        {"document_type": "registry_certificate", "variant": "registry_table"},
        {"document_type": "financial_statement", "variant": "financial_summary"},
        {"document_type": "business_plan", "variant": "narrative"},
    ],
}

INDIVIDUAL_CASE_DATA: dict = {
    "case_id": "CASE-TEST-002",
    "applicant_type": "individual",
    "applicant": {
        "name": "テスト 花子",
        "kana": "テスト ハナコ",
        "birth_date": "1995年06月15日",
        "age": "30",
        "gender": "女性",
        "current_address": "東京都杉並区テスト1-1-1",
        "phone": "090-9999-0002",
        "email": "hanako@example.test",
        "id_document_type": "運転免許証",
    },
    "employment": {
        "employer_name": "テスト株式会社",
        "department": "総務部",
        "job_title": "主任",
        "years_employed": "5年",
        "annual_income": "4,000,000円",
        "employer_phone": "03-9999-0003",
        "employer_address": "東京都渋谷区テスト2-2-2",
    },
    "property": {
        "property_name": "テストアパート",
        "room_number": "203",
        "property_address": "東京都世田谷区テスト3-3-3",
        "rent": "80,000円",
        "management_fee": "5,000円",
        "desired_move_in_date": "2026年08月01日",
        "usage_purpose": "居住用",
    },
    "emergency_contact": {
        "name": "テスト 一郎",
        "relation": "父",
        "phone": "090-9999-0004",
        "address": "埼玉県さいたま市テスト4-4-4",
    },
    "income": {
        "income_year": "2025年",
        "annual_income": "4,000,000円",
        "monthly_income": "333,000円",
        "income_type": "給与所得",
        "issuer_name": "テスト株式会社",
        "issue_date": "2026年05月01日",
        "base_salary": "270,000円",
        "overtime_allowance": "30,000円",
        "commuting_allowance": "10,000円",
        "bonus": "600,000円",
        "certificate_expiry": "2026年08月01日",
    },
    "guarantor": {
        "name": "テスト 一郎",
        "kana": "テスト イチロウ",
        "birth_date": "1965年01月01日",
        "relationship": "父",
        "current_address": "埼玉県さいたま市テスト4-4-4",
        "phone": "090-9999-0004",
        "employer_name": "テスト製造株式会社",
        "annual_income": "6,000,000円",
    },
    "identity_document": {
        "license_number": "999999999999",
        "expiry": "2028年06月15日",
        "issue_date": "2018年06月15日",
        "issue_place": "東京都",
    },
    "documents": [
        {"document_type": "rental_application_individual", "variant": "standard"},
        {"document_type": "income_certificate", "variant": "salary_certificate"},
        {"document_type": "identity_document", "variant": "drivers_license"},
    ],
}


@pytest.fixture
def corporate_case_data() -> dict:
    return CORPORATE_CASE_DATA.copy()


@pytest.fixture
def corporate_case() -> Case:
    return Case.model_validate(CORPORATE_CASE_DATA)


@pytest.fixture
def individual_case_data() -> dict:
    return INDIVIDUAL_CASE_DATA.copy()


@pytest.fixture
def individual_case() -> Case:
    return Case.model_validate(INDIVIDUAL_CASE_DATA)
