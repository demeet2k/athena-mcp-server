from __future__ import annotations

from typing import Any, Mapping

from .identity import digest

ARTIFACT = "ATHENA.IC10.COMPILER.V1"
GATE_ORDER = (
    "I01_IDENTITY_PROVENANCE",
    "I02_SYNTAX_NORMALIZATION_DEPENDENCIES",
    "I03_TYPE_UNIT_CARRIER",
    "I04_SCOPE_CORRIDOR_EVIDENCE_ALIGNMENT",
    "I05_INVARIANT_PRESERVATION",
    "I06_EVIDENCE_SUFFICIENCY_INDEPENDENCE",
    "I07_DEPENDENCY_CLOSURE_REPLAY_PREREQUISITES",
    "I08_BRIDGE_GLUING_RETURN_DEFECT",
    "I09_AUDIT_REPLAY_COMPLETENESS",
    "I10_EXISTING_PROMOTION_QUALIFICATION",
)


class IC10Compiler:
    """Pure ordered view over existing H6 + PROMOTION.2 evidence.

    This compiler never persists a PROMRUN, never calls a provider, and never
    creates canonical promotion authority. I10 can pass only by consuming an
    already-qualified exact-head PROMOTION.2 certificate from the existing
    promotion plane after I01-I09 have independently passed.
    """

    @staticmethod
    def _observed_witness(packet: Mapping[str, Any] | None, *, required: tuple[str, ...]) -> dict[str, Any]:
        p = dict(packet or {})
        defects = []
        if p.get("observed") is not True:
            defects.append("not_observed")
        if str(p.get("status") or "").upper() != "PASS":
            defects.append("status_not_pass")
        if not str(p.get("ref") or ""):
            defects.append("missing_ref")
        for field in required:
            if p.get(field) in (None, "", [], {}):
                defects.append(f"missing_{field}")
        return {
            "status": "PASS" if not defects else "HOLD",
            "defects": defects,
            "observed": p.get("observed") is True,
            "ref": p.get("ref"),
            "trust_class": p.get("trust_class", "CALLER_ATTESTED"),
            "packet": p,
        }

    @staticmethod
    def _gate(name: str, status: str, defects: list[str], evidence: Any, *, boundary: str) -> dict[str, Any]:
        return {
            "gate": name,
            "status": status,
            "defects": sorted(set(defects)),
            "evidence": evidence,
            "boundary": boundary,
        }

    def evaluate(self, candidate: Mapping[str, Any]) -> dict[str, Any]:
        c = dict(candidate)
        git_head = str(c.get("git_head") or "")
        gates: dict[str, dict[str, Any]] = {}

        # I01 — identity/provenance ---------------------------------------
        identity = dict(c.get("identity_decision") or {})
        provenance_refs = [str(x) for x in c.get("provenance_refs", []) if str(x)]
        defects = []
        if identity.get("decision") != "RESOLVED_EXISTING":
            defects.append("identity_not_resolved")
        if not identity.get("selected_oid"):
            defects.append("selected_oid_missing")
        if not provenance_refs:
            defects.append("provenance_missing")
        gates[GATE_ORDER[0]] = self._gate(
            GATE_ORDER[0], "PASS" if not defects else "HOLD", defects,
            {"identity_decision": identity, "provenance_refs": provenance_refs},
            boundary="identity/provenance standing only; does not establish claim truth",
        )

        # I02 — syntax/normalization/dependencies ------------------------
        w = self._observed_witness(c.get("syntax_witness"), required=("normalized", "dependencies_explicit"))
        defects = list(w["defects"])
        if w["packet"].get("normalized") is not True:
            defects.append("not_normalized")
        if w["packet"].get("dependencies_explicit") is not True:
            defects.append("dependencies_not_explicit")
        gates[GATE_ORDER[1]] = self._gate(
            GATE_ORDER[1], "PASS" if not defects else "HOLD", defects, w,
            boundary="observed syntax/dependency witness; caller attestation is not provider truth",
        )

        # I03 — type/unit/carrier ----------------------------------------
        w = self._observed_witness(c.get("type_carrier_witness"), required=("type", "carrier", "units_status"))
        defects = list(w["defects"])
        units = str(w["packet"].get("units_status") or "").upper()
        if units not in {"VALIDATED", "NOT_APPLICABLE"}:
            defects.append("units_not_validated")
        gates[GATE_ORDER[2]] = self._gate(
            GATE_ORDER[2], "PASS" if not defects else "HOLD", defects, w,
            boundary="type/carrier/unit admissibility only",
        )

        # I04 — scope/corridor/evidence alignment ------------------------
        w = self._observed_witness(c.get("scope_witness"), required=("scope", "validity_corridor", "evidence_alignment"))
        defects = list(w["defects"])
        alignment = str(w["packet"].get("evidence_alignment") or "").upper()
        if alignment not in {"PASS", "NOT_APPLICABLE"}:
            defects.append("evidence_alignment_not_pass")
        gates[GATE_ORDER[3]] = self._gate(
            GATE_ORDER[3], "PASS" if not defects else "HOLD", defects, w,
            boundary="scope/corridor alignment does not strengthen evidence class",
        )

        # I05 — invariant preservation -----------------------------------
        # A valid observed invariant witness may report an empty violations list.
        # Empty violations means no observed invariant breach; an absent violations
        # field is still a malformed witness and must fail closed.
        w = self._observed_witness(c.get("invariant_witness"), required=("declared_invariants",))
        defects = list(w["defects"])
        if "violations" not in w["packet"]:
            defects.append("missing_violations")
        violations = list(w["packet"].get("violations") or [])
        if violations:
            defects.append("invariant_violation")
        gates[GATE_ORDER[4]] = self._gate(
            GATE_ORDER[4], "PASS" if not defects else "HOLD", defects, w,
            boundary="declared invariant witness; does not infer undeclared invariants",
        )

        # I06 — H05 evidence sufficiency ---------------------------------
        evidence = dict(c.get("evidence_decision") or {})
        defects = []
        if evidence.get("status") != "EVIDENCE_SUFFICIENT":
            defects.append("evidence_not_sufficient")
        if evidence.get("promotion_authority") is not False:
            defects.append("evidence_authority_boundary_invalid")
        if evidence.get("defects"):
            defects.append("evidence_defects_present")
        gates[GATE_ORDER[5]] = self._gate(
            GATE_ORDER[5], "PASS" if not defects else "HOLD", defects, evidence,
            boundary="H05 sufficiency/independence only; evidence gate never promotes",
        )

        # I07 — dependency closure / replay prerequisites ----------------
        w = self._observed_witness(
            c.get("dependency_replay_witness"),
            required=("dependencies_closed", "replay_prerequisites", "exact_versions"),
        )
        defects = list(w["defects"])
        for field in ("dependencies_closed", "replay_prerequisites", "exact_versions"):
            if w["packet"].get(field) is not True:
                defects.append(f"{field}_not_satisfied")
        gates[GATE_ORDER[6]] = self._gate(
            GATE_ORDER[6], "PASS" if not defects else "HOLD", defects, w,
            boundary="dependency/replay readiness only; no execution authorization",
        )

        # I08 — H04 bridge/glue/return defect ----------------------------
        bridge = dict(c.get("bridge_decision") or {})
        defects = []
        if bridge.get("decision") != "ADMITTED":
            defects.append("bridge_not_admitted")
        if bridge.get("missing_obligations"):
            defects.append("bridge_obligations_missing")
        if bridge.get("defects"):
            defects.append("bridge_defects_present")
        reverse_defined = bool(
            bridge.get("reverse_transform_id") or bridge.get("compensation") or bridge.get("irreversible_reason")
        )
        if not reverse_defined:
            defects.append("return_or_irreversibility_undefined")
        gates[GATE_ORDER[7]] = self._gate(
            GATE_ORDER[7], "PASS" if not defects else "HOLD", defects, bridge,
            boundary="bridge/gluing/return admissibility only",
        )

        # I09 — audit/replay completeness --------------------------------
        w = self._observed_witness(c.get("audit_replay_witness"), required=("audit_complete", "replay_complete", "replay_digest"))
        defects = list(w["defects"])
        if w["packet"].get("audit_complete") is not True:
            defects.append("audit_incomplete")
        if w["packet"].get("replay_complete") is not True:
            defects.append("replay_incomplete")
        gates[GATE_ORDER[8]] = self._gate(
            GATE_ORDER[8], "PASS" if not defects else "HOLD", defects, w,
            boundary="audit/replay completeness; replay match is not external re-verification",
        )

        # I10 — existing PROMOTION.2 qualification -----------------------
        promotion = dict(c.get("promotion_certificate") or {})
        defects = []
        if promotion.get("status") != "QUALIFIED":
            defects.append("promotion_not_qualified")
        if promotion.get("promotion_allowed") is not True:
            defects.append("promotion_allowed_false")
        if not git_head or str(promotion.get("git_head") or "") != git_head:
            defects.append("promotion_git_head_mismatch")
        verification = dict((promotion.get("gates") or {}).get("external_verification") or {})
        if verification.get("status") != "PASS" or verification.get("trusted") is not True:
            defects.append("trusted_external_verification_missing")
        predecessors_pass = all(gates[name]["status"] == "PASS" for name in GATE_ORDER[:9])
        if not predecessors_pass:
            defects.append("predecessor_gate_hold")
        gates[GATE_ORDER[9]] = self._gate(
            GATE_ORDER[9], "PASS" if not defects else "HOLD", defects, promotion,
            boundary="consumes existing PROMOTION.2 authority; IC10Compiler cannot persist or mint a PROMRUN",
        )

        ordered = [gates[name] for name in GATE_ORDER]
        all_pass = all(g["status"] == "PASS" for g in ordered)
        body = {
            "artifact": ARTIFACT,
            "git_head": git_head,
            "candidate_ref": c.get("candidate_ref"),
            "gate_order": list(GATE_ORDER),
            "gates": ordered,
            "gate_map": gates,
            "decision": "IC10_CHAIN_SATISFIED" if all_pass else "IC10_HOLD",
            "first_hold": next((g["gate"] for g in ordered if g["status"] != "PASS"), None),
            "promotion_status_observed": promotion.get("status"),
            "promotion_run_id": promotion.get("run_id"),
            "promotion_authority": False,
            "canonical_emission_authority": "EXISTING_PROMOTION_LEDGER_ONLY",
            "mutation": False,
            "laws": [
                "I01_THROUGH_I09_NON_SKIPPABLE",
                "PROMOTION2_QUALIFIED != FULL_IC10_GATE_VECTOR",
                "IC10_CHAIN_SATISFIED != CLAIM_TRUTH",
                "IC10_COMPILER != SECOND_PROMOTION_LEDGER",
                "I10_CONSUMES_EXISTING_PROMOTION_AUTHORITY_ONLY",
            ],
        }
        body["decision_digest"] = "IC10." + digest(body, 32)
        return body
