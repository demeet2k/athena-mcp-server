from __future__ import annotations

import json
import tempfile
from pathlib import Path

from athena_mcp.bootstrap import bootstrap
from athena_mcp.cell_closure import CellClosureCompiler
from athena_mcp.core import AthenaCore
from athena_mcp.crystal_runtime import CrystalRuntime
from athena_mcp.h6_root import H6RootRuntime
from athena_mcp.store import Store

ARTIFACT = "ATHENA.KC144.GAP.CENSUS.WITNESS.V1"
OUTPUT = Path("kc144_gap_matrix_v1.json")


def main() -> int:
    with tempfile.NamedTemporaryFile(suffix=".db") as tmp:
        store = Store(tmp.name)
        try:
            core = AthenaCore(store)
            bootstrap(core)
            crystal = CrystalRuntime(core)
            h6 = H6RootRuntime(core, crystal)
            compiler = CellClosureCompiler(core, crystal, h6)
            matrix = compiler.matrix()
        finally:
            store.close()

    checks = {
        "seat_count_144": matrix["seat_count"] == 144,
        "block_partition_exact": matrix["block_counts"] == {
            "H6": 6, "X16": 16, "BR21": 21, "F37": 37,
            "IC10": 10, "KC15": 15, "KC27": 27, "SSN12": 12,
        },
        "constitution_closed_144": matrix["dimension_counts"]["constitution_status"] == {"CLOSED": 144},
        "registry_closed_144": matrix["dimension_counts"]["registry_status"] == {"CLOSED": 144},
        "population_not_fabricated": matrix["dimension_counts"]["population_status"] == {"UNKNOWN": 144},
        "execution_not_fabricated": matrix["dimension_counts"]["execution_status"] == {"UNKNOWN": 144},
        "return_not_fabricated": matrix["dimension_counts"]["return_status"] == {"UNKNOWN": 144},
        "known_f37_evidence_holds_retained": matrix["dimension_counts"]["evidence_status"].get("HOLD") == 4,
        "remaining_evidence_unknown": matrix["dimension_counts"]["evidence_status"].get("UNKNOWN") == 140,
        "no_false_closed_seats": matrix["overall_counts"].get("CLOSED", 0) == 0,
        "all_open_seats_have_next_witness": matrix["next_witness_counts"].get("NONE", 0) == 0,
    }
    ok = all(checks.values())
    witness = {
        "artifact": ARTIFACT,
        "status": "STRUCTURAL_CENSUS_MATCH" if ok else "STRUCTURAL_CENSUS_HOLD",
        "checks": checks,
        "matrix_id": matrix["matrix_id"],
        "seat_count": matrix["seat_count"],
        "block_counts": matrix["block_counts"],
        "dimension_counts": matrix["dimension_counts"],
        "overall_counts": matrix["overall_counts"],
        "next_witness_counts": matrix["next_witness_counts"],
        "evidence_ceiling": [
            "STRUCTURAL_CENSUS_ONLY",
            "EMPTY_RUNTIME_DB != GLOBAL_PROJECT_SEARCH",
            "UNKNOWN_POPULATION != MISSING_POPULATION",
            "CONSTITUTION_CLOSED != SEAT_POPULATION_CLOSED",
            "STRUCTURAL_CENSUS_MATCH != WHOLE_KC144_COMPLETION",
        ],
        "matrix": matrix,
    }
    OUTPUT.write_text(json.dumps(witness, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in witness.items() if k != "matrix"}, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
