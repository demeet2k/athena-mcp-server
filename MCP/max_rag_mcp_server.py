"""Standalone KC144 MAX–RAG MCP cartridge.

This host is intentionally separate from the validated Athena 323-tool host. It
mounts only the governed MAX–RAG v1 surface, performs no source retrieval or
external dispatch, and creates no promotion authority.
"""

from pathlib import Path
import sys

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parent))

from crystal_108d.max_rag_game_v1 import register_max_rag_game_v1


mcp = FastMCP("Athena KC144 MAX-RAG")
register_max_rag_game_v1(mcp)


if __name__ == "__main__":
    mcp.run()
