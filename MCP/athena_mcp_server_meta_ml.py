"""Athena MCP server entrypoint with the Meta Machine Learning Game installed."""
from athena_mcp_server import mcp
from meta_ml_game_adapter import (
    register_meta_ml_resources,
    register_meta_ml_tools,
)


register_meta_ml_tools(mcp)
register_meta_ml_resources(mcp)


if __name__ == "__main__":
    mcp.run()
