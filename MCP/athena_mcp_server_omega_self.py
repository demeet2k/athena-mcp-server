"""Athena MCP server entrypoint with read-only ΩSELF IC10/RETURN projection."""
from athena_mcp_server import mcp
from omega_self_adapter import register_omega_self_resources, register_omega_self_tools
register_omega_self_tools(mcp)
register_omega_self_resources(mcp)
if __name__=="__main__":
    mcp.run()
