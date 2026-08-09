"""Ω29 V2 pure plan/execution/world-state classifier.

Caller-supplied source and clock observations are inputs, never authority. The
reducer performs no provider, filesystem, clock, scheduler, writer, admission,
promotion, or external mutation operation and cannot establish source freshness.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any

INPUT_SCHEMA = "ATHENA.OMEGA29.OPERATE.INPUT.V2"
BINDING_SCHEMA = "ATHENA.OMEGA29.SOURCE.BINDING.V1"
DECISION_SCHEMA = "ATHENA.OMEGA29.OPERATE.DECISION.V2"
RUNTIME_CONTEXT_SCHEMA = "ATHENA.OMEGA29.RUNTIME.CONTEXT.V1"
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_GUIDES = {"CONTINUE","CONSUME","PIVOT","ATTACK","VERIFY","FUSE","COMPARE","EVALUATE","HOLD","RETIRE","RESEED","STOP"}
TRANSITIONS = {"CONTINUE","RETRY","REBIND","REPAIR","ROLLBACK","REPLAN","HOLD","ESCALATE","COMPLETE"}
FORBIDDEN_PACKET_KEYS = {"authority","admission","admitted","accepted","protected_admission","protected_accepted","writer","writer_count","promoted","promotion","canonical","canonical_writer","canonical_writer_count","success","exit_permit","external_effects","external_mutation","external_mutations","source_freshness_verified"}
SOURCE_KEYS = {"repository","ref","object_format","head","observation_id"}
BINDING_BODY_KEYS = {"schema","run_id","invocation_id","athena","runtime","source_snapshot_digest","prompt_stack_digest","standing","authority","admission","promotion","external_effects"}
CONTEXT_BODY_KEYS = {"schema","run_id","invocation_id","now","clock_domain","clock_observation_id","source_binding_digest","standing","authority","admission","promotion","external_effects"}
ROOT_KEYS = {"schema","run_id","invocation_id","source_binding_digest","runtime_context_digest","source_heads","plan_state","execution_state","world_state","receipt","health","retry","capabilities"}

class OperateRejected(ValueError):
    pass

def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()

def _obj(value: Any, name: str) -> dict[str, Any]:
    if type(value) is not dict: raise OperateRejected(f"{name} must be an object")
    return value

def _str(value: Any, name: str) -> str:
    if type(value) is not str or not value: raise OperateRejected(f"{name} must be a non-empty string")
    return value

def _int(value: Any, name: str, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum: raise OperateRejected(f"{name} must be an integer >= {minimum}")
    return value

def _bool(value: Any, name: str) -> bool:
    if type(value) is not bool: raise OperateRejected(f"{name} must be a boolean")
    return value

def _zero(value: Any, name: str) -> int:
    if type(value) is not int or value != 0: raise OperateRejected(f"{name} must be exact integer zero")
    return value

def _sha(value: Any, name: str) -> str:
    value = _str(value, name)
    if not SHA256.fullmatch(value): raise OperateRejected(f"{name} must be a lowercase SHA-256")
    return value

def _git(value: Any, name: str) -> str:
    value = _str(value, name)
    if not GIT_SHA.fullmatch(value): raise OperateRejected(f"{name} must be a lowercase 40-character Git SHA")
    return value

def _closed(value: dict[str, Any], keys: set[str], name: str) -> None:
    if set(value) != keys: raise OperateRejected(f"{name} shape is not closed")

def _reject_claims(value: Any, path: str = "packet") -> None:
    if type(value) is dict:
        bad = FORBIDDEN_PACKET_KEYS.intersection(value)
        if bad: raise OperateRejected(f"claim-bearing keys forbidden at {path}: {sorted(bad)}")
        for key, child in value.items(): _reject_claims(child, f"{path}.{key}")
    elif type(value) is list:
        for i, child in enumerate(value): _reject_claims(child, f"{path}[{i}]")

def _source(value: Any, name: str, repo: str, ref: str) -> dict[str, str]:
    source = _obj(value, name); _closed(source, SOURCE_KEYS, name)
    if source["repository"] != repo or source["ref"] != ref: raise OperateRejected(f"{name} repository/ref identity changed")
    if source["object_format"] != "sha1": raise OperateRejected(f"{name}.object_format must be sha1")
    return {"repository": repo, "ref": ref, "object_format": "sha1", "head": _git(source["head"], f"{name}.head"), "observation_id": _str(source["observation_id"], f"{name}.observation_id")}

def validate_source_binding(value: Any) -> dict[str, Any]:
    binding = _obj(value, "source_binding"); _closed(binding, BINDING_BODY_KEYS | {"binding_digest"}, "source_binding")
    body = {k: binding[k] for k in BINDING_BODY_KEYS}
    if body["schema"] != BINDING_SCHEMA: raise OperateRejected("unsupported source binding schema")
    _str(body["run_id"], "source_binding.run_id"); _str(body["invocation_id"], "source_binding.invocation_id")
    athena = _source(body["athena"], "source_binding.athena", "demeet2k/Athena", "main")
    runtime = _source(body["runtime"], "source_binding.runtime", "demeet2k/athena-mcp-server", "master")
    _sha(body["prompt_stack_digest"], "source_binding.prompt_stack_digest"); _sha(body["source_snapshot_digest"], "source_binding.source_snapshot_digest")
    if body["standing"] != "EXACT_EXTERNAL_READBACK_INPUT_UNVERIFIED_BY_REDUCER": raise OperateRejected("source binding standing changed")
    if (body["authority"],body["admission"],body["promotion"]) != ("NONE","UNADMITTED","HOLD"): raise OperateRejected("source binding expanded claim standing")
    _zero(body["external_effects"], "source_binding.external_effects")
    if binding["binding_digest"] != digest(body): raise OperateRejected("source binding digest mismatch")
    return {**body, "athena": athena, "runtime": runtime, "binding_digest": binding["binding_digest"]}

def validate_runtime_context(value: Any, *, source_binding: dict[str, Any]) -> dict[str, Any]:
    context = _obj(value, "runtime_context"); _closed(context, CONTEXT_BODY_KEYS | {"context_digest"}, "runtime_context")
    body = {k: context[k] for k in CONTEXT_BODY_KEYS}
    if body["schema"] != RUNTIME_CONTEXT_SCHEMA: raise OperateRejected("unsupported runtime context schema")
    if (body["run_id"],body["invocation_id"]) != (source_binding["run_id"],source_binding["invocation_id"]): raise OperateRejected("runtime context run/invocation identity mismatch")
    _int(body["now"], "runtime_context.now"); _str(body["clock_observation_id"], "runtime_context.clock_observation_id")
    if body["clock_domain"] != "UTC_UNIX_SECONDS": raise OperateRejected("runtime context clock domain is unsupported")
    if body["source_binding_digest"] != source_binding["binding_digest"]: raise OperateRejected("runtime context source binding mismatch")
    if body["standing"] != "CALLER_SUPPLIED_RUNTIME_OBSERVATION_UNVERIFIED_BY_REDUCER": raise OperateRejected("runtime context standing changed")
    if (body["authority"],body["admission"],body["promotion"]) != ("NONE","UNADMITTED","HOLD"): raise OperateRejected("runtime context expanded claim standing")
    _zero(body["external_effects"], "runtime_context.external_effects")
    if context["context_digest"] != digest(body): raise OperateRejected("runtime context digest mismatch")
    return {**body, "context_digest": context["context_digest"]}

def _result(transition: str, incident: str, residuals: dict[str,bool], reason: str, binding_digest: str, context_digest: str, packet_digest: str) -> dict[str, Any]:
    if transition not in TRANSITIONS: raise AssertionError("internal unknown transition")
    body = {"schema":DECISION_SCHEMA,"transition":transition,"incident":incident,"residuals":residuals,"reason":reason,"source_binding_digest":binding_digest,"runtime_context_digest":context_digest,"packet_digest":packet_digest,"source_freshness_claim":"NOT_ESTABLISHED_BY_REDUCER","claim_ceiling":"LOCAL_CLASSIFICATION_AGAINST_CALLER_SUPPLIED_BINDING_ONLY","authority":"NONE","admission":"UNADMITTED","promotion":"HOLD","external_effects":0}
    return {**body, "decision_digest": digest(body)}

def decide(packet: Any, *, source_binding: Any, runtime_context: Any) -> dict[str, Any]:
    binding = validate_source_binding(source_binding)
    context = validate_runtime_context(runtime_context, source_binding=binding)
    packet = _obj(packet, "packet"); _reject_claims(packet)
    if packet.get("schema") != INPUT_SCHEMA: raise OperateRejected("unsupported input schema")
    _closed(packet, ROOT_KEYS | ({"mata_guide"} if "mata_guide" in packet else set()), "packet root")
    if (packet["run_id"],packet["invocation_id"]) != (binding["run_id"],binding["invocation_id"]): raise OperateRejected("packet run/invocation identity mismatch")
    if _sha(packet["source_binding_digest"], "source_binding_digest") != binding["binding_digest"]: raise OperateRejected("packet is not bound to the supplied source binding")
    if _sha(packet["runtime_context_digest"], "runtime_context_digest") != context["context_digest"]: raise OperateRejected("packet is not bound to the supplied runtime context")
    source = _obj(packet["source_heads"], "source_heads"); _closed(source, {"athena","runtime"}, "source_heads")
    athena, runtime = _git(source["athena"], "source_heads.athena"), _git(source["runtime"], "source_heads.runtime")
    plan, execution, world, receipt, health, retry = (_obj(packet[k], k) for k in ("plan_state","execution_state","world_state","receipt","health","retry"))
    _closed(plan,{"object_id","version","target_digest","required_postcondition_ids","completion_requested"},"plan_state")
    _closed(execution,{"object_id","plan_version","result_digest","receipt_sha256","exit_code","retryable"},"execution_state")
    _closed(world,{"object_id","observed_digest","observed_at","max_age_seconds"},"world_state")
    _closed(health,{"status","unresolved_incidents"},"health"); _closed(retry,{"count","limit"},"retry")
    caps = _obj(packet["capabilities"], "capabilities"); expected_caps={"retry","rebind","repair","rollback","replan","escalate"}; _closed(caps,expected_caps,"capabilities"); caps={k:_bool(caps[k],f"capabilities.{k}") for k in caps}
    po,pv,pt = _str(plan["object_id"],"plan_state.object_id"),_str(plan["version"],"plan_state.version"),_sha(plan["target_digest"],"plan_state.target_digest")
    completion = _bool(plan["completion_requested"],"plan_state.completion_requested")
    required=plan["required_postcondition_ids"]
    if type(required) is not list or not required or any(type(x) is not str or not x for x in required) or required != sorted(set(required)): raise OperateRejected("required_postcondition_ids must be a sorted unique non-empty string list")
    eo,epv,er = _str(execution["object_id"],"execution_state.object_id"),_str(execution["plan_version"],"execution_state.plan_version"),_sha(execution["result_digest"],"execution_state.result_digest")
    rsha,exit_code,retryable = _sha(execution["receipt_sha256"],"execution_state.receipt_sha256"),_int(execution["exit_code"],"execution_state.exit_code"),_bool(execution["retryable"],"execution_state.retryable")
    wo,wd,observed,max_age = _str(world["object_id"],"world_state.object_id"),_sha(world["observed_digest"],"world_state.observed_digest"),_int(world["observed_at"],"world_state.observed_at"),_int(world["max_age_seconds"],"world_state.max_age_seconds",1)
    rkeys={"source_binding_digest","object_id","plan_version","target_digest","required_postcondition_spec_digest","result_digest","postconditions"}; _closed(receipt,rkeys,"receipt")
    if receipt["source_binding_digest"] != binding["binding_digest"]: raise OperateRejected("receipt source binding mismatch")
    if receipt["object_id"] != po or receipt["object_id"] != eo: raise OperateRejected("receipt object identity mismatch")
    if receipt["plan_version"] != pv or receipt["plan_version"] != epv: raise OperateRejected("receipt plan version mismatch")
    if receipt["target_digest"] != pt or receipt["required_postcondition_spec_digest"] != digest(required): raise OperateRejected("receipt target/postcondition specification mismatch")
    rr = _sha(receipt["result_digest"],"receipt.result_digest"); pcs=receipt["postconditions"]
    if type(pcs) is not list or not pcs: raise OperateRejected("receipt.postconditions must be a non-empty list")
    seen=set(); passed=True
    for i,item in enumerate(pcs):
        item=_obj(item,f"receipt.postconditions[{i}]"); _closed(item,{"id","passed","evidence_digest"},"postcondition")
        ident=_str(item["id"],f"receipt.postconditions[{i}].id")
        if ident in seen: raise OperateRejected("duplicate postcondition id")
        seen.add(ident); passed &= _bool(item["passed"],f"postcondition {ident}.passed"); _sha(item["evidence_digest"],f"postcondition {ident}.evidence_digest")
    if sorted(seen) != required: raise OperateRejected("receipt postconditions do not exactly satisfy the required set")
    status=_str(health["status"],"health.status"); incidents=health["unresolved_incidents"]
    if type(incidents) is not list or any(type(x) is not str or not x for x in incidents): raise OperateRejected("health.unresolved_incidents must be a string list")
    rc,rl=_int(retry["count"],"retry.count"),_int(retry["limit"],"retry.limit")
    guide=packet.get("mata_guide")
    if guide is not None:
        guide=_obj(guide,"mata_guide"); _closed(guide,{"guide_id","directive","standing"},"MATA guide"); _str(guide["guide_id"],"mata_guide.guide_id")
        if guide["directive"] not in ALLOWED_GUIDES or guide["standing"] != "EVIDENCE_ONLY": raise OperateRejected("invalid MATA guide")
    residuals={"plan_execution":po!=eo or pv!=epv,"execution_world":eo!=wo or er!=wd,"plan_world":po!=wo or pt!=wd}; bd=binding["binding_digest"]; cd=context["context_digest"]; pd=digest(packet)
    if athena != binding["athena"]["head"] or runtime != binding["runtime"]["head"]: return _result("REBIND" if caps["rebind"] else "HOLD","SOURCE_BINDING_MISMATCH",residuals,"packet heads do not match the supplied source binding",bd,cd,pd)
    if observed > context["now"]: return _result("HOLD","CLOCK_INVERSION",residuals,"world observation is future-dated",bd,cd,pd)
    if context["now"]-observed > max_age: return _result("REBIND" if caps["rebind"] else "HOLD","OBSERVATION_STALE",residuals,"world observation exceeded freshness bound",bd,cd,pd)
    if rsha != digest(receipt): return _result("REPAIR" if caps["repair"] else "HOLD","RECEIPT_BINDING_MISMATCH",residuals,"receipt bytes do not match execution binding",bd,cd,pd)
    if rr != er: return _result("REPAIR" if caps["repair"] else "HOLD","RECEIPT_RESULT_MISMATCH",residuals,"receipt result does not match execution result",bd,cd,pd)
    if status != "HEALTHY" or incidents or exit_code != 0:
        if retryable and rc < rl and caps["retry"]: return _result("RETRY","RUNTIME_INCIDENT",residuals,"typed runtime incident has retry budget",bd,cd,pd)
        if caps["escalate"]: return _result("ESCALATE","RUNTIME_INCIDENT",residuals,"runtime incident is not lawfully retryable",bd,cd,pd)
        return _result("HOLD","RUNTIME_INCIDENT",residuals,"runtime incident has no lawful recovery capability",bd,cd,pd)
    if not passed:
        if caps["rollback"]: return _result("ROLLBACK","POSTCONDITION_FAILED",residuals,"receipt success did not establish postconditions",bd,cd,pd)
        return _result("REPAIR" if caps["repair"] else "HOLD","POSTCONDITION_FAILED",residuals,"postconditions failed without expanded authority",bd,cd,pd)
    if residuals["plan_execution"]: return _result("REPLAN" if caps["replan"] else "HOLD","PLAN_EXECUTION_DIVERGENCE",residuals,"execution is not bound to the current plan",bd,cd,pd)
    if residuals["execution_world"]: return _result("REPAIR" if caps["repair"] else "HOLD","EXECUTION_WORLD_DIVERGENCE",residuals,"receipt result is not the observed world",bd,cd,pd)
    if residuals["plan_world"]: return _result("REPLAN" if caps["replan"] else "HOLD","PLAN_WORLD_DIVERGENCE",residuals,"observed world did not reach plan target",bd,cd,pd)
    return _result("COMPLETE" if completion else "CONTINUE","NONE",residuals,"binding-relative receipt and observed postconditions agree" if completion else "state is coherent but completion was not requested",bd,cd,pd)
