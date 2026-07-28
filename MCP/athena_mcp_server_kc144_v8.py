"""Run Athena MCP with KC144 V7 and V8 tools registered."""
from __future__ import annotations

import athena_mcp_server as base_server
from kc144_v8_navigation import register_kc144_v8

registrars = []
for module_name, function_name in (
    ("kc144_meta_navigation", "register_kc144_meta_navigation"),
    ("kc144_v7_navigation", "register_kc144_v7"),
):
    try:
        module = __import__(module_name, fromlist=[function_name])
        registrars.append(getattr(module, function_name))
    except (ImportError, AttributeError):
        pass

mcp = None
for candidate in ("mcp", "server", "app"):
    value = getattr(base_server, candidate, None)
    if value is not None and hasattr(value, "tool"):
        mcp = value
        break
if mcp is None:
    raise RuntimeError("No FastMCP-compatible server object found")

for registrar in registrars:
    registrar(mcp)
register_kc144_v8(mcp)

if __name__ == "__main__":
    runner = getattr(mcp, "run", None)
    if not callable(runner):
        raise RuntimeError("Resolved MCP server has no run()")
    runner()
