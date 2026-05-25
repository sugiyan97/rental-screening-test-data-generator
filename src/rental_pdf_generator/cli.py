import argparse
import json
import sys
from pathlib import Path

from .generator import CasePdfGenerator
from .models import Case


def main() -> None:
    parser = argparse.ArgumentParser(description="入居審査テスト用PDFを生成するツール")
    parser.add_argument("--input", required=True, type=Path, help="入力JSONLファイルパス")
    parser.add_argument("--output", required=True, type=Path, help="出力ディレクトリ")
    parser.add_argument("--case-id", default=None, help="特定ケースのみ生成")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"エラー: 入力ファイルが見つかりません: {args.input}", file=sys.stderr)
        sys.exit(1)

    cases = _load_cases(args.input, args.case_id)
    if not cases:
        target = f" (case_id: {args.case_id})" if args.case_id else ""
        print(f"エラー: 処理対象のケースがありません{target}", file=sys.stderr)
        sys.exit(1)

    generator = CasePdfGenerator(output_dir=args.output)
    for case in cases:
        print(f"生成中: {case.case_id} ({len(case.documents)}書類)")
        generator.generate(case)
        print(f"完了: {case.case_id} → {args.output / case.case_id}")


def _load_cases(input_path: Path, case_id_filter: str | None) -> list[Case]:
    cases = []
    with input_path.open(encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                case = Case.model_validate(data)
            except (json.JSONDecodeError, ValueError) as e:
                print(
                    f"警告: {input_path}:{lineno} の解析に失敗しました: {e}",
                    file=sys.stderr,
                )
                continue
            if case_id_filter is None or case.case_id == case_id_filter:
                cases.append(case)
    return cases
