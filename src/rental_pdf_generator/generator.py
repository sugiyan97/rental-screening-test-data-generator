from pathlib import Path

from playwright.sync_api import sync_playwright

from .answer_builder import build_answer
from .file_writer import ensure_dir, write_json
from .models import Case, DocumentSpec, apply_case_overrides
from .renderers import (
    PdfPasswordNotSupportedError,
    encrypt_pdf,
    render_document,
)
from .template_loader import TemplateLoader


def document_stem(doc_spec: DocumentSpec) -> str:
    """書類ファイル・正解JSON の共通ファイル名（拡張子なし）を返す。

    label が指定された場合は末尾に付けることで、同一 document_type / variant の
    書類を1ケースに複数含めてもファイル名が衝突しない。
    """
    stem = f"{doc_spec.document_type}_{doc_spec.variant}"
    if doc_spec.label:
        stem = f"{stem}_{doc_spec.label}"
    return stem


class CasePdfGenerator:
    def __init__(
        self,
        output_dir: Path,
        templates_dir: Path | None = None,
        output_format: str | None = None,
    ) -> None:
        self._output_dir = output_dir
        self._loader = TemplateLoader(templates_dir)
        # 指定された場合、全書類の出力形式をこの形式で上書きする
        self._output_format_override = output_format

    def generate(self, case: Case) -> dict:
        case_dir = self._output_dir / case.case_id
        answers_dir = case_dir / "answers"
        ensure_dir(answers_dir)

        generated_documents = []

        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(locale="ja-JP")
            page = context.new_page()

            for doc_spec in case.documents:
                doc_path, answer_path, output_format = self._generate_document(
                    page=page,
                    case=case,
                    doc_spec=doc_spec,
                    case_dir=case_dir,
                    answers_dir=answers_dir,
                )
                generated_documents.append(
                    self._build_document_entry(doc_spec, doc_path, answer_path, output_format)
                )

            browser.close()

        case_meta: dict = {
            "case_id": case.case_id,
            "applicant_type": case.applicant_type,
            "generated_documents": generated_documents,
        }
        if case.description:
            case_meta["description"] = case.description
        write_json(case_dir / "case_meta.json", case_meta)
        return case_meta

    def _build_document_entry(
        self,
        doc_spec: DocumentSpec,
        doc_path: Path,
        answer_path: Path,
        output_format: str,
    ) -> dict:
        relative_path = f"{doc_path.parent.name}/{doc_path.name}"
        entry = {
            "document_type": doc_spec.document_type,
            "variant": doc_spec.variant,
            "output_format": output_format,
            "file": relative_path,
        }
        if doc_spec.label:
            entry["label"] = doc_spec.label
        if output_format == "pdf":
            # 既存の利用側との互換のため pdf 形式では pdf キーも残す
            entry["pdf"] = relative_path
        if doc_spec.pdf_password:
            # 期待値（パスワード保護されている書類）として利用側が参照できるよう記録する
            entry["pdf_password"] = doc_spec.pdf_password
        entry["answer"] = f"answers/{answer_path.name}"
        return entry

    def _generate_document(
        self,
        page,
        case: Case,
        doc_spec: DocumentSpec,
        case_dir: Path,
        answers_dir: Path,
    ) -> tuple[Path, Path, str]:
        template = self._loader.load(
            case_id=case.case_id,
            document_type=doc_spec.document_type,
            variant=doc_spec.variant,
        )
        # overrides が指定された書類は、部分上書きしたケースデータで描画・正解JSONを作る
        doc_case = apply_case_overrides(case, doc_spec.overrides)
        html = template.render(case=doc_case)

        output_format = self._output_format_override or doc_spec.output_format
        if doc_spec.pdf_password and output_format != "pdf":
            raise PdfPasswordNotSupportedError(
                f"pdf_password は output_format が pdf の書類にのみ指定できます。\n"
                f"  case_id: {case.case_id}\n"
                f"  document_type: {doc_spec.document_type}\n"
                f"  variant: {doc_spec.variant}\n"
                f"  output_format: {output_format}"
            )
        stem = document_stem(doc_spec)
        doc_dir = case_dir / output_format
        ensure_dir(doc_dir)
        doc_path = doc_dir / f"{stem}.{output_format}"

        page.set_content(html, wait_until="networkidle", timeout=30000)
        render_document(page=page, output_format=output_format, path=doc_path, title=stem)
        if doc_spec.pdf_password:
            encrypt_pdf(doc_path, doc_spec.pdf_password)

        answer = build_answer(doc_case, doc_spec.document_type, doc_spec.variant)
        answer_path = answers_dir / f"{stem}.json"
        write_json(answer_path, answer)

        return doc_path, answer_path, output_format
