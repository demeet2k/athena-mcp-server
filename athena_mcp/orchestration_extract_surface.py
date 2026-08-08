from __future__ import annotations

from .orchestration_extract import transform_manifest

EXTRACTION_TOOL_NAMES={
    "athena_extraction_plan",
    "athena_extraction_task",
    "athena_extraction_complete",
    "athena_extraction_fail",
    "athena_extraction_result",
    "athena_extraction_expand_result",
    "athena_extraction_frontier",
    "athena_extraction_run",
}

def call_extraction_tool(ledger,name,args):
    a=dict(args or {})
    if name=="athena_extraction_plan":
        return ledger.plan(a["seed_ref"],a["seed"],a.get("transforms"),a.get("max_depth",1),a.get("max_tasks_per_generation",16),a.get("actor","agent"))
    if name=="athena_extraction_task":
        value=ledger.task(a["task_id"]);return value if value is not None else {"found":False,"task_id":a["task_id"]}
    if name=="athena_extraction_complete":
        return ledger.complete(a["task_id"],a["outputs"],a["witness"],a.get("actor","agent"))
    if name=="athena_extraction_fail":
        return ledger.fail(a["task_id"],a["reason"],a["witness"],a.get("actor","agent"))
    if name=="athena_extraction_result":
        value=ledger.result(a["result_id"]);return value if value is not None else {"found":False,"result_id":a["result_id"]}
    if name=="athena_extraction_expand_result":
        return ledger.expand_result(a["result_id"],a.get("transforms"),a.get("actor","agent"))
    if name=="athena_extraction_frontier":return ledger.frontier(a["run_id"])
    if name=="athena_extraction_run":
        value=ledger.run(a["run_id"]);return value if value is not None else {"found":False,"run_id":a["run_id"]}
    raise KeyError(name)

def extraction_resource_value(ledger):
    return {
        "law":{
            "seed":"SX+ = dedup(SX U T(SX))",
            "planning":"PLANNED task != semantic execution",
            "completion":"actual outputs + verified witness",
            "failure":"explicit reason + verified witness",
            "recursion":"verified EXTRES may seed next generation within depth/task bounds",
            "anti_fake":"scheduler never invents transform outputs",
        },
        "transform_manifest":transform_manifest(),
        "benchmark":ledger.benchmark(),
    }
