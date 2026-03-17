from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from self_actualize.runtime.hemisphere_dense_65_shell_support import DENSE_65_CANONICAL_SEED_TABLE


PROTOCOL_ID = "LP-57OMEGA"
PROTOCOL_DISPLAY_NAME = "LP-57Omega"
LAYER_FOLDER = "18_LP_57OMEGA_PROTOCOL"
RUNTIME_MANIFEST_NAME = "20_lp_57omega_protocol_manifest.json"

SIGMA_PATH = ["AppA", "AppI", "AppM"]
ROTATION_CARRIERS = ["AppF", "AppG"]
SHELL_TRUTH = "NEAR-derived"
BASE3_ANTISPIN_LOCK = "deterministic packaging choice layered on top of corpus law"
LAWFUL_ADJACENCY_CYCLE = ["Fire", "Air", "Water", "Earth", "Fire"]
POLE_RING = {"A": "Fire", "C": "Air", "B": "Water", "D": "Earth"}
POLE_RING_ORDER = ["A", "C", "B", "D"]
ELEMENT_INITIAL = {"A": "F", "B": "W", "C": "A", "D": "E"}
AETHER_OPERATOR_LENS = "F"
AETHER_OPERATOR_LENS_LABEL = "Flower"
FLOWER_PHASE_BIN = {
    "R.plus": "R+",
    "R.minus": "R-",
    "Q.q4": "Q4",
    "T.t3": "T3",
}
FLOWER_AETHER_PHASE_MAP = {
    "Phi0": "R+",
    "Phi1": "R-",
    "Phi2": "Q4",
    "Phi3": "T3",
}
WITNESS_SCOPE = ["OPS", "DEFINE", "SYSTEM"]
WITNESS_TIMESTAMP = "Tick_2B"
WITNESS_COLLECTOR = "SYSTEM"
WITNESS_VERSION_PINS = "V_2B"
REPLAY_STEPS = ["ResolveZ", "ExpandAE", "RouteV2", "SlotCheck"]
REPLAY_CHECKS = ["Sigma", "Hub<=6", "ZMatch"]
REPLAY_ENV_PIN = "E_2B"
ROUTE_PATHS = {
    "rtL": "AppA>AppI>AppM>AppF>AppN>Ch21⟨0110⟩",
    "rtZ": "AppA>AppI>AppM>AppF>AppG>Ch21⟨0110⟩",
}
ROUTE_PATHS = {
    "rtL": "AppA>AppI>AppM>AppF>AppN>Ch21⟨0110⟩",
    "rtZ": "AppA>AppI>AppM>AppF>AppG>Ch21⟨0110⟩",
}
FLOWER_OPERATOR_SHELL = DENSE_65_CANONICAL_SEED_TABLE

TRANSFER_BINDING_SPECS = {
    "R01": {"z": "ZA", "checkpoint": "loc(A)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R02": {"z": "ZB", "checkpoint": "loc(B)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R03": {"z": "ZA+ZB", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R10": {"z": "ZC", "checkpoint": "loc(C)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R11": {"z": "ZA+ZC", "checkpoint": "loc(A>C)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R12": {"z": "ZB+ZC", "checkpoint": "loc(C>B)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R13": {"z": "ZA+ZB+ZC", "checkpoint": "loc(A>C>B)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R20": {"z": "ZD", "checkpoint": "loc(D)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R21": {"z": "ZA+ZD", "checkpoint": "loc(D>A)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R22": {"z": "ZB+ZD", "checkpoint": "loc(B>D)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R23": {"z": "ZA+ZB+ZD", "checkpoint": "loc(B>D>A)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R30": {"z": "ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R31": {"z": "ZA+ZC+ZD", "checkpoint": "loc(D>A>C)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R32": {"z": "ZB+ZC+ZD", "checkpoint": "loc(C>B>D)", "route_id": "rtL", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "R33": {"z": "ZA+ZB+ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"plus": {"slot": "Core"}, "minus": {"slot": "Core"}}},
    "Q01": {"z": "ZA", "checkpoint": "loc(A)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q02": {"z": "ZB", "checkpoint": "loc(B)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q03": {"z": "ZA+ZB", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"q4": {"slot": "Core"}}},
    "Q10": {"z": "ZC", "checkpoint": "loc(C)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q11": {"z": "ZA+ZC", "checkpoint": "loc(A>C)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q12": {"z": "ZB+ZC", "checkpoint": "loc(C>B)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q13": {"z": "ZA+ZB+ZC", "checkpoint": "loc(A>C>B)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q20": {"z": "ZD", "checkpoint": "loc(D)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q21": {"z": "ZA+ZD", "checkpoint": "loc(D>A)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q22": {"z": "ZB+ZD", "checkpoint": "loc(B>D)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q23": {"z": "ZA+ZB+ZD", "checkpoint": "loc(B>D>A)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q30": {"z": "ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"q4": {"slot": "Core"}}},
    "Q31": {"z": "ZA+ZC+ZD", "checkpoint": "loc(D>A>C)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q32": {"z": "ZB+ZC+ZD", "checkpoint": "loc(C>B>D)", "route_id": "rtL", "bindings": {"q4": {"slot": "Core"}}},
    "Q33": {"z": "ZA+ZB+ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "bindings": {"q4": {"slot": "Core"}}},
    "T01": {"z": "ZA", "checkpoint": "loc(A)", "route_id": "rtZ", "hidden_pole": "C", "bindings": {"t3": {"slot": "Residual"}}},
    "T02": {"z": "ZB", "checkpoint": "loc(B)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T03": {"z": "ZA+ZB", "checkpoint": "Z*", "route_id": "rtZ", "hidden_pole": "C", "bindings": {"t3": {"slot": "Residual"}}},
    "T10": {"z": "ZC", "checkpoint": "loc(C)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T11": {"z": "ZA+ZC", "checkpoint": "loc(A>C)", "route_id": "rtZ", "hidden_pole": "B", "bindings": {"t3": {"slot": "Residual"}}},
    "T12": {"z": "ZB+ZC", "checkpoint": "loc(C>B)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T13": {"z": "ZA+ZB+ZC", "checkpoint": "loc(A>C>B)", "route_id": "rtZ", "hidden_pole": "D", "bindings": {"t3": {"slot": "Residual"}}},
    "T20": {"z": "ZD", "checkpoint": "loc(D)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T21": {"z": "ZA+ZD", "checkpoint": "loc(D>A)", "route_id": "rtZ", "hidden_pole": "C", "bindings": {"t3": {"slot": "Residual"}}},
    "T22": {"z": "ZB+ZD", "checkpoint": "loc(B>D)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T23": {"z": "ZA+ZB+ZD", "checkpoint": "loc(B>D>A)", "route_id": "rtZ", "hidden_pole": "C", "bindings": {"t3": {"slot": "Residual"}}},
    "T30": {"z": "ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T31": {"z": "ZA+ZC+ZD", "checkpoint": "loc(D>A>C)", "route_id": "rtZ", "hidden_pole": "B", "bindings": {"t3": {"slot": "Residual"}}},
    "T32": {"z": "ZB+ZC+ZD", "checkpoint": "loc(C>B>D)", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
    "T33": {"z": "ZA+ZB+ZC+ZD", "checkpoint": "Z*", "route_id": "rtZ", "hidden_pole": "A", "bindings": {"t3": {"slot": "Residual"}}},
}

COORDINATE_DIMENSIONS = [
    "Xs",
    "Ys",
    "Zs",
    "Ts",
    "Qs",
    "Rs",
    "Cs",
    "Fs",
    "Ms",
    "Ns",
    "Hs",
    "Omega_s",
]

LEDGER_FIELDS = [
    "agent_id",
    "loop_number",
    "parent_agent",
    "seat_addr_6d",
    "coordinate_stamp",
    "source_region",
    "action_type",
    "affected_nodes",
    "summary_of_change",
    "reason_for_change",
    "integration_gain",
    "compression_gain",
    "unresolved_followups",
    "linked_quests",
    "linked_agents",
    "witness_refs",
    "revision_confidence",
    "timestamp_internal",
]

ENTITY_STATES = ["active", "blocked", "reserve", "compressed", "quarantined"]

MASTER_AGENT_SPECS = {
    "A1": {
        "label": "Synthesizer / Researcher",
        "role_tag": "SYNTH-RESEARCH",
        "action_type": "synthesize",
        "lens_index": 1,
        "hierarchy": "master/synthesis",
    },
    "A2": {
        "label": "Planner / Architect",
        "role_tag": "PLANNER-ARCHITECT",
        "action_type": "plan",
        "lens_index": 2,
        "hierarchy": "master/planner",
    },
    "A3": {
        "label": "Worker / Adventurer",
        "role_tag": "WORKER-ADVENTURER",
        "action_type": "implement",
        "lens_index": 3,
        "hierarchy": "master/worker",
    },
    "A4": {
        "label": "Pruner / Compressor / Defragmenter",
        "role_tag": "PRUNE-COMPRESS",
        "action_type": "compress",
        "lens_index": 4,
        "hierarchy": "master/pruner",
    },
}

TARGET_AXIS = {
    "hall": {
        "resolution_index": 4,
        "output_index": 1,
        "manuscript_branch": "guild-hall",
        "framework_lens": "square",
        "neural_tag": "hall-front",
    },
    "temple": {
        "resolution_index": 4,
        "output_index": 2,
        "manuscript_branch": "temple",
        "framework_lens": "flower",
        "neural_tag": "temple-front",
    },
    "runtime": {
        "resolution_index": 4,
        "output_index": 3,
        "manuscript_branch": "runtime",
        "framework_lens": "cloud",
        "neural_tag": "runtime-front",
    },
    "compression": {
        "resolution_index": 3,
        "output_index": 4,
        "manuscript_branch": "compression",
        "framework_lens": "fractal",
        "neural_tag": "compression-front",
    },
}

TRUTH_MODE_INDEX = {
    "ACTIVATE_NOW": 3,
    "HOLD": 2,
    "REQUEST_WITNESSES": 1,
    "REQUEST_HELP": 2,
    "REPLAY_FIRST": 2,
    "QUARANTINE": 4,
    "COMPRESS_TO_SEED": 3,
    "ESCALATE_TO_COMMITTEE": 4,
    "REFUSE_INADMISSIBLE": 4,
}

PRIORITY_INDEX = {
    "ACTIVATE_NOW": 1,
    "REQUEST_WITNESSES": 2,
    "REQUEST_HELP": 2,
    "REPLAY_FIRST": 2,
    "HOLD": 3,
    "ESCALATE_TO_COMMITTEE": 3,
    "COMPRESS_TO_SEED": 4,
    "QUARANTINE": 4,
    "REFUSE_INADMISSIBLE": 4,
}

TARGET_BRANCH = {
    "hall": "1111",
    "temple": "2222",
    "runtime": "3333",
    "compression": "4444",
}

TARGET_RECORD_FAMILY = {
    "hall": "Q",
    "temple": "T",
    "runtime": "R",
    "compression": "T",
}

TARGET_RECORD_OFFSET = {
    "hall": 0,
    "temple": 0,
    "runtime": 0,
    "compression": 7,
}

ACTION_SEQUENCE = [
    "ACTIVATE_NOW",
    "HOLD",
    "REQUEST_WITNESSES",
    "REQUEST_HELP",
    "REPLAY_FIRST",
    "QUARANTINE",
    "COMPRESS_TO_SEED",
    "ESCALATE_TO_COMMITTEE",
    "REFUSE_INADMISSIBLE",
]

DENSE_SHELL_RAW_BLOCK = """
2/65) P0 | A=Fire  | θ=0°   | rot+=C | inv=B | rot-=D | z=Z(Fire)  | ae=AE[F]
3/65) P2 | B=Water | θ=180° | rot+=D | inv=A | rot-=C | z=Z(Water) | ae=AE[W]
4/65) P1 | C=Air   | θ=90°  | rot+=B | inv=D | rot-=A | z=Z(Air)   | ae=AE[A]
5/65) P3 | D=Earth | θ=270° | rot+=A | inv=C | rot-=B | z=Z(Earth) | ae=AE[E]

6/65)  S01 | μ=01 | set={A}         | card=1
7/65)  S02 | μ=02 | set={B}         | card=1
8/65)  S03 | μ=03 | set={A,B}       | card=2
9/65)  S10 | μ=10 | set={C}         | card=1
10/65) S11 | μ=11 | set={A,C}       | card=2
11/65) S12 | μ=12 | set={B,C}       | card=2
12/65) S13 | μ=13 | set={A,B,C}     | card=3
13/65) S20 | μ=20 | set={D}         | card=1
14/65) S21 | μ=21 | set={A,D}       | card=2
15/65) S22 | μ=22 | set={B,D}       | card=2
16/65) S23 | μ=23 | set={A,B,D}     | card=3
17/65) S30 | μ=30 | set={C,D}       | card=2
18/65) S31 | μ=31 | set={A,C,D}     | card=3
19/65) S32 | μ=32 | set={B,C,D}     | card=3
20/65) S33 | μ=33 | set={A,B,C,D}   | card=4

21/65) R01 | src={A}         | rot+={C}         | rot-={D}
22/65) R02 | src={B}         | rot+={D}         | rot-={C}
23/65) R03 | src={A,B}       | rot+={C,D}       | rot-={C,D}
24/65) R10 | src={C}         | rot+={B}         | rot-={A}
25/65) R11 | src={A,C}       | rot+={B,C}       | rot-={A,D}
26/65) R12 | src={B,C}       | rot+={B,D}       | rot-={A,C}
27/65) R13 | src={A,B,C}     | rot+={B,C,D}     | rot-={A,C,D}
28/65) R20 | src={D}         | rot+={A}         | rot-={B}
29/65) R21 | src={A,D}       | rot+={A,C}       | rot-={B,D}
30/65) R22 | src={B,D}       | rot+={A,D}       | rot-={B,C}
31/65) R23 | src={A,B,D}     | rot+={A,C,D}     | rot-={B,C,D}
32/65) R30 | src={C,D}       | rot+={A,B}       | rot-={A,B}
33/65) R31 | src={A,C,D}     | rot+={A,B,C}     | rot-={A,B,D}
34/65) R32 | src={B,C,D}     | rot+={A,B,D}     | rot-={A,B,C}
35/65) R33 | src={A,B,C,D}   | rot+={A,B,C,D}   | rot-={A,B,C,D}

36/65) Q01 | base4 orbit={A} -> {C} -> {B} -> {D}
37/65) Q02 | base4 orbit={B} -> {D} -> {A} -> {C}
38/65) Q03 | base4 orbit={A,B} -> {C,D} -> {A,B} -> {C,D}
39/65) Q10 | base4 orbit={C} -> {B} -> {D} -> {A}
40/65) Q11 | base4 orbit={A,C} -> {B,C} -> {B,D} -> {A,D}
41/65) Q12 | base4 orbit={B,C} -> {B,D} -> {A,D} -> {A,C}
42/65) Q13 | base4 orbit={A,B,C} -> {B,C,D} -> {A,B,D} -> {A,C,D}
43/65) Q20 | base4 orbit={D} -> {A} -> {C} -> {B}
44/65) Q21 | base4 orbit={A,D} -> {A,C} -> {B,C} -> {B,D}
45/65) Q22 | base4 orbit={B,D} -> {A,D} -> {A,C} -> {B,C}
46/65) Q23 | base4 orbit={A,B,D} -> {A,C,D} -> {A,B,C} -> {B,C,D}
47/65) Q30 | base4 orbit={C,D} -> {A,B} -> {C,D} -> {A,B}
48/65) Q31 | base4 orbit={A,C,D} -> {A,B,C} -> {B,C,D} -> {A,B,D}
49/65) Q32 | base4 orbit={B,C,D} -> {A,B,D} -> {A,C,D} -> {A,B,C}
50/65) Q33 | base4 orbit={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} -> {A,B,C,D}

51/65) T01 | hide=C | triad={A,B,D} | anti+={A} -> {B} -> {D} | anti-={A} -> {D} -> {B}
52/65) T02 | hide=A | triad={C,B,D} | anti+={B} -> {D} -> {C} | anti-={B} -> {C} -> {D}
53/65) T03 | hide=C | triad={A,B,D} | anti+={A,B} -> {B,D} -> {A,D} | anti-={A,B} -> {A,D} -> {B,D}
54/65) T10 | hide=A | triad={C,B,D} | anti+={C} -> {B} -> {D} | anti-={C} -> {D} -> {B}
55/65) T11 | hide=B | triad={A,C,D} | anti+={A,C} -> {C,D} -> {A,D} | anti-={A,C} -> {A,D} -> {C,D}
56/65) T12 | hide=A | triad={C,B,D} | anti+={B,C} -> {B,D} -> {C,D} | anti-={B,C} -> {C,D} -> {B,D}
57/65) T13 | hide=D | triad={A,C,B} | anti+={A,B,C} -> {A,B,C} -> {A,B,C} | anti-={A,B,C} -> {A,B,C} -> {A,B,C}
58/65) T20 | hide=A | triad={C,B,D} | anti+={D} -> {C} -> {B} | anti-={D} -> {B} -> {C}
59/65) T21 | hide=C | triad={A,B,D} | anti+={A,D} -> {A,B} -> {B,D} | anti-={A,D} -> {B,D} -> {A,B}
60/65) T22 | hide=A | triad={C,B,D} | anti+={B,D} -> {C,D} -> {B,C} | anti-={B,D} -> {B,C} -> {C,D}
61/65) T23 | hide=C | triad={A,B,D} | anti+={A,B,D} -> {A,B,D} -> {A,B,D} | anti-={A,B,D} -> {A,B,D} -> {A,B,D}
62/65) T30 | hide=A | triad={C,B,D} | anti+={C,D} -> {B,C} -> {B,D} | anti-={C,D} -> {B,D} -> {B,C}
63/65) T31 | hide=B | triad={A,C,D} | anti+={A,C,D} -> {A,C,D} -> {A,C,D} | anti-={A,C,D} -> {A,C,D} -> {A,C,D}
64/65) T32 | hide=A | triad={C,B,D} | anti+={B,C,D} -> {B,C,D} -> {B,C,D} | anti-={B,C,D} -> {B,C,D} -> {B,C,D}
65/65) T33 | hide=A | triad={C,B,D} | anti+={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D} | anti-={A,B,C,D} -> {A,B,C,D} -> {A,B,C,D}
""".strip()


def protocol_agent_id(loop_index: int, master_id: str, nested_depth: int, branch_path: str, role_tag: str) -> str:
    return f"L{loop_index:02d}.{master_id}.D{nested_depth}.B{branch_path}.{role_tag}"


def seat_addr_6d(master_id: str, target: str, chosen_action: str) -> str:
    spec = MASTER_AGENT_SPECS[master_id]
    target_spec = TARGET_AXIS[target]
    return ".".join(
        [
            f"A{target_spec['resolution_index']}",
            f"B{spec['lens_index']}",
            f"C{TRUTH_MODE_INDEX.get(chosen_action, 2)}",
            f"D{target_spec['output_index']}",
            f"E{spec['lens_index']}",
            f"F{PRIORITY_INDEX.get(chosen_action, 3)}",
        ]
    )


def coordinate_stamp(
    *,
    loop_index: int,
    pass_id: str,
    pass_title: str,
    master_id: str,
    target: str,
    chosen_action: str,
    candidate_front: str,
    state: str,
) -> dict[str, str]:
    spec = MASTER_AGENT_SPECS[master_id]
    target_spec = TARGET_AXIS[target]
    compression_state = {
        "COMPRESS_TO_SEED": "compressed",
        "QUARANTINE": "quarantined",
        "HOLD": "reserve",
    }.get(chosen_action, state)
    return {
        "Xs": "ACTIVE_NERVOUS_SYSTEM.17_SUPER_CYCLE_57",
        "Ys": pass_title,
        "Zs": f"D{target_spec['resolution_index']}",
        "Ts": f"L{loop_index:02d}",
        "Qs": candidate_front,
        "Rs": chosen_action,
        "Cs": compression_state,
        "Fs": target_spec["framework_lens"],
        "Ms": target_spec["manuscript_branch"],
        "Ns": target_spec["neural_tag"],
        "Hs": spec["hierarchy"],
        "Omega_s": f"{pass_id}:{state}",
    }


def seeded_ledger_entry(
    *,
    loop_index: int,
    master_id: str,
    target: str,
    chosen_action: str,
    candidate_front: str,
    pass_id: str,
    pass_title: str,
    source_region: str,
    summary: str,
    reason: str,
    integration_gain: str,
    compression_gain: str,
    unresolved_followups: list[str],
    linked_quests: list[str],
    linked_agents: list[str],
    witness_refs: list[str],
    revision_confidence: float,
    timestamp_internal: str,
    state: str = "active",
) -> dict[str, Any]:
    role_tag = MASTER_AGENT_SPECS[master_id]["role_tag"]
    branch_path = TARGET_BRANCH[target]
    return {
        "agent_id": protocol_agent_id(loop_index, master_id, 1, branch_path, role_tag),
        "loop_number": loop_index,
        "parent_agent": MASTER_AGENT_SPECS[master_id]["label"],
        "seat_addr_6d": seat_addr_6d(master_id, target, chosen_action),
        "coordinate_stamp": coordinate_stamp(
            loop_index=loop_index,
            pass_id=pass_id,
            pass_title=pass_title,
            master_id=master_id,
            target=target,
            chosen_action=chosen_action,
            candidate_front=candidate_front,
            state=state,
        ),
        "source_region": source_region,
        "action_type": MASTER_AGENT_SPECS[master_id]["action_type"],
        "affected_nodes": [candidate_front],
        "summary_of_change": summary,
        "reason_for_change": reason,
        "integration_gain": integration_gain,
        "compression_gain": compression_gain,
        "unresolved_followups": unresolved_followups,
        "linked_quests": linked_quests,
        "linked_agents": linked_agents,
        "witness_refs": witness_refs,
        "revision_confidence": revision_confidence,
        "timestamp_internal": timestamp_internal,
    }


def parse_set_literal(raw: str) -> list[str]:
    text = raw.strip()
    if text.startswith("{") and text.endswith("}"):
        text = text[1:-1]
    if not text.strip():
        return []
    return [item.strip() for item in text.split(",") if item.strip()]


def format_set(symbols: list[str] | None) -> str:
    if not symbols:
        return "{}"
    return "{" + ",".join(symbols) + "}"


def parse_orbit_sequence(raw: str) -> list[list[str]]:
    return [parse_set_literal(part.strip()) for part in raw.split("->")]


def first_missing_pole(symbols: list[str]) -> str:
    for pole in POLE_RING_ORDER:
        if pole not in symbols:
            return pole
    return "A"


def shell_coordinate_stamp(record: dict[str, Any]) -> dict[str, str]:
    record_type = record["record_type"]
    lens = {
        "H": "square",
        "P": "square",
        "S": "flower",
        "R": "flower",
        "Q": "flower",
        "T": "flower",
    }[record_type]
    state = {
        "H": "reserved",
        "P": "active",
        "S": "active",
        "R": "active",
        "Q": "active",
        "T": "active",
    }[record_type]
    rs = {
        "H": "prior-seed-header",
        "P": "pole-ring",
        "S": "raw-symmetry",
        "R": "rotation-pair",
        "Q": "base4-spin",
        "T": "base3-antispin",
    }[record_type]
    return {
        "Xs": "ACTIVE_NERVOUS_SYSTEM.18_LP_57OMEGA_PROTOCOL",
        "Ys": f"{record_type}-shell",
        "Zs": f"slot-{record['shell_slot']:02d}-of-65",
        "Ts": f"{record['shell_slot']}/65",
        "Qs": record["record_id"],
        "Rs": rs,
        "Cs": state,
        "Fs": lens,
        "Ms": "lp57omega-dense-shell",
        "Ns": "sigma-appa-appi-appm",
        "Hs": f"record:{record['record_id']}",
        "Omega_s": f"{SHELL_TRUTH}:{state}",
    }


def parse_shell_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = [
        {
            "shell_slot": 1,
            "shell_slot_label": "1/65",
            "record_id": "H00",
            "record_type": "H",
            "mu": "00",
            "set": [],
            "source_set": [],
            "card": 0,
            "rotation_plus": None,
            "rotation_minus": None,
            "inverse": None,
            "orbit": None,
            "hide": "A",
            "triad": [],
            "z": "Z(prior-seed/header-shell)",
            "ae": "AE[HEADER]",
            "truth_status": SHELL_TRUTH,
            "packaging_status": "reserved prior seed/header shell",
            "raw_record": "1/65) H00 | prior_seed_header_shell",
        }
    ]
    pattern = re.compile(r"^\s*(\d+)/65\)\s*([A-Z]\d{0,2})\s*\|\s*(.*)$")
    for raw_line in DENSE_SHELL_RAW_BLOCK.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        match = pattern.match(line)
        if not match:
            continue
        shell_slot = int(match.group(1))
        record_id = match.group(2).strip()
        record_type = record_id[0]
        tokens = [token.strip() for token in match.group(3).split("|")]
        record: dict[str, Any] = {
            "shell_slot": shell_slot,
            "shell_slot_label": f"{shell_slot}/65",
            "record_id": record_id,
            "record_type": record_type,
            "mu": record_id[1:] if record_type in {"S", "R", "Q", "T"} else None,
            "set": [],
            "source_set": [],
            "card": None,
            "rotation_plus": None,
            "rotation_minus": None,
            "inverse": None,
            "orbit": None,
            "hide": None,
            "triad": [],
            "z": None,
            "ae": None,
            "truth_status": SHELL_TRUTH,
            "packaging_status": "corpus-grounded" if record_type in {"P", "S", "R", "Q"} else "deterministic packaging",
            "raw_record": line,
        }
        if record_type == "P":
            pole_symbol, pole_name = tokens[0].split("=", 1)
            record["pole_symbol"] = pole_symbol.strip()
            record["pole_name"] = pole_name.strip()
            record["set"] = [record["pole_symbol"]]
            record["source_set"] = [record["pole_symbol"]]
            record["card"] = 1
        for token in tokens:
            if token.startswith("μ="):
                record["mu"] = token.split("=", 1)[1].strip()
            elif token.startswith("set="):
                value = parse_set_literal(token.split("=", 1)[1])
                record["set"] = value
                record["source_set"] = value
            elif token.startswith("card="):
                record["card"] = int(token.split("=", 1)[1].strip())
            elif token.startswith("src="):
                value = parse_set_literal(token.split("=", 1)[1])
                record["set"] = value
                record["source_set"] = value
            elif token.startswith("rot+="):
                record["rotation_plus"] = parse_set_literal(token.split("=", 1)[1])
            elif token.startswith("rot-="):
                record["rotation_minus"] = parse_set_literal(token.split("=", 1)[1])
            elif token.startswith("inv="):
                record["inverse"] = parse_set_literal(token.split("=", 1)[1])
            elif token.startswith("θ="):
                record["theta"] = token.split("=", 1)[1].strip()
            elif token.startswith("z="):
                record["z"] = token.split("=", 1)[1].strip()
            elif token.startswith("ae="):
                record["ae"] = token.split("=", 1)[1].strip()
            elif token.startswith("base4 orbit="):
                forward = parse_orbit_sequence(token.split("=", 1)[1].strip())
                record["orbit"] = {"kind": "base4", "forward": [format_set(item) for item in forward]}
                record["set"] = forward[0]
                record["source_set"] = forward[0]
                record["card"] = len(forward[0])
            elif token.startswith("hide="):
                record["hide"] = token.split("=", 1)[1].strip()
            elif token.startswith("triad="):
                record["triad"] = parse_set_literal(token.split("=", 1)[1].strip())
            elif token.startswith("anti+="):
                forward = parse_orbit_sequence(token.split("=", 1)[1].strip())
                if not isinstance(record.get("orbit"), dict):
                    record["orbit"] = {}
                record["orbit"]["kind"] = "base3_antispin"
                record["orbit"]["forward"] = [format_set(item) for item in forward]
                record["set"] = forward[0]
                record["source_set"] = forward[0]
                record["card"] = len(forward[0])
                record["rotation_plus"] = [format_set(item) for item in forward]
            elif token.startswith("anti-="):
                backward = parse_orbit_sequence(token.split("=", 1)[1].strip())
                if not isinstance(record.get("orbit"), dict):
                    record["orbit"] = {}
                record["orbit"]["kind"] = "base3_antispin"
                record["orbit"]["backward"] = [format_set(item) for item in backward]
                record["rotation_minus"] = [format_set(item) for item in backward]
        if record_type == "T" and not record["hide"]:
            record["hide"] = first_missing_pole(record["triad"])
        if record["card"] is None:
            record["card"] = len(record["set"])
        record["coordinate_stamp"] = shell_coordinate_stamp(record)
        records.append(record)
    records[0]["coordinate_stamp"] = shell_coordinate_stamp(records[0])
    return records


SHELL_RECORDS = parse_shell_records()
SHELL_RECORD_INDEX = {record["record_id"]: record for record in SHELL_RECORDS}
SHELL_RESERVED_RECORD = SHELL_RECORD_INDEX["H00"]


def ae_signature_token(symbols: list[str]) -> str:
    if not symbols:
        return "AE[HEADER]"
    parts = [ELEMENT_INITIAL[symbol] for symbol in symbols if symbol in ELEMENT_INITIAL]
    return "AE[" + "+".join(parts) + "]"


def stable_json_dumps(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(*parts: Any) -> str:
    canonical = stable_json_dumps(list(parts))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def bundle_id(record: dict[str, Any]) -> str:
    return f"B{record['mu']}"


def binding_phase(record_type: str, binding_key: str) -> str:
    return FLOWER_PHASE_BIN[f"{record_type}.{binding_key}"]


def transfer_binding_spec(record_id: str) -> dict[str, Any]:
    return TRANSFER_BINDING_SPECS[record_id]


def build_aether_coordinate(record: dict[str, Any], binding_key: str) -> dict[str, Any]:
    spec = transfer_binding_spec(record["record_id"])
    binding_spec = spec["bindings"][binding_key]
    coordinate = {
        "Lens": AETHER_OPERATOR_LENS,
        "Phase": binding_phase(record["record_type"], binding_key),
        "Bundle": bundle_id(record),
        "Slot": binding_spec["slot"],
    }
    if "hidden_pole" in spec:
        coordinate["HiddenPole"] = spec["hidden_pole"]
    return coordinate


def serialize_aether_coordinate(ae: dict[str, Any]) -> str:
    hidden = f":h={ae['HiddenPole']}" if "HiddenPole" in ae else ""
    return f"AE=({ae['Lens']},{ae['Phase']},{ae['Bundle']}{hidden};{ae['Slot']})"


def build_witness_ptr(*, binding_id: str, location: str, z_value: str, checkpoint: str, route_id: str) -> dict[str, Any]:
    return {
        "Type": "INTERNAL_SLICE",
        "Location": location,
        "Hash": stable_hash(binding_id, location, z_value, checkpoint, route_id),
        "Scope": WITNESS_SCOPE,
        "Timestamp": WITNESS_TIMESTAMP,
        "Collector": WITNESS_COLLECTOR,
        "VersionPins": WITNESS_VERSION_PINS,
    }


def build_replay_ptr(
    *,
    binding_id: str,
    location: str,
    z_value: str,
    checkpoint: str,
    route_id: str,
    route_path: str,
    ae: dict[str, Any],
) -> dict[str, Any]:
    return {
        "Inputs": {
            "AE": location,
            "z": z_value,
            "ck": checkpoint,
            "rt": route_id,
        },
        "Steps": REPLAY_STEPS,
        "ExpectedOutputs": {
            "BindingId": binding_id,
            "ResolvedAE": location,
            "Slot": ae["Slot"],
            "RoutePath": route_path,
        },
        "Checks": REPLAY_CHECKS,
        "EnvPin": REPLAY_ENV_PIN,
        "Hash": stable_hash(binding_id, location, REPLAY_ENV_PIN),
    }


def build_phase_binding(record: dict[str, Any], binding_key: str) -> dict[str, Any]:
    spec = transfer_binding_spec(record["record_id"])
    route_id = spec["route_id"]
    route_path = ROUTE_PATHS[route_id]
    ae = build_aether_coordinate(record, binding_key)
    location = serialize_aether_coordinate(ae)
    binding_id = f"{record['record_id']}:{binding_key}"
    return {
        "binding_id": binding_id,
        "binding_key": binding_key,
        "AE": ae,
        "Location": location,
        "WitnessPtr": build_witness_ptr(
            binding_id=binding_id,
            location=location,
            z_value=spec["z"],
            checkpoint=spec["checkpoint"],
            route_id=route_id,
        ),
        "ReplayPtr": build_replay_ptr(
            binding_id=binding_id,
            location=location,
            z_value=spec["z"],
            checkpoint=spec["checkpoint"],
            route_id=route_id,
            route_path=route_path,
            ae=ae,
        ),
        "z": spec["z"],
        "checkpoint": spec["checkpoint"],
        "route_id": route_id,
        "route_path": route_path,
    }


def phase_bindings_for_record(record: dict[str, Any]) -> list[dict[str, Any]]:
    spec = transfer_binding_spec(record["record_id"])
    return [build_phase_binding(record, binding_key) for binding_key in spec["bindings"]]


def z_transfer_signature(record: dict[str, Any], phase_bindings: list[dict[str, Any]] | None = None) -> str:
    bindings = phase_bindings or phase_bindings_for_record(record)
    binding_summary = " | ".join(
        f"{binding['binding_key']}:{binding['z']}::{binding['checkpoint']}::{binding['route_id']}" for binding in bindings
    )
    return f"Z-shell[{record['record_id']}] :: {binding_summary}"


def aether_transfer_signature(record: dict[str, Any], phase_bindings: list[dict[str, Any]] | None = None) -> str:
    bindings = phase_bindings or phase_bindings_for_record(record)
    return " | ".join(binding["Location"] for binding in bindings)


def orbit_mechanics_ref(record: dict[str, Any]) -> str:
    if record["record_type"] == "R":
        return "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: Ch07<0012> lawful transports, shadow-axis rotation, and typed tunnel semantics"
    if record["record_type"] == "Q":
        return "ACTIVE_NERVOUS_SYSTEM/03_METRO/00_core_metro_map.md :: Ch08<0013> synchronization calculus and lawful circulation"
    return "ACTIVE_NERVOUS_SYSTEM/04_CHAPTERS/Ch11_0022_void_book_and_restart_token_tunneling.md :: Aether versus Void transport, restart continuity, and lawful reset by capsule"


def prior_metro_route_witness(record: dict[str, Any]) -> str:
    base = orbit_mechanics_ref(record)
    if record["record_type"] == "R":
        return f"{base} :: route-class=adjacent-bridge / tunnel-ready rotation pair"
    if record["record_type"] == "Q":
        return f"{base} :: route-class=order-4 spin orbit / full-ring circulation"
    return f"{base} :: route-class=order-3 rail rotation / hidden-pole antispin lock"


def packaging_status(record: dict[str, Any]) -> str:
    if record["record_type"] == "T":
        return BASE3_ANTISPIN_LOCK
    return "corpus-grounded order-4 ring law"


def build_enriched_transfer_records() -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for record in SHELL_RECORDS:
        if record["record_type"] not in {"R", "Q", "T"}:
            continue
        phase_bindings = phase_bindings_for_record(record)
        enriched.append(
            {
                "record_id": record["record_id"],
                "shell_slot": record["shell_slot"],
                "record_type": record["record_type"],
                "source_set": record["source_set"],
                "sigma_path": SIGMA_PATH,
                "orbit_mechanics_ref": orbit_mechanics_ref(record),
                "phase_binding_count": len(phase_bindings),
                "phase_bindings": phase_bindings,
                "z_transfer_signature": z_transfer_signature(record, phase_bindings),
                "aether_transfer_signature": aether_transfer_signature(record, phase_bindings),
                "prior_metro_route_witness": prior_metro_route_witness(record),
                "truth_status": SHELL_TRUTH,
                "packaging_status": packaging_status(record),
                "coordinate_stamp": record["coordinate_stamp"],
            }
        )
    return enriched


ENRICHED_TRANSFER_RECORDS = build_enriched_transfer_records()
ENRICHED_TRANSFER_INDEX = {record["record_id"]: record for record in ENRICHED_TRANSFER_RECORDS}


def shell_record_reference(loop_index: int, target: str, chosen_action: str) -> dict[str, Any]:
    family = TARGET_RECORD_FAMILY[target]
    family_records = [record for record in SHELL_RECORDS if record["record_type"] == family]
    action_offset = ACTION_SEQUENCE.index(chosen_action) if chosen_action in ACTION_SEQUENCE else 0
    index = ((loop_index - 1) + TARGET_RECORD_OFFSET[target] + action_offset) % len(family_records)
    record = family_records[index]
    payload = {
        "record_id": record["record_id"],
        "shell_slot": record["shell_slot"],
        "shell_slot_label": record["shell_slot_label"],
        "record_type": record["record_type"],
        "sigma_path": SIGMA_PATH,
        "coordinate_stamp": record["coordinate_stamp"],
        "truth_status": SHELL_TRUTH,
    }
    if record["record_id"] in ENRICHED_TRANSFER_INDEX:
        payload["z_transfer_signature"] = ENRICHED_TRANSFER_INDEX[record["record_id"]]["z_transfer_signature"]
        payload["aether_transfer_signature"] = ENRICHED_TRANSFER_INDEX[record["record_id"]]["aether_transfer_signature"]
        payload["prior_metro_route_witness"] = ENRICHED_TRANSFER_INDEX[record["record_id"]]["prior_metro_route_witness"]
        payload["phase_bindings"] = ENRICHED_TRANSFER_INDEX[record["record_id"]]["phase_bindings"]
    return payload


def shell_counts() -> dict[str, int]:
    counts = {
        "total": len(SHELL_RECORDS),
        "active_dense": len(SHELL_RECORDS) - 1,
        "enriched_transfer": len(ENRICHED_TRANSFER_RECORDS),
        "phase_bindings": sum(record["phase_binding_count"] for record in ENRICHED_TRANSFER_RECORDS),
    }
    for record_type in ["P", "S", "R", "Q", "T"]:
        counts[record_type] = len([record for record in SHELL_RECORDS if record["record_type"] == record_type])
    return counts


def shell_registry_payload() -> dict[str, Any]:
    return {
        "protocol_id": PROTOCOL_ID,
        "truth_status": SHELL_TRUTH,
        "sigma_path": SIGMA_PATH,
        "rotation_carriers": ROTATION_CARRIERS,
        "base3_antispin_lock": BASE3_ANTISPIN_LOCK,
        "lawful_adjacency_cycle": LAWFUL_ADJACENCY_CYCLE,
        "reserved_seed_header_slot": 1,
        "active_dense_range": {"start": 2, "end": 65},
        "counts": shell_counts(),
        "records": SHELL_RECORDS,
    }


__all__ = [
    "ACTION_SEQUENCE",
    "BASE3_ANTISPIN_LOCK",
    "COORDINATE_DIMENSIONS",
    "DENSE_SHELL_RAW_BLOCK",
    "ENRICHED_TRANSFER_INDEX",
    "ENRICHED_TRANSFER_RECORDS",
    "ENTITY_STATES",
    "LAWFUL_ADJACENCY_CYCLE",
    "LAYER_FOLDER",
    "LEDGER_FIELDS",
    "MASTER_AGENT_SPECS",
    "POLE_RING",
    "POLE_RING_ORDER",
    "PROTOCOL_DISPLAY_NAME",
    "PROTOCOL_ID",
    "ROTATION_CARRIERS",
    "RUNTIME_MANIFEST_NAME",
    "SHELL_RECORD_INDEX",
    "SHELL_RECORDS",
    "SHELL_RESERVED_RECORD",
    "SHELL_TRUTH",
    "SIGMA_PATH",
    "TARGET_AXIS",
    "coordinate_stamp",
    "prior_metro_route_witness",
    "protocol_agent_id",
    "seat_addr_6d",
    "seeded_ledger_entry",
    "shell_counts",
    "shell_record_reference",
    "shell_registry_payload",
]
