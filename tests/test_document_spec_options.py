"""DocumentSpec の pdf_password / label / overrides（異常ファイル生成用オプション）のテスト。"""

import json

import pikepdf
import pytest

from rental_pdf_generator.generator import CasePdfGenerator, document_stem
from rental_pdf_generator.models import (
    Case,
    DocumentSpec,
    apply_case_overrides,
    deep_merge,
)
from rental_pdf_generator.renderers import PdfPasswordNotSupportedError

PASSWORD = "cosoji-test-2026"


def _case_with_documents(base_case: Case, case_id: str, documents: list[DocumentSpec]) -> Case:
    case = base_case.model_copy(deep=True)
    case.case_id = case_id
    case.documents = documents
    return case


# --- document_stem -------------------------------------------------------


def test_document_stem_without_label():
    spec = DocumentSpec(document_type="rental_application_individual", variant="standard")
    assert document_stem(spec) == "rental_application_individual_standard"


def test_document_stem_with_label():
    spec = DocumentSpec(
        document_type="rental_application_individual",
        variant="standard",
        label="applicant_a",
    )
    assert document_stem(spec) == "rental_application_individual_standard_applicant_a"


# --- deep_merge / apply_case_overrides -----------------------------------


def test_deep_merge_merges_nested_dicts():
    base = {"applicant": {"name": "A", "phone": "090-0000-0000"}, "top": 1}
    merged = deep_merge(base, {"applicant": {"name": "B"}, "top": 2})
    assert merged == {"applicant": {"name": "B", "phone": "090-0000-0000"}, "top": 2}
    # 元の dict は変更しない
    assert base["applicant"]["name"] == "A"


def test_deep_merge_replaces_non_dict_values():
    merged = deep_merge({"documents": [1, 2]}, {"documents": [3]})
    assert merged == {"documents": [3]}


def test_apply_case_overrides_without_overrides_returns_same_case(individual_case):
    assert apply_case_overrides(individual_case, None) is individual_case
    assert apply_case_overrides(individual_case, {}) is individual_case


def test_apply_case_overrides_keeps_unspecified_fields(individual_case):
    overridden = apply_case_overrides(individual_case, {"applicant": {"name": "上書き 太郎"}})
    assert overridden.applicant.name == "上書き 太郎"
    # 上書きしなかった項目は元のまま
    assert overridden.applicant.phone == individual_case.applicant.phone
    assert overridden.employment.employer_name == individual_case.employment.employer_name
    # 元の Case は変更されない
    assert individual_case.applicant.name == "テスト 花子"


# --- pdf_password --------------------------------------------------------


@pytest.fixture
def password_protected_meta(individual_case, tmp_path):
    """1書類だけパスワード保護し、残りは通常出力するケースを生成する。"""
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-PWPDF",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                pdf_password=PASSWORD,
            ),
            DocumentSpec(document_type="income_certificate", variant="salary_certificate"),
            DocumentSpec(document_type="identity_document", variant="drivers_license"),
        ],
    )
    meta = CasePdfGenerator(output_dir=tmp_path).generate(case)
    return meta, tmp_path / case.case_id


def test_password_protected_pdf_cannot_be_opened_without_password(password_protected_meta):
    _, case_dir = password_protected_meta
    path = case_dir / "pdf" / "rental_application_individual_standard.pdf"
    with pytest.raises(pikepdf.PasswordError):
        pikepdf.open(path)


def test_password_protected_pdf_opens_with_password(password_protected_meta):
    _, case_dir = password_protected_meta
    path = case_dir / "pdf" / "rental_application_individual_standard.pdf"
    with pikepdf.open(path, password=PASSWORD) as pdf:
        assert len(pdf.pages) >= 1


def test_other_documents_are_still_generated_and_readable(password_protected_meta):
    """パスワード保護書類があっても、他の書類は通常どおり生成・オープンできる。"""
    _, case_dir = password_protected_meta
    for name in (
        "income_certificate_salary_certificate.pdf",
        "identity_document_drivers_license.pdf",
    ):
        path = case_dir / "pdf" / name
        assert path.exists()
        with pikepdf.open(path) as pdf:
            assert len(pdf.pages) >= 1


def test_case_meta_records_pdf_password(password_protected_meta):
    meta, case_dir = password_protected_meta
    entries = meta["generated_documents"]
    assert entries[0]["pdf_password"] == PASSWORD
    assert "pdf_password" not in entries[1]

    on_disk = json.loads((case_dir / "case_meta.json").read_text(encoding="utf-8"))
    assert on_disk["generated_documents"][0]["pdf_password"] == PASSWORD


def test_pdf_password_with_non_pdf_output_format_raises(individual_case, tmp_path):
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-PW-PNG",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                output_format="png",
                pdf_password=PASSWORD,
            )
        ],
    )
    with pytest.raises(PdfPasswordNotSupportedError):
        CasePdfGenerator(output_dir=tmp_path).generate(case)


def test_pdf_password_with_output_format_override_raises(individual_case, tmp_path):
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-PW-OVERRIDE",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                pdf_password=PASSWORD,
            )
        ],
    )
    generator = CasePdfGenerator(output_dir=tmp_path, output_format="jpg")
    with pytest.raises(PdfPasswordNotSupportedError):
        generator.generate(case)


# --- label / overrides ---------------------------------------------------


@pytest.fixture
def two_applications_meta(individual_case, tmp_path):
    """同一種別・名義違いの申込書2通を生成する（label + overrides）。"""
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-TWO-APPS",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                label="applicant_a",
            ),
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                label="applicant_b",
                overrides={
                    "applicant": {
                        "name": "別名 次郎",
                        "kana": "ベツメイ ジロウ",
                        "birth_date": "1985年08月08日",
                    }
                },
            ),
        ],
    )
    meta = CasePdfGenerator(output_dir=tmp_path).generate(case)
    return meta, tmp_path / case.case_id


def test_label_avoids_file_collision_for_same_document_type(two_applications_meta):
    meta, case_dir = two_applications_meta
    assert len(meta["generated_documents"]) == 2
    for label in ("applicant_a", "applicant_b"):
        stem = f"rental_application_individual_standard_{label}"
        assert (case_dir / "pdf" / f"{stem}.pdf").exists()
        assert (case_dir / "answers" / f"{stem}.json").exists()


def test_case_meta_records_label_and_paths(two_applications_meta):
    meta, _ = two_applications_meta
    labels = [entry["label"] for entry in meta["generated_documents"]]
    assert labels == ["applicant_a", "applicant_b"]
    files = {entry["file"] for entry in meta["generated_documents"]}
    answers = {entry["answer"] for entry in meta["generated_documents"]}
    assert len(files) == 2
    assert len(answers) == 2


def test_overrides_make_answer_names_differ(two_applications_meta):
    _, case_dir = two_applications_meta

    def _fields(label: str) -> dict:
        path = case_dir / "answers" / f"rental_application_individual_standard_{label}.json"
        return json.loads(path.read_text(encoding="utf-8"))["fields"]

    a = _fields("applicant_a")
    b = _fields("applicant_b")
    assert a["name"] == "テスト 花子"
    assert b["name"] == "別名 次郎"
    assert a["name"] != b["name"]
    assert b["kana"] == "ベツメイ ジロウ"
    assert b["birth_date"] == "1985年08月08日"
    # 上書きしていない項目（物件情報）は2通で同一
    assert a["property_name"] == b["property_name"]


def test_overrides_apply_to_rendered_document(individual_case, tmp_path):
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-OVERRIDE-CSV",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="standard",
                output_format="csv",
                label="renamed",
                overrides={"applicant": {"name": "上書き 太郎"}},
            )
        ],
    )
    CasePdfGenerator(output_dir=tmp_path).generate(case)

    path = tmp_path / case.case_id / "csv" / "rental_application_individual_standard_renamed.csv"
    text = path.read_text(encoding="utf-8")
    assert "上書き 太郎" in text
    assert "テスト 花子" not in text


# --- 印刷＋手書き混在バリアント ------------------------------------------


def test_print_handwriting_mixed_variant_renders_as_jpg(individual_case, tmp_path):
    case = _case_with_documents(
        individual_case,
        "CASE-TEST-MIXED",
        [
            DocumentSpec(
                document_type="rental_application_individual",
                variant="print_handwriting_mixed",
                output_format="jpg",
            )
        ],
    )
    CasePdfGenerator(output_dir=tmp_path).generate(case)

    path = (
        tmp_path
        / case.case_id
        / "jpg"
        / "rental_application_individual_print_handwriting_mixed.jpg"
    )
    assert path.exists()
    with path.open("rb") as f:
        assert f.read(3) == b"\xff\xd8\xff"
    answer_path = (
        tmp_path
        / case.case_id
        / "answers"
        / "rental_application_individual_print_handwriting_mixed.json"
    )
    answer = json.loads(answer_path.read_text(encoding="utf-8"))
    assert answer["variant"] == "print_handwriting_mixed"
    assert answer["fields"]["name"] == "テスト 花子"
