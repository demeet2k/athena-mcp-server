from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List


FILTER_ORDER = [
    "authority",
    "witness",
    "zone",
    "surface_class",
    "root",
    "family",
    "tags",
]

WITNESS_WEIGHT = {
    "indexed": 1.0,
    "generated": 0.9,
    "archive": 0.78,
    "promoted": 0.7,
    "board": 0.64,
    "physical": 0.42,
}

PROOF_WEIGHT = {
    "OK": 1.0,
    "NEAR": 0.78,
    "AMBIG": 0.46,
    "FAIL": 0.1,
}

REPLAY_WEIGHT = {
    "replay-safe": 1.0,
    "generated-refreshable": 0.92,
    "replay-partial": 0.68,
    "witness-only": 0.38,
}

ZONE_PRIORITY = {
    "Cortex": 1.0,
    "RuntimeMirror": 0.95,
    "GovernanceMirror": 0.92,
    "DeepRoot": 0.96,
    "CorpusAtlas": 0.88,
    "ArchiveAtlas": 0.76,
    "BoardScope": 0.64,
    "PromotedSlice": 0.7,
    "CapsuleLayer": 0.94,
    "GraphLayer": 0.9,
    "ReceiptLineage": 0.84,
    "ReserveQuarantine": 0.48,
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def witness_score(record: Dict[str, Any]) -> float:
    return WITNESS_WEIGHT.get(record.get("witness_class", "physical"), 0.35)


def proof_score(record: Dict[str, Any]) -> float:
    return PROOF_WEIGHT.get(record.get("proof_state", "AMBIG"), 0.35)


def replay_score(record: Dict[str, Any]) -> float:
    return REPLAY_WEIGHT.get(record.get("replay_class", "witness-only"), 0.35)


def freshness_score(record: Dict[str, Any]) -> float:
    freshness = record.get("freshness", {})
    if isinstance(freshness, dict):
        return float(freshness.get("score", 0.35))
    return 0.35


def text_match_score(record: Dict[str, Any], query_text: str) -> float:
    if not query_text:
        return 0.5
    haystack_parts = [
        record.get("title_hint", ""),
        record.get("relative_path", ""),
        record.get("root_name", ""),
        record.get("family_id", ""),
        " ".join(record.get("query_tags", [])),
        record.get("semantic_role", ""),
        record.get("storage_zone", ""),
    ]
    haystack = normalize(" ".join(haystack_parts))
    query_norm = normalize(query_text)
    if not query_norm:
        return 0.5
    if query_norm == normalize(record.get("relative_path", "")):
        return 1.0
    if query_norm == normalize(record.get("title_hint", "")):
        return 0.98
    if query_norm in haystack:
        return 0.84
    query_tokens = set(query_norm.split())
    if not query_tokens:
        return 0.5
    overlap = query_tokens & set(haystack.split())
    if not overlap:
        return 0.0
    return round(0.38 + (0.5 * (len(overlap) / len(query_tokens))), 3)


def tag_overlap_score(record: Dict[str, Any], query_tags: Iterable[str]) -> float:
    wanted = {normalize(tag) for tag in query_tags if tag}
    if not wanted:
        return 0.5
    present = {normalize(tag) for tag in record.get("query_tags", [])}
    overlap = wanted & present
    if not overlap:
        return 0.0
    return round(0.4 + (0.6 * (len(overlap) / len(wanted))), 3)


def cost_score(record: Dict[str, Any]) -> float:
    zone = record.get("storage_zone", "")
    zone_weight = ZONE_PRIORITY.get(zone, 0.5)
    freshness = freshness_score(record)
    size_bytes = max(1, int(record.get("size_bytes", 1)))
    size_penalty = 0.05
    if size_bytes > 1_000_000:
        size_penalty = 0.18
    elif size_bytes > 250_000:
        size_penalty = 0.12
    elif size_bytes > 50_000:
        size_penalty = 0.08
    return max(0.08, round(1.0 - ((0.55 * zone_weight) + (0.35 * freshness) - size_penalty), 3))


def apply_filters(
    records: List[Dict[str, Any]],
    entry_filters: Dict[str, Any],
    query_text: str = "",
    override_tags: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    current = list(records)
    tags = list(override_tags or [])
    query_norm = normalize(query_text)

    for stage in FILTER_ORDER:
        if stage == "authority":
            minimum = int(entry_filters.get("authority_min", 0))
            if minimum:
                current = [record for record in current if int(record.get("authority_rank", 0)) >= minimum]
        elif stage == "witness":
            allowed = set(entry_filters.get("witnesses", []))
            if allowed:
                current = [record for record in current if record.get("witness_class") in allowed]
        elif stage == "zone":
            allowed = set(entry_filters.get("zones", []))
            if allowed:
                current = [record for record in current if record.get("storage_zone") in allowed]
        elif stage == "surface_class":
            allowed = set(entry_filters.get("surface_classes", []))
            if allowed:
                current = [record for record in current if record.get("surface_class") in allowed]
        elif stage == "root":
            allowed = {normalize(item) for item in entry_filters.get("roots", [])}
            if allowed:
                current = [record for record in current if normalize(record.get("root_name", "")) in allowed]
        elif stage == "family":
            allowed = {normalize(item) for item in entry_filters.get("families", [])}
            if allowed:
                current = [record for record in current if normalize(record.get("family_id", "")) in allowed]
        elif stage == "tags":
            allowed_tags = {normalize(item) for item in entry_filters.get("tags_any", [])}
            if tags:
                allowed_tags |= {normalize(item) for item in tags}
            if allowed_tags:
                current = [
                    record
                    for record in current
                    if allowed_tags & {normalize(tag) for tag in record.get("query_tags", [])}
                ]

    if entry_filters.get("text_required"):
        current = [record for record in current if record.get("text_extractable")]
    if entry_filters.get("query_text_required") and query_norm:
        current = [
            record
            for record in current
            if text_match_score(record, query_text) > 0.0
        ]
    return current


def rank_records(
    records: List[Dict[str, Any]],
    ranking_stack: List[str],
    query_text: str = "",
    query_tags: Iterable[str] | None = None,
    preferred_zones: Iterable[str] | None = None,
) -> List[Dict[str, Any]]:
    weighted: List[Dict[str, Any]] = []
    preferred = list(preferred_zones or [])
    tag_list = list(query_tags or [])
    zone_boost = {
        zone: round(1.0 - (index * 0.08), 3)
        for index, zone in enumerate(preferred, start=0)
    }

    for record in records:
        contributions: Dict[str, float] = {}
        for item in ranking_stack:
            if item == "authority":
                contributions[item] = round(int(record.get("authority_rank", 0)) / 5.0, 3)
            elif item == "witness":
                contributions[item] = witness_score(record)
            elif item == "proof":
                contributions[item] = proof_score(record)
            elif item == "freshness":
                contributions[item] = freshness_score(record)
            elif item == "replay":
                contributions[item] = replay_score(record)
            elif item == "zone_priority":
                contributions[item] = zone_boost.get(
                    record.get("storage_zone", ""), ZONE_PRIORITY.get(record.get("storage_zone", ""), 0.45)
                )
            elif item == "text_match":
                contributions[item] = text_match_score(record, query_text)
            elif item == "tag_overlap":
                contributions[item] = tag_overlap_score(record, tag_list)
            elif item == "cost":
                contributions[item] = 1.0 - cost_score(record)
            else:
                contributions[item] = 0.0
        total = round(sum(contributions.values()) / max(1, len(ranking_stack)), 4)
        ranked = dict(record)
        ranked["ranking"] = {"score": total, "contributions": contributions}
        weighted.append(ranked)

    return sorted(
        weighted,
        key=lambda item: (-item["ranking"]["score"], item.get("relative_path", "")),
    )


def run_shortcut(
    plan: Dict[str, Any],
    records: List[Dict[str, Any]],
    query_text: str = "",
    query_tags: Iterable[str] | None = None,
    limit: int = 12,
) -> Dict[str, Any]:
    filtered = apply_filters(records, plan.get("entry_filters", {}), query_text, query_tags)
    if not filtered and plan.get("fallback_zones"):
        relaxed = dict(plan.get("entry_filters", {}))
        relaxed["zones"] = list(plan.get("fallback_zones", []))
        filtered = apply_filters(records, relaxed, query_text, query_tags)

    ranked = rank_records(
        filtered,
        list(plan.get("ranking_stack", [])),
        query_text=query_text,
        query_tags=query_tags,
        preferred_zones=plan.get("preferred_zones", []),
    )
    matches = ranked[:limit]
    result_class = "answer" if matches else "abstain"
    if matches and any(item.get("proof_state") == "AMBIG" for item in matches[:3]):
        result_class = "ambiguity"
    if matches and all(item.get("storage_zone") == "ReserveQuarantine" for item in matches[:3]):
        result_class = "next-front"

    return {
        "shortcut_id": plan.get("shortcut_id"),
        "intent_class": plan.get("intent_class"),
        "matches": matches,
        "result_class": result_class,
        "stop_condition": plan.get("stop_condition", "first witnessed closure"),
        "filter_order": FILTER_ORDER,
        "preferred_zones": plan.get("preferred_zones", []),
        "ranking_stack": plan.get("ranking_stack", []),
    }


def summarize_route(matches: List[Dict[str, Any]], result_class: str) -> str:
    if not matches:
        return "No lawful witness-bearing route resolved; abstain and widen through fallback zones or stronger witnesses."
    zones = sorted({item.get("storage_zone", "") for item in matches[:5] if item.get("storage_zone")})
    titles = [item.get("title_hint") or item.get("relative_path") for item in matches[:3]]
    return (
        f"{result_class.upper()} through {', '.join(zones)} using "
        f"{' -> '.join(title for title in titles if title)}"
    )
