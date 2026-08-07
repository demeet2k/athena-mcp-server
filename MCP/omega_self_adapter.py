"""Read-only MCP projection for ΩSELF IC10/RETURN control state."""
from __future__ import annotations
from pathlib import Path
from typing import Any
import json, os, hashlib

DEFAULT_ROOT=Path(os.environ.get("ATHENA_OMEGA_SELF_ROOT","../Athena"))

def _root(root=None): return Path(root) if root is not None else DEFAULT_ROOT
def _read(rel, root=None): return json.loads((_root(root)/rel).read_text(encoding="utf-8"))

def omega_self_status(root=None) -> dict[str,Any]:
    p43=_read("crystal/v2/ic10-return/contract.lock.json",root)
    hold=_read("crystal/v2/ic10-return/fixtures/authority-absence-hold.json",root)
    ref=_read("crystal/v2/ic10-return/reference/omega-self-v1/contract.lock.json",root)
    return {
        "resource":"athena://omega-self/ic10-return/v1",
        "p43_schema":p43["schema"],
        "reference_schema":ref["schema"],
        "external_state":hold["status"],
        "promotion_ready":hold["promotion_ready"],
        "write_boundary":"READ_ONLY_MCP_PROJECTION",
    }

def omega_self_reference_contract(root=None): return _read("crystal/v2/ic10-return/reference/omega-self-v1/contract.lock.json",root)

def register_omega_self_tools(mcp):
    @mcp.tool()
    def omega_self_status_tool() -> str:
        """Return P43/ΩSELF status. Read-only; never promotes."""
        return json.dumps(omega_self_status(),indent=2,ensure_ascii=False)

    @mcp.tool()
    def omega_self_reference_contract_tool() -> str:
        """Return the additive non-authoritative ΩSELF reference contract."""
        return json.dumps(omega_self_reference_contract(),indent=2,ensure_ascii=False)

def register_omega_self_resources(mcp):
    @mcp.resource("athena://omega-self/ic10-return/v1")
    def omega_self_resource() -> str:
        return json.dumps(omega_self_status(),indent=2,ensure_ascii=False)

    @mcp.resource("athena://omega-self/ic10-return/reference")
    def omega_self_reference_resource() -> str:
        return json.dumps(omega_self_reference_contract(),indent=2,ensure_ascii=False)
