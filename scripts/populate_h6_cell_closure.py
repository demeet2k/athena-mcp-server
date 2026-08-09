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
SPEC = ROOT / "spec" / "H6_SOURCE_POPULATION_V1.json"
OUTPUT = Path("kc144_h6_source_population_matrix_v1.json")
ARTIFACT = "ATHENA.KC144.H6.SOURCE.POPULATION.RECEIPT.V1"


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def source_bundle(paths: list[str]) -> tuple[str, list[str]]:
    parts = []
    refs = []
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            raise RuntimeError(f"required H6 source missing: {rel}")
        blob = git_blob(rel)
        refs.append(f"GIT_BLOB:{rel}:{blob}")
        parts.append(f"\n===== {rel} @ {blob} =====\n{path.read_text(encoding='utf-8')}\n")
    return "".join(parts), refs


def main() -> int:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    checkout_head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()

    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store = Store(tmp.name)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            h6 = H6RootRuntime(core, crystal)
            compiler = CellClosureCompiler(core, crystal, h6)

            seat_bindings = {}
            source_receipts = {}
            for gid_text, binding in sorted(spec["seat_bindings"].items(), key=lambda kv: int(kv[0])):
                gid = int(gid_text)
                descriptor = seat(gid)
                body, evidence_refs = source_bundle(binding["sources"])
                registered = core.register(
                    "KC144_STATION",
                    "H6",
                    "POPULATE",
                    descriptor["code"],
                    "SOURCE_BOUND_GIT_BUNDLE",
                    {"sources": "git_blob_refs"},
                    {"station": descriptor["role"]},
                    constraints={"gid": gid, "epoch": descriptor["epoch"] if "epoch" in descriptor else "EPOCH-B-EIGHT-BLOCK"},
                    payload={"gid": gid, "role": descriptor["role"], "sources": binding["sources"]},
                    actor="H6.SOURCE.POPULATION",
                    status="CANDIDATE",
                )
                oid = registered["object"]["oid"]
                parent_vid = registered["version"]["vid"]
                ingested = core.ingest_text(
                    oid,
                    parent_vid,
                    body,
                    f"git-bundle://H6/{descriptor['code']}@{checkout_head}",
                    "text/x-athena-source-bundle",
                    actor="H6.SOURCE.POPULATION",
                )
                seat_bindings[gid] = [{
                    "oid": oid,
                    "authority": "CONSTITUTIONAL_SEAT",
                    "evidence_refs": evidence_refs,
                }]
                source_receipts[str(gid)] = {
                    "code": descriptor["code"],
                    "oid": oid,
                    "vid": ingested["version"]["vid"],
                    "mid": ingested["mid"],
                    "sources": binding["sources"],
                    "evidence_refs": evidence_refs,
                }

            qualification = spec["qualification_evidence"]
            runtime_evidence = {}
            evidence_evidence = {}
            return_evidence = {}
            for gid in range(1, 7):
                runtime_evidence[gid] = {
                    "status": "PARTIAL",
                    "standing": "QUALIFIED_CANDIDATE_NOT_CANONICAL",
                    "candidate_head": spec["h6_candidate_head"],
                    "master_target_run": qualification["master_target_run"],
                    "promotion_artifact": qualification["master_target_promotion_artifact"],
                    "promotion_digest": qualification["master_target_promotion_digest"],
                    "evidence_level": "E5_PROVIDER_OBSERVED",
                    "canonical_installation": False,
                    "next_required_witness": "MERGE_AND_REQUALIFY_H6_CANDIDATE",
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
                    "artifact_digest": qualification["full_circuit_cold_digest"],
                }

            matrix = compiler.matrix(
                seat_bindings=seat_bindings,
                runtime_evidence=runtime_evidence,
                evidence_evidence=evidence_evidence,
                return_evidence=return_evidence,
            )
        finally:
            store.close()

    checks = {
        "six_h6_population_closed": matrix["dimension_counts"]["population_status"].get("CLOSED") == 6,
        "remaining_population_unknown": matrix["dimension_counts"]["population_status"].get("UNKNOWN") == 138,
        "six_h6_execution_partial_candidate_only": matrix["dimension_counts"]["execution_status"].get("PARTIAL") == 6,
        "remaining_execution_unknown": matrix["dimension_counts"]["execution_status"].get("UNKNOWN") == 138,
        "six_h6_evidence_closed": matrix["dimension_counts"]["evidence_status"].get("CLOSED") == 6,
        "four_f37_evidence_holds_retained": matrix["dimension_counts"]["evidence_status"].get("HOLD") == 4,
        "remaining_evidence_unknown": matrix["dimension_counts"]["evidence_status"].get("UNKNOWN") == 134,
        "six_h6_return_closed": matrix["dimension_counts"]["return_status"].get("CLOSED") == 6,
        "remaining_return_unknown": matrix["dimension_counts"]["return_status"].get("UNKNOWN") == 138,
        "no_h6_false_canonical_closure": all(matrix["packets"][gid - 1]["closure"]["overall_state"] == "OPEN_TYPED" for gid in range(1, 7)),
        "h6_runtime_standing_candidate_only": all(matrix["packets"][gid - 1]["runtime"].get("canonical_installation") is False for gid in range(1, 7)),
        "h6_source_bindings_are_explicit": all(len(matrix["packets"][gid - 1]["population"]["constitutional_bindings"]) == 1 for gid in range(1, 7)),
    }
    ok = all(checks.values())
    receipt = {
        "artifact": ARTIFACT,
        "status": "H6_SOURCE_POPULATION_MATCH" if ok else "H6_SOURCE_POPULATION_HOLD",
        "checkout_head": checkout_head,
        "h6_candidate_head": spec["h6_candidate_head"],
        "canonical_installation": False,
        "checks": checks,
        "source_receipts": source_receipts,
        "matrix_id": matrix["matrix_id"],
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "evidence_ceiling": [
            "H6_SOURCE_POPULATION_ONLY",
            "SOURCE_POPULATED != CANONICALLY_INSTALLED",
            "QUALIFIED_CANDIDATE != MERGED_MASTER",
            "SIX_H6_SEATS_POPULATED != WHOLE_KC144_POPULATED",
        ],
        "matrix": matrix,
    }
    OUTPUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in receipt.items() if k not in {"matrix", "source_receipts"}}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
