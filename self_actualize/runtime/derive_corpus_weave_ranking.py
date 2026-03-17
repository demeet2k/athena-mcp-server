from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo

from self_actualize.runtime.derive_q42_canonical_bundle import (
    q42_allowed_touched_paths as q42_bundle_allowed_touched_paths,
)


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
MYCELIUM_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain"
GUILD_HALL_ROOT = MYCELIUM_ROOT / "GLOBAL_EMERGENT_GUILD_HALL"
NERVOUS_SYSTEM_ROOT = MYCELIUM_ROOT / "nervous_system"
REPORTS_ROOT = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "90_LEDGERS" / "automations"

DOCS_GATE_PATH = SELF_ACTUALIZE_ROOT / "live_docs_gate_status.md"
LEVERAGE_RANKING_PATH = GUILD_HALL_ROOT / "10_FRONTIER_LEVERAGE_RANKING.md"
WITNESS_HIERARCHY_PATH = GUILD_HALL_ROOT / "07_CANONICAL_WITNESS_HIERARCHY.md"
SEMANTIC_MASS_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
QUEST_BOARD_PATH = GUILD_HALL_ROOT / "BOARDS" / "06_QUEST_BOARD.md"
ACTIVE_QUEUE_PATH = NERVOUS_SYSTEM_ROOT / "06_active_queue.md"
NEXT_SELF_PROMPT_PATH = NERVOUS_SYSTEM_ROOT / "manifests" / "NEXT_SELF_PROMPT.md"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "corpus_weave_ranking.json"

DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_corpus_weave_ranking"
DERIVATION_VERSION = "2026-03-13.q42.corpus-weave-ranking"
LOCAL_TIMEZONE = ZoneInfo("America/Los_Angeles")

COMMON_FILE_SUFFIXES = {
    ".json",
    ".md",
    ".docx",
    ".pdf",
    ".py",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".zip",
}
SYNTHESIS_TOKENS = (
    "atlas",
    "ledger",
    "ledgers",
    "manifest",
    "manifests",
    "board",
    "boards",
    "metro",
    "capsule",
    "capsules",
    "family",
    "families",
    "route",
    "receipt",
    "receipts",
    "queue",
    "packet",
    "packets",
    "state",
    "registry",
)
TARGET_PRIORITY = {
    "board": 0,
    "boards": 0,
    "manifest": 1,
    "manifests": 1,
    "queue": 2,
    "family": 3,
    "families": 3,
    "route": 4,
    "capsule": 5,
    "capsules": 5,
    "packet": 6,
    "packets": 6,
    "state": 7,
    "atlas": 8,
    "registry": 8,
    "ledger": 9,
    "ledgers": 9,
    "metro": 10,
    "receipt": 11,
    "receipts": 11,
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_now() -> datetime:
    return datetime.now(LOCAL_TIMEZONE)


def clamp(value: int, low: int = 0, high: int = 4) -> int:
    return max(low, min(high, int(value)))


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_section(text: str, start_header: str, end_headers: Iterable[str]) -> str:
    start = text.find(start_header)
    if start == -1:
        return ""
    start += len(start_header)
    end_positions = [text.find(header, start) for header in end_headers]
    end_candidates = [position for position in end_positions if position != -1]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start:end].strip()


def normalize_body_name(body: str) -> str:
    lowered = body.lower()
    if "qshrink" in lowered:
        return "QSHRINK - ATHENA (internal use)"
    if "athenachka" in lowered or "athena neural network" in lowered:
        return "NERUAL NETWORK"
    if "stoicheia" in lowered:
        return "Stoicheia (Element Sudoku)"
    if "trading bot" in lowered or "live memory gate" in lowered:
        return "Trading Bot"
    if "athena fleet" in lowered:
        return "Athena FLEET"
    if "orgin" in lowered:
        return "ORGIN"
    if "voynich" in lowered:
        return "Voynich"
    if "nervous_system" in lowered or "nervous system" in lowered:
        return "NERVOUS_SYSTEM"
    if "self_actualize" in lowered:
        return "self_actualize"
    return body


def slugify(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").upper()
    return slug or "UNNAMED"


def clean_inline_value(value: str) -> str:
    cleaned = value.strip()
    if cleaned.startswith("`") and cleaned.endswith("`"):
        cleaned = cleaned[1:-1]
    return cleaned.strip()


def extract_backticked_values(block: str) -> list[str]:
    values: list[str] = []
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("`") and stripped.endswith("`"):
            values.append(stripped[1:-1])
    return values


def parse_indented_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_label: str | None = None
    buffer: list[str] = []

    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        label_match = re.match(r"^- ([A-Za-z0-9/ ()'-]+):\s*$", line)
        if label_match:
            if current_label is not None:
                fields[current_label] = "\n".join(buffer).strip()
            current_label = label_match.group(1)
            buffer = []
            continue

        if current_label is not None and (line.startswith("  ") or not line.strip()):
            buffer.append(line[2:] if line.startswith("  ") else "")

    if current_label is not None:
        fields[current_label] = "\n".join(buffer).strip()

    return fields


def parse_docs_gate_status(text: str) -> dict:
    status_match = re.search(r"Command status: `([A-Z]+)`", text)
    query_match = re.search(r"- Query:\s*\n\s*`([^`]+)`", text)
    stderr_match = re.search(r"## Stderr\s*```text\n(.*?)```", text, re.S)

    state = status_match.group(1) if status_match else "UNKNOWN"
    detail = stderr_match.group(1).rstrip() if stderr_match else ""

    return {
        "state": state,
        "query": query_match.group(1).strip() if query_match else "",
        "detail": detail,
        "source_path": str(DOCS_GATE_PATH),
    }


def parse_witness_hierarchy(text: str) -> dict[str, int]:
    labels = {
        "physical": "Physical Witness",
        "indexed": "Indexed Witness",
        "board": "Board Witness",
        "archive": "Archive Witness",
        "promoted": "Promoted Witness",
    }
    values: dict[str, int] = {}
    for key, label in labels.items():
        pattern = rf"### \d+\. {re.escape(label)}.*?- current value:\s*\n\s*`(\d+)`"
        match = re.search(pattern, text, re.S)
        values[key] = int(match.group(1)) if match else 0
    return values


def split_ranked_label(label: str) -> tuple[str, str]:
    parts = label.split(" ", 1)
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts[0], parts[1]


def parse_ranked_frontier_section(section: str, state: str) -> list[dict]:
    pattern = re.compile(
        r"(?ms)^\d+\.\s+`(?P<label>[^`]+)`\n"
        r"\s+score:\s+`(?P<score>\d+)`\n"
        r"\s+anchor:\s+`(?P<anchor_body>[^`]+)`\s+via\s+`(?P<semantic_anchor>[^`]+)`\s+and\s+`(?P<witness_anchor>[^`]+)`\n"
        r"\s+shape:\s+lift=(?P<lift>\d+),\s+writeback=(?P<writeback>\d+),\s+restart=(?P<restart>\d+),\s+readiness=(?P<readiness>\d+),\s+penalty=(?P<penalty>\d+)\n"
        r"\s+why-now:\s+(?P<why_now>.+?)(?=^\d+\.\s+`|\n##\s|\Z)"
    )
    frontiers: list[dict] = []
    for match in pattern.finditer(section):
        frontier_id, title = split_ranked_label(match.group("label").strip())
        frontiers.append(
            {
                "id": frontier_id,
                "title": title,
                "state": state,
                "anchor_body": normalize_body_name(match.group("anchor_body").strip()),
                "semantic_anchor": match.group("semantic_anchor").strip(),
                "witness_anchor": match.group("witness_anchor").strip(),
                "source_or_archive_lift": clamp(int(match.group("lift"))),
                "cross_scale_writeback": clamp(int(match.group("writeback"))),
                "restart_gain": clamp(int(match.group("restart"))),
                "execution_readiness": clamp(int(match.group("readiness"))),
                "blocker_penalty": clamp(int(match.group("penalty"))),
                "reported_score": int(match.group("score")),
                "why_now": " ".join(match.group("why_now").split()),
                "candidate_type": "frontier",
            }
        )
    return frontiers


def parse_unassigned_pressure(section: str, board_gap: int) -> list[dict]:
    pattern = re.compile(
        r"(?ms)- `(?P<id>[^`]+)`:\s*\n\s*(?P<title>.+?)\n- Why now:\s*\n\s*(?P<why_now>.+?)\n- Anchor:\s*\n\s*`(?P<anchor>[^`]+)`\s+with\s+`(?P<anchor_detail>[^`]+)`"
    )
    frontiers: list[dict] = []
    for match in pattern.finditer(section):
        gap_bonus = 1 if board_gap >= 1500 else 0
        frontiers.append(
            {
                "id": match.group("id").strip(),
                "title": " ".join(match.group("title").split()),
                "state": "OPEN",
                "anchor_body": "self_actualize",
                "semantic_anchor": match.group("anchor_detail").strip(),
                "witness_anchor": clean_inline_value(match.group("anchor").strip()),
                "source_or_archive_lift": clamp(3 + gap_bonus),
                "cross_scale_writeback": 4,
                "restart_gain": 3,
                "execution_readiness": 2,
                "blocker_penalty": 0,
                "reported_score": 0,
                "why_now": " ".join(match.group("why_now").split()),
                "candidate_type": "frontier",
            }
        )
    return frontiers


def parse_frontier_ranking(text: str, board_gap: int) -> dict[str, dict]:
    blocked_section = extract_section(
        text,
        "## Blocked Highest Latent Leverage",
        ("## Executable Order",),
    )
    executable_section = extract_section(
        text,
        "## Executable Order",
        ("## Highest Unassigned Pressure",),
    )
    unassigned_section = extract_section(
        text,
        "## Highest Unassigned Pressure",
        ("## Before/After",),
    )

    frontiers = (
        parse_ranked_frontier_section(blocked_section, "BLOCKED")
        + parse_ranked_frontier_section(executable_section, "OPEN")
        + parse_unassigned_pressure(unassigned_section, board_gap)
    )
    return {entry["id"]: entry for entry in frontiers}


def parse_quest_board(text: str) -> dict[str, dict]:
    header_pattern = re.compile(
        r"^### Quest (?P<id>[^:]+): (?P<title>.+?) `\[(?P<state>OPEN|BLOCKED|PROMOTED(?: [^\]]+)?)\]`$",
        re.M,
    )
    matches = list(header_pattern.finditer(text))
    quests: dict[str, dict] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        fields = parse_indented_fields(block)
        state = "PROMOTED" if match.group("state").startswith("PROMOTED") else match.group("state")
        target_surfaces = extract_backticked_values(fields.get("Target surfaces", ""))
        quests[match.group("id")] = {
            "id": match.group("id"),
            "title": match.group("title").strip(),
            "state": state,
            "objective": " ".join(fields.get("Objective", "").split()),
            "why_now": " ".join(fields.get("Why now", "").split()),
            "target_surfaces": target_surfaces,
            "witness_needed": " ".join(fields.get("Witness needed", "").split()),
            "writeback": " ".join(fields.get("Writeback", "").split()),
            "restart_seed": " ".join(fields.get("Restart seed", fields.get("Next Seed", "")).split()),
            "macro_note": " ".join(fields.get("Macro Note", "").split()),
            "completion_evidence": extract_backticked_values(fields.get("Completion evidence", "")),
        }
    return quests


def parse_active_queue(text: str) -> dict[str, dict]:
    header_pattern = re.compile(r"^### (?P<id>[A-Z0-9-]+)$", re.M)
    matches = list(header_pattern.finditer(text))
    entries: dict[str, dict] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block = text[start:end].strip()
        fields = parse_indented_fields(block)
        entries[match.group("id")] = {
            "id": match.group("id"),
            "quest": clean_inline_value(fields.get("Quest", "")),
            "state": clean_inline_value(fields.get("State", "")),
            "objective": " ".join(fields.get("Objective", "").split()),
            "why_now": " ".join(fields.get("Why Now", "").split()),
            "targets": extract_backticked_values(fields.get("Targets", "")),
            "writeback": " ".join(fields.get("Writeback", "").split()),
            "next_seed": " ".join(fields.get("Next Seed", "").split()),
        }
    return entries


def parse_restart_seed(text: str) -> str:
    match = re.search(r"## Current Restart Seed\s*\n\s*`([^`]+)`", text, re.S)
    return match.group(1).strip() if match else ""


def is_meaningful_body(body: str, records: int) -> bool:
    if records < 5:
        return False
    if body.startswith("."):
        return False
    suffix = Path(body).suffix.lower()
    if suffix in COMMON_FILE_SUFFIXES:
        return False
    return True


def body_index(semantic_mass: dict) -> dict[str, dict]:
    bodies: dict[str, dict] = {}
    for entry in semantic_mass.get("body_profiles", []):
        body = entry.get("body", "")
        records = int(entry.get("records", 0))
        if not is_meaningful_body(body, records):
            continue
        bodies[body] = entry
    return bodies


def low_mass_cutoff(bodies: dict[str, dict]) -> int:
    counts = sorted(entry.get("records", 0) for entry in bodies.values())
    if not counts:
        return 120
    index = max(0, int(len(counts) * 0.3) - 1)
    return counts[index]


def lower_texts(*parts: str) -> str:
    return " ".join(part for part in parts if part).lower()


def infer_anchor_body(
    title: str,
    objective: str,
    why_now: str,
    target_surfaces: list[str],
    fallback: str = "",
) -> str:
    combined = lower_texts(title, objective, why_now, " ".join(target_surfaces))
    if "qshrink" in combined:
        return "QSHRINK - ATHENA (internal use)"
    if "athenachka" in combined or "athena neural network" in combined:
        return "NERUAL NETWORK"
    if "trading bot" in combined or "live memory gate" in combined or "google docs" in combined:
        return "Trading Bot"
    if "athena fleet" in combined:
        return "Athena FLEET"
    if "orgin" in combined:
        return "ORGIN"
    if "stoicheia" in combined:
        return "Stoicheia (Element Sudoku)"
    if "voynich" in combined:
        return "Voynich"
    if fallback:
        return normalize_body_name(fallback)
    for path in target_surfaces:
        head = path.split("/", 1)[0].strip()
        if head:
            return normalize_body_name(head)
    return "self_actualize"


def docs_gate_dependent(candidate: dict) -> bool:
    haystack = lower_texts(
        candidate.get("title", ""),
        candidate.get("objective", ""),
        candidate.get("why_now", ""),
        " ".join(candidate.get("target_surfaces", [])),
    )
    return any(
        token in haystack
        for token in (
            "google docs",
            "live docs",
            "docs_search.py",
            "oauth",
            "live memory gate",
            "token.json",
            "credentials.json",
        )
    )


def path_is_synthesis_surface(path: str) -> bool:
    lowered = path.lower()
    return any(token in lowered for token in SYNTHESIS_TOKENS)


def prioritized_synthesis_targets(paths: list[str]) -> list[str]:
    unique_paths = sorted(set(path for path in paths if path_is_synthesis_surface(path)))

    def sort_key(path: str) -> tuple[int, int, str]:
        lowered = path.lower()
        priority = min(
            (rank for token, rank in TARGET_PRIORITY.items() if token in lowered),
            default=99,
        )
        return (priority, len(path), path)

    return sorted(unique_paths, key=sort_key)[:6]


def keyword_flags(candidate: dict, board_gap: int) -> dict[str, bool]:
    lowered = lower_texts(
        candidate.get("title", ""),
        candidate.get("objective", ""),
        candidate.get("why_now", ""),
        candidate.get("writeback", ""),
        candidate.get("semantic_anchor", ""),
    )
    archive_terms = ("archive", "dark", "atlas", "searchable", "mirror tissue", "indexed lag", "searchable body")
    return {
        "duplicate_or_mirror": any(
            token in lowered
            for token in ("duplicate", "mirror", "stale", "split", "drift", "synchron", "reconcile", "reconciliation")
        ),
        "archive_dark": any(token in lowered for token in archive_terms)
        or (
            board_gap >= 1500
            and (
                candidate.get("anchor_body") == "self_actualize"
                or "archive-backed" in lowered
                or "atlas" in candidate.get("id", "").lower()
            )
        ),
        "weak_route_presence": len(candidate.get("synthesis_targets", [])) <= 1,
        "low_promotion": candidate.get("body_records", 0) <= candidate.get("low_mass_cutoff", 0),
    }


def score_source_or_archive_lift(candidate: dict) -> int:
    body_records = candidate.get("body_records", 0)
    source_records = candidate.get("body_source_records", 0)
    lowered = lower_texts(candidate.get("title", ""), candidate.get("objective", ""), candidate.get("why_now", ""))

    score = 1
    if body_records >= 500 or source_records >= 300:
        score += 1
    if any(token in lowered for token in ("source", "archive", "atlas", "mirror", "witness", "searchable", "memory")):
        score += 1
    if docs_gate_dependent(candidate):
        score += 1
    return clamp(score)


def score_cross_scale_writeback(candidate: dict) -> int:
    target_roots = {path.split("/", 1)[0] for path in candidate.get("target_surfaces", []) if "/" in path}
    synthesis_count = len(candidate.get("synthesis_targets", []))
    writeback = candidate.get("writeback", "").lower()

    score = 1
    if len(target_roots) >= 3 or synthesis_count >= 2:
        score += 1
    if len(target_roots) >= 4 or synthesis_count >= 4:
        score += 1
    if any(token in writeback for token in ("hall", "queue", "manifest", "receipt", "board", "temple", "restart")):
        score += 1
    return clamp(score)


def score_restart_gain(candidate: dict, current_restart_seed: str) -> int:
    score = 1
    restart_seed = lower_texts(candidate.get("restart_seed", ""))
    current_seed = current_restart_seed.lower()
    identity = lower_texts(candidate.get("id", ""), candidate.get("title", ""), candidate.get("anchor_body", ""))

    if restart_seed:
        score += 1
    if any(token and token in current_seed for token in (candidate.get("id", "").lower(), candidate.get("anchor_body", "").lower())):
        score += 1
    if any(token in restart_seed for token in ("next", "restart", "seed")) or "q42" in current_seed and "q42" in identity:
        score += 1
    return clamp(score)


def score_execution_readiness(candidate: dict) -> int:
    if candidate.get("state") == "BLOCKED":
        return 0

    target_count = len(candidate.get("target_surfaces", []))
    synthesis_count = len(candidate.get("synthesis_targets", []))
    score = 1
    if target_count >= 2 or synthesis_count >= 1:
        score += 1
    if target_count >= 4 or synthesis_count >= 2:
        score += 1
    if candidate.get("writeback") or candidate.get("restart_seed"):
        score += 1
    return clamp(score)


def score_blocker_penalty(candidate: dict, docs_state: str) -> int:
    if candidate.get("state") == "BLOCKED" and docs_gate_dependent(candidate) and docs_state == "BLOCKED":
        return 4
    if candidate.get("state") == "BLOCKED":
        return 2
    return 0


def score_neglect_bonus(candidate: dict, flags: dict[str, bool]) -> int:
    score = 0
    if flags["low_promotion"]:
        score += 1
    if flags["weak_route_presence"]:
        score += 1
    if flags["duplicate_or_mirror"] or flags["archive_dark"]:
        score += 1
    return clamp(score, 0, 3)


def recent_reports() -> list[Path]:
    reports = sorted(REPORTS_ROOT.glob("corpus_weave_vishnu_*.md"))
    return reports[-6:]


def extract_prior_score(text: str, candidate_terms: list[str]) -> tuple[int | None, int | None]:
    lowered = text.lower()
    for term in candidate_terms:
        term_lower = term.lower()
        if not term_lower or term_lower not in lowered:
            continue
        window_start = lowered.find(term_lower)
        window = text[window_start : window_start + 500]
        score_match = re.search(r"score:\s*`?(\d+)`?", window)
        penalty_match = re.search(r"penalty:\s*`?(\d+)`?", window)
        score = int(score_match.group(1)) if score_match else None
        penalty = int(penalty_match.group(1)) if penalty_match else None
        return score, penalty
    return None, None


def repeat_penalty(candidate: dict, provisional_final: int, report_payloads: list[dict]) -> int:
    candidate_terms = [
        candidate.get("id", ""),
        candidate.get("title", ""),
        candidate.get("anchor_body", ""),
    ]
    mentions = 0
    latest_hit = False
    prior_score: int | None = None
    prior_penalty: int | None = None

    for index, payload in enumerate(report_payloads):
        text = payload["text"]
        lowered = text.lower()
        if any(term and term.lower() in lowered for term in candidate_terms):
            mentions += 1
            if index == len(report_payloads) - 1:
                latest_hit = True
            score, penalty = extract_prior_score(text, candidate_terms)
            if score is not None and (prior_score is None or score > prior_score):
                prior_score = score
                prior_penalty = penalty

    if mentions == 0:
        return 0

    materially_stronger = False
    if prior_score is not None:
        if provisional_final > prior_score:
            materially_stronger = True
        elif (
            provisional_final == prior_score
            and prior_penalty is not None
            and candidate.get("blocker_penalty", 0) < prior_penalty
            and candidate.get("synthesis_targets")
        ):
            materially_stronger = True

    if materially_stronger:
        return 0

    penalty = 1
    if latest_hit:
        penalty += 1
    if mentions >= 2:
        penalty += 1
    return clamp(penalty, 0, 3)


def build_candidate_from_quest(
    quest: dict,
    ranking_entry: dict | None,
    current_restart_seed: str,
    docs_state: str,
    bodies: dict[str, dict],
    mass_cutoff: int,
    board_gap: int,
) -> dict:
    candidate = dict(quest)
    candidate["candidate_type"] = "quest"
    candidate["anchor_body"] = infer_anchor_body(
        quest["title"],
        quest["objective"],
        quest["why_now"],
        quest["target_surfaces"],
        ranking_entry["anchor_body"] if ranking_entry else "",
    )
    body_entry = bodies.get(candidate["anchor_body"], {})
    candidate["body_records"] = int(body_entry.get("records", 0))
    candidate["body_source_records"] = int(body_entry.get("role_counts", {}).get("source", 0))
    candidate["low_mass_cutoff"] = mass_cutoff
    candidate["docs_gate_dependent"] = docs_gate_dependent(candidate)
    candidate["synthesis_targets"] = prioritized_synthesis_targets(candidate.get("target_surfaces", []))

    if ranking_entry:
        candidate["semantic_anchor"] = ranking_entry.get("semantic_anchor", "")
        candidate["witness_anchor"] = ranking_entry.get("witness_anchor", "")
        candidate["source_or_archive_lift"] = ranking_entry["source_or_archive_lift"]
        candidate["cross_scale_writeback"] = ranking_entry["cross_scale_writeback"]
        candidate["restart_gain"] = ranking_entry["restart_gain"]
        candidate["execution_readiness"] = ranking_entry["execution_readiness"]
        candidate["blocker_penalty"] = ranking_entry["blocker_penalty"]
    else:
        candidate["semantic_anchor"] = ""
        candidate["witness_anchor"] = ""
        candidate["source_or_archive_lift"] = score_source_or_archive_lift(candidate)
        candidate["cross_scale_writeback"] = score_cross_scale_writeback(candidate)
        candidate["restart_gain"] = score_restart_gain(candidate, current_restart_seed)
        candidate["execution_readiness"] = score_execution_readiness(candidate)
        candidate["blocker_penalty"] = score_blocker_penalty(candidate, docs_state)

    flags = keyword_flags(candidate, board_gap)
    candidate["neglect_flags"] = flags
    candidate["base_leverage"] = (
        candidate["source_or_archive_lift"]
        + candidate["cross_scale_writeback"]
        + candidate["restart_gain"]
        + candidate["execution_readiness"]
        - candidate["blocker_penalty"]
    )
    candidate["neglect_bonus"] = score_neglect_bonus(candidate, flags)
    return candidate


def build_candidate_from_ranking(
    ranking_entry: dict,
    current_restart_seed: str,
    docs_state: str,
    bodies: dict[str, dict],
    mass_cutoff: int,
    board_gap: int,
) -> dict:
    candidate = {
        "id": ranking_entry["id"],
        "title": ranking_entry["title"],
        "state": ranking_entry["state"],
        "objective": ranking_entry.get("semantic_anchor", ""),
        "why_now": ranking_entry.get("why_now", ""),
        "target_surfaces": [],
        "writeback": "",
        "restart_seed": current_restart_seed if ranking_entry["id"] in current_restart_seed else "",
        "candidate_type": ranking_entry.get("candidate_type", "frontier"),
        "anchor_body": ranking_entry["anchor_body"],
        "semantic_anchor": ranking_entry.get("semantic_anchor", ""),
        "witness_anchor": ranking_entry.get("witness_anchor", ""),
    }
    if candidate["id"] == "FRONT-FULL-ATLAS-REGEN":
        candidate["target_surfaces"] = [
            "self_actualize/corpus_atlas.json",
            "self_actualize/corpus_atlas_summary.md",
            "self_actualize/mycelium_brain/receipts/corpus_weave_atlas_regen_receipt.md",
        ]
        candidate["writeback"] = "atlas, summary, and receipt"
    candidate["synthesis_targets"] = prioritized_synthesis_targets(candidate["target_surfaces"])
    body_entry = bodies.get(candidate["anchor_body"], {})
    candidate["body_records"] = int(body_entry.get("records", 0))
    candidate["body_source_records"] = int(body_entry.get("role_counts", {}).get("source", 0))
    candidate["low_mass_cutoff"] = mass_cutoff
    candidate["docs_gate_dependent"] = docs_gate_dependent(candidate)
    candidate["source_or_archive_lift"] = ranking_entry["source_or_archive_lift"]
    candidate["cross_scale_writeback"] = ranking_entry["cross_scale_writeback"]
    candidate["restart_gain"] = ranking_entry["restart_gain"]
    candidate["execution_readiness"] = ranking_entry["execution_readiness"]
    candidate["blocker_penalty"] = score_blocker_penalty(candidate, docs_state)
    flags = keyword_flags(candidate, board_gap)
    candidate["neglect_flags"] = flags
    candidate["base_leverage"] = (
        candidate["source_or_archive_lift"]
        + candidate["cross_scale_writeback"]
        + candidate["restart_gain"]
        + candidate["execution_readiness"]
        - candidate["blocker_penalty"]
    )
    candidate["neglect_bonus"] = score_neglect_bonus(candidate, flags)
    return candidate


def build_synthetic_body_candidates(
    bodies: dict[str, dict],
    occupied_bodies: set[str],
    quest_text: str,
    queue_text: str,
    mass_cutoff: int,
) -> list[dict]:
    candidates: list[dict] = []
    occupied_text = lower_texts(quest_text, queue_text)
    for body, entry in bodies.items():
        records = int(entry.get("records", 0))
        if body in occupied_bodies:
            continue
        if body.lower() in occupied_text:
            continue
        if records > max(mass_cutoff * 2, 180):
            continue
        source_records = int(entry.get("role_counts", {}).get("source", 0))
        if source_records <= 0:
            continue
        candidate = {
            "id": f"BODY-{slugify(body)}-INTERCONNECT",
            "title": f"Interconnect {body}",
            "state": "OPEN",
            "objective": f"make the low-mass {body} body more routeable and replayable",
            "why_now": f"{body} carries {records} indexed records with no active canonical bridge in the Hall surfaces",
            "target_surfaces": [],
            "writeback": "",
            "restart_seed": "",
            "candidate_type": "body",
            "anchor_body": body,
            "semantic_anchor": "low-mass family densification",
            "witness_anchor": "indexed",
            "body_records": records,
            "body_source_records": source_records,
            "low_mass_cutoff": mass_cutoff,
            "docs_gate_dependent": False,
            "synthesis_targets": [],
            "source_or_archive_lift": clamp(2 if source_records >= 25 else 1),
            "cross_scale_writeback": 1,
            "restart_gain": clamp(2 if records >= 40 else 1),
            "execution_readiness": clamp(2 if records >= 40 else 1),
            "blocker_penalty": 0,
        }
        flags = {
            "duplicate_or_mirror": False,
            "archive_dark": False,
            "weak_route_presence": True,
            "low_promotion": True,
        }
        candidate["neglect_flags"] = flags
        candidate["base_leverage"] = (
            candidate["source_or_archive_lift"]
            + candidate["cross_scale_writeback"]
            + candidate["restart_gain"]
            + candidate["execution_readiness"]
            - candidate["blocker_penalty"]
        )
        candidate["neglect_bonus"] = score_neglect_bonus(candidate, flags)
        candidates.append(candidate)
    return candidates


def candidate_sort_key(candidate: dict) -> tuple[int, int, int, int, int, str]:
    return (
        -candidate["final_score"],
        -candidate["execution_readiness"],
        -candidate["cross_scale_writeback"],
        candidate["blocker_penalty"],
        candidate["repeat_penalty"],
        f"{candidate['id']}|{candidate['title']}".lower(),
    )


def one_line_bridge_rationale(candidate: dict, docs_state: str) -> str:
    reasons: list[str] = []
    body = candidate.get("anchor_body", "")
    if candidate.get("docs_gate_dependent") and docs_state == "BLOCKED":
        reasons.append("Docs-gate dependence keeps the body disconnected from live memory")
    if candidate.get("neglect_flags", {}).get("duplicate_or_mirror"):
        reasons.append("duplicate or synchronization drift is still visible")
    if candidate.get("neglect_flags", {}).get("archive_dark"):
        reasons.append("archive or atlas darkness still outruns live indexing")
    if candidate.get("neglect_flags", {}).get("weak_route_presence"):
        reasons.append("route presence is still thin")
    if candidate.get("body_records", 0) and candidate["body_records"] <= candidate.get("low_mass_cutoff", 0):
        reasons.append(f"the body is still low-mass at {candidate['body_records']} indexed records")
    if not reasons:
        reasons.append("it improves whole-corpus coherence without reopening solved fronts")
    return f"{body}: " + "; ".join(reasons[:2])


def allowed_touched_paths(candidate: dict) -> list[str]:
    if candidate.get("id") == "Q42":
        return q42_bundle_allowed_touched_paths()
    return prioritized_synthesis_targets(candidate.get("synthesis_targets", []))


def build_missing_bridge_entry(candidate: dict) -> dict:
    return {
        "rank": 0,
        "id": candidate["id"],
        "title": candidate["title"],
        "anchor_body": candidate["anchor_body"],
        "state": candidate["state"],
        "candidate_type": candidate["candidate_type"],
        "docs_gate_dependent": candidate["docs_gate_dependent"],
        "final_score": candidate["final_score"],
        "score_breakdown": {
            "source_or_archive_lift": candidate["source_or_archive_lift"],
            "cross_scale_writeback": candidate["cross_scale_writeback"],
            "restart_gain": candidate["restart_gain"],
            "execution_readiness": candidate["execution_readiness"],
            "blocker_penalty": candidate["blocker_penalty"],
            "neglect_bonus": candidate["neglect_bonus"],
            "repeat_penalty": candidate["repeat_penalty"],
            "base_leverage": candidate["base_leverage"],
        },
        "rationale": candidate["bridge_rationale"],
        "allowed_touched_paths": allowed_touched_paths(candidate),
    }


def build_neglected_area_entry(body: str, body_entry: dict, representative: dict, docs_state: str) -> dict:
    rationale = one_line_bridge_rationale(representative, docs_state)
    return {
        "rank": 0,
        "body": body,
        "records": int(body_entry.get("records", 0)),
        "representative_candidate_id": representative["id"],
        "representative_candidate_title": representative["title"],
        "state": representative["state"],
        "final_score": representative["final_score"],
        "rationale": rationale,
    }


def choose_winning_move(candidates: list[dict], docs_state: str) -> tuple[dict, list[str]]:
    for candidate in candidates:
        candidate_paths = allowed_touched_paths(candidate)
        if candidate.get("docs_gate_dependent") and docs_state == "BLOCKED":
            continue
        if candidate.get("execution_readiness", 0) < 2:
            continue
        if not candidate_paths:
            continue
        winning = build_missing_bridge_entry(candidate)
        winning["mode"] = "write_eligible"
        winning["report_only"] = False
        winning["instruction"] = candidate["bridge_rationale"]
        return winning, candidate_paths

    fallback = build_missing_bridge_entry(candidates[0])
    fallback["mode"] = "report_only"
    fallback["report_only"] = True
    fallback["instruction"] = fallback["rationale"]
    return fallback, []


def select_report_path() -> str:
    local_timestamp = local_now()
    stamp = local_timestamp.strftime("%Y-%m-%d_%H")
    return f"NERVOUS_SYSTEM/90_LEDGERS/automations/corpus_weave_vishnu_{stamp}.md"


def derive_corpus_weave_ranking() -> dict:
    docs_gate_text = load_text(DOCS_GATE_PATH)
    leverage_text = load_text(LEVERAGE_RANKING_PATH)
    witness_text = load_text(WITNESS_HIERARCHY_PATH)
    semantic_mass = load_json(SEMANTIC_MASS_PATH)
    quest_board_text = load_text(QUEST_BOARD_PATH)
    active_queue_text = load_text(ACTIVE_QUEUE_PATH)
    next_self_prompt_text = load_text(NEXT_SELF_PROMPT_PATH)

    docs_gate = parse_docs_gate_status(docs_gate_text)
    witness_values = parse_witness_hierarchy(witness_text)
    board_gap = max(0, witness_values.get("board", 0) - witness_values.get("indexed", 0))
    frontier_ranking = parse_frontier_ranking(leverage_text, board_gap)
    quests = parse_quest_board(quest_board_text)
    active_queue = parse_active_queue(active_queue_text)
    current_restart_seed = parse_restart_seed(next_self_prompt_text)
    bodies = body_index(semantic_mass)
    mass_cutoff = low_mass_cutoff(bodies)

    promoted_ids = {
        quest_id
        for quest_id, quest in quests.items()
        if quest.get("state") == "PROMOTED"
    }
    promoted_ids.update(
        entry_id
        for entry_id, entry in active_queue.items()
        if entry.get("state") in {"PROMOTED", "COMPLETE"}
    )

    candidates: dict[str, dict] = {}
    for quest_id, quest in quests.items():
        if quest.get("state") not in {"OPEN", "BLOCKED"}:
            continue
        ranking_entry = frontier_ranking.get(quest_id)
        candidate = build_candidate_from_quest(
            quest,
            ranking_entry,
            current_restart_seed,
            docs_gate["state"],
            bodies,
            mass_cutoff,
            board_gap,
        )
        candidates[quest_id] = candidate

    for frontier_id, frontier in frontier_ranking.items():
        if frontier_id in promoted_ids:
            continue
        if frontier_id in candidates:
            continue
        candidates[frontier_id] = build_candidate_from_ranking(
            frontier,
            current_restart_seed,
            docs_gate["state"],
            bodies,
            mass_cutoff,
            board_gap,
        )

    occupied_bodies = {candidate["anchor_body"] for candidate in candidates.values()}
    for candidate in build_synthetic_body_candidates(
        bodies,
        occupied_bodies,
        quest_board_text,
        active_queue_text,
        mass_cutoff,
    ):
        candidates[candidate["id"]] = candidate

    report_payloads = [{"path": path, "text": load_text(path)} for path in recent_reports()]

    for candidate in candidates.values():
        provisional = candidate["base_leverage"] + candidate["neglect_bonus"]
        candidate["repeat_penalty"] = repeat_penalty(candidate, provisional, report_payloads)
        candidate["final_score"] = provisional - candidate["repeat_penalty"]
        candidate["bridge_rationale"] = one_line_bridge_rationale(candidate, docs_gate["state"])

    ranked_candidates = sorted(candidates.values(), key=candidate_sort_key)
    bridge_candidates = [candidate for candidate in ranked_candidates if candidate["candidate_type"] != "body"] or ranked_candidates
    missing_bridges = [build_missing_bridge_entry(candidate) for candidate in bridge_candidates[:5]]
    for index, entry in enumerate(missing_bridges, start=1):
        entry["rank"] = index

    area_representatives: dict[str, dict] = {}
    for candidate in ranked_candidates:
        body = candidate["anchor_body"]
        if body not in area_representatives:
            area_representatives[body] = candidate
    neglected_areas = []
    for body, representative in area_representatives.items():
        body_entry = bodies.get(body, {"records": representative.get("body_records", 0)})
        neglected_areas.append(build_neglected_area_entry(body, body_entry, representative, docs_gate["state"]))
    neglected_areas.sort(
        key=lambda entry: (
            -entry["final_score"],
            entry["state"] == "PROMOTED",
            entry["body"].lower(),
        )
    )
    neglected_areas = neglected_areas[:3]
    for index, entry in enumerate(neglected_areas, start=1):
        entry["rank"] = index

    winning_move, touched_paths_allowed = choose_winning_move(bridge_candidates, docs_gate["state"])

    blockers: list[str] = []
    if docs_gate["state"] == "BLOCKED" and docs_gate["detail"]:
        blockers.append(docs_gate["detail"])
    if winning_move["report_only"]:
        blockers.append("No write-eligible bridge cleared the readiness and lawful-target bar; this hour remains report-only.")

    restart_seed = (
        candidates[winning_move["id"]].get("restart_seed")
        if winning_move["id"] in candidates and candidates[winning_move["id"]].get("restart_seed")
        else current_restart_seed
    )

    return {
        "generated_at": utc_now(),
        "derivation_version": DERIVATION_VERSION,
        "derivation_command": DERIVATION_COMMAND,
        "source_paths": {
            "live_docs_gate_status": str(DOCS_GATE_PATH),
            "frontier_leverage_ranking": str(LEVERAGE_RANKING_PATH),
            "canonical_witness_hierarchy": str(WITNESS_HIERARCHY_PATH),
            "semantic_mass_ledger": str(SEMANTIC_MASS_PATH),
            "quest_board": str(QUEST_BOARD_PATH),
            "active_queue": str(ACTIVE_QUEUE_PATH),
            "next_self_prompt": str(NEXT_SELF_PROMPT_PATH),
            "recent_reports": [str(payload["path"]) for payload in report_payloads],
        },
        "docs_gate_status": docs_gate,
        "selected_report_path": select_report_path(),
        "neglected_areas": neglected_areas,
        "missing_bridges": missing_bridges[: max(3, min(5, len(missing_bridges)))],
        "winning_move": winning_move,
        "touched_paths_allowed": touched_paths_allowed,
        "blockers": blockers,
        "restart_seed": restart_seed,
    }


def main() -> int:
    payload = derive_corpus_weave_ranking()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
