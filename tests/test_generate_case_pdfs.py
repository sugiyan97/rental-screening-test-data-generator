import json

import pytest

from rental_pdf_generator.generator import CasePdfGenerator
from rental_pdf_generator.models import DocumentSpec
from rental_pdf_generator.template_loader import TemplateNotFoundError


def test_generate_corporate_case(corporate_case, tmp_path):
    generator = CasePdfGenerator(output_dir=tmp_path)
    meta = generator.generate(corporate_case)

    case_dir = tmp_path / corporate_case.case_id
    assert (case_dir / "case_meta.json").exists()
    assert (case_dir / "pdf" / "rental_application_corporate.pdf").exists()
    assert (case_dir / "pdf" / "registry_certificate.pdf").exists()
    assert (case_dir / "pdf" / "financial_statement.pdf").exists()
    assert (case_dir / "pdf" / "business_plan.pdf").exists()
    assert (case_dir / "answers" / "rental_application_corporate.json").exists()
    assert (case_dir / "answers" / "registry_certificate.json").exists()
    assert (case_dir / "answers" / "financial_statement.json").exists()
    assert (case_dir / "answers" / "business_plan.json").exists()
    assert meta["case_id"] == corporate_case.case_id
    assert len(meta["generated_documents"]) == 4


def test_generate_individual_case(individual_case, tmp_path):
    generator = CasePdfGenerator(output_dir=tmp_path)
    meta = generator.generate(individual_case)

    case_dir = tmp_path / individual_case.case_id
    assert (case_dir / "pdf" / "rental_application_individual.pdf").exists()
    assert (case_dir / "pdf" / "income_certificate.pdf").exists()
    assert (case_dir / "answers" / "rental_application_individual.json").exists()
    assert (case_dir / "answers" / "income_certificate.json").exists()
    assert len(meta["generated_documents"]) == 2


def test_case_meta_json_structure(individual_case, tmp_path):
    generator = CasePdfGenerator(output_dir=tmp_path)
    generator.generate(individual_case)

    meta_path = tmp_path / individual_case.case_id / "case_meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["case_id"] == individual_case.case_id
    assert meta["applicant_type"] == "individual"
    doc = meta["generated_documents"][0]
    assert "document_type" in doc
    assert "variant" in doc
    assert "pdf" in doc
    assert "answer" in doc
    assert doc["pdf"].startswith("pdf/")
    assert doc["answer"].startswith("answers/")


def test_answer_json_structure(individual_case, tmp_path):
    generator = CasePdfGenerator(output_dir=tmp_path)
    generator.generate(individual_case)

    answer_path = (
        tmp_path / individual_case.case_id / "answers" / "rental_application_individual.json"
    )
    answer = json.loads(answer_path.read_text(encoding="utf-8"))
    assert answer["case_id"] == individual_case.case_id
    assert answer["document_type"] == "rental_application_individual"
    assert "fields" in answer
    assert answer["fields"]["name"] == "テスト 花子"


def test_answer_json_encoding(corporate_case, tmp_path):
    generator = CasePdfGenerator(output_dir=tmp_path)
    generator.generate(corporate_case)

    answer_path = (
        tmp_path / corporate_case.case_id / "answers" / "rental_application_corporate.json"
    )
    raw = answer_path.read_bytes()
    assert "テスト商事株式会社".encode() in raw


def test_invalid_template_raises_error(corporate_case, tmp_path):
    corporate_case.documents.append(
        DocumentSpec(document_type="nonexistent_type", variant="standard")
    )
    generator = CasePdfGenerator(output_dir=tmp_path)
    with pytest.raises(TemplateNotFoundError):
        generator.generate(corporate_case)
