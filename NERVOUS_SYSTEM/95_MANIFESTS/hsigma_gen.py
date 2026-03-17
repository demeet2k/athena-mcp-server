from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path

ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
MAN = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
SELF = ROOT / "self_actualize"
MATH = ROOT / "MATH" / "FINAL FORM" / "MATH GOD" / "atlas" / "hsigma_explicit"
REC = ROOT / "self_actualize" / "mycelium_brain" / "receipts"
NOW = datetime.now().astimezone().isoformat()

LF = [
    ("LAMBDA1", "Metro", "Metro layer", "Discrete transfer-optimized routing graph preserving station identity and interchange load."),
    ("LAMBDA2", "Mycelium", "Mycelium layer", "Branching adaptive diffusion graph preserving branching pressure and filament continuity."),
    ("LAMBDA3", "Neural", "Neural layer", "Convergence/divergence associative graph preserving recurrence and cross-link density."),
    ("LAMBDA4", "Zero", "Zero layer", "Collapse and normalization pole preserving sink behavior, reset behavior, and route simplification."),
    ("LAMBDA5", "Liminal", "Liminal layer", "Phase-shift and uncertainty layer preserving ambiguity without erasing structure."),
    ("LAMBDA6", "Aether", "Aether layer", "Expansion and lift pole preserving reopening, re-expansion, and possibility inflation."),
    ("LAMBDA7", "Tunnel", "Tunnel layer", "Nonlocal bypass layer preserving entrance and exit identity plus shortcut legality."),
    ("LAMBDA8", "BridgeReturn", "Bridge / return / hinge layer", "Linkage layer for transfer, return, folding, and structural reattachment."),
    ("LAMBDA9", "Dimensional", "Dimensional layer", "Lift, crossing, non-planar projection, and manifold transit layer."),
    ("LAMBDA10", "ReplayWitnessProof", "Replay / witness / proof layer", "Evidentiary route layer preserving recurrence, replay, witness, and proof closure."),
    ("LAMBDA11", "SeedRegeneration", "Seed / crystal / regeneration layer", "Compression and reseeding layer preserving regeneration anchors and save-state survivability."),
]

DS = [
    ("D0", "Planar routing stratum", "Metro, mycelium, and neural surface-level navigation."),
    ("D1", "Hinge / liminal stratum", "Transfer, phase-shift, bridge approach, and ambiguity mediation."),
    ("D2", "Pole stratum", "Zero collapse and aether expansion."),
    ("D3", "Nonlocal transit stratum", "Tunnels, lifts, crossings, and nonlocal bridgework."),
    ("D4", "Evidentiary / regenerative stratum", "Replay, witness, proof closure, seed preservation, and regeneration."),
]

TOPO = {
    "Metro": ["Liminal", "BridgeReturn", "ReplayWitnessProof"],
    "Mycelium": ["Liminal", "Aether", "SeedRegeneration"],
    "Neural": ["Liminal", "ReplayWitnessProof", "Dimensional"],
    "Zero": ["Liminal", "Tunnel", "ReplayWitnessProof"],
    "Aether": ["Liminal", "Tunnel", "Dimensional", "SeedRegeneration"],
    "Liminal": ["Metro", "Mycelium", "Neural", "Zero", "Aether", "Tunnel", "BridgeReturn", "Dimensional"],
    "Tunnel": ["Zero", "Aether", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "BridgeReturn": ["Metro", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "Dimensional": ["BridgeReturn", "Tunnel", "ReplayWitnessProof"],
    "ReplayWitnessProof": ["Zero", "BridgeReturn", "SeedRegeneration"],
    "SeedRegeneration": ["Aether", "Mycelium", "ReplayWitnessProof"],
}

RDEF = [
    "R1|Metro rail|01|01|01|01",
    "R2|Mycelial filament|12|23|12|23",
    "R3|Neural link|123|13|123|13",
    "R4|Zero-collapse route|02|01|012|02",
    "R5|Liminal transition route|0123|123|12|3",
    "R6|Aether expansion route|13|02|123|13",
    "R7|Tunnel bypass route|0123|13|123|3",
    "R8|Bridge / hinge route|013|013|0123|013",
    "R9|Dimensional lift route|13|123|123|13",
    "R10|Manifold crossing route|23|3|123|3",
    "R11|Replay loop|3|013|123|03",
    "R12|Witness / proof-bearing route|03|02|012|023",
    "R13|Seed / regeneration route|13|23|123|23",
]

TDEF = [
    "T/ZC|Zero-collapse tunnel|02|0123|012|02|zero",
    "T/AL|Aether-lift tunnel|13|0123|123|13|aether",
    "T/LS|Liminal-shortcut tunnel|0123|23|0123|3|liminal",
    "T/DJ|Dimensional-jump tunnel|0123|3|123|3|dimensional",
    "T/RR|Replay-return tunnel|3|13|0123|03|replay",
    "T/BC|Bridge-compression tunnel|0123|0123|0123|03|bridge",
]

EDEF = [
    "Z0|02|01|012|023",
    "ZL|02|02|012|02",
    "A0|13|02|123|13",
    "L0|0123|123|12|3",
    "MT|013|01|01|01",
    "MS|0123|012|012|03",
    "MY|12|23|12|23",
    "NN|123|13|123|13",
    "TE|02|13|012|3",
    "TX|13|13|123|3",
    "DB|123|13|123|13",
    "DL|13|123|123|13",
    "MC|23|3|123|3",
    "RA|3|013|123|03",
    "WA|03|02|012|023",
    "SC|13|23|123|23",
    "MR|3|13|123|03",
    "PA|3|02|012|03",
    "LP|123|23|123|3",
]

ROWDEF = [
    "Z0|Global Zero Anchor|zero_anchor|seated|Zero,Liminal,Tunnel,Dimensional,ReplayWitnessProof|R4,R5,R7,R8,R9,R11|6|4|Z++|L0,TE,DB,RA|T/ZC,T/RR,T/BC|C1,C3|83",
    "ZL|Local Zero Point|local_zero_point|seated|Zero,Liminal,Tunnel|R4,R5,R7|3|3|Z+|L0,TE,Z0|T/ZC|C1,C6|50",
    "A0|Primary Aether Point|aether_point|seated|Aether,Liminal,Tunnel,Dimensional,SeedRegeneration|R5,R6,R7,R8,R9|5|4|A++|L0,TX,DL,SC|T/AL,T/DJ|C1,C5|75",
    "L0|Liminal Transfer Point|liminal_transfer_hinge|seated|Liminal,Zero,Aether,Tunnel,BridgeReturn,Dimensional|R4,R5,R6,R7,R8,R9,R10|7|4|balanced mediator|Z0,A0,MS,DB|T/LS,T/ZC,T/AL,T/DJ|C1,C2,C3,C6|92",
    "MT|Metro Transfer Hub|metro_transfer_hub|seated|Metro,Liminal,BridgeReturn,ReplayWitnessProof|R1,R5,R8,R11|4|3|neutral|MS,L0,RA|T/LS,T/BC|C2|58",
    "MS|Master Transfer Station|cross_family_master_interchange|seated|Metro,Mycelium,Neural,Liminal,BridgeReturn,Dimensional,ReplayWitnessProof|R1,R2,R3,R5,R8,R9,R11|7|4|neutral structural hinge|MT,MY,NN,DB|T/LS,T/BC,T/DJ|C2,C3|92",
    "MY|Mycelium Branch Hub|mycelial_branching_hub|seated|Mycelium,Liminal,Aether,SeedRegeneration|R2,R5,R6,R7,R13|5|4|A+|MS,A0,SC,L0|T/LS,T/AL|C2,C5,C6|75",
    "NN|Neural Convergence Hub|neural_convergence_hub|seated|Neural,Liminal,Aether,Dimensional,ReplayWitnessProof|R3,R5,R6,R7,R10,R12|6|5|balanced-liminal|MS,MC,WA,L0|T/LS,T/DJ|C2,C4,C6|91",
    "TE|Tunnel Entrance|tunnel_entrance|seated|Tunnel,Zero,Liminal,BridgeReturn|R4,R5,R7,R8|4|3|Z+ entry|Z0,L0,DB|T/ZC,T/LS,T/DJ|C1,C3|58",
    "TX|Tunnel Exit|tunnel_exit|seated|Tunnel,Aether,Liminal,BridgeReturn|R5,R6,R7,R8|4|3|A+ release|A0,L0,DL|T/AL,T/LS,T/DJ|C1,C3|58",
    "DB|Dimensional Bridge Station|dimensional_bridge_station|seated|BridgeReturn,Liminal,Dimensional,Tunnel|R5,R7,R8,R9,R10|5|3|balanced|L0,MS,MC,TE,TX|T/DJ,T/BC|C1,C3|67",
    "DL|Dimensional Lift|dimensional_lift_station|seated|Dimensional,Aether,Tunnel|R6,R7,R9,R10|4|2|A+|A0,DB,MC,TX|T/AL,T/DJ|C1,C3|50",
    "MC|Manifold Crossing|manifold_crossing_station|seated|Dimensional,BridgeReturn,Neural,ReplayWitnessProof|R7,R8,R9,R10,R12|5|3|balanced-opposed|DB,DL,NN,WA|T/DJ,T/BC|C3,C4|67",
    "RA|Replay Anchor|replay_anchor|seated|ReplayWitnessProof,BridgeReturn,SeedRegeneration|R8,R11,R12,R13|4|3|Z-return bias|MR,WA,SC,MT|T/RR,T/BC|C4,C5|58",
    "WA|Witness Anchor|witness_anchor|seated|ReplayWitnessProof,Neural|R5,R11,R12|3|2|Z-stabilized|RA,NN,PA||C4|42",
    "SC|Seed Crystal|seed_crystal_anchor|seated|SeedRegeneration,Aether,Mycelium,ReplayWitnessProof|R6,R11,R12,R13|4|3|A-seeded|A0,MY,RA||C5|58",
    "MR|Mobius Return Hinge|return_hinge|frontier|BridgeReturn,ReplayWitnessProof,Zero|R4,R7,R8,R11|4|3|cyclic return|RA,Z0,DB|T/RR,T/ZC|C4|58",
    "PA|Proof Anchor|proof_anchor|frontier|ReplayWitnessProof,BridgeReturn|R8,R11,R12|3|2|Z-stabilized evidentiary closure|WA,RA,MR||C4|42",
    "LP|Latent Pressure Hub|latent_pressure_hub|inferred|Liminal,BridgeReturn,Dimensional|R5,R7,R8,R9,R10|5|4|unresolved|L0,DB,MC,MS|T/LS,T/DJ,T/BC|C2,C3,C6|60",
]

CANDDEF = [
    ("C1", "Zero-Aether Mediating Lift Hub", "frontier", "medium-high", [212, 166, 222, 247, 255], ["Z0", "L0", "A0", "TE", "TX"], "Repeated entrance/exit asymmetry plus simultaneous zero-collapse and aether-expansion pressure."),
    ("C2", "Metro-Mycelium-Neural Composite Transfer Node", "frontier", "high structural", [217, 166, 212], ["MT", "MS", "MY", "NN", "L0"], "Pairwise transfers do not fully absorb three-family convergence pressure."),
    ("C3", "Dimensional Midspan Bridge", "frontier", "high structural", [222, 247, 255], ["DB", "DL", "MC", "TE", "TX"], "Jumps and crossings imply a lawful intermediate stabilizer."),
    ("C4", "Replay / Proof Closure Junction", "frontier", "medium", [51, 247, 255], ["RA", "WA", "MR", "PA"], "Witness-bearing replay without a closure node remains structurally incomplete."),
    ("C5", "Seed-Replay Regeneration Coupler", "frontier", "medium", [81, 235, 247], ["SC", "A0", "RA", "MY"], "Seed crystal and replay anchor need a stable bridge for save-state regeneration."),
    ("C6", "Frontier Liminal Distributor", "frontier", "low-medium", [222, 223, 238, 239, 254, 255], ["L0", "ZL", "A0", "MS"], "Branching frontier pressure exceeds the capacity of a single liminal hinge abstraction."),
]

SL = {
    "q0": {0: "SEAT", 1: "ADVANCE", 2: "CROSS", 3: "RETURN"},
    "q1": {0: "TOG-SAME", 1: "TOG-OPP", 2: "SPLIT-SAME", 3: "SPLIT-OPP"},
    "q2": {0: "IN-IN", 1: "IN-ANTI", 2: "ANTI-IN", 3: "ANTI-ANTI"},
    "q3": {0: "WALL", 1: "WHEEL", 2: "FLOOR", 3: "MIX"},
}

SF = {
    "Metro": "D0",
    "Mycelium": "D0",
    "Neural": "D0",
    "Liminal": "D1",
    "BridgeReturn": "D1",
    "Zero": "D2",
    "Aether": "D2",
    "Tunnel": "D3",
    "Dimensional": "D3",
    "ReplayWitnessProof": "D4",
    "SeedRegeneration": "D4",
}


def pset(text: str) -> list[int]:
    return [int(char) for char in text]


ROUTES = {}
for row in RDEF:
    rid, name, p0, p1, p2, p3 = row.split("|")
    ROUTES[rid] = {"name": name, "P0": pset(p0), "P1": pset(p1), "P2": pset(p2), "P3": pset(p3)}

TUNNELS = {}
for row in TDEF:
    tid, name, p0, p1, p2, p3, bias = row.split("|")
    TUNNELS[tid] = {"title": name, "P0": pset(p0), "P1": pset(p1), "P2": pset(p2), "P3": pset(p3), "bias": bias}

EXP = {}
for row in EDEF:
    rid, p0, p1, p2, p3 = row.split("|")
    EXP[rid] = {"P0": pset(p0), "P1": pset(p1), "P2": pset(p2), "P3": pset(p3)}

ROWS = []
for row in ROWDEF:
    rid, title, row_class, status, families, routes, deg, span, polarity, related, tunnels, hidden, w0 = row.split("|")
    ROWS.append(
        {
            "nexus_id": rid,
            "title": title,
            "class": row_class,
            "status": status,
            "host_families": families.split(",") if families else [],
            "incident_routes": routes.split(",") if routes else [],
            "deg_s": int(deg),
            "span": int(span),
            "polarity": polarity,
            "related_hubs": related.split(",") if related else [],
            "touching_tunnels": tunnels.split(",") if tunnels else [],
            "hidden_neighbors": hidden.split(",") if hidden else [],
            "w0": int(w0),
        }
    )

ROW = {item["nexus_id"]: item for item in ROWS}
ORDER = [item["nexus_id"] for item in ROWS]

GRAPH = defaultdict(set)
for row in ROWS:
    for neighbor in row["related_hubs"]:
        GRAPH[row["nexus_id"]].add(neighbor)
        GRAPH[neighbor].add(row["nexus_id"])

CANDS = [
    {
        "candidate_id": cid,
        "title": title,
        "status": status,
        "confidence": confidence,
        "evidence_states": states,
        "adjacent_explicit_nodes": nodes,
        "structural_need": need,
    }
    for cid, title, status, confidence, states, nodes, need in CANDDEF
]


def h(text: str, length: int = 4) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest().upper()[:length]


def dec(byte_value: int) -> tuple[int, int, int, int]:
    return byte_value % 4, (byte_value // 4) % 4, (byte_value // 16) % 4, (byte_value // 64) % 4


def enc(q0: int, q1: int, q2: int, q3: int) -> int:
    return q0 + 4 * q1 + 16 * q2 + 64 * q3


def nbrs(byte_value: int) -> list[int]:
    q = list(dec(byte_value))
    result = set()
    for index in range(4):
        for delta in (-1, 1):
            nxt = q.copy()
            nxt[index] = (nxt[index] + delta) % 4
            result.add(enc(*nxt))
    return sorted(result)


def gate(book: dict, q: tuple[int, int, int, int]) -> float:
    return sum(q[index] in book[f"P{index}"] for index in range(4)) / 4.0


def route_ok(route_id: str, row_id: str, q: tuple[int, int, int, int]) -> bool:
    if gate(ROUTES[route_id], q) < 0.5:
        return False
    if route_id == "R12":
        return bool({"R11", "RA", "WA", "PA", "NN", "MC", "SC"} & (set(ROW[row_id]["incident_routes"]) | set(GRAPH[row_id]) | {row_id}))
    if route_id == "R13":
        return bool({"A0", "RA", "SC", "MY"} & (set(GRAPH[row_id]) | {row_id}))
    return True


def tunnel_ok(tunnel_id: str, q: tuple[int, int, int, int]) -> bool:
    return gate(TUNNELS[tunnel_id], q) >= 0.5


def expose(row_id: str, q: tuple[int, int, int, int]) -> float:
    return gate(EXP[row_id], q)


def act_routes(row_id: str, q: tuple[int, int, int, int]) -> list[str]:
    return [route_id for route_id in ROW[row_id]["incident_routes"] if route_ok(route_id, row_id, q)]


def act_tunnels(row_id: str, q: tuple[int, int, int, int]) -> list[str]:
    return [tunnel_id for tunnel_id in ROW[row_id]["touching_tunnels"] if tunnel_ok(tunnel_id, q)]


def bfs(row_id: str, q: tuple[int, int, int, int]) -> tuple[list[str], dict[str, int]]:
    if expose(row_id, q) < 0.5:
        return [], {}
    seen = {row_id}
    dist = {row_id: 0}
    queue = deque([row_id])
    while queue:
        current = queue.popleft()
        current_routes = set(act_routes(current, q))
        for neighbor in GRAPH[current]:
            if neighbor in seen or expose(neighbor, q) < 0.5:
                continue
            if not (current_routes & set(act_routes(neighbor, q))):
                continue
            seen.add(neighbor)
            dist[neighbor] = dist[current] + 1
            queue.append(neighbor)
    return sorted(seen, key=lambda item: ORDER.index(item)), dist


def fams(node_ids: list[str]) -> list[str]:
    values = set()
    for node_id in node_ids:
        values.update(ROW[node_id]["host_families"])
    return sorted(values)


def strata(node_ids: list[str]) -> list[str]:
    return sorted({SF[family] for node_id in node_ids for family in ROW[node_id]["host_families"] if family in SF})


def radius_two_families(distances: dict[str, int]) -> list[str]:
    return fams([node_id for node_id, depth in distances.items() if depth <= 2])


def replay_value(reach: list[str], q: tuple[int, int, int, int]) -> float:
    value = (1 if "RA" in reach else 0) + (1 if "WA" in reach else 0) + (1 if "SC" in reach else 0)
    if "PA" in reach:
        value += 0.5
    elif expose("PA", q) >= 0.75:
        value += 0.25
    return value / 3.5


def hidden_pressure(row_id: str, q: tuple[int, int, int, int], reach: list[str], active_tunnels: list[str]) -> float:
    q0, q1, q2, q3 = q
    u_cross = 1.0 if (q1 == 3 and q3 == 3 and "MC" not in reach) else 0.5 if (q1 in {1, 3} and q3 == 3 and "MC" not in reach) else 0.0
    te_in, tx_in = "TE" in reach, "TX" in reach
    u_tunnel = 1.0 if active_tunnels and te_in != tx_in else 0.5 if active_tunnels and not (te_in or tx_in) else 0.0
    z_in, a_in, l_in = ("Z0" in reach or "ZL" in reach), "A0" in reach, "L0" in reach
    u_pole = 1.0 if z_in and a_in and not l_in else 0.5 if q0 in {1, 2, 3} and z_in != a_in else 0.0
    replay_in, closure_in = ("RA" in reach or "WA" in reach), ("MR" in reach or "PA" in reach)
    u_replay = 1.0 if replay_in and not closure_in else 0.5 if replay_in and expose("PA", q) >= 0.75 else 0.0
    tri = sum(1 for item in ("MT", "MY", "NN") if item in reach)
    u_transfer = 1.0 if tri >= 2 and "MS" not in reach else 0.5 if tri >= 1 and "MS" not in reach else 0.0
    if row_id == "LP" and q1 in {2, 3} and q3 == 3:
        u_transfer = max(u_transfer, 1.0)
    return round((u_cross + u_tunnel + u_pole + u_replay + u_transfer) / 5.0, 6)


def contradiction(q: tuple[int, int, int, int], reach: list[str], active_routes: list[str], active_tunnels: list[str]) -> float:
    z_in, a_in, l_in = ("Z0" in reach or "ZL" in reach), "A0" in reach, "L0" in reach
    v_pole = 1 if z_in and a_in and not l_in else 0
    te_in, tx_in = "TE" in reach, "TX" in reach
    v_tunnel = 1 if active_tunnels and te_in != tx_in else 0
    v_dim = 1 if ({"R9", "R10"} & set(active_routes)) and not ({"DB", "DL", "MC"} & set(reach)) else 0
    v_replay = 1 if "R11" in active_routes and not ({"RA", "WA", "MR", "PA"} & set(reach)) else 0
    return round((v_pole + v_tunnel + v_dim + v_replay) / 4.0, 6)


def visibility(status: str, exposure: float, pressure: float) -> str:
    if exposure >= 0.5 and status in {"seated", "frontier"}:
        return "explicit"
    if exposure >= 0.25 or pressure >= 0.45:
        return "implied"
    return "absent"


def timing_states() -> list[dict]:
    out = []
    for byte_value in range(256):
        q0, q1, q2, q3 = dec(byte_value)
        out.append(
            {
                "byte": byte_value,
                "q0": q0,
                "q1": q1,
                "q2": q2,
                "q3": q3,
                "labels": {
                    "anchor_phase": SL["q0"][q0],
                    "relation_state": SL["q1"][q1],
                    "spin_field": SL["q2"][q2],
                    "plane_state": SL["q3"][q3],
                },
                "neighbors": nbrs(byte_value),
            }
        )
    return out


def build_cells() -> tuple[list[dict], dict[str, dict[str, float]]]:
    cells = []
    rowmap = {row_id: {} for row_id in ORDER}
    wmap = {row_id: {} for row_id in ORDER}
    reachmap = {row_id: {} for row_id in ORDER}
    for row_id in ORDER:
        row = ROW[row_id]
        cp = row["deg_s"] / 7.0
        for byte_value in range(256):
            q = dec(byte_value)
            exp = round(expose(row_id, q), 6)
            active_routes = act_routes(row_id, q)
            reach, distances = bfs(row_id, q)
            reachmap[row_id][byte_value] = reach
            active_tunnels = [tunnel_id for tunnel_id in act_tunnels(row_id, q) if reach]
            reached_strata = strata(reach)
            reached_families = fams(reach)
            local_families = radius_two_families(distances)
            reachability = sum(1 for item in reach if ROW[item]["status"] in {"seated", "frontier"}) / 18.0
            tunnel_gain = len(active_tunnels) / 6.0
            dimensional_gain = len(reached_strata) / 5.0
            compression_value = len(local_families) / max(1, len(reached_families))
            replay_gain = replay_value(reach, q)
            pressure = hidden_pressure(row_id, q, reach, active_tunnels)
            contradiction_load = contradiction(q, reach, active_routes, active_tunnels)
            frontier_fraction = sum(1 for item in reach if ROW[item]["status"] != "seated") / max(1, len(reach))
            route_density = len(active_routes) / max(1, len(row["incident_routes"]))
            weight = round(20 * cp + 20 * reachability + 15 * tunnel_gain + 15 * dimensional_gain + 10 * compression_value + 10 * replay_gain, 6)
            cell = {
                "nexus_id": row_id,
                "byte": byte_value,
                "coordinate": {"q0": q[0], "q1": q[1], "q2": q[2], "q3": q[3]},
                "exposure": exp,
                "active_routes": active_routes,
                "active_tunnel_classes": active_tunnels,
                "reached_nexus": reach,
                "reached_strata": reached_strata,
                "reachable_families": reached_families,
                "weight": weight,
                "visibility": visibility(row["status"], exp, pressure),
                "hidden_pressure": pressure,
                "contradiction": contradiction_load,
                "frontier_fraction": round(frontier_fraction, 6),
                "route_density": round(route_density, 6),
                "exposed_nexus_count": len(reach),
                "exposed_tunnel_count": len(active_tunnels),
                "reachability": round(reachability, 6),
                "tunnel_gain": round(tunnel_gain, 6),
                "dimensional_gain": round(dimensional_gain, 6),
                "compression_value": round(compression_value, 6),
                "replay_value": round(replay_gain, 6),
                "centrality_prior": round(cp, 6),
                "novel_exposure": 0.0,
                "timing_instability": 0.0,
                "classification": "pending",
            }
            rowmap[row_id][byte_value] = cell
            wmap[row_id][byte_value] = weight
            cells.append(cell)

    stats = {}
    for row_id in ORDER:
        weights = list(wmap[row_id].values())
        mean = sum(weights) / len(weights)
        variance = sum((weight - mean) ** 2 for weight in weights) / len(weights)
        stats[row_id] = {"mean": mean, "std": math.sqrt(variance)}

    for row_id in ORDER:
        for byte_value in range(256):
            cell = rowmap[row_id][byte_value]
            neighbors = nbrs(byte_value)
            overlap = set.intersection(*[set(reachmap[row_id][neighbor]) for neighbor in neighbors]) if neighbors else set()
            novel = set(cell["reached_nexus"]) - overlap
            cell["novel_exposure"] = round(len([item for item in novel if ROW[item]["status"] != "inferred"]) / 18.0, 6)
            cell["weight"] = round(cell["weight"] + 10 * cell["novel_exposure"], 6)
            neighbor_weights = [wmap[row_id][neighbor] for neighbor in neighbors]
            cell["timing_instability"] = round((max(neighbor_weights) - min(neighbor_weights)) / 100.0, 6)
            status = ROW[row_id]["status"]
            aligned = len(cell["reached_strata"])
            mean = stats[row_id]["mean"]
            std = stats[row_id]["std"]
            if cell["contradiction"] >= 0.40:
                classification = "contradictory"
            elif status == "seated" and cell["weight"] >= 80 and aligned >= 4 and cell["contradiction"] < 0.25 and cell["exposed_nexus_count"] >= mean + std:
                classification = "master-key"
            elif cell["hidden_pressure"] >= 0.45 and cell["contradiction"] < 0.40:
                classification = "hidden-pressure"
            elif cell["frontier_fraction"] > 0.50 and cell["contradiction"] < 0.40:
                classification = "frontier"
            elif cell["timing_instability"] >= 0.25 and cell["contradiction"] < 0.40:
                classification = "unstable"
            elif status == "seated" and cell["weight"] >= 70 and cell["hidden_pressure"] < 0.30 and cell["contradiction"] < 0.25:
                classification = "seated"
            elif 55 <= cell["weight"] < 70 and cell["contradiction"] < 0.40:
                classification = "promising"
            else:
                classification = "degenerate"
            if status == "frontier" and classification in {"master-key", "seated"}:
                classification = "frontier"
            if status == "inferred" and classification in {"master-key", "seated"}:
                classification = "hidden-pressure"
            cell["classification"] = classification
    return cells, {row_id: {"mean_weight": round(value["mean"], 6), "std_weight": round(value["std"], 6)} for row_id, value in stats.items()}


def bundle_objects() -> tuple[dict, dict, dict, dict]:
    layers = [{"layer_id": a, "code": b, "title": c, "description": d} for a, b, c, d in LF]
    strata_list = [{"stratum_id": a, "title": b, "description": c} for a, b, c in DS]
    states = timing_states()
    cells, row_stats = build_cells()
    counts = {
        "layer_families": 11,
        "route_families": 13,
        "seated_nexus_rows": 16,
        "frontier_explicit_rows": 2,
        "inferred_rows": 1,
        "tunnel_classes": 6,
        "dimensional_strata": 5,
        "timing_states": 256,
        "mindsweeper_cells": 4864,
    }
    seed = "ATH-HSIGMA::11L/16S+2F+1I/13R/6T/5D/256PSI/4864M/MUFIX"
    save_state = {
        "save_state_id": "HSIGMA_STAR",
        "visibility_mode": "class-exhaustive / instance-frontier",
        "layers": [item["code"] for item in layers],
        "explicit_nexus_rows": [item["nexus_id"] for item in ROWS if item["status"] == "seated"],
        "frontier_nexus_rows": [item["nexus_id"] for item in ROWS if item["status"] == "frontier"],
        "inferred_nexus_rows": [item["nexus_id"] for item in ROWS if item["status"] == "inferred"],
        "route_families": list(ROUTES),
        "tunnel_classes": list(TUNNELS),
        "dimensional_strata": [item["stratum_id"] for item in strata_list],
        "timing_engine": {"space": "Z4^4", "byte_encode": "B=q0+4q1+16q2+64q3", "state_count": 256, "neighborhood": "toroidal axis-neighbors"},
        "hidden_candidates": [item["candidate_id"] for item in CANDS],
        "fixed_point_rule": "stop when no candidate promotion and no material row-class change",
        "frontier_policy": "never promote unsupported latent structure into explicit fact",
        "mnemonic_seed_string": seed,
    }
    regeneration_seed = {
        "seed_id": "OMEGA_REGEN_HSIGMA",
        "components": ["Layer registry", "Nexus row set", "Incidence structure", "Dimensional strata", "Timing lattice", "Route gate book", "Nexus exposure book", "Weight function", "Mindsweeper cell schema", "Hidden-nexus inference operator", "Fixed-point operator", "Frontier policy"],
        "deterministic_regeneration_steps": ["Recreate the 11 layer families.", "Seat the 16 explicit rows.", "Add the 2 frontier explicit rows without promoting them.", "Add LP as inferred only.", "Restore the 13 route families and 6 tunnel classes.", "Rebuild the 5 strata.", "Recreate the 256-state toroidal timing lattice.", "Reapply route and nexus gate books.", "Recompute all 4864 mindsweeper cells.", "Rerun hidden inference and the fixed-point pass.", "Save the stabilized object back to HSIGMA_STAR."],
        "mnemonic_seed_string": seed,
    }
    crosswalk = {
        "deep_root_authority": "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK",
        "binding": {"basis_documents": 16, "matrix_pairs": 256, "observer_passes": 64, "symmetry_stack": "15 plus zero point", "metro_levels": 7, "lane_level_support": ["H6", "Seed-6D", "Appendix Q"]},
        "law": "HSIGMA is the current whole-organism visible snapshot above the existing H6 and Seed-6D lane bundles; H6, Seed-6D, and Appendix Q remain evidence-support and convergence surfaces.",
        "crosswalk_paths": [
            "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/07_METRO_STACK/06_level_6_hologram_weave_map.md",
            "self_actualize/mycelium_brain/dynamic_neural_network/14_DEEPER_INTEGRATED_CROSS_SYNTHESIS_NETWORK/08_APPENDIX_CRYSTAL/AppQ_appendix_only_metro_map.md",
            "MATH/FINAL FORM/MATH GOD/atlas/h6_explicit/math_h6_convergence_bundle.md",
        ],
    }
    bundle = {
        "generated_at": NOW,
        "bundle_id": "HSIGMA_LIVE_HOLOGRAM_BUNDLE",
        "title": "HSIGMA Live Hologram Bundle",
        "docs_gate_status": "BLOCKED",
        "docs_gate_detail": "Trading Bot/credentials.json and Trading Bot/token.json are still missing.",
        "visibility_mode": "class-exhaustive / instance-frontier",
        "current_runtime_truth": {"canonical_authority": "NEXT57", "active_loop": "L02", "active_family": "A02 self_actualize", "restart_seed": "L03 Survey A03 ECOSYSTEM", "visible_caps": {"hall": 8, "temple": 8}, "active_membrane": "Q41 / TQ06", "feeders": ["Q42", "Q46", "TQ04", "TQ06", "Q02(blocked)"]},
        "counts": counts,
        "layer_families": layers,
        "dimensional_strata": strata_list,
        "global_topology_seed": TOPO,
        "nexus_registry": ROWS,
        "timing_states": states,
        "route_families": [{"route_id": route_id, "title": route["name"], "gate_book": {"P0": route["P0"], "P1": route["P1"], "P2": route["P2"], "P3": route["P3"]}} for route_id, route in ROUTES.items()],
        "tunnel_classes": [{"tunnel_id": tunnel_id, "title": tunnel["title"], "gate_book": {"P0": tunnel["P0"], "P1": tunnel["P1"], "P2": tunnel["P2"], "P3": tunnel["P3"]}, "entrance_bias": tunnel["bias"]} for tunnel_id, tunnel in TUNNELS.items()],
        "nexus_exposure_book": EXP,
        "hidden_candidates": CANDS,
        "row_statistics": row_stats,
        "save_state_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_SAVE_STATE.json",
        "mindsweeper_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_MINDSWEEPER_FIELD_4864.json",
        "deep_root_crosswalk": crosswalk,
        "frontier_policy": "No unsupported latent structure may be promoted into explicit fact. MR and PA remain frontier-explicit. LP remains inferred.",
        "regeneration_seed": regeneration_seed,
    }
    mindsweeper = {
        "generated_at": NOW,
        "field_id": "HSIGMA_MINDSWEEPER_FIELD_4864",
        "bundle_id": "HSIGMA_LIVE_HOLOGRAM_BUNDLE",
        "rows": ORDER,
        "columns": list(range(256)),
        "cell_count": 4864,
        "cell_schema": ["nexus_id", "byte", "coordinate", "exposure", "active_routes", "active_tunnel_classes", "reached_nexus", "reached_strata", "reachable_families", "weight", "visibility", "hidden_pressure", "contradiction", "frontier_fraction", "route_density", "exposed_nexus_count", "exposed_tunnel_count", "reachability", "tunnel_gain", "dimensional_gain", "compression_value", "replay_value", "centrality_prior", "novel_exposure", "timing_instability", "classification"],
        "cells": cells,
    }
    return bundle, mindsweeper, save_state, crosswalk


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def simple_bundle_markdown(bundle: dict) -> str:
    counts = bundle["counts"]
    lines = [
        "# HSIGMA Live Hologram Bundle",
        "",
        f"Generated: `{bundle['generated_at']}`",
        "",
        "## Scope",
        "",
        "- Docs gate: `BLOCKED`",
        "- Canonical runtime authority: `NEXT57`",
        "- Visibility mode: `class-exhaustive / instance-frontier`",
        "- Active loop: `L02 Survey A02 self_actualize`",
        "- Restart seed: `L03 Survey A03 ECOSYSTEM`",
        "- Visible caps: `Hall 8 / Temple 8`",
        "",
        "## Canonical Counts",
        "",
    ]
    lines.extend([f"- `{key.replace('_', ' ')}`: `{value}`" for key, value in counts.items()])
    lines.extend(
        [
            "",
            "## Nexus Registry Summary",
            "",
            "- Seated rows: `Z0, ZL, A0, L0, MT, MS, MY, NN, TE, TX, DB, DL, MC, RA, WA, SC`",
            "- Frontier explicit rows: `MR, PA`",
            "- Inferred row: `LP`",
            "",
            "## Timing Engine",
            "",
            "- Space: `Z4^4`",
            "- Byte encode: `B=q0+4q1+16q2+64q3`",
            "- State count: `256`",
            "- Neighborhood law: `8 toroidal axis-neighbors per state`",
            "- Mindsweeper field: `19 x 256 = 4864 cells`",
            "",
            "## Deep Root Crosswalk",
            "",
            "- Compiled basis: `16`",
            "- Matrix pairs: `256`",
            "- Observer passes: `64`",
            "- Symmetry stack: `15 plus zero point`",
            "- Metro levels: `7`",
            "- H6 / Seed-6D / Appendix Q role: `lane-level support; not superseding HSIGMA`",
            "",
            "## Frontier Law",
            "",
            "- `MR` and `PA` remain frontier-explicit.",
            "- `LP` remains inferred.",
            "- `C1-C6` remain hidden candidates until fixed-point thresholds promote them lawfully.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def simple_crosswalk_markdown(bundle: dict) -> str:
    crosswalk = bundle["deep_root_crosswalk"]
    lines = [
        "# HSIGMA To Deep Root Crosswalk",
        "",
        f"Generated: `{bundle['generated_at']}`",
        "",
        "## Law",
        "",
        crosswalk["law"],
        "",
        "## Bindings",
        "",
        f"- Basis documents: `{crosswalk['binding']['basis_documents']}`",
        f"- Matrix pairs: `{crosswalk['binding']['matrix_pairs']}`",
        f"- Observer passes: `{crosswalk['binding']['observer_passes']}`",
        f"- Symmetry stack: `{crosswalk['binding']['symmetry_stack']}`",
        f"- Metro levels: `{crosswalk['binding']['metro_levels']}`",
        f"- Lane-level support: `{', '.join(crosswalk['binding']['lane_level_support'])}`",
        "",
        "## Authority Paths",
        "",
    ]
    lines.extend([f"- `{path}`" for path in crosswalk["crosswalk_paths"]])
    lines.append("")
    return "\n".join(lines)


def coord(xs: str, ys: str, zs: str, ts: str, qs: str, rs: str, cs: str, fs: str, ms: str, ns: str, hs: str, omega: str) -> dict:
    return {"Xs": xs, "Ys": ys, "Zs": zs, "Ts": ts, "Qs": qs, "Rs": rs, "Cs": cs, "Fs": fs, "Ms": h(ms), "Ns": h(ns), "Hs": hs, "Omega_s": omega}


def main() -> None:
    bundle, mindsweeper, save_state, crosswalk = bundle_objects()
    write_json(MAN / "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", bundle)
    write_text(MAN / "HSIGMA_LIVE_HOLOGRAM_BUNDLE.md", simple_bundle_markdown(bundle))
    write_json(MAN / "HSIGMA_MINDSWEEPER_FIELD_4864.json", mindsweeper)
    write_json(MAN / "HSIGMA_SAVE_STATE.json", save_state)
    write_text(MAN / "HSIGMA_TO_DEEP_ROOT_CROSSWALK.md", simple_crosswalk_markdown(bundle))
    write_json(MATH / "hsigma_live_hologram_bundle.json", bundle)
    write_text(MATH / "hsigma_live_hologram_bundle.md", simple_bundle_markdown(bundle))
    write_text(MATH / "hsigma_h6_seed6d_crosswalk.md", simple_crosswalk_markdown(bundle))

    refs = {
        "hsigma_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_LIVE_HOLOGRAM_BUNDLE.json",
        "hsigma_save_state_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_SAVE_STATE.json",
        "hsigma_mindsweeper_ref": "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_MINDSWEEPER_FIELD_4864.json",
        "hsigma_frontier_policy": "class-exhaustive / instance-frontier / MR and PA frontier / LP inferred / no unsupported promotion",
        "hsigma_coordinate_delta_ref": "self_actualize/next57_hsigma_coordinate_delta.json",
    }

    for path in [SELF / "next57_four_agent_corpus_cycle_state.json", SELF / "next57_prime_loop_protocol.json"]:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(refs)
        data["hologram_substrate"] = "HSIGMA"
        schema = data.get("agent_ledger_schema")
        if isinstance(schema, dict):
            for field in ["hsigma_nodes_touched", "timing_states_touched", "frontier_changes", "candidate_pressure_changes", "save_state_ref"]:
                if field not in schema.get("fields", []):
                    schema["fields"].append(field)
            schema.setdefault("sample_entry", {})
            schema["sample_entry"]["hsigma_nodes_touched"] = ["Z0", "L0", "RA", "SC"]
            schema["sample_entry"]["timing_states_touched"] = [0, 81, 166, 212, 247, 255]
            schema["sample_entry"]["frontier_changes"] = ["MR kept frontier", "PA kept frontier", "LP kept inferred"]
            schema["sample_entry"]["candidate_pressure_changes"] = ["C3 increased under split-opposed mix", "C4 preserved as replay/proof frontier"]
            schema["sample_entry"]["save_state_ref"] = refs["hsigma_save_state_ref"]
            if "HSIGMA frontier policy preserves MR and PA as frontier and LP as inferred until lawful promotion." not in schema.get("continuity_law", []):
                schema["continuity_law"].append("HSIGMA frontier policy preserves MR and PA as frontier and LP as inferred until lawful promotion.")
            data["agent_ledger_schema"] = schema
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    ledger = json.loads((SELF / "next57_agent_ledger_schema.json").read_text(encoding="utf-8"))
    for field in ["hsigma_nodes_touched", "timing_states_touched", "frontier_changes", "candidate_pressure_changes", "save_state_ref"]:
        if field not in ledger["fields"]:
            ledger["fields"].append(field)
    if "HSIGMA frontier policy preserves MR and PA as frontier and LP as inferred until lawful promotion." not in ledger["continuity_law"]:
        ledger["continuity_law"].append("HSIGMA frontier policy preserves MR and PA as frontier and LP as inferred until lawful promotion.")
    ledger["sample_entry"]["hsigma_nodes_touched"] = ["Z0", "L0", "MT", "MS", "RA", "SC"]
    ledger["sample_entry"]["timing_states_touched"] = [0, 81, 166, 212, 222, 247, 255]
    ledger["sample_entry"]["frontier_changes"] = ["MR kept frontier", "PA kept frontier", "LP kept inferred"]
    ledger["sample_entry"]["candidate_pressure_changes"] = ["C1 retained as pole mediator frontier", "C3 retained as dimensional midspan frontier", "C4 retained as replay/proof frontier"]
    ledger["sample_entry"]["save_state_ref"] = refs["hsigma_save_state_ref"]
    ledger["sample_entry"]["artifact_ref"] = refs["hsigma_ref"]
    write_json(SELF / "next57_agent_ledger_schema.json", ledger)

    current_loop = "L02"
    hsigma_entries = []
    for row in ROWS:
        omega = "CLASS_FRONTIER" if row["status"] != "seated" else "LOCAL_ONLY"
        hsigma_entries.append({"node_id": f"HSIGMA::{row['nexus_id']}", "source_path": refs["hsigma_ref"], "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "Survey", current_loop, "QHS-L02-H01", "Prime", "LINKED", "Square", row["nexus_id"], f"NEXUS::{row['nexus_id']}", "NODE", omega), "agent_id": "L02.A2.D0.BROOT.PLAN-ARCHITECT", "loop_id": current_loop, "quest_links": ["QHS-L02-H01"], "v4_or_appendix_anchor": "AppI/AppM/AppQ"})
    for route_id in ROUTES:
        hsigma_entries.append({"node_id": f"HSIGMA::{route_id}", "source_path": refs["hsigma_ref"], "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "Survey", current_loop, "QHS-L02-H02", "Prime", "PACKETIZED", "Flower", route_id, f"ROUTE::{route_id}", "NODE", "LOCAL_ONLY"), "agent_id": "L02.A2.D0.BROOT.PLAN-ARCHITECT", "loop_id": current_loop, "quest_links": ["QHS-L02-H02"], "v4_or_appendix_anchor": "AppA/AppI/AppM"})
    for tunnel_id in TUNNELS:
        hsigma_entries.append({"node_id": f"HSIGMA::{tunnel_id}", "source_path": refs["hsigma_ref"], "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "Survey", current_loop, "QHS-L02-H03", "Prime", "PACKETIZED", "Flower", tunnel_id, f"TUNNEL::{tunnel_id}", "NODE", "LOCAL_ONLY"), "agent_id": "L02.A2.D0.BROOT.PLAN-ARCHITECT", "loop_id": current_loop, "quest_links": ["QHS-L02-H03"], "v4_or_appendix_anchor": "AppI/AppM/AppQ"})
    for candidate in CANDS:
        hsigma_entries.append({"node_id": f"HSIGMA::{candidate['candidate_id']}", "source_path": refs["hsigma_ref"], "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "Survey", current_loop, "TQHS-L02-T03", "Prime", "RAW", "Cloud", candidate["candidate_id"], f"CAND::{candidate['candidate_id']}", "NODE", "CLASS_FRONTIER"), "agent_id": "L02.A4.D0.BROOT.PRUNE-COMPRESS", "loop_id": current_loop, "quest_links": ["TQHS-L02-T03"], "v4_or_appendix_anchor": "AppI/AppM"})
    hsigma_entries.append({"node_id": "HSIGMA::SAVE_STATE", "source_path": refs["hsigma_save_state_ref"], "coordinate_tuple": coord("A01", "HSIGMA_SAVE_STATE.json", "Survey", current_loop, "QHS-L02-H04", "Prime", "COMPRESSED", "Fractal", "HSIGMA_STAR", "SAVE_STATE", "SURFACE", "RESTART"), "agent_id": "L02.A4.D0.BROOT.PRUNE-COMPRESS", "loop_id": current_loop, "quest_links": ["QHS-L02-H04"], "v4_or_appendix_anchor": "AppI/AppM/AppQ"})
    hsigma_entries.append({"node_id": "HSIGMA::REGENERATION_SEED", "source_path": refs["hsigma_ref"], "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "Survey", current_loop, "TQHS-L02-T04", "Prime", "COMPRESSED", "Fractal", "OMEGA_REGEN_HSIGMA", "REGEN", "SURFACE", "RESTART"), "agent_id": "L02.A4.D0.BROOT.PRUNE-COMPRESS", "loop_id": current_loop, "quest_links": ["TQHS-L02-T04"], "v4_or_appendix_anchor": "AppI/AppM/AppQ"})

    coord_path = SELF / "next57_liminal_coordinate_registry.json"
    coord_data = json.loads(coord_path.read_text(encoding="utf-8"))
    coord_data["hsigma_coordinate_delta_ref"] = refs["hsigma_coordinate_delta_ref"]
    coord_data["hsigma_nodes"] = hsigma_entries
    coord_data["compression_nodes"].append({"node_id": "hsigma-save-state", "coordinate_tuple": coord("A01", "HSIGMA_SAVE_STATE.json", "COMPRESS", current_loop, "QHS-L02-H04", "COMPRESS", "COMPRESSED", "Fractal", "HSIGMA_STAR", "SAVE_STATE", "PRUNE", "RESTART")})
    coord_data["unresolved_issues"].append({"issue_id": "hsigma-instance-frontier", "coordinate_tuple": coord("A01", "HSIGMA_LIVE_HOLOGRAM_BUNDLE.json", "FRONTIER", current_loop, "TQHS-L02-T01", "Prime", "RAW", "Cloud", "INSTANCE_FRONTIER", "HSIGMA", "UNRESOLVED", "CLASS_FRONTIER")})
    write_json(coord_path, coord_data)
    write_json(SELF / "next57_hsigma_coordinate_delta.json", {"generated_at": NOW, "delta_id": "NEXT57_HSIGMA_COORDINATE_DELTA", "truth": "OK", "source_bundle": refs["hsigma_ref"], "entry_count": len(hsigma_entries), "entries": hsigma_entries})

    hall = json.loads((SELF / "next57_guild_hall_quest_tree.json").read_text(encoding="utf-8"))
    hall["hsigma_overlay"] = {"overlay_id": "HSIGMA_HALL_OVERLAY", "count_policy": "overlay_not_counted_against_visible_cap", "macro_family": [{"quest_id": "QHS-L02-H01", "title": "Compile HSIGMA Registry", "objective": "compile the 19-row nexus registry with class-exhaustive and instance-frontier law", "restart_seed": "QHS-L02-H02"}, {"quest_id": "QHS-L02-H02", "title": "Compile HSIGMA Timing Lattice", "objective": "materialize the 256-state timing byte lattice and toroidal neighbor geometry", "restart_seed": "QHS-L02-H03"}, {"quest_id": "QHS-L02-H03", "title": "Materialize HSIGMA Mindsweeper Field", "objective": "compute the 4864-cell mindsweeper field with route, tunnel, and classification data", "restart_seed": "QHS-L02-H04"}, {"quest_id": "QHS-L02-H04", "title": "Attach HSIGMA Coordinates And Save State", "objective": "attach coordinate back-pointers and persist HSIGMA_STAR as the regeneration-safe save state", "restart_seed": "L03 Survey A03 ECOSYSTEM"}], "machine_artifacts": [refs["hsigma_ref"], refs["hsigma_mindsweeper_ref"], refs["hsigma_save_state_ref"]]}
    write_json(SELF / "next57_guild_hall_quest_tree.json", hall)

    temple = json.loads((SELF / "next57_temple_quest_tree.json").read_text(encoding="utf-8"))
    temple["hsigma_overlay"] = {"overlay_id": "HSIGMA_TEMPLE_OVERLAY", "count_policy": "overlay_not_counted_against_visible_cap", "macro_family": [{"quest_id": "TQHS-L02-T01", "title": "Ratify HSIGMA Frontier And Promotion Law", "objective": "keep HSIGMA class-exhaustive and instance-frontier while forbidding unsupported promotion", "restart_seed": "TQHS-L02-T02"}, {"quest_id": "TQHS-L02-T02", "title": "Preserve Pole Distinction And Replay Legality", "objective": "keep zero, liminal, aether, tunnel, replay, proof, and seed legally distinct inside HSIGMA", "restart_seed": "TQHS-L02-T03"}, {"quest_id": "TQHS-L02-T03", "title": "Preserve Hidden Candidate Restraint", "objective": "keep MR, PA, LP, and C1-C6 at frontier or inferred status until fixed-point thresholds are met", "restart_seed": "TQHS-L02-T04"}, {"quest_id": "TQHS-L02-T04", "title": "Ratify Regeneration And Fixed-Point Doctrine", "objective": "preserve HSIGMA_STAR and the deterministic regeneration seed as the lawful rebuild contract", "restart_seed": "L03 Survey A03 ECOSYSTEM"}], "machine_artifacts": ["NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_LIVE_HOLOGRAM_BUNDLE.md", "NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_TO_DEEP_ROOT_CROSSWALK.md", refs["hsigma_save_state_ref"]]}
    write_json(SELF / "next57_temple_quest_tree.json", temple)

    receipt = "\n".join(["# HSIGMA Live Canon Install Receipt", "", f"Generated: `{NOW}`", "", "- Canonical authority: `NEXT57`", "- Docs gate: `BLOCKED`", "- Runtime truth honored: `L02 / L03 / Hall 8 / Temple 8`", "- Live canon installed: `NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_LIVE_HOLOGRAM_BUNDLE.json`", "- Save state installed: `NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_SAVE_STATE.json`", "- Mindsweeper field installed: `NERVOUS_SYSTEM/95_MANIFESTS/HSIGMA_MINDSWEEPER_FIELD_4864.json`", "- MATH mirror installed: `MATH/FINAL FORM/MATH GOD/atlas/hsigma_explicit/hsigma_live_hologram_bundle.json`", "- Counts: `11 layers / 13 routes / 16 seated / 2 frontier / 1 inferred / 6 tunnels / 5 strata / 256 timing / 4864 cells`", "- Frontier policy: `class-exhaustive / instance-frontier / no unsupported promotion`", ""])
    write_text(REC / "2026-03-13_hsigma_live_canon_install.md", receipt)


if __name__ == "__main__":
    main()
