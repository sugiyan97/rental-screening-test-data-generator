from pathlib import Path

from jinja2 import Environment, FileSystemLoader, TemplateNotFound

_TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


class TemplateNotFoundError(Exception):
    pass


class TemplateLoader:
    def __init__(self, templates_dir: Path | None = None) -> None:
        self._templates_dir = templates_dir if templates_dir is not None else _TEMPLATES_DIR
        self._env = Environment(
            loader=FileSystemLoader(str(self._templates_dir)),
            autoescape=False,
        )

    def load(self, case_id: str, document_type: str, variant: str):
        template_path = f"{document_type}/{variant}.html"
        try:
            return self._env.get_template(template_path)
        except TemplateNotFound as err:
            available = self._list_available(document_type)
            raise TemplateNotFoundError(
                f"テンプレートが見つかりません。\n"
                f"  case_id: {case_id}\n"
                f"  document_type: {document_type}\n"
                f"  variant: {variant}\n"
                f"  期待パス: templates/{template_path}\n"
                f"  利用可能なvariant: {available or '(なし)'}"
            ) from err

    def _list_available(self, document_type: str) -> list[str]:
        doc_dir = self._templates_dir / document_type
        if not doc_dir.exists():
            return []
        return sorted(p.stem for p in doc_dir.glob("*.html"))
