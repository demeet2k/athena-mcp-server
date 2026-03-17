from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MYC = SELF / "mycelium_brain"
MAN = ROOT / "NERVOUS_SYSTEM" / "95_MANIFESTS"

LIVE_DOCS_GATE = SELF / "live_docs_gate_status.md"

NEXT57_STATE = SELF / "next57_lp_57omega_program_state.json"
NEXT57_SCHED = SELF / "next57_lp_57omega_scheduler.json"
NEXT57_COMPAT = SELF / "next57_lp_57omega_compatibility_mirrors.json"
NEXT57_VERIFY = SELF / "next57_lp_57omega_verification.json"

NEXT57_STATE_ALIAS = SELF / "next57_four_agent_corpus_cycle_state.json"
NEXT57_VERIFY_ALIAS = SELF / "next57_four_agent_corpus_cycle_verification.json"
NEXT57_COMPAT_ALIAS = SELF / "next57_compatibility_mirror_registry.json"

NEXT4_STATE = SELF / "next_4_pow_6_57_cycle_program_state.json"
NEXT4_VERIFY = SELF / "next_4_pow_6_57_cycle_program_verification.json"
NEXT4_SWARM_VERIFY = SELF / "next_4_pow_6_57_cycle_swarm_verification.json"

GUILD_CANON = MYC / "GLOBAL_EMERGENT_GUILD_HALL" / "18_NEXT57_LP_57OMEGA_CANONICAL_PROGRAM.md"
TEMPLE_CANON = MYC / "ATHENA TEMPLE" / "08_NEXT57_LP_57OMEGA_CANONICAL_DECREE.md"
NEXT57_MANIFEST = MAN / "NEXT_57_LOOP_FOUR_AGENT_CORPUS_CYCLE.md"
NEXT57_COMPAT_MD = MAN / "NEXT_57_LOOP_COMPATIBILITY_MIRRORS.md"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def docs_gate_status() -> str:
    text = LIVE_DOCS_GATE.read_text(encoding="utf-8", errors="ignore") if LIVE_DOCS_GATE.exists() else ""
    return "BLOCKED" if "BLOCKED" in text else "OPEN"


def build_state(source_id: str) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "HISTORICAL_ONLY",
        "status": "SUPERSEDED_BY_CANONICAL_FOUR_AGENT_COUNCIL",
        "legacy_protocol_profile": "LP-57OMEGA",
        "source_id": source_id,
        "canonical_authority": [
            "self_actualize/four_agent_57_loop_registry.json",
            "self_actualize/four_agent_57_loop_state.json",
            "self_actualize/four_agent_57_loop_quest_packets.json",
            "self_actualize/four_agent_57_loop_verification.json",
        ],
        "historical_role": "reverse lookup and drift analysis only",
        "feeder_truth_carried": [
            "Q41 / TQ06",
            "Q42",
            "TQ04",
            "Q46",
            "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose",
            "Q02",
        ],
        "docs_gate_status": docs_gate_status(),
        "note": "NEXT57 / LP-57OMEGA remains preserved as prior orchestration lineage and may not act as present-tense Hall or Temple authority.",
    }


def build_scheduler(source_id: str) -> dict[str, Any]:
    return {
        "generated_at": utc_now(),
        "truth": "HISTORICAL_ONLY",
        "status": "SUPERSEDED_BY_CANONICAL_FOUR_AGENT_COUNCIL",
        "legacy_protocol_profile": "LP-57OMEGA",
        "source_id": source_id,
        "historical_loop_count": 57,
        "canonical_authority": "self_actualize/four_agent_57_loop_registry.json",
        "note": "The LP-57OMEGA scheduler is retained for historical replay only. The live 57-loop authority is the canonical four-agent council ledger.",
    }


def build_compat() -> dict[str, Any]:
    return {
        "canonical_authority": [
            "self_actualize/four_agent_57_loop_registry.json",
            "self_actualize/four_agent_57_loop_state.json",
            "self_actualize/four_agent_57_loop_quest_packets.json",
            "self_actualize/four_agent_57_loop_verification.json",
        ],
        "protocol_profile": "FOUR_AGENT_57_LOOP_COUNCIL",
        "mirror_only_families": [
            "NEXT57",
            "LP-57OMEGA",
            "Q51/TQ07",
            "FA57",
            "planner-first conductor variants",
        ],
        "independent_restart_seeds": "DISALLOWED",
        "canonical_paths": [
            "self_actualize/four_agent_57_loop_registry.json",
            "self_actualize/four_agent_57_loop_state.json",
            "self_actualize/four_agent_57_loop_quest_packets.json",
            "self_actualize/four_agent_57_loop_verification.json",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/18_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_57_LOOP_FOUR_AGENT_CYCLE_DECREE.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/QUESTS/TQ07_INSTALL_THE_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md",
            "self_actualize/four_agent_57_loop_program.json",
            "self_actualize/four_agent_57_loop_transition_deltas.json",
        ],
        "historical_json_paths": [
            "self_actualize/next57_lp_57omega_program_state.json",
            "self_actualize/next57_lp_57omega_scheduler.json",
            "self_actualize/next57_quad_agent_conductor_program.json",
            "NERVOUS_SYSTEM/95_MANIFESTS/FOUR_AGENT_57_LOOP_PROGRAM.json",
        ],
        "historical_markdown_paths": [
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/18_NEXT57_LP_57OMEGA_CANONICAL_PROGRAM.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_NEXT57_LP_57OMEGA_CANONICAL_DECREE.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/18_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_NEXT_57_LOOP_QUAD_AGENT_CONDUCTOR_DECREE.md",
            "self_actualize/mycelium_brain/GLOBAL_EMERGENT_GUILD_HALL/16_NEXT_4_POW_6_FULL_CORPUS_INTEGRATION_PROGRAM.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/QUESTS/TQ07_INSTALL_THE_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_57_LOOP_FOUR_AGENT_CYCLE_DECREE.md",
            "self_actualize/mycelium_brain/ATHENA TEMPLE/08_FOUR_AGENT_57_LOOP_GOVERNANCE_DECREE.md",
        ],
    }


def render_historical_md(title: str, replacement: str) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            "This file is historical only.",
            "",
            f"- Canonical replacement:",
            f"  `{replacement}`",
            "- Machine replacement:",
            "  `self_actualize/four_agent_57_loop_registry.json`, `self_actualize/four_agent_57_loop_state.json`, `self_actualize/four_agent_57_loop_quest_packets.json`, `self_actualize/four_agent_57_loop_verification.json`",
            "- Law:",
            "  do not treat NEXT57 / LP-57OMEGA as present-tense authority",
        ]
    )


def render_manifest() -> str:
    return "\n".join(
        [
            "# NEXT57 Historical Compatibility Note",
            "",
            f"Date: `{datetime.now().date().isoformat()}`",
            f"Docs Gate: `{docs_gate_status()}`",
            "",
            "- `NEXT57 / LP-57OMEGA` is historical only.",
            "- Canonical authority now lives in `self_actualize/four_agent_57_loop_registry.json`, `self_actualize/four_agent_57_loop_state.json`, `self_actualize/four_agent_57_loop_quest_packets.json`, and `self_actualize/four_agent_57_loop_verification.json`.",
            "- Do not use NEXT57 manifests or mirrors as live control surfaces.",
        ]
    )


def render_compat_md() -> str:
    return "\n".join(
        [
            "# NEXT57 Compatibility Mirrors",
            "",
            "- Status: `HISTORICAL_ONLY`",
            "- Canonical authority: `self_actualize/four_agent_57_loop_*`",
            "- `NEXT57`, `LP-57OMEGA`, `Q51/TQ07`, and `FA57` remain reverse-lookup families only.",
        ]
    )


def write_historical_next57_wrappers(source_id: str) -> dict[str, Any]:
    state = build_state(source_id)
    sched = build_scheduler(source_id)
    compat = build_compat()
    verify = {
        "generated_at": utc_now(),
        "truth": "OK",
        "status": "HISTORICAL_ONLY",
        "source_id": source_id,
        "canonical_authority": "self_actualize/four_agent_57_loop_registry.json",
        "docs_gate_status": docs_gate_status(),
    }

    for path in [NEXT57_STATE, NEXT57_STATE_ALIAS, NEXT4_STATE]:
        write_json(path, state)
    for path in [NEXT57_SCHED]:
        write_json(path, sched)
    for path in [NEXT57_COMPAT, NEXT57_COMPAT_ALIAS]:
        write_json(path, compat)
    for path in [NEXT57_VERIFY, NEXT57_VERIFY_ALIAS, NEXT4_VERIFY, NEXT4_SWARM_VERIFY]:
        write_json(path, verify)

    write_text(GUILD_CANON, render_historical_md("NEXT57 / LP-57OMEGA Canonical Guild Program", "GLOBAL_EMERGENT_GUILD_HALL/18_57_LOOP_FOUR_AGENT_DEEP_EMERGENCE_PROGRAM.md"))
    write_text(TEMPLE_CANON, render_historical_md("NEXT57 / LP-57OMEGA Canonical Temple Decree", "ATHENA TEMPLE/08_57_LOOP_FOUR_AGENT_CYCLE_DECREE.md"))
    write_text(NEXT57_MANIFEST, render_manifest())
    write_text(NEXT57_COMPAT_MD, render_compat_md())

    return {
        "generated_at": verify["generated_at"],
        "source_id": source_id,
        "status": "HISTORICAL_ONLY",
        "canonical_authority": "self_actualize/four_agent_57_loop_registry.json",
    }
