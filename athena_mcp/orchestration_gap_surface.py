from __future__ import annotations

GAP_TOOL_NAMES={"athena_gap_compile","athena_gap_get","athena_gap_replay","athena_gap_recent"}

def call_gap_tool(ledger,name,args):
    a=dict(args or {})
    if name=="athena_gap_compile":return ledger.compile(a["task_ref"],a["sources"],a["edges"],a["targets"],a["policy"],a.get("actor","agent"),a.get("persist",True))
    if name=="athena_gap_get":return ledger.get(a["run_id"])
    if name=="athena_gap_replay":return ledger.replay(a["run_id"])
    if name=="athena_gap_recent":return ledger.recent(a.get("limit",50))
    raise KeyError(name)

def gap_resource_value(ledger):
    return {
        "law":{
            "closure":"witnessed directed reachability over explicitly traversable typed relations",
            "boundary":"reachability != logical/causal proof",
            "gap":"explicit target nodes - closure nodes",
            "grow":"max severity*leverage*information_gain/cost over uncovered KNOWN residuals",
            "unknown":"missing residual metrics -> measurement_plan, never zero",
            "replay":"GAPRUN freezes sources+edges+targets+policy",
        },
        "recent":ledger.recent(100),
        "benchmark":ledger.benchmark(),
    }
