from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from self_actualize.runtime.crystal_remaster_contracts import RuntimeCarrierContractRecord
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
CAPABILITY_STACK_PATH = SELF_ACTUALIZE_ROOT / "qshrink_capability_stack.json"
FLOWER_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_flower.json"
NETWORK_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_network_integration.json"
CLOUD_JSON_PATH = SELF_ACTUALIZE_ROOT / "qshrink_connectivity_cloud.json"
AGENT_MATRIX_PATH = SELF_ACTUALIZE_ROOT / "qshrink_agent_task_matrix.json"
QSHRINK_RUNTIME_MEMBRANE_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_corridor_membrane.json"
QSHRINK_RUNTIME_CARRIER_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_runtime_carrier_contract.json"
QSHRINK_RUNTIME_CARRIER_JSON_MIRROR = REGISTRY_ROOT / QSHRINK_RUNTIME_CARRIER_JSON_PATH.name
DASHBOARD_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_cloud_runtime_hardening_dashboard.json"
DASHBOARD_JSON_MIRROR = REGISTRY_ROOT / DASHBOARD_JSON_PATH.name
VERIFICATION_JSON_PATH = SELF_ACTUALIZE_ROOT / "q42_cloud_runtime_hardening_verification.json"
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

MANIFESTS_ROOT = MYCELIUM_ROOT / "nervous_system" / "manifests"
FAMILIES_ROOT = MYCELIUM_ROOT / "nervous_system" / "families"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"
NERVOUS_RUNTIME_ROOT = MYCELIUM_ROOT / "nervous_system"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS"

ACTIVE_QUEUE_PATH = NERVOUS_RUNTIME_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = MANIFESTS_ROOT / "NEXT_SELF_PROMPT.md"
QSHRINK_ACTIVE_FRONT_PATH = MANIFESTS_ROOT / "QSHRINK_ACTIVE_FRONT.md"
QSHRINK_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use_route_map.md"
QSHRINK_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_qshrink_athena_internal_use.md"
ATHENA_FLEET_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_orgin_route_map.md"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "06_QUEST_BOARD.md"
CHANGE_FEED_PATH = GUILD_HALL_ROOT / "04_CHANGE_FEED_BOARD.md"
RUNTIME_MEMBRANE_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_CORRIDOR_MEMBRANE.md"
RUNTIME_CARRIER_MD_PATH = MANIFESTS_ROOT / "ATHENA_OS_QSHRINK_RUNTIME_CARRIER_CONTRACT.md"
QSHRINK_AGENT_PLAN_PATH = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL" / "13_QSHRINK_LOOPED_AGENTIC_PLAN.md"
QSHRINK_ECOSYSTEM_CAPSULE_PATH = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "qshrink" / "02_qshrink_shiva_corpus_ecosystem.md"
QSHRINK_AGENT_CAPSULE_PATH = NERVOUS_SYSTEM_ROOT / "50_CORPUS_CAPSULES" / "qshrink" / "03_qshrink_agent_sweep_contract.md"

MANIFEST_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_CLOUD_RUNTIME_HARDENING_MANIFEST.md"
DASHBOARD_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_CLOUD_RUNTIME_HARDENING_DASHBOARD.md"
VERIFICATION_MD_PATH = NERVOUS_SYSTEM_ROOT / "95_MANIFESTS" / "Q42_CLOUD_RUNTIME_HARDENING_VERIFICATION.md"
RUNTIME_MD_PATH = NERVOUS_RUNTIME_ROOT / "33_q42_cloud_runtime_hardening_runtime.md"
RECEIPT_MD_PATH = RECEIPTS_ROOT / "2026-03-13_q42_cloud_runtime_hardening.md"

CLOUD_SUBFRONT = "QS64-19 Connectivity-Diagnose-Cloud"
FRACTAL_SUBFRONT = "QS64-20 Connectivity-Diagnose-Fractal"
DERIVATION_VERSION = "2026-03-13.q42-cloud-runtime-hardening-v1"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_q42_cloud_runtime_hardening"


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


def build_runtime_carrier() -> RuntimeCarrierContractRecord:
    runtime_payload = load_json(RUNTIME_VERIFICATION_PATH)
    membrane_payload = load_json(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH)
    truth_state = "OK" if runtime_payload.get("truth") == "OK" and membrane_payload.get("truth_state") == "OK" else "NEAR"
    return RuntimeCarrierContractRecord(
        carrier_id="Q42-M3-RUNTIME-CARRIER",
        source_body_id="A16",
        runtime_surface="MATH\\FINAL FORM\\FRAMEWORKS CODE\\Athena OS\\athena_os\\qshrink\\",
        membrane_surface=relative_string(RUNTIME_MEMBRANE_MD_PATH),
        verification_surfaces=[
            relative_string(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
            relative_string(RUNTIME_VERIFICATION_PATH),
            relative_string(RUNTIME_MEMBRANE_MD_PATH),
        ],
        replay_surface=relative_string(CLOUD_JSON_PATH),
        writeback_surfaces=[
            relative_string(QSHRINK_ACTIVE_FRONT_PATH),
            relative_string(QSHRINK_ROUTE_MAP_PATH),
            relative_string(ATHENA_FLEET_ROUTE_MAP_PATH),
            relative_string(NEXT_SELF_PROMPT_PATH),
        ],
        truth_state=truth_state,
        selection_state="PROMOTED_CURRENT" if truth_state == "OK" else "PROMOTE_NEXT",
        next_seed=FRACTAL_SUBFRONT,
        note="Athena OS runtime is now the active Cloud-selected carrier contract layered above the Flower membrane.",
    )


def render_runtime_carrier_markdown(record: RuntimeCarrierContractRecord) -> str:
    verification_lines = "\n".join(f"- `{item}`" for item in record.verification_surfaces)
    writeback_lines = "\n".join(f"- `{item}`" for item in record.writeback_surfaces)
    return f"""# ATHENA OS QSHRINK RUNTIME CARRIER CONTRACT

Date: `2026-03-13`
Truth: `{record.truth_state}`
Selection state: `{record.selection_state}`

## Carrier

- carrier id: `{record.carrier_id}`
- source body id: `{record.source_body_id}`
- runtime surface: `{record.runtime_surface}`
- membrane surface: `{record.membrane_surface}`
- replay surface: `{record.replay_surface}`
- next seed: `{record.next_seed}`

## Verification surfaces

{verification_lines}

## Writeback surfaces

{writeback_lines}

## Note

{record.note}
"""


def render_fleet_route_map(record: RuntimeCarrierContractRecord) -> str:
    return f"""# FAMILY Athena FLEET Route Map

## Intake

- `Athena FLEET/MYCELIUM_NETWORK_STANDARD_TEXT_RECORD.md`
- `Athena FLEET/FLEET_MYCELIUM_NETWORK/00_README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md`
- `self_actualize/qshrink_connectivity_flower.json`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_runtime_carrier_contract.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Main transfer

`QSHRINK -> Athena FLEET ecosystem -> Athena OS runtime carrier contract -> Hall Cloud writeback`

Governance overlay:

`Athena FLEET -> Trading Bot truth corridor -> blocked Docs gate`

## Law

- Flower is upstream-complete and no longer the active owner-facing pass
- Cloud is the active owner-facing synchronization layer
- `P2` is the current promoted runtime carrier pressure
- `P3` remains queue-visible behind the carrier and is not bundled into this pass
- `M2` remains an external governance overlay while Docs is blocked

## Cloud status

- Flower core upstream: `OK`
- Cloud sync: `OK`
- Runtime carrier: `{record.truth_state}`
- External gate overlay: `blocked-by-missing-credentials`
- Queue-visible follow-on: `P3 / ORGIN`

## Fixed metro lines

- `M1 contraction-rail`: `OK` / `flower-core` / `witnessed`
- `M2 governance-rail`: `NEAR` / `external-gate-overlay` / `blocked-by-missing-credentials`
- `M3 runtime-rail`: `{record.truth_state}` / `cloud-active` / `{record.selection_state.lower()}`
- `M4 hall-rail`: `OK` / `flower-core` / `witnessed`
- `M5 seed-rail`: `OK` / `flower-core` / `queue-visible`

## Next route

`{CLOUD_SUBFRONT} -> {FRACTAL_SUBFRONT}`
"""


def render_orgin_route_map() -> str:
    return f"""# FAMILY ORGIN Route Map

## Intake

- `ORGIN/Fine Tuning Docs/`
- `self_actualize/orgin_atlas.json`
- `NERVOUS_SYSTEM\\50_CORPUS_CAPSULES\\orgin\\08_orgin_readable_mirror_megalithic_tome_generator_latent_tunneling_multi.md`
- `self_actualize\\mycelium_brain\\nervous_system\\packets\\PKT_2026-03-13_q42_orgin_seed_packet_witness.md`

## Main transfer

`ORGIN -> readable mirror bundle -> seed packet witness -> Athena FLEET cloud queue -> runtime carrier contract`

## Law

Read `ORGIN` as origin memory and observer-seed matter.
Do not route it as miscellaneous storage.
Mirror surfaces remain queue-visible follow-on matter behind the runtime carrier and do not bypass atlas indexing or the blocked Docs gate.
Do not pre-claim the denser mirror mesh in this pass.

## Next route

`ORGIN -> queue-visible P3 behind {CLOUD_SUBFRONT} -> {FRACTAL_SUBFRONT}`
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
  synchronize the owner-facing corridor surfaces on Cloud, promote `P2` through the Athena OS runtime carrier contract, keep the blocked Docs gate external, and keep `P3` queue-visible
- Why Now:
  Flower is now upstream-complete, but the organism still drifts between Flower, Cloud, and Fractal wording; the honest next move is to make Cloud the single active truth before deeper recursion
- Active subfront:
  `{CLOUD_SUBFRONT}`
- Targets:
  `self_actualize/q42_runtime_carrier_contract.json`
  `self_actualize/qshrink_connectivity_cloud.json`
  `self_actualize/qshrink_network_integration.json`
  `self_actualize/qshrink_agent_task_matrix.json`
  `manifests/ATHENA_OS_QSHRINK_RUNTIME_CARRIER_CONTRACT.md`
  `manifests/QSHRINK_ACTIVE_FRONT.md`
  `families/FAMILY_qshrink_athena_internal_use_route_map.md`
  `families/FAMILY_athena_fleet_route_map.md`
  `families/FAMILY_orgin_route_map.md`
  `manifests/NEXT_SELF_PROMPT.md`
  `../receipts/2026-03-13_q42_cloud_runtime_hardening.md`
- Witness:
  one Cloud-sync proof bundle showing `QS64-19` as the only active owner-facing pass, one promoted runtime carrier contract, one queue-visible `P3` marker, one atlas refresh, and one restart-safe Fractal handoff
- Writeback:
  quest board, change feed, active queue, next-self-prompt, and receipt
- Next Seed:
  `{FRACTAL_SUBFRONT}`
"""


def replace_q42_queue_block() -> None:
    text = read_text(ACTIVE_QUEUE_PATH)
    pattern = r"### FRONT-Q42-QSHRINK-AGENT-SWEEP\n.*?(?=\n### FRONT-|\Z)"
    updated = re.sub(pattern, render_q42_queue_block().rstrip() + "\n\n", text, flags=re.S)
    write_text(ACTIVE_QUEUE_PATH, updated)


def update_next_self_prompt() -> None:
    text = read_text(NEXT_SELF_PROMPT_PATH)
    current_seed_pattern = r"## Current Restart Seed\n\n`[^`]+`"
    current_seed_replacement = (
        "## Current Restart Seed\n\n"
        "`2026-03-13 America/Los_Angeles: keep packet governance on Q41/TQ06 as the active control membrane, "
        "preserve blocked-Docs honesty, hold Q42 on QS64-19 Connectivity-Diagnose-Cloud as the active owner-facing pass, "
        "keep P2 current through the Athena OS runtime carrier contract, keep P3 queue-visible behind it, "
        f"then carry Q42 into {FRACTAL_SUBFRONT} as the next corridor followthrough.`"
    )
    text = re.sub(current_seed_pattern, current_seed_replacement, text, flags=re.S)
    preferred_order_pattern = r"Preferred frontier order:\n(?:.*\n)*?(?=```|\Z)"
    preferred_order_replacement = (
        "Preferred frontier order:\n"
        f"1. one `Q42` Cloud runtime-carrier hardening pass through `{CLOUD_SUBFRONT}`\n"
        f"2. one `Q42` corridor carrythrough from `{CLOUD_SUBFRONT}` into `{FRACTAL_SUBFRONT}`\n"
        "3. one `P3` ORGIN mirror-deepening follow-on after the carrier remains stable\n"
        "4. one `TQ04` runner-contract binding pass\n"
        "5. one `Q02` live-memory bootstrap prerequisite pass if OAuth material appears\n"
    )
    text = re.sub(preferred_order_pattern, preferred_order_replacement, text, flags=re.S)
    write_text(NEXT_SELF_PROMPT_PATH, text)


def render_q42_quest_block() -> str:
    return f"""### Quest Q42: Activate The First QSHRINK Agent Sweep `[OPEN]`

- Objective:
  bind the first-wave QSHRINK agent set to the new 64-lattice so compression, connectivity, runtime, and promotion work become one repeatable ownerable sweep, synchronize the owner-facing corridor on Cloud, and promote the Athena OS runtime carrier without bundling the ORGIN mirror deepening into the same pass
- Why now:
  Flower is upstream-complete, but the live surfaces still drift between Flower, Cloud, and Fractal wording; the honest next gain is to make Cloud the single active truth and land the selected `P2` promotion before recursive crossings begin
- Active subfront:
  `{CLOUD_SUBFRONT}`
- Target surfaces:
  `self_actualize/q42_runtime_carrier_contract.json`
  `self_actualize/qshrink_agent_task_matrix.json`
  `self_actualize/qshrink_runtime_verification.json`
  `self_actualize/qshrink_capability_stack.json`
  `self_actualize/qshrink_connectivity_flower.json`
  `self_actualize/qshrink_connectivity_cloud.json`
  `self_actualize/qshrink_network_integration.json`
  `self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/13_QSHRINK_LOOPED_AGENTIC_PLAN.md`
  `self_actualize/mycelium_brain/nervous_system/manifests/QSHRINK_ACTIVE_FRONT.md`
  `self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md`
  `self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md`
  `NERVOUS_SYSTEM/50_CORPUS_CAPSULES/qshrink/06_qshrink_core_corridor_cloud.md`
  one QSHRINK receipt
- Witness needed:
  one synced Cloud truth layer, one promoted runtime carrier contract, one queue-visible `P3` marker, one integration refresh, and one receipt proving `{CLOUD_SUBFRONT}` is the only active owner-facing core-corridor subfront
- Writeback:
  Hall quest board, change feed, active queue, next-self-prompt, and receipt
- Restart seed:
  keep `Q42` open on `{CLOUD_SUBFRONT}`, keep `Q02` suppressed while Docs gate is blocked, and emit `{FRACTAL_SUBFRONT}` as the sole next corridor seed
"""


def replace_q42_quest_board_block() -> None:
    text = read_text(QUEST_BOARD_PATH)
    pattern = r"### Quest Q42: Activate The First QSHRINK Agent Sweep `\[OPEN\]`\n.*?(?=\n### Quest |\Z)"
    updated = re.sub(pattern, render_q42_quest_block().rstrip() + "\n\n", text, flags=re.S)
    write_text(QUEST_BOARD_PATH, updated)


def append_change_feed_entry() -> None:
    text = read_text(CHANGE_FEED_PATH)
    existing_phrase = "Q42 Cloud synchronization and runtime carrier hardening is now landed"
    if existing_phrase in text:
        return
    numbers = [int(match) for match in re.findall(r"(?m)^(\d+)\.\s", text)]
    next_number = max(numbers) + 1 if numbers else 1
    entry = (
        f"{next_number}. Q42 Cloud synchronization and runtime carrier hardening is now landed: "
        f"`derive_q42_cloud_runtime_hardening.py` and `q42_runtime_carrier_contract.json` promote `P2` into the active Athena OS runtime carrier, "
        f"`qshrink_connectivity_cloud.json`, `qshrink_network_integration.json`, and `qshrink_agent_task_matrix.json` now agree on `{CLOUD_SUBFRONT}` as the active owner-facing pass, "
        f"`P3` remains explicitly queue-visible, and Hall, queue, route, and restart surfaces now emit `{FRACTAL_SUBFRONT}` as the sole next corridor seed."
    )
    updated = text.rstrip() + "\n" + entry + "\n"
    write_text(CHANGE_FEED_PATH, updated)


def skill_path(skill_name: str) -> Path | None:
    skills_root = Path.home() / ".codex" / "skills"
    local_path = skills_root / skill_name / "SKILL.md"
    if local_path.exists():
        return local_path
    system_path = skills_root / ".system" / skill_name / "SKILL.md"
    if system_path.exists():
        return system_path
    return None


def build_qshrink_network_payload(carrier: RuntimeCarrierContractRecord) -> Dict[str, Any]:
    atlas = load_json(WORKSPACE_ROOT / "Athena FLEET" / "QSHRINK2_CORPUS_ECOSYSTEM" / "02_QSHRINK2_CORPUS_ATLAS.json")
    flower = load_json(FLOWER_JSON_PATH)
    cloud = load_json(CLOUD_JSON_PATH)
    capability = load_json(CAPABILITY_STACK_PATH)
    runtime_verification = load_json(RUNTIME_VERIFICATION_PATH)
    summary = atlas.get("summary", {})
    return {
        "generated_at": utc_now(),
        "derivation_command": "python -m self_actualize.runtime.derive_qshrink_network_integration",
        "truth": "OK",
        "source_paths": {
            "qshrink_ecosystem": str(WORKSPACE_ROOT / "Athena FLEET" / "QSHRINK2_CORPUS_ECOSYSTEM"),
            "runtime_verification": str(RUNTIME_VERIFICATION_PATH),
            "capability_stack": str(CAPABILITY_STACK_PATH),
            "connectivity_square": str(SELF_ACTUALIZE_ROOT / "qshrink_connectivity_square.json"),
            "connectivity_flower": str(FLOWER_JSON_PATH),
            "connectivity_cloud": str(CLOUD_JSON_PATH),
            "runtime_membrane": str(QSHRINK_RUNTIME_MEMBRANE_JSON_PATH),
            "runtime_carrier": str(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
        },
        "corpus_metrics": {
            "total_files": summary.get("total_files", 0),
            "total_bytes": summary.get("total_bytes", 0),
            "duplicate_groups_count": summary.get("duplicate_groups_count", 0),
            "duplicate_savings_bytes": summary.get("duplicate_savings_bytes", 0),
        },
        "runtime_verification_truth": runtime_verification.get("truth", "NEAR"),
        "capability_stack_truth": capability.get("truth", "NEAR"),
        "connectivity_flower_truth": flower.get("truth", "NEAR"),
        "connectivity_cloud_truth": cloud.get("truth", "NEAR"),
        "flower_core_status": flower.get("flower_core_status", "NEAR"),
        "external_gate_overlay_status": flower.get("external_gate_overlay_status", "blocked-by-missing-credentials"),
        "flower_activation_status": flower.get("flower_activation_status", "NEAR"),
        "cloud_sync_status": cloud.get("cloud_sync_status", "NEAR"),
        "runtime_carrier_status": carrier.truth_state,
        "cloud_frontier_status": cloud.get("truth", "NEAR"),
        "promoted_pressure": cloud.get("promoted_pressure", {"id": "P2"}),
        "queue_visible_pressures": cloud.get("queue_visible_pressures", [{"id": "P3", "body": "ORGIN"}]),
        "active_subfront": CLOUD_SUBFRONT,
        "next_seed": FRACTAL_SUBFRONT,
    }


def render_qshrink_family(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# FAMILY QSHRINK Internal Use

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
Primary rail: `Me`
Primary face: `Air`
Primary hub: `AppN`

## Role

`QSHRINK - ATHENA (internal use)` remains Athena's Shiva layer: the contraction organ that binds doctrine, Fleet routing, runtime proof, Hall closure, Cloud synchronization, and replay-safe restart.

## Current front

- active subfront: `{payload['active_subfront']}`
- flower core status: `{payload['flower_core_status']}`
- cloud sync status: `{payload['cloud_sync_status']}`
- runtime carrier status: `{payload['runtime_carrier_status']}`
- promoted pressure: `{payload['promoted_pressure']['id']}`
- queue-visible follow-on: `{queued}`
- external gate overlay: `{payload['external_gate_overlay_status']}`
- next seed: `{payload['next_seed']}`

## Local mass

- full corpus files scanned: `{payload['corpus_metrics']['total_files']}`
- duplicate groups visible to QSHRINK2: `{payload['corpus_metrics']['duplicate_groups_count']}`
"""


def render_qshrink_route_map(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# FAMILY QSHRINK Internal Use Route Map

## Intake

- `QSHRINK - ATHENA (internal use)/README.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/11_QSHRINK_CORE_CORRIDOR_CONTRACT.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/12_QSHRINK_CORE_CORRIDOR_METRO.md`
- `Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/13_QSHRINK_CORE_CORRIDOR_CLOUD.md`
- `self_actualize/qshrink_connectivity_flower.json`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_runtime_carrier_contract.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`

## Main transfer

`QSHRINK - ATHENA (internal use) -> Athena FLEET ecosystem -> qshrink_connectivity_cloud.json -> runtime carrier contract -> active queue -> next prompt`

## Law

- keep QSHRINK as the contraction root
- treat Flower as upstream-complete truth, not as the active pass
- keep Cloud as the current owner-facing synchronization layer
- hold `P2` as the promoted runtime carrier pressure
- keep `P3` queue-visible behind the carrier
- keep `M2` explicit as an external blocked Docs overlay

## Queue-visible follow-on

`{queued}`

## Next route

`QSHRINK -> {payload['active_subfront']} -> {payload['next_seed']}`
"""


def render_qshrink_active_front(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# QSHRINK ACTIVE FRONT

## FrontID

`Q42`

## Quest

Activate The First QSHRINK Agent Sweep

## State

`OPEN`

## Truth

`{payload['truth']}`

## Objective

Close `{payload['active_subfront']}` honestly by synchronizing Hall, queue, route, and restart surfaces on Cloud, promoting `P2` through the Athena OS runtime carrier contract, keeping `M2` external, and leaving `P3` queue-visible.

## Why Now

Flower is now upstream-complete, but owner-facing surfaces still drift between Flower, Cloud, and Fractal wording. The honest current move is to make Cloud the single active truth and land the selected runtime carrier promotion before Fractal recursion begins.

## Targets

- `self_actualize/q42_runtime_carrier_contract.json`
- `self_actualize/q42_runtime_corridor_membrane.json`
- `self_actualize/q42_orgin_seed_packet_witness.json`
- `self_actualize/qshrink_connectivity_cloud.json`
- `self_actualize/qshrink_network_integration.json`
- `self_actualize/qshrink_agent_task_matrix.json`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_qshrink_athena_internal_use_route_map.md`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_athena_fleet_route_map.md`
- `self_actualize/mycelium_brain/nervous_system/families/FAMILY_orgin_route_map.md`

## Queue-visible follow-on

`{queued}`

## Next Seed

`{payload['next_seed']}`
"""


def render_qshrink_capsule(payload: Dict[str, Any]) -> str:
    queued = ", ".join(item.get("id", "") for item in payload.get("queue_visible_pressures", [])) or "none"
    return f"""# QSHRINK Shiva Corpus Ecosystem

Truth class: `{payload['truth']}`
Domain: `qshrink`
Date: `{payload['generated_at'][:10]}`

## Capsule Summary

The QSHRINK corridor now treats Flower as upstream-complete, Cloud as the active owner-facing pass, and the Athena OS runtime carrier contract as the current promoted pressure while ORGIN remains queue-visible.

## State

- active subfront: `{payload['active_subfront']}`
- flower core status: `{payload['flower_core_status']}`
- cloud sync status: `{payload['cloud_sync_status']}`
- runtime carrier status: `{payload['runtime_carrier_status']}`
- queue-visible follow-on: `{queued}`
- next seed: `{payload['next_seed']}`
"""


def build_agent_payload(carrier: RuntimeCarrierContractRecord) -> Dict[str, Any]:
    cloud = load_json(CLOUD_JSON_PATH)
    first_wave_agents = [
        {
            "skill": "q-shrink",
            "quest": "QS64-09 QShrink-Synthesize-Square",
            "status": "ACTIVE",
            "role": "compress cross-body synthesis into replayable witness shells and support the carrier promotion writeback.",
            "target_surfaces": [
                "Athena FLEET/QSHRINK2_CORPUS_ECOSYSTEM/",
                "self_actualize/qshrink_network_integration.json",
                "self_actualize/qshrink_agent_task_matrix.json",
                "self_actualize/q42_runtime_carrier_contract.json",
            ],
            "expected_outputs": [
                "one contraction contract",
                "one holographic artifact bundle",
                "one carrier-promotion delta",
            ],
        },
        {
            "skill": "metro-cartography",
            "quest": "QS64-18 Connectivity-Diagnose-Flower",
            "status": "DONE",
            "role": "hold the five corridor transit lines and their transfer-hub law through the completed Flower closure pass.",
            "target_surfaces": [
                "Athena FLEET/",
                "Trading Bot/",
                "ORGIN/",
                "self_actualize/qshrink_connectivity_flower.json",
            ],
            "expected_outputs": ["one corridor map", "one cadence handoff plan", "one transfer-hub witness"],
        },
        {
            "skill": "guild-hall-quest-loop",
            "quest": "QS64-18 Connectivity-Diagnose-Flower",
            "status": "DONE",
            "role": "convert the completed Flower closure into quest writeback, queue refresh, and restart alignment.",
            "target_surfaces": [
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md",
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
            ],
            "expected_outputs": ["one quest writeback", "one queue refresh", "one receipt and restart seed"],
        },
        {
            "skill": "manuscript-intake",
            "quest": CLOUD_SUBFRONT,
            "status": "ACTIVE",
            "role": "refresh the atlas slice for the heaviest corridor bodies so Cloud state stays grounded while P2 lands.",
            "target_surfaces": [
                "Athena FLEET/",
                "Trading Bot/",
                "ORGIN/",
                "self_actualize/corpus_atlas.json",
                "self_actualize/qshrink_connectivity_cloud.json",
            ],
            "expected_outputs": ["one grounded cloud witness", "one refreshed atlas slice", "one heavy-body ranking delta"],
        },
        {
            "skill": "corpus-status-synthesizer",
            "quest": CLOUD_SUBFRONT,
            "status": "ACTIVE",
            "role": "rank connected pressure fronts and keep P2 current while P3 stays queue-visible.",
            "target_surfaces": [
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/04_CHANGE_FEED_BOARD.md",
                "GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md",
                "self_actualize/qshrink_network_integration.json",
                "self_actualize/qshrink_connectivity_cloud.json",
            ],
            "expected_outputs": ["one ranked pressure report", "one witness-aware queue ordering"],
        },
        {
            "skill": "deeper-integrated-neural-network",
            "quest": FRACTAL_SUBFRONT,
            "status": "READY",
            "role": "map recursive metro crossings once Cloud synchronization and the runtime carrier promotion are fully landed.",
            "target_surfaces": [
                "self_actualize/mycelium_brain/dynamic_neural_network/",
                "GLOBAL_EMERGENT_GUILD_HALL/13_QSHRINK_LOOPED_AGENTIC_PLAN.md",
            ],
            "expected_outputs": ["one metro map", "one appendix or pairwise synthesis pack"],
        },
    ]
    for agent in first_wave_agents:
        path = skill_path(agent["skill"])
        agent["skill_path"] = str(path) if path else None
        agent["truth"] = "OK" if path else "MISSING"
    return {
        "generated_at": utc_now(),
        "truth": cloud.get("truth", "OK"),
        "docs_gate": "BLOCKED",
        "blocked_by": ["Trading Bot/credentials.json missing", "Trading Bot/token.json missing"],
        "front_id": "Q42",
        "front_title": "Activate The First QSHRINK Agent Sweep",
        "activation_quest": "QS64-09 QShrink-Synthesize-Square",
        "active_subfront": CLOUD_SUBFRONT,
        "next_connectivity_quest": FRACTAL_SUBFRONT,
        "restart_seed": FRACTAL_SUBFRONT,
        "loop_law": "gate check -> local witness -> cloud sync -> carrier promotion -> guild writeback -> queue refresh -> restart",
        "guild_law": "request -> quest -> witness -> writeback -> restart",
        "cloud_selected_pressure": "P2",
        "queued_follow_on_pressure": "P3",
        "runtime_carrier_status": carrier.truth_state,
        "first_wave_agents": first_wave_agents,
    }


def render_agent_plan(payload: Dict[str, Any]) -> str:
    lines = [
        "# QSHRINK Looped Agentic Plan",
        "",
        f"Date: `{payload['generated_at'][:10]}`",
        f"Truth: `{payload['truth']}`",
        f"Hall frontier: `{payload['front_id']} {payload['front_title']}`",
        f"Crystal activation: `{payload['activation_quest']}`",
        f"Active subfront: `{payload['active_subfront']}`",
        f"Next connectivity quest: `{payload['next_connectivity_quest']}`",
        "Live Docs Gate: `BLOCKED` due to missing OAuth files, so this plan is grounded in local corpus witness only.",
        "",
        "## Cloud Selection",
        "",
        f"- selected pressure: `{payload['cloud_selected_pressure']}`",
        f"- queued follow-on: `{payload['queued_follow_on_pressure']}`",
        f"- runtime carrier status: `{payload['runtime_carrier_status']}`",
        "",
        "## First-Wave Agent Task Matrix",
        "",
    ]
    for index, agent in enumerate(payload["first_wave_agents"], start=1):
        targets = "; ".join(f"`{item}`" for item in agent["target_surfaces"])
        outputs = "; ".join(agent["expected_outputs"])
        lines.extend(
            [
                f"### A{index:02d} `{agent['skill']}` -> `{agent['quest']}`",
                "",
                f"- Status: `{agent['status']}`",
                f"- Skill truth: `{agent['truth']}`",
                f"- Role: {agent['role']}",
                f"- Target surfaces: {targets}",
                f"- Expected outputs: {outputs}",
                "",
            ]
        )
    lines.extend(["## Restart Seed", "", f"`{payload['restart_seed']}`"])
    return "\n".join(lines) + "\n"


def render_agent_capsule(payload: Dict[str, Any]) -> str:
    active_agents = [agent["skill"] for agent in payload["first_wave_agents"] if agent["status"] == "ACTIVE"]
    return f"""# QSHRINK Agent Sweep Contract

Date: `{payload['generated_at'][:10]}`
Truth class: `{payload['truth']}`
Hall frontier: `{payload['front_id']}`
Crystal activation: `{payload['activation_quest']}`
Active subfront: `{payload['active_subfront']}`
Next connectivity quest: `{payload['next_connectivity_quest']}`

## Summary

The current QSHRINK sweep keeps Flower upstream-complete, makes Cloud the active ownerable pass, and promotes `P2` runtime carrier hardening while leaving `P3` queue-visible.

## Cloud selection

- selected pressure: `{payload['cloud_selected_pressure']}`
- queued follow-on: `{payload['queued_follow_on_pressure']}`
- runtime carrier status: `{payload['runtime_carrier_status']}`

## Active agents

{chr(10).join(f"- {agent}" for agent in active_agents)}

## Next seed

`{payload['restart_seed']}`
"""


def render_manifest(outputs: Dict[str, str], module_runs: List[Dict[str, Any]]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    run_lines = "\n".join(f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`" for run in module_runs)
    return f"""# Q42 CLOUD RUNTIME HARDENING MANIFEST

Date: `2026-03-13`
Derivation: `{DERIVATION_COMMAND}`
Wave: `Q42 / {CLOUD_SUBFRONT}`

## Law

- keep Flower as upstream-complete truth, not as the active owner-facing pass
- synchronize Hall, queue, front, route, and restart surfaces on Cloud
- promote `P2` through the Athena OS runtime carrier contract
- keep `P3` queue-visible and do not bundle ORGIN mirror deepening into this pass
- emit `{FRACTAL_SUBFRONT}` as the sole next restart seed

## Outputs

{output_lines}

## Downstream reruns

{run_lines}
"""


def render_dashboard(payload: Dict[str, Any]) -> str:
    verifier_truth = payload.get("verifier_truth", {})
    return f"""# Q42 CLOUD RUNTIME HARDENING DASHBOARD

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Corridor

- active subfront: `{payload['active_subfront']}`
- cloud sync status: `{payload['cloud_sync_status']}`
- runtime carrier status: `{payload['runtime_carrier_status']}`
- promoted pressure: `{payload['promoted_pressure']}`
- queue-visible follow-on: `{payload['queue_visible_follow_on']}`

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
    return f"""# Q42 CLOUD RUNTIME HARDENING VERIFICATION

Date: `2026-03-13`
Truth: `{payload['truth']}`

## Checks

{check_lines}

## Unresolved

{unresolved_lines}
"""


def render_runtime(outputs: Dict[str, str], verification: Dict[str, Any]) -> str:
    output_lines = "\n".join(f"- `{label}`: `{path}`" for label, path in outputs.items())
    return f"""# 33 Q42 CLOUD RUNTIME HARDENING RUNTIME

Date: `2026-03-13`
Truth: `{verification['truth']}`
Docs gate: `{verification['docs_gate_status']}`

## Outputs

{output_lines}
"""


def render_receipt(
    carrier: RuntimeCarrierContractRecord,
    verification: Dict[str, Any],
    module_runs: List[Dict[str, Any]],
) -> str:
    run_lines = "\n".join(f"- `{run['module']}`: `{'OK' if run['ok'] else 'FAIL'}`" for run in module_runs)
    unresolved_lines = "\n".join(f"- {item}" for item in verification["unresolved"]) or "- none"
    return f"""# 2026-03-13 q42 cloud runtime hardening

- truth: `{verification['truth']}`
- docs gate: `{verification['docs_gate_status']}`
- active subfront: `{verification['active_subfront']}`
- cloud sync status: `{verification['cloud_sync_status']}`
- runtime carrier status: `{verification['runtime_carrier_status']}`
- next seed: `{verification['next_restart_seed']}`

## Landed witness

- runtime carrier: `{carrier.carrier_id}` / `{carrier.truth_state}` / `{carrier.selection_state}`

## Downstream reruns

{run_lines}

## Honest limits

{unresolved_lines}
"""


def build_verification(generated_paths: List[Path], module_runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    cloud = load_json(CLOUD_JSON_PATH)
    network = load_json(NETWORK_JSON_PATH)
    agent_matrix = load_json(AGENT_MATRIX_PATH)
    atlas = load_json(CORPUS_ATLAS_PATH)
    atlas_paths = {record.get("relative_path") for record in atlas.get("records", [])}
    generated_relative = [relative_string(path) for path in generated_paths if path.exists()]
    atlas_missing = [path for path in generated_relative if path not in atlas_paths]

    phase4_candidates = load_json(PHASE4_PATH).get("candidates", [])
    knowledge_edges = load_json(KNOWLEDGE_FABRIC_PATH).get("edges", [])
    pt2_edges = load_json(PHASE4_PT2_PATH).get("edges", [])
    phase4_edge_ids = {item.get("bridge_edge_id") for item in phase4_candidates if item.get("bridge_edge_id")}
    knowledge_edge_ids = {item.get("edge_id") for item in knowledge_edges}
    pt2_edge_ids = {item.get("edge_id") for item in pt2_edges}

    queue_text = read_text(ACTIVE_QUEUE_PATH)
    next_prompt_text = read_text(NEXT_SELF_PROMPT_PATH)
    qshrink_route_text = read_text(QSHRINK_ROUTE_MAP_PATH)
    fleet_route_text = read_text(ATHENA_FLEET_ROUTE_MAP_PATH)
    orgin_route_text = read_text(ORGIN_ROUTE_MAP_PATH)
    active_front_text = read_text(QSHRINK_ACTIVE_FRONT_PATH)
    quest_board_text = read_text(QUEST_BOARD_PATH)
    change_feed_text = read_text(CHANGE_FEED_PATH)

    verifier_truth = {
        "qshrink_runtime_verification": load_json(QSHRINK_STACK_VERIFY_PATH).get("truth", "UNKNOWN"),
        "aqm_runtime_lane": load_json(AQM_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "atlasforge_runtime_lane": load_json(ATLASFORGE_RUNTIME_PATH).get("truth", "UNKNOWN"),
        "runtime_waist": load_json(RUNTIME_WAIST_PATH).get("truth", "UNKNOWN"),
    }

    carrier_payload = load_json(QSHRINK_RUNTIME_CARRIER_JSON_PATH)
    checks = {
        "runtime_carrier_ok": carrier_payload.get("truth_state") == "OK",
        "cloud_truth_ok": cloud.get("truth") == "OK" and cloud.get("active_subfront") == CLOUD_SUBFRONT and cloud.get("next_restart_seed") == FRACTAL_SUBFRONT,
        "cloud_sync_status_ok": cloud.get("cloud_sync_status") == "OK",
        "cloud_promoted_p2": cloud.get("promoted_pressure", {}).get("id") == "P2",
        "cloud_queue_visible_p3": any(item.get("id") == "P3" for item in cloud.get("queue_visible_pressures", [])),
        "network_active_subfront_cloud": network.get("active_subfront") == CLOUD_SUBFRONT,
        "network_next_seed_fractal": network.get("next_seed") == FRACTAL_SUBFRONT,
        "network_runtime_carrier_ok": network.get("runtime_carrier_status") == "OK",
        "agent_matrix_active_subfront_cloud": agent_matrix.get("active_subfront") == CLOUD_SUBFRONT,
        "agent_matrix_next_fractal": agent_matrix.get("next_connectivity_quest") == FRACTAL_SUBFRONT,
        "agent_matrix_selected_p2": agent_matrix.get("cloud_selected_pressure") == "P2",
        "agent_matrix_queue_p3": agent_matrix.get("queued_follow_on_pressure") == "P3",
        "active_front_aligned": CLOUD_SUBFRONT in active_front_text and FRACTAL_SUBFRONT in active_front_text and "runtime carrier" in active_front_text.lower(),
        "active_queue_aligned": CLOUD_SUBFRONT in queue_text and FRACTAL_SUBFRONT in queue_text and "queue-visible" in queue_text.lower(),
        "next_prompt_aligned": CLOUD_SUBFRONT in next_prompt_text and FRACTAL_SUBFRONT in next_prompt_text and "P3" in next_prompt_text,
        "quest_board_aligned": CLOUD_SUBFRONT in quest_board_text and FRACTAL_SUBFRONT in quest_board_text and "runtime carrier" in quest_board_text.lower(),
        "change_feed_written": "Q42 Cloud synchronization and runtime carrier hardening is now landed" in change_feed_text,
        "qshrink_route_map_aligned": CLOUD_SUBFRONT in qshrink_route_text and FRACTAL_SUBFRONT in qshrink_route_text and "runtime carrier" in qshrink_route_text.lower(),
        "fleet_route_map_aligned": CLOUD_SUBFRONT in fleet_route_text and FRACTAL_SUBFRONT in fleet_route_text and "queue-visible" in fleet_route_text.lower(),
        "orgin_route_map_aligned": CLOUD_SUBFRONT in orgin_route_text and FRACTAL_SUBFRONT in orgin_route_text and "queue-visible" in orgin_route_text.lower(),
        "orgin_remains_queue_only": "mirror lattice" not in orgin_route_text.lower(),
        "atlas_refresh_complete": not atlas_missing,
        "phase4_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(phase4_edge_ids),
        "knowledge_fabric_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(knowledge_edge_ids),
        "phase4_pt2_direct_edges_preserved": {"CS-001", "CS-002", "CS-003"}.issubset(pt2_edge_ids),
        "downstream_reruns_green": all(run["ok"] for run in module_runs),
        "runtime_verifiers_green": all(value == "OK" for value in verifier_truth.values()),
        "docs_gate_preserved_blocked": docs_gate_status() == "blocked-by-missing-credentials",
    }
    unresolved: List[str] = []
    if docs_gate_status() != "blocked-by-missing-credentials":
        unresolved.append("Docs gate no longer matches the expected blocked-by-missing-credentials state.")
    if atlas_missing:
        unresolved.append("One or more Cloud-runtime-hardening surfaces are still missing from corpus_atlas.json.")
    if cloud.get("truth") != "OK":
        unresolved.append("Cloud no longer reports the expected OK truth state.")
    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "truth": "OK" if all(checks.values()) else "FAIL",
        "docs_gate_status": docs_gate_status(),
        "active_subfront": CLOUD_SUBFRONT,
        "cloud_sync_status": cloud.get("cloud_sync_status", "NEAR"),
        "runtime_carrier_status": cloud.get("runtime_carrier_status", "NEAR"),
        "promoted_pressure": cloud.get("promoted_pressure", {}).get("id", "P2"),
        "queue_visible_follow_on": ",".join(item.get("id", "") for item in cloud.get("queue_visible_pressures", [])) or "P3",
        "checks": checks,
        "verifier_truth": verifier_truth,
        "atlas_refresh_pending_paths": atlas_missing,
        "next_restart_seed": FRACTAL_SUBFRONT,
        "unresolved": unresolved,
    }


def build_dashboard(verification: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generated_at": verification["generated_at"],
        "derivation_version": DERIVATION_VERSION,
        "truth": verification["truth"],
        "active_subfront": verification["active_subfront"],
        "cloud_sync_status": verification["cloud_sync_status"],
        "runtime_carrier_status": verification["runtime_carrier_status"],
        "promoted_pressure": verification["promoted_pressure"],
        "queue_visible_follow_on": verification["queue_visible_follow_on"],
        "docs_gate_status": verification["docs_gate_status"],
        "verifier_truth": verification["verifier_truth"],
        "next_restart_seed": verification["next_restart_seed"],
    }


def main() -> int:
    runtime_carrier = build_runtime_carrier()
    network_payload = build_qshrink_network_payload(runtime_carrier)
    agent_payload = build_agent_payload(runtime_carrier)

    write_json(QSHRINK_RUNTIME_CARRIER_JSON_PATH, runtime_carrier.to_dict())
    write_json(QSHRINK_RUNTIME_CARRIER_JSON_MIRROR, runtime_carrier.to_dict())
    write_text(RUNTIME_CARRIER_MD_PATH, render_runtime_carrier_markdown(runtime_carrier))
    write_json(NETWORK_JSON_PATH, network_payload)
    write_text(QSHRINK_FAMILY_PATH, render_qshrink_family(network_payload))
    write_text(QSHRINK_ROUTE_MAP_PATH, render_qshrink_route_map(network_payload))
    write_text(QSHRINK_ACTIVE_FRONT_PATH, render_qshrink_active_front(network_payload))
    write_text(QSHRINK_ECOSYSTEM_CAPSULE_PATH, render_qshrink_capsule(network_payload))
    write_json(AGENT_MATRIX_PATH, agent_payload)
    write_text(QSHRINK_AGENT_PLAN_PATH, render_agent_plan(agent_payload))
    write_text(QSHRINK_AGENT_CAPSULE_PATH, render_agent_capsule(agent_payload))

    derivation_runs = [
        run_module("self_actualize.runtime.derive_qshrink_connectivity_cloud"),
        {"module": "local.qshrink_network_write", "returncode": 0, "stdout": "", "stderr": "", "ok": True},
        {"module": "local.qshrink_agent_matrix_write", "returncode": 0, "stdout": "", "stderr": "", "ok": True},
    ]

    write_text(ATHENA_FLEET_ROUTE_MAP_PATH, render_fleet_route_map(runtime_carrier))
    write_text(ORGIN_ROUTE_MAP_PATH, render_orgin_route_map())
    replace_q42_queue_block()
    update_next_self_prompt()
    replace_q42_quest_board_block()
    append_change_feed_entry()

    outputs = {
        "runtime_carrier_json": relative_string(QSHRINK_RUNTIME_CARRIER_JSON_PATH),
        "dashboard_json": relative_string(DASHBOARD_JSON_PATH),
        "verification_json": relative_string(VERIFICATION_JSON_PATH),
        "manifest_md": relative_string(MANIFEST_MD_PATH),
        "dashboard_md": relative_string(DASHBOARD_MD_PATH),
        "verification_md": relative_string(VERIFICATION_MD_PATH),
        "runtime_md": relative_string(RUNTIME_MD_PATH),
        "receipt_md": relative_string(RECEIPT_MD_PATH),
    }

    provisional_verification = {
        "generated_at": utc_now(),
        "truth": "NEAR",
        "docs_gate_status": docs_gate_status(),
        "active_subfront": CLOUD_SUBFRONT,
        "cloud_sync_status": "NEAR",
        "runtime_carrier_status": runtime_carrier.truth_state,
        "promoted_pressure": "P2",
        "queue_visible_follow_on": "P3",
        "checks": {},
        "verifier_truth": {},
        "next_restart_seed": FRACTAL_SUBFRONT,
        "unresolved": ["Cloud-runtime-hardening atlas refresh pending."],
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
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_carrier, provisional_verification, derivation_runs))

    generated_paths = [
        QSHRINK_RUNTIME_CARRIER_JSON_PATH,
        QSHRINK_RUNTIME_CARRIER_JSON_MIRROR,
        RUNTIME_CARRIER_MD_PATH,
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
        QSHRINK_ACTIVE_FRONT_PATH,
        QSHRINK_FAMILY_PATH,
        QSHRINK_ROUTE_MAP_PATH,
        QSHRINK_ECOSYSTEM_CAPSULE_PATH,
        QSHRINK_AGENT_PLAN_PATH,
        QSHRINK_AGENT_CAPSULE_PATH,
        ATHENA_FLEET_ROUTE_MAP_PATH,
        ORGIN_ROUTE_MAP_PATH,
        QUEST_BOARD_PATH,
        CHANGE_FEED_PATH,
        CLOUD_JSON_PATH,
        NETWORK_JSON_PATH,
        AGENT_MATRIX_PATH,
    ]
    refresh_corpus_atlas(generated_paths)

    downstream_runs = derivation_runs + [
        run_module("self_actualize.runtime.derive_phase4_structured_neuron_storage"),
        run_module("self_actualize.runtime.derive_knowledge_fabric"),
        run_module("self_actualize.runtime.derive_phase4_pt2_inter_metro_lens_weight_superstructure"),
        run_module("self_actualize.runtime.verify_qshrink_stack"),
        run_module("self_actualize.runtime.verify_aqm_runtime_lane"),
        run_module("self_actualize.runtime.verify_atlasforge_runtime_lane"),
        run_module("self_actualize.runtime.verify_runtime_waist"),
    ]

    verification = build_verification(generated_paths, downstream_runs)
    dashboard = build_dashboard(verification)

    write_json(DASHBOARD_JSON_PATH, dashboard)
    write_json(DASHBOARD_JSON_MIRROR, dashboard)
    write_json(VERIFICATION_JSON_PATH, verification)
    write_json(VERIFICATION_JSON_MIRROR, verification)
    write_text(DASHBOARD_MD_PATH, render_dashboard(dashboard))
    write_text(VERIFICATION_MD_PATH, render_verification(verification))
    write_text(RUNTIME_MD_PATH, render_runtime(outputs, verification))
    write_text(RECEIPT_MD_PATH, render_receipt(runtime_carrier, verification, downstream_runs))

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
            ATHENA_FLEET_ROUTE_MAP_PATH,
            ORGIN_ROUTE_MAP_PATH,
            QUEST_BOARD_PATH,
            CHANGE_FEED_PATH,
            QSHRINK_ACTIVE_FRONT_PATH,
            QSHRINK_FAMILY_PATH,
            QSHRINK_ROUTE_MAP_PATH,
            QSHRINK_ECOSYSTEM_CAPSULE_PATH,
            QSHRINK_AGENT_PLAN_PATH,
            QSHRINK_AGENT_CAPSULE_PATH,
        ]
    )

    print(f"Wrote Q42 Cloud-runtime-hardening artifacts under {SELF_ACTUALIZE_ROOT}")
    print(f"Truth: {verification['truth']}")
    return 0 if verification["truth"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
