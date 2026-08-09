from __future__ import annotations
import athena_mcp_server as base
from kc144_navigation_v13 import register_kc144_v13

mcp = next((getattr(base, name, None) for name in ("mcp", "server", "app") if hasattr(getattr(base, name, None), "tool")), None)
if mcp is None:
    raise RuntimeError("FastMCP-compatible server object not found")
register_kc144_v13(mcp)

if __name__ == "__main__":
    mcp.run()
