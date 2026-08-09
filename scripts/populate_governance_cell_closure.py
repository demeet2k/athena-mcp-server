from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from athena_mcp.bootstrap import bootstrap
from athena_mcp.cell_closure import CellClosureCompiler
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.inner_constitution import seat
from athena_mcp.store import Store

ROOT = Path(__file__).resolve().parents[1]
H6_SPEC = ROOT / "spec" / "H6_SOURCE_POPULATION_V1.json"
GOV_SPEC = ROOT / "spec" / "GOVERNANCE_RETURN_SOURCE_POPULATION_V1.json"
OUTPUT = Path("kc144_governance_population_matrix_v1.json")
ARTIFACT = "ATHENA.KC144.GOVERNANCE.SOURCE.POPULATION.RECEIPT.V1"


def blob_sha(path: str) -> str:
    return subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True).strip()


def bind_sources(core: AthenaCore, gid: int, paths: list[str], checkout_head: str) -> tuple[dict, dict]:
    descriptor = seat(gid)
    pieces = []
    refs = []
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"required source missing for GID{gid:03d}: {rel}")
        sha = blob_sha(rel)
        refs.append(f"GIT_BLOB:{rel}:{sha}")
        pieces.append(f"\n===== {rel} @ {sha} =====\n{path.read_text(encoding='utf-8')}\n")
    registered = core.register(
        "KC144_STATION", descriptor["block"], "POPULATE", descriptor["code"], "SOURCE_BOUND_GIT_BUNDLE",
        {"sources": "git_blob_refs"}, {"station": descriptor["role"]},
        constraints={"gid": gid, "epoch": "EPOCH-B-EIGHT-BLOCK"},
        payload={"gid": gid, "role": descriptor["role"], "sources": paths},
        actor="KC144.SOURCE.POPULATION", status="CANDIDATE")
    oid = registered["object"]["oid"]
    ingested = core.ingest_text(
        oid, registered["version"]["vid"], "".join(pieces),
        f"git-bundle://KC144/GID{gid:03d}@{checkout_head}", "text/x-athena-source-bundle",
        actor="KC144.SOURCE.POPULATION")
    binding = {"oid": oid, "authority": "CONSTITUTIONAL_SEAT", "evidence_refs": refs}
    receipt = {"gid": gid, "code": descriptor["code"], "oid": oid, "vid": ingested["version"]["vid"],
               "mid": ingested["mid"], "sources": paths, "evidence_refs": refs}
    return binding, receipt


def main() -> int:
    h6 = json.loads(H6_SPEC.read_text(encoding="utf-8"))
    gov = json.loads(GOV_SPEC.read_text(encoding="utf-8"))
    checkout_head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store = Store(tmp.name)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            h6_runtime = H6RootRuntime(core, crystal)
            compiler = CellClosureCompiler(core, crystal, h6_runtime)

            seat_bindings = {}
            source_receipts = {}
            combined = {**h6["seat_bindings"], **gov["bindings"]}
            for gid_text, mapping in sorted(combined.items(), key=lambda kv: int(kv[0])):
                gid = int(gid_text)
                binding, receipt = bind_sources(core, gid, list(mapping["sources"]), checkout_head)
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            qualification = h6["qualification_evidence"]
            runtime_evidence = {}
            evidence_evidence = {}
            return_evidence = {}

            # H6: source/evidence/return closed; execution remains candidate-only.
            for gid in range(1, 7):
                runtime_evidence[gid] = {
                    "status": "PARTIAL", "standing": "QUALIFIED_CANDIDATE_NOT_CANONICAL",
                    "candidate_head": h6["h6_candidate_head"], "canonical_installation": False,
                    "evidence_level": "E5_PROVIDER_OBSERVED",
                    "master_target_run": qualification["master_target_run"],
                }
                evidence_evidence[gid] = {
                    "status": "CLOSED", "evidence_level": "E5_PROVIDER_OBSERVED",
                    "master_target_run": qualification["master_target_run"],
                    "full_circuit_cold_run": qualification["full_circuit_cold_run"],
                }
                return_evidence[gid] = {
                    "status": "CLOSED", "evidence_level": "E5_PROVIDER_OBSERVED",
                    "full_circuit_cold_run": qualification["full_circuit_cold_run"],
                    "artifact_id": qualification["full_circuit_cold_artifact"],
                }

            # IC10 and SSN12: explicit source bodies exist, but station-specific
            # executable closure/certification has not yet been demonstrated.
            for gid in range(81, 91):
                runtime_evidence[gid] = {
                    "status": "PARTIAL", "standing": "SOURCE_SUBSTRATE_PRESENT_NOT_GATE_QUALIFIED",
                    "evidence_level": "E1_STATICALLY_VALIDATED", "canonical_installation": True,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL", "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }

            for gid in range(133, 145):
                runtime_evidence[gid] = {
                    "status": "PARTIAL", "standing": "SOURCE_SUBSTRATE_PRESENT_NOT_STATION_QUALIFIED",
                    "evidence_level": "E1_STATICALLY_VALIDATED", "canonical_installation": True,
                }
                evidence_evidence[gid] = {
                    "status": "PARTIAL", "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "SOURCE_BOUND_NOT_STATION_CERTIFIED",
                }
                return_evidence[gid] = {
                    "status": "PARTIAL", "evidence_level": "E1_STATICALLY_VALIDATED",
                    "standing": "RETURN_SUBSTRATE_PRESENT_NOT_STATION_CERTIFIED",
                }

            matrix = compiler.matrix(
                seat_bindings=seat_bindings,
                runtime_evidence=runtime_evidence,
                evidence_evidence=evidence_evidence,
                return_evidence=return_evidence)
        finally:
            store.close()

    checks = {
        "source_population_closed_28": matrix["dimension_counts"]["population_status"].get("CLOSED") == 28,
        "population_unknown_116": matrix["dimension_counts"]["population_status"].get("UNKNOWN") == 116,
        "execution_partial_28": matrix["dimension_counts"]["execution_status"].get("PARTIAL") == 28,
        "execution_unknown_116": matrix["dimension_counts"]["execution_status"].get("UNKNOWN") == 116,
        "evidence_closed_h6_6": matrix["dimension_counts"]["evidence_status"].get("CLOSED") == 6,
        "evidence_partial_governance_22": matrix["dimension_counts"]["evidence_status"].get("PARTIAL") == 22,
        "evidence_hold_f37_4": matrix["dimension_counts"]["evidence_status"].get("HOLD") == 4,
        "evidence_unknown_112": matrix["dimension_counts"]["evidence_status"].get("UNKNOWN") == 112,
        "return_closed_h6_6": matrix["dimension_counts"]["return_status"].get("CLOSED") == 6,
        "return_partial_ssn12_12": matrix["dimension_counts"]["return_status"].get("PARTIAL") == 12,
        "return_unknown_126": matrix["dimension_counts"]["return_status"].get("UNKNOWN") == 126,
        "all_28_bindings_explicit": all(
            len(matrix["packets"][gid - 1]["population"]["constitutional_bindings"]) == 1
            for gid in list(range(1, 7)) + list(range(81, 91)) + list(range(133, 145))),
        "no_governance_false_closure": all(
            matrix["packets"][gid - 1]["closure"]["overall_state"] == "OPEN_TYPED"
            for gid in list(range(81, 91)) + list(range(133, 145))),
        "f37_holds_preserved": matrix["overall_counts"].get("HOLD") == 4,
    }
    ok = all(checks.values())
    receipt = {
        "artifact": ARTIFACT,
        "status": "GOVERNANCE_SOURCE_POPULATION_MATCH" if ok else "GOVERNANCE_SOURCE_POPULATION_HOLD",
        "checkout_head": checkout_head,
        "canonical_h6_installation": False,
        "checks": checks,
        "source_receipts": source_receipts,
        "matrix_id": matrix["matrix_id"],
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "evidence_ceiling": [
            "SOURCE_POPULATION_ONLY_FOR_IC10_SSN12",
            "SOURCE_SUBSTRATE != STATION_EXECUTION_QUALIFICATION",
            "SSN12_SOURCE_SUBSTRATE != RETURN_CERTIFICATION",
            "IC10_SOURCE_SUBSTRATE != I01_I10_GATE_COMPILER_CLOSED",
            "28_SOURCE_POPULATED_SEATS != WHOLE_KC144_POPULATED",
        ],
        "matrix": matrix,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k not in {"matrix", "source_receipts"}}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
