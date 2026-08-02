from __future__ import annotations
import json,pathlib
from typing import Any
from kc144_v7_runtime import V7Runtime,plain
_BASE=pathlib.Path(__file__).resolve().parents[1]; _RUNTIME=V7Runtime(_BASE/'baml_src',_BASE/'recordings'); _REGISTERED=set()
def dump(v:Any)->str:return json.dumps(plain(v),indent=2,sort_keys=True,ensure_ascii=False)
def register_kc144_v7(mcp:Any)->Any:
    if id(mcp) in _REGISTERED:return mcp
    _REGISTERED.add(id(mcp))
    @mcp.tool()
    def kc144_v7_validate()->str:return dump(_RUNTIME.validate())
    @mcp.tool()
    def kc144_v7_revisions()->str:return dump(_RUNTIME.revisions.events)
    @mcp.tool()
    def kc144_v7_recordings()->str:return dump({'recordings':_RUNTIME.fixtures.list(),'external_witness_effect':'NONE','authority_effect':'NONE'})
    return mcp
