from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"
MYCELIUM_BRAIN_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
DEEP_ROOT = (
    MYCELIUM_BRAIN_ROOT
    / "dynamic_neural_network"
    / "14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK"
)
HEMISPHERE_ROOT = MYCELIUM_BRAIN_ROOT / "nervous_system" / "hemispheres"

ARTIFACT_DATE = "2026-03-13"
DERIVATION_VERSION = "2026-03-13.total-holographic-snapshot-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.compile_total_holographic_snapshot"

DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
TRANSFER_HUBS_PATH = NERVOUS_SYSTEM_ROOT / "20_METRO" / "03_TRANSFER_HUBS.md"
DUAL_HEMISPHERE_CROSSWALK_PATH = HEMISPHERE_ROOT / "12_dual_hemisphere_crosswalk_map.md"
CROSS_HEMISPHERE_ENTRYPOINT_PATH = HEMISPHERE_ROOT / "18_cross_hemisphere_entrypoint_atlas.md"
GRAND_CENTRAL_REGISTRY_PATH = SELF_ACTUALIZE_ROOT / "grand_central_station_registry.json"
GRAND_CENTRAL_WEIGHTS_PATH = SELF_ACTUALIZE_ROOT / "grand_central_weight_exchange.json"
GRAND_CENTRAL_TUNNELS_PATH = SELF_ACTUALIZE_ROOT / "grand_central_zpoint_tunnels.json"
AP6D_DASHBOARD_PATH = SELF_ACTUALIZE_ROOT / "ap6d_integration_dashboard.json"
SEAT_REGISTRY_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_AWAKENING_AGENT_SEAT_REGISTRY.json"
)
SEAT_BRIDGES_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_SEAT_BRIDGE_RECORDS.json"
TRANSITION_PACKETS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "AP6D_TRANSITION_PACKETS.json"
NEXUS_TUNNELS_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_NEXUS_TUNNELS.json"
DIMENSION_BRIDGES_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_DIMENSION_BRIDGES.json"
)
SEAT_ROUTE_MAP_PATH = (
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ATHENA_PRIME_6D_SEAT_ROUTE_BRIDGE_MAP_4096.json"
)
AETHER_POINTS_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_aether_point_registry.json"
Z_POINT_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_z_point_registry.json"
LIMINAL_COORDINATES_PATH = SELF_ACTUALIZE_ROOT / "next57_liminal_coordinate_registry.json"
REPLAY_RECEIPTS_PATH = SELF_ACTUALIZE_ROOT / "phase4_replay_receipts.json"
METRO_SYSTEMS_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_metro_system_registry.json"
CROSSWALK_EDGES_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
LENS_PROFILES_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_lens_weight_profile_registry.json"
DEEP_NET_SUMMARY_PATH = SELF_ACTUALIZE_ROOT / "deep_integration_neural_net.json"

LEDGER_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "90_LEDGERS"
    / "42_TOTAL_HOLOGRAPHIC_SNAPSHOT_MASTER_NEXUS_MINDSWEEPER_2026-03-13.md"
)
HSIGMA_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "95_MANIFESTS"
    / "TOTAL_HOLOGRAPHIC_SNAPSHOT_HSIGMA_2026-03-13.json"
)
NEXUS_REGISTRY_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "95_MANIFESTS"
    / "TOTAL_HOLOGRAPHIC_NEXUS_REGISTRY_2026-03-13.json"
)
MATRIX_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "95_MANIFESTS"
    / "TOTAL_HOLOGRAPHIC_MINDSWEEPER_4096x256_2026-03-13.jsonl"
)
HIDDEN_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "95_MANIFESTS"
    / "TOTAL_HOLOGRAPHIC_HIDDEN_NEXUS_CANDIDATES_2026-03-13.json"
)
SEED_OUTPUT_PATH = (
    NERVOUS_SYSTEM_ROOT
    / "95_MANIFESTS"
    / "TOTAL_HOLOGRAPHIC_REGENERATION_SEED_2026-03-13.json"
)

HSIGMA_SYMBOL = "HΣ"
MASTER_SCORE_THRESHOLD = 0.70
MASTER_KEY_PERCENTILE = 0.95

FEATURE_FAMILY_DENOMINATOR = 10.0
SURFACE_WEIGHT = {
    "Cortex": ("structural", "wall", "address"),
    "RuntimeHub": ("generative", "floor", "runtime"),
    "Hall": ("generative", "wheel", "hall"),
    "Temple": ("structural", "wheel", "temple"),
    "DeepRoot": ("center", "wheel", "deep-root"),
    "Replay": ("center", "floor", "replay"),
    "Appendix": ("structural", "wall", "appendix"),
}
BRIDGE_ROLE_WEIGHT = {
    "ingress": 0.45,
    "compression": 0.65,
    "weave": 0.80,
    "seed_promotion": 1.00,
}
FEATURE_FAMILY_PLANE = {
    "basis": "wall",
    "matrix": "wall",
    "observer": "wheel",
    "metro": "wheel",
    "projection": "floor",
    "bridge": "floor",
    "feeder": "wheel",
    "surface": "mix",
    "dimension": "mix",
    "tunnel": "floor",
    "replay": "floor",
    "liminal": "wheel",
    "aether": "floor",
    "hub": "wheel",
    "anchor": "mix",
}
Q0_LABELS = {
    0: "GC0 center",
    1: "GCL structural hemisphere",
    2: "GCR generative hemisphere",
    3: "GCZ-Aether transit axis",
}
Q1_LABELS = {
    0: "TOG/SAME",
    1: "TOG/OPP",
    2: "SPLIT/SAME",
    3: "SPLIT/OPP",
}
Q2_LABELS = {
    0: "(IN,IN)",
    1: "(IN,ANTI)",
    2: "(ANTI,IN)",
    3: "(ANTI,ANTI)",
}
Q3_LABELS = {
    0: "WALL",
    1: "WHEEL",
    2: "FLOOR",
    3: "MIX",
}

SOURCE_PATHS = [
    DOCS_GATE_PATH,
    TRANSFER_HUBS_PATH,
    DUAL_HEMISPHERE_CROSSWALK_PATH,
    CROSS_HEMISPHERE_ENTRYPOINT_PATH,
    GRAND_CENTRAL_REGISTRY_PATH,
    GRAND_CENTRAL_WEIGHTS_PATH,
    GRAND_CENTRAL_TUNNELS_PATH,
    AP6D_DASHBOARD_PATH,
    SEAT_REGISTRY_PATH,
    SEAT_BRIDGES_PATH,
    TRANSITION_PACKETS_PATH,
    NEXUS_TUNNELS_PATH,
    DIMENSION_BRIDGES_PATH,
    SEAT_ROUTE_MAP_PATH,
    AETHER_POINTS_PATH,
    Z_POINT_PATH,
    LIMINAL_COORDINATES_PATH,
    REPLAY_RECEIPTS_PATH,
    METRO_SYSTEMS_PATH,
    CROSSWALK_EDGES_PATH,
    LENS_PROFILES_PATH,
    DEEP_NET_SUMMARY_PATH,
    DEEP_ROOT / "README.md",
    DEEP_ROOT / "00_CONTROL" / "04_ALGORITHMIC_PIPELINE.md",
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md",
    NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_relative(path: Path) -> str:
    return str(path.resolve().relative_to(WORKSPACE_ROOT)).replace("/", "\\")


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_div(num: float, den: float) -> float:
    if not den:
        return 0.0
    return num / den


def mean(values: Iterable[float]) -> float:
    items = list(values)
    if not items:
        return 0.0
    return sum(items) / len(items)


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    index = pct * (len(ordered) - 1)
    lower = int(math.floor(index))
    upper = int(math.ceil(index))
    if lower == upper:
        return ordered[lower]
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower())
    return cleaned.strip("-") or "item"


def parse_docs_gate() -> str:
    text = DOCS_GATE_PATH.read_text(encoding="utf-8")
    for line in text.splitlines():
        if "Command status:" in line:
            parts = line.split("`")
            if len(parts) >= 2:
                return parts[1]
    return "UNKNOWN"


def parse_markdown_table(markdown: str) -> list[dict[str, str]]:
    tables: list[list[str]] = []
    current: list[str] = []
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        if line.startswith("|"):
            current.append(line)
            continue
        if current:
            tables.append(current)
            current = []
    if current:
        tables.append(current)
    for table in tables:
        if len(table) < 2:
            continue
        headers = [header.strip() for header in table[0].strip("|").split("|")]
        rows: list[dict[str, str]] = []
        for line in table[2:]:
            values = [value.strip() for value in line.strip("|").split("|")]
            if len(values) != len(headers):
                continue
            rows.append(dict(zip(headers, values)))
        if rows:
            return rows
    return []


def parse_transfer_hubs(markdown: str) -> list[dict[str, Any]]:
    hubs: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    header_pattern = re.compile(r"^###\s+(T\d+)\s+-\s+(.*?)\s*$")
    bullet_pattern = re.compile(r"^- ([^:]+):\s*(.*)$")
    for raw_line in markdown.splitlines():
        line = raw_line.strip()
        header_match = header_pattern.match(line)
        if header_match:
            if current:
                hubs.append(current)
            current = {
                "hub_id": header_match.group(1),
                "canonical_name": header_match.group(2),
            }
            continue
        if not current:
            continue
        bullet_match = bullet_pattern.match(line)
        if bullet_match:
            key = bullet_match.group(1).strip().lower().replace(" ", "_")
            current[key] = bullet_match.group(2).strip()
    if current:
        hubs.append(current)
    for hub in hubs:
        hub["lines_served"] = re.findall(r"`([^`]+)`", hub.get("lines_served", ""))
        hub["status"] = hub.get("status", "live")
    return hubs


def decode_byte(byte_state: int) -> tuple[int, int, int, int]:
    q0 = byte_state % 4
    q1 = (byte_state // 4) % 4
    q2 = (byte_state // 16) % 4
    q3 = (byte_state // 64) % 4
    return q0, q1, q2, q3


def encode_byte(q0: int, q1: int, q2: int, q3: int) -> int:
    return q0 + (4 * q1) + (16 * q2) + (64 * q3)


def neighboring_bytes(byte_state: int) -> list[int]:
    q0, q1, q2, q3 = decode_byte(byte_state)
    neighbors: list[int] = []
    for index, value in enumerate((q0, q1, q2, q3)):
        for delta in (-1, 1):
            candidate = value + delta
            if not 0 <= candidate <= 3:
                continue
            coords = [q0, q1, q2, q3]
            coords[index] = candidate
            neighbors.append(encode_byte(coords[0], coords[1], coords[2], coords[3]))
    return neighbors


class TotalHolographicSnapshotCompiler:
    def __init__(self) -> None:
        self.docs_gate_status = parse_docs_gate()
        self.generated_at = utc_now()
        self.source_digests = self._build_source_digests()

    def _build_source_digests(self) -> list[dict[str, Any]]:
        digests: list[dict[str, Any]] = []
        for path in SOURCE_PATHS:
            if not path.exists():
                continue
            digests.append(
                {
                    "path": normalize_relative(path),
                    "sha256": file_sha256(path),
                    "size_bytes": path.stat().st_size,
                }
            )
        return digests

    def load_context(self) -> dict[str, Any]:
        return {
            "transfer_hubs": parse_transfer_hubs(TRANSFER_HUBS_PATH.read_text(encoding="utf-8")),
            "grand_central_registry": load_json(GRAND_CENTRAL_REGISTRY_PATH)["registry"],
            "grand_central_weights": load_json(GRAND_CENTRAL_WEIGHTS_PATH)["routes"],
            "grand_central_tunnels": load_json(GRAND_CENTRAL_TUNNELS_PATH)["tunnels"],
            "ap6d_dashboard": load_json(AP6D_DASHBOARD_PATH),
            "named_seats": load_json(SEAT_REGISTRY_PATH)["named_seats"],
            "seat_bridges": load_json(SEAT_BRIDGES_PATH)["bridges"],
            "transition_packets": load_json(TRANSITION_PACKETS_PATH)["packets"],
            "nexus_tunnels": load_json(NEXUS_TUNNELS_PATH)["records"],
            "dimension_bridges": load_json(DIMENSION_BRIDGES_PATH)["records"],
            "seat_route_rows": load_json(SEAT_ROUTE_MAP_PATH)["rows"],
            "aether_points": load_json(AETHER_POINTS_PATH)["aether_points"],
            "zpoints": load_json(Z_POINT_PATH)["zpoints"],
            "liminal_registry": load_json(LIMINAL_COORDINATES_PATH),
            "replay_receipts": load_json(REPLAY_RECEIPTS_PATH)["receipts"],
            "metro_systems": load_json(METRO_SYSTEMS_PATH)["systems"],
            "crosswalk_edges": load_json(CROSSWALK_EDGES_PATH)["edges"],
            "lens_profiles": load_json(LENS_PROFILES_PATH)["profiles"],
            "deep_net_summary": load_json(DEEP_NET_SUMMARY_PATH),
            "dual_hemisphere_crosswalk": parse_markdown_table(
                DUAL_HEMISPHERE_CROSSWALK_PATH.read_text(encoding="utf-8")
            ),
            "cross_hemisphere_entrypoints": parse_markdown_table(
                CROSS_HEMISPHERE_ENTRYPOINT_PATH.read_text(encoding="utf-8")
            ),
        }

    def build_explicit_registry(
        self, context: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
        registry_rows: list[dict[str, Any]] = []
        explicit_nodes: list[dict[str, Any]] = []
        node_index: dict[str, dict[str, Any]] = {}
        roots_by_name = {
            item["root_name"]: item["root_id"] for item in context["grand_central_registry"]
        }

        for hub in context["transfer_hubs"]:
            node_id = f"ST-{hub['hub_id']}"
            row = {
                "nexus_id": node_id,
                "canonical_name": hub["canonical_name"],
                "nexus_class": "transfer_hub",
                "host_layers": ["metro", "cortex", "grand-central"],
                "route_degree": max(1, len(hub.get("lines_served", []))),
                "dimensional_span": 2,
                "zero_aether_polarity": "centered",
                "master_weight": round(clamp(0.55 + (0.03 * len(hub.get("lines_served", [])))), 3),
                "recurrence": 1.0,
                "related_hubs": ["ST-T10"] if node_id != "ST-T10" else ["A01", "A02", "A16"],
                "touching_tunnels": ["ZT-001", "ZT-002"] if node_id in {"ST-T10", "ST-T4"} else [],
                "timing_states": self._timing_template_for_node("transfer_hub", hub.get("status", "live")),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(TRANSFER_HUBS_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[node_id] = row

        for root in context["grand_central_registry"]:
            polarity = "centered"
            if root["root_id"] == "A15":
                polarity = "zero-bearing"
            elif root["root_id"] == "A12":
                polarity = "aether-bearing"
            row = {
                "nexus_id": root["root_id"],
                "canonical_name": root["root_name"],
                "nexus_class": "grand_central_root",
                "host_layers": ["grand-central", "cortex", root["tract"]],
                "route_degree": 1 + sum(
                    1
                    for route in context["grand_central_weights"]
                    if route["source_family"] == root["root_name"]
                    or route["target_family"] == root["root_name"]
                ),
                "dimensional_span": 2 if root["hemisphere"] != "bilateral" else 3,
                "zero_aether_polarity": polarity,
                "master_weight": round(clamp(0.58 + (0.05 * safe_div(root["authority_rank"], 5.0))), 3),
                "recurrence": 1.0,
                "related_hubs": [
                    route["target_family"]
                    for route in context["grand_central_weights"]
                    if route["source_family"] == root["root_name"]
                ][:6],
                "touching_tunnels": [
                    tunnel["tunnel_id"]
                    for tunnel in context["grand_central_tunnels"]
                    if root["root_name"] in tunnel["entry_route"] or root["root_name"] in tunnel["resume_target"]
                ],
                "timing_states": self._timing_template_for_node(root["hemisphere"], root["tract"]),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(GRAND_CENTRAL_REGISTRY_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        for seat in context["named_seats"]:
            row = {
                "nexus_id": seat["seat_id"],
                "canonical_name": seat["seat_name"],
                "nexus_class": "named_seat",
                "host_layers": ["ap6d", seat["seat_stratum"].lower(), seat["branch"].lower()],
                "route_degree": max(1, len(seat.get("route_targets", [])) + len(seat.get("shadow_feeders", []))),
                "dimensional_span": 4 if "Prime" in seat["seat_id"] else 3,
                "zero_aether_polarity": "liminal-bearing" if seat["seat_stratum"] in {"Feeder", "SeatField"} else "centered",
                "master_weight": round(
                    clamp(
                        0.60
                        + (0.05 * safe_div(seat.get("depth", 0), 6.0))
                        + (0.02 * len(seat.get("fabric_zone_path", [])))
                        + (0.02 if seat.get("activation_state") == "CURRENT" else 0.0)
                    ),
                    3,
                ),
                "recurrence": 1.0,
                "related_hubs": [roots_by_name.get(binding, binding) for binding in seat.get("corpus_bindings", [])[:6]],
                "touching_tunnels": [],
                "timing_states": self._timing_template_for_node("generative", seat["seat_stratum"]),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(SEAT_REGISTRY_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        for zpoint in context["zpoints"]:
            row = {
                "nexus_id": zpoint["zpoint_id"],
                "canonical_name": zpoint["label"],
                "nexus_class": "zero_anchor",
                "host_layers": ["zero", "tunnel", "replay"],
                "route_degree": len(zpoint.get("binding_hubs", [])),
                "dimensional_span": 2,
                "zero_aether_polarity": "zero-bearing",
                "master_weight": round(clamp(0.68 + (0.02 * len(zpoint.get("binding_hubs", [])))), 3),
                "recurrence": 1.0,
                "related_hubs": list(zpoint.get("binding_hubs", [])),
                "touching_tunnels": [
                    tunnel["tunnel_id"]
                    for tunnel in context["grand_central_tunnels"]
                    if tunnel["tunnel_class"].startswith(zpoint["zpoint_id"])
                ],
                "timing_states": self._timing_template_for_node("transit", "zero"),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(Z_POINT_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        root_lookup_pairs = sorted(roots_by_name.items(), key=lambda item: len(item[0]), reverse=True)
        for tunnel in context["grand_central_tunnels"]:
            related_hubs: list[str] = []
            route_text = f"{tunnel.get('entry_route', '')} {tunnel.get('resume_target', '')}"
            for root_name, root_id in root_lookup_pairs:
                if root_name and root_name in route_text and root_id not in related_hubs:
                    related_hubs.append(root_id)
            if "GCZ" in route_text and "Z1" not in related_hubs:
                related_hubs.append("Z1")
            if tunnel["tunnel_id"] == "ZT-006" and "Z5" not in related_hubs:
                related_hubs.append("Z5")
            row = {
                "nexus_id": tunnel["tunnel_id"],
                "canonical_name": tunnel["tunnel_class"],
                "nexus_class": "tunnel_anchor",
                "host_layers": ["tunnel", "grand-central", "zero"],
                "route_degree": max(2, len(related_hubs)),
                "dimensional_span": 3 if tunnel["tunnel_id"] in {"ZT-005", "ZT-006"} else 2,
                "zero_aether_polarity": "aether-bearing" if tunnel["tunnel_id"] == "ZT-006" else "zero-bearing",
                "master_weight": 0.73 if tunnel.get("proof_state") == "OK" else 0.71,
                "recurrence": 1.0,
                "related_hubs": related_hubs[:6] or ["ST-T10"],
                "touching_tunnels": [tunnel["tunnel_id"]],
                "timing_states": self._timing_template_for_node("transit", "tunnel"),
                "hidden_neighbors": [],
                "status_class": "seated" if tunnel.get("proof_state") in {"OK", "NEAR"} else "frontier",
                "source_paths": [normalize_relative(GRAND_CENTRAL_TUNNELS_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        liminal_registry = context["liminal_registry"]
        for stamp in liminal_registry.get("loop_coordinate_stamps", []):
            row = {
                "nexus_id": f"LIM-{stamp['loop_id']}",
                "canonical_name": stamp["loop_id"],
                "nexus_class": "liminal_loop",
                "host_layers": ["liminal", "loop", "governance"],
                "route_degree": 3,
                "dimensional_span": 2,
                "zero_aether_polarity": "liminal-bearing",
                "master_weight": 0.66,
                "recurrence": 1.0,
                "related_hubs": ["ST-T10", "A02"],
                "touching_tunnels": ["ZT-002"],
                "timing_states": self._timing_template_for_node("center", "liminal"),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(LIMINAL_COORDINATES_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        for agent in liminal_registry.get("master_agents", []):
            coordinate_tuple = agent.get("coordinate_tuple", {})
            anchor_hub = coordinate_tuple.get("Xs", "A02")
            role_name = agent.get("agent_id", "MASTER-AGENT").split(".")[-1]
            row = {
                "nexus_id": f"LIM-{agent['agent_id']}",
                "canonical_name": role_name,
                "nexus_class": "liminal_master_agent",
                "host_layers": ["liminal", "master-agent", "governance"],
                "route_degree": 2,
                "dimensional_span": 2,
                "zero_aether_polarity": "liminal-bearing",
                "master_weight": 0.69,
                "recurrence": 1.0,
                "related_hubs": [anchor_hub, "ST-T10"],
                "touching_tunnels": [],
                "timing_states": self._timing_template_for_node("center", "master-agent"),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(LIMINAL_COORDINATES_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        top_aether_points = sorted(
            context["aether_points"],
            key=lambda item: (item["aether_density"], item["repair_gain"], -item["tunnel_cost"]),
            reverse=True,
        )[:16]
        for point in top_aether_points:
            row = {
                "nexus_id": point["point_id"],
                "canonical_name": point["point_id"],
                "nexus_class": "aether_anchor",
                "host_layers": ["aether", "field", point["system_id"]],
                "route_degree": 3,
                "dimensional_span": 3,
                "zero_aether_polarity": "aether-bearing",
                "master_weight": round(clamp(0.55 + point["aether_density"] * 0.35), 3),
                "recurrence": 1.0,
                "related_hubs": [point["source_record_id"], point["system_id"]],
                "touching_tunnels": [],
                "timing_states": self._timing_template_for_node("transit", "aether"),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(AETHER_POINTS_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        for receipt in context["replay_receipts"][:12]:
            row = {
                "nexus_id": receipt["action_id"],
                "canonical_name": receipt["action_id"],
                "nexus_class": "replay_anchor",
                "host_layers": ["replay", "receipt", "verification"],
                "route_degree": len(receipt.get("writeback_paths", [])),
                "dimensional_span": 2,
                "zero_aether_polarity": "centered",
                "master_weight": 0.61,
                "recurrence": 1.0,
                "related_hubs": ["A02", "ST-T10"],
                "touching_tunnels": ["ZT-002"] if receipt["action_id"] == "RR-0001" else [],
                "timing_states": self._timing_template_for_node("center", "replay"),
                "hidden_neighbors": [],
                "status_class": "seated",
                "source_paths": [normalize_relative(REPLAY_RECEIPTS_PATH)],
            }
            registry_rows.append(row)
            explicit_nodes.append(row)
            node_index[row["nexus_id"]] = row

        return registry_rows, explicit_nodes, node_index

    def _timing_template_for_node(self, hemisphere: str, subtype: str) -> list[int]:
        preferred_q0 = 0
        if hemisphere in {"left", "structural"}:
            preferred_q0 = 1
        elif hemisphere in {"right", "generative"}:
            preferred_q0 = 2
        elif hemisphere in {"transit", "bilateral"}:
            preferred_q0 = 3
        preferred_q3 = 1
        if subtype in {"address", "zero"}:
            preferred_q3 = 0
        elif subtype in {"replay", "aether"}:
            preferred_q3 = 2
        elif subtype in {"master-agent", "liminal"}:
            preferred_q3 = 3
        scored: list[tuple[float, int]] = []
        for byte_state in range(256):
            q0, q1, q2, q3 = decode_byte(byte_state)
            score = 1.0
            if q0 == preferred_q0:
                score += 1.0
            if q3 == preferred_q3:
                score += 0.7
            if subtype == "transfer_hub" and q1 in {0, 2}:
                score += 0.2
            if subtype in {"aether", "replay"} and q2 in {1, 3}:
                score += 0.3
            if subtype in {"zero", "address"} and q2 in {0, 1}:
                score += 0.3
            scored.append((score, byte_state))
        scored.sort(reverse=True)
        return [item[1] for item in scored[:8]]

    def build_explicit_edges(
        self, context: dict[str, Any], node_index: dict[str, dict[str, Any]]
    ) -> list[dict[str, Any]]:
        edges: list[dict[str, Any]] = []
        root_name_to_id = {node["canonical_name"]: node["nexus_id"] for node in node_index.values()}

        for route in context["grand_central_weights"]:
            source_id = root_name_to_id.get(route["source_family"], route["source_family"])
            target_id = root_name_to_id.get(route["target_family"], route["target_family"])
            edges.append(
                {
                    "edge_id": route["commissure_id"],
                    "source_id": source_id,
                    "target_id": target_id,
                    "edge_kind": "commissure",
                    "weight": route["dispatch_score"],
                    "proof_state": route["proof_state"],
                    "route_family": "grand-central",
                    "source_paths": [normalize_relative(GRAND_CENTRAL_WEIGHTS_PATH)],
                }
            )

        for bridge in context["seat_bridges"]:
            edges.append(
                {
                    "edge_id": bridge["bridge_id"],
                    "source_id": bridge["source_seat"],
                    "target_id": bridge["target_seat"],
                    "edge_kind": bridge["bridge_kind"],
                    "weight": 1.0 if bridge["proof_state"] == "OK" else 0.65,
                    "proof_state": bridge["proof_state"],
                    "route_family": "seat-bridge",
                    "source_paths": [normalize_relative(SEAT_BRIDGES_PATH)],
                }
            )

        for edge in context["crosswalk_edges"]:
            edges.append(
                {
                    "edge_id": edge["edge_id"],
                    "source_id": edge["source_id"],
                    "target_id": edge["target_id"],
                    "edge_kind": edge["edge_kind"],
                    "weight": edge["weight"],
                    "proof_state": "OK",
                    "route_family": "inter-metro",
                    "source_paths": [normalize_relative(CROSSWALK_EDGES_PATH)],
                }
            )

        for zpoint in context["zpoints"]:
            for binding_hub in zpoint.get("binding_hubs", []):
                edges.append(
                    {
                        "edge_id": f"{zpoint['zpoint_id']}->{binding_hub}",
                        "source_id": zpoint["zpoint_id"],
                        "target_id": binding_hub,
                        "edge_kind": "zpoint-binding",
                        "weight": 0.75 if zpoint["proof_state"] == "OK" else 0.55,
                        "proof_state": zpoint["proof_state"],
                        "route_family": "zero",
                        "source_paths": [normalize_relative(Z_POINT_PATH)],
                    }
                )

        for point in sorted(context["aether_points"], key=lambda item: item["aether_density"], reverse=True)[:64]:
            edges.append(
                {
                    "edge_id": f"{point['point_id']}->{point['source_record_id']}",
                    "source_id": point["point_id"],
                    "target_id": point["source_record_id"],
                    "edge_kind": "aether-binding",
                    "weight": point["aether_density"],
                    "proof_state": "OK",
                    "route_family": "aether",
                    "source_paths": [normalize_relative(AETHER_POINTS_PATH)],
                }
            )

        return edges

    def build_raw_rows(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        tunnel_by_nexus = {item["nexus_id"]: item for item in context["nexus_tunnels"]}
        bridge_by_addr: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in context["dimension_bridges"]:
            bridge_by_addr[record["prime_addr_6d"]].append(record)

        dual_crosswalk_rows = context["dual_hemisphere_crosswalk"]
        crosswalk_scores = [float(item.get("Bridge", "0") or 0) for item in dual_crosswalk_rows]
        global_crosswalk_mean = mean(crosswalk_scores)

        raw_rows: list[dict[str, Any]] = []
        for row in context["seat_route_rows"]:
            tunnel_record = tunnel_by_nexus.get(row["nexus_id"], {})
            bridge_records = bridge_by_addr.get(row["prime_addr_6d"], [])
            features = self._build_feature_pack(row, tunnel_record, bridge_records, global_crosswalk_mean)
            static_scores = self._compute_static_scores(row, tunnel_record, bridge_records, features)
            raw_rows.append(
                {
                    "nexus_id": row["nexus_id"],
                    "prime_addr_6d": row["prime_addr_6d"],
                    "seat_id": row["seat_id"],
                    "basis_doc_id": row["basis_doc_id"],
                    "matrix_cell_id": row["matrix_cell_id"],
                    "observer_pass_id": row["observer_pass_id"],
                    "witness_state_id": row["witness_state_id"],
                    "metro_level": row["metro_level"],
                    "projection_3d_id": row["projection_3d_id"],
                    "bridge_ids": list(row.get("bridge_ids", [])),
                    "activation_wave": row["activation_wave"],
                    "feeder_front": row["feeder_front"],
                    "source_witness": row["source_witness"],
                    "truth": row["truth"],
                    "connected_dims": list(tunnel_record.get("connected_dims", [])),
                    "connected_surfaces": list(tunnel_record.get("connected_surfaces", [])),
                    "tunnel_class": tunnel_record.get("tunnel_class", "UNKNOWN"),
                    "restart_seed": tunnel_record.get("restart_seed", ""),
                    "bridge_records": bridge_records,
                    "features": features,
                    "static_scores": static_scores,
                    "host_layers": sorted({feature["layer"] for feature in features if feature["layer"]}),
                    "related_hubs": self._related_hubs_for_row(row, tunnel_record),
                }
            )
        return raw_rows

    def _build_feature_pack(
        self,
        row: dict[str, Any],
        tunnel_record: dict[str, Any],
        bridge_records: list[dict[str, Any]],
        global_crosswalk_mean: float,
    ) -> list[dict[str, Any]]:
        features: list[dict[str, Any]] = []

        def add_feature(
            node_id: str,
            node_class: str,
            route_family: str,
            hemisphere: str,
            polarity: str,
            plane: str,
            layer: str,
            dimensions: Iterable[str],
            replay: float = 0.0,
            compression: float = 0.0,
        ) -> None:
            features.append(
                {
                    "node_id": node_id,
                    "node_class": node_class,
                    "route_family": route_family,
                    "hemisphere": hemisphere,
                    "polarity": polarity,
                    "plane": plane,
                    "layer": layer,
                    "dimensions": list(dimensions),
                    "replay": replay,
                    "compression": compression,
                }
            )

        add_feature(row["basis_doc_id"], "basis_doc", "basis", "structural", "neutral", "wall", "basis", ["4D"], 0.0, 1.0)
        add_feature(row["matrix_cell_id"], "matrix_cell", "matrix", "structural", "neutral", "wall", "matrix", ["4D"], 0.0, 0.9)
        observer_hemisphere = "generative"
        observer_name = row["observer_pass_id"].upper()
        if "EARTH" in observer_name or "AIR" in observer_name:
            observer_hemisphere = "structural"
        add_feature(
            row["observer_pass_id"],
            "observer_pass",
            "observer",
            observer_hemisphere,
            "neutral",
            "wheel",
            "observer",
            ["4D", "5D"],
            0.1,
            0.3,
        )
        add_feature(
            row["metro_level"],
            "metro_level",
            "metro",
            "center",
            "neutral",
            "wheel",
            "metro",
            ["4D", "5D", "6D"],
            0.2,
            0.2,
        )
        add_feature(
            row["projection_3d_id"],
            "projection",
            "projection",
            "center",
            "inward",
            "floor",
            "projection",
            ["3D", "4D"],
            0.1,
            0.4,
        )

        feeder_front = row["feeder_front"]
        feeder_hemisphere = "center"
        if feeder_front in {"Q42", "Q46"}:
            feeder_hemisphere = "generative"
        elif feeder_front == "TQ04":
            feeder_hemisphere = "structural"
        elif feeder_front == "Q02":
            feeder_hemisphere = "transit"
        add_feature(
            feeder_front,
            "feeder_front",
            "feeder",
            feeder_hemisphere,
            "neutral",
            "wheel",
            "feeder",
            ["5D", "6D"],
            0.3,
            0.2,
        )

        connected_surfaces = list(tunnel_record.get("connected_surfaces", []))
        for surface in connected_surfaces:
            hemisphere, plane, layer = SURFACE_WEIGHT.get(surface, ("center", "mix", "surface"))
            add_feature(
                surface,
                "surface",
                "surface",
                hemisphere,
                "neutral",
                plane,
                layer,
                tunnel_record.get("connected_dims", []),
                0.2 if surface in {"Replay", "RuntimeHub"} else 0.0,
                0.2 if surface in {"Cortex", "DeepRoot"} else 0.0,
            )

        dims = list(tunnel_record.get("connected_dims", []))
        for dim in dims:
            add_feature(
                dim,
                "dimension",
                "dimension",
                "transit",
                "neutral",
                "mix",
                "dimension",
                [dim],
                0.0,
                0.1 if dim in {"5D", "6D", "7D"} else 0.0,
            )

        tunnel_class = tunnel_record.get("tunnel_class", "UNKNOWN")
        add_feature(
            tunnel_class,
            "tunnel",
            "tunnel",
            "transit",
            "inward",
            "floor",
            "tunnel",
            dims or ["4D"],
            0.4,
            0.2,
        )

        for bridge in bridge_records:
            role = bridge["bridge_role"]
            polarity = "inward" if role in {"ingress", "compression"} else "outward"
            add_feature(
                bridge["bridge_id"],
                "dimension_bridge",
                "bridge",
                "transit",
                polarity,
                "floor",
                "bridge",
                [bridge["from_dim"], bridge["to_dim"]],
                0.3 if role == "seed_promotion" else 0.1,
                0.5 if role in {"compression", "weave"} else 0.2,
            )

        add_feature("ANCHOR-GC0", "anchor", "anchor", "center", "neutral", "mix", "anchor", ["4D", "5D", "6D"], 0.2, 0.2)
        add_feature("ANCHOR-GCL", "anchor", "anchor", "structural", "neutral", "wall", "anchor", ["4D", "5D"], 0.0, 0.4)
        add_feature("ANCHOR-GCR", "anchor", "anchor", "generative", "neutral", "wheel", "anchor", ["4D", "5D", "6D"], 0.2, 0.1)
        add_feature("ANCHOR-GCZ", "anchor", "anchor", "transit", "inward", "floor", "anchor", dims or ["4D"], 0.4, 0.2)

        if any(bridge["bridge_role"] == "seed_promotion" for bridge in bridge_records):
            add_feature("AETHER-FIELD", "aether_field", "aether", "transit", "outward", "floor", "aether", ["6D", "7D"], 0.3, 0.4)
        if feeder_front in {"Q42", "TQ04", "TQ06", "Q02", "Q46"} or {"Hall", "Temple"} & set(connected_surfaces):
            add_feature("LIMINAL-FIELD", "liminal_field", "liminal", "center", "neutral", "wheel", "liminal", ["5D", "6D"], 0.2, 0.2)
        add_feature("REPLAY-FIELD", "replay_field", "replay", "center", "inward", "floor", "replay", ["4D", "5D", "6D"], 0.9, 0.1)

        if global_crosswalk_mean:
            add_feature(
                "HEMISPHERE-COMMISSURE",
                "hemisphere_commissure",
                "hub",
                "center",
                "neutral",
                "wheel",
                "commissure",
                ["4D", "5D", "6D"],
                0.2,
                clamp(global_crosswalk_mean),
            )

        return features

    def _compute_static_scores(
        self,
        row: dict[str, Any],
        tunnel_record: dict[str, Any],
        bridge_records: list[dict[str, Any]],
        features: list[dict[str, Any]],
    ) -> dict[str, float]:
        route_family_span = safe_div(
            len({feature["route_family"] for feature in features}),
            FEATURE_FAMILY_DENOMINATOR,
        )
        dimension_span = safe_div(len(set(tunnel_record.get("connected_dims", []))), 5.0)
        witness_refs = {
            normalize_relative(SEAT_ROUTE_MAP_PATH),
            normalize_relative(NEXUS_TUNNELS_PATH),
            normalize_relative(DIMENSION_BRIDGES_PATH),
        }
        if row.get("source_witness"):
            witness_refs.add(str(row["source_witness"]))
        source_recurrence = clamp(safe_div(len(witness_refs), 6.0))
        bridge_strength = mean(
            BRIDGE_ROLE_WEIGHT.get(item["bridge_role"], 0.4) for item in bridge_records
        )
        if not bridge_records:
            bridge_strength = 0.35
        replay_witness_role = clamp(
            0.35
            + (0.20 if row["truth"] == "OK" else 0.05)
            + (0.20 if tunnel_record.get("restart_seed") else 0.0)
            + (0.10 if any(feature["route_family"] == "replay" for feature in features) else 0.0)
        )
        zero_signal = 0.80 if tunnel_record.get("tunnel_class", "").startswith("4D_NATIVE") else 0.45
        aether_signal = 0.85 if any(item["bridge_role"] == "seed_promotion" for item in bridge_records) else 0.35
        liminal_signal = 0.75 if row["feeder_front"] in {"Q42", "TQ04", "TQ06", "Q02", "Q46"} else 0.30
        polarity = clamp((zero_signal + aether_signal + liminal_signal) / 3.0)
        master_weight = clamp(
            (0.25 * route_family_span)
            + (0.20 * dimension_span)
            + (0.20 * source_recurrence)
            + (0.15 * bridge_strength)
            + (0.10 * replay_witness_role)
            + (0.10 * polarity)
        )
        centrality = clamp((route_family_span * 0.5) + (dimension_span * 0.25) + (bridge_strength * 0.25))
        return {
            "route_family_span": round(route_family_span, 6),
            "dimension_span": round(dimension_span, 6),
            "source_recurrence": round(source_recurrence, 6),
            "dispatch_or_bridge_strength": round(bridge_strength, 6),
            "replay_witness_role": round(replay_witness_role, 6),
            "z_aether_liminal_polarity": round(polarity, 6),
            "master_weight": round(master_weight, 6),
            "centrality": round(centrality, 6),
        }

    def _related_hubs_for_row(self, row: dict[str, Any], tunnel_record: dict[str, Any]) -> list[str]:
        hubs = {"ST-T10"}
        feeder = row.get("feeder_front")
        if feeder:
            hubs.add(feeder)
        for surface in tunnel_record.get("connected_surfaces", []):
            if surface == "Cortex":
                hubs.add("A01")
            elif surface == "RuntimeHub":
                hubs.add("A02")
            elif surface == "Hall":
                hubs.add("LIM-L01")
            elif surface == "Temple":
                hubs.add("LIM-L02")
        return sorted(hubs)

    def cell_metrics(self, row: dict[str, Any], byte_state: int) -> dict[str, Any]:
        q0, q1, q2, q3 = decode_byte(byte_state)
        anchor_mode = {0: "center", 1: "structural", 2: "generative", 3: "transit"}[q0]
        plane_mode = {0: "wall", 1: "wheel", 2: "floor", 3: "mix"}[q3]
        inward_allowance = {0: 1.0, 1: 0.9, 2: 0.45, 3: 0.2}[q2]
        outward_allowance = {0: 0.2, 1: 0.65, 2: 0.9, 3: 1.0}[q2]
        relation_bonus = {0: (0.10, 0.00), 1: (0.04, 0.12), 2: (0.02, 0.18), 3: (-0.02, 0.22)}[q1]
        coherence_bonus, novelty_bonus = relation_bonus

        visible_features: list[dict[str, Any]] = []
        route_families: set[str] = set()
        visible_dims: set[str] = set()
        dominant_layers: Counter[str] = Counter()
        tunnel_count = 0
        replay_hits = 0.0
        compression_hits = 0.0
        contradiction_cost = 0.0

        for feature in row["features"]:
            plane_weight = 1.0 if plane_mode == "mix" or feature["plane"] in {plane_mode, "mix"} else 0.0
            if not plane_weight:
                continue
            hemisphere_weight = 1.0
            if anchor_mode == "structural" and feature["hemisphere"] == "generative":
                hemisphere_weight = 0.45
            elif anchor_mode == "generative" and feature["hemisphere"] == "structural":
                hemisphere_weight = 0.45
            elif anchor_mode == "transit" and feature["hemisphere"] not in {"transit", "center"}:
                hemisphere_weight = 0.5
            polarity_weight = 1.0
            if feature["polarity"] == "inward":
                polarity_weight = inward_allowance
            elif feature["polarity"] == "outward":
                polarity_weight = outward_allowance
            visibility = plane_weight * hemisphere_weight * polarity_weight
            if visibility < 0.40:
                continue
            visible_features.append(feature)
            route_families.add(feature["route_family"])
            visible_dims.update(feature["dimensions"])
            dominant_layers[feature["layer"]] += 1
            if feature["route_family"] == "tunnel":
                tunnel_count += 1
            replay_hits += feature["replay"] * visibility
            compression_hits += feature["compression"] * visibility

        visible_node_count = 1 + len(visible_features)
        route_density = safe_div(len(route_families), max(1, len(visible_features)))
        dimensional_span = safe_div(len(visible_dims), 5.0)
        reachability = clamp(safe_div(visible_node_count, 18.0) + (0.10 * route_density))
        tunnel_gain = clamp(safe_div(tunnel_count, 6.0) + (0.15 if anchor_mode == "transit" else 0.0))
        compression_value = clamp(safe_div(compression_hits, 4.0) + (0.10 if plane_mode == "wall" else 0.0))
        replay_value = clamp(safe_div(replay_hits, 3.0) + (0.10 if plane_mode == "floor" else 0.0))
        novel_exposure = clamp(safe_div(len(route_families), 10.0) + novelty_bonus)

        if row["truth"] != "OK":
            contradiction_cost += 0.15
        if row["feeder_front"] == "Q02" and outward_allowance > 0.6:
            contradiction_cost += 0.20
        if plane_mode == "floor" and replay_hits <= 0.15:
            contradiction_cost += 0.15
        if anchor_mode == "transit" and not any(feature["route_family"] in {"bridge", "tunnel"} for feature in visible_features):
            contradiction_cost += 0.10
        contradiction_cost = clamp(contradiction_cost)

        weight = clamp(
            (0.20 * row["static_scores"]["centrality"])
            + (0.20 * reachability)
            + (0.15 * tunnel_gain)
            + (0.15 * dimensional_span)
            + (0.10 * compression_value)
            + (0.10 * replay_value)
            + (0.10 * novel_exposure)
            - (0.10 * contradiction_cost)
            + coherence_bonus
        )

        missing_signatures: list[str] = []
        if len(route_families) >= 3 and "hub" not in route_families:
            missing_signatures.append("latent_transfer_station")
        if row["feeder_front"] in {"Q42", "TQ04", "TQ06"} and "liminal" not in route_families:
            missing_signatures.append("latent_liminal_gate")
        if any(bridge["bridge_role"] == "seed_promotion" for bridge in row["bridge_records"]) and "aether" not in route_families:
            missing_signatures.append("latent_aether_return")
        if row["tunnel_class"].startswith("4D_NATIVE") and "anchor" not in route_families:
            missing_signatures.append("latent_zero_repair_junction")
        if plane_mode == "floor" and replay_hits < 0.20:
            missing_signatures.append("latent_replay_closure")

        frontier_status = "stable"
        if row["feeder_front"] == "Q02":
            frontier_status = "docs-gate-blocked"
        elif missing_signatures:
            frontier_status = "latent-gap"

        contradiction_class = "none"
        if contradiction_cost >= 0.35:
            contradiction_class = "high"
        elif contradiction_cost >= 0.15:
            contradiction_class = "medium"

        return {
            "byte_state": byte_state,
            "q0": q0,
            "q1": q1,
            "q2": q2,
            "q3": q3,
            "weight": round(weight, 6),
            "visible_node_count": visible_node_count,
            "route_density": round(route_density, 6),
            "route_family_count": len(route_families),
            "tunnel_count": tunnel_count,
            "dimension_span": round(dimensional_span, 6),
            "reachability": round(reachability, 6),
            "tunnel_gain": round(tunnel_gain, 6),
            "compression_value": round(compression_value, 6),
            "replay_value": round(replay_value, 6),
            "novel_exposure": round(novel_exposure, 6),
            "contradiction_cost": round(contradiction_cost, 6),
            "contradiction_class": contradiction_class,
            "frontier_status": frontier_status,
            "missing_signatures": missing_signatures,
            "dominant_layers": [item[0] for item in dominant_layers.most_common(4)],
        }

    def compile(self) -> dict[str, Any]:
        context = self.load_context()
        explicit_registry_rows, explicit_nodes, node_index = self.build_explicit_registry(context)
        explicit_edges = self.build_explicit_edges(context, node_index)
        raw_rows = self.build_raw_rows(context)

        weight_samples: list[float] = []
        for row in raw_rows:
            for byte_state in range(256):
                weight_samples.append(self.cell_metrics(row, byte_state)["weight"])

        master_key_threshold = percentile(weight_samples, MASTER_KEY_PERCENTILE)
        median_weight = percentile(weight_samples, 0.50)

        class_counts: Counter[str] = Counter()
        byte_summary: dict[int, dict[str, Any]] = {
            byte_state: {
                "weight_total": 0.0,
                "visible_total": 0,
                "route_density_total": 0.0,
                "tunnel_total": 0,
                "master_key_count": 0,
                "hidden_pressure_count": 0,
                "contradictory_count": 0,
                "row_count": 0,
            }
            for byte_state in range(256)
        }

        hidden_candidates: dict[str, dict[str, Any]] = {}
        raw_master_rows: list[dict[str, Any]] = []

        with MATRIX_OUTPUT_PATH.open("w", encoding="utf-8") as matrix_handle:
            for row in raw_rows:
                row_cells = [self.cell_metrics(row, byte_state) for byte_state in range(256)]
                weight_by_state = {item["byte_state"]: item["weight"] for item in row_cells}
                signature_map: dict[str, list[dict[str, Any]]] = defaultdict(list)
                top_state_weights: list[tuple[float, int]] = []
                hidden_neighbors_for_row: set[str] = set()
                for cell in row_cells:
                    neighbors = neighboring_bytes(cell["byte_state"])
                    neighbor_weights = [weight_by_state[neighbor] for neighbor in neighbors]
                    variance = 0.0
                    if neighbor_weights:
                        average = mean(neighbor_weights)
                        variance = mean((value - average) ** 2 for value in neighbor_weights)
                    signature_support = 0
                    for signature in cell["missing_signatures"]:
                        matching_neighbors = 0
                        for neighbor in neighbors:
                            neighbor_cell = row_cells[neighbor]
                            if signature in neighbor_cell["missing_signatures"]:
                                matching_neighbors += 1
                        signature_support = max(signature_support, matching_neighbors)
                        signature_map[signature].append(cell)
                    hidden_pressure = clamp(
                        safe_div(len(cell["missing_signatures"]), 4.0)
                        + safe_div(signature_support, 6.0)
                        + (0.10 if cell["frontier_status"] != "stable" else 0.0)
                    )

                    cell_class = "degenerate"
                    if cell["weight"] >= master_key_threshold and (
                        cell["route_family_count"] >= 3 or cell["dimension_span"] >= 0.40
                    ):
                        cell_class = "master-key"
                    elif cell["contradiction_cost"] >= 0.35:
                        cell_class = "contradictory"
                    elif hidden_pressure >= 0.75 and signature_support >= 3:
                        cell_class = "hidden-pressure"
                    elif variance >= 0.04:
                        cell_class = "unstable"
                    elif cell["frontier_status"] != "stable":
                        cell_class = "frontier"
                    elif cell["weight"] >= median_weight and variance < 0.03 and row["truth"] == "OK":
                        cell_class = "seated"
                    elif cell["weight"] >= median_weight:
                        cell_class = "promising"

                    if cell_class == "master-key":
                        byte_summary[cell["byte_state"]]["master_key_count"] += 1
                    if cell_class == "hidden-pressure":
                        byte_summary[cell["byte_state"]]["hidden_pressure_count"] += 1
                    if cell_class == "contradictory":
                        byte_summary[cell["byte_state"]]["contradictory_count"] += 1
                    class_counts[cell_class] += 1
                    byte_summary[cell["byte_state"]]["weight_total"] += cell["weight"]
                    byte_summary[cell["byte_state"]]["visible_total"] += cell["visible_node_count"]
                    byte_summary[cell["byte_state"]]["route_density_total"] += cell["route_density"]
                    byte_summary[cell["byte_state"]]["tunnel_total"] += cell["tunnel_count"]
                    byte_summary[cell["byte_state"]]["row_count"] += 1

                    for signature in cell["missing_signatures"]:
                        hidden_neighbors_for_row.add(signature)

                    matrix_row = {
                        "nexus_id": row["nexus_id"],
                        "byte_state": cell["byte_state"],
                        "q0": cell["q0"],
                        "q1": cell["q1"],
                        "q2": cell["q2"],
                        "q3": cell["q3"],
                        "weight": cell["weight"],
                        "cell_class": cell_class,
                        "visible_node_count": cell["visible_node_count"],
                        "route_density": cell["route_density"],
                        "tunnel_count": cell["tunnel_count"],
                        "dimension_span": cell["dimension_span"],
                        "hidden_pressure": round(hidden_pressure, 6),
                        "contradiction_class": cell["contradiction_class"],
                        "frontier_status": cell["frontier_status"],
                        "dominant_layers": cell["dominant_layers"],
                    }
                    matrix_handle.write(json.dumps(matrix_row) + "\n")
                    top_state_weights.append((cell["weight"], cell["byte_state"]))

                for signature, signature_cells in signature_map.items():
                    evidence_states = sorted({item["byte_state"] for item in signature_cells})
                    if len(evidence_states) < 3:
                        continue
                    average_route_count = mean(item["route_family_count"] for item in signature_cells)
                    if average_route_count < 2:
                        continue
                    candidate_id = f"HC-{slugify(signature)}-{slugify(row['nexus_id'])}"
                    hidden_candidates[candidate_id] = {
                        "candidate_id": candidate_id,
                        "candidate_class": signature,
                        "evidence_states": evidence_states,
                        "adjacent_nodes": row["related_hubs"][:6],
                        "structural_need": self._structural_need(signature),
                        "confidence_class": self._confidence_class(len(evidence_states)),
                        "seat_now_or_frontier": "frontier",
                    }

                top_state_weights.sort(reverse=True)
                if row["static_scores"]["master_weight"] >= MASTER_SCORE_THRESHOLD:
                    raw_master_rows.append(
                        {
                            "nexus_id": row["nexus_id"],
                            "canonical_name": row["nexus_id"],
                            "nexus_class": "raw_nexus",
                            "host_layers": row["host_layers"],
                            "route_degree": len({feature["route_family"] for feature in row["features"]}),
                            "dimensional_span": len(set(row["connected_dims"])),
                            "zero_aether_polarity": self._polarity_label(row["static_scores"]["z_aether_liminal_polarity"]),
                            "master_weight": round(row["static_scores"]["master_weight"], 6),
                            "recurrence": round(row["static_scores"]["source_recurrence"], 6),
                            "related_hubs": row["related_hubs"],
                            "touching_tunnels": [row["tunnel_class"]],
                            "timing_states": [item[1] for item in top_state_weights[:8]],
                            "hidden_neighbors": sorted(hidden_neighbors_for_row),
                            "status_class": "seated" if row["truth"] == "OK" else "frontier",
                            "source_paths": [
                                normalize_relative(SEAT_ROUTE_MAP_PATH),
                                normalize_relative(NEXUS_TUNNELS_PATH),
                                normalize_relative(DIMENSION_BRIDGES_PATH),
                            ],
                        }
                    )

        master_registry_rows = explicit_registry_rows + raw_master_rows
        master_registry_rows.sort(key=lambda item: (-item["master_weight"], item["canonical_name"]))

        byte_rows: list[dict[str, Any]] = []
        for byte_state, summary in byte_summary.items():
            count = summary["row_count"] or 1
            q0, q1, q2, q3 = decode_byte(byte_state)
            byte_rows.append(
                {
                    "byte_state": byte_state,
                    "q0": q0,
                    "q1": q1,
                    "q2": q2,
                    "q3": q3,
                    "anchor": Q0_LABELS[q0],
                    "hand_relation": Q1_LABELS[q1],
                    "spin": Q2_LABELS[q2],
                    "plane": Q3_LABELS[q3],
                    "avg_weight": round(summary["weight_total"] / count, 6),
                    "avg_visible_nodes": round(summary["visible_total"] / count, 6),
                    "avg_route_density": round(summary["route_density_total"] / count, 6),
                    "avg_tunnels": round(summary["tunnel_total"] / count, 6),
                    "master_key_count": summary["master_key_count"],
                    "hidden_pressure_count": summary["hidden_pressure_count"],
                    "contradictory_count": summary["contradictory_count"],
                }
            )
        byte_rows.sort(key=lambda item: (-item["master_key_count"], -item["avg_weight"], item["byte_state"]))

        hsigma = self.build_hsigma(
            context=context,
            explicit_edges=explicit_edges,
            explicit_registry_rows=explicit_registry_rows,
            raw_rows=raw_rows,
            master_registry_rows=master_registry_rows,
            hidden_candidates=hidden_candidates,
            class_counts=class_counts,
            byte_rows=byte_rows,
            master_key_threshold=master_key_threshold,
        )
        nexus_registry_payload = {
            "generated_at": self.generated_at,
            "derivation_version": DERIVATION_VERSION,
            "docs_gate_status": self.docs_gate_status,
            "master_threshold": MASTER_SCORE_THRESHOLD,
            "raw_nexus_count": len(raw_rows),
            "master_registry_count": len(master_registry_rows),
            "master_registry": master_registry_rows,
        }
        hidden_payload = {
            "generated_at": self.generated_at,
            "derivation_version": DERIVATION_VERSION,
            "docs_gate_status": self.docs_gate_status,
            "candidate_count": len(hidden_candidates),
            "candidates": list(hidden_candidates.values()),
        }
        regeneration_seed = {
            "generated_at": self.generated_at,
            "derivation_version": DERIVATION_VERSION,
            "compiler_command": DERIVATION_COMMAND,
            "docs_gate_status": self.docs_gate_status,
            "output_paths": {
                "ledger": normalize_relative(LEDGER_OUTPUT_PATH),
                "hsigma": normalize_relative(HSIGMA_OUTPUT_PATH),
                "nexus_registry": normalize_relative(NEXUS_REGISTRY_OUTPUT_PATH),
                "mindsweeper_jsonl": normalize_relative(MATRIX_OUTPUT_PATH),
                "hidden_candidates": normalize_relative(HIDDEN_OUTPUT_PATH),
                "regeneration_seed": normalize_relative(SEED_OUTPUT_PATH),
            },
            "row_counts": {
                "raw_nexus": len(raw_rows),
                "master_registry": len(master_registry_rows),
                "matrix_rows": len(raw_rows) * 256,
                "hidden_candidates": len(hidden_candidates),
            },
            "source_digests": self.source_digests,
            "replay_recipe": [
                DERIVATION_COMMAND,
                f"verify docs gate remains {self.docs_gate_status}",
                f"confirm matrix row count == {len(raw_rows) * 256}",
                "rebuild markdown ledger from HSigma, nexus registry, hidden candidates, and byte summary",
            ],
        }

        write_json(HSIGMA_OUTPUT_PATH, hsigma)
        write_json(NEXUS_REGISTRY_OUTPUT_PATH, nexus_registry_payload)
        write_json(HIDDEN_OUTPUT_PATH, hidden_payload)
        write_json(SEED_OUTPUT_PATH, regeneration_seed)
        write_text(
            LEDGER_OUTPUT_PATH,
            self.build_markdown(
                hsigma=hsigma,
                nexus_registry=nexus_registry_payload,
                hidden_payload=hidden_payload,
                byte_rows=byte_rows,
                class_counts=class_counts,
                master_key_threshold=master_key_threshold,
            ),
        )

        self.validate_outputs(
            hsigma=hsigma,
            nexus_registry=nexus_registry_payload,
            hidden_payload=hidden_payload,
            matrix_rows=len(raw_rows) * 256,
            byte_rows=byte_rows,
        )
        return {
            "hsigma": hsigma,
            "nexus_registry": nexus_registry_payload,
            "hidden_payload": hidden_payload,
            "regeneration_seed": regeneration_seed,
        }

    def _structural_need(self, signature: str) -> str:
        reasons = {
            "latent_transfer_station": "Multiple route families converged without an explicit witnessed interchange.",
            "latent_liminal_gate": "Hall and Temple traffic required a phase-change carrier that is not explicitly seated.",
            "latent_aether_return": "Promotion-grade bridges surfaced without a visible aether-side return hinge.",
            "latent_zero_repair_junction": "Restart or repair traffic collapsed toward zero without a named repair junction.",
            "latent_replay_closure": "A floor-oriented traversal exposed motion without a lawful replay receipt.",
        }
        return reasons.get(signature, "Repeated neighboring timing states implied an unresolved transfer center.")

    def _confidence_class(self, evidence_count: int) -> str:
        if evidence_count >= 8:
            return "high"
        if evidence_count >= 5:
            return "medium"
        return "low"

    def _polarity_label(self, value: float) -> str:
        if value >= 0.75:
            return "balanced-zero-aether-liminal"
        if value >= 0.55:
            return "centered"
        return "frontier"

    def build_hsigma(
        self,
        context: dict[str, Any],
        explicit_edges: list[dict[str, Any]],
        explicit_registry_rows: list[dict[str, Any]],
        raw_rows: list[dict[str, Any]],
        master_registry_rows: list[dict[str, Any]],
        hidden_candidates: dict[str, dict[str, Any]],
        class_counts: Counter[str],
        byte_rows: list[dict[str, Any]],
        master_key_threshold: float,
    ) -> dict[str, Any]:
        top_dispatch = sorted(
            context["grand_central_weights"],
            key=lambda item: item["dispatch_score"],
            reverse=True,
        )[:12]
        top_master_keys = byte_rows[:16]
        return {
            "hologram_id": f"HSIGMA-{ARTIFACT_DATE}-LOCAL",
            "generated_at": self.generated_at,
            "derivation_version": DERIVATION_VERSION,
            "docs_gate_status": self.docs_gate_status,
            "N": {
                "raw_count": len(raw_rows),
                "master_count": len(master_registry_rows),
                "explicit_count": len(explicit_registry_rows),
                "registry_path": normalize_relative(NEXUS_REGISTRY_OUTPUT_PATH),
            },
            "E": {
                "explicit_edge_count": len(explicit_edges),
                "route_families": sorted({edge["route_family"] for edge in explicit_edges}),
                "top_edges": explicit_edges[:16],
            },
            "Z": {
                "count": len(context["zpoints"]),
                "items": context["zpoints"],
            },
            "A": {
                "count": len(context["aether_points"]),
                "anchors": sorted(
                    context["aether_points"],
                    key=lambda item: item["aether_density"],
                    reverse=True,
                )[:16],
            },
            "L": {
                "loop_count": len(context["liminal_registry"].get("loop_coordinate_stamps", [])),
                "master_agent_count": len(context["liminal_registry"].get("master_agents", [])),
                "loop_samples": context["liminal_registry"].get("loop_coordinate_stamps", [])[:8],
            },
            "T": {
                "count": len(context["grand_central_tunnels"]) + len(context["nexus_tunnels"]),
                "grand_central_tunnels": context["grand_central_tunnels"],
                "tunnel_classes": Counter(item["tunnel_class"] for item in context["nexus_tunnels"]),
            },
            "B": {
                "commissure_count": len(context["grand_central_weights"]),
                "seat_bridge_count": len(context["seat_bridges"]),
                "crosswalk_edge_count": len(context["crosswalk_edges"]),
                "top_dispatch_routes": top_dispatch,
            },
            "D": {
                "dimension_bridge_count": len(context["dimension_bridges"]),
                "bridge_roles": Counter(item["bridge_role"] for item in context["dimension_bridges"]),
                "active_dimensions": ["3D", "4D", "5D", "6D", "7D"],
            },
            "W": {
                "dispatch_formula": "0.20*C + 0.20*Reachability + 0.15*TunnelGain + 0.15*DimensionalSpan + 0.10*Compression + 0.10*Replay + 0.10*Novelty - 0.10*Contradiction",
                "grand_central_routes": top_dispatch,
                "lens_profiles": context["lens_profiles"][:8],
            },
            "Psi": {
                "state_count": 256,
                "byte_schema": {
                    "q0": Q0_LABELS,
                    "q1": Q1_LABELS,
                    "q2": Q2_LABELS,
                    "q3": Q3_LABELS,
                },
                "top_master_keys": top_master_keys,
            },
            "M": {
                "matrix_path": normalize_relative(MATRIX_OUTPUT_PATH),
                "row_count": len(raw_rows) * 256,
                "master_key_threshold": round(master_key_threshold, 6),
                "class_counts": dict(class_counts),
                "top_master_keys": top_master_keys,
                "candidate_count": len(hidden_candidates),
            },
            "R": {
                "receipt_count": len(context["replay_receipts"]),
                "replay_anchors": context["replay_receipts"][:12],
            },
            "provenance": {
                "source_count": len(self.source_digests),
                "source_digests": self.source_digests,
            },
            "save_state": {
                "ledger_path": normalize_relative(LEDGER_OUTPUT_PATH),
                "hidden_candidates_path": normalize_relative(HIDDEN_OUTPUT_PATH),
                "regeneration_seed_path": normalize_relative(SEED_OUTPUT_PATH),
                "future_docs_delta": self.docs_gate_status != "LIVE",
            },
        }

    def build_markdown(
        self,
        hsigma: dict[str, Any],
        nexus_registry: dict[str, Any],
        hidden_payload: dict[str, Any],
        byte_rows: list[dict[str, Any]],
        class_counts: Counter[str],
        master_key_threshold: float,
    ) -> str:
        master_rows = nexus_registry["master_registry"]
        top_master_keys = byte_rows[:12]
        hidden_candidates = hidden_payload["candidates"][:24]
        transfer_rows = [item for item in master_rows if item["nexus_class"] == "transfer_hub"]
        root_rows = [item for item in master_rows if item["nexus_class"] == "grand_central_root"]
        tunnel_rows = [item for item in master_rows if item["nexus_class"] == "tunnel_anchor"]
        raw_rows = [item for item in master_rows if item["nexus_class"] == "raw_nexus"]
        auxiliary_rows = [
            item
            for item in master_rows
            if item["nexus_class"] not in {"transfer_hub", "grand_central_root", "tunnel_anchor", "raw_nexus"}
        ]

        def registry_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
            if limit is not None:
                rows = rows[:limit]
            if not rows:
                return "_No rows._"
            headers = [
                "nexus_id",
                "canonical_name",
                "nexus_class",
                "master_weight",
                "route_degree",
                "dimensional_span",
                "status_class",
            ]
            table_rows = [
                [
                    str(row["nexus_id"]),
                    str(row["canonical_name"]),
                    str(row["nexus_class"]),
                    f"{row['master_weight']}",
                    str(row["route_degree"]),
                    str(row["dimensional_span"]),
                    str(row["status_class"]),
                ]
                for row in rows
            ]
            return self._markdown_table(headers, table_rows)

        parts = [
            "# TOTAL HOLOGRAPHIC SNAPSHOT / MASTER NEXUS WEIGHTS MINDSWEEPER",
            "",
            f"- Generated at: `{self.generated_at}`",
            f"- Derivation version: `{DERIVATION_VERSION}`",
            f"- Docs gate: `{self.docs_gate_status}`",
            f"- Hologram id: `{hsigma['hologram_id']}`",
            "",
            "PART I - MASTER HOLOGRAM THESIS",
            "",
            f"`{HSIGMA_SYMBOL}` is compiled as one compressed but replayable snapshot over the current organism. It preserves the local distinction among metro, mycelium, neural, zero, liminal, aether, tunnel, bridge, replay, and witness families while routing all of them through one saved state.",
            "",
            "PART II - CURRENT TOTAL SNAPSHOT OF THE MAPPING ORGANISM",
            "",
            self._markdown_table(
                ["family", "count", "note"],
                [
                    ["N", str(hsigma["N"]["raw_count"]), "raw nexus rows carried by the 4096-seat lattice"],
                    ["N*", str(hsigma["N"]["master_count"]), "human-facing master nexus registry"],
                    ["Z", str(hsigma["Z"]["count"]), "explicit zero family"],
                    ["A", str(hsigma["A"]["count"]), "explicit aether-point registry size"],
                    ["L", str(hsigma["L"]["loop_count"] + hsigma["L"]["master_agent_count"]), "liminal loop stamps plus master agents"],
                    ["T", str(hsigma["T"]["count"]), "grand central plus raw nexus tunnel surfaces"],
                    ["B", str(hsigma["B"]["commissure_count"] + hsigma["B"]["seat_bridge_count"]), "commissure and seat bridge surfaces"],
                    ["M", str(hsigma["M"]["row_count"]), "full mindsweeper cells"],
                ],
            ),
            "",
            "PART III - FOUR-AGENT NESTED CRYSTAL",
            "",
            self._markdown_table(
                ["agent", "purpose", "runtime binding"],
                [
                    ["A1", "snapshot synthesizer", "ingest canon, deep root, runtime, and hemisphere surfaces into one graph"],
                    ["A2", "nexus cartographer", "score explicit hubs and raw nexus rows into N*"],
                    ["A3", "two-hemisphere timing sweeper", "run the 256-byte sweep over every raw nexus row"],
                    ["A4", "weights mindsweeper compressor", "classify cells, infer latent candidates, and save the compressed hologram"],
                ],
            ),
            "",
            "PART IV - SINGLE-HOLOGRAM DATA MODEL (HSIGMA)",
            "",
            "```text",
            f"{HSIGMA_SYMBOL} = (N, E, Z, A, L, T, B, D, W, Psi, M, R)",
            "```",
            "",
            f"- N registry path: `{hsigma['N']['registry_path']}`",
            f"- Mindsweeper path: `{hsigma['M']['matrix_path']}`",
            f"- Save state ledger: `{hsigma['save_state']['ledger_path']}`",
            "",
            "PART V - MASTER NEXUS REGISTRY",
            "",
            "## Transfer hubs",
            "",
            registry_table(transfer_rows),
            "",
            "## Grand Central roots",
            "",
            registry_table(root_rows),
            "",
            "## Tunnel-class anchors",
            "",
            registry_table(tunnel_rows),
            "",
            "## Zero, liminal, aether, replay, and named-seat anchors",
            "",
            registry_table(auxiliary_rows),
            "",
            "## Raw nexus rows above master threshold",
            "",
            registry_table(raw_rows),
            "",
            "PART VI - TWO-HEMISPHERE TIMING LATTICE",
            "",
            self._markdown_table(
                ["axis", "values"],
                [
                    ["q0", "GC0 center / GCL structural / GCR generative / GCZ-Aether transit"],
                    ["q1", "TOG/SAME / TOG/OPP / SPLIT/SAME / SPLIT/OPP"],
                    ["q2", "(IN,IN) / (IN,ANTI) / (ANTI,IN) / (ANTI,ANTI)"],
                    ["q3", "WALL / WHEEL / FLOOR / MIX"],
                ],
            ),
            "",
            "PART VII - 256-STATE ORIENTATION BYTE STANDARD",
            "",
            "```text",
            "B = q0 + 4q1 + 16q2 + 64q3",
            "```",
            "",
            self._markdown_table(
                ["byte", "anchor", "relation", "spin", "plane", "avg_weight", "master_keys"],
                [
                    [
                        str(item["byte_state"]),
                        item["anchor"],
                        item["hand_relation"],
                        item["spin"],
                        item["plane"],
                        f"{item['avg_weight']}",
                        str(item["master_key_count"]),
                    ]
                    for item in top_master_keys
                ],
            ),
            "",
            "PART VIII - SIMPLE EXHAUSTIVE SWEEP ALGORITHM",
            "",
            "1. Ingest explicit ledgers and machine manifests.",
            "2. Normalize explicit hubs and raw nexus rows into one graph-backed feature field.",
            "3. Score N* using the master nexus equation.",
            "4. Sweep every raw nexus row across all 256 byte states.",
            "5. Accumulate weights and per-byte summaries.",
            "6. Classify cells as seated, promising, hidden-pressure, unstable, contradictory, frontier, degenerate, or master-key.",
            "7. Infer latent candidates only when neighboring-byte pressure repeats across at least three states.",
            "8. Save HSigma, the full mindsweeper JSONL, the master registry, hidden candidates, and the regeneration seed.",
            "",
            "PART IX - WEIGHT FUNCTION + MINDSWEEPER MATRIX MODEL",
            "",
            "```text",
            "w(n,B) = 0.20*Centrality + 0.20*Reachability + 0.15*TunnelGain + 0.15*DimensionalSpan + 0.10*Compression + 0.10*Replay + 0.10*Novelty - 0.10*Contradiction",
            "```",
            "",
            f"- Master-key threshold: `{round(master_key_threshold, 6)}`",
            f"- Class counts: `{json.dumps(dict(class_counts), sort_keys=True)}`",
            "",
            "PART X - MASTER NEXUS X TIMING EXPOSURE FIELD",
            "",
            f"The full field is saved at `{normalize_relative(MATRIX_OUTPUT_PATH)}` with `{hsigma['M']['row_count']}` JSONL rows. The table above shows the strongest byte states by average yield and master-key count.",
            "",
            "PART XI - HIDDEN NEXUS DISCOVERY LOGIC",
            "",
            self._markdown_table(
                ["candidate_id", "candidate_class", "evidence_states", "confidence", "seat_state"],
                [
                    [
                        item["candidate_id"],
                        item["candidate_class"],
                        ",".join(str(state) for state in item["evidence_states"][:8]),
                        item["confidence_class"],
                        item["seat_now_or_frontier"],
                    ]
                    for item in hidden_candidates
                ]
                or [["none", "none", "-", "-", "-"]],
            ),
            "",
            "PART XII - ZERO / LIMINAL / AETHER / TUNNEL MAP",
            "",
            f"- Zero family count: `{hsigma['Z']['count']}`",
            f"- Liminal loop count: `{hsigma['L']['loop_count']}`",
            f"- Aether point count: `{hsigma['A']['count']}`",
            f"- Tunnel surface count: `{hsigma['T']['count']}`",
            "",
            "PART XIII - MASTER ROUTE / HUB / BRIDGE / TUNNEL REGISTRY",
            "",
            f"- Explicit edge count: `{hsigma['E']['explicit_edge_count']}`",
            f"- Commissure routes: `{hsigma['B']['commissure_count']}`",
            f"- Seat bridges: `{hsigma['B']['seat_bridge_count']}`",
            f"- Crosswalk edges: `{hsigma['B']['crosswalk_edge_count']}`",
            "",
            "PART XIV - MASTER-KEY ORIENTATIONS OF EXPLORATION",
            "",
            self._markdown_table(
                ["byte", "anchor", "spin", "plane", "master_keys", "hidden_pressure"],
                [
                    [
                        str(item["byte_state"]),
                        item["anchor"],
                        item["spin"],
                        item["plane"],
                        str(item["master_key_count"]),
                        str(item["hidden_pressure_count"]),
                    ]
                    for item in top_master_keys
                ],
            ),
            "",
            "PART XV - FRONTIER / CONTRADICTION / UNSTABLE ZONES",
            "",
            f"- Frontier cells: `{class_counts.get('frontier', 0)}`",
            f"- Hidden-pressure cells: `{class_counts.get('hidden-pressure', 0)}`",
            f"- Contradictory cells: `{class_counts.get('contradictory', 0)}`",
            f"- Unstable cells: `{class_counts.get('unstable', 0)}`",
            "",
            "PART XVI - COMPRESSED SINGLE-HOLOGRAM SAVE STATE",
            "",
            f"- HSigma JSON: `{normalize_relative(HSIGMA_OUTPUT_PATH)}`",
            f"- Master registry JSON: `{normalize_relative(NEXUS_REGISTRY_OUTPUT_PATH)}`",
            f"- Hidden candidate JSON: `{normalize_relative(HIDDEN_OUTPUT_PATH)}`",
            "",
            "PART XVII - REGENERATION SEED OF THE WHOLE HOLOGRAM",
            "",
            f"- Regeneration seed: `{normalize_relative(SEED_OUTPUT_PATH)}`",
            f"- Source digests carried: `{len(self.source_digests)}`",
            f"- Replay command: `{DERIVATION_COMMAND}`",
            "",
            "PART XVIII - FINAL INTEGRITY VERDICT",
            "",
            f"The current artifact is lawful as a local-first snapshot. The docs gate remains `{self.docs_gate_status}`, so every live-doc claim stays blocked and frontier uncertainty remains isolated instead of hallucinated. The saved hologram is replayable, the mindsweeper field is exhaustive over the 4096-seat raw lattice, and hidden candidates were admitted only under repeated neighborhood pressure.",
            "",
        ]
        return "\n".join(parts)

    def _markdown_table(self, headers: list[str], rows: list[list[str]]) -> str:
        head = "| " + " | ".join(headers) + " |"
        divider = "| " + " | ".join("---" for _ in headers) + " |"
        body = ["| " + " | ".join(row) + " |" for row in rows]
        return "\n".join([head, divider, *body])

    def validate_outputs(
        self,
        hsigma: dict[str, Any],
        nexus_registry: dict[str, Any],
        hidden_payload: dict[str, Any],
        matrix_rows: int,
        byte_rows: list[dict[str, Any]],
    ) -> None:
        if self.docs_gate_status != "BLOCKED":
            raise RuntimeError(f"Expected BLOCKED docs gate, found {self.docs_gate_status}")
        if hsigma["M"]["row_count"] != matrix_rows:
            raise RuntimeError("Matrix row count mismatch")
        if not LEDGER_OUTPUT_PATH.exists() or not HSIGMA_OUTPUT_PATH.exists():
            raise RuntimeError("Required artifact outputs are missing")
        if len(byte_rows) != 256:
            raise RuntimeError("Expected 256 byte states")
        required_explicit = {"ST-T1", "ST-T10", "A01", "A19", "Z0", "Z5"}
        required_explicit.update({f"ZT-00{i}" for i in range(1, 7)})
        registry_ids = {item["nexus_id"] for item in nexus_registry["master_registry"]}
        missing = sorted(required_explicit - registry_ids)
        if missing:
            raise RuntimeError(f"Master registry missing explicit anchors: {missing}")
        if hidden_payload["candidate_count"] != len(hidden_payload["candidates"]):
            raise RuntimeError("Hidden candidate count mismatch")
        with MATRIX_OUTPUT_PATH.open("r", encoding="utf-8") as handle:
            actual_rows = sum(1 for _ in handle)
        if actual_rows != matrix_rows:
            raise RuntimeError(f"Mindsweeper matrix row count mismatch: expected {matrix_rows}, got {actual_rows}")


def main() -> int:
    compiler = TotalHolographicSnapshotCompiler()
    compiler.compile()
    print(
        json.dumps(
            {
                "generated_at": compiler.generated_at,
                "docs_gate_status": compiler.docs_gate_status,
                "ledger": normalize_relative(LEDGER_OUTPUT_PATH),
                "hsigma": normalize_relative(HSIGMA_OUTPUT_PATH),
                "nexus_registry": normalize_relative(NEXUS_REGISTRY_OUTPUT_PATH),
                "mindsweeper": normalize_relative(MATRIX_OUTPUT_PATH),
                "hidden_candidates": normalize_relative(HIDDEN_OUTPUT_PATH),
                "regeneration_seed": normalize_relative(SEED_OUTPUT_PATH),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
