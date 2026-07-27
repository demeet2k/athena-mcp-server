# P07 hosted MCP package

This package exposes the existing Athena MCP server through Streamable HTTP at
`/mcp`. It does not change the stdio entry point, grant promotion authority,
or claim a deployment.

Required deployment locks:

- `ATHENA_BUILD_COMMIT`: exact lowercase 40-hex source commit supplied while
  building the image. The Dockerfile seals it into
  `/app/.athena-deployed-commit`; runtime environment variables cannot
  override that file.
- `ATHENA_MCP_BEARER_TOKEN`: secret bearer token of at least 32 characters.
  The MCP endpoint returns `503` when it is absent or too short.
- `ATHENA_MCP_ALLOWED_ORIGINS`: comma-separated browser origins. Requests
  without an `Origin` header are treated as non-browser clients and still
  require the bearer token.
- `PORT`: optional listening port, default `8080`.

Build and run locally:

```bash
DEPLOYED_COMMIT="$(git rev-parse HEAD)"
docker build -f Dockerfile.mcp \
  --build-arg ATHENA_BUILD_COMMIT="$DEPLOYED_COMMIT" \
  -t athena-mcp:p07 .
docker run --rm -p 8080:8080 \
  -e ATHENA_MCP_BEARER_TOKEN='replace-with-at-least-32-characters' \
  athena-mcp:p07
```

The public `/healthz` response is ready only when the token and immutable
build-commit file are valid. It exposes the commit but never the token.

After deployment, capture the witness without recording the token:

```bash
export ATHENA_MCP_BEARER_TOKEN='host-secret-at-least-32-characters'
python scripts/probe_mcp_host.py \
  https://example.invalid/mcp \
  <exact-expected-commit> \
  --output p07-deployment-witness.json
```

The probe derives `/healthz` from the MCP URL and rejects the witness unless
the host itself attests the expected commit, `/mcp` path, ready state, and
non-promotional boundary. The witness is necessary but not sufficient for
promotion. Control-plane admission must preserve the P06 forward/return, v1
fallback, rollback, and authority boundaries.
