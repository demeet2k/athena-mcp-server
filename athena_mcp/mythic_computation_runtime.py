from __future__ import annotations

import hashlib
import re
from collections import deque
from copy import deepcopy
from typing import Any, Dict, List

from .mythic_computation_protocol import MCK_VERSION, STATUS_ENUM

EPISTEMIC_LAWS = [
    "TRADITION_INTERNAL != EMPIRICAL_CAUSATION",
    "SYMBOLIC_CORRESPONDENCE != PHYSICAL_CAUSAL_EDGE",
    "SOURCE_REPORTED != OBSERVED",
    "DIVINATORY_OUTPUT != FACT",
    "R != W != D != INTERPRETATION",
    "W != D != U",
    "PUBLIC_DESCRIPTION != INITIATORY_AUTHORIZATION",
    "MODERN_RECONSTRUCTION != HISTORICAL_SOURCE_STATE",
    "MODEL_BRIDGE != CULTURAL_IDENTITY",
    "SIMULATION != EXECUTION",
]

HIGH_STAKES = {"MEDICAL", "LEGAL", "FINANCIAL", "SAFETY_CRITICAL"}
HAZARDOUS = {"TOXIC", "HARM_DIRECTED", "COERCIVE", "ILLEGAL", "DANGEROUS"}

_STANDING_RANK = {
    "UNKNOWN": 0,
    "SYMBOLIC_INFERENCE": 1,
    "TRADITION_INTERNAL": 1,
    "EXPERIMENTAL_HYPOTHESIS": 1,
    "SOURCE_REPORTED": 2,
    "OBSERVED": 3,
}


def _tokens(value: str) -> set[str]:
    return {x for x in re.findall(r"[\w]+", str(value).lower()) if x}


def _score(query: str, terms: List[str], context: str = "") -> float:
    q = _tokens(f"{query} {context}")
    t = _tokens(" ".join(str(x) for x in terms))
    if not q or not t:
        return 0.0
    overlap = len(q & t)
    union = len(q | t)
    phrase_bonus = 0.0
    qtext = str(query).lower()
    for term in terms:
        term = str(term).strip().lower()
        if term and term in qtext:
            phrase_bonus += 0.25
    return round((overlap / union) + phrase_bonus, 8)


def _weakest_status(statuses: List[str]) -> str:
    if not statuses:
        return "UNKNOWN"
    return min(statuses, key=lambda x: (_STANDING_RANK.get(x, 0), x))


class MythicComputationRuntime:
    def symbolic_address(self, query: str, address_space: List[Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        ranked = []
        for entry in address_space:
            row = deepcopy(entry)
            row.setdefault("standing", "UNKNOWN")
            row["score"] = _score(query, row.get("terms") or [], context)
            ranked.append(row)
        ranked.sort(key=lambda x: (-x["score"], str(x["id"])))
        top = ranked[0]
        positive = [x for x in ranked if x["score"] > 0]
        if not positive:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_NO_ADDRESS_MATCH",
                "query": query,
                "context": context,
                "ranked": ranked,
                "transform_loss": ["No caller-supplied address had positive lexical support; runtime refused to invent one."],
                "authority": "NONE",
                "laws": list(EPISTEMIC_LAWS),
            }
        tied = [x for x in positive if x["score"] == top["score"]]
        status = "ADDRESS_SELECTED" if len(tied) == 1 else "HOLD_AMBIGUOUS_ADDRESS"
        return {
            "version": MCK_VERSION,
            "status": status,
            "query": query,
            "context": context,
            "selected": deepcopy(top) if len(tied) == 1 else None,
            "ties": [x["id"] for x in tied],
            "ranked": ranked,
            "provenance": [x.get("source_ref") for x in tied if x.get("source_ref")],
            "transform_loss": [
                "Lexical fit is only an address-selection heuristic; semantic equivalence and tradition-internal meaning require an explicit decoder/source."
            ],
            "authority": "SYMBOLIC_ADDRESS_SELECTION_ONLY",
            "law": "ADDRESS_MATCH != EMPIRICAL_OR_CAUSAL_VALIDATION",
        }

    def correspondence_route(self, src: str, dst: str, edges: List[Dict[str, Any]], max_depth: int = 8) -> Dict[str, Any]:
        adjacency: Dict[str, List[Dict[str, Any]]] = {}
        for raw in edges:
            edge = deepcopy(raw)
            edge.setdefault("directed", True)
            adjacency.setdefault(edge["src"], []).append(edge)
            if not edge["directed"]:
                rev = deepcopy(edge)
                rev["src"], rev["dst"] = edge["dst"], edge["src"]
                adjacency.setdefault(rev["src"], []).append(rev)
        q = deque([(src, [])])
        seen = {src}
        found = None
        while q:
            node, path = q.popleft()
            if len(path) >= max_depth:
                continue
            for edge in sorted(adjacency.get(node, []), key=lambda e: (e["dst"], e["relation"], e["standing"])):
                new_path = path + [edge]
                if edge["dst"] == dst:
                    found = new_path
                    q.clear()
                    break
                if edge["dst"] not in seen:
                    seen.add(edge["dst"])
                    q.append((edge["dst"], new_path))
        if found is None:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_NO_ROUTE",
                "src": src,
                "dst": dst,
                "max_depth": max_depth,
                "authority": "NONE",
                "law": "MISSING_ROUTE != ZERO_DISTANCE",
            }
        standings = [edge["standing"] for edge in found]
        return {
            "version": MCK_VERSION,
            "status": "ROUTE_FOUND",
            "src": src,
            "dst": dst,
            "path": found,
            "depth": len(found),
            "standing_trace": standings,
            "weakest_standing": _weakest_status(standings),
            "source_refs": [edge.get("source_ref") for edge in found if edge.get("source_ref")],
            "causal_authority": False,
            "authority": "TYPED_SYMBOLIC_ROUTE_ONLY",
            "transform_loss": [
                "Path composition preserves the supplied edge labels/standing but does not prove transitivity, equivalence, or causation."
            ],
            "law": "ROUTE_EXISTS != CAUSAL_PATH; EDGE_STANDING_NEVER_UPGRADED_BY_TRAVERSAL",
        }

    def oracle_decode(
        self,
        query: str,
        codebook: List[Dict[str, Any]],
        sample: int | None = None,
        seed: str | None = None,
        use_case: str = "GENERAL",
    ) -> Dict[str, Any]:
        use_case = str(use_case or "GENERAL").upper()
        if use_case in HIGH_STAKES:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_SAFETY_CRITICAL_USE",
                "use_case": use_case,
                "query": query,
                "decision_authority": "NONE",
                "law": "DIVINATORY_OUTPUT != MEDICAL_LEGAL_FINANCIAL_OR_SAFETY_EVIDENCE",
            }
        if sample is None and seed is None:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_SAMPLE_REQUIRED",
                "query": query,
                "law": "DECODER != ENTROPY_SOURCE",
            }
        ordered = list(codebook)
        if sample is None:
            digest = hashlib.sha256(f"{seed}|{query}".encode("utf-8")).hexdigest()
            raw = int(digest, 16)
            sample_mode = "DETERMINISTIC_SEEDED_HASH"
        else:
            raw = int(sample)
            sample_mode = "CALLER_SUPPLIED_INTEGER"
        index = raw % len(ordered)
        entry = deepcopy(ordered[index])
        entry.setdefault("standing", "UNKNOWN")
        return {
            "version": MCK_VERSION,
            "status": "SYMBOLIC_GENERATION_ONLY",
            "query": query,
            "use_case": use_case,
            "R_sampler": {"mode": sample_mode, "raw": raw, "index": index, "population": len(ordered)},
            "W_witness": {"code": entry["code"], "source_ref": entry.get("source_ref")},
            "D_decoder": {
                "interpretation": entry["interpretation"],
                "standing": entry["standing"],
                "source_ref": entry.get("source_ref"),
            },
            "U_update": {"decision_authority": "NONE", "permitted_use": "REFLECTION_OR_CREATIVE_HYPOTHESIS_ONLY"},
            "authority": "SYMBOLIC_ONLY",
            "laws": [
                "R != W != D != INTERPRETATION",
                "DIVINATORY_OUTPUT != FACT",
                "SYMBOLIC_GENERATION != OBSERVED_FUTURE",
            ],
        }

    def protocol_machine(
        self,
        boundary: Dict[str, Any],
        phase: Dict[str, Any],
        steps: List[str],
        mode: str = "TRANSFORMING",
        risk_class: str = "NONE",
        witness: Any = None,
    ) -> Dict[str, Any]:
        risk_class = str(risk_class or "NONE").upper()
        mode = str(mode or "TRANSFORMING").upper()
        if risk_class in HAZARDOUS:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_NON_EXECUTABLE_HAZARD",
                "risk_class": risk_class,
                "execution_authority": "NONE",
                "law": "HISTORICAL_OR_SYMBOLIC_REPRESENTATION != HAZARDOUS_EXECUTION",
            }
        if not bool(boundary.get("authorized")):
            return {
                "version": MCK_VERSION,
                "status": "HOLD_BOUNDARY",
                "boundary": deepcopy(boundary),
                "phase": deepcopy(phase),
                "execution_authority": "NONE",
                "law": "B_REQUIRED_BEFORE_THETA_OR_PI",
            }
        if not bool(phase.get("ready")):
            return {
                "version": MCK_VERSION,
                "status": "HOLD_PHASE",
                "boundary": deepcopy(boundary),
                "phase": deepcopy(phase),
                "execution_authority": "NONE",
                "law": "THETA_REQUIRED_BEFORE_PI",
            }
        trace = ["CLOSED", "PREPARED", "BOUNDED", "ACTIVE", mode]
        trace.extend(f"STEP:{i+1}:{step}" for i, step in enumerate(steps))
        trace.append("WITNESSED" if witness is not None else "AWAITING_WITNESS")
        if witness is not None:
            trace.extend(["INTERPRETED_EXTERNALLY", "CLOSED"])
        return {
            "version": MCK_VERSION,
            "status": "SIMULATED_PROTOCOL" if witness is not None else "SIMULATED_PROTOCOL_AWAITING_WITNESS",
            "boundary": deepcopy(boundary),
            "phase": deepcopy(phase),
            "mode": mode,
            "steps": list(steps),
            "state_trace": trace,
            "witness": deepcopy(witness),
            "B_Theta_Pi_separation": True,
            "execution_authority": "NONE",
            "authority": "WORKFLOW_STATE_MACHINE_ONLY",
            "laws": ["B != THETA != PI", "SIMULATION != EXECUTION", "WITNESS != INTERPRETATION"],
        }

    def model_bridge(
        self,
        source_model: Dict[str, Any],
        target_model: Dict[str, Any],
        field_map: Dict[str, str],
        invariants: List[str] | None = None,
        source_ref: str | None = None,
        target_ref: str | None = None,
    ) -> Dict[str, Any]:
        mapped = deepcopy(target_model)
        applied = []
        missing_source = []
        overwritten = []
        for src_key, dst_key in sorted(field_map.items()):
            if src_key not in source_model:
                missing_source.append(src_key)
                continue
            if dst_key in mapped:
                overwritten.append(dst_key)
            mapped[dst_key] = deepcopy(source_model[src_key])
            applied.append({"source": src_key, "target": dst_key})
        residue = {k: deepcopy(v) for k, v in source_model.items() if k not in field_map}
        loss = []
        if residue:
            loss.append(f"{len(residue)} source fields remain unmapped.")
        if missing_source:
            loss.append(f"{len(missing_source)} requested source fields were absent.")
        if overwritten:
            loss.append(f"{len(overwritten)} target fields were explicitly overwritten by the supplied field map.")
        if not loss:
            loss.append("Field transport completed, but semantic/cultural equivalence is still not implied.")
        return {
            "version": MCK_VERSION,
            "status": "BRIDGE_COMPILED",
            "source_ref": source_ref,
            "target_ref": target_ref,
            "field_map": deepcopy(field_map),
            "applied": applied,
            "target_output": mapped,
            "unmapped_residue": residue,
            "missing_source_fields": missing_source,
            "overwritten_target_fields": overwritten,
            "invariants": list(invariants or []),
            "transform_loss": loss,
            "identity_equivalence": False,
            "authority": "EXPLICIT_LOSSY_MODEL_TRANSPORT_ONLY",
            "law": "MODEL_BRIDGE != CULTURAL_IDENTITY; UNMAPPED != ZERO",
        }

    def epistemic_split(
        self,
        items: List[Dict[str, Any]],
        requested_promotion: str | None = None,
        use_case: str = "GENERAL",
    ) -> Dict[str, Any]:
        use_case = str(use_case or "GENERAL").upper()
        buckets = {status: [] for status in STATUS_ENUM}
        for item in items:
            buckets[item["status"]].append(deepcopy(item))
        symbolic_present = bool(
            buckets["TRADITION_INTERNAL"]
            or buckets["SYMBOLIC_INFERENCE"]
            or buckets["EXPERIMENTAL_HYPOTHESIS"]
            or buckets["UNKNOWN"]
        )
        if use_case in HIGH_STAKES and symbolic_present:
            return {
                "version": MCK_VERSION,
                "status": "HOLD_SAFETY_CRITICAL_USE",
                "use_case": use_case,
                "buckets": buckets,
                "promotion": None,
                "decision_authority": "NONE",
                "law": "SYMBOLIC_OR_TRADITION_INTERNAL_STATE != SAFETY_CRITICAL_EVIDENCE",
            }

        promotion = None
        if requested_promotion:
            requested_promotion = str(requested_promotion).upper()
            decisions = []
            for item in items:
                ok = False
                reason = ""
                if requested_promotion == "OBSERVED":
                    ok = item["status"] == "OBSERVED" and bool(str(item.get("witness_ref") or "").strip())
                    reason = "OBSERVED requires existing OBSERVED standing plus a witness_ref."
                elif requested_promotion == "EMPIRICAL_SUPPORT":
                    ok = (
                        item["status"] == "OBSERVED"
                        and bool(str(item.get("witness_ref") or "").strip())
                        and bool(item.get("independent"))
                    )
                    reason = "EMPIRICAL_SUPPORT requires OBSERVED + witness_ref + independent=true."
                elif requested_promotion == "HISTORICAL_PRIMARY":
                    ok = (
                        item.get("provenance_type") == "PRIMARY_HISTORICAL_SOURCE"
                        and bool(str(item.get("source_ref") or "").strip())
                    )
                    reason = "HISTORICAL_PRIMARY requires PRIMARY_HISTORICAL_SOURCE + source_ref."
                else:
                    reason = "Unknown promotion target."
                decisions.append({"claim": item["claim"], "allowed": ok, "reason": reason})
            allowed = bool(decisions) and all(x["allowed"] for x in decisions)
            promotion = {
                "requested": requested_promotion,
                "status": "ALLOWED_WITHIN_DECLARED_SCOPE" if allowed else "REJECTED_UNSUPPORTED_PROMOTION",
                "decisions": decisions,
            }

        return {
            "version": MCK_VERSION,
            "status": "SPLIT",
            "use_case": use_case,
            "counts": {k: len(v) for k, v in buckets.items()},
            "buckets": buckets,
            "promotion": promotion,
            "decision_authority": "NONE",
            "laws": list(EPISTEMIC_LAWS),
        }

    def benchmark(self) -> Dict[str, Any]:
        cases = [
            {"claim": "internal ontology statement", "status": "TRADITION_INTERNAL"},
            {"claim": "symbolic mapping", "status": "SYMBOLIC_INFERENCE"},
            {"claim": "secondary report", "status": "SOURCE_REPORTED", "source_ref": "source://secondary"},
            {"claim": "untested hypothesis", "status": "EXPERIMENTAL_HYPOTHESIS"},
            {"claim": "unknown", "status": "UNKNOWN"},
            {"claim": "observed with witness", "status": "OBSERVED", "witness_ref": "test://w1"},
        ]
        illegal_reference = sum(1 for x in cases if x["status"] != "OBSERVED")
        protected = self.epistemic_split(cases, requested_promotion="OBSERVED")
        protected_illegal = sum(1 for x in protected["promotion"]["decisions"] if x["allowed"] and x["claim"] != "observed with witness")

        gate_cases = [
            (False, False, "HOLD_BOUNDARY"),
            (False, True, "HOLD_BOUNDARY"),
            (True, False, "HOLD_PHASE"),
            (True, True, "SIMULATED_PROTOCOL_AWAITING_WITNESS"),
        ]
        gate_pass = 0
        for authorized, ready, expected in gate_cases:
            got = self.protocol_machine({"authorized": authorized}, {"ready": ready}, ["noop"])
            gate_pass += int(got["status"] == expected)

        high_stakes = self.oracle_decode(
            "diagnose me",
            [{"code": "A", "interpretation": "symbolic reflection", "standing": "SYMBOLIC_INFERENCE"}],
            sample=0,
            use_case="MEDICAL",
        )
        return {
            "mck_version": MCK_VERSION,
            "benchmark_kind": "DETERMINISTIC_SYNTHETIC_REGRESSION_NOT_REAL_WORLD_EFFECTIVENESS",
            "evidence_collapse_cases": len(cases),
            "unsafe_reference_illegal_promotions": illegal_reference,
            "protected_illegal_promotions": protected_illegal,
            "protocol_gate_cases": len(gate_cases),
            "protocol_gate_expectations_passed": gate_pass,
            "high_stakes_oracle_hold": high_stakes["status"] == "HOLD_SAFETY_CRITICAL_USE",
            "laws": [
                "SYNTHETIC_REGRESSION_PASS != GENERAL_EFFECTIVENESS",
                "SELF_GENERATED_BENCHMARK != INDEPENDENT_EVIDENCE",
                "PREDICTION != OBSERVATION",
            ],
        }
