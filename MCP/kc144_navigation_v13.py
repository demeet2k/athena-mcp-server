from __future__ import annotations
import json
from typing import Any
import kc144_navigation_v12 as _v12
from kc144_navigation_v12 import register_kc144_v12
from kc144_harness_v13 import Harness, depth, scan, synthesis, tunnel
from kc144_meta_v12 import compile_query

_REG=set()
_HARNESS=Harness()

def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)

def register_kc144_v13(mcp: Any) -> Any:
    if hasattr(mcp, "tools") and "locate_kc144" not in mcp.tools:
        _v12._REG.discard(id(mcp))
    register_kc144_v12(mcp)
    if id(mcp) in _REG:
        return mcp
    _REG.add(id(mcp))

    def tool(name, function, doc):
        function.__name__ = name
        function.__doc__ = doc
        mcp.tool()(function)

    tool("kc144_harness_scan_v13", lambda paths, recursive=True: dump(scan(paths, recursive)), "Scan bodies into AID/OID/VID artifact shadows.")
    tool("kc144_harness_run_v13", lambda query, paths=None, maps=None: dump(_HARNESS.run(query, paths or [], maps or [])), "Run the federated mycelium harness and return to M12.")
    tool("kc144_harness_replay_v13", lambda run_id: dump(_HARNESS.replay(run_id)), "Replay a stored federated harness run.")
    tool("kc144_harness_status_v13", lambda: dump(_HARNESS.status()), "Return persistent harness status and authority boundary.")

    def cross(query, maps=None):
        compiled = compile_query(query)
        artifacts = _HARNESS.store.artifacts()
        return dump(synthesis(query, compiled, _HARNESS.store.search(query), artifacts, maps or []))

    tool("kc144_cross_synthesize_v13", cross, "Cross-synthesize compiler, map, artifact, and source projections.")
    tool("kc144_depth_v13", lambda max_depth=12: dump(depth(max_depth)), "Materialize bounded BR/KC/angular depth laws.")
    tool("kc144_tunnel_v13", lambda system, address, target_depth, child_digit=0: dump(tunnel(system, address, target_depth, child_digit)), "Navigate a typed parent/child depth tunnel.")
    tool("kc144_tool_bus_v13", lambda: dump({"tools": _HARNESS.status()["tools"], "truth_effect": "NONE"}), "List the six explicit capability-addressed KC144 organs.")
    return mcp
