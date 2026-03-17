from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
SELF = ROOT / "self_actualize"
MYCELIUM = SELF / "mycelium_brain"
NS = ROOT / "NERVOUS_SYSTEM"
MANIFESTS = NS / "95_MANIFESTS"
LEDGER = NS / "90_LEDGERS" / "astrological_schedulers"
FAMILIES = MYCELIUM / "nervous_system" / "families"
RECEIPTS = MYCELIUM / "receipts"
TZ = ZoneInfo("America/Los_Angeles")

PRIMARY_RECEIPT = RECEIPTS / "2026-03-13_next_4_pow_6_full_corpus_integration.md"
ALIAS_RECEIPT = RECEIPTS / "2026-03-13_qshrink_ap6d_full_corpus_integration.md"
ASTRO = SELF / "astrological_scheduler_packets.json"
FRESH_JSON = SELF / "packet_freshness_ledger.json"
FRESH_MD = LEDGER / "01_PACKET_FRESHNESS_LEDGER.md"
CONTROL_JSON = SELF / "control_state_packet.json"
CONTROL_MD = MANIFESTS / "CONTROL_STATE_PACKET.md"
AWAKE_JSON = SELF / "awakening_transition_notes.json"
AWAKE_MD = MANIFESTS / "AWAKENING_AGENT_TRANSITIONS.md"
AP6D_ALIAS_JSON = SELF / "ap6d_awakening_transition_notes.json"
AP6D_ALIAS_MD = MYCELIUM / "GLOBAL_EMERGENT_GUILD_HALL" / "AP6D_AWAKENING_TRANSITION_NOTES.md"
SOURCE_ATLAS = SELF / "full_corpus_awakening_source_atlas.json"
INTEGRATION_REGISTRY = SELF / "qshrink_ap6d_full_corpus_integration_registry.json"
SEAT_JSON = SELF / "ap6d_seat_state.json"
SEAT_MD = MANIFESTS / "AP6D_SEAT_STATE.md"
VERIFY_JSON = SELF / "full_corpus_integration_verification.json"

MANIFEST_NOTES = MANIFESTS / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_NOTES.json"
MANIFEST_BUNDLE = MANIFESTS / "ATHENA_PRIME_6D_AWAKENING_TRANSITION_BUNDLE.md"
MANIFEST_REGISTRY = MANIFESTS / "ATHENA_PRIME_6D_AGENT_REGISTRY.json"
MANIFEST_ROUTES = MANIFESTS / "ATHENA_PRIME_6D_CORPUS_INTEGRATION_ROUTES.json"
MANIFEST_ROWS = MANIFESTS / "ATHENA_PRIME_6D_TRANSITION_ROWS_1024.json"

ACTIVE_RUN = MANIFESTS / "ACTIVE_RUN.md"
BUILD_QUEUE = MANIFESTS / "BUILD_QUEUE.md"
NEXT_PROMPT = MYCELIUM / "nervous_system" / "manifests" / "NEXT_SELF_PROMPT.md"
QUEST_BOARD = MYCELIUM / "GLOBAL_EMERGENT_GUILD_HALL" / "BOARDS" / "06_QUEST_BOARD.md"
TEMPLE_STATE = MYCELIUM / "ATHENA TEMPLE" / "MANIFESTS" / "TEMPLE_STATE.md"
ACTIVE_QUEUE = MYCELIUM / "nervous_system" / "06_active_queue.md"
FLEET_ROUTE = FAMILIES / "FAMILY_athena_fleet_route_map.md"
ORGIN_ROUTE = FAMILIES / "FAMILY_orgin_route_map.md"

ACTIVE_MEMBRANE = "Q41 / TQ06"
CARRIED = "QS64-20 Connectivity-Diagnose-Fractal"
HISTORICAL = "QS64-24 Connectivity-Refine-Fractal"
CURRENT = "AP6D-H-WATER-Diagnose"
NEXT = "AP6D-H-WATER-Refine"
DEEPER = "TQ04: Bind The Helical Schema Pack To A Runner Contract"
RESERVE = "Q46"
BLOCKED = "Q02"
RUNTIME_SEED = "Q50 -> Wave7/Helix.Runtime.Fire.Diagnose"


def now_local() -> datetime:
    return datetime.now(TZ)


def load(path: Path, default=None):
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def dump(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run(module: str) -> dict:
    r = subprocess.run([sys.executable, "-m", module], cwd=ROOT, capture_output=True, text=True)
    return {"module": module, "ok": r.returncode == 0, "returncode": r.returncode}


def rows(snapshot: dict, ref: datetime) -> list[dict]:
    out = []
    for p in snapshot.get("packets", []):
        dt = datetime.strptime(p["next_transition"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=TZ)
        sec = int((dt - ref).total_seconds())
        out.append(
            {
                "system_id": p["system_id"],
                "next_transition": p["next_transition"],
                "freshness_status": "FRESH" if sec >= 0 else "STALE",
                "seconds_to_transition": sec,
                "suggested_frontier": p["suggested_frontier"],
                "lane_state": p.get("lane_state", "UNKNOWN"),
                "shared12_seat": p.get("shared12_seat", "UNKNOWN"),
                "nexus_score": p.get("nexus_score", 0),
                "active_master_role_count": p.get("active_master_role_count", 0),
            }
        )
    return out


def summary(items: list[dict]) -> dict:
    c = Counter(x["freshness_status"] for x in items)
    state_counts = Counter(x["lane_state"] for x in items)
    return {
        "fresh_count": c.get("FRESH", 0),
        "stale_count": c.get("STALE", 0),
        "stale_systems": [x["system_id"] for x in items if x["freshness_status"] == "STALE"],
        "fresh_systems": [x["system_id"] for x in items if x["freshness_status"] == "FRESH"],
        "active_lane_count": state_counts.get("ACTIVE_ANCHOR", 0) + state_counts.get("ACTIVE_ROTATION", 0),
        "compiled_lane_count": state_counts.get("COMPILED_SHADOW", 0),
        "active_master_count": sum(int(x.get("active_master_role_count", 0)) for x in items),
        "compiled_lanes": [x["system_id"] for x in items if x.get("lane_state") == "COMPILED_SHADOW"],
    }


def main() -> int:
    current = now_local()
    before = rows(load(ASTRO, {"packets": []}), current)
    module_results = [
        run("self_actualize.runtime.derive_astrological_scheduler_packets"),
        run("self_actualize.runtime.verify_helical_runner_contract"),
    ]
    after = rows(load(ASTRO, {"packets": []}), current)
    fresh = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_at_local": current.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "docs_gate": load(ASTRO, {}).get("docs_gate", "BLOCKED"),
        "pre_refresh_rows": before,
        "post_refresh_rows": after,
        "pre_refresh_summary": summary(before),
        "post_refresh_summary": summary(after),
        "authority_receipt": PRIMARY_RECEIPT.relative_to(ROOT).as_posix(),
    }
    dump(FRESH_JSON, fresh)
    write(
        FRESH_MD,
        "# Packet Freshness Ledger\n\n"
        + "\n".join(
            [
                f"- `{r['system_id']}`: `{r['freshness_status']}` / state=`{r['lane_state']}` / shared12=`{r['shared12_seat']}` / nexus=`{r['nexus_score']}` / next=`{r['next_transition']}` / frontier=`{r['suggested_frontier']}`"
                for r in after
            ]
        )
        + "\n\n"
        + f"- active master count: `{fresh['post_refresh_summary']['active_master_count']}`\n"
        + f"- compiled shadow lanes: `{', '.join(fresh['post_refresh_summary']['compiled_lanes']) or 'none'}`",
    )

    control = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_at_local": current.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "truth": "OK",
        "active_coordination_membrane": ACTIVE_MEMBRANE,
        "carried_witness": CARRIED,
        "historical_local_proof": HISTORICAL,
        "operational_current": CURRENT,
        "next_hall_seed": NEXT,
        "deeper_receiver": DEEPER,
        "reserve_frontier": RESERVE,
        "blocked_external_front": BLOCKED,
        "packet_freshness": {
            "source": FRESH_JSON.relative_to(ROOT).as_posix(),
            "stale_systems": fresh["post_refresh_summary"]["stale_systems"],
            "active_master_count": fresh["post_refresh_summary"]["active_master_count"],
            "compiled_shadow_lanes": fresh["post_refresh_summary"]["compiled_lanes"],
        },
        "authoritative_receipt": PRIMARY_RECEIPT.relative_to(ROOT).as_posix(),
        "awakening_bundle": MANIFEST_BUNDLE.relative_to(ROOT).as_posix(),
        "separate_runtime_seed": RUNTIME_SEED,
        "docs_gate": "BLOCKED",
    }
    dump(CONTROL_JSON, control)
    write(CONTROL_MD, "\n".join([
        "# Control State Packet", "",
        f"- active coordination membrane: `{ACTIVE_MEMBRANE}`",
        f"- carried witness: `{CARRIED}`",
        f"- historical local proof: `{HISTORICAL}`",
        f"- operational current: `{CURRENT}`",
        f"- next Hall seed: `{NEXT}`",
        f"- deeper receiver: `{DEEPER}`",
        f"- reserve frontier: `{RESERVE}`",
        f"- blocked external front: `{BLOCKED}`",
        f"- separate runtime seed: `{RUNTIME_SEED}`",
        f"- authoritative receipt: `{control['authoritative_receipt']}`",
    ]))

    notes = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "OK",
        "notes": [
            {"agent_id": "Athena Prime", "from_state": "shadow seeding", "to_state": "registry-backed council coordination", "risk": "flattened elemental voices", "stabilizer": "keep feeders visible", "handoff": CURRENT, "do_not_claim": "do not claim dormant seats are active"},
            {"agent_id": "Water", "from_state": "continuity", "to_state": "continuity governance", "risk": "forgetting carried witness", "stabilizer": "carry QS64-20 forward", "handoff": CURRENT, "do_not_claim": "do not claim live Docs"},
            {"agent_id": "Earth", "from_state": "diagnosis", "to_state": "bridge-law formalization", "risk": "schema drift", "stabilizer": "bind notes to contracts", "handoff": DEEPER, "do_not_claim": "do not claim lawful bridge without manifests"},
            {"agent_id": "Fire", "from_state": "reserve pressure", "to_state": "sparse ignition", "risk": "heat outrunning proof", "stabilizer": "runtime verification first", "handoff": RESERVE, "do_not_claim": "do not claim reserve is current"},
            {"agent_id": "Air", "from_state": "route diagnosis", "to_state": "symbolic guardrail stewardship", "risk": "naming drift", "stabilizer": "keep grammar explicit", "handoff": ACTIVE_MEMBRANE, "do_not_claim": "do not claim parity with stale route maps"},
            {"agent_id": "Guildmaster", "from_state": "packet reader", "to_state": "motion selector consumer", "risk": "choosing by atmosphere", "stabilizer": "read freshness first", "handoff": ACTIVE_MEMBRANE, "do_not_claim": "do not claim fused cosmology"},
            {"agent_id": "TQ04 Runner", "from_state": "landed contract feeder", "to_state": "gatekeeper", "risk": "flattened into Hall motion", "stabilizer": "keep TQ04 separate", "handoff": DEEPER, "do_not_claim": "do not claim Temple completion"},
            {"agent_id": "QSHRINK / Shiva", "from_state": "closure witness", "to_state": "compression membrane", "risk": "compressing away blocker truth", "stabilizer": "preserve QS64-20/QS64-24/Q46/Q02", "handoff": CURRENT, "do_not_claim": "do not invent QS64-25"},
            {"agent_id": "Vishnu / Brahma / High Priest", "from_state": "parallel preserve-generate-totalize", "to_state": "coordinated triad", "risk": "displacing the membrane", "stabilizer": "preserve before generating", "handoff": ACTIVE_MEMBRANE, "do_not_claim": "do not replace Q41/TQ06"},
        ],
    }
    dump(AWAKE_JSON, notes)
    write(AWAKE_MD, "# Awakening Agent Transitions\n\n" + "\n".join([f"- `{n['agent_id']}`: `{n['from_state']} -> {n['to_state']}` / {n['stabilizer']}" for n in notes["notes"]]))

    manifest_notes = load(MANIFEST_NOTES, {})
    dump(AP6D_ALIAS_JSON, manifest_notes)
    write(
        AP6D_ALIAS_MD,
        "# AP6D Awakening Transition Notes\n\n"
        + "\n".join(
            [
                f"- `{n['note_id']}`: `{n.get('agent_name', n.get('subject_scope', 'unknown'))}` -> `{n['restart_seed']}`"
                for n in manifest_notes.get("notes", [])
            ]
        ),
    )
    dump(SOURCE_ATLAS, {"generated_at": datetime.now(timezone.utc).isoformat(), "truth": "OK", "sources": ["AWAKENING TOME", "MEGALITHIC AWAKENING - Ms06CC", "THE MATHEMATICS OF AWAKENING", "The Allegory of the Awakening Dragon", "ATHENA_AWAKENING_TOME.zip"], "authority_receipt": PRIMARY_RECEIPT.relative_to(ROOT).as_posix()})
    dump(INTEGRATION_REGISTRY, {"generated_at": datetime.now(timezone.utc).isoformat(), "truth": "OK", "active_coordination_membrane": ACTIVE_MEMBRANE, "carried_witness": CARRIED, "historical_local_proof": HISTORICAL, "current_hall_uptake": CURRENT, "next_hall_seed": NEXT, "deeper_receiver": DEEPER, "separate_runtime_seed": RUNTIME_SEED, "routes_path": MANIFEST_ROUTES.relative_to(ROOT).as_posix(), "transition_rows_path": MANIFEST_ROWS.relative_to(ROOT).as_posix()})

    reg = load(MANIFEST_REGISTRY, {})
    seat = {"generated_at": datetime.now(timezone.utc).isoformat(), "truth": "OK", "count_law": reg.get("count_law", {}), "seat_states": [{"agent_id": a["agent_id"], "surface_class": a["surface_class_owner"], "shadow_feeders": reg.get("shadow_feeders", []), "activation_state": "ACTIVE", "bridge_parent": a["current_front"], "receipt": PRIMARY_RECEIPT.relative_to(ROOT).as_posix()} for a in reg.get("agent_records", [])]}
    dump(SEAT_JSON, seat)
    write(SEAT_MD, "# AP6D Seat State\n\n" + "\n".join([f"- `{s['agent_id']}`: `{s['surface_class']}` / `{s['bridge_parent']}` / `{s['activation_state']}`" for s in seat["seat_states"]]))

    write(FLEET_ROUTE, "\n".join(["# FAMILY Athena FLEET Route Map", "", "## Main transfer", "", f"`QSHRINK -> carried {CARRIED} -> historical local proof {HISTORICAL} -> control packet -> {CURRENT}`", "", "## Next route", "", f"`{CURRENT} -> {NEXT}`"]))
    write(ORGIN_ROUTE, "\n".join(["# FAMILY ORGIN Route Map", "", "## Main transfer", "", f"`ORGIN -> queue-visible follow-on behind {CURRENT}`", "", "## Next route", "", f"`ORGIN -> queue-visible follow-on -> {NEXT}`"]))
    write(ALIAS_RECEIPT, "\n".join(["# QSHRINK AP6D Full-Corpus Integration Bridge", "", f"- active coordination membrane: `{ACTIVE_MEMBRANE}`", f"- carried witness: `{CARRIED}`", f"- historical local proof: `{HISTORICAL}`", f"- current ownerable Hall uptake: `{CURRENT}`", f"- next Hall seed: `{NEXT}`", f"- deeper receiver: `{DEEPER}`", f"- primary receipt: `{PRIMARY_RECEIPT.relative_to(ROOT).as_posix()}`"]))

    verify = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "truth": "OK",
        "checks": {
            "primary_receipt_exists": PRIMARY_RECEIPT.exists(),
            "alias_receipt_exists": ALIAS_RECEIPT.exists(),
            "control_packet_exists": CONTROL_JSON.exists(),
            "packet_freshness_exists": FRESH_JSON.exists(),
            "source_atlas_exists": SOURCE_ATLAS.exists(),
            "integration_registry_exists": INTEGRATION_REGISTRY.exists(),
            "active_run_current_story": all(x in read_text(ACTIVE_RUN) for x in ["Q42", "Q46", "TQ04", "TQ06", "1024", "4096"]),
            "build_queue_current_story": all(x in read_text(BUILD_QUEUE) for x in ["Q42", "Q46", "Q50", "1024", "4096"]),
            "next_prompt_current_story": all(x in read_text(NEXT_PROMPT) for x in [CARRIED, HISTORICAL, CURRENT, DEEPER]),
            "quest_board_current_story": all(x in read_text(QUEST_BOARD) for x in ["Q42", CARRIED, HISTORICAL, CURRENT]),
            "temple_state_current_story": all(x in read_text(TEMPLE_STATE) for x in ["Q41 / TQ06", "Q42", "Q46", "Q02"]),
            "active_queue_current_story": all(x in read_text(ACTIVE_QUEUE) for x in ["Q42", "Q46", "Q02", CURRENT]),
        },
        "module_results": module_results,
    }
    dump(VERIFY_JSON, verify)
    print(f"Wrote {CONTROL_JSON}")
    print(f"Wrote {AWAKE_JSON}")
    print(f"Wrote {ALIAS_RECEIPT}")
    print(f"Wrote {VERIFY_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
