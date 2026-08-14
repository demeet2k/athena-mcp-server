from __future__ import annotations

import copy
from typing import Any, Mapping, MutableMapping

from .nexus4d_types import (
    _apply_delta, _authority_checks, _canonical, _clean_id, _digest,
    _eval_predicate, _evidence_meets, _finite_number, _merge_evidence,
    _normalize_evidence, _normalize_paths, _path_covered, normalize_spec,
)
from .nexus4d_planner import (
    _candidate_readset_digest, _decision_cone, _empty_node_state,
    _invariant_statuses, _require_node, plan_snapshot,
)

def _apply_event(spec: MutableMapping[str, Any], snapshot: MutableMapping[str, Any], event_type: str, payload: Mapping[str, Any], seq: int, authority_states: Mapping[str, Mapping[str, Any]] | None = None) -> None:
    if event_type == "STATE_OBSERVED":
        changed = _apply_delta(snapshot["state"], payload.get("state_delta") or {})
        if not payload.get("source_ref"):
            raise ValueError("STATE_OBSERVED requires source_ref")
        affected = _decision_cone(spec, changed)
        for node_id in sorted(affected):
            node_state = snapshot["node_state"][node_id]
            if node_state["stage"] in {"CLAIMED", "CANDIDATE", "VERIFIED"}:
                node_state["stage"] = "INVALIDATED"
                node_state["holds"].append({"reason": "RELEVANT_STATE_DRIFT", "seq": seq, "changed_paths": changed})
        snapshot["last_changed_paths"] = changed
        return

    if event_type == "AUTHORITY_UPDATED":
        if not payload.get("authority_ref"):
            raise ValueError("AUTHORITY_UPDATED requires authority_ref")
        add = payload.get("add") or []
        remove = payload.get("remove") or []
        if not isinstance(add, list) or not isinstance(remove, list):
            raise ValueError("AUTHORITY_UPDATED add/remove must be arrays")
        authorities = set(snapshot["authorities"])
        authorities.update(_clean_id(value, "authority") for value in add)
        authorities.difference_update(_clean_id(value, "authority") for value in remove)
        snapshot["authorities"] = sorted(authorities)
        return

    if event_type in {"CAPACITY_UPDATED", "QUEUE_UPDATED"}:
        node_id, node, node_state = _require_node(spec, snapshot, payload)
        if event_type == "CAPACITY_UPDATED":
            capacity = int(payload.get("capacity"))
            if capacity < 1 or capacity > 10000:
                raise ValueError("capacity must be in [1,10000]")
            node_state["capacity"] = capacity
        else:
            depth = int(payload.get("queue_depth"))
            if depth < 0 or depth > 1000000:
                raise ValueError("queue_depth must be in [0,1000000]")
            node_state["queue_depth"] = depth
        node_state["last_event_seq"] = seq
        return

    if event_type == "CONTRADICTION_RECORDED":
        left = _clean_id(payload.get("left_claim_ref"), "left_claim_ref")
        right = _clean_id(payload.get("right_claim_ref"), "right_claim_ref")
        if left == right:
            raise ValueError("contradiction claims must be distinct")
        record = {
            "contradiction_id": _digest("NXCONTRA", [left, right, payload.get("scope")]),
            "left_claim_ref": left,
            "right_claim_ref": right,
            "scope": payload.get("scope"),
            "discrimination_obligation": payload.get("discrimination_obligation") or "SELECT_EVIDENCE_BEARING_DISCRIMINATING_TEST",
            "seq": seq,
            "status": "OPEN",
        }
        snapshot["contradictions"].append(record)
        return

    if event_type.startswith("TOPOLOGY_"):
        change_id = _clean_id(payload.get("change_id"), "topology.change_id")
        records = snapshot["topology_candidates"]
        if event_type == "TOPOLOGY_CANDIDATE":
            if change_id in records:
                raise ValueError("topology change already exists")
            if not payload.get("patch") or not payload.get("rollback") or not payload.get("falsifier") or not payload.get("replacement_spec"):
                raise ValueError("topology candidate requires patch, replacement_spec, rollback and falsifier")
            replacement_raw = copy.deepcopy(payload["replacement_spec"])
            replacement_raw["initial_state"] = copy.deepcopy(snapshot["state"])
            replacement = normalize_spec(replacement_raw)
            records[change_id] = {
                "status": "CANDIDATE",
                "proposal": {key: copy.deepcopy(value) for key, value in payload.items() if key != "replacement_spec"},
                "base_spec": copy.deepcopy(spec),
                "base_spec_digest": _digest("NXSPEC", spec),
                "base_topology_epoch": int(snapshot["topology_epoch"]),
                "replacement_spec": replacement,
                "replacement_spec_digest": _digest("NXSPEC", replacement),
                "tests": None,
                "seq": seq,
            }
            return
        if change_id not in records:
            raise ValueError("unknown topology change")
        record = records[change_id]
        if event_type == "TOPOLOGY_TESTED":
            observed_gain = _finite_number(payload.get("observed_gain"), "topology.observed_gain")
            record["status"] = "TESTED"
            record["tests"] = copy.deepcopy(payload)
            record["observed_gain"] = observed_gain
            record["invariant_regressions"] = list(payload.get("invariant_regressions") or [])
            record["seq"] = seq
            return
        if event_type == "TOPOLOGY_PROMOTED":
            if record.get("status") != "TESTED":
                raise ValueError("topology promotion requires TESTED status")
            if float(record.get("observed_gain", 0.0)) <= 0 or record.get("invariant_regressions"):
                raise ValueError("topology promotion requires positive observed gain and zero invariant regressions")
            if not payload.get("authority_ref"):
                raise ValueError("topology promotion requires authority_ref")
            replacement = copy.deepcopy(record.get("replacement_spec") or {})
            if not replacement:
                raise ValueError("topology promotion has no replacement_spec")
            topology_requirements = list(spec.get("topology_authority_claims") or [])
            topology_requirements.extend(replacement.get("topology_authority_claims") or [])
            topology_checks = _authority_checks(topology_requirements, authority_states)
            if any(not item["passed"] for item in topology_checks):
                raise ValueError("topology promotion lacks required canonical authority claims")
            record["authority_claim_checks"] = topology_checks
            failed_current = [item["id"] for item in replacement["hard_invariants"] if not _eval_predicate(item["predicate"], snapshot["state"])["passed"]]
            if failed_current:
                raise ValueError(f"replacement topology hard invariants fail on current state {failed_current}")
            new_nodes = {item["id"]: item for item in replacement["nodes"]}
            old_node_state = snapshot["node_state"]
            removed = sorted(set(old_node_state) - set(new_nodes))
            active_removed = [node_id for node_id in removed if old_node_state[node_id]["stage"] in {"CLAIMED", "CANDIDATE", "VERIFIED"}]
            if active_removed:
                raise ValueError(f"replacement topology removes active nodes {active_removed}")
            for node_id in removed:
                snapshot["retired_node_state"][node_id] = old_node_state[node_id]
            snapshot["node_state"] = {
                node_id: copy.deepcopy(old_node_state[node_id]) if node_id in old_node_state else _empty_node_state(new_nodes[node_id], seq)
                for node_id in sorted(new_nodes)
            }
            for node_id, node in new_nodes.items():
                snapshot["node_state"][node_id]["capacity"] = int(node["capacity"])
            spec.clear()
            spec.update(replacement)
            record["status"] = "PROMOTED"
            record["authority_ref"] = payload["authority_ref"]
            record["seq"] = seq
            snapshot["topology_epoch"] = int(snapshot["topology_epoch"]) + 1
            return
        if event_type == "TOPOLOGY_ROLLED_BACK":
            if record.get("status") != "PROMOTED":
                raise ValueError("topology rollback requires PROMOTED status")
            if not payload.get("rollback_receipt") or not payload.get("authority_ref"):
                raise ValueError("topology rollback requires rollback_receipt and authority_ref")
            base_spec = copy.deepcopy(record.get("base_spec") or {})
            if not base_spec:
                raise ValueError("topology rollback has no preserved base_spec")
            topology_requirements = list(spec.get("topology_authority_claims") or [])
            topology_requirements.extend(base_spec.get("topology_authority_claims") or [])
            topology_checks = _authority_checks(topology_requirements, authority_states)
            if any(not item["passed"] for item in topology_checks):
                raise ValueError("topology rollback lacks required canonical authority claims")
            failed_current = [item["id"] for item in base_spec["hard_invariants"] if not _eval_predicate(item["predicate"], snapshot["state"])["passed"]]
            if failed_current:
                raise ValueError(f"rollback topology hard invariants fail on current state {failed_current}")
            base_nodes = {item["id"]: item for item in base_spec["nodes"]}
            current_node_state = snapshot["node_state"]
            removed = sorted(set(current_node_state) - set(base_nodes))
            active_removed = [node_id for node_id in removed if current_node_state[node_id]["stage"] in {"CLAIMED", "CANDIDATE", "VERIFIED"}]
            if active_removed:
                raise ValueError(f"rollback topology removes active nodes {active_removed}")
            for node_id in removed:
                snapshot["retired_node_state"][node_id] = current_node_state[node_id]
            restored = {}
            for node_id in sorted(base_nodes):
                if node_id in current_node_state:
                    restored[node_id] = copy.deepcopy(current_node_state[node_id])
                elif node_id in snapshot["retired_node_state"]:
                    restored[node_id] = copy.deepcopy(snapshot["retired_node_state"].pop(node_id))
                else:
                    restored[node_id] = _empty_node_state(base_nodes[node_id], seq)
                restored[node_id]["capacity"] = int(base_nodes[node_id]["capacity"])
            snapshot["node_state"] = restored
            spec.clear()
            spec.update(base_spec)
            record["status"] = "ROLLED_BACK"
            record["rollback_receipt"] = payload["rollback_receipt"]
            record["rollback_authority_ref"] = payload["authority_ref"]
            record["seq"] = seq
            snapshot["topology_epoch"] = int(snapshot["topology_epoch"]) + 1
            return

    node_id, node, node_state = _require_node(spec, snapshot, payload)

    if event_type == "CLAIMED":
        reclaim_expired = node_state["stage"] == "CLAIMED" and int((node_state.get("claim") or {}).get("lease_until_revision", snapshot["revision"])) < int(snapshot["revision"])
        if node_state["stage"] not in {"OPEN", "INVALIDATED"} and not reclaim_expired:
            raise ValueError(f"node {node_id} cannot be claimed from {node_state['stage']}")
        current_plan = plan_snapshot(spec, snapshot, authority_states=authority_states)
        selected = {item["node_id"]: item for item in current_plan["batch"]}
        if node_id not in selected:
            raise ValueError(f"node {node_id} is not in the current lawful nexus batch")
        claim_id = _clean_id(payload.get("claim_id"), "claim_id")
        readset_digest = _clean_id(payload.get("readset_digest"), "readset_digest")
        if readset_digest != selected[node_id]["nexus_packet"]["readset_digest"]:
            raise ValueError("claim readset_digest is stale or mismatched")
        writeset = _normalize_paths(payload.get("writeset", node["writeset"]), "claim.writeset")
        if sorted(writeset) != sorted(node["writeset"]):
            raise ValueError("claim writeset must exactly match node contract")
        lease_until = int(payload.get("lease_until_revision", int(snapshot["revision"]) + 1))
        if lease_until < int(snapshot["revision"]):
            raise ValueError("claim lease is already expired")
        node_state["stage"] = "CLAIMED"
        node_state["attempt"] = int(node_state["attempt"]) + 1
        node_state["claim"] = {
            "claim_id": claim_id,
            "actor": str(payload.get("actor") or "agent"),
            "readset_digest": readset_digest,
            "writeset": writeset,
            "lease_until_revision": lease_until,
            "packet_id": selected[node_id]["nexus_packet"]["packet_id"],
            "authority_receipts": copy.deepcopy(authority_states or {}),
        }
        node_state["candidate"] = None
        node_state["holds"] = []
    elif event_type == "CANDIDATE_PRODUCED":
        if node_state["stage"] != "CLAIMED" or not node_state.get("claim"):
            raise ValueError("candidate requires an active claim")
        if payload.get("claim_id") != node_state["claim"]["claim_id"]:
            raise ValueError("candidate claim_id does not match active claim")
        if int(node_state["claim"].get("lease_until_revision", snapshot["revision"])) < int(snapshot["revision"]):
            raise ValueError("candidate claim lease expired")
        candidate_id = _clean_id(payload.get("candidate_id"), "candidate_id")
        readset_digest = _clean_id(payload.get("readset_digest"), "candidate.readset_digest")
        if readset_digest != node_state["claim"]["readset_digest"]:
            raise ValueError("candidate readset_digest does not match claim")
        state_delta = payload.get("state_delta") or {}
        if not isinstance(state_delta, Mapping):
            raise ValueError("candidate state_delta must be an object")
        undeclared = sorted(str(path) for path in state_delta if not any(_path_covered(str(path), declared) for declared in node["writeset"]))
        if undeclared:
            raise ValueError(f"candidate state_delta exceeds declared writeset {undeclared}")
        node_state["stage"] = "CANDIDATE"
        node_state["candidate"] = {
            "candidate_id": candidate_id,
            "claim_id": node_state["claim"]["claim_id"],
            "readset_digest": readset_digest,
            "state_delta": copy.deepcopy(state_delta),
            "claims": copy.deepcopy(payload.get("claims") or []),
            "unresolved_unknowns": copy.deepcopy(payload.get("unresolved_unknowns") or []),
            "produced_refs": copy.deepcopy(payload.get("produced_refs") or []),
        }
    elif event_type == "EVIDENCE_RECORDED":
        if node_state["stage"] not in {"CANDIDATE", "VERIFIED"} or not node_state.get("candidate"):
            raise ValueError("evidence requires a candidate")
        if payload.get("candidate_id") != node_state["candidate"]["candidate_id"]:
            raise ValueError("evidence candidate_id mismatch")
        profile = _normalize_evidence(payload.get("profile"), "event.evidence.profile")
        node_state["evidence"] = _merge_evidence(node_state["evidence"], profile)
        refs = payload.get("refs") or []
        if not isinstance(refs, list) or not refs:
            raise ValueError("evidence requires non-empty refs")
        for ref in refs:
            text = _clean_id(ref, "evidence.ref")
            if text not in node_state["evidence_refs"]:
                node_state["evidence_refs"].append(text)
    elif event_type == "VERIFIED":
        if node_state["stage"] != "CANDIDATE" or not node_state.get("candidate"):
            raise ValueError("verification requires CANDIDATE stage")
        if payload.get("candidate_id") != node_state["candidate"]["candidate_id"]:
            raise ValueError("verification candidate_id mismatch")
        if payload.get("passed") is not True:
            node_state["stage"] = "HELD"
            node_state["holds"].append({"reason": "VERIFICATION_FAILED", "witness": payload.get("witness"), "seq": seq})
        else:
            if not payload.get("verifier_ref"):
                raise ValueError("passed verification requires verifier_ref")
            if not _evidence_meets(node_state["evidence"], node["evidence_threshold"]):
                raise ValueError("evidence profile does not meet node threshold")
            node_state["stage"] = "VERIFIED"
            node_state["candidate"]["verifier_ref"] = payload["verifier_ref"]
    elif event_type == "COMMITTED":
        if node_state["stage"] != "VERIFIED" or not node_state.get("candidate"):
            raise ValueError("commit requires VERIFIED candidate")
        if payload.get("candidate_id") != node_state["candidate"]["candidate_id"]:
            raise ValueError("commit candidate_id mismatch")
        if int((node_state.get("claim") or {}).get("lease_until_revision", -1)) < int(snapshot["revision"]):
            raise ValueError("commit claim lease expired")
        missing_authority = sorted(set(node["required_authorities"]) - set(snapshot["authorities"]))
        if missing_authority:
            raise ValueError(f"commit lacks required authority scope {missing_authority}")
        canonical_checks = _authority_checks(node["required_authority_claims"], authority_states)
        if any(not item["passed"] for item in canonical_checks):
            raise ValueError("commit lacks required canonical authority claims")
        current_digest = _candidate_readset_digest(spec, snapshot, node_id)
        if current_digest != node_state["candidate"]["readset_digest"]:
            raise ValueError("candidate readset is stale; relevant state drift requires re-execution")
        if not payload.get("authority_ref"):
            raise ValueError("commit requires authority_ref")
        state_delta = node_state["candidate"]["state_delta"]
        declared_delta = payload.get("state_delta")
        if declared_delta is not None and _canonical(declared_delta) != _canonical(state_delta):
            raise ValueError("commit state_delta differs from verified candidate")
        changed = _apply_delta(snapshot["state"], state_delta)
        invariant_statuses = _invariant_statuses(spec, snapshot)
        failed = [item["id"] for item in invariant_statuses if not item["passed"]]
        if failed:
            raise ValueError(f"commit violates hard invariants {failed}")
        affected = _decision_cone(spec, changed)
        for affected_id in sorted(affected - {node_id}):
            affected_state = snapshot["node_state"][affected_id]
            if affected_state["stage"] in {"CLAIMED", "CANDIDATE", "VERIFIED"}:
                affected_state["stage"] = "INVALIDATED"
                affected_state["holds"].append({"reason": "DECISION_CONE_INVALIDATED", "source_node": node_id, "changed_paths": changed, "seq": seq})
        node_state["stage"] = "COMMITTED"
        node_state["candidate"]["authority_ref"] = payload["authority_ref"]
        node_state["candidate"]["authority_claim_checks"] = canonical_checks
        node_state["candidate"]["commit_ref"] = payload.get("commit_ref") or _digest("NXCOMMIT", [node_id, node_state["candidate"]["candidate_id"], state_delta])
        snapshot["last_changed_paths"] = changed
    elif event_type == "CONSUMED":
        if node_state["stage"] != "COMMITTED":
            raise ValueError("consumption requires COMMITTED stage")
        consumer = _clean_id(payload.get("consumer"), "consumer")
        expected_consumer = node["consumer"]
        if expected_consumer and consumer != expected_consumer:
            raise ValueError("consumer does not match node contract")
        if not payload.get("receipt_ref"):
            raise ValueError("consumption requires receipt_ref")
        node_state["consumer_receipts"].append({"consumer": consumer, "receipt_ref": payload["receipt_ref"], "seq": seq})
        node_state["stage"] = "CONSUMED"
    elif event_type == "OUTCOME_OBSERVED":
        if node_state["stage"] != "CONSUMED":
            raise ValueError("outcome observation requires CONSUMED stage")
        if not payload.get("observation_ref"):
            raise ValueError("outcome observation requires observation_ref")
        changed = _apply_delta(snapshot["state"], payload.get("state_delta") or {})
        node_state["outcome_receipts"].append({"observation_ref": payload["observation_ref"], "scope": payload.get("scope"), "seq": seq})
        node_state["stage"] = "OUTCOME_OBSERVED"
        snapshot["last_changed_paths"] = changed
    elif event_type == "HELD":
        reason = _clean_id(payload.get("reason"), "hold.reason")
        node_state["stage"] = "HELD"
        node_state["holds"].append({"reason": reason, "witness": payload.get("witness"), "seq": seq})
    elif event_type == "RELEASED":
        if node_state["stage"] not in {"CLAIMED", "HELD", "INVALIDATED"}:
            raise ValueError("release requires CLAIMED, HELD or INVALIDATED stage")
        node_state["stage"] = "OPEN"
        node_state["claim"] = None
        node_state["candidate"] = None
        node_state["holds"] = []
        node_state["wait_since_revision"] = int(snapshot["revision"])
    elif event_type == "INVALIDATED":
        if node_state["stage"] in {"COMMITTED", "CONSUMED", "OUTCOME_OBSERVED"} and not payload.get("authority_ref"):
            raise ValueError("invalidating durable lifecycle state requires authority_ref")
        node_state["stage"] = "INVALIDATED"
        node_state["holds"].append({"reason": payload.get("reason") or "EXPLICIT_INVALIDATION", "witness": payload.get("witness"), "seq": seq})
    else:
        raise ValueError(f"unhandled event type {event_type}")
    node_state["last_event_seq"] = seq


def _snapshot_digest(snapshot: Mapping[str, Any]) -> str:
    return _digest("NXSNAP", snapshot)
