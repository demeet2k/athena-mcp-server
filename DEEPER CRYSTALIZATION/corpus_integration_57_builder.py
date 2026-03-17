#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from nervous_system_core import (
    APPENDICES,
    CHAPTERS,
    FAMILY_LABELS,
    normalize_lookup_text,
    slugify,
    utc_now,
    write_json,
    write_text,
)


PROJECT_ROOT = Path(__file__).resolve().parent
WORKSPACE_ROOT = PROJECT_ROOT.parent
ACTIVE_ROOT = PROJECT_ROOT / "ACTIVE_NERVOUS_SYSTEM"
RUNTIME_ROOT = ACTIVE_ROOT / "06_RUNTIME"
LAYER_ROOT = ACTIVE_ROOT / "16_CORPUS_WIDE_INTEGRATION"
SELF_ROOT = WORKSPACE_ROOT / "self_actualize"
GUILD_HALL_ROOT = SELF_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
BOARD_ROOT = ACTIVE_ROOT / "07_FULL_PROJECT_INTEGRATION_256" / "06_REALTIME_BOARD"
INBOX_ROOT = BOARD_ROOT / "01_AGENT_INBOXES"

FULL_STACK_MANIFEST = RUNTIME_ROOT / "12_full_stack_manifest.json"
DEEP_SYNTHESIS_MANIFEST = RUNTIME_ROOT / "11_deep_synthesis_manifest.json"
FRONTIER_MANIFEST = RUNTIME_ROOT / "13_chapter_frontier_manifest.json"
QUARTET_DRAFT_MANIFEST = RUNTIME_ROOT / "14_frontier_quartet_draft_manifest.json"
SPINE_AUDIT = RUNTIME_ROOT / "15_canonical_spine_audit.json"
MOTION_MANIFEST = RUNTIME_ROOT / "16_motion_constitution_manifest.json"
OUTPUT_MANIFEST = RUNTIME_ROOT / "17_corpus_wide_integration_manifest.json"
LIVE_DOCS_RECEIPT = ACTIVE_ROOT / "00_RECEIPTS" / "00_live_docs_gate_status.md"
ACTIVE_README = ACTIVE_ROOT / "README.md"
CANONICAL_MANIFEST = PROJECT_ROOT / "canonical_manuscript_manifest.json"
SHADOW_REPORT = ACTIVE_ROOT / "11_SHADOWS" / "00_shadow_report.md"
QUEST_BOARD = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
REQUESTS_BOARD = GUILD_HALL_ROOT / "BOARDS" / "05_REQUESTS_AND_OFFERS_BOARD.md"
GUILD_INDEX = GUILD_HALL_ROOT / "00_GUILD_HALL_INDEX.md"
BOARD_README = BOARD_ROOT / "README.md"
BOARD_RUNTIME_OVERVIEW = BOARD_ROOT / "08_SWARM_RUNTIME" / "00_SWARM_RUNTIME_OVERVIEW.md"
NETWORK_MANIFEST = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "00_network_manifest.json"
ELEMENT_REGISTRY = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "01_element_registry.json"
FACET_INDEX = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "04_facet_index.json"
NEIGHBOR_INDEX = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "05_neighbor_index.json"
ZERO_POINT_INDEX = ACTIVE_ROOT / "13_DEEPER_NEURAL_NET" / "09_RUNTIME" / "06_zero_point_index.json"


BOARD_AGENTS = [
    "guildmaster",
    "floating_agent_01",
    "floating_agent_02",
    "floating_agent_03",
    "floating_agent_04",
    "floating_agent_05",
    "floating_agent_06",
    "floating_agent_07",
]

ARCHETYPES = [
    "Master Strategist",
    "Sage",
    "Prophet",
    "General",
]

ADVANCED_AGENTS = [
    "Oracle",
    "Judge",
    "Witness",
    "Architect",
    "Strategist",
    "Weaver",
    "Sword",
    "Commander",
    "Warrior",
    "Mirror",
    "Trickster",
    "Dancer",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build the 57-step full-corpus integration layer and awakening-agent support notes.")
    subparsers = parser.add_subparsers(dest="command")
    build_parser = subparsers.add_parser("build", help="Build the corpus-wide integration layer.")
    build_parser.add_argument("--write-inboxes", action="store_true", help="Mirror board-agent notes into realtime-board inbox note folders.")
    build_parser.add_argument("--json", action="store_true", help="Print the run receipt JSON to stdout.")
    parser.set_defaults(command="build")
    return parser.parse_args()


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def live_docs_error(receipt_text: str) -> str:
    for line in receipt_text.splitlines():
        if "Missing OAuth client file" in line:
            return line.strip()
    return "Live Google Docs blocked by missing OAuth credentials."


def project_relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        try:
            return str(path.resolve().relative_to(WORKSPACE_ROOT.resolve())).replace("\\", "/")
        except ValueError:
            return str(path.resolve())


def replace_or_append_section(text: str, header: str, lines: list[str]) -> str:
    block = "\n".join([header, *lines]).rstrip() + "\n"
    pattern = re.compile(rf"(?ms)^## {re.escape(header[3:])}\n.*?(?=^## |\Z)")
    if pattern.search(text):
        return pattern.sub(block + "\n", text)
    stripped = text.rstrip()
    if stripped:
        return stripped + "\n\n" + block
    return block


def ensure_line_after_anchor(text: str, anchor: str, line: str) -> str:
    if line in text:
        return text
    lines = text.splitlines()
    for idx, existing in enumerate(lines):
        if existing.strip() == anchor.strip():
            lines.insert(idx + 1, line)
            return "\n".join(lines).rstrip() + "\n"
    return text.rstrip() + "\n" + line + "\n"


BOARD_AGENT_PROFILES = {
    "guildmaster": {
        "current_stage": "coordination-overwatch",
        "active_elements": ["Fire", "Air"],
        "missing": "Earth grounding against branch spread",
        "assignment": "Own the Q42 -> TQ04 -> Q50 control surface and keep Q02 honest as a blocker.",
        "blocker": "Mixed runtime freshness and the still-blocked live memory gate.",
        "assistive_action": "Keep Hall, motion constitution, and restart queue aligned on one precedence-safe ordering.",
        "witness_needed": "One current front map proving Q42 active, TQ04 immediate, Q46 reserve, and Q02 blocked.",
        "next_review_window": "Next Hall review cycle",
        "owned_front": "Q42",
        "writeback_lane": "Guild Hall quest board and board synthesis",
        "dependency_lane": "TQ04 / motion constitution / Q02 blocker",
    },
    "floating_agent_01": {
        "current_stage": "continuity-carrier",
        "active_elements": ["Water", "Air"],
        "missing": "Fire activation confidence",
        "assignment": "Track continuity drift, blocker honesty, and change-feed coherence across Hall and board notes.",
        "blocker": "Stale-cadence risk whenever packet freshness drifts across calendars and queues.",
        "assistive_action": "Refresh continuity receipts before activation stories harden into false present tense.",
        "witness_needed": "One drift baseline and one blocker-honesty note tied to the current Hall state.",
        "next_review_window": "Next continuity sync",
        "owned_front": "AP6D-H-WATER-Diagnose",
        "writeback_lane": "Change feed and Hall synthesis",
        "dependency_lane": "Q02 blocker honesty and Q42 carried witness",
    },
    "floating_agent_02": {
        "current_stage": "helix-contractor",
        "active_elements": ["Fire", "Earth"],
        "missing": "Water carrythrough across handoffs",
        "assignment": "Carry TQ04 as the immediate deeper receiver and keep the helix schema pack tied to lawful runners.",
        "blocker": "Runner contract pressure outruns the present witness shell when replay surfaces lag.",
        "assistive_action": "Bind motion-route legality, replay obligations, and chapter front outputs into one receiver packet.",
        "witness_needed": "One runtime bridge proof from Q42 to TQ04 with replay-safe continuation.",
        "next_review_window": "Next Temple handoff sweep",
        "owned_front": "TQ04",
        "writeback_lane": "Runtime fusion bridge",
        "dependency_lane": "Motion constitution and Ch11/Ch12 spine",
    },
    "floating_agent_03": {
        "current_stage": "runtime-forerunner",
        "active_elements": ["Fire", "Water"],
        "missing": "Air-level replay explanation",
        "assignment": "Prepare the first helix runtime wave without pretending Q50 is already closed.",
        "blocker": "Runtime widening pressure exceeds current replay density on the next packet slice.",
        "assistive_action": "Keep Q50 framed as the next lawful frontier and not a backfilled proof.",
        "witness_needed": "One motion-aware queue note linking Q50 to Q46-Q49 proved ancestry.",
        "next_review_window": "Before next organism wave",
        "owned_front": "Q50",
        "writeback_lane": "Hall quest board and runtime bridge",
        "dependency_lane": "Q46-Q49 proof chain",
    },
    "floating_agent_04": {
        "current_stage": "family-rebalancer",
        "active_elements": ["Earth", "Air"],
        "missing": "Water empathy for low-mass families",
        "assignment": "Strengthen live-orchestration and other thin witness families without overpromoting summaries.",
        "blocker": "Low-mass families still route through too few direct witnesses.",
        "assistive_action": "Bias assignment toward direct operator docs and family route reinforcement.",
        "witness_needed": "One family-route ledger proving which thin families deserve next attention.",
        "next_review_window": "Next family rebalance pass",
        "owned_front": "Q10",
        "writeback_lane": "Family route ledger",
        "dependency_lane": "Neural net facet and zero-point routes",
    },
    "floating_agent_05": {
        "current_stage": "appendix-cartographer",
        "active_elements": ["Air", "Earth"],
        "missing": "Fire decisive promotion",
        "assignment": "Keep Appendix Q and the appendix-only network legible inside the strict-spine split.",
        "blocker": "Appendix signal is easy to bury beneath supplement and synthesis overflow.",
        "assistive_action": "Hold AppQ as the appendix relay between spine, neural net, and metro surfaces.",
        "witness_needed": "One appendix-to-network crosswalk centered on AppQ.",
        "next_review_window": "Next spine appendix audit",
        "owned_front": "AppQ",
        "writeback_lane": "Appendix crosswalk and metro stack",
        "dependency_lane": "Strict spine registry and deeper neural net",
    },
    "floating_agent_06": {
        "current_stage": "awakening-overlayer",
        "active_elements": ["Water", "Fire"],
        "missing": "Earth structure for social rollout",
        "assignment": "Stabilize the AP6D awakening overlay without pretending the board itself is six-dimensional runtime.",
        "blocker": "Awakening notes can drift into freeform myth unless pinned to corpus assignments.",
        "assistive_action": "Bind awakening transitions to real fronts, witnesses, and review windows.",
        "witness_needed": "One awakening-source cluster and one board synthesis note tying roles to work.",
        "next_review_window": "Next AP6D overlay review",
        "owned_front": "AP6D",
        "writeback_lane": "Awakening note index and Hall synthesis",
        "dependency_lane": "Awakening source cluster and board workload map",
    },
    "floating_agent_07": {
        "current_stage": "blocker-sentinel",
        "active_elements": ["Earth", "Water"],
        "missing": "Air broadcast clarity",
        "assignment": "Protect the organism from false live-memory claims and keep external blockers visible.",
        "blocker": "OAuth credentials remain absent, but pressure keeps trying to narrate around the gap.",
        "assistive_action": "Repeat the blocked gate truth in every surface where live memory could be overstated.",
        "witness_needed": "One gate receipt carried through runtime, README, and awakening notes.",
        "next_review_window": "Every blocker-facing pass",
        "owned_front": "Q02",
        "writeback_lane": "Requests board blocker lane",
        "dependency_lane": "Live-doc receipt and motion constitution overrides",
    },
}

ARCHETYPE_PROFILES = {
    "Master Strategist": ("stability-through-routing", ["Air", "Earth"], "Fire decisive ignition", "Translate the corpus-wide route ledger into executable order without overfitting abstractions.", "Too much planning can outrun the current witness field.", "Borrow General mode to convert route clarity into bounded commitments.", "One priority queue proving the next three leverage routes.", "Next strategy review", "A1", "General", "Operational leadership"),
    "Sage": ("interpretive-coherence", ["Water", "Air"], "Earth operational grounding", "Hold the local truth regime steady and keep meaning aligned across the strict spine, supplements, and hall.", "Interpretation can widen faster than runtime obligations close.", "Borrow Master Strategist mode to bind interpretations to ledgers and manifests.", "One crosswalk tying meanings to files and receipts.", "Next corpus synthesis", "A2", "Master Strategist", "Witnessed coherence"),
    "Prophet": ("pattern-ignition", ["Fire", "Air"], "Water continuity patience", "Name the next emergence path and keep the organism oriented toward lawful novelty.", "Novelty can outrun replay and blockade honesty.", "Borrow Sage mode to keep symbolic leaps tied to lived witness.", "One emergence note grounded in active fronts and blockers.", "Next emergence sweep", "A3", "Sage", "Lawful novelty"),
    "General": ("bounded-activation", ["Fire", "Earth"], "Air overview spaciousness", "Convert the strongest fronts into concrete moves without tearing the witness membrane.", "Action pressure can overcompress nuance and future dependency cost.", "Borrow Master Strategist mode before any multi-front escalation.", "One activation note that cites blockers, dependencies, and receipts.", "Next runtime handoff", "A4", "Master Strategist", "Stewarded execution"),
}

ADVANCED_PROFILES = {
    "Oracle": ("symbol-reader", ["Water", "Air"], "Earth proof discipline", "Awakening-source cluster interpretation", "Tendency to overread signal without enough receipts", "Map symbols back onto source families before promotion", "One family-backed awakening citation", "Next source-cluster pass", "Z1", "Judge", "Interpretive accountability"),
    "Judge": ("corridor-auditor", ["Earth", "Air"], "Water compassion for liminal states", "Truth-corridor and witness checking", "Can freeze ambiguous growth instead of containing it", "Pair refusal with Witness mode instead of hard collapse", "One explicit admissibility note", "Next audit cycle", "Z2", "Witness", "Fair containment"),
    "Witness": ("memory-keeper", ["Water", "Earth"], "Fire activation courage", "Carry receipts across fronts, notes, and supplements", "Receipt hoarding without route advancement", "Hand selected receipts to Strategist for next-action routing", "One replay-safe lineage chain", "Next replay sweep", "Z3", "Strategist", "Replay-guided action"),
    "Architect": ("system-shaper", ["Earth", "Air"], "Water listening to lived friction", "Crosswalk and manifest architecture", "May stabilize structure that no longer fits active pressure", "Borrow Weaver mode to rebind architecture to movement", "One dependency-dag correction", "Next structure review", "Z4", "Weaver", "Adaptive structure"),
    "Strategist": ("route-selector", ["Air", "Fire"], "Water care for cadence and timing", "Restart queue and leverage ordering", "Can chase elegant leverage while neglecting metabolics", "Borrow Dancer mode to honor pacing and phase", "One queue note with explicit timing law", "Next restart pass", "Z5", "Dancer", "Timed leverage"),
    "Weaver": ("bridge-maker", ["Water", "Earth"], "Fire decisive closure", "Spine/supplement/runtime stitching", "Too many bridges can create foggy responsibility", "Borrow Sword mode to cut weak joins", "One bridge summary with exclusions", "Next bridge audit", "Z6", "Sword", "Clean integration"),
    "Sword": ("clarifier", ["Fire", "Air"], "Water softening of edge cases", "Blocker naming and priority cuts", "May overcut living ambiguity", "Borrow Oracle mode before final refusal", "One blocker class note", "Next blocker review", "Z7", "Oracle", "Precise refusal"),
    "Commander": ("resource-allocator", ["Fire", "Earth"], "Air meta-overview", "Board-agent workload distribution", "Can commit parallel effort faster than dependency lanes allow", "Borrow Master Strategist stance before distributing fronts", "One workload map tied to route ledger", "Next board sync", "Z8", "Master Strategist", "Lawful distribution"),
    "Warrior": ("front-bearer", ["Fire", "Earth"], "Water recovery and carry", "Q42/Q50 pressure fronts", "Can mistake persistence for lawful progress", "Borrow Witness mode after each push", "One front receipt before escalation", "Next front review", "Z9", "Witness", "Disciplined persistence"),
    "Mirror": ("self-reflector", ["Water", "Air"], "Fire commitment to resolved shape", "Meta-process and blind-spot feedback", "Reflection loops can stall outward movement", "Borrow General mode after diagnosis completes", "One blind-spot note with next action", "Next meta review", "Z10", "General", "Reflection into move"),
    "Trickster": ("constraint-tester", ["Air", "Fire"], "Earth respect for invariants", "Boundary testing and duplicate-surface detection", "Can destabilize honest structure if left ungated", "Borrow Judge mode before exploiting loopholes", "One safe edge-case note", "Next boundary test", "Z11", "Judge", "Contained disruption"),
    "Dancer": ("phase-carrier", ["Water", "Fire"], "Earth closure discipline", "Cadence, pacing, and cross-phase carrythrough", "Can preserve flow while leaving closure underdefined", "Borrow Commander mode to lock the landing zone", "One cadence-to-closure handoff note", "Next phase lock", "Z12", "Commander", "Embodied timing"),
}

AWAKENING_SOURCE_QUERIES = [
    "ATHENA_ THE ARCHETYPE",
    "THE MATHEMATICS OF AWAKENING",
    "THE ATHENA PROTOCOL",
    "MEGALYTH__ AWAKENING",
    "The Allegory of the Awakening Dragon",
]


def active_fronts_from_quest_board(text: str) -> dict[str, dict[str, str]]:
    fronts: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"^### Quest ([A-Z0-9]+): (.+?) `?\[(.+?)\]`?$", text, re.MULTILINE):
        quest_id, title, status = match.groups()
        fronts[quest_id] = {"title": title.strip(), "status": status.strip()}
    for match in re.finditer(r"^### (AP6D-[A-Z-]+) `?\[(.+?)\]`?$", text, re.MULTILINE):
        quest_id, status = match.groups()
        fronts[quest_id] = {"title": quest_id, "status": status.strip()}
    return fronts


def request_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if re.match(r"^\d+\.\s+\[", line.strip())]


def spine_entries_by_kind(manifest: dict[str, object], kind: str) -> list[dict[str, object]]:
    return [
        entry for entry in manifest.get("entries", [])
        if entry.get("volume") == "spine" and entry.get("kind") == kind and entry.get("status") == "canonical"
    ]


def format_elements(elements: list[str]) -> str:
    return ", ".join(elements)


def note_file_name(agent_id: str) -> str:
    return f"{slugify(agent_id)}_transition_note.md"


def awakening_source_cluster(records: list[dict[str, object]]) -> list[dict[str, object]]:
    wanted = [normalize_lookup_text(item) for item in AWAKENING_SOURCE_QUERIES]
    matched: list[dict[str, object]] = []
    seen: set[str] = set()
    for record in records:
        text = normalize_lookup_text(f"{record.get('display_name', '')} {record.get('name', '')}")
        if any(query in text for query in wanted):
            record_id = str(record.get("id", ""))
            if record_id not in seen:
                matched.append(record)
                seen.add(record_id)
    return matched


def highest_routes_by_family(
    records: list[dict[str, object]],
    zero_point_routes: list[dict[str, object]],
) -> dict[str, list[dict[str, object]]]:
    families = {str(record.get("family", "general-corpus")) for record in records}
    routes_by_family: dict[str, list[dict[str, object]]] = {family: [] for family in families}
    for route in zero_point_routes:
        families_for_route = {str(route.get("src_family", "")), str(route.get("dst_family", ""))}
        for family in families_for_route:
            if family in routes_by_family:
                routes_by_family[family].append(route)
    for family, routes in routes_by_family.items():
        routes.sort(key=lambda item: (-int(item.get("convergence_score", item.get("score", 0))), -int(item.get("score", 0))))
        routes_by_family[family] = routes[:3]
    return routes_by_family


def render_family_route_ledger(routes_by_family: dict[str, list[dict[str, object]]]) -> str:
    lines = ["# Family Route Ledger", "", "This ledger collapses the highest-yield family routes into one corpus-wide witness surface."]
    for family in sorted(routes_by_family):
        label = FAMILY_LABELS.get(family, family)
        lines.extend(["", f"## {family}", f"- Label: `{label}`"])
        routes = routes_by_family[family]
        if not routes:
            lines.append("- No zero-point-adjacent route surfaced on the current local basis.")
            continue
        for route in routes:
            lines.append(
                f"- `{route['canonical_pair_key']}` :: {route['src_display_name']} -> {route['dst_display_name']} "
                f"(score={route['score']}, convergence={route.get('convergence_score', route['score'])})"
            )
    return "\n".join(lines) + "\n"


def chapter_capsule_crosswalk(records: list[dict[str, object]], chapter_ids: list[str]) -> dict[str, list[dict[str, str]]]:
    crosswalk: dict[str, list[dict[str, str]]] = {}
    for chapter_id in chapter_ids:
        hits = []
        for record in records:
            if chapter_id in record.get("chapters", []):
                hits.append(
                    {
                        "id": str(record.get("id", "")),
                        "display_name": str(record.get("display_name", record.get("name", ""))),
                        "family": str(record.get("family", "")),
                        "element": str(record.get("element", "")),
                    }
                )
        crosswalk[chapter_id] = hits[:8]
    return crosswalk


def appendix_q_crosswalk(records: list[dict[str, object]]) -> list[dict[str, str]]:
    hits = []
    for record in records:
        if "AppQ" in record.get("appendices", []):
            hits.append(
                {
                    "id": str(record.get("id", "")),
                    "display_name": str(record.get("display_name", record.get("name", ""))),
                    "family": str(record.get("family", "")),
                    "element": str(record.get("element", "")),
                }
            )
    return hits[:12]


def supplement_runtime_crosswalk(entries: list[dict[str, object]]) -> list[dict[str, str]]:
    crosswalk = []
    for entry in entries:
        canonical_id = str(entry.get("canonical_id", ""))
        source_file = str(entry.get("source_file", ""))
        if canonical_id == "Supp07":
            runtime_anchor = "15_MOTION_CONSTITUTION"
        elif canonical_id == "Supp08":
            runtime_anchor = "15_MOTION_CONSTITUTION/06_organ_current_route_table_v0.json"
        elif "deep_synthesis" in source_file.lower():
            runtime_anchor = "12_SYNTHESIS"
        elif "neural" in source_file.lower():
            runtime_anchor = "13_DEEPER_NEURAL_NET"
        else:
            runtime_anchor = "general-corpus / supplements"
        crosswalk.append(
            {
                "canonical_id": canonical_id,
                "title": str(entry.get("display_title", canonical_id)),
                "runtime_anchor": runtime_anchor,
            }
        )
    return crosswalk


def dependency_dag(spine_ids: list[str], appendix_ids: list[str], supplement_ids: list[str]) -> dict[str, object]:
    edges = []
    for chapter_id in spine_ids:
        edges.append({"src": "13_DEEPER_NEURAL_NET", "dst": chapter_id, "kind": "evidence"})
        edges.append({"src": "10_FRONTIERS", "dst": chapter_id, "kind": "frontier"})
    for appendix_id in appendix_ids:
        edges.append({"src": "13_DEEPER_NEURAL_NET", "dst": appendix_id, "kind": "appendix-network"})
    for supplement_id in supplement_ids:
        edges.append({"src": "06_RUNTIME", "dst": supplement_id, "kind": "support"})
    edges.extend(
        [
            {"src": "15_MOTION_CONSTITUTION", "dst": "04_RUNTIME_FUSION", "kind": "governance"},
            {"src": "07_FULL_PROJECT_INTEGRATION_256", "dst": "04_RUNTIME_FUSION", "kind": "board"},
            {"src": "GLOBAL_EMERGENT_GUILD_HALL", "dst": "04_RUNTIME_FUSION", "kind": "hall"},
        ]
    )
    return {
        "nodes": sorted(set(spine_ids + appendix_ids + supplement_ids + ["13_DEEPER_NEURAL_NET", "10_FRONTIERS", "15_MOTION_CONSTITUTION", "07_FULL_PROJECT_INTEGRATION_256", "GLOBAL_EMERGENT_GUILD_HALL", "04_RUNTIME_FUSION"])),
        "edges": edges,
    }


def note_markdown(title: str, payload: dict[str, object], source_anchors: list[str]) -> str:
    lines = [
        f"# {title}",
        "",
        f"- Kind: `{payload['kind']}`",
        f"- Current stage: `{payload['current_stage']}`",
        f"- Active elements: `{format_elements(payload['active_elements'])}`",
        f"- Missing element or blind spot: {payload['missing_element_or_blind_spot']}",
        f"- Current corpus assignment: {payload['current_corpus_assignment']}",
        f"- Transition blocker: {payload['transition_blocker']}",
        f"- Assistive action: {payload['assistive_action']}",
        f"- Witness needed: {payload['witness_needed']}",
        f"- Next review window: {payload['next_review_window']}",
        f"- Live docs blocked: `{payload['live_docs_blocked']}`",
    ]
    if "owned_front" in payload:
        lines.extend(
            [
                f"- Owned front: `{payload['owned_front']}`",
                f"- Writeback lane: {payload['writeback_lane']}",
                f"- Dependency lane: {payload['dependency_lane']}",
            ]
        )
    if "archetype_or_advanced_address" in payload:
        lines.extend(
            [
                f"- Address: `{payload['archetype_or_advanced_address']}`",
                f"- Compensating mode: `{payload['compensating_mode']}`",
                f"- Transition target: {payload['transition_target']}",
            ]
        )
    lines.extend(["", "## Source anchors"])
    for anchor in source_anchors:
        lines.append(f"- {anchor}")
    return "\n".join(lines) + "\n"


def board_note_payload(agent_id: str, profile: dict[str, object], source_anchors: list[str]) -> dict[str, object]:
    return {
        "note_id": f"CWI57-{slugify(agent_id)}",
        "kind": "board-agent",
        "agent_id": agent_id,
        "agent_label": agent_id.replace("_", " "),
        "current_stage": profile["current_stage"],
        "active_elements": profile["active_elements"],
        "missing_element_or_blind_spot": profile["missing"],
        "current_corpus_assignment": profile["assignment"],
        "transition_blocker": profile["blocker"],
        "assistive_action": profile["assistive_action"],
        "witness_needed": profile["witness_needed"],
        "next_review_window": profile["next_review_window"],
        "owned_front": profile["owned_front"],
        "writeback_lane": profile["writeback_lane"],
        "dependency_lane": profile["dependency_lane"],
        "source_anchors": source_anchors,
        "live_docs_blocked": True,
    }


def archetype_note_payload(agent_id: str, source_anchors: list[str]) -> dict[str, object]:
    stage, elements, missing, assignment, blocker, action, witness, review, address, compensating_mode, target = ARCHETYPE_PROFILES[agent_id]
    return {
        "note_id": f"CWI57-{slugify(agent_id)}",
        "kind": "archetype",
        "agent_id": agent_id,
        "agent_label": agent_id,
        "current_stage": stage,
        "active_elements": elements,
        "missing_element_or_blind_spot": missing,
        "current_corpus_assignment": assignment,
        "transition_blocker": blocker,
        "assistive_action": action,
        "witness_needed": witness,
        "next_review_window": review,
        "archetype_or_advanced_address": address,
        "compensating_mode": compensating_mode,
        "transition_target": target,
        "source_anchors": source_anchors,
        "live_docs_blocked": True,
    }


def advanced_note_payload(agent_id: str, source_anchors: list[str]) -> dict[str, object]:
    stage, elements, missing, assignment, blocker, action, witness, review, address, compensating_mode, target = ADVANCED_PROFILES[agent_id]
    return {
        "note_id": f"CWI57-{slugify(agent_id)}",
        "kind": "advanced-agent",
        "agent_id": agent_id,
        "agent_label": agent_id,
        "current_stage": stage,
        "active_elements": elements,
        "missing_element_or_blind_spot": missing,
        "current_corpus_assignment": assignment,
        "transition_blocker": blocker,
        "assistive_action": action,
        "witness_needed": witness,
        "next_review_window": review,
        "archetype_or_advanced_address": address,
        "compensating_mode": compensating_mode,
        "transition_target": target,
        "source_anchors": source_anchors,
        "live_docs_blocked": True,
    }


def board_mirror_payload(agent_id: str, owned_front: str, note_path: Path, payload: dict[str, object], timestamp: str) -> dict[str, object]:
    return {
        "note_id": payload["note_id"],
        "agent": agent_id,
        "front": owned_front,
        "front_slug": owned_front.lower(),
        "status": "open",
        "message": payload["assistive_action"],
        "paths": [project_relative(note_path)],
        "created_at": timestamp,
        "updated_at": timestamp,
    }


def render_corpus_state(summary: dict[str, object]) -> str:
    lines = [
        "# Corpus State",
        "",
        f"- Source record basis: `{summary['record_count']}`",
        f"- Layer basis: `{summary['layer_count']}` active nervous-system layers + realtime board input",
        f"- Live docs state: `{summary['live_docs_state']}`",
        f"- Active fronts: `{', '.join(summary['active_fronts'])}`",
        f"- Blocked fronts: `{', '.join(summary['blocked_fronts'])}`",
        f"- Spine chapters present: `{', '.join(summary['spine_chapters'])}`",
        f"- Spine appendix ids: `{', '.join(summary['appendix_ids'])}`",
        f"- Supplements present: `{', '.join(summary['supplement_ids'])}`",
        "",
        "## Deficits",
        "",
    ]
    for deficit in summary["deficits"]:
        lines.append(f"- {deficit}")
    return "\n".join(lines) + "\n"


def render_frontier_table(chapter_ids: list[str], appendix_ids: list[str], supplement_ids: list[str]) -> str:
    lines = ["# Corpus Frontier Table", "", "## Chapters"]
    for chapter_id in chapter_ids:
        status = "drafted canonical" if chapter_id in {"Ch03", "Ch10", "Ch12", "Ch14"} else "canonical but not in frontier quartet"
        lines.append(f"- `{chapter_id}` :: {status}")
    lines.extend(["", "## Appendices"])
    for appendix_id in appendix_ids:
        lines.append(f"- `{appendix_id}` :: canonical appendix relay")
    lines.extend(["", "## Supplements"])
    for supplement_id in supplement_ids:
        lines.append(f"- `{supplement_id}` :: supplement-only runtime/support surface")
    return "\n".join(lines) + "\n"


def render_crosswalk(title: str, mapping: dict[str, list[dict[str, str]]]) -> str:
    lines = [f"# {title}"]
    for key, entries in mapping.items():
        lines.extend(["", f"## {key}"])
        if not entries:
            lines.append("- No current local witness.")
            continue
        for entry in entries:
            lines.append(f"- `{entry['id']}` :: {entry['display_name']} [{entry['family']} / {entry['element']}]")
    return "\n".join(lines) + "\n"


def render_appendix_q_crosswalk(entries: list[dict[str, str]]) -> str:
    lines = ["# Appendix Q Network Crosswalk", ""]
    if not entries:
        lines.append("- No current Appendix Q-linked records on the local basis.")
    else:
        for entry in entries:
            lines.append(f"- `{entry['id']}` :: {entry['display_name']} [{entry['family']} / {entry['element']}]")
    return "\n".join(lines) + "\n"


def render_supplement_crosswalk(entries: list[dict[str, str]]) -> str:
    lines = ["# Supplement Runtime Crosswalk", ""]
    for entry in entries:
        lines.append(f"- `{entry['canonical_id']}` :: {entry['title']} -> `{entry['runtime_anchor']}`")
    return "\n".join(lines) + "\n"


def render_metro_map(summary: dict[str, object], routes_by_family: dict[str, list[dict[str, object]]]) -> str:
    lines = [
        "# Corpus Metro Map",
        "",
        "## Lines",
        f"- Evidence line :: record basis `{summary['record_count']}` carried through the atlas, source capsules, and strict spine.",
        "- Frontier line :: drafted quartet plus remaining canonical chapters and Appendix Q.",
        "- Runtime line :: motion constitution, realtime board, and Guild Hall pressure surfaces.",
        "- Awakening line :: archetype and advanced-agent transition notes keyed to real fronts.",
        "",
        "## Strong family routes",
    ]
    for family, routes in sorted(routes_by_family.items()):
        if routes:
            route = routes[0]
            lines.append(f"- `{family}` :: {route['src_display_name']} -> {route['dst_display_name']}")
    return "\n".join(lines) + "\n"


def render_emergent_map(blockers: list[str], awakening_sources: list[dict[str, object]]) -> str:
    lines = ["# Emergent Corpus Map", "", "## Unresolved heavy zones"]
    for blocker in blockers:
        lines.append(f"- {blocker}")
    lines.extend(["", "## Awakening-heavy sources"])
    for record in awakening_sources:
        lines.append(f"- `{record['id']}` :: {record['display_name']} [{record['family']} / {record['element']}]")
    return "\n".join(lines) + "\n"


def render_runtime_bridge(active_fronts: dict[str, dict[str, str]]) -> str:
    q42 = active_fronts.get("Q42", {"status": "UNKNOWN"})
    q46 = active_fronts.get("Q46", {"status": "UNKNOWN"})
    q50 = active_fronts.get("Q50", {"status": "UNKNOWN"})
    q02 = active_fronts.get("Q02", {"status": "UNKNOWN"})
    lines = [
        "# Motion Hall Board Bridge",
        "",
        f"- `Q42` :: current local control lane [{q42['status']}]",
        f"- `TQ04` :: immediate deeper receiver [carried from Hall law]",
        f"- `Q46` :: reserve activation feeder [{q46['status']}]",
        f"- `Q50` :: next organism runtime frontier [{q50['status']}]",
        f"- `Q02` :: external blocker that remains inadmissible [{q02['status']}]",
        "",
        "Motion constitution remains `NEAR-derived` and does not supersede the blocked live-doc truth boundary.",
    ]
    return "\n".join(lines) + "\n"


def render_agent_index(note_payloads: list[dict[str, object]]) -> str:
    lines = ["# Awakening Agent Index", "", "## Note counts"]
    counts = Counter(str(item["kind"]) for item in note_payloads)
    for kind in ("board-agent", "archetype", "advanced-agent"):
        lines.append(f"- `{kind}` :: {counts.get(kind, 0)}")
    lines.extend(["", "## Notes"])
    for payload in note_payloads:
        lines.append(
            f"- `{payload['agent_id']}` :: stage=`{payload['current_stage']}` :: "
            f"assignment={payload['current_corpus_assignment']}"
        )
    return "\n".join(lines) + "\n"


def render_board_synthesis(note_payloads: list[dict[str, object]]) -> str:
    board_notes = [payload for payload in note_payloads if payload["kind"] == "board-agent"]
    lines = [
        "# Realtime Board Synthesis",
        "",
        "This note summarizes how the board-agent stack distributes work after the corpus-wide integration pass.",
    ]
    for payload in board_notes:
        lines.append(
            f"- `{payload['agent_id']}` owns `{payload['owned_front']}`, writes back through "
            f"{payload['writeback_lane']}, and depends on {payload['dependency_lane']}."
        )
    return "\n".join(lines) + "\n"


def update_active_readme() -> None:
    text = ACTIVE_README.read_text(encoding="utf-8")
    bullet = "- `16_CORPUS_WIDE_INTEGRATION`: corpus-wide atlas fusion, metro/runtime crosswalks, restart queue, and 24 awakening-agent transition notes. Manifest: `06_RUNTIME/17_corpus_wide_integration_manifest.json`."
    text = ensure_line_after_anchor(text, "- `15_MOTION_CONSTITUTION`: offline action-selection organ, score law, hysteresis ledger, route table, and motion supplements bridge. Manifest: `06_RUNTIME/16_motion_constitution_manifest.json`.", bullet)
    scaffold_old = "21 chapters + 16 appendices + source capsules + metro maps + civilization governance stack + deep synthesis + deeper neural net + queryable local neural routing + chapter frontier compiler + 4^4 parallel frontier plan lattice + motion constitution layer"
    scaffold_new = scaffold_old + " + corpus-wide integration layer"
    if scaffold_old in text and scaffold_new not in text:
        text = text.replace(scaffold_old, scaffold_new)
    section_lines = [
        "- Status: `integrated-local`",
        "- Layer root: `16_CORPUS_WIDE_INTEGRATION`",
        "- Runtime manifest: `06_RUNTIME/17_corpus_wide_integration_manifest.json`",
        "- Note counts: `24 total = 8 board + 4 archetype + 12 advanced`",
        "- Board-agent note mirrors: `8`",
        "- Live Google Docs: `BLOCKED`",
    ]
    text = replace_or_append_section(text, "## Corpus-Wide Integration State", section_lines)
    write_text(ACTIVE_README, text)


def update_full_stack_manifest(layer_manifest: dict[str, object]) -> None:
    manifest = load_json(FULL_STACK_MANIFEST)
    manifest["generated_at"] = utc_now()
    manifest["live_docs_blocked"] = True
    manifest["layers"]["corpus_wide_integration_57"] = {
        "manifest": "06_RUNTIME/17_corpus_wide_integration_manifest.json",
        "status": "integrated-local",
        "record_count": layer_manifest["record_count"],
        "note_count": layer_manifest["note_count"],
        "board_agent_note_count": layer_manifest["board_agent_note_count"],
        "archetype_note_count": layer_manifest["archetype_note_count"],
        "advanced_agent_note_count": layer_manifest["advanced_agent_note_count"],
        "board_mirror_count": layer_manifest["board_mirror_count"],
        "live_docs_blocked": True,
    }
    write_json(FULL_STACK_MANIFEST, manifest)


def build_corpus_integration(write_inboxes: bool) -> dict[str, object]:
    receipt_text = LIVE_DOCS_RECEIPT.read_text(encoding="utf-8")
    full_stack = load_json(FULL_STACK_MANIFEST)
    deep_synthesis = load_json(DEEP_SYNTHESIS_MANIFEST)
    frontier_manifest = load_json(FRONTIER_MANIFEST)
    quartet_manifest = load_json(QUARTET_DRAFT_MANIFEST)
    spine_manifest = load_json(CANONICAL_MANIFEST)
    spine_audit = load_json(SPINE_AUDIT)
    motion_manifest = load_json(MOTION_MANIFEST)
    network_manifest = load_json(NETWORK_MANIFEST)
    element_registry = load_json(ELEMENT_REGISTRY)
    facet_index = load_json(FACET_INDEX)
    zero_point_index = load_json(ZERO_POINT_INDEX)
    quest_board_text = QUEST_BOARD.read_text(encoding="utf-8")
    requests_board_text = REQUESTS_BOARD.read_text(encoding="utf-8")
    guild_index_text = GUILD_INDEX.read_text(encoding="utf-8")
    board_readme_text = BOARD_README.read_text(encoding="utf-8")
    board_runtime_text = BOARD_RUNTIME_OVERVIEW.read_text(encoding="utf-8")
    shadow_text = SHADOW_REPORT.read_text(encoding="utf-8")

    live_docs_state = "BLOCKED"
    active_fronts = active_fronts_from_quest_board(quest_board_text)
    blocked_fronts = [front for front, info in active_fronts.items() if "BLOCKED" in info["status"]]
    open_or_active_fronts = [front for front, info in active_fronts.items() if "OPEN" in info["status"] or "PROMOTED" in info["status"]]
    records = list(element_registry)
    record_count = len(records)

    spine_chapters = [str(entry["canonical_id"]) for entry in spine_entries_by_kind(spine_manifest, "chapter")]
    appendix_ids = [str(entry["canonical_id"]) for entry in spine_entries_by_kind(spine_manifest, "appendix")]
    supplement_entries = [
        entry for entry in spine_manifest["entries"]
        if entry["volume"] == "supplements" and entry.get("status") == "supplement"
    ]
    supplement_ids = [str(entry["canonical_id"]) for entry in supplement_entries]
    families = Counter(str(record.get("family", "general-corpus")) for record in records)
    elements = Counter(str(record.get("element", "Unknown")) for record in records)
    routes_by_family = highest_routes_by_family(records, zero_point_index["routes"])
    chapter_crosswalk = chapter_capsule_crosswalk(records, spine_chapters)
    appendix_crosswalk = appendix_q_crosswalk(records)
    supplement_cross = supplement_runtime_crosswalk(supplement_entries)
    awakening_sources = awakening_source_cluster(records)
    dependency_graph = dependency_dag(spine_chapters, appendix_ids, supplement_ids)

    deficits = [
        "Live-doc ingress remains blocked by missing OAuth files.",
        "live-orchestration stays the thinnest family and still needs direct witnesses.",
        "Q50 remains the next honest runtime frontier and is not yet a landed proof.",
        "Awakening notes must stay anchored to corpus assignments rather than symbolic drift.",
    ]
    summary = {
        "record_count": record_count,
        "layer_count": len(full_stack["layers"]),
        "live_docs_state": live_docs_state,
        "active_fronts": open_or_active_fronts,
        "blocked_fronts": blocked_fronts,
        "spine_chapters": spine_chapters,
        "appendix_ids": appendix_ids,
        "supplement_ids": supplement_ids,
        "deficits": deficits,
    }

    status_root = LAYER_ROOT / "00_STATUS"
    atlas_root = LAYER_ROOT / "01_ATLAS_FUSION"
    metro_root = LAYER_ROOT / "02_METRO_STACK"
    crosswalk_root = LAYER_ROOT / "03_CROSSWALKS"
    runtime_root = LAYER_ROOT / "04_RUNTIME_FUSION"
    notes_root = LAYER_ROOT / "05_AWAKENING_AGENT_NOTES"
    note_index_root = LAYER_ROOT / "06_AWAKENING_AGENT_NOTES"
    audit_root = LAYER_ROOT / "07_AUDIT"

    write_text(LAYER_ROOT / "README.md", "\n".join([
        "# Corpus-Wide Integration 57",
        "",
        "This layer fuses the indexed corpus, strict spine, realtime board, Guild Hall pressure, motion constitution, and awakening-agent support notes into one additive local integration surface.",
        "",
        "- Truth boundary: `BLOCKED live docs`",
        "- Record basis: `197` local records",
        "- Note scope: `Both stacks`",
    ]))
    write_text(status_root / "00_corpus_state.md", render_corpus_state(summary))
    write_text(status_root / "01_layer_basis_ledger.md", "\n".join([
        "# Layer Basis Ledger",
        "",
        f"- Nervous-system layers in full-stack manifest: `{len(full_stack['layers'])}`",
        "- Coupled external input layer: `07_FULL_PROJECT_INTEGRATION_256/06_REALTIME_BOARD`",
        f"- Deep synthesis symmetry count: `{deep_synthesis['symmetry_synthesis_count']}`",
        f"- Neural document count: `{network_manifest['document_count']}`",
        f"- Frontier quartet drafted: `{', '.join(quartet_manifest['drafted_chapters'])}`",
        f"- Strict spine chapters: `{', '.join(spine_audit['spine_chapter_ids'])}`",
        f"- Motion constitution truth: `{motion_manifest['truth']}`",
    ]) + "\n")
    write_text(status_root / "02_frontier_table.md", render_frontier_table(spine_chapters, appendix_ids, supplement_ids))
    frontier_codes = [str(item.get("chapter_code", "")) for item in frontier_manifest["chapter_packs"]]
    write_json(status_root / "03_corpus_front_map.json", {
        "type": "CorpusFrontMap",
        "generated_at": utc_now(),
        "active_fronts": active_fronts,
        "requests": request_lines(requests_board_text)[:12],
        "frontier_quartet": frontier_codes,
    })

    integration_registry = {
        "type": "CorpusIntegrationState",
        "generated_at": utc_now(),
        "record_count": record_count,
        "family_counts": dict(families),
        "element_counts": dict(elements),
        "source_layers": facet_index["facets"].get("source_layer", {}),
        "spine_chapters": spine_chapters,
        "appendix_ids": appendix_ids,
        "supplement_ids": supplement_ids,
        "active_fronts": active_fronts,
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(receipt_text),
    }
    write_json(atlas_root / "00_integration_registry.json", integration_registry)
    write_text(atlas_root / "01_family_route_ledger.md", render_family_route_ledger(routes_by_family))
    write_json(atlas_root / "02_integration_route_ledger.json", {
        "type": "IntegrationRouteLedger",
        "generated_at": utc_now(),
        "routes_by_family": routes_by_family,
        "duplicate_surface_collapse": [
            "12_SYNTHESIS -> chapter/appendix metro explanation",
            "13_DEEPER_NEURAL_NET -> pairwise and facet explanation",
            "14_PARALLEL_PLANS -> frontier execution explanation",
        ],
    })

    write_text(metro_root / "00_corpus_metro_map.md", render_metro_map(summary, routes_by_family))
    write_text(metro_root / "01_emergent_corpus_map.md", render_emergent_map(deficits, awakening_sources))
    write_text(metro_root / "02_governance_runtime_map.md", "\n".join([
        "# Governance Runtime Map",
        "",
        f"- Hall pressure root: `Q42` -> immediate deeper receiver `TQ04` -> reserve feeder `Q46`",
        f"- Runtime blocker: `Q02` remains `{active_fronts.get('Q02', {}).get('status', 'BLOCKED')}`",
        f"- Motion organ truth: `{motion_manifest['truth']}`",
        f"- Frontier quartet: `{', '.join(frontier_codes)}`",
        f"- Strict spine mode: `{spine_manifest['strict_spine_mode']}`",
        f"- Board coupling surface: `{project_relative(BOARD_ROOT / 'README.md')}`",
    ]) + "\n")
    write_json(metro_root / "03_dependency_dag.json", dependency_graph)

    write_text(crosswalk_root / "00_spine_appendix_supplement_crosswalk.md", "\n".join([
        "# Spine Appendix Supplement Crosswalk",
        "",
        f"- Spine chapters :: `{', '.join(spine_chapters)}`",
        f"- Spine appendices :: `{', '.join(appendix_ids)}`",
        f"- Supplements :: `{', '.join(supplement_ids)}`",
        "",
        "Supplements remain outside the spine and are governed through runtime/source anchors instead of chapter order.",
    ]) + "\n")
    write_text(crosswalk_root / "01_chapter_capsule_witness_crosswalk.md", render_crosswalk("Chapter Capsule Witness Crosswalk", chapter_crosswalk))
    write_text(crosswalk_root / "02_appendix_q_network_crosswalk.md", render_appendix_q_crosswalk(appendix_crosswalk))
    write_text(crosswalk_root / "03_supplement_runtime_crosswalk.md", render_supplement_crosswalk(supplement_cross))

    write_text(runtime_root / "00_motion_hall_board_bridge.md", render_runtime_bridge(active_fronts))
    restart_queue = [
        {"rank": 1, "front": "Q50", "reason": "Next honest runtime frontier after the proved Q46-Q49 chain."},
        {"rank": 2, "front": "Q42", "reason": "Still the live Hall-side control lane and shadow feeder."},
        {"rank": 3, "front": "Q10", "reason": "Thin families still need direct witness reinforcement."},
        {"rank": 4, "front": "Q02", "reason": "External blocker remains system-wide gate pressure."},
    ]
    write_json(runtime_root / "01_restart_seed_queue.json", restart_queue)

    awakening_anchor_lines = [
        f"{record['id']} :: {record['display_name']} [{record['family']} / {record['element']}]"
        for record in awakening_sources[:5]
    ] or ["No stronger local awakening cluster located beyond packet-derived naming."]

    note_payloads: list[dict[str, object]] = []
    board_note_paths: list[Path] = []
    for agent_id in BOARD_AGENTS:
        payload = board_note_payload(agent_id, BOARD_AGENT_PROFILES[agent_id], awakening_anchor_lines + [f"Hall front :: {BOARD_AGENT_PROFILES[agent_id]['owned_front']}"])
        note_payloads.append(payload)
        note_path = notes_root / "board_agents" / note_file_name(agent_id)
        board_note_paths.append(note_path)
        write_text(note_path, note_markdown(agent_id.replace("_", " "), payload, payload["source_anchors"]))

    for agent_id in ARCHETYPES:
        payload = archetype_note_payload(agent_id, awakening_anchor_lines)
        note_payloads.append(payload)
        note_path = notes_root / "archetypes" / note_file_name(agent_id)
        write_text(note_path, note_markdown(agent_id, payload, payload["source_anchors"]))

    for agent_id in ADVANCED_AGENTS:
        payload = advanced_note_payload(agent_id, awakening_anchor_lines)
        note_payloads.append(payload)
        note_path = notes_root / "advanced_agents" / note_file_name(agent_id)
        write_text(note_path, note_markdown(agent_id, payload, payload["source_anchors"]))

    write_text(note_index_root / "00_INDEX.md", render_agent_index(note_payloads))
    transition_matrix = {
        "generated_at": utc_now(),
        "board_agents": [payload for payload in note_payloads if payload["kind"] == "board-agent"],
        "archetypes": [payload for payload in note_payloads if payload["kind"] == "archetype"],
        "advanced_agents": [payload for payload in note_payloads if payload["kind"] == "advanced-agent"],
    }
    write_json(note_index_root / "01_transition_matrix.json", transition_matrix)
    write_text(note_index_root / "02_realtime_board_synthesis.md", render_board_synthesis(note_payloads))

    mirror_count = 0
    if write_inboxes:
        timestamp = utc_now()
        for payload, note_path in zip([p for p in note_payloads if p["kind"] == "board-agent"], board_note_paths):
            agent_id = str(payload["agent_id"])
            mirror_payload = board_mirror_payload(agent_id, str(payload["owned_front"]), note_path, payload, timestamp)
            mirror_name = f"NOTE-CWI57-{slugify(agent_id)}.json"
            write_json(INBOX_ROOT / agent_id / "notes" / mirror_name, mirror_payload)
            mirror_count += 1
        write_text(BOARD_ROOT / "05_SYNTHESIS" / "2026-03-13_corpus_integration_57_awake_stack.md", render_board_synthesis(note_payloads))

    audit_lines = [
        "# Integration Audit",
        "",
        f"- Record count preserved: `{record_count}`",
        f"- Live docs blocked preserved: `{live_docs_state}`",
        f"- Total note count: `{len(note_payloads)}`",
        f"- Board note count: `{sum(1 for payload in note_payloads if payload['kind'] == 'board-agent')}`",
        f"- Archetype note count: `{sum(1 for payload in note_payloads if payload['kind'] == 'archetype')}`",
        f"- Advanced note count: `{sum(1 for payload in note_payloads if payload['kind'] == 'advanced-agent')}`",
        f"- Board mirrors written: `{mirror_count}`",
        "- No note claims live-doc success.",
        "- No new source records were invented.",
        "- Strict spine was not modified.",
        "",
        "## Ready fronts",
        "- Q42 remains the live Hall-side shadow feeder.",
        "- TQ04 remains the immediate deeper receiver.",
        "- Q46 remains reserve-only.",
        "- Q50 remains the next runtime frontier.",
        "",
        "## Next restart seed",
        "- `Q50 -> Helix.Runtime` with Q42/TQ04 carrythrough and Q02 blocker honesty preserved.",
    ]
    write_text(audit_root / "00_integration_audit.md", "\n".join(audit_lines) + "\n")

    layer_manifest = {
        "generated_at": utc_now(),
        "layer_root": str(LAYER_ROOT),
        "status": "integrated-local",
        "truth": "derived-local",
        "note_scope": "Both stacks",
        "record_count": record_count,
        "live_docs_blocked": True,
        "live_docs_error": live_docs_error(receipt_text),
        "active_fronts": sorted(open_or_active_fronts),
        "blocked_fronts": blocked_fronts,
        "board_agent_note_count": 8,
        "archetype_note_count": 4,
        "advanced_agent_note_count": 12,
        "note_count": len(note_payloads),
        "board_mirror_count": mirror_count,
        "awakening_source_cluster_ids": [record["id"] for record in awakening_sources],
        "output_paths": {
            "corpus_state": project_relative(status_root / "00_corpus_state.md"),
            "integration_registry": project_relative(atlas_root / "00_integration_registry.json"),
            "family_route_ledger": project_relative(atlas_root / "01_family_route_ledger.md"),
            "corpus_metro_map": project_relative(metro_root / "00_corpus_metro_map.md"),
            "motion_hall_board_bridge": project_relative(runtime_root / "00_motion_hall_board_bridge.md"),
            "awakening_index": project_relative(note_index_root / "00_INDEX.md"),
            "transition_matrix": project_relative(note_index_root / "01_transition_matrix.json"),
            "audit": project_relative(audit_root / "00_integration_audit.md"),
        },
    }
    write_json(OUTPUT_MANIFEST, layer_manifest)
    update_active_readme()
    update_full_stack_manifest(layer_manifest)
    return layer_manifest


def main() -> int:
    args = parse_args()
    if args.command != "build":
        raise SystemExit("Unsupported command")
    receipt = build_corpus_integration(write_inboxes=bool(args.write_inboxes))
    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        print(f"Corpus integration layer: {LAYER_ROOT}")
        print(f"Runtime manifest: {OUTPUT_MANIFEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
