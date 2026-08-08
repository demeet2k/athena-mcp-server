from __future__ import annotations

FIELD_TOOL_NAMES={
    "athena_field_compile",
    "athena_field_get",
    "athena_field_replay",
    "athena_field_recent",
}


def call_field_tool(ledger,name,args):
    a=dict(args or {})
    if name=="athena_field_compile":
        return ledger.compile(
            a["seed_ref"],
            a["module_outputs"],
            a.get("explicit_candidates") or [],
            a.get("ecosystem") or {},
            a.get("actor","agent"),
            a.get("persist",True),
        )
    if name=="athena_field_get":return ledger.get(a["run_id"])
    if name=="athena_field_replay":return ledger.replay(a["run_id"])
    if name=="athena_field_recent":return ledger.recent(a.get("limit",50))
    raise KeyError(name)


def field_resource_value(ledger):
    return {
        "law":{
            "version":"FIELD.1",
            "boundary":"assemble actual module residuals/tasks into action candidates; never invent candidate metrics",
            "origins":["SX.1","RAG.1","Y.1","GAP.1","HUG.ABI.1","BRANCH_EVOLUTION","AOR.3","EXPLICIT"],
            "merge":"exact action signatures may merge provenance; semantic similarity does not collapse",
            "metric_conflict":"conflicting explicit AOR measurements -> metric_state=CONFLICT -> remove disputed ranking operands -> remeasure/adjudicate",
            "handoff":"FIELD candidates become AOR candidate inputs only after required measurements/calibration/gates are supplied",
            "replay":"FIELDRUN freezes module outputs + explicit candidates + ecosystem + provenance edges",
        },
        "recent":ledger.recent(100),
        "benchmark":ledger.benchmark(),
    }
