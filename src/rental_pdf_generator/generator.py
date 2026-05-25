from pathlib import Path

from playwright.sync_api import sync_playwright

from .answer_builder import build_answer
from .file_writer import ensure_dir, write_json
from .models import Case, DocumentSpec
from .template_loader import TemplateLoader


class CasePdfGenerator:
    def __init__(
        self,
        output_dir: Path,
        templates_dir: Path | None = None,
    ) -> None:
        self._output_dir = output_dir
        self._loader = TemplateLoader(templates_dir)

    def generate(self, case: Case) -> dict:
        case_dir = self._output_dir / case.case_id
        pdf_dir = case_dir / "pdf"
        answers_dir = case_dir / "answers"
        ensure_dir(pdf_dir)
        ensure_dir(answers_dir)

        generated_documents = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(locale="ja-JP")
            page = context.new_page()

            for doc_spec in case.documents:
                pdf_path, answer_path = self._generate_document(
                    page=page,
                    case=case,
                    doc_spec=doc_spec,
                    pdf_dir=pdf_dir,
                    answers_dir=answers_dir,
                )
                generated_documents.append(
                    {
                        "document_type": doc_spec.document_type,
                        "variant": doc_spec.variant,
                        "pdf": f"pdf/{pdf_path.name}",
                        "answer": f"answers/{answer_path.name}",
                    }
                )

            browser.close()

        case_meta = {
            "case_id": case.case_id,
            "applicant_type": case.applicant_type,
            "generated_documents": generated_documents,
        }
        write_json(case_dir / "case_meta.json", case_meta)
        return case_meta

    def _generate_document(
        self,
        page,
        case: Case,
        doc_spec: DocumentSpec,
        pdf_dir: Path,
        answers_dir: Path,
    ) -> tuple[Path, Path]:
        template = self._loader.load(
            case_id=case.case_id,
            document_type=doc_spec.document_type,
            variant=doc_spec.variant,
        )
        html = template.render(case=case)

        pdf_path = pdf_dir / f"{doc_spec.document_type}.pdf"
        page.set_content(html, wait_until="networkidle", timeout=30000)
        page.pdf(
            path=str(pdf_path),
            format="A4",
            print_background=True,
        )

        answer = build_answer(case, doc_spec.document_type, doc_spec.variant)
        answer_path = answers_dir / f"{doc_spec.document_type}.json"
        write_json(answer_path, answer)

        return pdf_path, answer_path
