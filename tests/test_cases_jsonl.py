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
from rental_pdf_generator.models import apply_case_overrides

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


# --- Issue #50: 事業新規（設立1年未満）で事業計画書・資金エビデンス必須 CASE-000065 ---


def test_case_000065_established_date_is_six_to_ten_months_before_base_date(cases_by_id):
    """設立日は生成時点から6〜10ヶ月前の範囲（設立1年未満の前提が崩れていないか）。"""
    case = cases_by_id["CASE-000065"]
    established = _parse_jp_date(case.company.established_date)
    days_since = (BASE_DATE - established).days
    assert 180 <= days_since <= 310, "設立日が6〜10ヶ月前の想定範囲から外れている（要再生成）"


def test_case_000065_is_new_business_with_reason_and_no_supporting_docs(cases_by_id):
    """入居理由=新規開業・開業理由記載ありで、決算書・事業計画書・資金エビデンスは未提出。"""
    case = cases_by_id["CASE-000065"]
    assert case.applicant_type == "corporate"
    assert case.property.move_in_reason == "新規開業"
    assert case.company.new_business_reason
    document_types = {d.document_type for d in case.documents}
    assert document_types.isdisjoint({"financial_statement", "business_plan", "funding_evidence"})


def test_case_000065_application_form_reflects_new_business_reason(cases_by_id):
    """申込書（office）の正解JSONに入居理由・開業理由/背景が反映されている。"""
    case = cases_by_id["CASE-000065"]
    answer = build_answer(case, "rental_application_corporate", "office")
    fields = answer["fields"]
    assert fields["move_in_reason"] == "新規開業"
    assert fields["new_business_reason"] == case.company.new_business_reason


# --- Issue #40: 再アップロード（冪等更新）検証用 value-variant CASE-000032-V2 -------


def _document(case, document_type: str):
    return next(d for d in case.documents if d.document_type == document_type)


def _answer_of(case, document_type: str) -> dict:
    """その書類の overrides を適用した状態の正解 JSON の fields を返す。"""
    doc = _document(case, document_type)
    answer = build_answer(apply_case_overrides(case, doc.overrides), doc.document_type, doc.variant)
    return answer["fields"]


def _yen(value: str) -> int:
    """'△27,400,000円' -> -27400000"""
    amount = int(re.sub(r"[^\d]", "", value))
    return -amount if value.startswith(("△", "-", "▲")) else amount


@pytest.fixture(scope="module")
def reupload_pair(cases_by_id) -> tuple:
    return cases_by_id["CASE-000032"], cases_by_id["CASE-000032-V2"]


def test_case_000032_v2_case_data_is_identical_to_round1(reupload_pair):
    """ケースデータ本体（申込者特定キーを含む全項目）は round1 と完全に同一。

    round2 で変わるのは原本書類の overrides だけ。ここが崩れると
    「同一案件への2回目アップロード」にならず冪等更新を検証できない。
    """
    round1, round2 = reupload_pair
    exclude = {"case_id", "description", "documents"}
    assert round2.model_dump(exclude=exclude) == round1.model_dump(exclude=exclude)


def test_case_000032_v2_document_set_is_identical_to_round1(reupload_pair):
    """提出書類の構成（種別・様式・形式・ラベル）は round1 と同一。"""
    round1, round2 = reupload_pair

    def spec(doc):
        return (doc.document_type, doc.variant, doc.output_format, doc.label)

    assert [spec(d) for d in round2.documents] == [spec(d) for d in round1.documents]
    assert len(round2.documents) == 15


def test_case_000032_v2_overrides_only_on_original_documents(reupload_pair):
    """値を変えるのは原本（謄本・決算書）だけ。他の書類は round1 と同一内容。"""
    _, round2 = reupload_pair
    overridden = {d.document_type for d in round2.documents if d.overrides}
    assert overridden == {"registry_certificate", "financial_statement"}


def test_case_000032_v2_registry_head_office_is_overwritten(reupload_pair):
    """謄本の本店所在地だけが round1 と異なり、他の謄本項目は不変。"""
    round1, round2 = reupload_pair
    before, after = _answer_of(round1, "registry_certificate"), _answer_of(
        round2, "registry_certificate"
    )
    assert after["head_office_address"] == "東京都千代田区神田駿河台2-9-9 サンプル駿河台ビル8階"
    assert after["head_office_address"] != before["head_office_address"]
    # 同一案件と判定させるキー（商号・会社法人等番号）は不変
    assert after["company_name"] == before["company_name"]
    assert after["corporate_number"] == before["corporate_number"]
    changed = {k for k in before if before[k] != after.get(k)}
    assert changed == {"head_office_address"}


def test_case_000032_v2_registry_records_transfer_date(reupload_pair):
    """本店移転の登記日が原本に記録され、設立日より後になっている。"""
    round1, round2 = reupload_pair
    after = _answer_of(round2, "registry_certificate")
    assert after["head_office_transfer_date"] == "2026年07月10日"
    assert _parse_jp_date(after["head_office_transfer_date"]) > _parse_jp_date(
        after["established_date"]
    )
    assert _parse_jp_date(after["head_office_transfer_date"]) <= BASE_DATE
    # round1 の謄本は本店移転していないため移転日を持たない
    assert "head_office_transfer_date" not in _answer_of(round1, "registry_certificate")


def test_case_000032_v2_application_keeps_round1_head_office(reupload_pair):
    """申込書は round1 と同一（旧本店所在地のまま）。

    謄本の新住所で上書きされ、申込書由来の値は保護される——という
    原本優先上書きの検証は、申込書側が旧値のままでなければ成立しない。
    """
    round1, round2 = reupload_pair
    before = _answer_of(round1, "rental_application_corporate")
    after = _answer_of(round2, "rental_application_corporate")
    assert after == before
    assert after["head_office_address"] == "東京都文京区本郷7-3-1"
    assert after["head_office_address"] != _answer_of(round2, "registry_certificate")[
        "head_office_address"
    ]


def test_case_000032_v2_financial_amounts_are_overwritten(reupload_pair):
    """決算書は同一決算期のまま主要科目の金額だけが round1 と異なる。"""
    round1, round2 = reupload_pair
    before = _answer_of(round1, "financial_statement")
    after = _answer_of(round2, "financial_statement")
    assert after["fiscal_year"] == before["fiscal_year"] == "2026年度（第1期）"
    assert after["company_name"] == before["company_name"]
    changed = {k for k in before if before[k] != after.get(k)}
    assert changed == {
        "sales",
        "operating_income",
        "ordinary_income",
        "net_income",
        "total_assets",
        "net_assets",
    }
    assert after["sales"] == "12,600,000円"
    assert after["net_income"] == "△26,900,000円"
    assert after["total_assets"] == "168,100,000円"


def test_case_000032_v2_financials_stay_consistent(reupload_pair):
    """変更後の決算数値も 資産合計 = 負債合計 + 純資産合計 が成立する。"""
    round1, round2 = reupload_pair
    after = _answer_of(round2, "financial_statement")
    assert _yen(after["total_assets"]) == _yen(after["total_liabilities"]) + _yen(
        after["net_assets"]
    )
    # 損失が縮小した分だけ純資産が増える（払込資本は round1 と同額）
    before = _answer_of(round1, "financial_statement")
    loss_improvement = _yen(after["net_income"]) - _yen(before["net_income"])
    assert loss_improvement == 3_600_000
    assert _yen(after["net_assets"]) - _yen(before["net_assets"]) == loss_improvement
    # 第1期の新設スタートアップなので当期純損失であること自体は変わらない
    assert _yen(after["net_income"]) < 0
