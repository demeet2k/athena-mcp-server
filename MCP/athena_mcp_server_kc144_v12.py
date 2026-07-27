import athena_mcp_server as base
from kc144_navigation_v12 import register_kc144_v12
mcp=next((getattr(base,n) for n in ("mcp","server","app") if hasattr(getattr(base,n,None),"tool")),None)
if mcp is None:raise RuntimeError("FastMCP object not found")
register_kc144_v12(mcp)
if __name__=="__main__":mcp.run()
