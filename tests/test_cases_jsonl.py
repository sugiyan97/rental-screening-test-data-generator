"""input/cases.jsonl に収録されたケースの整合性テスト。

本人確認の特殊属性ケース（在留期限が1か月内・70歳以上）は、期限接近アラート／
高齢アラートの検証用データなので、日付の整合性をテストで固定しておく。
"""

import re
from datetime import date
from pathlib import Path

import pytest

from rental_pdf_generator.answer_builder import build_answer
from rental_pdf_generator.cli import _load_cases

CASES_PATH = Path(__file__).resolve().parents[1] / "input" / "cases.jsonl"

# 既存ケースの日付が基準としている「今日」
BASE_DATE = date(2026, 7, 29)


def _parse_jp_date(value: str) -> date:
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", value)
    assert m is not None, f"日付形式が不正: {value}"
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def _age_on(birth_date: str, on: date) -> int:
    b = _parse_jp_date(birth_date)
    return on.year - b.year - ((on.month, on.day) < (b.month, b.day))


@pytest.fixture(scope="module")
def cases_by_id() -> dict:
    cases = _load_cases(CASES_PATH, None)
    return {case.case_id: case for case in cases}


def test_all_cases_are_valid_models(cases_by_id):
    lines = [
        line for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
    # _load_cases は検証に失敗した行をスキップするため、行数と一致すれば全行が有効
    assert len(cases_by_id) == len(lines)


def test_case_ids_are_unique():
    ids = [
        line.split('"case_id": "', 1)[1].split('"', 1)[0]
        for line in CASES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(ids) == len(set(ids))


# --- CASE-000052: 有効期限が1か月内の在留カード（期限接近アラート） -------------


def test_case_000052_residence_card_expiry_within_one_month(cases_by_id):
    case = cases_by_id["CASE-000052"]
    expiry = _parse_jp_date(case.identity_document.expiry)
    remaining = (expiry - BASE_DATE).days
    assert expiry == date(2026, 8, 20)
    assert remaining == 22, "在留期限は基準日から残 22 日（1か月以内かつ失効前）"
    assert 0 < remaining < 31


def test_case_000052_is_foreign_worker_with_residence_card(cases_by_id):
    case = cases_by_id["CASE-000052"]
    assert case.applicant_type == "individual"
    assert case.identity_document.nationality == "ベトナム"
    assert case.identity_document.visa_type == "技術・人文知識・国際業務"
    assert case.identity_document.residence_card_number == "BB98765432EF"
    variants = {(d.document_type, d.variant) for d in case.documents}
    assert ("identity_document", "residence_card") in variants
    assert ("income_certificate", "salary_certificate") in variants
    assert ("rental_application_individual", "standard") in variants


def test_case_000052_answer_contains_residence_card_expiry(cases_by_id):
    case = cases_by_id["CASE-000052"]
    answer = build_answer(case, "identity_document", "residence_card")
    fields = answer["fields"]
    assert fields["expiry"] == "2026年08月20日"
    assert fields["period_of_stay"] == "1年（満了日：2026年08月20日）"
    assert fields["residence_card_number"] == "BB98765432EF"
    assert fields["birth_date"] == case.applicant.birth_date
    assert fields["name"] == case.applicant.name


def test_case_000052_card_issue_date_matches_one_year_period(cases_by_id):
    case = cases_by_id["CASE-000052"]
    issued = _parse_jp_date(case.identity_document.issue_date)
    expiry = _parse_jp_date(case.identity_document.expiry)
    # 在留期間「1年」＝ 交付日から約1年後が満了日
    assert 360 <= (expiry - issued).days <= 370


def test_case_000052_applicant_age_matches_birth_date(cases_by_id):
    case = cases_by_id["CASE-000052"]
    assert case.applicant.age == str(_age_on(case.applicant.birth_date, BASE_DATE))


# --- CASE-000053: 70歳以上の申込者の本人確認（高齢アラート） -------------------


def test_case_000053_applicant_is_over_70(cases_by_id):
    case = cases_by_id["CASE-000053"]
    age = _age_on(case.applicant.birth_date, BASE_DATE)
    assert case.applicant.birth_date == "1952年03月14日"
    assert age == 74
    assert age >= 70
    assert case.applicant.age == str(age)


def test_case_000053_identity_document_birth_date_is_consistent(cases_by_id):
    case = cases_by_id["CASE-000053"]
    answer = build_answer(case, "identity_document", "drivers_license")
    fields = answer["fields"]
    # 免許証に印字される生年月日は申込書と一致していなければならない
    assert fields["birth_date"] == case.applicant.birth_date == "1952年03月14日"
    assert fields["license_number"] == "456789012345"
    # 免許証自体は失効していない（期限接近アラートを誤発火させない）
    assert _parse_jp_date(fields["expiry"]) > BASE_DATE


def test_case_000053_income_is_salary_certificate_of_contract_employee(cases_by_id):
    case = cases_by_id["CASE-000053"]
    answer = build_answer(case, "income_certificate", "salary_certificate")
    fields = answer["fields"]
    assert fields["income_type"] == "給与所得（嘱託契約）"
    assert fields["annual_income"] == "3,600,000円"
    assert fields["income_year"] == "2025年"
    assert _parse_jp_date(fields["certificate_expiry"]) > BASE_DATE


def test_case_000053_guarantor_is_child_and_younger(cases_by_id):
    case = cases_by_id["CASE-000053"]
    assert case.guarantor.relationship == "長男"
    guarantor_age = _age_on(case.guarantor.birth_date, BASE_DATE)
    assert case.guarantor.age == str(guarantor_age)
    assert guarantor_age < _age_on(case.applicant.birth_date, BASE_DATE)
    variants = {(d.document_type, d.variant) for d in case.documents}
    assert ("guarantor_income_certificate", "salary_certificate") in variants
    assert ("guarantor_identity_document", "drivers_license") in variants


# --- Issue #37: 申込者特定 異常系ケース（CASE-000057〜060）の整合性 ---


def test_case_000057_is_joint_application(cases_by_id):
    """共同申込: 申込者2名（applicant と applicant_2）が別人で存在する。"""
    case = cases_by_id["CASE-000057"]
    assert case.applicant_type == "individual"
    assert case.applicant is not None and case.applicant_2 is not None
    assert case.applicant.name != case.applicant_2.name
    assert case.applicant.age == str(_age_on(case.applicant.birth_date, BASE_DATE))
    assert case.applicant_2.age == str(_age_on(case.applicant_2.birth_date, BASE_DATE))
    variants = {(d.document_type, d.variant) for d in case.documents}
    assert ("rental_application_individual", "joint_application") in variants


def test_case_000058_is_joint_representative(cases_by_id):
    """共同代表: 代表者2名（representative_ と representative_2_）が別人で存在する。"""
    case = cases_by_id["CASE-000058"]
    assert case.applicant_type == "corporate"
    c = case.company
    assert c.representative_name and c.representative_2_name
    assert c.representative_name != c.representative_2_name
    assert c.representative_age == str(_age_on(c.representative_birth_date, BASE_DATE))
    assert c.representative_2_age == str(_age_on(c.representative_2_birth_date, BASE_DATE))
    variants = {(d.document_type, d.variant) for d in case.documents}
    assert ("rental_application_corporate", "joint_representative") in variants


def test_case_000059_parent_company_representative_is_foreign(cases_by_id):
    """外国籍の親会社（法人保証人）代表: 国籍が日本以外で在留カードを添付する。"""
    case = cases_by_id["CASE-000059"]
    pc = case.parent_company
    assert pc.representative_nationality == "中国"
    assert pc.representative_name == "リー・ジャンウェイ"
    assert case.parent_company_identity_document is not None
    assert case.parent_company_identity_document.residence_card_number == "AB12345678CD"
    # 在留カードは失効前（期限接近アラートを誤発火させない）
    assert _parse_jp_date(case.parent_company_identity_document.expiry) > BASE_DATE
    variants = {(d.document_type, d.variant) for d in case.documents}
    assert ("parent_company_identity_document", "residence_card") in variants
    # 申込法人の代表者は日本人のまま（外国籍なのは親会社代表のみ）
    assert case.company.representative_name != pc.representative_name


def test_case_000060_guarantor_is_same_as_applicant(cases_by_id):
    """保証人=本人: 申込者と連帯保証人が同一人物（氏名・生年月日・住所が一致）。"""
    case = cases_by_id["CASE-000060"]
    a, g = case.applicant, case.guarantor
    assert a is not None and g is not None
    assert a.name == g.name
    assert a.birth_date == g.birth_date
    assert a.current_address == g.current_address
    assert g.relationship == "本人（申込者と同一）"
