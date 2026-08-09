from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from populate_f37_cell_closure import (  # noqa: E402
    bind_git_sources,
    bind_library_source_manifest,
    carrier_source_status,
)
from athena_mcp.bootstrap import bootstrap  # noqa: E402
from athena_mcp.cell_closure import CellClosureCompiler  # noqa: E402
from athena_mcp.core import AthenaCore  # noqa: E402
from athena_mcp.crystal_runtime import CrystalRuntime  # noqa: E402
from athena_mcp.h6_root import H6RootRuntime  # noqa: E402
from athena_mcp.inner_constitution import seat  # noqa: E402
from athena_mcp.store import Store  # noqa: E402

H6_SPEC = ROOT / "spec" / "H6_SOURCE_POPULATION_V1.json"
GOV_SPEC = ROOT / "spec" / "GOVERNANCE_RETURN_SOURCE_POPULATION_V1.json"
XB_SPEC = ROOT / "spec" / "X16_BR21_SOURCE_POPULATION_V1.json"
F37_SPEC = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
FINAL_SPEC = ROOT / "spec" / "KC15_KC27_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("kc144_final_source_population_matrix_v1.json")
ARTIFACT = "ATHENA.KC144.FINAL.SOURCE.POPULATION.RECEIPT.V1"


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def blob_sha(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def bind_external_manifest(
    core: AthenaCore,
    *,
    gid: int,
    method: str,
    source_record: dict,
    evidence_refs: list[str],
    output_contract: dict,
) -> tuple[dict, dict]:
    descriptor = seat(gid)
    registered = core.register(
        "KC144_STATION",
        descriptor["block"],
        "POPULATE",
        descriptor["code"],
        method,
        {"sources": "content_addressed_external_refs"},
        {"station": descriptor["role"], **output_contract},
        constraints={"gid": gid, "epoch": "EPOCH-B-EIGHT-BLOCK"},
        payload=source_record,
        actor="KC144.FINAL.SOURCE.POPULATION",
        status="CANDIDATE",
    )
    oid = registered["object"]["oid"]
    body = json.dumps(source_record, indent=2, sort_keys=True, ensure_ascii=False)
    record_digest = canonical_digest(source_record)
    ingested = core.ingest_text(
        oid,
        registered["version"]["vid"],
        body,
        f"external-source-manifest://KC144/GID{gid:03d}@{record_digest}",
        "application/vnd.athena.external-source-manifest+json",
        actor="KC144.FINAL.SOURCE.POPULATION",
    )
    binding = {
        "oid": oid,
        "authority": "CONSTITUTIONAL_SEAT",
        "evidence_refs": evidence_refs,
    }
    receipt = {
        "gid": gid,
        "code": descriptor["code"],
        "role": descriptor["role"],
        "oid": oid,
        "vid": ingested["version"]["vid"],
        "mid": ingested["mid"],
        "source_class": method,
        "source_record_digest": record_digest,
        "evidence_refs": evidence_refs,
    }
    return binding, receipt


def kc27_generic_meaning(coord: str, axes: dict) -> dict:
    if len(coord) != 3 or any(ch not in "012" for ch in coord):
        raise RuntimeError(f"invalid KC27 coordinate: {coord}")
    return {
        "origin_provenance": axes["A_origin_provenance"][coord[0]],
        "epistemic_operation": axes["B_epistemic_operation"][coord[1]],
        "route_manifestation": axes["C_route_manifestation"][coord[2]],
    }


def main() -> int:
    h6 = json.loads(H6_SPEC.read_text(encoding="utf-8"))
    gov = json.loads(GOV_SPEC.read_text(encoding="utf-8"))
    xb = json.loads(XB_SPEC.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SPEC.read_text(encoding="utf-8"))
    final = json.loads(FINAL_SPEC.read_text(encoding="utf-8"))
    checkout_head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    constitution_blob = blob_sha("athena_mcp/inner_constitution.py")

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store = Store(tmp.name)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            h6_runtime = H6RootRuntime(core, crystal)
            compiler = CellClosureCompiler(core, crystal, h6_runtime)

            seat_bindings: dict[int, list[dict]] = {}
            source_receipts: dict[str, dict] = {}

            inherited_git = {
                **h6["seat_bindings"],
                **gov["bindings"],
                **xb["bindings"],
            }
            for gid_text, mapping in sorted(inherited_git.items(), key=lambda kv: int(kv[0])):
                gid = int(gid_text)
                binding, receipt = bind_git_sources(core, gid, list(mapping["sources"]), checkout_head)
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            for gid in range(44, 81):
                binding, receipt = bind_library_source_manifest(core, gid, f37)
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            kc15 = final["kc15"]
            active_root = kc15["active_source_root"]
            hold_root = kc15["hold_semantics_source_root"]
            for gid in range(91, 106):
                descriptor = seat(gid)
                declared = kc15["active_masks"][str(gid)]
                if descriptor["code"] != declared["mask"]:
                    raise RuntimeError(
                        f"KC15 active mask mismatch GID{gid:03d}: constitution={descriptor['code']} spec={declared['mask']}"
                    )
                support = descriptor["coordinate"]
                expected_support = "{" + ",".join(declared["support"]) + "}"
                if support != expected_support:
                    raise RuntimeError(
                        f"KC15 support mismatch GID{gid:03d}: constitution={support} spec={expected_support}"
                    )
                source_record = {
                    "artifact": "ATHENA.KC144.KC15.SOURCE.OCCURRENCE.V1",
                    "gid": gid,
                    "mask": descriptor["code"],
                    "support": descriptor["coordinate"],
                    "role": descriptor["role"],
                    "active_epoch": "EPOCH-B-EIGHT-BLOCK",
                    "active_seating_source": active_root,
                    "mask_hold_semantics_source": hold_root,
                    "historical_gid_from_hold_source_is_not_seating_authority": True,
                    "standing": kc15["standing"],
                }
                evidence_refs = [
                    f"GIT_BLOB:athena_mcp/inner_constitution.py:{constitution_blob}#GID{gid:03d}",
                    f"LIBRARY_SHA256:{active_root['sha256']}:{active_root['version_id']}#GID{gid:03d}",
                    f"LIBRARY_SHA256:{hold_root['sha256']}:{hold_root['version_id']}#KC15.{descriptor['coordinate']}",
                ]
                binding, receipt = bind_external_manifest(
                    core,
                    gid=gid,
                    method="KC15_ACTIVE_EPOCH_PLUS_MASK_HOLD_SOURCE_MANIFEST",
                    source_record=source_record,
                    evidence_refs=evidence_refs,
                    output_contract={"mask": descriptor["code"], "support": descriptor["coordinate"]},
                )
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            kc27 = final["kc27"]
            legend = kc27["generic_domain_legend_source_root"]
            anchors = {int(k): v for k, v in kc27["named_anchor_gids"].items()}
            return_gids = {int(g) for g in kc27["return_coordinate_gids"]}
            for gid in range(106, 133):
                descriptor = seat(gid)
                coord = descriptor["coordinate"]
                generic = kc27_generic_meaning(coord, kc27["axes"])
                expected_anchor = anchors.get(gid)
                if expected_anchor is not None and descriptor["role"] != expected_anchor:
                    raise RuntimeError(
                        f"KC27 named anchor mismatch GID{gid:03d}: constitution={descriptor['role']} spec={expected_anchor}"
                    )
                if expected_anchor is None and descriptor["role"] != "UNRESOLVED_DOMAIN_ROLE":
                    raise RuntimeError(
                        f"KC27 unexpected specialization GID{gid:03d}: {descriptor['role']}"
                    )
                source_record = {
                    "artifact": "ATHENA.KC144.KC27.SOURCE.OCCURRENCE.V1",
                    "gid": gid,
                    "portal": descriptor["code"],
                    "coordinate": coord,
                    "canonical_specialization": descriptor["role"],
                    "generic_ternary_meaning": generic,
                    "legend_source": legend,
                    "specialization_policy": kc27["specialization_policy"],
                    "return_coordinate": gid in return_gids,
                    "standing": kc27["standing"],
                }
                evidence_refs = [
                    f"GIT_BLOB:athena_mcp/inner_constitution.py:{constitution_blob}#GID{gid:03d}",
                    f"LIBRARY_SHA256:{legend['sha256']}:{legend['version_id']}#{descriptor['code']}/{coord}",
                ]
                binding, receipt = bind_external_manifest(
                    core,
                    gid=gid,
                    method="KC27_GENERIC_TERNARY_LEGEND_SOURCE_MANIFEST",
                    source_record=source_record,
                    evidence_refs=evidence_refs,
                    output_contract={
                        "portal": descriptor["code"],
                        "coordinate": coord,
                        "canonical_specialization": descriptor["role"],
                    },
                )
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            qualification = h6["qualification_evidence"]
            runtime_evidence: dict[int, dict] = {}
            evidence_evidence: dict[int, dict] = {}
            return_evidence: dict[int, dict] = {}

            # H6 qualified-candidate standing inherited unchanged.
            for gid in range(1, 7):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "QUALIFIED_CANDIDATE_NOT_CANONICAL",
                    "candidate_head": h6["h6_candidate_head"],
                    "canonical_installation": False,
                    "evidence_level": "E5_PROVIDER_OBSERVED",
                    "master_target_run": qualification["master_target_run"],
                }
                evidence_evidence[gid] = {
                    "status": "CLOSED",
                    "evidence_level": "E5_PROVIDER_OBSERVED",
                    "master_target_run": qualification["master_target_run"],
                    "full_circuit_cold_run": qualification["full_circuit_cold_run"],
                }
                return_evidence[gid] = {
                    "status": "CLOSED",
                    "evidence_level": "E5_PROVIDER_OBSERVED",
                    "full_circuit_cold_run": qualification["full_circuit_cold_run"],
                    "artifact_id": qualification["full_circuit_cold_artifact"],
                }

            # X16 + BR21 source-populated, not station-qualified.
            for gid in range(7, 44):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "SOURCE_SUBSTRATE_PRESENT_NOT_STATION_QUALIFIED",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "canonical_installation": False,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }
            for gid in xb["return_partial_gids"]:
                return_evidence[int(gid)] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "RETURN_SOURCE_SUBSTRATE_PRESENT_NOT_STATION_CERTIFIED",
                }

            # F37 content-addressed source population, preserving honesty-ledger holds.
            f37_hold_gids = {int(g) for g in f37["known_hold_by_gid"]}
            for gid in range(44, 81):
                carrier = seat(gid)["code"]
                source_status = carrier_source_status(carrier, f37)
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "SOURCE_MATHEMATICS_PRESENT_NOT_STATION_RUNTIME_QUALIFIED",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "canonical_installation": False,
                    "source_status": source_status,
                }
                if gid in f37_hold_gids:
                    evidence_evidence[gid] = {
                        "status": "HOLD",
                        "evidence_level": "E1_SOURCE_MANIFEST",
                        "standing": "HONESTY_LEDGER_HOLD",
                        "obligation": f37["known_hold_by_gid"][str(gid)],
                    }
                else:
                    evidence_evidence[gid] = {
                        "status": "PARTIAL",
                        "evidence_level": "E1_SOURCE_MANIFEST",
                        "standing": "INTERNAL_CORPUS_SOURCE_SEATED_NOT_INDEPENDENTLY_CERTIFIED",
                        "source_status": source_status,
                    }
                return_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "standing": "RETURN_TEST_DESCRIBED_NOT_EXECUTED",
                }

            # IC10 source population inherited; gate qualification remains separate.
            for gid in range(81, 91):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "SOURCE_SUBSTRATE_PRESENT_NOT_GATE_QUALIFIED",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "canonical_installation": True,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }

            # KC15: source-populated, but the source itself preserves evidence/admission/authority HOLD.
            for gid in range(91, 106):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "SUPPORT_MASK_SOURCE_PRESENT_NOT_STATION_RUNTIME_QUALIFIED",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "canonical_installation": False,
                }
                evidence_evidence[gid] = {
                    "status": "HOLD",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "standing": "SOURCE_BOUND_HOLD_NOT_INDEPENDENT_NOT_ADMITTED",
                    "obligations": [
                        "INDEPENDENT_WITNESS",
                        "INTERPRETATION_REVIEW",
                        "ADMISSION_AUTHORITY",
                    ],
                }
                return_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "standing": "M12_RETURN_DECLARED_NOT_EXECUTED",
                }

            # KC27: generic domain legend closes source population without inventing specialization.
            for gid in range(106, 133):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "GENERIC_DOMAIN_LEGEND_PRESENT_NOT_STATION_RUNTIME_QUALIFIED",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "canonical_installation": False,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_SOURCE_MANIFEST",
                    "standing": "GENERIC_DOMAIN_LEGEND_SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }
                if gid in return_gids:
                    return_evidence[gid] = {
                        "status": "PARTIAL",
                        "evidence_level": "E1_SOURCE_MANIFEST",
                        "standing": "GENERIC_ROUTE_MANIFESTATION_RETURN_NOT_EXECUTED",
                    }

            # SSN12 source population inherited unchanged.
            for gid in range(133, 145):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "SOURCE_SUBSTRATE_PRESENT_NOT_STATION_QUALIFIED",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "canonical_installation": True,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }
                return_evidence[gid] = {
                    "status": "PARTIAL",
                    "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "RETURN_SUBSTRATE_PRESENT_NOT_STATION_CERTIFIED",
                }

            matrix = compiler.matrix(
                seat_bindings=seat_bindings,
                runtime_evidence=runtime_evidence,
                evidence_evidence=evidence_evidence,
                return_evidence=return_evidence,
            )
        finally:
            store.close()

    expected = final["expected_final_counts"]
    kc15_gids = set(range(91, 106))
    kc27_gids = set(range(106, 133))
    checks = {
        "population_closed_144": matrix["dimension_counts"]["population_status"].get("CLOSED") == 144,
        "population_unknown_zero": matrix["dimension_counts"]["population_status"].get("UNKNOWN", 0) == 0,
        "execution_partial_144": matrix["dimension_counts"]["execution_status"].get("PARTIAL") == 144,
        "execution_unknown_zero": matrix["dimension_counts"]["execution_status"].get("UNKNOWN", 0) == 0,
        "evidence_closed_6": matrix["dimension_counts"]["evidence_status"].get("CLOSED") == 6,
        "evidence_partial_119": matrix["dimension_counts"]["evidence_status"].get("PARTIAL") == 119,
        "evidence_hold_19": matrix["dimension_counts"]["evidence_status"].get("HOLD") == 19,
        "evidence_unknown_zero": matrix["dimension_counts"]["evidence_status"].get("UNKNOWN", 0) == 0,
        "return_closed_6": matrix["dimension_counts"]["return_status"].get("CLOSED") == 6,
        "return_partial_80": matrix["dimension_counts"]["return_status"].get("PARTIAL") == 80,
        "return_unknown_58": matrix["dimension_counts"]["return_status"].get("UNKNOWN") == 58,
        "overall_hold_19": matrix["overall_counts"].get("HOLD") == 19,
        "overall_open_typed_125": matrix["overall_counts"].get("OPEN_TYPED") == 125,
        "overall_closed_zero": matrix["overall_counts"].get("CLOSED", 0) == 0,
        "all_kc15_population_closed": all(
            matrix["packets"][gid - 1]["closure"]["population_status"] == "CLOSED"
            for gid in kc15_gids
        ),
        "all_kc15_evidence_hold": all(
            matrix["packets"][gid - 1]["closure"]["evidence_status"] == "HOLD"
            and matrix["packets"][gid - 1]["closure"]["overall_state"] == "HOLD"
            for gid in kc15_gids
        ),
        "all_kc15_return_partial": all(
            matrix["packets"][gid - 1]["closure"]["return_status"] == "PARTIAL"
            for gid in kc15_gids
        ),
        "all_kc27_population_closed": all(
            matrix["packets"][gid - 1]["closure"]["population_status"] == "CLOSED"
            for gid in kc27_gids
        ),
        "all_kc27_evidence_partial": all(
            matrix["packets"][gid - 1]["closure"]["evidence_status"] == "PARTIAL"
            for gid in kc27_gids
        ),
        "kc27_return_partial_only_c2": all(
            (
                matrix["packets"][gid - 1]["closure"]["return_status"] == "PARTIAL"
                if gid in return_gids
                else matrix["packets"][gid - 1]["closure"]["return_status"] == "UNKNOWN"
            )
            for gid in kc27_gids
        ),
        "unresolved_kc27_specializations_preserved": all(
            seat(gid)["role"] == "UNRESOLVED_DOMAIN_ROLE"
            for gid in kc27_gids - set(anchors)
        ),
        "f37_honesty_holds_preserved": all(
            matrix["packets"][gid - 1]["closure"]["evidence_status"] == "HOLD"
            for gid in f37_hold_gids
        ),
        "expected_counts_spec_matches": expected == {
            "population_status": {"CLOSED": 144},
            "execution_status": {"PARTIAL": 144},
            "evidence_status": {"CLOSED": 6, "PARTIAL": 119, "HOLD": 19},
            "return_status": {"CLOSED": 6, "PARTIAL": 80, "UNKNOWN": 58},
            "overall_state": {"HOLD": 19, "OPEN_TYPED": 125, "CLOSED": 0},
        },
    }
    ok = all(checks.values())
    receipt = {
        "artifact": ARTIFACT,
        "status": "KC144_SOURCE_POPULATION_144_MATCH" if ok else "KC144_SOURCE_POPULATION_HOLD",
        "checkout_head": checkout_head,
        "parent_f37_head": final["parent_f37_population"],
        "canonical_h6_installation": False,
        "provider_library_refetch": False,
        "checks": checks,
        "source_receipts": source_receipts,
        "source_roots": {
            "kc15_active": active_root,
            "kc15_hold_semantics": hold_root,
            "kc27_generic_legend": legend,
        },
        "matrix_id": matrix["matrix_id"],
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "new_population_gids": list(range(91, 133)),
        "kc15_evidence_hold_gids": sorted(kc15_gids),
        "kc27_return_partial_gids": sorted(return_gids),
        "population_complete": True,
        "inner_crystal_complete": False,
        "evidence_ceiling": [
            "SOURCE_POPULATION_144_OF_144",
            "SOURCE_POPULATION != EXECUTION_QUALIFICATION",
            "KC15_SUPPORT != TRUTH_OR_EVIDENCE_OR_PROBABILITY",
            "KC15_SOURCE_BOUND_HOLD_REMAINS_HOLD",
            "KC27_GENERIC_DOMAIN_LEGEND != CANONICAL_SPECIALIZATION",
            "UNRESOLVED_KC27_ROLES_REMAIN_UNRESOLVED",
            "RETURN_SEMANTICS_PRESENT != RETURN_EXECUTED",
            "LIBRARY_SOURCE_OBSERVED != PROVIDER_LIBRARY_REVERIFIED",
            "144_SOURCE_POPULATED_SEATS != INNER_CRYSTAL_CERTIFIED",
        ],
        "matrix": matrix,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k not in {"matrix", "source_receipts"}}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
