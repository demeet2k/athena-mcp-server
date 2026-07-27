# P10 authorized persistent endpoint handoff

This package turns the immutable P09 OCI artifact into a fail-closed activation
boundary. It does not choose a provider, create an account, spend money,
provision a secret, claim a deployment, merge a PR, or promote the runtime.

The only admitted image is:

`ghcr.io/demeet2k/athena-mcp-server@sha256:31458783d4aeb28e0a4036cb4fab39a2f2bc1f4ef6e3025d126c78a865162ad2`

Its exact frozen source is:

`52d0e2abf282aee5f8bf233521989bc2c8969989`

## Activation inputs

An authorized operator supplies all of the following without committing secret
material:

1. provider identifier and logical account scope;
2. persistent deployment identifier;
3. HTTPS endpoint ending exactly in `/mcp`;
4. protected secret-store reference;
5. provider evidence showing the exact digest above is selected;
6. a bearer token of at least 32 characters through
   `ATHENA_MCP_BEARER_TOKEN`.

Copy `provider-evidence.example.json` outside the repository, populate the
non-secret fields, and retain `secret_material_recorded: false`. The validator
rejects unknown fields so tokens, passwords, API keys, and informal notes
cannot leak into the receipt.

Validate inputs without contacting the endpoint:

```bash
python scripts/p10_persistent_witness.py \
  https://authorized.example/mcp \
  --provider-evidence /protected/provider-evidence.json \
  --validate-evidence-only
```

After the exact digest is live and the bearer secret is present only in the
environment, capture the persistent witness:

```bash
export ATHENA_MCP_BEARER_TOKEN='resolved-from-protected-secret-store'
python scripts/p10_persistent_witness.py \
  https://authorized.example/mcp \
  --provider-evidence /protected/provider-evidence.json \
  --samples 3 \
  --interval 20 \
  --output p10-persistent-witness.json
```

The probe performs repeated health and Streamable HTTP MCP sessions. Every
sample requires exact source attestation, the frozen graph, v2 identity,
two-hop forward route, reciprocal two-hop return, explicit
`athena-108d-v1` fallback, equal cutover receipts, and
`promotion_ready: false`.

A passing witness is still non-promotional. The control plane must admit it,
and IC10 remains the only promotion authority.
