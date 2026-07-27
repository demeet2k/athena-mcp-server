# P07 hosted MCP package

This package exposes the existing Athena MCP server through Streamable HTTP at
`/mcp`. It does not change the stdio entry point, grant promotion authority, or
claim a deployment.

Required runtime configuration:

- `ATHENA_MCP_BEARER_TOKEN`: a secret bearer token; the MCP endpoint returns
  `503` when it is absent.
- `ATHENA_MCP_ALLOWED_ORIGINS`: comma-separated browser origins. Requests
  without an `Origin` header are treated as non-browser clients and still
  require the bearer token.
- `PORT`: optional listening port, default `8080`.

Build and run locally:

```bash
docker build -f Dockerfile.mcp -t athena-mcp:p07 .
docker run --rm -p 8080:8080 \
  -e ATHENA_MCP_BEARER_TOKEN='replace-me' \
  athena-mcp:p07
```

After deployment, capture the witness without recording the token:

```bash
export ATHENA_MCP_BEARER_TOKEN='host-secret'
python scripts/probe_mcp_host.py \
  https://example.invalid/mcp \
  <exact-deployed-commit> \
  --output p07-deployment-witness.json
```

The witness is necessary but not sufficient for promotion. It must be admitted
by the control plane and retain the P06 forward/return, v1 fallback, rollback,
and authority boundaries.
