from __future__ import annotations

import json
from typing import Any, Iterable

from .identity import digest


ARTIFACT = "ATHENA.H6.ROOT.RUNTIME.V1"
ACTIVE_EPOCH = "EPOCH-B-EIGHT-BLOCK"


class H6RootRuntime:
    """Read-only constitutional facade over existing ATHENA root primitives.

    H6 does not create a second object store, coordinate store, transform store,
    evidence ledger, scheduler, execution engine, or promotion authority.  It
    normalizes current primitives into the six H01-H06 constitutional decisions.
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
            valid_candidates = {oid for oid in candidates if self._existing_oid(oid)}
            if alias_targets:
                valid_candidates = valid_candidates & alias_targets if valid_candidates else alias_targets
            candidates = valid_candidates
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
            "referent_compatibility": {oid: "ALIAS_OBSERVED" if oid in alias_targets else "UNKNOWN" for oid in ordered},
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
        status_map = {
            "RESOLVED": "ACTIVE",
            "PARTIAL": "ACTIVE",
            "UNKNOWN": "UNMAPPED",
            "N/A": "DORMANT",
            "HOLD": "CONFLICT",
        }
        status = status_map.get(raw_status, "UNMAPPED")
        value = coord.get("value") if coord else None
        # Existing KC144 coordinates generated from stable_gid are deterministic
        # projections.  They are not, by themselves, constitutional semantic
        # seating authority.
        authority = "PROJECTION_ONLY"
        constitutional_gid = None
        return {
            "artifact": "ATHENA.H02.PROJECTION.DECISION.V1",
            "oid": oid,
            "chart": chart,
            "epoch": epoch,
            "authority": authority,
            "status": status,
            "constitutional_gid": constitutional_gid,
            "projection_address": value,
            "projection_gid": value.get("gid") if isinstance(value, dict) else None,
            "source_eid": coord.get("source_eid") if coord else None,
            "transform_id": coord.get("transform_id") if coord else None,
            "loss": json.loads(coord["loss_json"]) if coord and coord.get("loss_json") else None,
            "law": "HASH_PROJECTION != CONSTITUTIONAL_SEATING",
        }

    # H03 -----------------------------------------------------------------
    def route_propose(
        self,
        source_oid: str,
        target: str,
        *,
        query_id: str,
        relations: Iterable[str] | None = None,
        max_depth: int = 12,
    ) -> dict[str, Any]:
        path = self.crystal.graph_path(source_oid, target, relations=list(relations or []), max_depth=max_depth)
        nav = self.core.navigate(source_oid)
        source_vid = (nav.get("head") or {}).get("vid") if nav.get("found") else None
        found = bool(path.get("found"))
        steps = [
            {
                "edge_id": e.get("edge_id"),
                "source": e.get("src"),
                "relation": e.get("relation"),
                "target": e.get("dst"),
                "eid": e.get("eid"),
            }
            for e in path.get("edges", [])
        ]
        payload = {
            "query_id": query_id,
            "source_oid": source_oid,
            "source_vid": source_vid,
            "target": target,
            "steps": steps,
            "relations": sorted(set(relations or [])),
        }
        return {
            "artifact": "ATHENA.H03.ROUTE.PROPOSAL.V1",
            "route_id": "H6ROUTE." + digest(payload, 24),
            **payload,
            "required_bridges": [],
            "required_evidence": [],
            "required_authority": ["READ_ONLY_NAVIGATION"],
            "cost_vector": {
                "hops": path.get("length") if found else None,
                "semantic_loss": "UNKNOWN",
                "stale_risk": "UNKNOWN",
                "integration_cost": "UNKNOWN",
            },
            "gain_vector": {
                "reachability": 1.0 if found else 0.0,
                "information_gain": "UNKNOWN",
                "closure_gain": "UNKNOWN",
            },
            "hard_gate_status": "PASS" if found and source_vid else "HOLD",
            "pareto_status": "UNMEASURED",
            "route_status": "CANDIDATE" if found else "HOLD",
            "native_path": path,
            "authority": "PROPOSAL_ONLY",
        }

    # H04 -----------------------------------------------------------------
    def bridge_decide(self, transform_id: str, bridge_contract: dict[str, Any] | None = None) -> dict[str, Any]:
        row = self.s.one(
            "SELECT t.*,p.mode,p.program_json,p.metric_json FROM transforms t "
            "LEFT JOIN transform_programs p ON p.transform_id=t.transform_id "
            "WHERE t.transform_id=?",
            (transform_id,),
        )
        if not row:
            return {
                "artifact": "ATHENA.H04.BRIDGE.DECISION.V1",
                "transform_id": transform_id,
                "decision": "HOLD",
                "missing_obligations": ["transform"],
                "defects": ["UNKNOWN_TRANSFORM"],
                "authority": "NONE",
            }

        contract = dict(bridge_contract or {})
        if not contract:
            loss_model = json.loads(row.get("loss_model_json") or "{}")
            if isinstance(loss_model, dict) and isinstance(loss_model.get("h6_bridge"), dict):
                contract = dict(loss_model["h6_bridge"])

        missing = []
        if not contract.get("preserved_invariants"):
            missing.append("preserved_invariants")
        if "lost_invariants" not in contract:
            missing.append("lost_invariants")
        if not contract.get("validity_corridor"):
            missing.append("validity_corridor")
        if not contract.get("evidence_refs"):
            missing.append("evidence_refs")
        if not contract.get("counterexamples"):
            missing.append("counterexamples")
        reverse_ok = bool(
            contract.get("reverse_transform_id")
            or contract.get("compensation")
            or contract.get("irreversible_reason")
        )
        if not reverse_ok:
            missing.append("reverse_or_compensation")

        defects = []
        transform_class = str(row.get("mode") or "LOOKUP").upper()
        lost = contract.get("lost_invariants") or []
        if transform_class == "ISOMORPHISM" and lost:
            defects.append("ISOMORPHISM_DECLARES_LOST_INVARIANTS")

        decision = "ADMITTED" if not missing and not defects else "HOLD"
        return {
            "artifact": "ATHENA.H04.BRIDGE.DECISION.V1",
            "bridge_id": "H6BRIDGE." + digest({"transform_id": transform_id, "contract": contract}, 24),
            "transform_id": transform_id,
            "source_chart": row["src_chart"],
            "target_chart": row["dst_chart"],
            "transform_class": transform_class,
            "transform_status": row["status"],
            "preserved_invariants": contract.get("preserved_invariants", []),
            "lost_invariants": lost,
            "validity_corridor": contract.get("validity_corridor"),
            "evidence_refs": contract.get("evidence_refs", []),
            "required_authority": contract.get("required_authority", []),
            "reverse_transform_id": contract.get("reverse_transform_id"),
            "compensation": contract.get("compensation"),
            "irreversible_reason": contract.get("irreversible_reason"),
            "counterexamples": contract.get("counterexamples", []),
            "missing_obligations": missing,
            "defects": defects,
            "decision": decision,
            "authority": "BRIDGE_ADMISSION_ONLY",
        }

    # H05 -----------------------------------------------------------------
    def evidence_decide(self, claim: dict[str, Any], evidence_items: Iterable[dict[str, Any]]) -> dict[str, Any]:
        items = [dict(x) for x in evidence_items]
        defects: list[str] = []

        evidence_ids = [str(x.get("evidence_id") or "") for x in items]
        evidence_ids_nonempty = [x for x in evidence_ids if x]
        if len(set(evidence_ids_nonempty)) < len(evidence_ids_nonempty):
            defects.append("duplicate_lineage")

        lineage_keys = [
            (
                str(x.get("source_id") or ""),
                str(x.get("source_revision") or ""),
                str(x.get("independence_group") or ""),
            )
            for x in items
        ]
        nonempty_lineages = [k for k in lineage_keys if any(k)]
        if len(set(nonempty_lineages)) < len(nonempty_lineages) and "duplicate_lineage" not in defects:
            defects.append("duplicate_lineage")

        groups = {
            str(x.get("independence_group"))
            for x in items
            if x.get("independence_group") not in (None, "")
        }
        independent_count = len(groups)
        minimum_independent = int((claim.get("evidence_floor") or {}).get("minimum_independent", 0))

        stale = [x for x in items if str(x.get("freshness", "")).upper() == "STALE"]
        if stale:
            defects.append("stale_evidence")
        if independent_count < minimum_independent:
            defects.append("independence_floor_unmet")

        status = "EVIDENCE_SUFFICIENT" if not defects else "EVIDENCE_INSUFFICIENT"
        return {
            "artifact": "ATHENA.H05.EVIDENCE.DECISION.V1",
            "claim_id": claim.get("claim_id"),
            "status": status,
            "evidence_count": len(items),
            "independent_count": independent_count,
            "minimum_independent": minimum_independent,
            "independence_groups": sorted(groups),
            "defects": defects,
            "counterevidence": [x for x in items if str(x.get("support_direction", "")).upper() in {"CONTRADICT", "COUNTER"}],
            "promotion_authority": False,
            "authority": "EVIDENCE_ASSESSMENT_ONLY",
        }

    # H06 -----------------------------------------------------------------
    def compile_query(
        self,
        *,
        request: str,
        goal: str,
        identity_targets: Iterable[str],
        semantic_vids: Iterable[str],
        git_head: str,
        topology_version: str,
        prompt_digest: str,
        evidence_floor: Any,
        authority_envelope: dict[str, Any],
        completion_predicate: dict[str, Any],
        stop_predicate: dict[str, Any],
        return_target: str,
    ) -> dict[str, Any]:
        targets = self._norm_ids(identity_targets)
        vids = self._norm_ids(semantic_vids)
        query_seed = {
            "request": request,
            "goal": goal,
            "identity_targets": targets,
            "semantic_vids": vids,
            "git_head": git_head,
            "topology_version": topology_version,
            "prompt_digest": prompt_digest,
            "evidence_floor": evidence_floor,
            "authority_envelope": authority_envelope,
            "completion_predicate": completion_predicate,
            "stop_predicate": stop_predicate,
            "return_target": return_target,
        }
        query_id = "H6Q." + digest(query_seed, 24)
        query_bundle = {
            "artifact": "ATHENA.H06.QUERYBUNDLE.V1",
            "query_id": query_id,
            **query_seed,
            "active_atlas_epoch": ACTIVE_EPOCH,
        }

        identities = [self.identity_decide(oid, candidate_oids=[oid]) for oid in targets]
        projections = [self.projection_decide(oid, "KC144", epoch=ACTIVE_EPOCH) for oid in targets]
        holds = []
        for d in identities:
            if d["decision"] not in {"RESOLVED_EXISTING"}:
                holds.append({"type": "IDENTITY_HOLD", "input_ref": d["input_ref"], "decision": d["decision"]})
        for d in projections:
            if d["status"] in {"CONFLICT"}:
                holds.append({"type": "PROJECTION_HOLD", "oid": d["oid"], "status": d["status"]})

        admission = "ADMITTED" if not holds else "CONDITIONAL"
        active_candidate = {
            "query_id": query_id,
            "identity_targets": [d.get("selected_oid") for d in identities if d.get("selected_oid")],
            "projection_refs": [
                {"oid": d["oid"], "chart": d["chart"], "status": d["status"]}
                for d in projections
            ],
            "authority_envelope": authority_envelope,
            "completion_predicate": completion_predicate,
            "stop_predicate": stop_predicate,
            "return_target": return_target,
            "execution_authority": False,
        }
        root_state = {
            "query_bundle": query_bundle,
            "identity_decisions": identities,
            "projection_decisions": projections,
            "route_proposals": [],
            "bridge_decisions": [],
            "evidence_decisions": [],
            "admission": admission,
            "active_subcrystal_candidate": active_candidate,
            "holds": holds,
        }
        return {
            "artifact": ARTIFACT,
            **root_state,
            "h6_root_digest": "H6ROOT." + digest(root_state, 32),
            "laws": [
                "H6_ADMISSION != EXECUTION_AUTHORITY",
                "H05_EVIDENCE_SUFFICIENCY != PROMOTION_AUTHORITY",
                "SEMANTIC_VID != GIT_HEAD != TOPOLOGY_VERSION != PROMPT_DIGEST",
            ],
        }
