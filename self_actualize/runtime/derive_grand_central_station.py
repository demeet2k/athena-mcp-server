from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_BRAIN_ROOT / "registry"

ROOT_BASIS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ROOT_BASIS_MAP.md"
BODY_TENSOR_PATH = SELF_ACTUALIZE_ROOT / "body_tensor.json"
SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
ROUTE_QUALITY_PATH = SELF_ACTUALIZE_ROOT / "route_quality_ledger.json"
DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
CH11_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "30_CHAPTERS"
    / "Ch11_0022_void_book_and_restart_token_tunneling.md"
)

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_grand_central_station"

REGISTRY_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_station_registry.json"
COMMISSURE_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_commissure_ledger.json"
WEIGHT_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"
TUNNEL_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_zpoint_tunnels.json"
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "grand_central_dashboard.json"

REGISTRY_JSON_MIRROR = REGISTRY_ROOT / "grand_central_station_registry.json"
COMMISSURE_JSON_MIRROR = REGISTRY_ROOT / "grand_central_commissure_ledger.json"
WEIGHT_JSON_MIRROR = REGISTRY_ROOT / "grand_central_weight_exchange.json"
TUNNEL_JSON_MIRROR = REGISTRY_ROOT / "grand_central_zpoint_tunnels.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / "grand_central_dashboard.json"

REGISTRY_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "GRAND_CENTRAL_STATION_REGISTRY.md"
)
COMMISSURE_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "17_GRAND_CENTRAL_COMMISSURE_LEDGER.md"
)
WEIGHT_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "18_GRAND_CENTRAL_WEIGHT_EXCHANGE.md"
)
TUNNEL_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "90_LEDGERS" / "19_Z_POINT_TUNNEL_LEDGER.md"
)
DASHBOARD_MD_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "GRAND_CENTRAL_STATION_DASHBOARD.md"
)
RUNTIME_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "nervous_system" / "24_grand_central_station_runtime.md"
)
RECEIPT_MD_PATH = (
    MYCELIUM_BRAIN_ROOT / "receipts" / "2026-03-12_grand_central_station_derivation.md"
)

STATUS_TO_BRANCH = {
    "absorbed": "live",
    "reserve": "reserve",
    "dormant": "dormant",
    "mirror": "mirror",
    "local": "local",
    "out_of_scope": "out_of_scope",
}

STATUS_PROOF_WEIGHT = {
    "live": 0.94,
    "reserve": 0.68,
    "dormant": 0.44,
    "mirror": 0.58,
    "local": 0.74,
    "out_of_scope": 0.25,
}

ROLE_COST_BONUS = {
    "generated": 0.18,
    "protocol": 0.08,
    "ledger": 0.06,
    "mirror": 0.12,
    "source": 0.02,
}

COMMISSURE_CLASS_BONUS = {
    "proof bridge": 0.10,
    "meaning bridge": 0.08,
    "execution bridge": 0.09,
    "continuity bridge": 0.11,
}

CONTINUITY_BASE = {
    "proof bridge": 0.82,
    "meaning bridge": 0.88,
    "execution bridge": 0.86,
    "continuity bridge": 0.93,
}

STATION_META = {
    "NERVOUS_SYSTEM": {
        "hemisphere": "left",
        "tract": "address",
        "bundle": "B64-A01-ADDR",
        "fiber": "integrate",
        "synapse": "bind",
        "authority_level": "canonical",
        "exchange": "GCL",
    },
    "self_actualize": {
        "hemisphere": "bilateral",
        "tract": "replay",
        "bundle": "B64-A02-REPLAY",
        "fiber": "return",
        "synapse": "reseed",
        "authority_level": "runtime",
        "exchange": "GCL+GCR",
    },
    "ECOSYSTEM": {
        "hemisphere": "left",
        "tract": "relation",
        "bundle": "B64-A03-RELATE",
        "fiber": "transmit",
        "synapse": "gate",
        "authority_level": "governance",
        "exchange": "GCL",
    },
    "DEEPER CRYSTALIZATION": {
        "hemisphere": "bilateral",
        "tract": "chamber",
        "bundle": "B64-A04-QUAR",
        "fiber": "integrate",
        "synapse": "gate",
        "authority_level": "historical-absorbed",
        "exchange": "GCL+GCR",
    },
    "MATH": {
        "hemisphere": "left",
        "tract": "chamber",
        "bundle": "B64-A05-PROOF",
        "fiber": "integrate",
        "synapse": "bind",
        "authority_level": "canonical-domain",
        "exchange": "GCL",
    },
    "Voynich": {
        "hemisphere": "right",
        "tract": "relation",
        "bundle": "B64-A06-MEAN",
        "fiber": "sense",
        "synapse": "bind",
        "authority_level": "canonical-domain",
        "exchange": "GCR",
    },
    "Trading Bot": {
        "hemisphere": "bilateral",
        "tract": "replay",
        "bundle": "B64-A07-GATE",
        "fiber": "transmit",
        "synapse": "gate",
        "authority_level": "external-bridge",
        "exchange": "GCL+GCR",
    },
    "Quadrant Binary": {
        "hemisphere": "left",
        "tract": "address",
        "bundle": "B64-A08-BIT4",
        "fiber": "sense",
        "synapse": "prime",
        "authority_level": "ancestor-kernel",
        "exchange": "GCL",
    },
    "QSHRINK - ATHENA (internal use)": {
        "hemisphere": "left",
        "tract": "chamber",
        "bundle": "B64-A09-COMP",
        "fiber": "integrate",
        "synapse": "gate",
        "authority_level": "compression-shell",
        "exchange": "GCL",
    },
    "NERUAL NETWORK": {
        "hemisphere": "bilateral",
        "tract": "relation",
        "bundle": "B64-A10-ADAPT",
        "fiber": "transmit",
        "synapse": "bind",
        "authority_level": "runtime-lab",
        "exchange": "GCL+GCR",
    },
    "FRESH": {
        "hemisphere": "right",
        "tract": "address",
        "bundle": "B64-A11-INTAKE",
        "fiber": "sense",
        "synapse": "prime",
        "authority_level": "intake-fringe",
        "exchange": "GCR",
    },
    "Athenachka Collective Books": {
        "hemisphere": "right",
        "tract": "replay",
        "bundle": "B64-A12-PUBLISH",
        "fiber": "return",
        "synapse": "bind",
        "authority_level": "publication-halo",
        "exchange": "GCR",
    },
    "I AM ATHENA": {
        "hemisphere": "right",
        "tract": "chamber",
        "bundle": "B64-A13-IDENT",
        "fiber": "integrate",
        "synapse": "bind",
        "authority_level": "identity-shell",
        "exchange": "GCR",
    },
    "GAMES": {
        "hemisphere": "right",
        "tract": "relation",
        "bundle": "B64-A14-SIM",
        "fiber": "transmit",
        "synapse": "gate",
        "authority_level": "simulation-lab",
        "exchange": "GCR",
    },
    "ORGIN": {
        "hemisphere": "right",
        "tract": "chamber",
        "bundle": "B64-A15-SEED",
        "fiber": "sense",
        "synapse": "reseed",
        "authority_level": "seed-reservoir",
        "exchange": "GCR",
    },
    "Athena FLEET": {
        "hemisphere": "bilateral",
        "tract": "relation",
        "bundle": "B64-A16-FLEET",
        "fiber": "transmit",
        "synapse": "bind",
        "authority_level": "pilot-cluster",
        "exchange": "GCL+GCR",
    },
    "Stoicheia (Element Sudoku)": {
        "hemisphere": "left",
        "tract": "relation",
        "bundle": "B64-A17-PLAY",
        "fiber": "sense",
        "synapse": "prime",
        "authority_level": "reserve-visual",
        "exchange": "GCL",
    },
    "CLEAN": {
        "hemisphere": "left",
        "tract": "chamber",
        "bundle": "B64-A18-STAGE",
        "fiber": "integrate",
        "synapse": "prime",
        "authority_level": "reserve-staging",
        "exchange": "GCL",
    },
    "mycelial_unified_nervous_system_bundle": {
        "hemisphere": "bilateral",
        "tract": "replay",
        "bundle": "B64-A19-BUNDLE",
        "fiber": "return",
        "synapse": "gate",
        "authority_level": "dormant-bundle",
        "exchange": "GCL+GCR",
    },
}

COMMISSURE_SPECS = [
    {
        "commissure_id": "C-001",
        "source_family": "MATH",
        "target_family": "Voynich",
        "class": "proof bridge",
        "purpose": "translate theorem kernels into operator-bearing manuscript law",
        "replay_policy": "close through GCP and AppM before promotion",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-002",
        "source_family": "self_actualize",
        "target_family": "NERVOUS_SYSTEM",
        "class": "execution bridge",
        "purpose": "write runtime state back into the canonical cortex without bypassing replay",
        "replay_policy": "runtime receipt required before cortex claim",
        "proof_state": "OK",
    },
    {
        "commissure_id": "C-003",
        "source_family": "QSHRINK - ATHENA (internal use)",
        "target_family": "self_actualize",
        "class": "execution bridge",
        "purpose": "turn compression doctrine into routable runtime arbitration rather than ambient shell mass",
        "replay_policy": "weight exchange must emit a dispatch score and receipt",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-004",
        "source_family": "ORGIN",
        "target_family": "I AM ATHENA",
        "class": "continuity bridge",
        "purpose": "preserve seed identity continuity across proto-self and current self surfaces",
        "replay_policy": "restart token required for any promotion across identity states",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-005",
        "source_family": "Athena FLEET",
        "target_family": "NERVOUS_SYSTEM",
        "class": "execution bridge",
        "purpose": "dock the promoted fleet cluster into canonical routing and proof-bearing publication surfaces",
        "replay_policy": "promotion must land through Grand Central then replay closure",
        "proof_state": "OK",
    },
    {
        "commissure_id": "C-006",
        "source_family": "Voynich",
        "target_family": "Athenachka Collective Books",
        "class": "meaning bridge",
        "purpose": "let translation work condense into publication-ready continuity surfaces",
        "replay_policy": "appendix and publication receipts required before export",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-007",
        "source_family": "Trading Bot",
        "target_family": "self_actualize",
        "class": "execution bridge",
        "purpose": "keep external-memory tooling grounded in the local runtime hub while the Docs gate stays blocked",
        "replay_policy": "blocked gate state must be cited at every crossing",
        "proof_state": "OK",
    },
    {
        "commissure_id": "C-008",
        "source_family": "DEEPER CRYSTALIZATION",
        "target_family": "self_actualize",
        "class": "continuity bridge",
        "purpose": "fold precursor integration mass back into the live runtime without restoring mirror authority",
        "replay_policy": "historical status must be preserved in any writeback",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-009",
        "source_family": "GAMES",
        "target_family": "Stoicheia (Element Sudoku)",
        "class": "meaning bridge",
        "purpose": "connect simulation mechanics to the reserve puzzle shelf as structure-play evidence",
        "replay_policy": "reserve status must remain visible at promotion time",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-010",
        "source_family": "ECOSYSTEM",
        "target_family": "MATH",
        "class": "proof bridge",
        "purpose": "bind governance doctrine to theorem-bearing transport and operator law",
        "replay_policy": "governance mirror cannot outrank the cortex at closure time",
        "proof_state": "OK",
    },
    {
        "commissure_id": "C-011",
        "source_family": "NERUAL NETWORK",
        "target_family": "self_actualize",
        "class": "execution bridge",
        "purpose": "route adaptive runtime experiments into the live writeback waist without side-channel drift",
        "replay_policy": "runtime harness or receipt required before promotion",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-012",
        "source_family": "CLEAN",
        "target_family": "DEEPER CRYSTALIZATION",
        "class": "continuity bridge",
        "purpose": "turn the clean staging shelf into a lawful reserve corridor instead of a silent side pile",
        "replay_policy": "promotion closes through pruning or staging receipt",
        "proof_state": "NEAR",
    },
    {
        "commissure_id": "C-013",
        "source_family": "mycelial_unified_nervous_system_bundle",
        "target_family": "self_actualize",
        "class": "continuity bridge",
        "purpose": "keep the dormant bundle shelf tied to the live runtime waist without restoring it as a peer organism",
        "replay_policy": "bundle state must remain dormant unless explicitly reactivated through replay",
        "proof_state": "NEAR",
    },
]

TUNNEL_SPECS = [
    {
        "tunnel_id": "ZT-001",
        "tunnel_class": "Z0 intake",
        "entry_route": "FRESH -> GCA -> NERVOUS_SYSTEM",
        "restart_token": "INTAKE-FIRST-WITNESS",
        "zero_state": "unknown placement held without premature classification",
        "resume_target": "A11 intake fringe receives first lawful station address",
        "continuity_receipt": "root-basis assignment plus first witness shell",
        "proof_state": "NEAR",
    },
    {
        "tunnel_id": "ZT-002",
        "tunnel_class": "Z1 restart",
        "entry_route": "ORGIN -> GCZ -> Ch11<0022> -> self_actualize",
        "restart_token": "CH11-RESTART-CONTINUITY",
        "zero_state": "continuity break admitted without false carry-forward",
        "resume_target": "runtime replay waist with preserved restart receipt",
        "continuity_receipt": "Ch11 restart token plus runtime writeback",
        "proof_state": "OK",
    },
    {
        "tunnel_id": "ZT-003",
        "tunnel_class": "Z2 contradiction",
        "entry_route": "Voynich -> GCC -> GCZ -> chamber quarantine",
        "restart_token": "CONTRADICTION-PRESERVE-BOTH",
        "zero_state": "paired hypotheses preserved instead of prematurely collapsed",
        "resume_target": "bounded manuscript lane with contradiction visible",
        "continuity_receipt": "quarantine note and replay-safe dual reading",
        "proof_state": "NEAR",
    },
    {
        "tunnel_id": "ZT-004",
        "tunnel_class": "Z3 repair",
        "entry_route": "DEEPER CRYSTALIZATION -> GCZ -> self_actualize",
        "restart_token": "PRECURSOR-REPAIR-DELTA",
        "zero_state": "historical drift held long enough for lawful repair",
        "resume_target": "runtime repair surfaces and receipts",
        "continuity_receipt": "repair receipt preserving mirror status",
        "proof_state": "NEAR",
    },
    {
        "tunnel_id": "ZT-005",
        "tunnel_class": "Z4 promotion",
        "entry_route": "Athena FLEET -> GCX -> 14_DEEPER... -> NERVOUS_SYSTEM",
        "restart_token": "FLEET-PROMOTION-DOCK",
        "zero_state": "promoted cluster held in the departure yard before cortex claim",
        "resume_target": "canonical fleet bridge and deep-root dock",
        "continuity_receipt": "promotion receipt plus registry entry",
        "proof_state": "OK",
    },
    {
        "tunnel_id": "ZT-006",
        "tunnel_class": "Z5 pruning",
        "entry_route": "historical skill mirrors -> GCZ -> witness shelf",
        "restart_token": "SOFT-DEMOTION-WITNESS",
        "zero_state": "authority removed without deleting lineage",
        "resume_target": "historical mirror status with live-router pointer intact",
        "continuity_receipt": "deprecation map and pruning ledger",
        "proof_state": "OK",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_live_directory_bodies(markdown: str) -> list[dict]:
    lines = markdown.splitlines()
    rows: list[dict] = []
    capture = False
    for line in lines:
        if line.startswith("## Live Directory Bodies"):
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if not capture or not line.startswith("| A"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) < 5:
            continue
        code, root, indexed_count, status, current_role = parts[:5]
        rows.append(
            {
                "root_id": code,
                "root_name": root.strip("`"),
                "indexed_count": int(indexed_count.strip("`")),
                "root_status": status.strip("`"),
                "current_role": current_role,
            }
        )
    return rows


def parse_docs_gate(markdown: str) -> str:
    match = re.search(r"Command status: `([^`]+)`", markdown)
    if match:
        return match.group(1)
    return "UNKNOWN"


def latest_route_baseline(payload: dict) -> float:
    entries = payload.get("entries", [])
    if not entries:
        return 0.75
    tail = entries[-5:]
    return sum(entry.get("route_score", 0.75) for entry in tail) / len(tail)


def normalize(value: float, floor: float = 0.0, ceiling: float = 1.0) -> float:
    return max(floor, min(ceiling, value))


def authority_rank(authority_level: str) -> int:
    order = {
        "canonical": 5,
        "runtime": 5,
        "governance": 4,
        "canonical-domain": 4,
        "external-bridge": 4,
        "pilot-cluster": 4,
        "compression-shell": 4,
        "historical-absorbed": 3,
        "ancestor-kernel": 3,
        "runtime-lab": 3,
        "publication-halo": 3,
        "identity-shell": 3,
        "simulation-lab": 3,
        "seed-reservoir": 3,
        "intake-fringe": 2,
        "reserve-visual": 2,
        "reserve-staging": 2,
        "dormant-bundle": 1,
    }
    return order.get(authority_level, 2)


def build_station_registry(
    root_rows: list[dict], body_tensor: dict, semantic_mass: dict, docs_gate: str
) -> dict:
    body_profiles = {
        item["body"]: item for item in semantic_mass.get("body_profiles", [])
    }
    tensor_profiles = {
        item["body"]: item for item in body_tensor.get("bronze_bodies", [])
    }

    registry_rows = []
    hemisphere_totals = {"left": 0, "right": 0, "bilateral": 0}
    tract_totals = {"address": 0, "relation": 0, "chamber": 0, "replay": 0}
    status_totals = {
        "live": 0,
        "mirror": 0,
        "local": 0,
        "reserve": 0,
        "dormant": 0,
        "out_of_scope": 0,
    }

    for row in root_rows:
        name = row["root_name"]
        meta = STATION_META[name]
        tensor = tensor_profiles.get(name, {})
        profile = body_profiles.get(name, {})
        branch_status = STATUS_TO_BRANCH.get(row["root_status"], row["root_status"])
        authority_level = meta["authority_level"]
        station_address = (
            f"GC0::{meta['exchange']}::{row['root_id']}::{meta['tract']}::"
            f"{meta['bundle']}::{meta['fiber']}::{meta['synapse']}"
        )
        registry_rows.append(
            {
                "station_address": station_address,
                "root_id": row["root_id"],
                "root_name": name,
                "indexed_count": row["indexed_count"],
                "hemisphere": meta["hemisphere"],
                "tract": meta["tract"],
                "bundle": meta["bundle"],
                "fiber": meta["fiber"],
                "synapse": meta["synapse"],
                "status": branch_status,
                "authority_level": authority_level,
                "authority_rank": authority_rank(authority_level),
                "routing_role": tensor.get("routing_role", row["current_role"]),
                "macro_element": tensor.get("macro_element", "Unassigned"),
                "dominant_role": profile.get("dominant_role", "source"),
                "witness_class": "indexed",
                "docs_gate": docs_gate,
            }
        )
        hemisphere_totals[meta["hemisphere"]] += 1
        tract_totals[meta["tract"]] += 1
        status_totals[branch_status] += 1

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.gc-v1",
        "derivation_command": DERIVATION_COMMAND,
        "docs_gate": docs_gate,
        "source_paths": {
            "root_basis_map": str(ROOT_BASIS_PATH),
            "body_tensor": str(BODY_TENSOR_PATH),
            "semantic_mass_ledger": str(SEMANTIC_MASS_PATH),
            "live_docs_gate": str(DOCS_GATE_PATH),
        },
        "source_timestamps": {
            "root_basis_map": file_timestamp(ROOT_BASIS_PATH),
            "body_tensor": file_timestamp(BODY_TENSOR_PATH),
            "semantic_mass_ledger": file_timestamp(SEMANTIC_MASS_PATH),
            "live_docs_gate": file_timestamp(DOCS_GATE_PATH),
        },
        "registry": registry_rows,
        "summary": {
            "root_count": len(registry_rows),
            "hemisphere_totals": hemisphere_totals,
            "tract_totals": tract_totals,
            "status_totals": status_totals,
        },
    }


def build_commissures(registry_payload: dict) -> dict:
    registry = {entry["root_name"]: entry for entry in registry_payload["registry"]}
    rows = []
    for spec in COMMISSURE_SPECS:
        src = registry[spec["source_family"]]
        dst = registry[spec["target_family"]]
        rows.append(
            {
                **spec,
                "source_station": src["station_address"],
                "target_station": dst["station_address"],
                "source_hemisphere": src["hemisphere"],
                "target_hemisphere": dst["hemisphere"],
                "source_status": src["status"],
                "target_status": dst["status"],
            }
        )
    bilateral_roots = [
        entry["root_name"]
        for entry in registry_payload["registry"]
        if entry["hemisphere"] == "bilateral"
    ]
    covered_roots = {
        item["source_family"] for item in rows
    } | {item["target_family"] for item in rows}
    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.gc-v1",
        "docs_gate": registry_payload["docs_gate"],
        "commissures": rows,
        "summary": {
            "commissure_count": len(rows),
            "covered_bilateral_roots": sorted(
                root for root in bilateral_roots if root in covered_roots
            ),
            "missing_bilateral_roots": sorted(
                root for root in bilateral_roots if root not in covered_roots
            ),
            "class_totals": {
                key: sum(1 for item in rows if item["class"] == key)
                for key in COMMISSURE_CLASS_BONUS
            },
        },
    }


def compute_route_weights(
    registry_payload: dict, commissure_payload: dict, route_quality_payload: dict
) -> dict:
    registry = {entry["root_name"]: entry for entry in registry_payload["registry"]}
    max_count = max(entry["indexed_count"] for entry in registry.values())
    route_baseline = latest_route_baseline(route_quality_payload)
    rows = []

    for commissure in commissure_payload["commissures"]:
        src = registry[commissure["source_family"]]
        dst = registry[commissure["target_family"]]
        avg_count = (src["indexed_count"] + dst["indexed_count"]) / 2
        salience = normalize(max(src["indexed_count"], dst["indexed_count"]) / max_count)
        proof = normalize(
            (
                STATUS_PROOF_WEIGHT[src["status"]]
                + STATUS_PROOF_WEIGHT[dst["status"]]
            )
            / 2
            * 0.88
            + COMMISSURE_CLASS_BONUS[commissure["class"]]
        )
        freshness = route_baseline
        if src["status"] == "live" and dst["status"] == "live":
            freshness += 0.08
        if (
            "Trading Bot" in (src["root_name"], dst["root_name"])
            and registry_payload["docs_gate"] == "BLOCKED"
        ):
            freshness -= 0.12
        if "reserve" in (src["status"], dst["status"]):
            freshness -= 0.05
        freshness = normalize(freshness)
        dominant_roles = [src["dominant_role"], dst["dominant_role"]]
        cost = 0.25 + 0.55 * math.sqrt(avg_count / max_count)
        cost += sum(ROLE_COST_BONUS.get(role, 0.04) for role in dominant_roles) / 2
        if commissure["class"] == "continuity bridge":
            cost -= 0.04
        cost = normalize(cost)
        continuity = CONTINUITY_BASE[commissure["class"]]
        if {"ORGIN", "I AM ATHENA"} & {src["root_name"], dst["root_name"]}:
            continuity += 0.03
        if {"Voynich", "Athenachka Collective Books"} & {
            src["root_name"],
            dst["root_name"],
        }:
            continuity += 0.02
        continuity = normalize(continuity)
        confidence = normalize((proof + freshness) / 2)
        replay_value = 0.82
        if {src["root_name"], dst["root_name"]} & {
            "NERVOUS_SYSTEM",
            "self_actualize",
            "QSHRINK - ATHENA (internal use)",
            "Trading Bot",
            "Athena FLEET",
        }:
            replay_value = 0.93
        dispatch_score = round(
            2.5 * salience
            + 2.0 * proof
            + 1.5 * freshness
            + 1.25 * continuity
            + 1.5 * confidence
            + 1.5 * replay_value
            - 1.5 * cost,
            3,
        )
        rows.append(
            {
                "commissure_id": commissure["commissure_id"],
                "source_family": commissure["source_family"],
                "target_family": commissure["target_family"],
                "bridge_class": commissure["class"],
                "weight": {
                    "salience": round(salience, 3),
                    "proof": round(proof, 3),
                    "freshness": round(freshness, 3),
                    "cost": round(cost, 3),
                    "continuity": round(continuity, 3),
                    "confidence": round(confidence, 3),
                    "replay_value": round(replay_value, 3),
                },
                "dispatch_score": dispatch_score,
                "witness_floor": round(min(proof, confidence), 3),
                "proof_state": commissure["proof_state"],
                "replay_policy": commissure["replay_policy"],
            }
        )

    rows.sort(key=lambda item: item["dispatch_score"], reverse=True)
    promotion_threshold = 6.35
    live_interchange_threshold = 7.0
    soft_demotion_threshold = 5.4

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.gc-v1",
        "docs_gate": registry_payload["docs_gate"],
        "route_baseline": round(route_baseline, 3),
        "thresholds": {
            "promotion_threshold": promotion_threshold,
            "live_interchange_threshold": live_interchange_threshold,
            "soft_demotion_threshold": soft_demotion_threshold,
        },
        "routes": rows,
        "summary": {
            "top_dispatch_routes": [row["commissure_id"] for row in rows[:5]],
            "promotable_routes": [
                row["commissure_id"]
                for row in rows
                if row["dispatch_score"] >= promotion_threshold
            ],
            "watch_routes": [
                row["commissure_id"]
                for row in rows
                if row["dispatch_score"] < soft_demotion_threshold
            ],
        },
    }


def build_tunnels(registry_payload: dict) -> dict:
    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.gc-v1",
        "docs_gate": registry_payload["docs_gate"],
        "kernel": {
            "source": str(CH11_PATH),
            "source_timestamp": file_timestamp(CH11_PATH),
            "law": "Ch11<0022> is the lawful restart-token and zero-point tunnel kernel.",
        },
        "tunnels": TUNNEL_SPECS,
        "summary": {
            "tunnel_count": len(TUNNEL_SPECS),
            "classes": [spec["tunnel_class"] for spec in TUNNEL_SPECS],
            "mandatory_for": [
                "critical manuscript flows",
                "runtime repair flows",
                "promotion crossings",
                "pruning crossings",
            ],
        },
    }


def build_dashboard(
    registry_payload: dict,
    commissure_payload: dict,
    weight_payload: dict,
    tunnel_payload: dict,
) -> dict:
    top_routes = weight_payload["routes"][:5]
    left = registry_payload["summary"]["hemisphere_totals"]["left"]
    right = registry_payload["summary"]["hemisphere_totals"]["right"]
    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.gc-v1",
        "docs_gate": registry_payload["docs_gate"],
        "station_status": "LIVE_LOCAL_SCOPE",
        "root_count": registry_payload["summary"]["root_count"],
        "hemisphere_totals": registry_payload["summary"]["hemisphere_totals"],
        "tract_totals": registry_payload["summary"]["tract_totals"],
        "status_totals": registry_payload["summary"]["status_totals"],
        "commissure_count": commissure_payload["summary"]["commissure_count"],
        "tunnel_count": tunnel_payload["summary"]["tunnel_count"],
        "promotion_threshold": weight_payload["thresholds"]["promotion_threshold"],
        "live_interchange_threshold": weight_payload["thresholds"]["live_interchange_threshold"],
        "soft_demotion_threshold": weight_payload["thresholds"]["soft_demotion_threshold"],
        "top_dispatch_routes": top_routes,
        "hemisphere_balance_delta": abs(left - right),
        "bilateral_coverage_ok": not commissure_payload["summary"]["missing_bilateral_roots"],
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def render_registry_markdown(payload: dict) -> str:
    rows = []
    for entry in payload["registry"]:
        rows.append(
            [
                entry["root_id"],
                f"`{entry['root_name']}`",
                entry["station_address"],
                entry["hemisphere"],
                entry["tract"],
                entry["bundle"],
                entry["fiber"],
                entry["synapse"],
                entry["status"],
                entry["authority_level"],
            ]
        )
    table = markdown_table(
        [
            "Root",
            "Name",
            "Station Address",
            "Hemisphere",
            "Tract",
            "Bundle",
            "Fiber",
            "Synapse",
            "Status",
            "Authority",
        ],
        rows,
    )
    summary = payload["summary"]
    return f"""# Grand Central Station Registry

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Docs gate: `{payload['docs_gate']}`
Verdict: `OK`

This manifest is the canonical root registry for Grand Central Station.
It is keyed by station address, root ID, hemisphere, tract, bundle, fiber, synapse,
status, and authority level.

## Station Law

`GC0` is the common hall.
Every major root now receives one lawful docking coordinate inside that hall.

## Registry

{table}

## Summary

- root count: `{summary['root_count']}`
- hemisphere totals:
  `left {summary['hemisphere_totals']['left']}`, `right {summary['hemisphere_totals']['right']}`, `bilateral {summary['hemisphere_totals']['bilateral']}`
- tract totals:
  `address {summary['tract_totals']['address']}`, `relation {summary['tract_totals']['relation']}`, `chamber {summary['tract_totals']['chamber']}`, `replay {summary['tract_totals']['replay']}`
- branch states:
  `live {summary['status_totals']['live']}`, `reserve {summary['status_totals']['reserve']}`, `dormant {summary['status_totals']['dormant']}`

## Derivation

- command:
  `{payload['derivation_command']}`
- sources:
  `ROOT_BASIS_MAP`, `body_tensor.json`, `semantic_mass_ledger.json`, and `live_docs_gate_status.md`

## Interpretation

- `hemisphere` records the primary exchange side, not an absolute exclusion of cross-traffic
- `tract` records the main station duty through Address, Relation, Chamber, or Replay
- `status` uses the normalized branch taxonomy: `live`, `reserve`, or `dormant`
- `authority_level` records how strongly the root may speak inside the station
"""


def render_commissure_markdown(payload: dict, weight_payload: dict) -> str:
    weight_map = {
        row["commissure_id"]: row["dispatch_score"] for row in weight_payload["routes"]
    }
    rows = []
    for item in payload["commissures"]:
        rows.append(
            [
                item["commissure_id"],
                f"`{item['source_family']}`",
                f"`{item['target_family']}`",
                item["class"],
                item["purpose"],
                f"`{weight_map[item['commissure_id']]}`",
                item["proof_state"],
            ]
        )
    table = markdown_table(
        ["ID", "Source", "Target", "Class", "Purpose", "Dispatch", "Proof"],
        rows,
    )
    summary = payload["summary"]
    return f"""# Grand Central Commissure Ledger

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Docs gate: `{payload['docs_gate']}`
Verdict: `OK`

The commissure layer makes the two hemispheres explicit and lawful.
No bilateral root should remain unbridged by the time it claims cross-corpus authority.

## Commissures

{table}

## Coverage

- commissure count: `{summary['commissure_count']}`
- proof bridges: `{summary['class_totals']['proof bridge']}`
- meaning bridges: `{summary['class_totals']['meaning bridge']}`
- execution bridges: `{summary['class_totals']['execution bridge']}`
- continuity bridges: `{summary['class_totals']['continuity bridge']}`
- covered bilateral roots:
  `{", ".join(summary['covered_bilateral_roots'])}`
- missing bilateral roots:
  `{", ".join(summary['missing_bilateral_roots']) if summary['missing_bilateral_roots'] else "none"}`

## Law

1. proof bridges translate left-hemisphere certainty into right-hemisphere meaning
2. meaning bridges keep symbolic and publication continuity from floating free of routing law
3. execution bridges move runtime or promoted work into the cortex without replay loss
4. continuity bridges preserve identity and precursor memory across restart-bearing crossings
"""


def render_weight_markdown(payload: dict) -> str:
    rows = []
    for item in payload["routes"]:
        weight = item["weight"]
        rows.append(
            [
                item["commissure_id"],
                f"`{item['source_family']}` -> `{item['target_family']}`",
                f"{weight['salience']:.3f}",
                f"{weight['proof']:.3f}",
                f"{weight['freshness']:.3f}",
                f"{weight['cost']:.3f}",
                f"{weight['continuity']:.3f}",
                f"{weight['confidence']:.3f}",
                f"{weight['replay_value']:.3f}",
                f"{item['dispatch_score']:.3f}",
            ]
        )
    table = markdown_table(
        [
            "ID",
            "Route",
            "Salience",
            "Proof",
            "Freshness",
            "Cost",
            "Continuity",
            "Confidence",
            "Replay",
            "Dispatch",
        ],
        rows,
    )
    thresholds = payload["thresholds"]
    return f"""# Grand Central Weight Exchange

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Docs gate: `{payload['docs_gate']}`
Verdict: `OK`

This ledger defines the unified internal weight vector for Grand Central Station.

## Weight Fields

- `salience`: how much corpus mass or strategic centrality the route carries
- `proof`: how much witness-bearing authority the route currently owns
- `freshness`: how alive and current the route is in the runtime organism
- `cost`: how expensive the route is to maintain or metabolize
- `continuity`: how well the route preserves lawful carry-through across changes
- `confidence`: confidence floor derived from proof and freshness together
- `replay_value`: how well the route closes through replay, receipt, and rerun

## Dispatch Law

`dispatch = 2.5*salience + 2*proof + 1.5*freshness + 1.25*continuity + 1.5*confidence + 1.5*replay - 1.5*cost`

## Route Weights

{table}

## Thresholds

- promotion threshold: `{thresholds['promotion_threshold']}`
- live interchange threshold: `{thresholds['live_interchange_threshold']}`
- soft demotion threshold: `{thresholds['soft_demotion_threshold']}`
- route baseline freshness: `{payload['route_baseline']}`

## Promotion Law

- routes above the promotion threshold may claim live interchange attention
- routes above the live interchange threshold are first-wave station priorities
- routes below the soft demotion threshold stay readable, but should not outrank fresher corridors
"""


def render_tunnel_markdown(payload: dict) -> str:
    rows = []
    for item in payload["tunnels"]:
        rows.append(
            [
                item["tunnel_id"],
                item["tunnel_class"],
                item["entry_route"],
                item["restart_token"],
                item["resume_target"],
                item["proof_state"],
            ]
        )
    table = markdown_table(
        ["Tunnel", "Class", "Entry Route", "Restart Token", "Resume Target", "Proof"],
        rows,
    )
    return f"""# Z-Point Tunnel Ledger

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Docs gate: `{payload['docs_gate']}`
Verdict: `OK`

This ledger turns the Z-point tunnel framework into explicit station traffic.

## Kernel

- source:
  `{payload['kernel']['source']}`
- law:
  {payload['kernel']['law']}

## Tunnels

{table}

## Continuity Law

Every tunnel crossing must:

1. name the entry route
2. carry a restart token
3. admit the zero state honestly
4. name the resume target
5. leave one continuity receipt instead of disappearing into metaphor
"""


def render_dashboard_markdown(payload: dict, registry_payload: dict) -> str:
    route_rows = []
    for item in payload["top_dispatch_routes"]:
        route_rows.append(
            [
                item["commissure_id"],
                f"`{item['source_family']}` -> `{item['target_family']}`",
                f"{item['dispatch_score']:.3f}",
                item["bridge_class"],
            ]
        )
    route_table = markdown_table(
        ["Ranked Route", "Path", "Dispatch", "Class"],
        route_rows,
    )
    status = registry_payload["summary"]["status_totals"]
    return f"""# Grand Central Station Dashboard

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Docs gate: `{payload['docs_gate']}`
Station status: `{payload['station_status']}`

## Whole Station

- stationed roots: `{payload['root_count']}`
- commissures: `{payload['commissure_count']}`
- tunnels: `{payload['tunnel_count']}`
- hemisphere balance delta: `{payload['hemisphere_balance_delta']}`
- bilateral coverage ok: `{payload['bilateral_coverage_ok']}`

## Branch States

- live: `{status['live']}`
- reserve: `{status['reserve']}`
- dormant: `{status['dormant']}`

## Thresholds

- promotion: `{payload['promotion_threshold']}`
- live interchange: `{payload['live_interchange_threshold']}`
- soft demotion: `{payload['soft_demotion_threshold']}`

## Top Dispatch Routes

{route_table}

## Honest Limits

- Google Docs ingress is still blocked, so no live external memory lane is claimed here
- Grand Central is live for local scope, not yet universal closure
- the next machine step is deeper edge propagation from this station into broader route ledgers
"""


def render_runtime_markdown(
    registry_payload: dict, dashboard_payload: dict, weight_payload: dict
) -> str:
    top = dashboard_payload["top_dispatch_routes"][0]
    return f"""# Grand Central Station Runtime

Date: `{registry_payload['generated_at'][:10]}`
Generated: `{registry_payload['generated_at']}`
Docs gate: `{registry_payload['docs_gate']}`
Verdict: `OK`

This is the runtime mirror of Grand Central Station.
It keeps the station state readable from the mycelium side without inventing a second authority surface.

## Active Files

- `self_actualize/grand_central_station_registry.json`
- `self_actualize/grand_central_commissure_ledger.json`
- `self_actualize/grand_central_weight_exchange.json`
- `self_actualize/grand_central_zpoint_tunnels.json`
- `self_actualize/grand_central_dashboard.json`

## Current Runtime Read

- stationed roots: `{dashboard_payload['root_count']}`
- bilateral roots: `{registry_payload['summary']['hemisphere_totals']['bilateral']}`
- top dispatch route:
  `{top['commissure_id']} {top['source_family']} -> {top['target_family']} = {top['dispatch_score']:.3f}`
- live interchange threshold:
  `{weight_payload['thresholds']['live_interchange_threshold']}`

## Regeneration

Run:

```powershell
python -m self_actualize.runtime.derive_grand_central_station
```

This mirror should follow the canonical cortex registry and dashboard, not drift away from them.
"""


def render_receipt_markdown(dashboard_payload: dict) -> str:
    return f"""# Grand Central Station Derivation Receipt

- Generated: `{dashboard_payload['generated_at']}`
- Command: `{DERIVATION_COMMAND}`
- Docs gate: `{dashboard_payload['docs_gate']}`
- Station status: `{dashboard_payload['station_status']}`

## Outputs

- `self_actualize/grand_central_station_registry.json`
- `self_actualize/grand_central_commissure_ledger.json`
- `self_actualize/grand_central_weight_exchange.json`
- `self_actualize/grand_central_zpoint_tunnels.json`
- `self_actualize/grand_central_dashboard.json`
- `NERVOUS_SYSTEM/95_MANIFESTS/GRAND_CENTRAL_STATION_REGISTRY.md`
- `NERVOUS_SYSTEM/90_LEDGERS/17_GRAND_CENTRAL_COMMISSURE_LEDGER.md`
- `NERVOUS_SYSTEM/90_LEDGERS/18_GRAND_CENTRAL_WEIGHT_EXCHANGE.md`
- `NERVOUS_SYSTEM/90_LEDGERS/19_Z_POINT_TUNNEL_LEDGER.md`
- `NERVOUS_SYSTEM/95_MANIFESTS/GRAND_CENTRAL_STATION_DASHBOARD.md`
- `self_actualize/mycelium_brain/nervous_system/24_grand_central_station_runtime.md`

## Summary

- stationed roots: `{dashboard_payload['root_count']}`
- commissures: `{dashboard_payload['commissure_count']}`
- tunnels: `{dashboard_payload['tunnel_count']}`
- bilateral coverage ok: `{dashboard_payload['bilateral_coverage_ok']}`

## Honest Scope

This receipt certifies a local-scope Grand Central implementation.
The Google Docs limb remains blocked and is therefore not counted as a live station ingress.
"""


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    root_basis = ROOT_BASIS_PATH.read_text(encoding="utf-8")
    docs_gate = parse_docs_gate(DOCS_GATE_PATH.read_text(encoding="utf-8"))
    body_tensor = load_json(BODY_TENSOR_PATH)
    semantic_mass = load_json(SEMANTIC_MASS_PATH)
    route_quality = load_json(ROUTE_QUALITY_PATH)

    root_rows = parse_live_directory_bodies(root_basis)
    registry_payload = build_station_registry(root_rows, body_tensor, semantic_mass, docs_gate)
    commissure_payload = build_commissures(registry_payload)
    weight_payload = compute_route_weights(registry_payload, commissure_payload, route_quality)
    tunnel_payload = build_tunnels(registry_payload)
    dashboard_payload = build_dashboard(
        registry_payload, commissure_payload, weight_payload, tunnel_payload
    )

    write_json(REGISTRY_JSON_PATH, registry_payload)
    write_json(COMMISSURE_JSON_PATH, commissure_payload)
    write_json(WEIGHT_JSON_PATH, weight_payload)
    write_json(TUNNEL_JSON_PATH, tunnel_payload)
    write_json(DASHBOARD_JSON_PATH, dashboard_payload)

    write_json(REGISTRY_JSON_MIRROR, registry_payload)
    write_json(COMMISSURE_JSON_MIRROR, commissure_payload)
    write_json(WEIGHT_JSON_MIRROR, weight_payload)
    write_json(TUNNEL_JSON_MIRROR, tunnel_payload)
    write_json(DASHBOARD_JSON_MIRROR, dashboard_payload)

    write_text(REGISTRY_MD_PATH, render_registry_markdown(registry_payload))
    write_text(COMMISSURE_MD_PATH, render_commissure_markdown(commissure_payload, weight_payload))
    write_text(WEIGHT_MD_PATH, render_weight_markdown(weight_payload))
    write_text(TUNNEL_MD_PATH, render_tunnel_markdown(tunnel_payload))
    write_text(DASHBOARD_MD_PATH, render_dashboard_markdown(dashboard_payload, registry_payload))
    write_text(
        RUNTIME_MD_PATH,
        render_runtime_markdown(registry_payload, dashboard_payload, weight_payload),
    )
    write_text(RECEIPT_MD_PATH, render_receipt_markdown(dashboard_payload))

    print(f"Wrote {REGISTRY_JSON_PATH}")
    print(f"Wrote {COMMISSURE_JSON_PATH}")
    print(f"Wrote {WEIGHT_JSON_PATH}")
    print(f"Wrote {TUNNEL_JSON_PATH}")
    print(f"Wrote {DASHBOARD_JSON_PATH}")
    print(f"Wrote {REGISTRY_MD_PATH}")
    print(f"Wrote {COMMISSURE_MD_PATH}")
    print(f"Wrote {WEIGHT_MD_PATH}")
    print(f"Wrote {TUNNEL_MD_PATH}")
    print(f"Wrote {DASHBOARD_MD_PATH}")
    print(f"Wrote {RUNTIME_MD_PATH}")
    print(f"Wrote {RECEIPT_MD_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
