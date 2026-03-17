from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
FAMILIES_ROOT = NERVOUS_SYSTEM_ROOT / "families"
TRADING_BOT_ROOT = WORKSPACE_ROOT / "Trading Bot"

SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
WITNESS_HIERARCHY_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
LIVE_DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "trading_bot_truth_corridor.json"
OUTPUT_FAMILY_PATH = FAMILIES_ROOT / "FAMILY_trading_bot.md"
OUTPUT_ROUTE_MAP_PATH = FAMILIES_ROOT / "FAMILY_trading_bot_route_map.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_trading_bot_truth_corridor"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def body_index(payload: dict) -> dict[str, dict]:
    return {entry["body"]: entry for entry in payload.get("body_profiles", [])}


def parse_gate_surface() -> dict:
    if not LIVE_DOCS_GATE_PATH.exists():
        return {"command_status": "UNKNOWN", "return_code": None}
    markdown = read_text(LIVE_DOCS_GATE_PATH)
    command_status = "UNKNOWN"
    return_code = None
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Command status:"):
            command_status = stripped.split("`")[1]
        if stripped.startswith("- Return code:"):
            try:
                return_code = int(stripped.split("`")[1])
            except (IndexError, ValueError):
                return_code = None
    return {"command_status": command_status, "return_code": return_code}


def resolve_gate_state() -> tuple[str, str, dict]:
    credentials_path = TRADING_BOT_ROOT / "credentials.json"
    token_path = TRADING_BOT_ROOT / "token.json"
    credentials_exists = credentials_path.exists()
    token_exists = token_path.exists()
    gate_surface = parse_gate_surface()

    if credentials_exists and token_exists:
        gate_detail = (
            "open"
            if gate_surface["command_status"] in {"OPEN", "OK", "AUTHED"} or gate_surface["return_code"] == 0
            else "blocked-by-auth-failure"
        )
        gate_state = "AUTHED" if gate_detail == "open" else "BLOCKED"
    elif credentials_exists:
        gate_detail = "blocked-by-missing-token"
        gate_state = "READY_FOR_AUTH"
    else:
        gate_detail = "blocked-by-missing-credentials"
        gate_state = "BLOCKED"

    return gate_state, gate_detail, {
        "credentials_path": str(credentials_path),
        "token_path": str(token_path),
        "credentials_exists": credentials_exists,
        "token_exists": token_exists,
        "command_status": gate_surface["command_status"],
        "return_code": gate_surface["return_code"],
    }


def derive_payload() -> dict:
    semantic_mass = load_json(SEMANTIC_MASS_PATH)
    witness_hierarchy = load_json(WITNESS_HIERARCHY_PATH)
    trading_bot_profile = body_index(semantic_mass).get("Trading Bot", {})
    witnesses = witness_hierarchy["witnesses"]
    gate_state, gate_detail, gate_files = resolve_gate_state()

    corridor_truth = "OK" if gate_detail == "open" else "NEAR"
    gate_truth = "OK" if gate_detail == "open" else "FAIL"
    fallback_mode = "local-first-truth-corridor" if gate_detail != "open" else "mirrored-live-docs"

    return {
        "generated_at": utc_now(),
        "derivation_command": DERIVATION_COMMAND,
        "truth": corridor_truth,
        "gate_state": gate_state,
        "gate_detail": gate_detail,
        "gate_truth": gate_truth,
        "fallback_mode": fallback_mode,
        "source_paths": {
            "trading_bot_root": str(TRADING_BOT_ROOT),
            "live_docs_gate_status": str(LIVE_DOCS_GATE_PATH),
            "semantic_mass_ledger": str(SEMANTIC_MASS_PATH),
            "witness_hierarchy": str(WITNESS_HIERARCHY_PATH),
        },
        "gate_files": gate_files,
        "body_metrics": {
            "records": trading_bot_profile.get("records", 0),
            "source_records": trading_bot_profile.get("role_counts", {}).get("source", 0),
            "ledger_records": trading_bot_profile.get("role_counts", {}).get("ledger", 0),
            "protocol_records": trading_bot_profile.get("role_counts", {}).get("protocol", 0),
            "generated_records": trading_bot_profile.get("role_counts", {}).get("generated", 0),
        },
        "witness_metrics": {
            "indexed": witnesses["indexed"]["value"],
            "board": witnesses["board"]["value"],
            "promoted": witnesses["promoted"]["value"],
        },
        "corridor_legs": [
            {
                "id": "LEG-01",
                "name": "local-governance-body",
                "truth": "OK",
                "meaning": "The Trading Bot body already exists locally as source, ledger, metro, swarm, and manuscript matter.",
                "surfaces": [
                    "Trading Bot/README.md",
                    "Trading Bot/docs_search.py",
                    "Trading Bot/TRADING_BOT_ATHENA_256X4/00_CONTROL/00_SYSTEM_CHARTER.md",
                    "Trading Bot/TRADING_BOT_ATHENA_256X4/03_METRO/04_RISK_CORRIDORS.md",
                    "Trading Bot/TRADING_BOT_ATHENA_256X4/04_SWARM/04_37_GATE_EXECUTION_LOOP.md",
                ],
            },
            {
                "id": "LEG-02",
                "name": "live-docs-ingress",
                "truth": gate_truth,
                "meaning": "Live Docs ingress must report an explicit blocked or open subtype instead of collapsing into generic gate language.",
                "surfaces": [
                    "self_actualize/live_docs_gate_status.md",
                    "Trading Bot/TRADING_BOT_ATHENA_256X4/00_CONTROL/07_GOOGLE_DOCS_GATE.md",
                ],
            },
            {
                "id": "LEG-03",
                "name": "nervous-system-bridge",
                "truth": "NEAR",
                "meaning": "The corpus already knows how Docs results should route into local witness packets, but the bridge needed a canonical family root.",
                "surfaces": [
                    "self_actualize/mycelium_brain/nervous_system/ganglia/GANGLION_trading_bot.md",
                    "self_actualize/mycelium_brain/nervous_system/neurons/NEURON_google_docs_to_local_corpus.md",
                ],
            },
            {
                "id": "LEG-04",
                "name": "truth-corridor-governance",
                "truth": corridor_truth,
                "meaning": "Even while the live gate is blocked, Trading Bot can be routed honestly into Hall, queue, manifest, and receipt law as a governance organ.",
                "surfaces": [
                    "self_actualize/mycelium_brain/nervous_system/families/FAMILY_trading_bot.md",
                    "self_actualize/mycelium_brain/nervous_system/families/FAMILY_trading_bot_route_map.md",
                    "self_actualize/mycelium_brain/nervous_system/manifests/DEEPER_ENHANCEMENT_ACTIVE_FRONT.md",
                    "self_actualize/mycelium_brain/nervous_system/06_active_queue.md",
                ],
            },
        ],
        "main_route": (
            "Trading Bot -> live_docs_gate_status.md -> FAMILY_trading_bot.md -> "
            "FAMILY_trading_bot_route_map.md -> DEEPER_ENHANCEMENT_ACTIVE_FRONT.md -> "
            "06_active_queue.md -> Guild Hall boards -> receipt"
        ),
        "mirror_target": "Trading Bot/LIVE_DOCS_MIRROR/",
        "next_seed": "Q34",
    }


def render_family(payload: dict) -> str:
    metrics = payload["body_metrics"]
    gate_files = payload["gate_files"]
    return f"""# FAMILY Trading Bot

Date: `{payload['generated_at'][:10]}`
Truth: `{payload['truth']}`
Primary rail: `Su`
Primary face: `Fire`
Primary hub: `AppI`

## Role

`Trading Bot` is Athena's live external-memory limb, governance-plane bridge, and
truth-corridor boundary organ.

It is not only the Docs blocker.
It is the place where blocked live ingress, launcher law, search protocol, manuscript body,
and future authenticated memory packets converge.

## Witness basis

- gate status:
  `self_actualize/live_docs_gate_status.md`
- family ganglion:
  `self_actualize/mycelium_brain/nervous_system/ganglia/GANGLION_trading_bot.md`
- Docs neuron:
  `self_actualize/mycelium_brain/nervous_system/neurons/NEURON_google_docs_to_local_corpus.md`
- local body:
  `Trading Bot/README.md`
  `Trading Bot/docs_search.py`
  `Trading Bot/TRADING_BOT_ATHENA_256X4/`
- machine witness:
  `self_actualize/trading_bot_truth_corridor.json`

## Local mass

- indexed records: `{metrics['records']}`
- source records: `{metrics['source_records']}`
- ledger records: `{metrics['ledger_records']}`
- protocol records: `{metrics['protocol_records']}`
- generated records: `{metrics['generated_records']}`

## Gate state

- Docs gate state: `{payload['gate_state']}`
- Docs gate detail: `{payload['gate_detail']}`
- credentials present: `{gate_files['credentials_exists']}`
- token present: `{gate_files['token_exists']}`
- fallback mode: `{payload['fallback_mode']}`

## Truth corridor

1. `LEG-01 local-governance-body` is `OK`:
   the local Trading Bot corpus is already a real organ with control, metro, swarm,
   ledger, and self-improvement surfaces.
2. `LEG-02 live-docs-ingress` is `{payload['gate_truth']}`:
   authenticated Google Docs ingress is still blocked until OAuth files appear.
3. `LEG-03 nervous-system-bridge` is `NEAR`:
   the existing Docs neuron and ganglion can now route through one canonical family root.
4. `LEG-04 truth-corridor-governance` is `{payload['truth']}`:
   Hall, queue, manifest, and receipt law can treat Trading Bot as a routed truth organ
   without pretending the live Docs limb is already open.

## Gate law

- blocked-by-missing-credentials:
  OAuth client material is absent, so only local corpus truth is lawful.
- blocked-by-missing-token:
  credentials exist, but an authenticated token has not been minted yet.
- blocked-by-auth-failure:
  both files exist, but the last gate witness did not prove an open session.
- open:
  live Docs search may mirror into local markdown, but mirrored outputs remain non-authoritative
  until atlas-indexed and cited by a witness surface.

## Current front

The next lawful frontier is no longer to "discover" what Trading Bot is.
It is to keep the blocked live-memory limb honest while reusing the newly routed governance
plane for runtime leverage and future authenticated Docs manifests.
"""


def render_route_map(payload: dict) -> str:
    return f"""# FAMILY Trading Bot Route Map

## Intake

- `Trading Bot/README.md`
- `Trading Bot/docs_search.py`
- `Trading Bot/search_docs.ps1`
- `Trading Bot/search_docs.cmd`
- `Trading Bot/TRADING_BOT_ATHENA_256X4/00_CONTROL/07_GOOGLE_DOCS_GATE.md`
- `Trading Bot/TRADING_BOT_ATHENA_256X4/03_METRO/04_RISK_CORRIDORS.md`
- `Trading Bot/TRADING_BOT_ATHENA_256X4/04_SWARM/04_37_GATE_EXECUTION_LOOP.md`

## Main transfer

`{payload['main_route']}`

## Law

Read `Trading Bot` through a split corridor:

- blocked live ingress remains explicit truth
- local governance body remains valid direct source
- neuron bridge remains the lawful path from future Docs results into local witness packets
- Hall and queue surfaces may route through the family root without implying authenticated memory

## Next route

`Trading Bot -> LIVE_DOCS_MIRROR -> atlas refresh -> witness packet -> authenticated Docs manifest`

Until then:

`Trading Bot -> truth corridor -> Hall/queue/manifest writeback -> next ranked frontier`
"""


def main() -> int:
    payload = derive_payload()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_FAMILY_PATH.write_text(render_family(payload), encoding="utf-8")
    OUTPUT_ROUTE_MAP_PATH.write_text(render_route_map(payload), encoding="utf-8")
    print(f"Wrote trading bot truth corridor json: {OUTPUT_JSON_PATH}")
    print(f"Wrote trading bot family root: {OUTPUT_FAMILY_PATH}")
    print(f"Wrote trading bot route map: {OUTPUT_ROUTE_MAP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
