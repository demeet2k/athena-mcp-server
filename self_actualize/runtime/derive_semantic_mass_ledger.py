from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
GUILD_HALL_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "GLOBAL_EMERGENT_GUILD_HALL"
RECEIPTS_ROOT = SELF_ACTUALIZE_ROOT / "mycelium_brain" / "receipts"

CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
ARCHIVE_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "archive_atlas.json"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "semantic_mass_ledger.json"
OUTPUT_MARKDOWN_PATH = GUILD_HALL_ROOT / "09_SEMANTIC_MASS_LEDGER.md"
OUTPUT_RECEIPT_PATH = RECEIPTS_ROOT / "2026-03-09_semantic_mass_ledger.md"
DERIVATION_COMMAND = "python -m self_actualize.runtime.derive_semantic_mass_ledger"

ROLE_ORDER = [
    "source",
    "generated",
    "mirror",
    "protocol",
    "ledger",
    "receipt",
    "vendor",
    "archive-backed",
]

GENERATED_TOP_LEVELS = {
    "QSHRINK - ATHENA (internal use)",
}

GENERATED_MARKERS = (
    "dynamic_neural_network",
    "active_nervous_system",
    "07_full_project_integration_256",
    "06_realtime_board",
    "trading_bot_athena_256x4",
    "_build/",
)

MIRROR_MARKERS = ("mirror", "mirrors", "precursor", "duplicate", "duplicates", "copy")
PROTOCOL_MARKERS = ("protocol", "protocols", "charter", "laws", "constitution")
LEDGER_MARKERS = ("ledger", "ledgers", "queue", "queues", "manifest", "manifests")
VENDOR_MARKERS = ("node_modules", ".venv", "vendor", "third_party", "site-packages")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def normalize_path(value: str) -> str:
    return value.replace("\\", "/").lower()


def pct(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((count / total) * 100, 1)


def classify_live_record(record: dict) -> str:
    relative_path = normalize_path(record.get("relative_path", ""))
    file_name = Path(record.get("relative_path", "")).name.lower()
    top_level = record.get("top_level") or "<unknown>"

    if any(marker in relative_path for marker in VENDOR_MARKERS):
        return "vendor"
    if "/receipts/" in relative_path or "receipt" in file_name:
        return "receipt"
    if any(marker in relative_path for marker in PROTOCOL_MARKERS):
        return "protocol"
    if any(marker in relative_path for marker in LEDGER_MARKERS):
        return "ledger"
    if any(marker in relative_path for marker in MIRROR_MARKERS):
        return "mirror"
    if top_level in GENERATED_TOP_LEVELS:
        return "generated"
    if any(marker in relative_path for marker in GENERATED_MARKERS):
        return "generated"
    return "source"


def top_entries(counter: Counter[str], limit: int = 5) -> list[dict[str, int | str | float]]:
    total = sum(counter.values())
    items: list[dict[str, int | str | float]] = []
    for name, count in counter.most_common(limit):
        items.append(
            {
                "name": name,
                "count": count,
                "share_percent": pct(count, total),
            }
        )
    return items


def derive_semantic_mass_ledger() -> dict:
    atlas = load_json(CORPUS_ATLAS_PATH)
    archive_atlas = load_json(ARCHIVE_ATLAS_PATH)
    live_records = atlas.get("records", [])
    archive_records = archive_atlas.get("records", [])

    live_role_counts: Counter[str] = Counter()
    live_role_by_body: dict[str, Counter[str]] = defaultdict(Counter)
    archive_top_levels: Counter[str] = Counter()
    body_counts: Counter[str] = Counter()

    for record in live_records:
        top_level = record.get("top_level") or "<unknown>"
        role = classify_live_record(record)
        live_role_counts[role] += 1
        live_role_by_body[top_level][role] += 1
        body_counts[top_level] += 1

    for record in archive_records:
        archive_top_levels[record.get("top_level") or "<unknown>"] += 1

    body_profiles = []
    for body, total in sorted(body_counts.items(), key=lambda item: (-item[1], item[0].lower())):
        role_counts = {role: live_role_by_body[body].get(role, 0) for role in ROLE_ORDER if role != "archive-backed"}
        dominant_role = max(role_counts.items(), key=lambda item: (item[1], item[0]))[0]
        body_profiles.append(
            {
                "body": body,
                "records": total,
                "share_of_indexed_percent": pct(total, len(live_records)),
                "dominant_role": dominant_role,
                "role_counts": role_counts,
            }
        )

    role_profiles = []
    for role in ROLE_ORDER:
        if role == "archive-backed":
            role_profiles.append(
                {
                    "role": role,
                    "count": len(archive_records),
                    "share_of_indexed_percent": pct(len(archive_records), len(live_records)),
                    "top_bodies": top_entries(archive_top_levels),
                    "scope": "archive",
                }
            )
            continue

        top_bodies = Counter({body: counts.get(role, 0) for body, counts in live_role_by_body.items() if counts.get(role, 0) > 0})
        role_profiles.append(
            {
                "role": role,
                "count": live_role_counts.get(role, 0),
                "share_of_live_percent": pct(live_role_counts.get(role, 0), len(live_records)),
                "top_bodies": top_entries(top_bodies),
                "scope": "live",
            }
        )

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-09.q06.runtime",
        "derivation_command": DERIVATION_COMMAND,
        "source_paths": {
            "corpus_atlas": str(CORPUS_ATLAS_PATH),
            "archive_atlas": str(ARCHIVE_ATLAS_PATH),
        },
        "source_timestamps": {
            "corpus_atlas": file_timestamp(CORPUS_ATLAS_PATH),
            "archive_atlas": file_timestamp(ARCHIVE_ATLAS_PATH),
        },
        "indexed_witness": len(live_records),
        "archive_witness": len(archive_records),
        "role_order": ROLE_ORDER,
        "classification_rules": {
            "vendor": list(VENDOR_MARKERS),
            "receipt": ["receipts folder", "receipt in filename"],
            "protocol": list(PROTOCOL_MARKERS),
            "ledger": list(LEDGER_MARKERS),
            "mirror": list(MIRROR_MARKERS),
            "generated": sorted(GENERATED_TOP_LEVELS) + list(GENERATED_MARKERS),
            "source": ["default fallback for live records not claimed by a more specific role"],
            "archive-backed": ["all records from archive_atlas.json"],
        },
        "roles": role_profiles,
        "body_profiles": body_profiles,
    }


def render_markdown(payload: dict) -> str:
    role_lines = []
    for role in payload["roles"]:
        share_key = "share_of_live_percent" if role["scope"] == "live" else "share_of_indexed_percent"
        share_label = "share of live indexed body" if role["scope"] == "live" else "archive mass relative to indexed live body"
        top_bodies = ", ".join(f"{item['name']} ({item['count']})" for item in role["top_bodies"][:3]) or "none"
        role_lines.append(
            f"- `{role['role']}`: `{role['count']}` records, `{role.get(share_key, 0)}`% {share_label}; top bodies: {top_bodies}"
        )

    body_lines = []
    for body in payload["body_profiles"][:12]:
        role_counts = ", ".join(
            f"{name}={count}"
            for name, count in body["role_counts"].items()
            if count > 0
        )
        body_lines.append(
            f"- `{body['body']}`: `{body['records']}` records, dominant role `{body['dominant_role']}`, role mix `{role_counts}`"
        )

    return f"""# Semantic Mass Ledger

Date: `{payload['generated_at'][:10]}`
Generated: `{payload['generated_at']}`
Verdict: `OK`

This surface classifies Athena by semantic role instead of raw file count alone.

## Witness Basis

- Indexed witness: `{payload['indexed_witness']}`
- Archive witness: `{payload['archive_witness']}`
- Derivation command: `{payload['derivation_command']}`

## Role Distribution

{chr(10).join(role_lines)}

## Major Body Profiles

{chr(10).join(body_lines)}

## Interpretation

- raw size alone overstates the centrality of generated operating shells
- receipts, ledgers, and protocols are real organism mass, but they should not be confused with first-order source matter
- archive-backed mass remains a separate semantic reservoir rather than live routed source
"""


def render_receipt(payload: dict) -> str:
    return f"""# Semantic Mass Ledger Receipt

- Generated: `{payload['generated_at']}`
- Quest: `Q06 Build A Semantic Mass Ledger`
- Verdict: `OK`
- Command: `{payload['derivation_command']}`

## Source Basis

- corpus atlas: `{payload['source_paths']['corpus_atlas']}` at `{payload['source_timestamps']['corpus_atlas']}`
- archive atlas: `{payload['source_paths']['archive_atlas']}` at `{payload['source_timestamps']['archive_atlas']}`

## Role Totals

{chr(10).join(f"- `{role['role']}`: `{role['count']}`" for role in payload['roles'])}

## Highest-Leverage Read

- the organism contains a large generated shell layer that should not automatically outrank source matter during prioritization
- archive-backed mass is still substantial and remains a distinct integration reservoir
- semantic weighting should now be used alongside raw file count in future guild and swarm syntheses
"""


def main() -> int:
    payload = derive_semantic_mass_ledger()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_MARKDOWN_PATH.write_text(render_markdown(payload), encoding="utf-8")
    OUTPUT_RECEIPT_PATH.write_text(render_receipt(payload), encoding="utf-8")
    print(f"Wrote semantic mass ledger json: {OUTPUT_JSON_PATH}")
    print(f"Wrote semantic mass ledger markdown: {OUTPUT_MARKDOWN_PATH}")
    print(f"Wrote semantic mass ledger receipt: {OUTPUT_RECEIPT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
