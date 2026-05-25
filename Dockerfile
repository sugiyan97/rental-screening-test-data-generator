FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

COPY pyproject.toml .
RUN uv sync --no-install-project

COPY src/ src/
COPY scripts/ scripts/
COPY templates/ templates/
COPY tests/ tests/
COPY input/ input/

RUN uv sync

RUN uv run playwright install --with-deps chromium

ENTRYPOINT ["uv", "run", "python", "scripts/generate_case_pdfs.py"]
CMD ["--input", "input/cases.jsonl", "--output", "output"]
