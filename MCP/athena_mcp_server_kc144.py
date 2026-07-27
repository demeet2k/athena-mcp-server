"""Run the Athena MCP server with KC144 Meta-Compiler tools registered."""
from __future__ import annotations

import athena_mcp_server as base_server
from kc144_meta_navigation import register_kc144_meta_navigation

mcp = None
for candidate in ("mcp", "server", "app"):
    value = getattr(base_server, candidate, None)
    if value is not None and hasattr(value, "tool"):
        mcp = value
        break
if mcp is None:
    raise RuntimeError("Could not find a FastMCP-compatible server object in athena_mcp_server")

register_kc144_meta_navigation(mcp)

if __name__ == "__main__":
    runner = getattr(mcp, "run", None)
    if not callable(runner):
        raise RuntimeError("The resolved MCP server has no callable run() method")
    runner()
