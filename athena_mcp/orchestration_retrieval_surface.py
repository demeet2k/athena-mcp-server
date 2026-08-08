from __future__ import annotations

from .orchestration_retrieval import retrieval_law

RETRIEVAL_TOOL_NAMES={
    "athena_retrieval_compile",
    "athena_retrieval_get",
    "athena_retrieval_replay",
    "athena_retrieval_recent",
}

def call_retrieval_tool(ledger,name,args,eq_ledger=None):
    a=dict(args or {})
    if name=="athena_retrieval_compile":
        eq_snapshot=a.get("eq_snapshot")
        context=a.get("equivalence_context")
        if eq_snapshot is not None and context:
            raise ValueError("provide eq_snapshot or equivalence_context, not both")
        if context:
            if eq_ledger is None:raise ValueError("equivalence_context requires connected EQ.1 ledger")
            eq_snapshot=eq_ledger.snapshot(context,a["candidates"])
        return ledger.compile(a["query_ref"],a["query"],a["candidates"],eq_snapshot,a.get("actor","agent"),a.get("task",""),a.get("persist",True))
    if name=="athena_retrieval_get":return ledger.get(a["run_id"])
    if name=="athena_retrieval_replay":return ledger.replay(a["run_id"])
    if name=="athena_retrieval_recent":return ledger.recent(a.get("limit",50))
    raise KeyError(name)

def retrieval_resource_value(ledger):
    return {"law":retrieval_law(),"recent":ledger.recent(100),"benchmark":ledger.benchmark()}
