"""input/cases_multilingual.jsonl（Issue #76/#78: 多言語決算書・資金エビデンス対応）の整合性テスト。

日本語65ケース（input/cases.jsonl）とは分離した多言語専用の入力ファイル。
真陽性（外貨表記のケースは expected_foreign_currency_flag=true）・
真陰性（外国親会社が関与してもJPY表記なら false）の両方を検証する。
"""

from pathlib import Path

import pytest

from rental_pdf_generator.answer_builder import build_answer
from rental_pdf_generator.cli import _load_cases
from rental_pdf_generator.generator import CasePdfGenerator

CASES_PATH = Path(__file__).resolve().parents[1] / "input" / "cases_multilingual.jsonl"

# Issue #78 で追加した通貨曖昧性トリオ（存款证明书）。
# 同一 variant・同一「元」表記で発行銀行名だけが異なる3ケース。
_CURRENCY_AMBIGUITY_TRIO_CASE_IDS = ("CASE-ML-000013", "CASE-ML-000014", "CASE-ML-000015")


@pytest.fixture(scope="module")
def cases_by_id() -> dict:
    cases = _load_cases(CASES_PATH, None)
    return {case.case_id: case for case in cases}


def test_all_multilingual_cases_are_valid_models(cases_by_id):
    lines = [line for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    # _load_cases は検証に失敗した行をスキップするため、行数と一致すれば全行が有効
    assert len(cases_by_id) == len(lines)
    # Issue #76: 7件 + Issue #78: 9件（CASE-ML-000008〜000016）= 16件
    assert len(cases_by_id) == 16


def test_multilingual_case_ids_are_unique():
    ids = [
        line.split('"case_id": "', 1)[1].split('"', 1)[0]
        for line in CASES_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert len(ids) == len(set(ids))


@pytest.mark.parametrize(
    "case_id,document_type,variant",
    [
        ("CASE-ML-000001", "financial_statement", "us_gaap_en"),
        ("CASE-ML-000002", "financial_statement", "singapore_hk_en"),
        ("CASE-ML-000003", "financial_statement", "ifrs_consolidated_en"),
        ("CASE-ML-000004", "bank_balance_certificate", "standard_en"),
        ("CASE-ML-000005", "bank_balance_certificate", "standard_en_scan_degraded"),
        ("CASE-ML-000006", "time_deposit_statement", "standard_en"),
        # Issue #78: 中国語（本土・台湾・香港）決算書・資金エビデンス
        ("CASE-ML-000008", "financial_statement", "cn_mainland_account_style"),
        ("CASE-ML-000009", "financial_statement", "cn_taiwan_report_form"),
        ("CASE-ML-000010", "financial_statement", "cn_hk_bilingual"),
        ("CASE-ML-000011", "financial_statement", "cn_mainland_en_translated"),
        ("CASE-ML-000012", "financial_statement", "cn_taiwan_en_translated"),
        ("CASE-ML-000013", "bank_balance_certificate", "cn_mainland_deposit_certificate"),
        ("CASE-ML-000014", "bank_balance_certificate", "cn_trad_deposit_certificate"),
        ("CASE-ML-000015", "bank_balance_certificate", "cn_trad_deposit_certificate"),
        ("CASE-ML-000016", "financial_statement", "cn_mainland_account_style"),
    ],
)
def test_source_currency_cases_have_expected_foreign_currency_flag_true(
    cases_by_id, case_id, document_type, variant
):
    case = cases_by_id[case_id]
    answer = build_answer(case, document_type, variant)
    assert answer["fields"]["expected_foreign_currency_flag"] is True
    assert answer["fields"].get("source_currency")


def test_case_ml_000007_is_true_negative_jpy_case(cases_by_id):
    """外国親会社が関与していても、決算書自体がJPY表記なら真陰性（false）になる。"""
    case = cases_by_id["CASE-ML-000007"]
    answer = build_answer(case, "parent_company_financial_statement", "financial_summary")
    assert answer["fields"]["expected_foreign_currency_flag"] is False
    assert "source_currency" not in answer["fields"]


def test_currency_ambiguity_trio_has_three_distinct_source_currencies(cases_by_id):
    """通貨曖昧性トリオ（存款证明书）は CNY/TWD/HKD の3通りの source_currency を持つ。"""
    currencies = {
        cases_by_id[case_id].bank_balance_certificate.source_currency
        for case_id in _CURRENCY_AMBIGUITY_TRIO_CASE_IDS
    }
    assert currencies == {"CNY", "TWD", "HKD"}


def test_currency_ambiguity_trio_uses_same_variant_and_wording_for_traditional_pair(cases_by_id):
    """CASE-ML-000014（TWD）とCASE-ML-000015（HKD）は同一variant・同一「元」表記の繁体字テンプレートを
    使い、発行銀行名だけが異なる（通貨判別の手がかりを銀行名だけに絞る設計）。"""
    twd_case = cases_by_id["CASE-ML-000014"]
    hkd_case = cases_by_id["CASE-ML-000015"]
    assert twd_case.documents[0].variant == hkd_case.documents[0].variant == (
        "cn_trad_deposit_certificate"
    )
    assert (
        twd_case.bank_balance_certificate.balance_amount
        == hkd_case.bank_balance_certificate.balance_amount
    )
    assert (
        twd_case.bank_balance_certificate.bank_name
        != hkd_case.bank_balance_certificate.bank_name
    )


def test_all_multilingual_cases_use_pdf_output_format_only(cases_by_id):
    """多言語ケースは output_format 未指定（= pdf）のみで運用する
    （DOCX/PPTX 用の _JP_FONT ハードコード問題を踏まないためのガード）。"""
    for case in cases_by_id.values():
        for document in case.documents:
            assert document.output_format == "pdf", (
                f"{case.case_id} の {document.document_type}/{document.variant} が "
                f"pdf 以外の output_format ({document.output_format}) を指定している"
            )


def test_multilingual_cases_generate_end_to_end(cases_by_id, tmp_path):
    """P5: 生成→answers突合の一連が既存フローで回ることを確認するE2Eスモークテスト。"""
    generator = CasePdfGenerator(output_dir=tmp_path)
    for case in cases_by_id.values():
        meta = generator.generate(case)
        case_dir = tmp_path / case.case_id
        assert (case_dir / "case_meta.json").exists()
        assert len(meta["generated_documents"]) == len(case.documents)
        for entry in meta["generated_documents"]:
            assert (case_dir / entry["answer"]).exists()
