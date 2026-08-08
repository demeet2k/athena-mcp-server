# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS builder

ARG SOURCE_DATE_EPOCH=0
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}
WORKDIR /src
COPY pyproject.toml ./
COPY athena_mcp ./athena_mcp
RUN python -m pip wheel --no-deps --wheel-dir /wheels .

FROM python:3.12-slim AS runtime
ARG VERSION=3.1.0
ARG VCS_REF=unknown
ARG SOURCE_URL=https://github.com/demeet2k/athena-mcp-server
LABEL org.opencontainers.image.title="ATHENA Canonical MCP" \
      org.opencontainers.image.description="Collective V11 × KC144 secure HTTP host and digest-pinned deployment runtime" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.source="${SOURCE_URL}" \
      org.opencontainers.image.licenses="NOASSERTION"
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    ATHENA_HTTP_HOST=0.0.0.0 \
    ATHENA_HTTP_PORT=8765 \
    ATHENA_DB=/var/lib/athena/athena.db \
    ATHENA_SCHEMA_MIGRATE=true
COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels \
    && groupadd --system --gid 65532 athena \
    && useradd --system --uid 65532 --gid 65532 --home-dir /nonexistent --shell /usr/sbin/nologin athena \
    && mkdir -p /var/lib/athena /tmp \
    && chown -R 65532:65532 /var/lib/athena /tmp
USER 65532:65532
WORKDIR /var/lib/athena
VOLUME ["/var/lib/athena"]
EXPOSE 8765
HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=4 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8765/readyz', timeout=4).read()"]
ENTRYPOINT ["athena-mcp-http"]
