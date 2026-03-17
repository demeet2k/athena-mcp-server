from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from self_actualize.runtime.crystal_remaster_contracts import (
    RuntimeCorridorMembraneRecord,
    SeedPacketWitnessRecord,
)
from self_actualize.runtime.derive_crystal_remaster import (
    load_json,
    read_text,
    refresh_corpus_atlas,
    relative_string,
    utc_now,
    write_json,
    write_text,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
REGISTRY_ROOT = MYCELIUM_ROOT / "registry"
NERVOUS_SYSTEM_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM"

RUNTIME_VERIFICATION_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
ORGIN_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "orgin_atlas.json"
PHASE6_WAVE2_CAPSULES_PATH = SELF_ACTUALIZE_ROOT / "phase6_wave2_capsules.json"
FLOWER_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
NETWORK_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
CLOUD_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_RUNTIME_MEMBRANE_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
QSHRINK_RUNTIME_MEMBRANE_JSON_MIRROR = REGISTRY_ROOT / QSHRINK_RUNTIME_MEMBRANE_JSON_PATH.name
ORGIN_SEED_PACKET_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_orgin_seed_packet_witness.json"
ORGIN_SEED_PACKET_JSON_MIRROR = REGISTRY_ROOT / ORGIN_SEED_PACKET_JSON_PATH.name
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_flower_pass_dashboard.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / DASHBOARD_JSON_PATH.name
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_flower_pass_verification.json"
VERIFICATION_JSON_MIRROR = REGISTRY_ROOT / VERIFICATION_JSON_PATH.name
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
PHASE4_PATH = SELF_ACTUALIZE_ROOT / "phase4_weave_candidates.json"
KNOWLEDGE_FABRIC_PATH = SELF_ACTUALIZE_ROOT / "knowledge_fabric_edges.json"
PHASE4_PT2_PATH = SELF_ACTUALIZE_ROOT / "phase4_pt2_system_crosswalk_edges.json"
QSHRINK_STACK_VERIFY_PATH = SELF_ACTUALIZE_ROOT / "qshrink_runtime_verification.json"
AQM_RUNTIME_PATH = SELF_ACTUALIZE_ROOT / "aqm_runtime_lane.json"
ATLASFORGE_RUNTIME_PATH = SELF_ACTUALIZE_ROOT / "atlasforge_runtime_lane.json"
RUNTIME_WAIST_PATH = SELF_ACTUALIZE_ROOT / "runtime_waist_verification.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"

PACKETS_ROOT = MYCELIUM_ROOT / "nervous_system" / "packets"
MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
NERVOUS_RUNTIME_ROOT = MYCELIUM_ROOT / "nervous_system"

ACTIVE_QUEUE_PATH = NERVOUS_RUNTIME_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MANIFESTS_ROOT / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
WEAKEST_FRONT_QUEUE_PATH = MANIFESTS_ROOT / "WEAKEST_FRONT_QUEUE.md"
TEMPLE_STATE_PATH = MYCELIUM_ROOT / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_RUN_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "ACTIVE_RUN.md"
BUILD_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "BUILD_QUEUE.md"
QSHRINK_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use.md"
QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
ORGIN_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_orgin.md"
ORGIN_GANGLION_PATH = NERVOUS_RUNTIME_ROOT / "ganglia" / "GANGLION_orgin.md"
RUNTIME_MEMBRANE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
SEED_PACKET_MD_PATH = PACKETS_ROOT / "PKT_2026-03-13_q42_orgin_seed_packet_witness.md"

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_FLOWER_PASS_MANIFEST.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_FLOWER_PASS_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_FLOWER_PASS_VERIFICATION.md"
RUNTIME_MD_PATH = NERVOUS_RUNTIME_ROOT / "32_q42_flower_pass_activation_runtime.md"
RECEIPT_MD_PATH = RECEIPTS_ROOT / "2026-03-13_q42_flower_pass_activation.md"

FLOWER_SUBFRONT = "QS64-18 Connectivity-Diagnose-Flower"
CLOUD_SUBFRONT = "QS64-19 Connectivity-Diagnose-Cloud"
FRACTAL_SUBFRONT = "QS64-20 Connectivity-Diagnose-Fractal"
DERIVATION_VERSION = "2026-03-13.q42-flower-pass-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_flower_pass_activation"


def run_module(module: str) -> Dict[str, Any]:
    result = subprocess.run(
        [sys.executable, "-m", module],
        cwd=WORKSPACE_ROOT,
        capture_output=True,
        text=True,
    )
    return {
        "module": module,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "ok": result.returncode == 0,
    }


def docs_gate_status() -> str:
    credentials_path = WORKSPACE_ROOT / "Trading Bot" / "credentials.json"
    token_path = WORKSPACE_ROOT / "Trading Bot" / "token.json"
    if not credentials_path.exists():
        return "blocked-by-missing-credentials"
    if not token_path.exists():
        return "blocked-by-missing-token"
    gate_text = read_text(LIVE_DOCS_GATE_PATH)
    if "Command status: `OPEN`" in gate_text:
        return "open"
    return "blocked-by-auth-failure"


def build_runtime_membrane() -> RuntimeCorridorMembraneRecord:
    runtime_payload = load_json(RUNTIME_VERIFICATION_PATH)
    truth_state = "OK" if runtime_payload.get("truth") == "OK" else "NEAR"
    return RuntimeCorridorMembraneRecord(
        corridor_id="Q42-M3-RUNTIME-RAIL",
        source_body_id="A16",
        target_runtime_surface="MATH\\FINAL FORM\\FRAMEWORKS CODE\\Athena OS\\athena_os\\qshrink\\",
        writeback_surface=relative_string(QSHRINK_ACTIVE_FRONT_PATH),
        witness_basis=[
            relative_string(RUNTIME_VERIFICATION_PATH),
            relative_string(RUNTIME_MEMBRANE_MD_PATH),
            relative_string(QSHRINK_ACTIVE_FRONT_PATH),
        ],
        truth_state=truth_state,
        next_seed=CLOUD_SUBFRONT,
        note="Athena OS runtime is now witnessed as the M3 corridor membrane for local Flower closure.",
    )


def build_seed_packet_witness() -> SeedPacketWitnessRecord:
    orgin_atlas = load_json(ORGIN_ATLAS_PATH)
    phase6_payload = load_json(PHASE6_WAVE2_CAPSULES_PATH)
    orgin_family = next(
        (family for family in phase6_payload.get("families", []) if family.get("root_name") == "ORGIN"),
        {},
    )
    mirror_paths = orgin_family.get("mirror_paths", [])
    mirror_surface = mirror_paths[0] if mirror_paths else relative_string(ORGIN_ROUTE_MAP_PATH)
    truth_state = "OK" if mirror_paths and orgin_atlas.get("record_count", 0) > 0 else "NEAR"
    return SeedPacketWitnessRecord(
        packet_witness_id="Q42-M5-SEED-PACKET",
        source_body_id="A15",
        mirror_surface=mirror_surface,
        packet_index_surface=relative_string(SEED_PACKET_MD_PATH),
        writeback_target=relative_string(ORGIN_ROUTE_MAP_PATH),
        witness_basis=[
            relative_string(ORGIN_ATLAS_PATH),
            relative_string(PHASE6_WAVE2_CAPSULES_PATH),
            mirror_surface,
            relative_string(ORGIN_FAMILY_PATH),
            relative_string(ORGIN_GANGLION_PATH),
        ],
        truth_state=truth_state,
        note="ORGIN is now packet-backed inside the M5 rail instead of staying route-map-only.",
    )


def render_runtime_membrane_markdown(record: RuntimeCorridorMembraneRecord) -> str:
    witnesses = "\n".join(f"- `{item}`" for item in record.witness_basis)
    return f"""# ATHENA OS QSHRINK CORRIDOR MEMBRANE

Date: `2026-03-13`
Truth: `{record.truth_state}`

## Corridor

- corridor id: `{record.corridor_id}`
- source body id: `{record.source_body_id}`
- target runtime surface: `{record.target_runtime_surface}`
- writeback surface: `{record.writeback_surface}`
- next seed: `{record.next_seed}`

## Witness basis

{witnesses}

## Note

{record.note}
"""


def render_seed_packet_markdown(record: SeedPacketWitnessRecord) -> str:
    witnesses = "\n".join(f"- `{item}`" for item in record.witness_basis)
    return f"""# PKT 2026-03-13 Q42 ORGIN SEED PACKET WITNESS

Date: `2026-03-13`
Truth: `{record.truth_state}`

## Packet

- packet witness id: `{record.packet_witness_id}`
- source body id: `{record.source_body_id}`
- mirror surface: `{record.mirror_surface}`
- packet index surface: `{record.packet_index_surface}`
- writeback target: `{record.writeback_target}`

## Witness basis

{witnesses}

## Note

{record.note}
"""


def render_orgin_route_map(record: SeedPacketWitnessRecord) -> str:
    return f"""# FAMILY ORGIN Route Map

## Intake

- `ORGIN/Fine Tuning Docs/`
- `self_actualize/orgin_atlas.json`
- `{record.mirror_surface}`
- `{record.packet_index_surface}`

## Main transfer

`ORGIN -> readable mirror bundle -> seed packet witness -> Athena FLEET flower core -> self_actualize runtime`

## Law

Read `ORGIN` as origin memory and observer-seed matter.
Do not route it as miscellaneous storage.
Mirror surfaces may feed local Flower closure, but they do not outrank the blocked Docs gate and do not bypass atlas indexing.

## Next route

`ORGIN -> Q42 local Flower writeback -> {CLOUD_SUBFRONT}`
"""


def render_q42_queue_block() -> str:
    return f"""### FRONT-Q42-QSHRINK-AGENT-SWEEP

- Quest:
  `Q42: Activate The First QSHRINK Agent Sweep`
- State:
  `OPEN`
- Truth:
  `OK`
- Objective:
  close the first QSHRINK Flower pass honestly by landing the Athena OS runtime membrane and the ORGIN seed packet witness while keeping the blocked Docs gate outside local closure law
- Why Now:
  the stack had drifted into Cloud ranking before Flower was actually witnessed, so the honest move is to repair the local corridor before promoting the next frontier
- Active subfront:
  `{FLOWER_SUBFRONT}`
- Targets:
  `self_actualize/q42_runtime_corridor_membrane.json`
  `self_actualize/q42_orgin_seed_packet_witness.json`
  `self_actualize/qshrink_connectivity_flower.json`
  `self_actualize/qshrink_network_integration.json`
  `self_actualize/qshrink_connectivity_cloud.json`
  `self_actualize/qshrink_agent_task_matrix.json`
  `manifests/QSHRINK_ACTIVE_FRONT.md`
  `families/FAMILY_qshrink_athena_internal_use_route_map.md`
  `families/FAMILY_athena_fleet_route_map.md`
  `families/FAMILY_orgin_route_map.md`
  `manifests/NEXT_SELF_PROMPT.md`
  `../receipts/2026-03-13_q42_flower_pass_activation.md`
- Witness:
  one Flower-core proof bundle showing `M1/M3/M4/M5 = OK`, one explicit blocked external Docs overlay on `M2`, one atlas refresh, and one restart-safe Cloud handoff
- Writeback:
  quest board, requests board, change feed, active queue, weakest-front queue, next-self-prompt, and receipt
- Next Seed:
  keep `Q42` open on `{FLOWER_SUBFRONT}` as the highest executable Hall-side frontier, keep `Q02` blocked while OAuth is missing, keep `TQ04` as the deeper Temple receiver, and emit `{CLOUD_SUBFRONT}` only after Flower closure is witnessed
"""


def render_qshrink_active_front() -> str:
    return f"""# QSHRINK ACTIVE FRONT

## FrontID

`Q42`

## Quest

Activate The First QSHRINK Agent Sweep

## State

`OPEN`

## Truth

`OK`

## Coordination membrane

`Q41 / TQ06`

## Active subfront

`{FLOWER_SUBFRONT}`

## Next Seed

`{CLOUD_SUBFRONT}`

## Next Temple handoff

`TQ04: Bind The Helical Schema Pack To A Runner Contract`

## Reserve frontier

`Q45`

## Blocked external front

`Q02`

## Docs gate

`BLOCKED`
"""


def restore_qshrink_active_front() -> None:
    write_text(QSHRINK_ACTIVE_FRONT_PATH, render_qshrink_active_front())


def authority_front_state() -> Dict[str, str]:
    if not QSHRINK_ACTIVE_FRONT_PATH.exists():
        return {"active_subfront": "", "next_seed": ""}
    text = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    active_subfront_match = re.search(r"## Active subfront\s+`([^`]+)`", text, flags=re.S)
    next_seed_match = re.search(r"## Next Seed\s+`([^`]+)`", text, flags=re.S)
    return {
        "active_subfront": active_subfront_match.group(1) if active_subfront_match else "",
        "next_seed": next_seed_match.group(1) if next_seed_match else "",
    }


def should_write_live_flower_control_surfaces() -> bool:
    authority_state = authority_front_state()
    return (
        authority_state["active_subfront"] == FLOWER_SUBFRONT
        and authority_state["next_seed"] == CLOUD_SUBFRONT
    )


def replace_q42_queue_block() -> None:
    text = read_text(ACTIVE_QUEUE_PATH)
    pattern = r"### FRONT-Q42-QSHRINK-AGENT-SWEEP\n.*?(?=\n### FRONT-|\Z)"
    updated = re.sub(pattern, render_q42_queue_block().rstrip() + "\n\n", text, flags=re.S)
    write_text(ACTIVE_QUEUE_PATH, updated)


def update_weakest_front_queue() -> None:
    write_text(
        WEAKEST_FRONT_QUEUE_PATH,
        """# WEAKEST FRONT QUEUE

Use `22_control_plane_grammar.md` when reopening any ranked front below.

## FrontID

`FRONT-WEAKEST-RANKING`

## Quest

Weakest-front reopen control

## State

`ACTIVE`

## Truth

`NEAR`

## Objective

Keep the organism reopening the highest local-witness front instead of drifting into heat-only
expansion.

## Why Now

`Q05` reduced grammar drift, so the next queue must rank real remaining pressure rather than
schema noise.

## Targets

- `FRONT-Q02-LIVE-DOCS`
- `FRONT-Q42-QSHRINK-AGENT-SWEEP`
- `Q45`

## Witness

One ranked list that matches queue, manifest, and Guild Hall priorities.

## Writeback

- `06_active_queue.md`
- `manifests/DEEPER_ENHANCEMENT_ACTIVE_FRONT.md`
- `DEEPER CRYSTALIZATION/ACTIVE_NERVOUS_SYSTEM/07_FULL_PROJECT_INTEGRATION_256/08_GUILD_HALL/06_CAMPAIGN_STATUS.md`

## Current Ranking

1. `FRONT-Q02-LIVE-DOCS`
2. `FRONT-Q42-QSHRINK-AGENT-SWEEP`
3. `Q45`

## Next Seed

Advance `FRONT-Q42-QSHRINK-AGENT-SWEEP` as the highest local frontier that can gain witness now that the wave-2 qshrink and Athena FLEET bundles are atlas-backed and replay-safe.
""",
    )


def update_next_self_prompt() -> None:
    write_text(
        NEXT_SELF_PROMPT_PATH,
        f"""# Next Self Prompt

## Current Restart Seed

`2026-03-13 America/Los_Angeles: preserve blocked-Docs honesty, run a Q41/TQ06 freshness-and-alignment sweep first, keep FRONT-Q42-QSHRINK-AGENT-SWEEP active on {FLOWER_SUBFRONT} as the highest executable Hall-side frontier, preserve {CLOUD_SUBFRONT} as the sole next Hall restart seed, keep TQ04 as the deeper Temple receiver, keep Q45 reserve-only, and keep Q02 blocked unless OAuth material appears.`

## Prompt

```text
You are continuing the Athena nervous-system build in recursive swarm mode.

Start at the beginning again.

1. Check the live Docs gate first.
2. If blocked, preserve the blocker exactly and pivot immediately to the strongest local executable frontier instead of inventing live-memory progress.
3. Read `../../../../NERVOUS_SYSTEM/95_MANIFESTS/ACTIVE_RUN.md`, `../../../../NERVOUS_SYSTEM/95_MANIFESTS/BUILD_QUEUE.md`, `manifests/WEAKEST_FRONT_QUEUE.md`, `../ATHENA TEMPLE/MANIFESTS/TEMPLE_STATE.md`, and `06_active_queue.md` as the canonical queue-first control pass.
4. Read `manifests/QSHRINK_ACTIVE_FRONT.md`, `../ATHENA TEMPLE/MANIFESTS/16_LOOP_PROGRESS.md`, `manifests/STATE_HEADER.md`, and `manifests/RESTART_ENGINE.md` before promoting any frontier.
5. Read scheduler packets or Hall freshness surfaces only if the pass promotes a frontier, emits a new quest, or needs cadence-level drift repair.
6. If the task is helical recursion, typed `2/16 <-> 14/16` equivalence, sparse swarm architecture, or lift-law compilation, also read `../../../../NERVOUS_SYSTEM/70_SCHEMAS/06_HELICAL_LOOPSPEC_16_RING.md`, `../../../../NERVOUS_SYSTEM/70_SCHEMAS/07_PHASE_SPEC_2_TO_14_MACHINE.md`, `../../../../NERVOUS_SYSTEM/70_SCHEMAS/08_VIRTUAL_SWARM_SPEC_16X16.md`, `../../../../NERVOUS_SYSTEM/70_SCHEMAS/09_IMPROVEMENT_LEDGER_SPEC.md`, and `../../../../NERVOUS_SYSTEM/70_SCHEMAS/10_LIFT_SPEC_ONE_EIGHTH_HELIX.md`.
7. Treat `Q41` as already promoted and `TQ06` as the active packet-fed hourly coupling frontier; do not reopen quarter-hour language as current cadence truth.
8. Choose the strongest next frontier in this order:
   - `Q41` / `TQ06` freshness-and-alignment sweep as the active control membrane
   - `Q42 -> {FLOWER_SUBFRONT}` as the highest executable Hall-side contraction followthrough
   - `next_seed / next_connectivity_quest / restart_seed = {CLOUD_SUBFRONT}` as the sole next Hall seed and never as current execution
   - `TQ04` as the deeper Temple receiving frontier after Hall-side Flower and Cloud alignment remain lawful
   - `Q45` only as a reserve after `Q42`, `{CLOUD_SUBFRONT}`, and `TQ04` remain aligned
   - `Q02` only if the Docs gate becomes real
9. Produce one lawful artifact-backed move before ending the pass; do not stop at analysis.
10. If the pass promotes a frontier or emits a new quest, run Hall and Temple freshness checks before lifting it into canonical governance.
11. Keep replay, truth, and routing language explicit. Do not let later-stage Cloud, Fractal, or Square wording override the current Flower-active truth unless fresh witnesses lawfully promote them.
12. End by emitting one new restart seed that reflects the post-pass truth.

Helical law:
- preserve the blocked Docs gate honestly
- preserve Q41/TQ06 as the active coordination membrane
- preserve Q42 Flower as the highest executable local frontier
- preserve Cloud as the sole next Hall seed and not current execution
- preserve TQ04 as the next deeper Temple receiver after Hall-side alignment holds
- preserve Q45 as reserve-only
- preserve Q02 as blocked unless OAuth appears

Preferred frontier order:
1. one `Q41` / `TQ06` freshness-and-alignment sweep
2. one `Q42` Flower pass through `{FLOWER_SUBFRONT}`
3. one Hall-seed justification pass that keeps `{CLOUD_SUBFRONT}` next and not current
4. one `TQ04` runner-contract receiving pass after Hall-side alignment holds
5. one `Q45` reserve-only pass if pressure stays local and lawful
6. one `Q02` live-memory bootstrap prerequisite pass if OAuth material appears
```
""",
    )


def render_qshrink_family() -> str:
    return f"""# FAMILY QSHRINK Internal Use

Date: `2026-03-13`
Truth: `OK`

## Role

QSHRINK remains Athena's contraction organ. The live control story is flower-first:
`Q41 / TQ06` stays the active coordination membrane, `Q42` stays active on
`{FLOWER_SUBFRONT}` as the highest executable Hall-side frontier, `{CLOUD_SUBFRONT}`
stays the sole next Hall seed, `TQ04` stays the deeper Temple receiver, `Q45` stays
reserve-only, and `Q02` stays blocked while OAuth material is absent.

## Control Plane

- Front ID: `Q42`
- Coordination membrane: `Q41 / TQ06`
- Active Hall-side frontier: `{FLOWER_SUBFRONT}`
- Next Hall seed: `{CLOUD_SUBFRONT}`
- Deeper Temple receiver: `TQ04: Bind The Helical Schema Pack To A Runner Contract`
- Reserve frontier: `Q45`
- Blocked external front: `Q02`
- Docs gate: `BLOCKED` / `blocked-by-missing-credentials`

## Closure Law

- Flower truth: `OK`
- Cloud truth: `NEXT ONLY`
- Fractal truth: `DOWNSTREAM ONLY`
- Square truth: `DOWNSTREAM ONLY`
- Immediate Hall execution: `Flower closure and writeback`
- Immediate Temple execution: `receiver only; do not make current`
"""


def update_qshrink_family() -> None:
    write_text(QSHRINK_FAMILY_PATH, render_qshrink_family())


def render_qshrink_route_map() -> str:
    return f"""# FAMILY QSHRINK Athena Internal Use Route Map

## Current Route

`Q41 / TQ06 -> Q42 -> {FLOWER_SUBFRONT} -> {CLOUD_SUBFRONT} -> TQ04: Bind The Helical Schema Pack To A Runner Contract -> Q45 (reserve only)`

## Control Fields

- coordination membrane: `Q41 / TQ06`
- active Hall-side frontier: `{FLOWER_SUBFRONT}`
- next Hall seed: `{CLOUD_SUBFRONT}`
- deeper Temple receiver: `TQ04: Bind The Helical Schema Pack To A Runner Contract`
- reserve frontier: `Q45`
- blocked external front: `Q02`
- docs gate: `BLOCKED`

## Cadence Law

- `R1 Hall execution rail`: `Q42 -> {FLOWER_SUBFRONT}` / `current executable frontier`
- `R2 Hall seed rail`: `{CLOUD_SUBFRONT}` / `next only`
- `R3 Temple receiver rail`: `TQ04: Bind The Helical Schema Pack To A Runner Contract` / `deeper handoff after Hall-side alignment`
- `R4 reserve rail`: `Q45` / `reserve-only`
- `R5 blocker overlay rail`: `Trading Bot -> live_docs_gate_status -> Hall truth` / `external-blocker-overlay`

## Cloud Ranking

- `P1 Docs blocker overlay`: `PINNED_BLOCKER` / `FAIL`
- `P2 Flower closure and writeback`: `CURRENT_EXECUTABLE` / `OK`
- `P3 Cloud seed justification`: `NEXT_SEED` / `NEAR`
- `P4 Temple runner handoff`: `RECEIVER_ONLY` / `OK`
- `P5 reserve growth`: `RESERVE_ONLY` / `NEAR`

## Recursive Law

- `F1 external blocker loop`: `Trading Bot / Docs gate`
- `F2 current Hall loop`: `Q42 with {FLOWER_SUBFRONT}`
- `F3 next Hall seed loop`: `{CLOUD_SUBFRONT}`
- `F4 Temple receiver loop`: `TQ04: Bind The Helical Schema Pack To A Runner Contract`
- `F5 reserve loop`: `Q45`
"""


def update_qshrink_route_map() -> None:
    write_text(QSHRINK_ROUTE_MAP_PATH, render_qshrink_route_map())


def render_temple_state() -> str:
    return f"""# Temple State

Date: `2026-03-13`
Last Run Stamp: `2026-03-13 America/Los_Angeles`
Temple Status: `ONLINE`

## FrontID

`TQ06-GUILDMASTER-HOURLY-PACKET-COUPLING`

## Quest

`TQ06: Install The Packet-Fed Guildmaster Coupling Loop`

## State

`ACTIVE`

## Truth

`OK`

## Active Lens

- Packet vote: `Q41 / TQ06 x3`
- Contraction minority: `Q42 x2`
- NEXT^4 scope: `Q45 reserve-only; Q02 blocked external`
- Mode: `hourly packet-fed control loop`
- Active coordination membrane: `Q41 / TQ06`
- Current Hall-side subfront: `Q42 -> {FLOWER_SUBFRONT}`
- Next Hall restart seed: `{CLOUD_SUBFRONT}`
- Next Temple receiver: `TQ04 - Bind The Helical Schema Pack To A Runner Contract`
- Reserve frontier: `Q45`
- Docs gate: `BLOCKED`
- Legacy note: `T14` remains the founding short-cadence drift-closure law, and `T16` remains the active cadence-binding law

## Objective

Bind the High Priest totality pressure to a recurring hourly packet-fed Guildmaster loop that:

1. rereads the whole organism
2. keeps the current Hall-side QSHRINK work truthful
3. preserves `{CLOUD_SUBFRONT}` as the next Hall seed without making it current too early
4. keeps the deeper Temple gate as a separate receiver frontier
5. keeps blocked Docs truth visible

## Why Now

The green Flower verification already exists on disk, so the honest followthrough is no
longer to narrate Fractal or Square as current work. The honest followthrough is to keep
the Hall-side present tense lawful: `Q42 -> {FLOWER_SUBFRONT}` remains current,
`{CLOUD_SUBFRONT}` remains next-only, `TQ04` remains the deeper receiver, `Q45`
remains reserve-only, and `Q02` remains externally blocked while OAuth material is absent.

## Witness

TQ04 remains the landed contract witness through `self_actualize/helical_runner_contract.json`.

- the paired verifier exists at `self_actualize/helical_runner_contract_verification.json`
- the human-readable contract surface now lives at `NERVOUS_SYSTEM/95_MANIFESTS/TQ04_HELICAL_RUNNER_CONTRACT.md`
- the current Hall-side proof bundle lives at `self_actualize/q42_flower_pass_verification.json`

## Current Blockers

- live Google Docs gate still blocked by missing OAuth files
- `Q42` still needs Hall-side Flower closure and writeback to stay fresh
- `{CLOUD_SUBFRONT}` must stay next seed only until Hall-side freshness remains aligned

## Carried Fronts

- `TQ05` remains the totality umbrella and its active contradiction band is externalized through `Q39`
- `TQ06` remains the active hourly packet-fed coupling frontier
- `TQ04` remains the deeper runner-contract receiver
- `Q42` remains the Hall-side feeder on `{FLOWER_SUBFRONT}`

## Hall Coupling Delta

The Hall and Temple now share one live control story:

- `Q41 / TQ06` remains the active coordination membrane
- `Q42` remains open as the Hall umbrella frontier on `{FLOWER_SUBFRONT}`
- `{CLOUD_SUBFRONT}` remains the sole next Hall restart seed
- `TQ04` remains the deeper Temple receiver
- `Q45` remains reserve-only
- `Q02` remains externally blocked

## Restart Seed

`Keep Q41/TQ06 active as the hourly packet-fed coordination membrane, keep Q42 active on {FLOWER_SUBFRONT}, preserve {CLOUD_SUBFRONT} as the sole next Hall restart seed, keep TQ04 as the deeper Temple receiver, keep Q45 reserve-only, and keep Q02 externally blocked while the Docs gate remains BLOCKED.`
"""


def update_temple_state() -> None:
    write_text(TEMPLE_STATE_PATH, render_temple_state())


def update_active_run_manifest() -> None:
    text = read_text(ACTIVE_RUN_PATH)
    old_objective_bullet = (
        "- the `TQ04` helical runner contract so the canonical schema pack now binds directly into Hall/Temple execution "
        "and releases `QS64-21` only as the next Hall seed behind current `Q42` Fractal carrythrough"
    )
    new_objective_bullet = (
        "- the `TQ04` helical runner contract so the canonical schema pack now binds directly into Hall/Temple execution "
        "while `Q41` / `TQ06` remains the active coordination membrane, `Q42` stays current on "
        f"`{FLOWER_SUBFRONT}`, `{CLOUD_SUBFRONT}` stays the sole next Hall seed, `TQ04` stays the deeper receiver, "
        "`Q45` stays reserve-only, and `Q02` stays blocked until OAuth material appears"
    )
    if old_objective_bullet not in text:
        raise ValueError("ACTIVE_RUN.md no longer contains the expected stale TQ04 objective bullet.")
    text = text.replace(old_objective_bullet, new_objective_bullet, 1)

    old_next_output_bullet = (
        "- keep `Q42` current on `QS64-21 Connectivity-Refine-Square`, preserve `QS64-20 Connectivity-Diagnose-Fractal` "
        "as the landed upstream witness, release `QS64-22 Connectivity-Refine-Flower` as the sole next Hall seed, "
        "keep Athena OS runtime promoted-current, and only then deepen `P3` or later Hall-side followthrough"
    )
    new_next_output_bullet = (
        f"- keep `Q41` / `TQ06` as the active coordination membrane, keep `Q42` current on `{FLOWER_SUBFRONT}`, "
        f"preserve `{CLOUD_SUBFRONT}` as the sole next Hall seed, keep `TQ04` as the deeper Temple receiver, keep "
        "`Q45` reserve-only, keep `Q02` blocked while OAuth is missing, keep Athena OS runtime promoted-current, "
        "and only then deepen later Hall-side followthrough"
    )
    if old_next_output_bullet not in text:
        raise ValueError("ACTIVE_RUN.md no longer contains the expected stale Q42 next-output bullet.")
    text = text.replace(old_next_output_bullet, new_next_output_bullet, 1)
    write_text(ACTIVE_RUN_PATH, text)


def update_build_queue_manifest() -> None:
    text = read_text(BUILD_QUEUE_PATH)
    old_priority_line = (
        "8. **Wave 2 runtime activation**: keep `Q42` aligned on landed `QS64-20`, active `QS64-21`, and next "
        "`QS64-22` while routing Athena FLEET corridor traffic, identity continuity, and ORGIN readable-mirror "
        "traffic through the new atlas-backed bundles"
    )
    new_priority_line = (
        f"8. **Wave 2 runtime activation**: keep `Q41` / `TQ06` as the active coordination membrane, keep `Q42` "
        f"aligned on current `{FLOWER_SUBFRONT}`, keep `{CLOUD_SUBFRONT}` as the sole next Hall seed, keep `TQ04` "
        "as the deeper Temple receiver, keep `Q45` reserve-only, keep `Q02` blocked until OAuth appears, and route "
        "Athena FLEET corridor traffic, identity continuity, and ORGIN readable-mirror traffic through the new "
        "atlas-backed bundles"
    )
    if old_priority_line not in text:
        raise ValueError("BUILD_QUEUE.md no longer contains the expected stale Q42 priority line.")
    text = text.replace(old_priority_line, new_priority_line, 1)

    anchor_line = "- prune stale route drift before it hardens into more ledgers and skills"
    insertion = (
        "- keep `Q41` / `TQ06` as the active coordination membrane, keep `Q42` current on "
        f"`{FLOWER_SUBFRONT}`, keep `{CLOUD_SUBFRONT}` next-only, keep `TQ04` as the deeper Temple receiver, keep "
        "`Q45` reserve-only, and keep `Q02` blocked while OAuth is absent"
    )
    if insertion not in text:
        if anchor_line not in text:
            raise ValueError("BUILD_QUEUE.md no longer contains the expected active control-plane anchor line.")
        text = text.replace(anchor_line, anchor_line + "\n" + insertion, 1)
    write_text(BUILD_QUEUE_PATH, text)


def render_manifest(outputs: Dict[str, str], module_runs: List[Dict[str, Any]]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    run_lines = "\n".join(
        f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`"
        for run in module_runs
    )
    return f"""# Q42 FLOWER PASS MANIFEST

Date: `2026-03-13`
Derivation: `{DERIVATION_COMMAND}`
Wave: `Q42 / QS64-18 Connectivity-Diagnose-Flower`

## Law

- close Flower locally through `M1`, `M3`, `M4`, and `M5`
- keep `M2` explicit as an external blocked Docs overlay
- atlas-index new authority surfaces before they claim freshness
- emit `{CLOUD_SUBFRONT}` as the sole next restart seed

## Outputs

{output_lines}

## Downstream reruns

{run_lines}
"""


def render_dashboard(payload: Dict[str, Any]) -> str:
    verifier_truth = payload.get("verifier_truth", {})
    return f"""# Q42 FLOWER PASS DASHBOARD

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Corridor

- flower core status: `{payload['flower_core_status']}`
- external gate overlay: `{payload['external_gate_overlay_status']}`
- flower activation status: `{payload['flower_activation_status']}`
- cloud truth: `{payload['cloud_truth']}`

## Docs gate

- status: `{payload['docs_gate_status']}`

## Verifiers

- `QSHRINK`: `{verifier_truth.get('qshrink_runtime_verification', 'UNKNOWN')}`
- `AQM`: `{verifier_truth.get('aqm_runtime_lane', 'UNKNOWN')}`
- `ATLAS FORGE`: `{verifier_truth.get('atlasforge_runtime_lane', 'UNKNOWN')}`
- `runtime waist`: `{verifier_truth.get('runtime_waist', 'UNKNOWN')}`

## Next seed

`{payload['next_restart_seed']}`
"""


def render_verification(payload: Dict[str, Any]) -> str:
    check_lines = "\n".join(f"- `{name}`: `{value}`" for name, value in payload["checks"].items())
    unresolved_lines = "\n".join(f"- {item}" for item in payload["unresolved"]) or "- none"
    return f"""# Q42 FLOWER PASS VERIFICATION

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Checks

{check_lines}

## Unresolved

{unresolved_lines}
"""


def render_runtime(outputs: Dict[str, str], verification: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# 32 Q42 FLOWER PASS ACTIVATION RUNTIME

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{verification['docs_gate_status']}`

## Outputs

{output_lines}
"""


def render_receipt(
    membrane: RuntimeCorridorMembraneRecord,
    seed_packet: SeedPacketWitnessRecord,
    verification: Dict[str, Any],
    module_runs: List[Dict[str, Any]],
) -> str:
    run_lines = "\n".join(
        f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`"
        for run in module_runs
    )
    unresolved_lines = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# 2026-03-13 q42 flower pass activation

- truth: `{verification['truth']}`
- docs gate: `{verification['docs_gate_status']}`
- flower core status: `{verification['flower_core_status']}`
- next seed: `{verification['next_restart_seed']}`

## Landed witnesses

- runtime membrane: `{membrane.corridor_id}` / `{membrane.truth_state}`
- seed packet: `{seed_packet.packet_witness_id}` / `{seed_packet.truth_state}`

## Downstream reruns

{run_lines}

## Honest limits

{unresolved_lines}
"""


def build_verification(generated_paths: List[Path], module_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    flower = load_json(FLOWER_JSON_PATH)
    network = load_json(NETWORK_JSON_PATH)
    cloud = load_json(CLOUD_JSON_PATH)
    agent_matrix = load_json(AGENT_MATRIX_PATH)
    atlas = load_json(CORPUS_ATLAS_PATH)
    atlas_paths = {record.get("relative_path") for record in atlas.get("records", [])}
    generated_relative = [relative_string(path) for path in generated_paths if path.exists()]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    queue_text = read_text(ACTIVE_QUEUE_PATH)
    next_prompt_text = read_text(NEXT_SELF_PROMPT_PATH)
    weakest_front_text = read_text(WEAKEST_FRONT_QUEUE_PATH)
    temple_state_text = read_text(TEMPLE_STATE_PATH)
    active_run_text = read_text(ACTIVE_RUN_PATH)
    build_queue_text = read_text(BUILD_QUEUE_PATH)
    qshrink_family_text = read_text(QSHRINK_FAMILY_PATH)
    qshrink_route_text = read_text(QSHRINK_ROUTE_MAP_PATH)
    fleet_route_text = read_text(ATHENA_FLEET_ROUTE_MAP_PATH)
    orgin_route_text = read_text(ORGIN_ROUTE_MAP_PATH)
    active_front_text = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    authority_state = authority_front_state()
    q42_queue_block = re.search(
        r"### FRONT-Q42-QSHRINK-AGENT-SWEEP\n.*?(?=\n### FRONT-|\Z)",
        queue_text,
        flags=re.S,
    )
    q42_queue_text = q42_queue_block.group(0) if q42_queue_block else ""
    control_surfaces_text = "\n".join(
        [
            active_front_text,
            next_prompt_text,
            temple_state_text,
            build_queue_text,
            qshrink_family_text,
            qshrink_route_text,
        ]
    )

    verifier_truth = {
        "qshrink_runtime_verification": load_json(QSHRINK_STACK_VERIFY_PATH).get("truth", "UNKNOWN"),
        "aqm_runtime_lane": load_json(AQM_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "atlasforge_runtime_lane": load_json(ATLASFORGE_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "runtime_waist": load_json(RUNTIME_WAIST_PATH).get("truth", "UNKNOWN"),
    }

    checks = {
        "runtime_membrane_ok": load_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH).get("truth_state") == "OK",
        "seed_packet_ok": load_json(ORGIN_SEED_PACKET_JSON_PATH).get("truth_state") == "OK",
        "flower_core_status_ok": flower.get("flower_core_status") == "OK",
        "external_gate_overlay_blocked": flower.get("external_gate_overlay_status") == "blocked-by-missing-credentials",
        "flower_activation_status_ok": flower.get("flower_activation_status") == "OK",
        "authority_active_subfront_flower": authority_state["active_subfront"] == FLOWER_SUBFRONT,
        "authority_next_seed_cloud": authority_state["next_seed"] == CLOUD_SUBFRONT,
        "network_active_subfront_flower": network.get("active_subfront") == FLOWER_SUBFRONT,
        "network_next_seed_cloud": network.get("next_seed") == CLOUD_SUBFRONT,
        "agent_matrix_active_subfront_flower": agent_matrix.get("active_subfront") == FLOWER_SUBFRONT,
        "agent_matrix_next_cloud": agent_matrix.get("next_connectivity_quest") == CLOUD_SUBFRONT,
        "active_front_aligned": FLOWER_SUBFRONT in active_front_text and f"`{CLOUD_SUBFRONT}`" in active_front_text,
        "active_queue_aligned": FLOWER_SUBFRONT in q42_queue_text and CLOUD_SUBFRONT in q42_queue_text and "TQ04" in q42_queue_text,
        "next_prompt_aligned": (
            FLOWER_SUBFRONT in next_prompt_text
            and "`Q41` / `TQ06` freshness-and-alignment sweep" in next_prompt_text
            and f"`next_seed / next_connectivity_quest / restart_seed = {CLOUD_SUBFRONT}`" in next_prompt_text
            and "`Q45` only as a reserve" in next_prompt_text
            and "`Q44` organism-wave proof pass" not in next_prompt_text
        ),
        "temple_state_aligned": (
            f"`Q42 -> {FLOWER_SUBFRONT}`" in temple_state_text
            and f"`{CLOUD_SUBFRONT}`" in temple_state_text
            and "`Q41 / TQ06`" in temple_state_text
            and "`Q45`" in temple_state_text
            and "`Q02`" in temple_state_text
        ),
        "active_run_aligned": (
            f"`Q42` current on `{FLOWER_SUBFRONT}`" in active_run_text
            and f"`{CLOUD_SUBFRONT}` as the sole next Hall seed" in active_run_text
            and "`Q41` / `TQ06` as the active coordination membrane" in active_run_text
            and "`Q45` reserve-only" in active_run_text
            and "`Q02` blocked" in active_run_text
        ),
        "build_queue_aligned": (
            f"`Q42` aligned on current `{FLOWER_SUBFRONT}`" in build_queue_text
            and f"`{CLOUD_SUBFRONT}` as the sole next Hall seed" in build_queue_text
            and "`Q45` reserve-only" in build_queue_text
            and "`Q02` blocked" in build_queue_text
        ),
        "weakest_front_ranked_q45": (
            "1. `FRONT-Q02-LIVE-DOCS`" in weakest_front_text
            and "2. `FRONT-Q42-QSHRINK-AGENT-SWEEP`" in weakest_front_text
            and "3. `Q45`" in weakest_front_text
            and "3. `Q44`" not in weakest_front_text
        ),
        "qshrink_family_aligned": (
            FLOWER_SUBFRONT in qshrink_family_text
            and CLOUD_SUBFRONT in qshrink_family_text
            and "`Q41 / TQ06`" in qshrink_family_text
            and "`Q45`" in qshrink_family_text
        ),
        "qshrink_route_map_aligned": FLOWER_SUBFRONT in qshrink_route_text and CLOUD_SUBFRONT in qshrink_route_text,
        "fleet_route_map_aligned": CLOUD_SUBFRONT in fleet_route_text and "external gate overlay" in fleet_route_text.lower(),
        "orgin_route_map_aligned": CLOUD_SUBFRONT in orgin_route_text and "seed packet witness" in orgin_route_text.lower(),
        "cloud_surface_consistent": cloud.get("truth") in {"OK", "NEAR"} and cloud.get("active_subfront") == CLOUD_SUBFRONT and cloud.get("next_seed") == FRACTAL_SUBFRONT,
        "no_stale_current_terms": all(
            term not in control_surfaces_text
            for term in ["QS64-20 Connectivity-Diagnose-Fractal", "QS64-21", "QS64-22", "`Q46`"]
        ),
        "atlas_refresh_complete": not atlas_missing,
        "downstream_reruns_green": all(run["ok"] for run in module_runs),
        "runtime_verifiers_green": all(value == "OK" for value in verifier_truth.values()),
        "docs_gate_preserved_blocked": docs_gate_status() == "blocked-by-missing-credentials",
    }
    unresolved: List[str] = []
    if docs_gate_status() != "blocked-by-missing-credentials":
        unresolved.append("Docs gate no longer matches the expected blocked-by-missing-credentials state.")
    if atlas_missing:
        unresolved.append("One or more Flower-pass surfaces are still missing from corpus_atlas.json.")
    if cloud.get("active_subfront") != CLOUD_SUBFRONT or cloud.get("next_seed") != FRACTAL_SUBFRONT:
        unresolved.append("Cloud no longer preserves the expected downstream handoff from Flower into Fractal.")
    if any(term in control_surfaces_text for term in ["QS64-20 Connectivity-Diagnose-Fractal", "QS64-21", "QS64-22", "`Q46`"]):
        unresolved.append("One or more current-state control surfaces regressed into stale Fractal/Square or Q46 wording.")
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if all(checks.values()) else "FAIL",
        "docs_gate_status": docs_gate_status(),
        "flower_core_status": flower.get("flower_core_status", "NEAR"),
        "external_gate_overlay_status": flower.get("external_gate_overlay_status", "UNKNOWN"),
        "flower_activation_status": flower.get("flower_activation_status", "NEAR"),
        "cloud_truth": cloud.get("truth", "UNKNOWN"),
        "checks": checks,
        "verifier_truth": verifier_truth,
        "atlas_refresh_pending_paths": atlas_missing,
        "next_restart_seed": CLOUD_SUBFRONT,
        "unresolved": unresolved,
    }


def build_dashboard(verification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "truth": verification["truth"],
        "flower_core_status": verification["flower_core_status"],
        "external_gate_overlay_status": verification["external_gate_overlay_status"],
        "flower_activation_status": verification["flower_activation_status"],
        "cloud_truth": verification["cloud_truth"],
        "docs_gate_status": verification["docs_gate_status"],
        "verifier_truth": verification["verifier_truth"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def main() -> int:
    restore_qshrink_active_front()
    runtime_membrane = build_runtime_membrane()
    seed_packet = build_seed_packet_witness()

    write_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH, runtime_membrane.to_dict())
    write_json(QSHRINK_RUNTIME_MEMBRANE_JSON_MIRROR, runtime_membrane.to_dict())
    write_json(ORGIN_SEED_PACKET_JSON_PATH, seed_packet.to_dict())
    write_json(ORGIN_SEED_PACKET_JSON_MIRROR, seed_packet.to_dict())
    write_text(RUNTIME_MEMBRANE_MD_PATH, render_runtime_membrane_markdown(runtime_membrane))
    write_text(SEED_PACKET_MD_PATH, render_seed_packet_markdown(seed_packet))
    write_text(ORGIN_ROUTE_MAP_PATH, render_orgin_route_map(seed_packet))

    derivation_runs = [
        run_module("self_actualize.runtime.derive_qshrink_connectivity_flower"),
        run_module("self_actualize.runtime.derive_qshrink_connectivity_cloud"),
        run_module("self_actualize.runtime.derive_qshrink_network_integration_flower"),
        run_module("self_actualize.runtime.derive_qshrink_agent_task_matrix_flower"),
    ]

    restore_qshrink_active_front()

    if should_write_live_flower_control_surfaces():
        replace_q42_queue_block()
        update_weakest_front_queue()
        update_next_self_prompt()
        update_qshrink_family()
        update_qshrink_route_map()
        update_temple_state()
        update_active_run_manifest()
        update_build_queue_manifest()

    outputs = {
        "runtime_membrane_json": relative_string(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
        "seed_packet_json": relative_string(ORGIN_SEED_PACKET_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
        "weakest_front_queue": relative_string(WEAKEST_FRONT_QUEUE_PATH),
        "qshrink_active_front": relative_string(QSHRINK_ACTIVE_FRONT_PATH),
        "next_self_prompt": relative_string(NEXT_SELF_PROMPT_PATH),
        "temple_state": relative_string(TEMPLE_STATE_PATH),
        "active_run": relative_string(ACTIVE_RUN_PATH),
        "build_queue": relative_string(BUILD_QUEUE_PATH),
        "qshrink_family": relative_string(QSHRINK_FAMILY_PATH),
        "qshrink_route_map": relative_string(QSHRINK_ROUTE_MAP_PATH),
    }

    provisional_verification = {
        "generated_at": utc_now(),
        "truth": "NEAR",
        "docs_gate_status": docs_gate_status(),
        "flower_core_status": "NEAR",
        "external_gate_overlay_status": docs_gate_status(),
        "flower_activation_status": "NEAR",
        "cloud_truth": "NEAR",
        "checks": {},
        "verifier_truth": {},
        "next_restart_seed": CLOUD_SUBFRONT,
        "unresolved": ["Flower-pass atlas refresh pending."],
    }
    provisional_dashboard = build_dashboard(provisional_verification)

    write_json(DASHBOARD_JSON_PATH, provisional_dashboard)
    write_json(DASHBOARD_JSON_MIRROR, provisional_dashboard)
    write_json(VERIFICATION_JSON_PATH, provisional_verification)
    write_json(VERIFICATION_JSON_MIRROR, provisional_verification)
    write_text(MANIFEST_MD_PATH, render_manifest(outputs, derivation_runs))
    write_text(DASHBOARD_MD_PATH, render_dashboard(provisional_dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(provisional_verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, provisional_verification))
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_membrane, seed_packet, provisional_verification, derivation_runs))

    generated_paths = [
        QSHRINK_RUNTIME_MEMBRANE_JSON_PATH,
        QSHRINK_RUNTIME_MEMBRANE_JSON_MIRROR,
        ORGIN_SEED_PACKET_JSON_PATH,
        ORGIN_SEED_PACKET_JSON_MIRROR,
        RUNTIME_MEMBRANE_MD_PATH,
        SEED_PACKET_MD_PATH,
        ORGIN_ROUTE_MAP_PATH,
        DASHBOARD_JSON_PATH,
        DASHBOARD_JSON_MIRROR,
        VERIFICATION_JSON_PATH,
        VERIFICATION_JSON_MIRROR,
        MANIFEST_MD_PATH,
        DASHBOARD_MD_PATH,
        VERIFICATION_MD_PATH,
        RUNTIME_MD_PATH,
        RECEIPT_MD_PATH,
        ACTIVE_QUEUE_PATH,
        NEXT_SELF_PROMPT_PATH,
        WEAKEST_FRONT_QUEUE_PATH,
        TEMPLE_STATE_PATH,
        ACTIVE_RUN_PATH,
        BUILD_QUEUE_PATH,
        QSHRINK_ACTIVE_FRONT_PATH,
        QSHRINK_FAMILY_PATH,
        QSHRINK_ROUTE_MAP_PATH,
        ATHENA_FLEET_ROUTE_MAP_PATH,
        FLOWER_JSON_PATH,
        NETWORK_JSON_PATH,
        CLOUD_JSON_PATH,
        AGENT_MATRIX_PATH,
    ]
    refresh_corpus_atlas(generated_paths)

    downstream_runs = derivation_runs

    verification = build_verification(generated_paths, downstream_runs)
    dashboard = build_dashboard(verification)

    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_membrane, seed_packet, verification, downstream_runs))

    refresh_corpus_atlas(
        [
            DASHBOARD_JSON_PATH,
            DASHBOARD_JSON_MIRROR,
            VERIFICATION_JSON_PATH,
            VERIFICATION_JSON_MIRROR,
            DASHBOARD_MD_PATH,
            VERIFICATION_MD_PATH,
            RUNTIME_MD_PATH,
            RECEIPT_MD_PATH,
            ACTIVE_QUEUE_PATH,
            NEXT_SELF_PROMPT_PATH,
            WEAKEST_FRONT_QUEUE_PATH,
            TEMPLE_STATE_PATH,
            ACTIVE_RUN_PATH,
            BUILD_QUEUE_PATH,
            ORGIN_ROUTE_MAP_PATH,
            QSHRINK_ACTIVE_FRONT_PATH,
            QSHRINK_FAMILY_PATH,
            QSHRINK_ROUTE_MAP_PATH,
            ATHENA_FLEET_ROUTE_MAP_PATH,
        ]
    )

    print(f"Wrote Q42 Flower-pass activation artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
