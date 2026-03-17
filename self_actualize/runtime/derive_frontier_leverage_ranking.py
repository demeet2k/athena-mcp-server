from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
TEMPLE_ROOT = MYCELIUM_ROOT / "ATHENA TEMPLE"
RECEIPTS_ROOT = MYCELIUM_ROOT / "receipts"

SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
WITNESS_HIERARCHY_PATH = SELF_ACTUALIZE_ROOT / "witness_hierarchy.json"
CORPUS_ATLAS_SUMMARY_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas_summary.md"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "frontier_leverage_ranking.json"
OUTPUT_MARKDOWN_PATH = GUILD_HALL_ROOT / "10_FRONTIER_LEVERAGE_RANKING.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-09_q25_semantic_witness_archive_leverage_ranking.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_frontier_leverage_ranking"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def quest_status_map(path: Path) -> dict[str, str]:
    statuses: dict[str, str] = {}
    pattern = r"### Quest (Q\d+): .* `\[(OPEN|BLOCKED|PROMOTED(?: [0-9-]+)?)\]`"
    for quest_id, raw_state in __import__("re").findall(pattern, path.read_text(encoding="utf-8")):
        if raw_state.startswith("PROMOTED"):
            statuses[quest_id] = "PROMOTED"
        else:
            statuses[quest_id] = raw_state
    return statuses


def body_index(payload: dict) -> dict[str, dict]:
    return {entry["body"]: entry for entry in payload.get("body_profiles", [])}


def role_index(payload: dict) -> dict[str, dict]:
    return {entry["role"]: entry for entry in payload.get("roles", [])}


def frontier_profiles(semantic_mass: dict, witness_hierarchy: dict, quest_statuses: dict[str, str]) -> tuple[list[dict], list[dict]]:
    bodies = body_index(semantic_mass)
    roles = role_index(semantic_mass)
    witnesses = witness_hierarchy["witnesses"]

    trading_bot = bodies.get("Trading Bot", {})
    math_body = bodies.get("MATH", {})
    archive_role = roles.get("archive-backed", {})

    quest_frontiers = [
        {
            "id": "Q02",
            "title": "Unlock The Live Memory Gate",
            "state": quest_statuses.get("Q02", "BLOCKED"),
            "anchor_body": "Trading Bot",
            "semantic_anchor": "ledger-heavy governance source",
            "witness_anchor": "indexed + board",
            "source_or_archive_lift": 4,
            "cross_scale_writeback": 5,
            "restart_gain": 5,
            "execution_readiness": 0,
            "blocker_penalty": 5,
            "pressure_note": "highest latent memory unlock, but still blocked by missing OAuth material",
            "evidence": {
                "anchor_records": trading_bot.get("records", 0),
                "ledger_records": trading_bot.get("role_counts", {}).get("ledger", 0),
                "source_records": trading_bot.get("role_counts", {}).get("source", 0),
                "board_witness": witnesses["board"]["value"],
            },
        },
        {
            "id": "Q36",
            "title": "Convert One AMBIG Leaf Using New Family Witness",
            "state": quest_statuses.get("Q36", "OPEN"),
            "anchor_body": "self_actualize",
            "semantic_anchor": "truth conversion + evidence ladder",
            "witness_anchor": "source + promoted + board",
            "source_or_archive_lift": 3,
            "cross_scale_writeback": 4,
            "restart_gain": 4,
            "execution_readiness": 3,
            "blocker_penalty": 0,
            "pressure_note": "new family witness is already live, so the next honest gain is to cash one ambiguity leaf into a stronger truth class",
            "evidence": {
                "self_actualize_source_records": bodies.get("self_actualize", {}).get("role_counts", {}).get("source", 0),
                "promoted_witness": witnesses["promoted"]["value"],
                "board_witness": witnesses["board"]["value"],
            },
        },
        {
            "id": "Q35",
            "title": "Mirror ORGIN Into A Routed Seed Corpus",
            "state": quest_statuses.get("Q35", "OPEN"),
            "anchor_body": "ORGIN",
            "semantic_anchor": "source mirror + routed working memory",
            "witness_anchor": "source + board",
            "source_or_archive_lift": 3,
            "cross_scale_writeback": 4,
            "restart_gain": 3,
            "execution_readiness": 3,
            "blocker_penalty": 0,
            "pressure_note": "ORGIN now has identity and routing, so the next leverage move is to give it searchable mirror tissue instead of leaving it mostly binary matter",
            "evidence": {
                "source_records": bodies.get("ORGIN", {}).get("role_counts", {}).get("source", 0),
                "board_witness": witnesses["board"]["value"],
            },
        },
        {
            "id": "Q07",
            "title": "Harden The Runtime Waist With Tests",
            "state": quest_statuses.get("Q07", "OPEN"),
            "anchor_body": "self_actualize",
            "semantic_anchor": "runtime source + replay closure",
            "witness_anchor": "indexed + receipt",
            "source_or_archive_lift": 2,
            "cross_scale_writeback": 3,
            "restart_gain": 3,
            "execution_readiness": 4,
            "blocker_penalty": 0,
            "pressure_note": "replay trust still trails synthesis sophistication, so even a narrow test lane pays across many future fronts",
            "evidence": {
                "self_actualize_records": bodies.get("self_actualize", {}).get("records", 0),
                "receipt_records": roles.get("receipt", {}).get("count", 0),
            },
        },
        {
            "id": "Q08",
            "title": "Promote Bruno Into A Source-Pinned B12 Wheel",
            "state": quest_statuses.get("Q08", "OPEN"),
            "anchor_body": "self_actualize",
            "semantic_anchor": "source-pinning + cross-domain transfer",
            "witness_anchor": "indexed",
            "source_or_archive_lift": 4,
            "cross_scale_writeback": 3,
            "restart_gain": 4,
            "execution_readiness": 3,
            "blocker_penalty": 0,
            "pressure_note": "strong source-pinning front with high transfer potential across manuscript, myth, and operator families",
            "evidence": {
                "self_actualize_source_records": bodies.get("self_actualize", {}).get("role_counts", {}).get("source", 0),
                "indexed_witness": witnesses["indexed"]["value"],
            },
        },
        {
            "id": "Q39",
            "title": "Externalize The 5/16 Contradiction Packets",
            "state": quest_statuses.get("Q39", "OPEN"),
            "anchor_body": "ATHENA TEMPLE",
            "semantic_anchor": "contradiction packetization + hall-temple writeback",
            "witness_anchor": "indexed + board + promoted",
            "source_or_archive_lift": 2,
            "cross_scale_writeback": 4,
            "restart_gain": 3,
            "execution_readiness": 3,
            "blocker_penalty": 0,
            "pressure_note": "the active contradiction band is concrete enough to packetize and route downstream",
            "evidence": {
                "temple_records": bodies.get("ATHENA TEMPLE", {}).get("records", 0),
                "board_witness": witnesses["board"]["value"],
                "promoted_witness": witnesses["promoted"]["value"],
            },
        },
        {
            "id": "Q10",
            "title": "Densify One Low-Mass Family",
            "state": quest_statuses.get("Q10", "OPEN"),
            "anchor_body": "NERVOUS_SYSTEM",
            "semantic_anchor": "source continuity + family density repair",
            "witness_anchor": "indexed",
            "source_or_archive_lift": 2,
            "cross_scale_writeback": 2,
            "restart_gain": 3,
            "execution_readiness": 4,
            "blocker_penalty": 0,
            "pressure_note": "family density skew remains a real long-range coherence risk, but the immediate leverage is lower than the fronts above",
            "evidence": {
                "nervous_system_records": bodies.get("NERVOUS_SYSTEM", {}).get("records", 0),
                "source_records": roles.get("source", {}).get("count", 0),
            },
        },
        {
            "id": "Q40",
            "title": "Sweep Stale Bruno References Beyond The Canonical Family Core",
            "state": quest_statuses.get("Q40", "OPEN"),
            "anchor_body": "self_actualize",
            "semantic_anchor": "stale-reference cleanup + atlas-facing consistency",
            "witness_anchor": "board + indexed",
            "source_or_archive_lift": 1,
            "cross_scale_writeback": 3,
            "restart_gain": 2,
            "execution_readiness": 4,
            "blocker_penalty": 0,
            "pressure_note": "the Bruno family core is now clean, so older meta-surfaces need a stale-reference sweep",
            "evidence": {
                "indexed_witness": witnesses["indexed"]["value"],
                "board_witness": witnesses["board"]["value"],
            },
        },
    ]

    unassigned_fronts = [
        {
            "id": "FRONT-NEXT-ARCHIVE-CANDIDATE",
            "title": "Choose The Next Archive Root After ATLAS FORGE",
            "why_now": "the first archive lift is now executable, so the next dark-matter root should be ranked deliberately rather than reopened by narrative heat",
            "anchor_records": archive_role.get("count", 0),
            "ledger_records": math_body.get("role_counts", {}).get("source", 0),
        }
    ]
    return quest_frontiers, unassigned_fronts


def score_frontier(frontier: dict) -> dict:
    leverage_score = (
        frontier["source_or_archive_lift"]
        + frontier["cross_scale_writeback"]
        + frontier["restart_gain"]
        + frontier["execution_readiness"]
        - frontier["blocker_penalty"]
    )
    ranked = dict(frontier)
    ranked["leverage_score"] = leverage_score
    return ranked


def derive_frontier_leverage_ranking() -> dict:
    semantic_mass = load_json(SEMANTIC_MASS_PATH)
    witness_hierarchy = load_json(WITNESS_HIERARCHY_PATH)
    statuses = quest_status_map(QUEST_BOARD_PATH)
    quest_frontiers, unassigned_fronts = frontier_profiles(semantic_mass, witness_hierarchy, statuses)
    ranked = [score_frontier(frontier) for frontier in quest_frontiers]
    blocked = [frontier for frontier in ranked if frontier["state"] == "BLOCKED"]
    executable = [frontier for frontier in ranked if frontier["state"] == "OPEN"]
    blocked.sort(key=lambda item: (-item["leverage_score"], item["id"]))
    executable.sort(key=lambda item: (-item["leverage_score"], item["id"]))

    roles = role_index(semantic_mass)
    witnesses = witness_hierarchy["witnesses"]

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-10.q25.guild-state.runtime",
        "derivation_command": DERIVATION_COMMAND,
        "source_paths": {
            "semantic_mass_ledger": str(SEMANTIC_MASS_PATH),
            "witness_hierarchy": str(WITNESS_HIERARCHY_PATH),
            "corpus_atlas_summary": str(CORPUS_ATLAS_SUMMARY_PATH),
            "quest_board": str(QUEST_BOARD_PATH),
        },
        "source_timestamps": {
            "semantic_mass_ledger": file_timestamp(SEMANTIC_MASS_PATH),
            "witness_hierarchy": file_timestamp(WITNESS_HIERARCHY_PATH),
            "corpus_atlas_summary": file_timestamp(CORPUS_ATLAS_SUMMARY_PATH),
            "quest_board": file_timestamp(QUEST_BOARD_PATH),
        },
        "current_evidence": {
            "indexed_witness": witnesses["indexed"]["value"],
            "physical_witness": witnesses["physical"]["value"],
            "board_witness": witnesses["board"]["value"],
            "archive_witness": witnesses["archive"]["value"],
            "promoted_witness": witnesses["promoted"]["value"],
            "live_source_share_percent": roles["source"]["share_of_live_percent"],
            "live_generated_share_percent": roles["generated"]["share_of_live_percent"],
            "archive_backed_share_percent": roles["archive-backed"]["share_of_indexed_percent"],
        },
        "rank_formula": "source_or_archive_lift + cross_scale_writeback + restart_gain + execution_readiness - blocker_penalty",
        "rank_dimensions": [
            "source_or_archive_lift",
            "cross_scale_writeback",
            "restart_gain",
            "execution_readiness",
            "blocker_penalty",
        ],
        "blocked_frontiers": blocked,
        "executable_frontiers": executable,
        "unassigned_fronts": unassigned_fronts,
        "recommended_next_seed": executable[0]["id"] if executable else None,
    }


def render_frontier_line(frontier: dict, ordinal: int) -> str:
    factors = (
        f"lift={frontier['source_or_archive_lift']}, "
        f"writeback={frontier['cross_scale_writeback']}, "
        f"restart={frontier['restart_gain']}, "
        f"readiness={frontier['execution_readiness']}, "
        f"penalty={frontier['blocker_penalty']}"
    )
    return (
        f"{ordinal}. `{frontier['id']} {frontier['title']}`\n"
        f"   score: `{frontier['leverage_score']}`\n"
        f"   anchor: `{frontier['anchor_body']}` via `{frontier['semantic_anchor']}` and `{frontier['witness_anchor']}`\n"
        f"   shape: {factors}\n"
        f"   why-now: {frontier['pressure_note']}"
    )


def render_markdown(payload: dict) -> str:
    blocked_lines = "\n".join(
        render_frontier_line(frontier, ordinal)
        for ordinal, frontier in enumerate(payload["blocked_frontiers"], start=1)
    )
    executable_lines = "\n".join(
        render_frontier_line(frontier, ordinal)
        for ordinal, frontier in enumerate(payload["executable_frontiers"], start=1)
    )
    unassigned = payload["unassigned_fronts"][0]
    evidence = payload["current_evidence"]

    return f"""# Frontier Leverage Ranking

Date: `{payload['generated_at'][:10]}`
Quest: `Q25`
Temple Frontier: `TQ02`
Truth: `OK`

## Inputs

- `self_actualize/semantic_mass_ledger.json`
- `self_actualize/witness_hierarchy.json`
- `self_actualize/corpus_atlas_summary.md`
- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/01_ACTIVE_FRONTS_BOARD.md`
- `GLOBAL_EMERGENT_GUILD_HALL/BOARDS/06_QUEST_BOARD.md`

## Ranking Recipe

Each frontier is ranked by four positive factors and one penalty:

1. `source_or_archive_lift`
   how much source-rich or archive-backed witness becomes more reusable
2. `cross_scale_writeback`
   how many organs become cleaner if the front lands
3. `restart_gain`
   how much the next loop gets easier, clearer, or more honest
4. `execution_readiness`
   how executable the front is with current local witness
5. `blocker_penalty`
   subtract when the front is currently blocked by an external dependency

Working score:

`leverage_score = {payload['rank_formula']}`

## Current Evidence Read

- indexed witness: `{evidence['indexed_witness']}`
- physical witness: `{evidence['physical_witness']}`
- board witness: `{evidence['board_witness']}`
- archive witness: `{evidence['archive_witness']}`
- promoted witness: `{evidence['promoted_witness']}`
- live source share: `{evidence['live_source_share_percent']}%`
- live generated share: `{evidence['live_generated_share_percent']}%`
- archive-backed share relative to indexed: `{evidence['archive_backed_share_percent']}%`

Interpretation:

- raw generated mass is not a good proxy for leverage
- promoted source roots and archive-backed unlocks deserve more weight than narrative heat alone
- restart gain matters most when it also improves replay, routeability, or lawful reuse

## Blocked Highest Latent Leverage

{blocked_lines}

## Executable Order

{executable_lines}

## Highest Unassigned Pressure

- `{unassigned['id']}`:
  {unassigned['title']}
- Why now:
  {unassigned['why_now']}
- Anchor:
  `archive reservoir` with `{unassigned['anchor_records']}` archive-backed records and `{unassigned['ledger_records']}` source-ledger anchor records

## Before/After

Before:

- freshness was getting better, but frontier order still drifted between boards
- `Q25` existed mostly as prose, not as a rerunnable measurement pass
- the Hall could say one thing about priority while the queue and Temple still implied another

After:

- `Q25` is now grounded in a runtime derivation path
- blocked latent leverage is separated from executable leverage
- the strongest executable front after this pass is `{payload['recommended_next_seed']}`
- the strongest next quest candidate beyond the current numbered set is `{unassigned['id']}`

## Restart Seed

`{payload['recommended_next_seed']}`
"""


def render_receipt(payload: dict) -> str:
    evidence = payload["current_evidence"]
    executable = payload["executable_frontiers"][0]
    return f"""# Q25 Semantic Witness And Archive Leverage Ranking Receipt

- Generated: `{payload['generated_at']}`
- Quest: `Q25 Rank Live Fronts By Semantic Witness And Archive Leverage`
- Temple frontier: `TQ02 Couple Semantic Mass And Witness Class To Quest Ranking`
- Verdict: `OK`
- Command: `{payload['derivation_command']}`

## Source Basis

- semantic mass ledger:
  `{payload['source_paths']['semantic_mass_ledger']}` at `{payload['source_timestamps']['semantic_mass_ledger']}`
- witness hierarchy:
  `{payload['source_paths']['witness_hierarchy']}` at `{payload['source_timestamps']['witness_hierarchy']}`
- corpus atlas summary:
  `{payload['source_paths']['corpus_atlas_summary']}` at `{payload['source_timestamps']['corpus_atlas_summary']}`

## Witness Read

- indexed witness: `{evidence['indexed_witness']}`
- physical witness: `{evidence['physical_witness']}`
- board witness: `{evidence['board_witness']}`
- archive witness: `{evidence['archive_witness']}`
- promoted witness: `{evidence['promoted_witness']}`

## Ranked Outcome

- blocked highest latent leverage: `{payload['blocked_frontiers'][0]['id']}`
- executable highest leverage: `{executable['id']}`
- executable next seed: `{payload['recommended_next_seed']}`

## Deep Read

- archive-backed leverage must now compete directly with live prose-heavy bodies instead of waiting in a side queue
- generated shell mass remains operationally important, but it should not outrank source lift by default
- the next honest frontier is to bind `Trading Bot` into the truth corridor while preserving the blocked Docs limb honestly
"""


def main() -> int:
    payload = derive_frontier_leverage_ranking()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote frontier leverage ranking json: {OUTPUT_JSON_PATH}")
    print(f"Wrote frontier leverage ranking markdown: {OUTPUT_MARKDOWN_PATH}")
    print(f"Wrote frontier leverage ranking receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
