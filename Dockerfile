FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY legal_mcp/ legal_mcp/
COPY landing/ landing/

RUN pip install --no-cache-dir .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD python -c "from legal_mcp.src.server import mcp; print('ok')" || exit 1

CMD ["legal-mcp"]
