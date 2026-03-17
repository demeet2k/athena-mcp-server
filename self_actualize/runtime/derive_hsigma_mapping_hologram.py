from __future__ import annotations

import json
import math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev
from zoneinfo import ZoneInfo


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ROOT = WORKSPACE_ROOT / "self_actualize"
MANIFEST_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"
HALL_ROOT = SELF_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = SELF_ROOT / "mycelium_brain" / "ATHENA TEMPLE"
RUNTIME_ROOT = SELF_ROOT / "mycelium_brain" / "nervous_system"
RECEIPTS_ROOT = SELF_ROOT / "mycelium_brain" / "receipts"
TIMEZONE = ZoneInfo("America/Los_Angeles")

DOCS_GATE_PATH = SELF_ROOT / "live_docs_gate_status.md"
CREDENTIALS_PATH = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
TOKEN_PATH = WORKSPACE_ROOT / "Trading Bot" / "token.json"

HSIGMA_MANIFEST_PATH = MANIFEST_ROOT / "ATHENA_HSIGMA_MAPPING_HOLOGRAM.json"
HSIGMA_MINDSWEEPER_PATH = MANIFEST_ROOT / "ATHENA_HSIGMA_MINDSWEEPER_19x256.json"
HSIGMA_SAVE_STATE_PATH = MANIFEST_ROOT / "ATHENA_HSIGMA_SAVE_STATE.json"
HSIGMA_WITNESS_PATH = MANIFEST_ROOT / "ATHENA_HSIGMA_RUNTIME_WITNESS.md"
HALL_WITNESS_PATH = HALL_ROOT / "18_HSIGMA_RUNTIME_WITNESS.md"
TEMPLE_WITNESS_PATH = TEMPLE_ROOT / "07_HSIGMA_RUNTIME_WITNESS.md"
RUNTIME_WITNESS_PATH = RUNTIME_ROOT / "receipts" / "HSIGMA_RUNTIME_WITNESS.md"
RECEIPT_WITNESS_PATH = RECEIPTS_ROOT / "2026-03-13_hsigma_runtime_witness.md"

SEED_STRING = "ATH-HSIGMA::11Λ/16S+2F+1I/13R/6T/5D/256Ψ/4864M/μFIX"
FRONTIER_POLICY = "never promote unsupported latent structure into explicit fact"
CLASS_PRECEDENCE = [
    "contradictory",
    "master-key",
    "hidden-pressure",
    "frontier",
    "unstable",
    "seated",
    "promising",
    "degenerate",
]

LAYERS = [
    {"id": "L1", "symbol": "Λ1", "name": "Metro", "description": "Discrete transfer-optimized routing graph. Preserves station identity, interchange load, and map legibility."},
    {"id": "L2", "symbol": "Λ2", "name": "Mycelium", "description": "Branching adaptive diffusion graph. Preserves branching, growth pressure, substrate spread, and filament continuity."},
    {"id": "L3", "symbol": "Λ3", "name": "Neural", "description": "Convergence/divergence associative graph. Preserves recurrence, cross-link density, witness attachment, and pattern compression."},
    {"id": "L4", "symbol": "Λ4", "name": "Zero", "description": "Collapse/normalization pole. Preserves sink behavior, reset behavior, route simplification, and graph normalization."},
    {"id": "L5", "symbol": "Λ5", "name": "Liminal", "description": "Phase-shift / uncertainty / transition layer. Preserves ambiguity without erasing structure. Mediates pole changes and inter-map transfer."},
    {"id": "L6", "symbol": "Λ6", "name": "Aether", "description": "Expansion / lift / outward projection pole. Preserves reopening, re-expansion, lift behavior, and possibility inflation."},
    {"id": "L7", "symbol": "Λ7", "name": "Tunnel", "description": "Nonlocal bypass layer. Preserves entrance/exit identity, bypass invariants, and shortcut legality."},
    {"id": "L8", "symbol": "Λ8", "name": "BridgeReturn", "description": "Linkage layer for transfer, return, folding, and structural reattachment. Includes ordinary bridges and return hinges."},
    {"id": "L9", "symbol": "Λ9", "name": "Dimensional", "description": "Lift, crossing, non-planar projection, and manifold transit layer. Hosts dimensional lifts and manifold crossings."},
    {"id": "L10", "symbol": "Λ10", "name": "ReplayWitnessProof", "description": "Evidentiary route layer. Preserves recurrence, observation, replay, witness-bearing continuity, and proof-bearing closure."},
    {"id": "L11", "symbol": "Λ11", "name": "SeedRegeneration", "description": "Compression and re-seeding layer. Preserves regeneration anchors, seed crystals, and save-state survivability."},
]

DIMENSIONAL_STRATA = [
    {"id": "D0", "name": "Planar routing stratum", "description": "Metro / mycelium / neural surface-level navigation."},
    {"id": "D1", "name": "Hinge / liminal stratum", "description": "Transfer, phase-shift, bridge approach, ambiguity mediation."},
    {"id": "D2", "name": "Pole stratum", "description": "Zero collapse and aether expansion."},
    {"id": "D3", "name": "Nonlocal transit stratum", "description": "Tunnels, lifts, crossings, nonlocal bridgework."},
    {"id": "D4", "name": "Evidentiary / regenerative stratum", "description": "Replay, witness, proof closure, seed preservation, regeneration."},
]

TOPOLOGY_SEED = {
    "Metro": ["Liminal", "BridgeReturn", "ReplayWitnessProof"],
    "Mycelium": ["Liminal", "Aether", "SeedRegeneration"],
    "Neural": ["Liminal", "ReplayWitnessProof", "Dimensional"],
    "Zero": ["Liminal", "Tunnel", "ReplayWitnessProof"],
    "Aether": ["Liminal", "Tunnel", "Dimensional", "SeedRegeneration"],
    "Liminal": ["Metro", "Mycelium", "Neural", "Zero", "Aether", "Tunnel", "BridgeReturn", "Dimensional"],
    "Tunnel": ["Zero", "Aether", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "BridgeReturn": ["Metro", "Liminal", "Dimensional", "ReplayWitnessProof"],
    "Dimensional": ["BridgeReturn", "Tunnel", "ReplayWitnessProof"],
    "ReplayWitnessProof": ["Zero", "BridgeReturn", "Neural", "SeedRegeneration"],
    "SeedRegeneration": ["Aether", "Mycelium", "ReplayWitnessProof"],
}

FRONTIER_MAP = [
    "exact counts of local zero points and local aether points",
    "exact metro station inventory",
    "exact mycelial branch multiplicity",
    "exact neural convergence multiplicity",
    "tunnel midspans / collapsed interiors",
    "exact pairing of entrances to exits",
    "whether a Möbius return hinge is seated now",
    "whether a proof anchor is seated now",
    "exact coordinates of seed crystals",
    "exact manifold crossing multiplicity",
    "exact witness/proof closures",
]

BRIDGES = [
    {"id": "B/TR", "name": "Transfer bridge", "description": "Connects distinct route families while preserving source and target identity."},
    {"id": "B/DH", "name": "Dimensional hinge", "description": "Supports lawful move between planar and nonlocal strata."},
    {"id": "B/MR", "name": "Mobius return hinge", "description": "Return-fold bridge; currently frontier until supported."},
    {"id": "B/WB", "name": "Witness bridge", "description": "Carries replay into witness-bearing structure."},
    {"id": "B/BC", "name": "Compression bridge", "description": "High compression-value bridge that collapses multiple local paths into one recoverable line."},
]

TUNNELS = [
    {"id": "T/ZC", "name": "Zero-collapse tunnel", "strongest": "q0 in {0,2}, q2 has IN, q3 in {0,2}", "entry": "zero-leaning node", "exit": "normalized or return-compatible node"},
    {"id": "T/AL", "name": "Aether-lift tunnel", "strongest": "q0 in {1,3}, q2 has ANTI, q3 in {1,3}", "entry": "liminal or post-zero node", "exit": "aether or lift-facing node"},
    {"id": "T/LS", "name": "Liminal-shortcut tunnel", "strongest": "q1 in {2,3}, q3 = 3", "entry": "liminal transfer", "exit": "nearby cross-family hub"},
    {"id": "T/DJ", "name": "Dimensional-jump tunnel", "strongest": "q1 = 3, q3 = 3", "entry": "bridge or tunnel gateway", "exit": "lift or crossing station"},
    {"id": "T/RR", "name": "Replay-return tunnel", "strongest": "q0 = 3, q1 in {1,3}", "entry": "replay anchor", "exit": "zero / return hinge / witness zone"},
    {"id": "T/BC", "name": "Bridge-compression tunnel", "strongest": "q3 in {0,3}", "entry": "high-centrality hub", "exit": "replay or bridge station"},
]

ROUTES = [
    {"id": "R1", "name": "Metro rail", "description": "Ordinary planar transit; optimizes transfer clarity.", "gate": {"q0": [0, 1], "q1": [0, 1], "q2": [0, 1], "q3": [0, 1]}},
    {"id": "R2", "name": "Mycelial filament", "description": "Branching spread; optimizes diffusion and branch discovery.", "gate": {"q0": [1, 2], "q1": [2, 3], "q2": [1, 2], "q3": [2, 3]}},
    {"id": "R3", "name": "Neural link", "description": "Convergence/divergence; optimizes associative recurrence.", "gate": {"q0": [1, 2, 3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "R4", "name": "Zero-collapse route", "description": "Normalization path into zero structures.", "gate": {"q0": [0, 2], "q1": [0, 1], "q2": [0, 1, 2], "q3": [0, 2]}},
    {"id": "R5", "name": "Liminal transition route", "description": "Mediated phase-shift path between distinct structural families.", "gate": {"q0": [0, 1, 2, 3], "q1": [1, 2, 3], "q2": [1, 2], "q3": [3]}},
    {"id": "R6", "name": "Aether expansion route", "description": "Reopening / lift / outward projection path.", "gate": {"q0": [1, 3], "q1": [0, 2], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "R7", "name": "Tunnel bypass route", "description": "Nonlocal shortcut that preserves entrance/exit legality.", "gate": {"q0": [0, 1, 2, 3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [3]}},
    {"id": "R8", "name": "Bridge / hinge route", "description": "Structural attachment, transfer, and return-line support.", "gate": {"q0": [0, 1, 3], "q1": [0, 1, 3], "q2": [0, 1, 2, 3], "q3": [0, 1, 3]}},
    {"id": "R9", "name": "Dimensional lift route", "description": "Vertical or non-planar transit into higher structural span.", "gate": {"q0": [1, 3], "q1": [1, 2, 3], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "R10", "name": "Manifold crossing route", "description": "Cross-sheet transit where distinct sections intersect lawfully.", "gate": {"q0": [2, 3], "q1": [3], "q2": [1, 2, 3], "q3": [3]}},
    {"id": "R11", "name": "Replay loop", "description": "Recurrence path used for return, verification, and memory.", "gate": {"q0": [3], "q1": [0, 1, 3], "q2": [1, 2, 3], "q3": [0, 3]}},
    {"id": "R12", "name": "Witness / proof-bearing route", "description": "Evidentiary path; supports witness and possible proof closure.", "gate": {"q0": [0, 3], "q1": [0, 2], "q2": [0, 1, 2], "q3": [0, 2, 3]}, "invariant": "replay support required"},
    {"id": "R13", "name": "Seed / regeneration route", "description": "Compression-safe route into seed crystals and regeneration.", "gate": {"q0": [1, 3], "q1": [2, 3], "q2": [1, 2, 3], "q3": [2, 3]}, "invariant": "aether or replay support required"},
]

ROW_DEFS = [
    {"id": "Z0", "title": "Global Zero Anchor", "status": "seated", "node_class": "zero anchor", "host_layers": ["Zero", "Liminal", "Tunnel", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R4", "R5", "R7", "R8", "R9", "R11"], "span": 4, "polarity": "Z++", "related_hubs": ["L0", "TE", "DB", "RA"], "touching_tunnels": ["T/ZC", "T/RR", "T/BC"], "hidden_neighbors": ["C1", "C3"], "strata": ["D1", "D2", "D3", "D4"], "exposure": {"q0": [0, 2], "q1": [0, 1], "q2": [0, 1, 2], "q3": [0, 2, 3]}},
    {"id": "ZL", "title": "Local Zero Point", "status": "seated", "node_class": "local zero point", "host_layers": ["Zero", "Liminal", "Tunnel"], "incident_routes": ["R4", "R5", "R7"], "span": 3, "polarity": "Z+", "related_hubs": ["L0", "TE", "Z0"], "touching_tunnels": ["T/ZC"], "hidden_neighbors": ["C1", "C6"], "strata": ["D1", "D2", "D3"], "exposure": {"q0": [0, 2], "q1": [0, 2], "q2": [0, 1, 2], "q3": [0, 2]}},
    {"id": "A0", "title": "Primary Aether Point", "status": "seated", "node_class": "aether point", "host_layers": ["Aether", "Liminal", "Tunnel", "Dimensional", "SeedRegeneration"], "incident_routes": ["R5", "R6", "R7", "R8", "R9"], "span": 4, "polarity": "A++", "related_hubs": ["L0", "TX", "DL", "SC"], "touching_tunnels": ["T/AL", "T/DJ"], "hidden_neighbors": ["C1", "C5"], "strata": ["D1", "D2", "D3", "D4"], "exposure": {"q0": [1, 3], "q1": [0, 2], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "L0", "title": "Liminal Transfer Point", "status": "seated", "node_class": "liminal transfer hinge", "host_layers": ["Liminal", "Zero", "Aether", "Tunnel", "BridgeReturn", "Dimensional"], "incident_routes": ["R4", "R5", "R6", "R7", "R8", "R9", "R10"], "span": 4, "polarity": "balanced mediator", "related_hubs": ["Z0", "A0", "MS", "DB"], "touching_tunnels": ["T/LS", "T/ZC", "T/AL", "T/DJ"], "hidden_neighbors": ["C1", "C2", "C3", "C6"], "strata": ["D0", "D1", "D2", "D3"], "exposure": {"q0": [0, 1, 2, 3], "q1": [1, 2, 3], "q2": [1, 2], "q3": [3]}},
    {"id": "MT", "title": "Metro Transfer Hub", "status": "seated", "node_class": "metro transfer hub", "host_layers": ["Metro", "Liminal", "BridgeReturn", "ReplayWitnessProof"], "incident_routes": ["R1", "R5", "R8", "R11"], "span": 3, "polarity": "neutral", "related_hubs": ["MS", "L0", "RA"], "touching_tunnels": ["T/LS", "T/BC"], "hidden_neighbors": ["C2"], "strata": ["D0", "D1", "D4"], "exposure": {"q0": [0, 1, 3], "q1": [0, 1], "q2": [0, 1], "q3": [0, 1]}},
    {"id": "MS", "title": "Master Transfer Station", "status": "seated", "node_class": "cross-family master interchange", "host_layers": ["Metro", "Mycelium", "Neural", "Liminal", "BridgeReturn", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R1", "R2", "R3", "R5", "R8", "R9", "R11"], "span": 4, "polarity": "neutral structural hinge", "related_hubs": ["MT", "MY", "NN", "DB"], "touching_tunnels": ["T/LS", "T/BC", "T/DJ"], "hidden_neighbors": ["C2", "C3"], "strata": ["D0", "D1", "D3", "D4"], "exposure": {"q0": [0, 1, 2, 3], "q1": [0, 1, 2], "q2": [0, 1, 2], "q3": [0, 3]}},
    {"id": "MY", "title": "Mycelium Branch Hub", "status": "seated", "node_class": "mycelial branching hub", "host_layers": ["Mycelium", "Liminal", "Aether", "SeedRegeneration"], "incident_routes": ["R2", "R5", "R6", "R7", "R13"], "span": 4, "polarity": "A+", "related_hubs": ["MS", "A0", "SC", "L0"], "touching_tunnels": ["T/LS", "T/AL"], "hidden_neighbors": ["C2", "C5", "C6"], "strata": ["D0", "D1", "D2", "D4"], "exposure": {"q0": [1, 2], "q1": [2, 3], "q2": [1, 2], "q3": [2, 3]}},
    {"id": "NN", "title": "Neural Convergence Hub", "status": "seated", "node_class": "neural convergence hub", "host_layers": ["Neural", "Liminal", "Aether", "Dimensional", "ReplayWitnessProof"], "incident_routes": ["R3", "R5", "R6", "R7", "R10", "R12"], "span": 5, "polarity": "balanced-liminal", "related_hubs": ["MS", "MC", "WA", "L0"], "touching_tunnels": ["T/LS", "T/DJ"], "hidden_neighbors": ["C2", "C4", "C6"], "strata": ["D0", "D1", "D2", "D3", "D4"], "exposure": {"q0": [1, 2, 3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "TE", "title": "Tunnel Entrance", "status": "seated", "node_class": "tunnel entrance", "host_layers": ["Tunnel", "Zero", "Liminal", "BridgeReturn"], "incident_routes": ["R4", "R5", "R7", "R8"], "span": 3, "polarity": "Z+ entry", "related_hubs": ["Z0", "L0", "DB"], "touching_tunnels": ["T/ZC", "T/LS", "T/DJ"], "hidden_neighbors": ["C1", "C3"], "strata": ["D1", "D2", "D3"], "exposure": {"q0": [0, 2], "q1": [1, 3], "q2": [0, 1, 2], "q3": [3]}},
    {"id": "TX", "title": "Tunnel Exit", "status": "seated", "node_class": "tunnel exit", "host_layers": ["Tunnel", "Aether", "Liminal", "BridgeReturn"], "incident_routes": ["R5", "R6", "R7", "R8"], "span": 3, "polarity": "A+ release", "related_hubs": ["A0", "L0", "DL"], "touching_tunnels": ["T/AL", "T/LS", "T/DJ"], "hidden_neighbors": ["C1", "C3"], "strata": ["D1", "D2", "D3"], "exposure": {"q0": [1, 3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [3]}},
    {"id": "DB", "title": "Dimensional Bridge Station", "status": "seated", "node_class": "dimensional bridge station", "host_layers": ["BridgeReturn", "Liminal", "Dimensional", "Tunnel"], "incident_routes": ["R5", "R7", "R8", "R9", "R10"], "span": 3, "polarity": "balanced", "related_hubs": ["L0", "MS", "MC", "TE", "TX"], "touching_tunnels": ["T/DJ", "T/BC"], "hidden_neighbors": ["C1", "C3"], "strata": ["D1", "D3", "D4"], "exposure": {"q0": [1, 2, 3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "DL", "title": "Dimensional Lift", "status": "seated", "node_class": "dimensional lift station", "host_layers": ["Dimensional", "Aether", "Tunnel"], "incident_routes": ["R6", "R7", "R9", "R10"], "span": 2, "polarity": "A+", "related_hubs": ["A0", "DB", "MC", "TX"], "touching_tunnels": ["T/AL", "T/DJ"], "hidden_neighbors": ["C1", "C3"], "strata": ["D2", "D3"], "exposure": {"q0": [1, 3], "q1": [1, 2, 3], "q2": [1, 2, 3], "q3": [1, 3]}},
    {"id": "MC", "title": "Manifold Crossing", "status": "seated", "node_class": "manifold crossing station", "host_layers": ["Dimensional", "BridgeReturn", "Neural", "ReplayWitnessProof"], "incident_routes": ["R7", "R8", "R9", "R10", "R12"], "span": 3, "polarity": "balanced-opposed", "related_hubs": ["DB", "DL", "NN", "WA"], "touching_tunnels": ["T/DJ", "T/BC"], "hidden_neighbors": ["C3", "C4"], "strata": ["D0", "D3", "D4"], "exposure": {"q0": [2, 3], "q1": [3], "q2": [1, 2, 3], "q3": [3]}},
    {"id": "RA", "title": "Replay Anchor", "status": "seated", "node_class": "replay anchor", "host_layers": ["ReplayWitnessProof", "BridgeReturn", "SeedRegeneration"], "incident_routes": ["R8", "R11", "R12", "R13"], "span": 3, "polarity": "Z-return bias", "related_hubs": ["MR", "WA", "SC", "MT"], "touching_tunnels": ["T/RR", "T/BC"], "hidden_neighbors": ["C4", "C5"], "strata": ["D1", "D3", "D4"], "exposure": {"q0": [3], "q1": [0, 1, 3], "q2": [1, 2, 3], "q3": [0, 3]}},
    {"id": "WA", "title": "Witness Anchor", "status": "seated", "node_class": "witness anchor", "host_layers": ["ReplayWitnessProof", "Neural"], "incident_routes": ["R5", "R11", "R12"], "span": 2, "polarity": "Z-stabilized", "related_hubs": ["RA", "NN", "PA"], "touching_tunnels": ["T/RR"], "hidden_neighbors": ["C4"], "strata": ["D0", "D4"], "exposure": {"q0": [0, 3], "q1": [0, 2], "q2": [0, 1, 2], "q3": [0, 2, 3]}},
    {"id": "SC", "title": "Seed Crystal", "status": "seated", "node_class": "seed crystal / regeneration anchor", "host_layers": ["SeedRegeneration", "Aether", "Mycelium", "ReplayWitnessProof"], "incident_routes": ["R6", "R11", "R12", "R13"], "span": 3, "polarity": "A-seeded", "related_hubs": ["A0", "MY", "RA"], "touching_tunnels": ["T/AL", "T/RR"], "hidden_neighbors": ["C5"], "strata": ["D0", "D2", "D4"], "exposure": {"q0": [1, 3], "q1": [2, 3], "q2": [1, 2, 3], "q3": [2, 3]}},
    {"id": "MR", "title": "Mobius Return Hinge", "status": "frontier", "node_class": "return hinge / Mobius hinge", "host_layers": ["BridgeReturn", "ReplayWitnessProof", "Zero"], "incident_routes": ["R4", "R7", "R8", "R11"], "span": 3, "polarity": "cyclic return", "related_hubs": ["RA", "Z0", "DB"], "touching_tunnels": ["T/RR", "T/ZC"], "hidden_neighbors": ["C4"], "strata": ["D1", "D2", "D4"], "exposure": {"q0": [3], "q1": [1, 3], "q2": [1, 2, 3], "q3": [0, 3]}},
    {"id": "PA", "title": "Proof Anchor", "status": "frontier", "node_class": "proof anchor", "host_layers": ["ReplayWitnessProof", "BridgeReturn"], "incident_routes": ["R8", "R11", "R12"], "span": 2, "polarity": "Z-stabilized evidentiary closure", "related_hubs": ["WA", "RA", "MR"], "touching_tunnels": [], "hidden_neighbors": ["C4"], "strata": ["D1", "D4"], "exposure": {"q0": [3], "q1": [0, 2], "q2": [0, 1, 2], "q3": [0, 3]}},
    {"id": "LP", "title": "Latent Pressure Hub", "status": "inferred", "node_class": "unresolved but pressure-bearing nexus", "host_layers": ["Liminal", "BridgeReturn", "Dimensional"], "incident_routes": ["R5", "R7", "R8", "R9", "R10"], "span": 3, "polarity": "unresolved", "related_hubs": ["L0", "DB", "MC", "MS"], "touching_tunnels": ["T/LS", "T/DJ", "T/BC"], "hidden_neighbors": [], "strata": ["D1", "D3", "D4"], "exposure": {"q0": [1, 2, 3], "q1": [2, 3], "q2": [1, 2, 3], "q3": [3]}},
]

MASTER_KEYS = [
    {"id": "K0", "coords": [0, 0, 0, 0], "byte": 0, "signature": "SEAT / TOG-SAME / IN-IN / WALL", "use": "baseline seating, zero normalization, metro/witness stabilization"},
    {"id": "K1", "coords": [0, 1, 1, 3], "byte": 212, "signature": "SEAT / TOG-OPP / IN-ANTI / MIX", "use": "first hidden-tunnel and liminal fracture probe"},
    {"id": "K2", "coords": [1, 0, 1, 1], "byte": 81, "signature": "ADVANCE / TOG-SAME / IN-ANTI / WHEEL", "use": "coherent aether lift, dimensional opening, seed approach"},
    {"id": "K3", "coords": [1, 2, 1, 3], "byte": 217, "signature": "ADVANCE / SPLIT-SAME / IN-ANTI / MIX", "use": "mycelial branching and hidden transfer scan"},
    {"id": "K4", "coords": [2, 1, 2, 2], "byte": 166, "signature": "CROSS / TOG-OPP / ANTI-IN / FLOOR", "use": "counterphase floor cut, branch-convergence triangulation"},
    {"id": "K5", "coords": [2, 3, 1, 3], "byte": 222, "signature": "CROSS / SPLIT-OPP / IN-ANTI / MIX", "use": "manifold crossing, dimensional jump, latent hub pressure"},
    {"id": "K6", "coords": [3, 0, 3, 0], "byte": 51, "signature": "RETURN / TOG-SAME / ANTI-ANTI / WALL", "use": "replay closure, witness verification, proof-pressure check"},
    {"id": "K7", "coords": [3, 1, 3, 3], "byte": 247, "signature": "RETURN / TOG-OPP / ANTI-ANTI / MIX", "use": "Mobius-return test, contradiction resolution, replay tunnel scan"},
    {"id": "K8", "coords": [3, 2, 2, 3], "byte": 235, "signature": "RETURN / SPLIT-SAME / ANTI-IN / MIX", "use": "seed recovery and regeneration coupling"},
    {"id": "K9", "coords": [3, 3, 3, 3], "byte": 255, "signature": "RETURN / SPLIT-OPP / ANTI-ANTI / MIX", "use": "maximal frontier excavation and hidden-pressure saturation"},
]

PHRASE_MACROS = [
    {"id": "PHI_hidden", "bytes": [0, 212, 217, 222, 255, 247, 51], "purpose": "seat -> fracture -> branch -> crossing -> saturate hidden pressure -> return -> verify"},
    {"id": "PHI_regen", "bytes": [0, 81, 235, 247, 51], "purpose": "seat -> lift -> recover seed -> test return -> verify closure"},
    {"id": "PHI_transfer", "bytes": [0, 166, 217, 212], "purpose": "baseline seat -> counterphase floor cut -> split branch scan -> hidden liminal probe"},
]

HIDDEN_CANDIDATES = [
    {"id": "C1", "name": "Zero-Aether Mediating Lift Hub", "evidence_states": [212, 166, 222, 247, 255], "adjacent_rows": ["Z0", "L0", "A0", "TE", "TX"], "route_support": ["R4", "R5", "R6", "R7", "R9"], "confidence": "medium-high", "disposition": "frontier"},
    {"id": "C2", "name": "Metro-Mycelium-Neural Composite Transfer Node", "evidence_states": [217, 166, 212], "adjacent_rows": ["MT", "MS", "MY", "NN", "L0"], "route_support": ["R1", "R2", "R3", "R5", "R8", "R9"], "confidence": "high structural", "disposition": "frontier"},
    {"id": "C3", "name": "Dimensional Midspan Bridge", "evidence_states": [222, 247, 255], "adjacent_rows": ["DB", "DL", "MC", "TE", "TX"], "route_support": ["R7", "R8", "R9", "R10"], "confidence": "high structural", "disposition": "frontier"},
    {"id": "C4", "name": "Replay-Proof Closure Junction", "evidence_states": [51, 247, 255], "adjacent_rows": ["RA", "WA", "MR", "PA"], "route_support": ["R8", "R11", "R12"], "confidence": "medium", "disposition": "frontier"},
    {"id": "C5", "name": "Seed-Replay Regeneration Coupler", "evidence_states": [81, 235, 247], "adjacent_rows": ["SC", "A0", "RA", "MY"], "route_support": ["R6", "R11", "R13"], "confidence": "medium", "disposition": "frontier"},
    {"id": "C6", "name": "Frontier Liminal Distributor", "evidence_states": [], "adjacent_rows": ["L0", "ZL", "A0", "MS"], "route_support": ["R5", "R7", "R8", "R9", "R10"], "confidence": "low-medium", "disposition": "frontier"},
]
ASTRO_LANE_BUNDLES = {
    "western_solar12": ["MT", "L0", "Z0", "WA"],
    "planetary_office": ["MT", "MS", "RA", "PA"],
    "chinese_cycle": ["MY", "L0", "ZL", "SC"],
    "vedic_lunar": ["NN", "RA", "WA", "PA"],
    "mayan_calendar": ["MY", "SC", "A0", "RA"],
    "decan_office": ["TE", "DB", "TX", "MR"],
    "egyptian_kheper": ["Z0", "RA", "MR", "PA"],
    "norse_rune_yggdrasil": ["DB", "DL", "MC", "LP"],
}

AP6D_BRIDGE_SPAN_ROWS = {
    "3D->4D": ["TE", "L0", "ZL"],
    "4D->5D": ["Z0", "DB", "MR"],
    "5D->6D": ["MS", "NN", "MC"],
    "6D->7D": ["A0", "SC", "RA"],
}

# Override the mnemonic with explicit Unicode escapes so downstream witnesses stay stable.
SEED_STRING = "ATH-HSIGMA::11\u039b/16S+2F+1I/13R/6T/5D/256\u03a8/4864M/\u03bcFIX"


def local_now() -> datetime:
    return datetime.now(TIMEZONE)


def docs_gate() -> str:
    return "BLOCKED" if not CREDENTIALS_PATH.exists() or not TOKEN_PATH.exists() else "OPEN"


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def row_lookup() -> dict[str, dict[str, object]]:
    return {row["id"]: row for row in ROW_DEFS}


def route_lookup() -> dict[str, dict[str, object]]:
    return {route["id"]: route for route in ROUTES}


def encode_byte(q0: int, q1: int, q2: int, q3: int) -> int:
    return q0 + 4 * q1 + 16 * q2 + 64 * q3


def decode_byte(byte: int) -> dict[str, int]:
    return {
        "q0": byte % 4,
        "q1": (byte // 4) % 4,
        "q2": (byte // 16) % 4,
        "q3": (byte // 64) % 4,
    }


def axis_neighbors(byte: int) -> list[int]:
    coords = decode_byte(byte)
    neighbors = []
    for key in ("q0", "q1", "q2", "q3"):
        for delta in (-1, 1):
            updated = dict(coords)
            updated[key] = (updated[key] + delta) % 4
            neighbors.append(encode_byte(updated["q0"], updated["q1"], updated["q2"], updated["q3"]))
    return sorted(set(neighbors))


def surrogate_coords(now: datetime) -> dict[str, int]:
    return {
        "q0": now.hour // 6,
        "q1": now.weekday() % 4,
        "q2": now.minute // 15,
        "q3": now.timetuple().tm_yday % 4,
    }


def route_gate_score(route_id: str, byte: int) -> float:
    coords = decode_byte(byte)
    gate = route_lookup()[route_id]["gate"]
    hits = sum(1 for key in ("q0", "q1", "q2", "q3") if coords[key] in gate[key])
    return hits / 4.0


def exposure_score(row_id: str, byte: int) -> float:
    coords = decode_byte(byte)
    gate = row_lookup()[row_id]["exposure"]
    hits = sum(1 for key in ("q0", "q1", "q2", "q3") if coords[key] in gate[key])
    return hits / 4.0


def tunnel_activation(byte: int, active_routes: set[str]) -> set[str]:
    coords = decode_byte(byte)
    active = set()
    if "R4" in active_routes and coords["q0"] in {0, 2} and coords["q3"] in {0, 2} and coords["q2"] in {0, 1, 2}:
        active.add("T/ZC")
    if "R6" in active_routes and coords["q0"] in {1, 3} and coords["q3"] in {1, 3} and coords["q2"] in {1, 2, 3}:
        active.add("T/AL")
    if {"R5", "R7"} & active_routes and coords["q1"] in {2, 3} and coords["q3"] == 3:
        active.add("T/LS")
    if {"R8", "R9", "R10"} & active_routes and coords["q1"] == 3 and coords["q3"] == 3:
        active.add("T/DJ")
    if "R11" in active_routes and coords["q0"] == 3 and coords["q1"] in {1, 3}:
        active.add("T/RR")
    if "R8" in active_routes and coords["q3"] in {0, 3}:
        active.add("T/BC")
    return active


def reachable_rows(start_row_id: str, byte: int) -> tuple[list[str], set[str], set[str], set[str]]:
    if exposure_score(start_row_id, byte) < 0.5:
        return [], set(), set(), set()
    routes_by_row = {
        row["id"]: {route_id for route_id in row["incident_routes"] if route_gate_score(route_id, byte) >= 0.5}
        for row in ROW_DEFS
    }
    visible_rows = {row["id"] for row in ROW_DEFS if exposure_score(row["id"], byte) >= 0.5}
    queue = [start_row_id]
    seen: set[str] = set()
    reached_routes: set[str] = set()
    reached_layers: set[str] = set()
    reached_strata: set[str] = set()
    while queue:
        current = queue.pop(0)
        if current in seen or current not in visible_rows:
            continue
        seen.add(current)
        row = row_lookup()[current]
        reached_routes.update(routes_by_row[current])
        reached_layers.update(row["host_layers"])
        reached_strata.update(row["strata"])
        for other in ROW_DEFS:
            other_id = other["id"]
            if other_id in seen or other_id not in visible_rows:
                continue
            if routes_by_row[current] & routes_by_row[other_id]:
                queue.append(other_id)
    return sorted(seen), reached_routes, reached_layers, reached_strata


def replay_value(reach: set[str]) -> float:
    score = 0.0
    if "RA" in reach:
        score += 1.0
    if "WA" in reach:
        score += 1.0
    if "PA" in reach:
        score += 0.5
    if "SC" in reach:
        score += 1.0
    return score / 3.5


def hidden_pressure_components(row_id: str, byte: int, reach: set[str], active_routes: set[str]) -> dict[str, float]:
    cross = 1.0 if "R10" in active_routes and "MC" not in reach else 0.0
    tunnel = 1.0 if "R7" in active_routes and (("TE" in reach) != ("TX" in reach)) else 0.5 if "R7" in active_routes else 0.0
    pole = 1.0 if {"Z0", "A0"} <= reach and "L0" not in reach else 0.0
    replay = 1.0 if "R11" in active_routes and "RA" in reach and ("MR" not in reach or "PA" not in reach) else 0.0
    transfer = 1.0 if len({"MT", "MY", "NN"} & reach) >= 2 and "MS" not in reach else 0.0
    if row_id == "LP" and decode_byte(byte)["q3"] == 3:
        transfer = max(transfer, 1.0)
    return {
        "u_cross": cross,
        "u_tunnel": tunnel,
        "u_pole": pole,
        "u_replay": replay,
        "u_transfer": transfer,
    }


def contradiction_components(reach: set[str], active_routes: set[str]) -> dict[str, int]:
    pole = int({"Z0", "A0"} <= reach and not ({"L0", "DB"} & reach))
    tunnel = int("R7" in active_routes and not ({"TE", "TX"} <= reach))
    dimensional = int(bool({"R9", "R10"} & active_routes) and not bool({"DB", "DL", "MC"} & reach))
    replay = int("R11" in active_routes and not bool({"RA", "WA", "MR", "PA"} & reach))
    return {"v_pole": pole, "v_tunnel": tunnel, "v_dim": dimensional, "v_replay": replay}


def cell_visibility(status: str, exposure: float) -> str:
    if exposure >= 0.5 and status in {"seated", "frontier"}:
        return "explicit"
    if exposure >= 0.25:
        return "implied"
    return "absent"


def aggregate_class(classes: list[str]) -> str:
    for name in CLASS_PRECEDENCE:
        if name in classes:
            return name
    return "degenerate"


def build_cells() -> dict[str, object]:
    row_stats: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in ROW_DEFS:
        degree = len(row["incident_routes"])
        centrality = degree / 7.0
        row["schematic_degree"] = degree
        row["centrality_prior"] = centrality
        row["w0"] = round(100 * (0.6 * centrality + 0.4 * (row["span"] / 5.0)))
    for candidate in HIDDEN_CANDIDATES:
        if candidate["id"] == "C6":
            candidate["evidence_states"] = [
                byte
                for byte in range(256)
                if decode_byte(byte)["q1"] in {2, 3} and decode_byte(byte)["q3"] == 3
            ]
    for byte in range(256):
        for row in ROW_DEFS:
            reach_list, reached_routes, reached_layers, reached_strata = reachable_rows(row["id"], byte)
            reach = set(reach_list)
            active_incident_routes = {route_id for route_id in row["incident_routes"] if route_gate_score(route_id, byte) >= 0.5}
            active_tunnels = tunnel_activation(byte, reached_routes)
            radius_two_layers = set(row["host_layers"])
            for related in row["related_hubs"]:
                radius_two_layers.update(row_lookup().get(related, {}).get("host_layers", []))
            compression = min(len(radius_two_layers) / max(1, len(reached_layers)), 1.0) if reached_layers else 0.0
            replay_component = replay_value(reach)
            hidden_parts = hidden_pressure_components(row["id"], byte, reach, reached_routes)
            contradiction_parts = contradiction_components(reach, reached_routes)
            frontier_count = sum(1 for reached_id in reach if row_lookup()[reached_id]["status"] != "seated")
            base_weight = (
                20 * row["centrality_prior"]
                + 20 * (len(reach) / 18.0)
                + 15 * (len(active_tunnels) / 6.0)
                + 15 * (len(reached_strata) / 5.0)
                + 10 * compression
                + 10 * replay_component
            )
            row_stats[row["id"]].append(
                {
                    "row_id": row["id"],
                    "byte": byte,
                    "coords": decode_byte(byte),
                    "exposure": round(exposure_score(row["id"], byte), 3),
                    "weight_base": round(base_weight, 3),
                    "reachable_rows": reach_list,
                    "active_routes": sorted(active_incident_routes),
                    "reached_routes": sorted(reached_routes),
                    "active_tunnels": sorted(active_tunnels),
                    "reached_layers": sorted(reached_layers),
                    "reached_strata": sorted(reached_strata),
                    "replay_component": round(replay_component, 3),
                    "compression_value": round(compression, 3),
                    "hidden_components": hidden_parts,
                    "contradiction_components": contradiction_parts,
                    "frontier_fraction": round(frontier_count / max(1, len(reach)), 3),
                    "route_density": round(len(active_incident_routes) / max(1, len(row["incident_routes"])), 3),
                    "exposed_nexus_count": len(reach),
                }
            )
    candidate_support = {}
    for row_id, cells in row_stats.items():
        counts = [cell["exposed_nexus_count"] for cell in cells]
        mean_count = mean(counts)
        std_count = pstdev(counts)
        for cell in cells:
            shared = set(cell["reachable_rows"])
            for neighbor in axis_neighbors(cell["byte"]):
                shared &= set(row_stats[row_id][neighbor]["reachable_rows"])
            novel = len(set(cell["reachable_rows"]) - shared) / 18.0
            hidden_pressure = sum(cell["hidden_components"].values()) / 5.0
            contradiction = sum(cell["contradiction_components"].values()) / 4.0
            weights = [row_stats[row_id][neighbor]["weight_base"] for neighbor in axis_neighbors(cell["byte"])]
            instability = (max(weights) - min(weights)) / 100.0 if weights else 0.0
            cell["novel_nexus_exposure"] = round(novel, 3)
            cell["hidden_pressure"] = round(hidden_pressure, 3)
            cell["contradiction"] = round(contradiction, 3)
            cell["weight"] = round(min(100.0, cell["weight_base"] + 10 * novel), 3)
            cell["visibility"] = cell_visibility(row_lookup()[row_id]["status"], cell["exposure"])
            cell["instability"] = round(instability, 3)
            aligned_layers = len(cell["reached_layers"])
            if cell["contradiction"] >= 0.4:
                cell["class"] = "contradictory"
            elif cell["weight"] >= 80 and aligned_layers >= 4 and cell["contradiction"] < 0.25 and cell["exposed_nexus_count"] >= mean_count + std_count:
                cell["class"] = "master-key"
            elif cell["hidden_pressure"] >= 0.45 and cell["contradiction"] < 0.4:
                cell["class"] = "hidden-pressure"
            elif cell["frontier_fraction"] > 0.5 and cell["contradiction"] < 0.4:
                cell["class"] = "frontier"
            elif cell["instability"] >= 0.25 and cell["contradiction"] < 0.4:
                cell["class"] = "unstable"
            elif cell["weight"] >= 70 and cell["hidden_pressure"] < 0.30 and cell["contradiction"] < 0.25:
                cell["class"] = "seated"
            elif 55 <= cell["weight"] < 70 and cell["contradiction"] < 0.4:
                cell["class"] = "promising"
            else:
                cell["class"] = "degenerate"
    for candidate in HIDDEN_CANDIDATES:
        states = candidate["evidence_states"]
        samples = [
            row_stats[row_id][state]
            for row_id in candidate["adjacent_rows"]
            if row_id in row_stats
            for state in states
            if state < len(row_stats[row_id])
        ]
        hidden_avg = round(mean(item["hidden_pressure"] for item in samples), 3) if samples else 0.0
        contradiction_avg = round(mean(item["contradiction"] for item in samples), 3) if samples else 0.0
        candidate_support[candidate["id"]] = {
            "state_count": len(states),
            "route_family_count": len(candidate["route_support"]),
            "hidden_pressure_avg": hidden_avg,
            "contradiction_avg": contradiction_avg,
            "promotion_threshold_met": len(states) >= 4 and len(candidate["route_support"]) >= 2 and hidden_avg > 0.55 and contradiction_avg < 0.25,
            "seated_threshold_met": len(states) >= 8 and len(candidate["route_support"]) >= 3 and hidden_avg > 0.55 and contradiction_avg < 0.25,
            "fixed_point_passes": 2,
            "promoted": False,
        }
    return {"cells_by_row": row_stats, "candidate_support": candidate_support}


def current_state(cells_by_row: dict[str, list[dict[str, object]]], now: datetime) -> dict[str, object]:
    coords = surrogate_coords(now)
    byte = encode_byte(coords["q0"], coords["q1"], coords["q2"], coords["q3"])
    rows = {row_id: dict(cells[byte]) for row_id, cells in cells_by_row.items()}
    top_rows = sorted(rows.values(), key=lambda item: (-item["weight"], CLASS_PRECEDENCE.index(item["class"])))
    top_master_keys = [item["row_id"] for item in top_rows if item["class"] == "master-key"][:10]
    if not top_master_keys:
        top_master_keys = [item["row_id"] for item in top_rows[:5]]
    return {
        "byte": byte,
        "coords": coords,
        "neighbors": axis_neighbors(byte),
        "rows": rows,
        "top_master_keys": top_master_keys,
        "frontier_rows": [row_id for row_id, cell in rows.items() if cell["class"] == "frontier"],
        "hidden_pressure_rows": [row_id for row_id, cell in rows.items() if cell["class"] == "hidden-pressure"],
    }


def aggregate_bundle_state(save_state: dict[str, object], row_ids: list[str]) -> dict[str, object]:
    row_state_map = save_state["current_state"]["rows"]
    selected = [row_state_map[row_id] for row_id in row_ids]
    strata = sorted({stratum for row_id in row_ids for stratum in row_lookup()[row_id]["strata"]})
    return {
        "row_ids": row_ids,
        "byte": save_state["current_state"]["byte"],
        "weight": round(mean(item["weight"] for item in selected), 3),
        "hidden_pressure": round(mean(item["hidden_pressure"] for item in selected), 3),
        "cell_class": aggregate_class([item["class"] for item in selected]),
        "contradictory": any(item["class"] == "contradictory" for item in selected),
        "strata": strata,
        "restart_seed": save_state["regeneration_seed"]["mnemonic"],
    }


def build_bundle(now: datetime | None = None) -> dict[str, object]:
    now = now or local_now()
    cells = build_cells()
    current = current_state(cells["cells_by_row"], now)
    manifest = {
        "generated_at": now.isoformat(),
        "generated_at_utc": now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "timezone": "America/Los_Angeles",
        "docs_gate": docs_gate(),
        "symbolic_name": "HSigma",
        "visibility_mode": "class-exhaustive / instance-frontier",
        "counts": {"layers": 11, "routes": 13, "tunnels": 6, "strata": 5, "nexus_rows": 19, "seated_rows": 16, "frontier_rows": 2, "inferred_rows": 1, "timing_states": 256, "mindsweeper_cells": 4864},
        "contracts": {
            "HSigmaManifest": ["metadata", "counts", "layers", "dimensional_strata", "topology_seed", "frontier_map", "routes", "bridges", "tunnels", "nexus_rows", "timing_engine", "route_gate_book", "nexus_exposure_book", "master_keys", "phrase_macros", "mindsweeper", "hidden_candidates", "frontier_policy", "save_state"],
            "HSigmaCell": ["row_id", "byte", "coords", "weight", "visibility", "hidden_pressure", "contradiction", "frontier_fraction", "route_density", "exposed_nexus_count", "exposed_tunnel_count", "instability", "class", "active_routes", "reached_strata", "reachable_rows"],
            "HSigmaSaveState": ["current_state", "top_master_keys", "frontier_rows", "hidden_candidates", "regeneration_seed"],
        },
        "layers": LAYERS,
        "dimensional_strata": DIMENSIONAL_STRATA,
        "topology_seed": TOPOLOGY_SEED,
        "frontier_map": FRONTIER_MAP,
        "routes": ROUTES,
        "bridges": BRIDGES,
        "tunnels": TUNNELS,
        "nexus_rows": ROW_DEFS,
        "timing_engine": {
            "space": "Z4^4",
            "byte_formula": "B = q0 + 4q1 + 16q2 + 64q3",
            "neighborhood": "toroidal axis-neighbors only",
            "current_surrogate_formula": {"q0": "floor(local_hour / 6)", "q1": "weekday mod 4", "q2": "floor(minute / 15)", "q3": "day_of_year mod 4"},
            "current_byte": current["byte"],
            "current_coords": current["coords"],
            "current_neighbors": current["neighbors"],
        },
        "route_gate_book": {route["id"]: route["gate"] for route in ROUTES},
        "nexus_exposure_book": {row["id"]: row["exposure"] for row in ROW_DEFS},
        "master_keys": MASTER_KEYS,
        "phrase_macros": PHRASE_MACROS,
        "mindsweeper": {"rows": 19, "cols": 256, "cells": 4864, "current_byte": current["byte"], "current_top_rows": current["top_master_keys"]},
        "hidden_candidates": [{**candidate, "support": cells["candidate_support"][candidate["id"]]} for candidate in HIDDEN_CANDIDATES],
        "frontier_policy": FRONTIER_POLICY,
    }
    mindsweeper = {
        "generated_at": manifest["generated_at"],
        "docs_gate": manifest["docs_gate"],
        "contract": "HSigmaCell",
        "dimensions": {"rows": 19, "cols": 256, "cells": 4864},
        "rows": [
            {
                "row_id": row_id,
                "status": row_lookup()[row_id]["status"],
                "cells": [
                    {
                        "row_id": cell["row_id"],
                        "byte": cell["byte"],
                        "coords": cell["coords"],
                        "weight": cell["weight"],
                        "visibility": cell["visibility"],
                        "hidden_pressure": cell["hidden_pressure"],
                        "contradiction": cell["contradiction"],
                        "frontier_fraction": cell["frontier_fraction"],
                        "route_density": cell["route_density"],
                        "exposed_nexus_count": cell["exposed_nexus_count"],
                        "exposed_tunnel_count": len(cell["active_tunnels"]),
                        "instability": cell["instability"],
                        "class": cell["class"],
                        "active_routes": cell["active_routes"],
                        "reached_strata": cell["reached_strata"],
                        "reachable_rows": cell["reachable_rows"],
                    }
                    for cell in row_cells
                ],
            }
            for row_id, row_cells in sorted(cells["cells_by_row"].items())
        ],
    }
    save_state = {
        "generated_at": manifest["generated_at"],
        "generated_at_utc": manifest["generated_at_utc"],
        "timezone": manifest["timezone"],
        "docs_gate": manifest["docs_gate"],
        "symbolic_name": "HSigmaStar",
        "visibility_mode": manifest["visibility_mode"],
        "counts": manifest["counts"],
        "layers": [layer["name"] for layer in LAYERS],
        "explicit_nexus_rows": [row["id"] for row in ROW_DEFS if row["status"] == "seated"],
        "frontier_nexus_rows": [row["id"] for row in ROW_DEFS if row["status"] == "frontier"],
        "inferred_nexus_rows": [row["id"] for row in ROW_DEFS if row["status"] == "inferred"],
        "route_families": [route["id"] for route in ROUTES],
        "tunnel_classes": [tunnel["id"] for tunnel in TUNNELS],
        "dimensional_strata": [stratum["id"] for stratum in DIMENSIONAL_STRATA],
        "timing_engine": manifest["timing_engine"],
        "current_state": current,
        "top_master_key_rows": current["top_master_keys"],
        "frontier_rows": current["frontier_rows"],
        "hidden_candidates": [{"id": candidate["id"], "name": candidate["name"], "support": cells["candidate_support"][candidate["id"]], "disposition": candidate["disposition"]} for candidate in HIDDEN_CANDIDATES],
        "regeneration_seed": {"mnemonic": SEED_STRING, "operators": ["layers", "nexus_rows", "incidence", "dimensional_strata", "timing_lattice", "route_gate_book", "nexus_exposure_book", "weight_function", "mindsweeper_schema", "hidden_inference", "fixed_point", "frontier_policy"], "frontier_policy": FRONTIER_POLICY},
        "artifact_paths": {"manifest": str(HSIGMA_MANIFEST_PATH), "mindsweeper": str(HSIGMA_MINDSWEEPER_PATH), "save_state": str(HSIGMA_SAVE_STATE_PATH), "witness": str(HSIGMA_WITNESS_PATH)},
        "astro_lane_bundles": ASTRO_LANE_BUNDLES,
        "ap6d_bridge_span_rows": AP6D_BRIDGE_SPAN_ROWS,
    }
    summary = {
        "generated_at": manifest["generated_at"],
        "byte": current["byte"],
        "coords": current["coords"],
        "top_master_key_rows": [{"row_id": row_id, "weight": current["rows"][row_id]["weight"], "class": current["rows"][row_id]["class"], "hidden_pressure": current["rows"][row_id]["hidden_pressure"]} for row_id in current["top_master_keys"]],
        "frontier_rows": [{"row_id": row_id, "weight": current["rows"][row_id]["weight"], "class": current["rows"][row_id]["class"], "hidden_pressure": current["rows"][row_id]["hidden_pressure"]} for row_id in save_state["frontier_nexus_rows"]],
        "hidden_candidate_pressure": [{"id": candidate["id"], "state_count": cells["candidate_support"][candidate["id"]]["state_count"], "hidden_pressure_avg": cells["candidate_support"][candidate["id"]]["hidden_pressure_avg"], "contradiction_avg": cells["candidate_support"][candidate["id"]]["contradiction_avg"], "promoted": cells["candidate_support"][candidate["id"]]["promoted"]} for candidate in HIDDEN_CANDIDATES],
    }
    return {"manifest": manifest, "mindsweeper": mindsweeper, "save_state": save_state, "summary": summary}


def render_witness(summary: dict[str, object], docs_state: str) -> str:
    lines = [
        "# Athena HSigma Runtime Witness",
        "",
        f"Date: `{summary['generated_at']}`",
        "Truth: `class-exhaustive / instance-frontier`",
        f"Docs Gate: `{docs_state}`",
        "",
        "## Current Byte",
        "",
        f"- byte: `{summary['byte']}`",
        f"- coords: `{summary['coords']}`",
        "- byte law: `B = q0 + 4q1 + 16q2 + 64q3`",
        "- coupling law: `q0=floor(local_hour/6)`, `q1=weekday mod 4`, `q2=floor(minute/15)`, `q3=day_of_year mod 4`",
        "",
        "## Top Master-Key Rows",
        "",
    ]
    for row in summary["top_master_key_rows"]:
        lines.append(f"- `{row['row_id']}` -> class=`{row['class']}` -> weight=`{row['weight']}` -> hidden_pressure=`{row['hidden_pressure']}`")
    lines.extend(["", "## Frontier Rows", ""])
    for row in summary["frontier_rows"]:
        lines.append(f"- `{row['row_id']}` -> class=`{row['class']}` -> weight=`{row['weight']}` -> hidden_pressure=`{row['hidden_pressure']}`")
    lines.extend(["", "## Hidden Candidate Pressure", ""])
    for item in summary["hidden_candidate_pressure"]:
        lines.append(f"- `{item['id']}` -> states=`{item['state_count']}` -> hidden_pressure_avg=`{item['hidden_pressure_avg']}` -> contradiction_avg=`{item['contradiction_avg']}` -> promoted=`{item['promoted']}`")
    lines.extend(["", "## Honesty", "", "- local schema graph only", "- no live Google Docs witness", "- no live ephemeris or instance-level coordinate claims"])
    return "\n".join(lines)


def write_witnesses(bundle: dict[str, object]) -> None:
    witness = render_witness(bundle["summary"], bundle["manifest"]["docs_gate"])
    for path in [HSIGMA_WITNESS_PATH, HALL_WITNESS_PATH, TEMPLE_WITNESS_PATH, RUNTIME_WITNESS_PATH, RECEIPT_WITNESS_PATH]:
        write_text(path, witness)


def ensure_hsigma_artifacts(now: datetime | None = None) -> dict[str, object]:
    bundle = build_bundle(now)
    write_json(HSIGMA_MANIFEST_PATH, bundle["manifest"])
    write_json(HSIGMA_MINDSWEEPER_PATH, bundle["mindsweeper"])
    write_json(HSIGMA_SAVE_STATE_PATH, bundle["save_state"])
    write_witnesses(bundle)
    return bundle


def load_hsigma_artifacts(now: datetime | None = None) -> dict[str, object]:
    if HSIGMA_SAVE_STATE_PATH.exists() and HSIGMA_MANIFEST_PATH.exists() and HSIGMA_MINDSWEEPER_PATH.exists() and now is None:
        return {
            "manifest": json.loads(HSIGMA_MANIFEST_PATH.read_text(encoding="utf-8")),
            "mindsweeper": json.loads(HSIGMA_MINDSWEEPER_PATH.read_text(encoding="utf-8")),
            "save_state": json.loads(HSIGMA_SAVE_STATE_PATH.read_text(encoding="utf-8")),
        }
    return ensure_hsigma_artifacts(now)


def main() -> int:
    bundle = ensure_hsigma_artifacts()
    print(f"Wrote HSigma manifest: {HSIGMA_MANIFEST_PATH}")
    print(f"Wrote HSigma mindsweeper: {HSIGMA_MINDSWEEPER_PATH}")
    print(f"Wrote HSigma save state: {HSIGMA_SAVE_STATE_PATH}")
    print(f"Current byte: {bundle['summary']['byte']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
