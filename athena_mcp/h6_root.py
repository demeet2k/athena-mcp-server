from __future__ import annotations

import json
from typing import Any, Iterable

from .identity import digest

ARTIFACT = "ATHENA.H6.ROOT.RUNTIME.V1"
ACTIVE_EPOCH = "EPOCH-B-EIGHT-BLOCK"


class H6RootRuntime:
    """Read-only constitutional facade over existing ATHENA root primitives.

    This facade adds no second object/coordinate/transform/evidence store, no
    scheduler, no execution engine and no promotion authority. It normalizes
    existing primitives into the six H01-H06 constitutional decisions.
    """

    def __init__(self, core, crystal):
        self.core = core
        self.crystal = crystal
        self.s = core.s

    @staticmethod
    def _norm_ids(values: Iterable[str] | None) -> list[str]:
        return sorted({str(v) for v in (values or []) if str(v)})

    def _existing_oid(self, oid: str) -> bool:
        return bool(self.s.one("SELECT oid FROM objects WHERE oid=?", (oid,)))

    # H01 -----------------------------------------------------------------
    def identity_decide(self, input_ref: str, candidate_oids: Iterable[str] | None = None) -> dict[str, Any]:
        direct = self.core.navigate(input_ref)
        candidates = set(self._norm_ids(candidate_oids))
        alias_rows = self.s.rows(
            "SELECT dst,eid FROM edges WHERE src=? AND relation='ALIAS_OF' ORDER BY created_at",
            (input_ref,),
        )
        alias_targets = {row["dst"] for row in alias_rows if self._existing_oid(row["dst"])}

        if direct.get("found"):
            selected = direct["object"]["oid"]
            candidates.add(selected)
            decision = "RESOLVED_EXISTING"
        else:
            valid = {oid for oid in candidates if self._existing_oid(oid)}
            if alias_targets:
                valid = valid & alias_targets if valid else alias_targets
            candidates = valid
            if len(candidates) == 1:
                selected = next(iter(candidates))
                decision = "RESOLVED_EXISTING"
            elif len(candidates) > 1:
                selected = None
                decision = "AMBIG_HOLD"
            else:
                selected = None
                decision = "CREATE_NEW"

        ordered = sorted(candidates)
        return {
            "artifact": "ATHENA.H01.IDENTITY.DECISION.V1",
            "input_ref": input_ref,
            "candidate_oids": ordered,
            "selected_oid": selected,
            "decision": decision,
            "type_compatibility": {oid: "UNKNOWN" for oid in ordered},
            "referent_compatibility": {
                oid: "ALIAS_OBSERVED" if oid in alias_targets else "UNKNOWN" for oid in ordered
            },
            "lineage_compatibility": {oid: "OBSERVED_OBJECT" for oid in ordered},
            "context_compatibility": {oid: "UNKNOWN" for oid in ordered},
            "contradictions": [],
            "alias_eids": [row["eid"] for row in alias_rows],
            "authority": "IDENTITY_ONLY",
            "mutation": False,
        }

    # H02 -----------------------------------------------------------------
    def projection_decide(self, oid: str, chart: str, *, epoch: str = ACTIVE_EPOCH) -> dict[str, Any]:
        if not self._existing_oid(oid):
            return {
                "artifact": "ATHENA.H02.PROJECTION.DECISION.V1",
                "oid": oid,
                "chart": chart,
                "epoch": epoch,
                "authority": "NONE",
                "status": "UNMAPPED",
                "constitutional_gid": None,
                "projection_address": None,
                "defects": ["UNKNOWN_OID"],
            }
        coord = self.crystal._coordinate(oid, chart)
        raw_status = coord.get("status") if coord else None
        status = {
            "RESOLVED": "ACTIVE",
            "PARTIAL": "ACTIVE",
            "UNKNOWN": "UNMAPPED",
            "N/A": "DORMANT",
            "HOLD": "CONFLICT",
        }.get(raw_status, "UNMAPPED")
        value = coord.get("value") if coord else None
        return {
            "artifact": "ATHENA.H02.PROJECTION.DECISION.V1",
            "oid": oid,
            "chart": chart,
            "epoch": epoch,
            "authority": "PROJECTION_ONLY",
            "status": status,
            "constitutional_gid": None,
            "projection_address": value,
            "projection_gid": value.get("gid") if isinstance(value, dict) else None,
            "source_eid": coord.get("source_eid") if coord else None,
            "transform_id": coord.get("transform_id") if coord else None,
            "loss": json.loads(coord["loss_json"]) if coord and coord.get("loss_json") else None,
            "law": "HASH_PROJECTION != CONSTITUTIONAL_SEATING",
        }

    # H03 -----------------------------------------------------------------
    def route_propose(self, source_oid: str, target: str, *, query_id: str,
                      relations: Iterable[str] | None = None, max_depth: int = 12) -> dict[str, Any]:
        path = self.crystal.graph_path(source_oid, target, relations=list(relations or []), max_depth=max_depth)
        nav = self.core.navigate(source_oid)
        source_vid = (nav.get("head") or {}).get("vid") if nav.get("found") else None
        found = bool(path.get("found"))
        steps = [
            {"edge_id": e.get("edge_id"), "source": e.get("src"), "relation": e.get("relation"),
             "target": e.get("dst"), "eid": e.get("eid")}
            for e in path.get("edges", [])
        ]
        payload = {"query_id": query_id, "source_oid": source_oid, "source_vid": source_vid,
                   "target": target, "steps": steps, "relations": sorted(set(relations or []))}
        return {
            "artifact": "ATHENA.H03.ROUTE.PROPOSAL.V1",
            "route_id": "H6ROUTE." + digest(payload, 24), **payload,
            "required_bridges": [], "required_evidence": [],
            "required_authority": ["READ_ONLY_NAVIGATION"],
            "cost_vector": {"hops": path.get("length") if found else None, "semantic_loss": "UNKNOWN",
                            "stale_risk": "UNKNOWN", "integration_cost": "UNKNOWN"},
            "gain_vector": {"reachability": 1.0 if found else 0.0, "information_gain": "UNKNOWN",
                            "closure_gain": "UNKNOWN"},
            "hard_gate_status": "PASS" if found and source_vid else "HOLD",
            "pareto_status": "UNMEASURED", "route_status": "CANDIDATE" if found else "HOLD",
            "native_path": path, "authority": "PROPOSAL_ONLY",
        }

    # H04 -----------------------------------------------------------------
    def bridge_decide(self, transform_id: str, bridge_contract: dict[str, Any] | None = None) -> dict[str, Any]:
        row = self.s.one(
            "SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t "
            "LEFT JOIN transform_programs p ON p.transform_id=t.transform_id WHERE t.transform_id=?",
            (transform_id,),
        )
        if not row:
            return {"artifact": "ATHENA.H04.BRIDGE.DECISION.V1", "transform_id": transform_id,
                    "decision": "HOLD", "missing_obligations": ["transform"],
                    "defects": ["UNKNOWN_TRANSFORM"], "authority": "NONE"}
        contract = dict(bridge_contract or {})
        if not contract:
            loss_model = json.loads(row.get("loss_model_json") or "{}")
            if isinstance(loss_model, dict) and isinstance(loss_model.get("h6_bridge"), dict):
                contract = dict(loss_model["h6_bridge"])
        missing: list[str] = []
        if not contract.get("preserved_invariants"): missing.append("preserved_invariants")
        if "lost_invariants" not in contract: missing.append("lost_invariants")
        if not contract.get("validity_corridor"): missing.append("validity_corridor")
        if not contract.get("evidence_refs"): missing.append("evidence_refs")
        if not contract.get("counterexamples"): missing.append("counterexamples")
        reverse_id = contract.get("reverse_transform_id")
        if not (reverse_id or contract.get("compensation") or contract.get("irreversible_reason")):
            missing.append("reverse_or_compensation")
        defects: list[str] = []
        transform_class = str(row.get("mode") or "LOOKUP").upper()
        lost = contract.get("lost_invariants") or []
        if transform_class == "ISOMORPHISM" and lost: defects.append("ISOMORPHISM_DECLARES_LOST_INVARIANTS")
        if transform_class == "ISOMORPHISM" and not reverse_id: defects.append("ISOMORPHISM_REVERSE_REQUIRED")
        if reverse_id:
            reverse_row = self.s.one("SELECT src_chart,dst_chart FROM transforms WHERE transform_id=?", (reverse_id,))
            if not reverse_row: defects.append("REVERSE_TRANSFORM_UNKNOWN")
            elif reverse_row["src_chart"] != row["dst_chart"] or reverse_row["dst_chart"] != row["src_chart"]:
                defects.append("REVERSE_DIRECTION_MISMATCH")
        decision = "ADMITTED" if not missing and not defects else "HOLD"
        return {
            "artifact": "ATHENA.H04.BRIDGE.DECISION.V1",
            "bridge_id": "H6BRIDGE." + digest({"transform_id": transform_id, "contract": contract}, 24),
            "transform_id": transform_id, "source_chart": row["src_chart"], "target_chart": row["dst_chart"],
            "transform_class": transform_class, "transform_status": row["status"],
            "preserved_invariants": contract.get("preserved_invariants", []), "lost_invariants": lost,
            "validity_corridor": contract.get("validity_corridor"), "evidence_refs": contract.get("evidence_refs", []),
            "required_authority": contract.get("required_authority", []), "reverse_transform_id": reverse_id,
            "compensation": contract.get("compensation"), "irreversible_reason": contract.get("irreversible_reason"),
            "counterexamples": contract.get("counterexamples", []), "missing_obligations": missing,
            "defects": defects, "decision": decision, "authority": "BRIDGE_ADMISSION_ONLY",
        }

    # H05 -----------------------------------------------------------------
    def evidence_decide(self, claim: dict[str, Any], evidence_items: Iterable[dict[str, Any]]) -> dict[str, Any]:
        items = [dict(item) for item in evidence_items]
        defects: list[str] = []
        ids = [str(item.get("evidence_id") or "") for item in items]
        nonempty_ids = [value for value in ids if value]
        if len(set(nonempty_ids)) < len(nonempty_ids): defects.append("duplicate_lineage")
        lineage_keys = [(str(i.get("source_id") or ""), str(i.get("source_revision") or ""),
                         str(i.get("independence_group") or "")) for i in items]
        nonempty_lineages = [key for key in lineage_keys if any(key)]
        if len(set(nonempty_lineages)) < len(nonempty_lineages) and "duplicate_lineage" not in defects:
            defects.append("duplicate_lineage")
        groups = {str(i.get("independence_group")) for i in items if i.get("independence_group") not in (None, "")}
        independent_count = len(groups)
        minimum_independent = int((claim.get("evidence_floor") or {}).get("minimum_independent", 0))
        if any(str(i.get("freshness", "")).upper() == "STALE" for i in items): defects.append("stale_evidence")
        if independent_count < minimum_independent: defects.append("independence_floor_unmet")
        counterevidence = [i for i in items if str(i.get("support_direction", "")).upper() in {"CONTRADICT", "COUNTER"}]
        if counterevidence: defects.append("counterevidence_present")
        status = "EVIDENCE_SUFFICIENT" if not defects else "EVIDENCE_INSUFFICIENT"
        return {"artifact": "ATHENA.H05.EVIDENCE.DECISION.V1", "claim_id": claim.get("claim_id"),
                "status": status, "evidence_count": len(items), "independent_count": independent_count,
                "minimum_independent": minimum_independent, "independence_groups": sorted(groups),
                "defects": defects, "counterevidence": counterevidence, "promotion_authority": False,
                "authority": "EVIDENCE_ASSESSMENT_ONLY"}

    # H06 -----------------------------------------------------------------
    def compile_query(self, *, request: str, goal: str, identity_targets: Iterable[str], semantic_vids: Iterable[str],
                      git_head: str, topology_version: str, prompt_digest: str, evidence_floor: Any,
                      authority_envelope: dict[str, Any], completion_predicate: dict[str, Any],
                      stop_predicate: dict[str, Any], return_target: str) -> dict[str, Any]:
        targets = self._norm_ids(identity_targets)
        vids = self._norm_ids(semantic_vids)
        seed = {"request": request, "goal": goal, "identity_targets": targets, "semantic_vids": vids,
                "git_head": git_head, "topology_version": topology_version, "prompt_digest": prompt_digest,
                "evidence_floor": evidence_floor, "authority_envelope": authority_envelope,
                "completion_predicate": completion_predicate, "stop_predicate": stop_predicate,
                "return_target": return_target}
        query_id = "H6Q." + digest(seed, 24)
        bundle = {"artifact": "ATHENA.H06.QUERYBUNDLE.V1", "query_id": query_id, **seed,
                  "active_atlas_epoch": ACTIVE_EPOCH}
        identities = [self.identity_decide(oid, candidate_oids=[oid]) for oid in targets]
        projections = [self.projection_decide(oid, "KC144", epoch=ACTIVE_EPOCH) for oid in targets]
        holds: list[dict[str, Any]] = []
        current_semantic_vids: dict[str, str | None] = {}
        for decision in identities:
            if decision["decision"] != "RESOLVED_EXISTING":
                holds.append({"type": "IDENTITY_HOLD", "input_ref": decision["input_ref"],
                              "decision": decision["decision"]})
                continue
            oid = decision.get("selected_oid")
            head = self.s.head(f"object:{oid}") if oid else None
            current_vid = head.get("vid") if head else None
            current_semantic_vids[str(oid)] = current_vid
            if current_vid and current_vid not in vids:
                holds.append({"type": "SEMANTIC_VID_HOLD", "oid": oid, "current_vid": current_vid,
                              "supplied_semantic_vids": vids})
        for decision in projections:
            if decision["status"] in {"UNMAPPED", "AMBIG", "SUPERSEDED", "CONFLICT"}:
                holds.append({"type": "PROJECTION_HOLD", "oid": decision["oid"], "status": decision["status"]})
        admission = "ADMITTED" if not holds else "CONDITIONAL"
        active = {"query_id": query_id,
                  "identity_targets": [d.get("selected_oid") for d in identities if d.get("selected_oid")],
                  "projection_refs": [{"oid": d["oid"], "chart": d["chart"], "status": d["status"]} for d in projections],
                  "current_semantic_vids": current_semantic_vids,
                  "authority_envelope": authority_envelope, "completion_predicate": completion_predicate,
                  "stop_predicate": stop_predicate, "return_target": return_target, "execution_authority": False}
        root = {"query_bundle": bundle, "identity_decisions": identities, "projection_decisions": projections,
                "route_proposals": [], "bridge_decisions": [], "evidence_decisions": [],
                "admission": admission, "active_subcrystal_candidate": active, "holds": holds}
        return {"artifact": ARTIFACT, **root, "h6_root_digest": "H6ROOT." + digest(root, 32),
                "laws": ["H6_ADMISSION != EXECUTION_AUTHORITY",
                         "H05_EVIDENCE_SUFFICIENCY != PROMOTION_AUTHORITY",
                         "SEMANTIC_VID != GIT_HEAD != TOPOLOGY_VERSION != PROMPT_DIGEST"]}
