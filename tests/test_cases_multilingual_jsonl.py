"""input/cases_multilingual.jsonl（Issue #76: 英語 / Issue #79: 韓国語 多言語決算書・
資金エビデンス対応）の整合性テスト。

日本語65ケース（input/cases.jsonl）とは分離した多言語専用の入力ファイル。
真陽性（外貨表記のケースは expected_foreign_currency_flag=true）・
真陰性（外国親会社が関与してもJPY表記なら false）の両方を検証する。
"""

from pathlib import Path

import pytest

from rental_pdf_generator.answer_builder import build_answer
from rental_pdf_generator.cli import _load_cases
from rental_pdf_generator.generator import CasePdfGenerator
from rental_pdf_generator.models import Financials

CASES_PATH = Path(__file__).resolve().parents[1] / "input" / "cases_multilingual.jsonl"

# Issue #79: 韓国語ケースはDOCX/PPTXがハングルグリフを持たない Yu Gothic 埋め込みのため、
# pdf 限定で運用する（output_format 未指定 = pdf）。
_KOREAN_CASE_IDS = {
    "CASE-ML-000017",
    "CASE-ML-000018",
    "CASE-ML-000019",
    "CASE-ML-000020",
    "CASE-ML-000021",
    "CASE-ML-000022",
    "CASE-ML-000023",
}


@pytest.fixture(scope="module")
def cases_by_id() -> dict:
    cases = _load_cases(CASES_PATH, None)
    return {case.case_id: case for case in cases}


def test_all_multilingual_cases_are_valid_models(cases_by_id):
    lines = [line for line in CASES_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]
    # _load_cases は検証に失敗した行をスキップするため、行数と一致すれば全行が有効
    assert len(cases_by_id) == len(lines)
    assert len(cases_by_id) == 14


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
        # Issue #79: 韓国語決算書・資金エビデンス対応
        ("CASE-ML-000017", "financial_statement", "kr_nts_standard"),
        ("CASE-ML-000018", "financial_statement", "kr_kifrs_audited"),
        ("CASE-ML-000019", "financial_statement", "kr_sme_simple"),
        ("CASE-ML-000020", "financial_statement", "kr_kgaap_bracket_minus"),
        ("CASE-ML-000021", "bank_balance_certificate", "kr_standard"),
        ("CASE-ML-000022", "time_deposit_statement", "kr_standard"),
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


def test_case_ml_000023_is_true_negative_jpy_case(cases_by_id):
    """Issue #79: 韓国法人の在日拠点向け内部決算（JPY明示）は真陰性になる。

    #76のCASE-ML-000007（外国親会社関与だがJPY未明示）とは異なり、
    source_currency: "JPY" を明示した上での false を検証する。
    """
    case = cases_by_id["CASE-ML-000023"]
    assert case.financials_detail.source_currency == "JPY"
    answer = build_answer(case, "financial_statement", "kr_sme_simple")
    assert answer["fields"]["expected_foreign_currency_flag"] is False
    # source_currency を明示しているため（#76 CASE-ML-000007の「未設定」経路とは異なり）、
    # キー自体は出力されるが値はJPYのまま、flag だけが false になる。
    assert answer["fields"]["source_currency"] == "JPY"


def test_kr_financials_detail_row_keys_are_subset_of_financials_fields(cases_by_id):
    """financials_detail の全 key が Financials.model_fields のサブセット（タイポ防止）。"""
    valid_keys = set(Financials.model_fields.keys())
    checked_any = False
    for case_id in _KOREAN_CASE_IDS:
        case = cases_by_id.get(case_id)
        if case is None or case.financials_detail is None:
            continue
        rows = [
            *case.financials_detail.balance_sheet_rows,
            *case.financials_detail.profit_loss_rows,
        ]
        for row in rows:
            if row.key is not None:
                checked_any = True
                assert row.key in valid_keys, f"{case_id}: 未知のkey '{row.key}'"
    assert checked_any


def test_korean_cases_are_pdf_only(cases_by_id):
    """Issue #79: 韓国語ケースはDOCX/PPTXがハングルグリフを持たないため pdf 限定で運用する。"""
    checked_any = False
    for case_id in _KOREAN_CASE_IDS:
        case = cases_by_id[case_id]
        for doc in case.documents:
            checked_any = True
            assert doc.output_format == "pdf"
    assert checked_any


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
