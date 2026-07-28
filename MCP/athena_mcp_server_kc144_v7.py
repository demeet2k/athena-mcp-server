from __future__ import annotations
import athena_mcp_server as base_server
from kc144_v7_navigation import register_kc144_v7
try:
    from kc144_meta_navigation import register_kc144_meta_navigation
except ImportError: register_kc144_meta_navigation=None
mcp=None
for candidate in ('mcp','server','app'):
    value=getattr(base_server,candidate,None)
    if value is not None and hasattr(value,'tool'):mcp=value;break
if mcp is None:raise RuntimeError('No FastMCP-compatible server object found')
if register_kc144_meta_navigation is not None:register_kc144_meta_navigation(mcp)
register_kc144_v7(mcp)
if __name__=='__main__':mcp.run()
