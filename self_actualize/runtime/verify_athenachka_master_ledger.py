from __future__ import annotations

import json
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
MASTER_LEDGER_ROOT = WORKSPACE_ROOT / "self_actualize" / "master_ledger"
LEDGER_JSON_PATH = MASTER_LEDGER_ROOT / "ATHENACHKA_MASTER_LEDGER.json"


def main() -> int:
    if not LEDGER_JSON_PATH.exists():
        print(f"Missing ledger bundle: {LEDGER_JSON_PATH}")
        return 1
    bundle = json.loads(LEDGER_JSON_PATH.read_text(encoding="utf-8"))
    documents = bundle.get("documents", [])
    nodes = bundle.get("nodes", [])
    routes = bundle.get("routes", [])
    nexuses = {item.get("nexus_id", "") for item in bundle.get("nexuses", [])}
    tunnels = bundle.get("tunnels", [])
    hsigma = bundle.get("master_hologram", {}).get("visible_core_manifest", {})
    checks = {
        "documents_present": bool(documents),
        "nodes_present": bool(nodes),
        "routes_present": bool(routes),
        "nexuses_present": bool(nexuses),
        "no_duplicate_record_ids": len({doc.get("record_id") for doc in documents}) == len(documents),
        "all_documents_have_routes": all(doc.get("upstream_routes") for doc in documents),
        "named_routes_resolve": all(route.get("origin_node") in nexuses and route.get("destination_node") in nexuses for route in bundle.get("reading_routes", [])),
        "tunnels_resolve": all(tunnel.get("exit_node", "").startswith("NODE-") or tunnel.get("exit_node", "") in nexuses for tunnel in tunnels),
        "hsigma_counts": hsigma.get("layer_family_count") == 11 and hsigma.get("route_family_count") == 13 and hsigma.get("seated_explicit_nexus_count") == 16 and hsigma.get("frontier_explicit_nexus_count") == 2 and hsigma.get("inferred_latent_nexus_count") == 1 and hsigma.get("tunnel_class_count") == 6 and hsigma.get("dimensional_strata_count") == 5 and hsigma.get("timing_state_count") == 256 and hsigma.get("mindsweeper_cell_count") == 4864,
    }
    for key, value in checks.items():
        print(f"{key}: {value}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
