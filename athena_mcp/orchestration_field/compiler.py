from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

FIELD_KINDS = (
    "MEASURE", "CALIBRATE", "RETRIEVE", "EXECUTE", "REPAIR", "DEVELOP",
    "AUTHORITY", "REVIEW", "IMPLEMENT", "TEST", "BRIDGE", "SUCCESSOR",
)
AOR_MEASUREMENT_FIELDS = {
    "readiness", "gain", "independence", "bridge", "cost", "delta_j", "information_gain", "option_value",
    "evidence", "connection", "replay", "navigation", "reconstruction", "implementation", "novelty",
    "duplicate", "fake", "bloat", "unsupported", "unhandled_contradiction", "coordinate_loss", "resource_cost",
}
ROUTING_METADATA_FIELDS = {
    "claim_id", "min_authority", "resolved", "branch_id", "requires", "require_coordinates", "coordinates",
}
_STRUCTURAL = {
    "id", "kind", "operation", "target_ref", "payload", "dependencies", "source_refs", "field_origin",
    "metric_state", "metric_conflicts", "routing_conflicts",
}


def _digest(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def _canon(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    except (TypeError, ValueError):
        return repr(value)


def _proposal(kind, operation, target_ref, payload=None, source_refs=None, dependencies=None, explicit_fields=None):
    kind = str(kind or "").upper()
    operation = str(operation or "").strip()
    target_ref = str(target_ref or "").strip()
    if kind not in FIELD_KINDS:
        raise ValueError(f"unknown FIELD kind {kind}")
    if not operation or not target_ref:
        raise ValueError("FIELD proposal requires operation and target_ref")
    deps = sorted({str(x) for x in (dependencies or []) if str(x)})
    body = dict(payload or {})
    signature = {"kind": kind, "operation": operation, "target_ref": target_ref, "payload": body, "dependencies": deps}
    cid = "PHI." + _digest(signature)[:24]
    out = {
        "id": cid,
        **signature,
        "source_refs": sorted({str(x) for x in (source_refs or []) if str(x)}),
        "field_origin": [],
        "metric_state": "EXPLICIT" if explicit_fields else "UNMEASURED",
    }
    if explicit_fields:
        out.update(dict(explicit_fields))
    return out


def _conflicts(prior, new, fields):
    out = {}
    for field in sorted(fields):
        if field in prior and field in new and _canon(prior[field]) != _canon(new[field]):
            out[field] = {"left": prior[field], "right": new[field]}
    return out


def _merge(proposals):
    """Merge only exact action signatures; semantic similarity never collapses.

    Generated duplicates contribute provenance only. Two explicit packets with
    contradictory AOR metrics/routing metadata fail closed: disputed routing or
    ranking operands are removed and candidate metric_state becomes CONFLICT.
    """
    merged = {}
    merges = []
    for raw in proposals:
        p = dict(raw)
        prior = merged.get(p["id"])
        if prior is None:
            merged[p["id"]] = p
            continue
        prior["source_refs"] = sorted(set(prior.get("source_refs") or []) | set(p.get("source_refs") or []))
        prior["field_origin"] = sorted(set(prior.get("field_origin") or []) | set(p.get("field_origin") or []))
        merges.append({"candidate": p["id"], "merged_sources": p.get("source_refs") or []})
        both_explicit = prior.get("metric_state") in {"EXPLICIT", "CONFLICT"} and p.get("metric_state") == "EXPLICIT"
        if both_explicit:
            metric_conflict = _conflicts(prior, p, AOR_MEASUREMENT_FIELDS)
            routing_conflict = _conflicts(prior, p, ROUTING_METADATA_FIELDS)
            if metric_conflict:
                prior.setdefault("metric_conflicts", []).append(metric_conflict)
                for field in AOR_MEASUREMENT_FIELDS:
                    prior.pop(field, None)
                prior["metric_state"] = "CONFLICT"
            if routing_conflict:
                prior.setdefault("routing_conflicts", []).append(routing_conflict)
                for field in ROUTING_METADATA_FIELDS:
                    prior.pop(field, None)
                prior["metric_state"] = "CONFLICT"
            if not metric_conflict and not routing_conflict and prior.get("metric_state") != "CONFLICT":
                for field in AOR_MEASUREMENT_FIELDS | ROUTING_METADATA_FIELDS:
                    if field in p and field not in prior:
                        prior[field] = p[field]
        elif prior.get("metric_state") not in {"EXPLICIT", "CONFLICT"} and p.get("metric_state") == "EXPLICIT":
            for key, value in p.items():
                if key not in _STRUCTURAL:
                    prior[key] = value
            prior["metric_state"] = "EXPLICIT"
    return [merged[k] for k in sorted(merged)], merges


def _from_extraction(frontier):
    out = []
    for task in frontier or []:
        if str(task.get("status") or "PLANNED").upper() != "PLANNED":
            continue
        p = _proposal(
            "EXECUTE", "execute_extraction_transform", task.get("task_id"),
            {"transform": task.get("transform"), "seed_ref": task.get("seed_ref"), "depth": task.get("depth")},
            [task.get("task_id"), task.get("run_id")],
            [task.get("parent_task_id")] if task.get("parent_task_id") else [],
        )
        p["field_origin"] = ["SX.1"]
        out.append(p)
    return out


def _from_retrieval(rag):
    out = []
    rag = dict(rag or {})
    run_ref = rag.get("run_id") or rag.get("query_ref") or "RAG.1"
    for item in rag.get("measurement_plan") or []:
        p = _proposal("MEASURE", "measure_retrieval_candidate", item.get("candidate"), {"defects": item.get("defects") or []}, [run_ref])
        p["field_origin"] = ["RAG.1"]
        out.append(p)
    coverage = rag.get("coverage") or {}
    for role in coverage.get("missing_roles") or []:
        p = _proposal("RETRIEVE", "acquire_missing_retrieval_role", f"role:{role}", {"role": role}, [run_ref])
        p["field_origin"] = ["RAG.1"]
        out.append(p)
    for facet in coverage.get("missing_facets") or []:
        p = _proposal("RETRIEVE", "acquire_missing_retrieval_facet", f"facet:{facet}", {"facet": facet}, [run_ref])
        p["field_origin"] = ["RAG.1"]
        out.append(p)
    return out


def _from_authority(plan):
    out = []
    for item in plan or []:
        route = str(item.get("route") or "resolve_authority")
        kind = "TEST" if route == "execute_witnessed_test" else "AUTHORITY"
        p = _proposal(
            kind, route, item.get("candidate"),
            {"reason": item.get("reason"), "minimum": item.get("minimum"), "current": item.get("current"), "authority_status": item.get("authority_status")},
            [item.get("candidate")],
        )
        p["field_origin"] = ["Y.1"]
        out.append(p)
    return out


def _from_gap(gap):
    out = []
    gap = dict(gap or {})
    run_ref = gap.get("run_id") or "GAP.1"
    for item in gap.get("measurement_plan") or []:
        p = _proposal("MEASURE", "measure_gap_residual", item.get("target"), {"node": item.get("node"), "defects": item.get("defects") or []}, [run_ref])
        p["field_origin"] = ["GAP.1"]
        out.append(p)
    for row in gap.get("gap") or []:
        p = _proposal("DEVELOP", "address_gap_target", row.get("id"), {"node": row.get("node"), "residual_score": row.get("residual_score")}, [run_ref])
        p["field_origin"] = ["GAP.1"]
        out.append(p)
    return out


def _from_hug(invocations):
    out = []
    for inv in invocations or []:
        status = str(inv.get("status") or "").upper()
        iid = inv.get("invocation_id")
        if status == "PLANNED":
            kind, op = "EXECUTE", "execute_hug_invocation"
        elif status == "FAILED":
            kind, op = "REPAIR", "repair_hug_failure"
        else:
            continue
        p = _proposal(kind, op, iid, {"impl_id": inv.get("impl_id"), "failure": inv.get("failure")}, [iid, inv.get("impl_id")])
        p["field_origin"] = ["HUG.ABI.1"]
        out.append(p)
    return out


def _from_branches(branches):
    out = []
    for branch in branches or []:
        status = str(branch.get("status") or branch.get("state") or "").upper()
        if status != "REVIEW":
            continue
        ref = branch.get("branch_id")
        p = _proposal(
            "REVIEW", "review_branch_reactivation", ref,
            {"basis_id": branch.get("basis_id"), "ewma_reward": branch.get("ewma_reward", branch.get("ewma")), "last_trigger_ref": branch.get("last_trigger_ref")},
            [ref, branch.get("last_eid")],
        )
        p["field_origin"] = ["BRANCH_EVOLUTION"]
        out.append(p)
    return out


def _from_aor(aor):
    out = []
    aor = dict(aor or {})
    run_ref = aor.get("run_id") or "AORRUN"
    for item in aor.get("measurement_plan") or []:
        target = item.get("candidate") or item.get("id")
        p = _proposal("MEASURE", "measure_aor_candidate", target, {"defects": item.get("defects") or item.get("missing_metrics") or item.get("missing") or []}, [run_ref])
        p["field_origin"] = ["AOR.3"]
        out.append(p)
    for item in aor.get("calibration_plan") or aor.get("calibration_frontier") or []:
        target = item.get("candidate") or item.get("id")
        p = _proposal("CALIBRATE", "calibrate_aor_candidate", target, {"metrics": item.get("metrics") or item.get("defects") or []}, [run_ref])
        p["field_origin"] = ["AOR.3"]
        out.append(p)
    return out


def _from_explicit(explicit):
    out = []
    reserved = {"kind", "operation", "target_ref", "payload", "source_refs", "dependencies", "field_origin", "id", "metric_state", "metric_conflicts", "routing_conflicts"}
    for item0 in explicit or []:
        item = dict(item0)
        fields = {k: v for k, v in item.items() if k not in reserved}
        p = _proposal(item.get("kind"), item.get("operation"), item.get("target_ref"), item.get("payload"), item.get("source_refs"), item.get("dependencies"), fields or None)
        p["field_origin"] = sorted({str(x) for x in (item.get("field_origin") or ["EXPLICIT"]) if str(x)})
        out.append(p)
    return out


def build_field(seed_ref: str, module_outputs: Mapping[str, Any], explicit_candidates: Iterable[Mapping[str, Any]] = (), ecosystem: Mapping[str, Any] | None = None):
    seed_ref = str(seed_ref or "").strip()
    if not seed_ref:
        raise ValueError("seed_ref required")
    modules = dict(module_outputs or {})
    proposals = []
    proposals += _from_extraction(modules.get("extraction_frontier"))
    proposals += _from_retrieval(modules.get("retrieval"))
    proposals += _from_authority(modules.get("authority_plan"))
    proposals += _from_gap(modules.get("gap"))
    proposals += _from_hug(modules.get("hug_invocations"))
    proposals += _from_branches(modules.get("branches"))
    proposals += _from_aor(modules.get("aor"))
    proposals += _from_explicit(explicit_candidates)
    candidates, exact_merges = _merge(proposals)
    edges = []
    for candidate in candidates:
        for src in candidate["source_refs"]:
            edges.append({"src": src, "relation": "proposes", "dst": candidate["id"]})
        for dep in candidate["dependencies"]:
            edges.append({"src": candidate["id"], "relation": "depends", "dst": dep})
    unmeasured = [c["id"] for c in candidates if c.get("metric_state") != "EXPLICIT"]
    conflicts = [c["id"] for c in candidates if c.get("metric_state") == "CONFLICT"]
    return {
        "version": "FIELD.1",
        "seed_ref": seed_ref,
        "ecosystem": dict(ecosystem or {}),
        "candidates": candidates,
        "candidate_ids": [c["id"] for c in candidates],
        "unmeasured_candidate_ids": unmeasured,
        "conflict_candidate_ids": conflicts,
        "exact_signature_merges": exact_merges,
        "field_edges": edges,
        "module_presence": sorted(k for k, v in modules.items() if v not in (None, [], {})),
        "handoff_to_aor": candidates,
        "law": "assemble actual module-emitted action proposals; exact action signatures may merge provenance only; generated proposals receive no invented AOR metrics; explicit metric/routing disagreement fails closed to CONFLICT and strips disputed ranking/routing operands; semantic similarity never collapses",
    }
