FROM python:3.12-slim AS build

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /src
COPY pyproject.toml ./
COPY athena_mcp ./athena_mcp
RUN python -m pip wheel --no-deps --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ATHENA_DB=/var/lib/athena/athena.db \
    ATHENA_HTTP_HOST=0.0.0.0 \
    ATHENA_HTTP_PORT=8765 \
    ATHENA_MIGRATE=true

RUN groupadd --gid 65532 athena \
    && useradd --uid 65532 --gid 65532 --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin athena
COPY --from=build /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels \
    && mkdir -p /var/lib/athena \
    && chown -R 65532:65532 /var/lib/athena

USER 65532:65532
WORKDIR /var/lib/athena
VOLUME ["/var/lib/athena"]
EXPOSE 8765

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=4 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/readyz', timeout=3).read()"]

ENTRYPOINT ["python", "-m", "athena_mcp.http_host"]
CMD ["--host", "0.0.0.0", "--port", "8765", "--db", "/var/lib/athena/athena.db", "--migrate"]
