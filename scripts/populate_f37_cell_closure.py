from __future__ import annotations

import hashlib
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
XB_SPEC = ROOT / "spec" / "X16_BR21_SOURCE_POPULATION_V1.json"
F37_SPEC = ROOT / "spec" / "F37_LIBRARY_SOURCE_POPULATION_V1.json"
OUTPUT = Path("kc144_f37_population_matrix_v1.json")
ARTIFACT = "ATHENA.KC144.F37.LIBRARY.SOURCE.POPULATION.RECEIPT.V1"


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def blob_sha(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def bind_git_sources(core: AthenaCore, gid: int, paths: list[str], checkout_head: str) -> tuple[dict, dict]:
    descriptor = seat(gid)
    pieces: list[str] = []
    refs: list[str] = []
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"required source missing for GID{gid:03d}: {rel}")
        sha = blob_sha(rel)
        refs.append(f"GIT_BLOB:{rel}:{sha}")
        pieces.append(f"\n===== {rel} @ {sha} =====\n{path.read_text(encoding='utf-8')}\n")
    registered = core.register(
        "KC144_STATION",
        descriptor["block"],
        "POPULATE",
        descriptor["code"],
        "SOURCE_BOUND_GIT_BUNDLE",
        {"sources": "git_blob_refs"},
        {"station": descriptor["role"]},
        constraints={"gid": gid, "epoch": "EPOCH-B-EIGHT-BLOCK"},
        payload={"gid": gid, "role": descriptor["role"], "sources": paths},
        actor="KC144.SOURCE.POPULATION",
        status="CANDIDATE",
    )
    oid = registered["object"]["oid"]
    ingested = core.ingest_text(
        oid,
        registered["version"]["vid"],
        "".join(pieces),
        f"git-bundle://KC144/GID{gid:03d}@{checkout_head}",
        "text/x-athena-source-bundle",
        actor="KC144.SOURCE.POPULATION",
    )
    binding = {"oid": oid, "authority": "CONSTITUTIONAL_SEAT", "evidence_refs": refs}
    receipt = {
        "gid": gid,
        "code": descriptor["code"],
        "oid": oid,
        "vid": ingested["version"]["vid"],
        "mid": ingested["mid"],
        "source_class": "GIT_BUNDLE",
        "sources": paths,
        "evidence_refs": refs,
    }
    return binding, receipt


def carrier_source_status(carrier: str, f37: dict) -> str:
    for status, carriers in f37["source_status_partition"].items():
        if carrier in carriers:
            return status
    raise RuntimeError(f"carrier missing source-status partition: {carrier}")


def bind_library_source_manifest(core: AthenaCore, gid: int, f37: dict) -> tuple[dict, dict]:
    descriptor = seat(gid)
    carrier = descriptor["code"]
    roots = f37["source_roots"]
    status = carrier_source_status(carrier, f37)
    source_record = {
        "artifact": "ATHENA.KC144.F37.CARRIER.SOURCE.OCCURRENCE.V1",
        "gid": gid,
        "carrier": carrier,
        "role": descriptor["role"],
        "source_status": status,
        "source_roots": roots,
        "source_root_digest": canonical_digest(roots),
        "carrier_anchor": carrier,
        "observation_boundary": f37["source_observation_boundary"],
        "known_obligations": descriptor.get("known_obligations") or [],
    }
    refs = [
        f"LIBRARY_SHA256:{root['sha256']}:{root['version_id']}#{carrier}"
        for root in roots.values()
    ]
    registered = core.register(
        "KC144_STATION",
        descriptor["block"],
        "POPULATE",
        descriptor["code"],
        "CONTENT_ADDRESSED_LIBRARY_SOURCE_MANIFEST",
        {"sources": "library_file_id+version+sha256"},
        {"station": descriptor["role"], "source_status": status},
        constraints={"gid": gid, "epoch": "EPOCH-B-EIGHT-BLOCK"},
        payload=source_record,
        actor="KC144.F37.LIBRARY.SOURCE.POPULATION",
        status="CANDIDATE",
    )
    oid = registered["object"]["oid"]
    body = json.dumps(source_record, indent=2, sort_keys=True, ensure_ascii=False)
    ingested = core.ingest_text(
        oid,
        registered["version"]["vid"],
        body,
        f"library-source-manifest://KC144/{carrier}@{source_record['source_root_digest']}",
        "application/vnd.athena.library-source-manifest+json",
        actor="KC144.F37.LIBRARY.SOURCE.POPULATION",
    )
    binding = {"oid": oid, "authority": "CONSTITUTIONAL_SEAT", "evidence_refs": refs}
    receipt = {
        "gid": gid,
        "code": carrier,
        "oid": oid,
        "vid": ingested["version"]["vid"],
        "mid": ingested["mid"],
        "source_class": "CONTENT_ADDRESSED_LIBRARY_MANIFEST",
        "source_status": status,
        "source_root_digest": source_record["source_root_digest"],
        "evidence_refs": refs,
    }
    return binding, receipt


def main() -> int:
    h6 = json.loads(H6_SPEC.read_text(encoding="utf-8"))
    gov = json.loads(GOV_SPEC.read_text(encoding="utf-8"))
    xb = json.loads(XB_SPEC.read_text(encoding="utf-8"))
    f37 = json.loads(F37_SPEC.read_text(encoding="utf-8"))
    checkout_head = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()

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
            inherited = {
                **h6["seat_bindings"],
                **gov["bindings"],
                **xb["bindings"],
            }
            for gid_text, mapping in sorted(inherited.items(), key=lambda kv: int(kv[0])):
                gid = int(gid_text)
                binding, receipt = bind_git_sources(core, gid, list(mapping["sources"]), checkout_head)
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            for gid in range(44, 81):
                binding, receipt = bind_library_source_manifest(core, gid, f37)
                seat_bindings[gid] = [binding]
                source_receipts[str(gid)] = receipt

            qualification = h6["qualification_evidence"]
            runtime_evidence: dict[int, dict] = {}
            evidence_evidence: dict[int, dict] = {}
            return_evidence: dict[int, dict] = {}

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

            honesty_gids = {int(gid) for gid in f37["known_hold_by_gid"]}
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
                if gid in honesty_gids:
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

    f37_gids = list(range(44, 81))
    honesty_gids = {int(gid) for gid in f37["known_hold_by_gid"]}
    checks = {
        "source_population_closed_102": matrix["dimension_counts"]["population_status"].get("CLOSED") == 102,
        "population_unknown_42": matrix["dimension_counts"]["population_status"].get("UNKNOWN") == 42,
        "execution_partial_102": matrix["dimension_counts"]["execution_status"].get("PARTIAL") == 102,
        "execution_unknown_42": matrix["dimension_counts"]["execution_status"].get("UNKNOWN") == 42,
        "evidence_closed_h6_6": matrix["dimension_counts"]["evidence_status"].get("CLOSED") == 6,
        "evidence_partial_92": matrix["dimension_counts"]["evidence_status"].get("PARTIAL") == 92,
        "evidence_hold_f37_4": matrix["dimension_counts"]["evidence_status"].get("HOLD") == 4,
        "evidence_unknown_42": matrix["dimension_counts"]["evidence_status"].get("UNKNOWN") == 42,
        "return_closed_h6_6": matrix["dimension_counts"]["return_status"].get("CLOSED") == 6,
        "return_partial_56": matrix["dimension_counts"]["return_status"].get("PARTIAL") == 56,
        "return_unknown_82": matrix["dimension_counts"]["return_status"].get("UNKNOWN") == 82,
        "all_f37_population_closed": all(
            matrix["packets"][gid - 1]["closure"]["population_status"] == "CLOSED"
            for gid in f37_gids
        ),
        "f37_honesty_rows_remain_hold": all(
            matrix["packets"][gid - 1]["closure"]["evidence_status"] == "HOLD"
            and matrix["packets"][gid - 1]["closure"]["overall_state"] == "HOLD"
            for gid in honesty_gids
        ),
        "other_f37_rows_open_typed": all(
            matrix["packets"][gid - 1]["closure"]["overall_state"] == "OPEN_TYPED"
            for gid in f37_gids if gid not in honesty_gids
        ),
        "all_f37_return_only_partial": all(
            matrix["packets"][gid - 1]["closure"]["return_status"] == "PARTIAL"
            for gid in f37_gids
        ),
        "all_f37_bindings_content_addressed": all(
            len(matrix["packets"][gid - 1]["population"]["constitutional_bindings"]) == 1
            and len(matrix["packets"][gid - 1]["population"]["constitutional_bindings"][0]["evidence_refs"]) == 3
            for gid in f37_gids
        ),
        "whole_crystal_not_closed": matrix["overall_counts"].get("CLOSED", 0) == 0,
        "known_hold_count_4": matrix["overall_counts"].get("HOLD") == 4,
    }
    ok = all(checks.values())
    receipt = {
        "artifact": ARTIFACT,
        "status": "F37_SOURCE_POPULATION_MATCH" if ok else "F37_SOURCE_POPULATION_HOLD",
        "checkout_head": checkout_head,
        "parent_x16_br21_head": f37["parent_x16_br21_population"],
        "canonical_h6_installation": False,
        "provider_library_refetch": False,
        "checks": checks,
        "source_roots": f37["source_roots"],
        "source_status_partition": f37["source_status_partition"],
        "source_receipts": source_receipts,
        "matrix_id": matrix["matrix_id"],
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "new_population_gids": f37_gids,
        "known_hold_gids": sorted(honesty_gids),
        "evidence_ceiling": [
            "LIBRARY_SOURCE_OBSERVED != PROVIDER_LIBRARY_REVERIFIED",
            "SOURCE_STATUS_EXACT != CELL_EVIDENCE_CLOSED",
            "F37_SOURCE_POPULATION != STATION_EXECUTION_QUALIFICATION",
            "RETURN_TEST_DESCRIBED != RETURN_TEST_EXECUTED",
            "HONESTY_LEDGER_ROWS_REMAIN_HOLD",
            "SHARED_SOURCE_ROOTS != INDEPENDENT_EVIDENCE_COUNT",
            "102_SOURCE_POPULATED_SEATS != WHOLE_KC144_POPULATED",
        ],
        "matrix": matrix,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k not in {"matrix", "source_receipts"}}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
