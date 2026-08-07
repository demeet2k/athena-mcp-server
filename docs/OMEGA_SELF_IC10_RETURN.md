# ΩSELF IC10/RETURN MCP projection

Prepared against `demeet2k/athena-mcp-server@5d1401c7a82a94df1a8279b13336f69d35d3eb27`.

This is additive and read-only. It does not alter the current
`athena_mcp_server_meta_ml.py` entrypoint.

Exposes:
- `omega_self_status_tool`
- `omega_self_reference_contract_tool`
- `athena://omega-self/ic10-return/v1`
- `athena://omega-self/ic10-return/reference`

All canonical mutations, external authority admission, finality, watch closure,
and promotion remain in the Athena control plane.
