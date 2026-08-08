from __future__ import annotations

from .orchestration_hug import HUG_PARAMS

HUG_TOOL_NAMES={
    "athena_hug_register","athena_hug_state","athena_hug_list","athena_hug_promote",
    "athena_hug_plan","athena_hug_complete","athena_hug_fail","athena_hug_invocation","athena_hug_verify_packet",
}

def call_hug_tool(registry,name,args):
    a=dict(args or {})
    if name=="athena_hug_register":return registry.register(a["name"],a["version"],a["algorithm_ref"],a["implementation_digest"],a["parameter_semantics"],a["input_schema"],a["output_schema"],a.get("actor","agent"))
    if name=="athena_hug_state":
        value=registry.state(a["impl_id"]);return value if value is not None else {"found":False,"impl_id":a["impl_id"]}
    if name=="athena_hug_list":return registry.list(a.get("status"),a.get("limit",100))
    if name=="athena_hug_promote":return registry.promote(a["impl_id"],a["target_status"],a.get("test"),a.get("canonical_authority"),a.get("actor","agent"))
    if name=="athena_hug_plan":return registry.plan(a["impl_id"],a["arguments"],a.get("context"),a.get("required_status","CANONICAL"),a.get("actor","agent"))
    if name=="athena_hug_complete":return registry.complete(a["invocation_id"],a["output"],a["receipt"],a.get("actor","agent"))
    if name=="athena_hug_fail":return registry.fail(a["invocation_id"],a["reason"],a["witness"],a.get("actor","agent"))
    if name=="athena_hug_invocation":
        value=registry.invocation(a["invocation_id"]);return value if value is not None else {"found":False,"invocation_id":a["invocation_id"]}
    if name=="athena_hug_verify_packet":return registry.verify_packet(a["invocation_id"])
    raise KeyError(name)

def hug_resource_value(registry):
    return {
        "law":{
            "signature":"HUG(io,au,fx,lm,er,st)",
            "params":list(HUG_PARAMS),
            "status":"CANDIDATE -> TESTED -> CANONICAL",
            "anti_fake":"registered implementation identity + schemas + status gate required before HUGINV; plan != semantic execution",
            "completion":"output-schema validation + verified execution receipt",
            "packet_replay":"input digest integrity only unless a real executor provides semantic replay",
        },
        "implementations":registry.list(limit=500),
        "benchmark":registry.benchmark(),
    }
