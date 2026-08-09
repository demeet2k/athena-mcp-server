from __future__ import annotations

import json
from typing import Any, Iterable, Mapping

from .identity import digest
from .inner_constitution import ACTIVE_EPOCH, block_counts, seat, seats

ARTIFACT = "ATHENA.CELL.CLOSURE.COMPILER.V1"
PACKET_ARTIFACT = "ATHENA.CELL.CLOSURE.PACKET.V1"
MATRIX_ARTIFACT = "ATHENA.KC144.GAP.MATRIX.V1"

TERMINAL = {"CLOSED", "DORMANT_TYPED", "HOLD", "NOT_APPLICABLE", "SUPERSEDED"}


class CellClosureCompiler:
    """Read-only evidence-conservative closure census over the frozen KC144 body.

    Existing KC144 hash/index coordinate rows are projection evidence only. They
    never count as constitutional seat population unless the caller supplies an
    explicit, evidence-bound CONSTITUTIONAL_SEAT binding.
    """

    def __init__(self, core, crystal, h6=None):
        self.core = core
        self.crystal = crystal
        self.h6 = h6
        self.s = core.s

    @staticmethod
    def _bindings(mapping: Mapping[int | str, Iterable[Mapping[str, Any]]] | None, gid: int) -> list[dict]:
        if not mapping:
            return []
        raw = mapping.get(gid, mapping.get(str(gid), []))
        return [dict(x) for x in (raw or [])]

    @staticmethod
    def _record(mapping: Mapping[int | str, Mapping[str, Any]] | None, gid: int) -> dict:
        if not mapping:
            return {}
        raw = mapping.get(gid, mapping.get(str(gid), {}))
        return dict(raw or {})

    def _validate_population_bindings(self, bindings: list[dict]) -> tuple[list[dict], list[dict]]:
        admitted = []
        defects = []
        for index, binding in enumerate(bindings):
            oid = str(binding.get("oid") or "")
            authority = str(binding.get("authority") or "")
            evidence_refs = [str(x) for x in binding.get("evidence_refs", []) if str(x)]
            if not oid:
                defects.append({"index": index, "defect": "BINDING_OID_MISSING"})
                continue
            if not self.s.one("SELECT oid FROM objects WHERE oid=?", (oid,)):
                defects.append({"index": index, "oid": oid, "defect": "BINDING_OID_UNKNOWN"})
                continue
            if authority != "CONSTITUTIONAL_SEAT":
                defects.append({"index": index, "oid": oid, "defect": "BINDING_AUTHORITY_NOT_CONSTITUTIONAL"})
                continue
            if not evidence_refs:
                defects.append({"index": index, "oid": oid, "defect": "BINDING_EVIDENCE_MISSING"})
                continue
            admitted.append({"oid": oid, "authority": authority, "evidence_refs": sorted(set(evidence_refs))})
        return admitted, defects

    def _projection_observations(self, gid: int) -> list[dict]:
        rows = self.s.rows("SELECT subject_id,status,value_json,source_eid,transform_id FROM coordinates WHERE chart_id='CHART.KC144'")
        found = []
        for row in rows:
            try:
                value = json.loads(row["value_json"]) if row.get("value_json") else None
            except (TypeError, json.JSONDecodeError):
                value = None
            if isinstance(value, dict) and value.get("gid") == gid:
                found.append({
                    "subject_id": row["subject_id"],
                    "status": row["status"],
                    "source_eid": row.get("source_eid"),
                    "transform_id": row.get("transform_id"),
                    "authority": "PROJECTION_ONLY",
                })
        return found

    @staticmethod
    def _evidence_level(record: dict) -> str:
        return str(record.get("evidence_level") or "E0_SPECIFIED")

    @staticmethod
    def _next_witness(population_status: str, execution_status: str, evidence_status: str,
                      return_status: str, binding_defects: list[dict], obligations: list[str]) -> str:
        if binding_defects:
            return "REPAIR_CONSTITUTIONAL_SEAT_BINDING"
        if population_status != "CLOSED":
            return "BIND_SOURCE_BACKED_CONSTITUTIONAL_POPULATION"
        if execution_status not in TERMINAL:
            return "BIND_EXECUTABLE_RUNTIME_OR_DORMANT_STATUS"
        if obligations and evidence_status != "CLOSED":
            return "DISCHARGE_KNOWN_CONSTITUTIONAL_OBLIGATION"
        if evidence_status not in TERMINAL:
            return "BIND_EVIDENCE_AND_CLAIM_CEILING"
        if return_status not in TERMINAL:
            return "RUN_REPLAY_RETURN_WITNESS"
        return "NONE"

    def packet(
        self,
        gid: int,
        *,
        seat_bindings: Mapping[int | str, Iterable[Mapping[str, Any]]] | None = None,
        runtime_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
        evidence_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
        return_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
    ) -> dict:
        descriptor = seat(gid)
        raw_bindings = self._bindings(seat_bindings, gid)
        bindings, binding_defects = self._validate_population_bindings(raw_bindings)
        runtime = self._record(runtime_evidence, gid)
        evidence = self._record(evidence_evidence, gid)
        returned = self._record(return_evidence, gid)
        projections = self._projection_observations(gid)
        obligations = list(descriptor.get("known_obligations") or [])

        population_status = "CLOSED" if bindings else ("HOLD" if binding_defects else "UNKNOWN")
        execution_status = str(runtime.get("status") or "UNKNOWN")
        evidence_status = str(evidence.get("status") or ("HOLD" if obligations else "UNKNOWN"))
        return_status = str(returned.get("status") or "UNKNOWN")

        closure = {
            "constitution_status": "CLOSED",
            "registry_status": "CLOSED",
            "population_status": population_status,
            "execution_status": execution_status,
            "evidence_status": evidence_status,
            "return_status": return_status,
        }
        open_dimensions = [name for name, value in closure.items() if value not in TERMINAL]
        explicit_holds = [name for name, value in closure.items() if value == "HOLD"]
        overall = "CLOSED" if all(value == "CLOSED" for value in closure.values()) else (
            "HOLD" if explicit_holds else "OPEN_TYPED"
        )
        next_witness = self._next_witness(
            population_status, execution_status, evidence_status, return_status, binding_defects, obligations
        )

        body = {
            "artifact": PACKET_ARTIFACT,
            "identity": {
                "gid": gid,
                "block": descriptor["block"],
                "code": descriptor["code"],
                "canonical_role": descriptor["role"],
                "coordinate": descriptor.get("coordinate"),
                "epoch": ACTIVE_EPOCH,
            },
            "population": {
                "constitutional_bindings": bindings,
                "binding_defects": binding_defects,
                "projection_observations": projections,
                "projection_observations_are_population": False,
            },
            "runtime": runtime,
            "verification": {
                "evidence": evidence,
                "evidence_level": self._evidence_level(evidence),
                "known_constitutional_obligations": obligations,
            },
            "return": returned,
            "closure": {
                **closure,
                "overall_state": overall,
                "open_dimensions": open_dimensions,
                "explicit_holds": explicit_holds,
                "next_required_witness": next_witness,
            },
            "laws": [
                "PROJECTION_ONLY != CONSTITUTIONAL_POPULATION",
                "CONSTITUTION_CLOSED != POPULATION_CLOSED",
                "MECHANISM_EVIDENCE != BEHAVIORAL_OR_EMPIRICAL_CERTIFICATION",
                "UNKNOWN != ZERO",
            ],
        }
        body["packet_id"] = "CELLCLOSE." + digest(body, 32)
        return body

    def matrix(
        self,
        *,
        seat_bindings: Mapping[int | str, Iterable[Mapping[str, Any]]] | None = None,
        runtime_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
        evidence_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
        return_evidence: Mapping[int | str, Mapping[str, Any]] | None = None,
    ) -> dict:
        packets = [
            self.packet(
                gid,
                seat_bindings=seat_bindings,
                runtime_evidence=runtime_evidence,
                evidence_evidence=evidence_evidence,
                return_evidence=return_evidence,
            )
            for gid in range(1, 145)
        ]
        dims = [
            "constitution_status", "registry_status", "population_status",
            "execution_status", "evidence_status", "return_status",
        ]
        counts = {dimension: {} for dimension in dims}
        overall: dict[str, int] = {}
        next_witnesses: dict[str, int] = {}
        for packet in packets:
            closure = packet["closure"]
            for dimension in dims:
                value = closure[dimension]
                counts[dimension][value] = counts[dimension].get(value, 0) + 1
            state = closure["overall_state"]
            overall[state] = overall.get(state, 0) + 1
            witness = closure["next_required_witness"]
            next_witnesses[witness] = next_witnesses.get(witness, 0) + 1

        matrix = {
            "artifact": MATRIX_ARTIFACT,
            "compiler": ARTIFACT,
            "active_epoch": ACTIVE_EPOCH,
            "seat_count": len(packets),
            "block_counts": block_counts(),
            "dimension_counts": counts,
            "overall_counts": overall,
            "next_witness_counts": next_witnesses,
            "packets": packets,
            "laws": [
                "EXACTLY_144_SEATS",
                "ZERO_UNTYPED_EMPTY_SEATS",
                "PROJECTION_ONLY_NEVER_COUNTS_AS_POPULATION",
                "EVERY_OPEN_SEAT_HAS_NEXT_REQUIRED_WITNESS",
            ],
        }
        matrix["matrix_id"] = "KC144GAP." + digest(matrix, 32)
        return matrix


def frozen_constitution_manifest() -> dict:
    body = {
        "artifact": "ATHENA.KC144.INNER.CONSTITUTION.V1",
        "active_epoch": ACTIVE_EPOCH,
        "seat_count": 144,
        "block_counts": block_counts(),
        "seats": seats(),
    }
    body["constitution_id"] = "INNERCONST." + digest(body, 32)
    return body
