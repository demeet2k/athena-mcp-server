from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SELF_ACTUALIZE_ROOT = WORKSPACE_ROOT / "self_actualize"
CORPUS_ATLAS_PATH = SELF_ACTUALIZE_ROOT / "corpus_atlas.json"
OUTPUT_JSON_PATH = SELF_ACTUALIZE_ROOT / "body_tensor.json"
ROOT_BODY_LIMIT = 20

MANUSCRIPT_EXTS = {".md", ".docx", ".pdf", ".txt"}
CODE_EXTS = {".py", ".cpp", ".cuda", ".cpu", ".ps1", ".sh", ".cmd", ".js", ".ts", ".tsx"}
DATA_EXTS = {".csv", ".json", ".yaml", ".yml", ".toml", ".tsv"}
MEDIA_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
ARCHIVE_EXTS = {".zip"}

ELEMENT_BY_BODY = {
    "Athena FLEET": "Fire",
    "Trading Bot": "Fire",
    "QSHRINK - ATHENA (internal use)": "Air",
    "DEEPER CRYSTALIZATION": "Water",
    "Voynich": "Water",
    "MATH": "Air",
    "self_actualize": "Earth",
    "NERVOUS_SYSTEM": "Earth",
    "ECOSYSTEM": "Earth",
    "NERUAL NETWORK": "Air",
    "I AM ATHENA": "Water",
    "Athenachka Collective Books": "Water",
    "CLEAN": "Water",
    "FRESH": "Fire",
    "GAMES": "Fire",
    "Quadrant Binary": "Air",
    "Stoicheia (Element Sudoku)": "Earth",
    "mycelial_unified_nervous_system_bundle": "Earth",
}

ROLE_BY_BODY = {
    "Athena FLEET": "fleet-tesseract expansion shell",
    "Trading Bot": "external bridge and transport body",
    "QSHRINK - ATHENA (internal use)": "compression and governance shell",
    "DEEPER CRYSTALIZATION": "integration compiler",
    "Voynich": "translation reservoir",
    "MATH": "theorem kernel",
    "self_actualize": "runtime waist",
    "NERVOUS_SYSTEM": "control and routing cortex",
    "ECOSYSTEM": "registry and protocol shell",
    "NERUAL NETWORK": "adaptive runtime lab",
    "I AM ATHENA": "identity manuscript shell",
    "Athenachka Collective Books": "publication shelf",
    "CLEAN": "manuscript staging shelf",
    "FRESH": "intake fringe",
    "GAMES": "simulation and mechanics lab",
    "Quadrant Binary": "ancestor address kernel",
    "Stoicheia (Element Sudoku)": "visual reserve and puzzle asset shelf",
    "mycelial_unified_nervous_system_bundle": "compiled bundle shelf",
}

BUCKET_LABELS = {
    "manuscript": "manuscript",
    "code": "code",
    "data": "data",
    "media": "media",
    "archive": "archive",
    "other": "other",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_timestamp(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def load_atlas() -> dict:
    return json.loads(CORPUS_ATLAS_PATH.read_text(encoding="utf-8"))


def bucket_for_extension(extension: str) -> str:
    if extension in MANUSCRIPT_EXTS:
        return "manuscript"
    if extension in CODE_EXTS:
        return "code"
    if extension in DATA_EXTS:
        return "data"
    if extension in MEDIA_EXTS:
        return "media"
    if extension in ARCHIVE_EXTS:
        return "archive"
    return "other"


def is_bronze_body(name: str, count: int) -> bool:
    if count <= 1:
        return False
    if name.startswith("."):
        return False
    if Path(name).suffix:
        return False
    return True


def modality_verdict(bucket_counts: dict[str, int]) -> str:
    ranked = sorted(bucket_counts.items(), key=lambda item: (-item[1], item[0]))
    nonzero = [(name, count) for name, count in ranked if count > 0]
    if not nonzero:
        return "unclassified"
    lead_name, lead_count = nonzero[0]
    total = sum(bucket_counts.values()) or 1
    lead_share = lead_count / total
    if len(nonzero) == 1:
        return f"{BUCKET_LABELS[lead_name]} only"
    tail_name, tail_count = nonzero[1]
    tail_share = tail_count / total
    if lead_share >= 0.8 and tail_share < 0.15:
        return f"{BUCKET_LABELS[lead_name]} dominant"
    if lead_share >= 0.6:
        return f"{BUCKET_LABELS[lead_name]} dominant with secondary {BUCKET_LABELS[tail_name]} tail"
    return f"mixed {BUCKET_LABELS[lead_name]} and {BUCKET_LABELS[tail_name]}"


def top_extensions(extension_counts: Counter[str], limit: int = 4) -> list[dict[str, int | str]]:
    items: list[dict[str, int | str]] = []
    for extension, count in extension_counts.most_common(limit):
        label = extension or "[noext]"
        items.append({"extension": label, "count": count})
    return items


def derive_body_tensor() -> dict:
    atlas = load_atlas()
    records = atlas.get("records", [])
    by_top_level: dict[str, Counter[str]] = defaultdict(Counter)
    bucket_totals: dict[str, Counter[str]] = defaultdict(Counter)

    for record in records:
        top_level = record.get("top_level") or "<unknown>"
        extension = (record.get("extension") or "").lower()
        by_top_level[top_level][extension] += 1
        bucket_totals[top_level][bucket_for_extension(extension)] += 1

    counts = {name: sum(ext_counts.values()) for name, ext_counts in by_top_level.items()}
    bronze_names = [
        name
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))
        if is_bronze_body(name, count)
    ][:ROOT_BODY_LIMIT]

    bronze_bodies = []
    element_totals: Counter[str] = Counter()
    for name in bronze_names:
        total = counts[name]
        bucket_counts = {
            "manuscript": bucket_totals[name].get("manuscript", 0),
            "code": bucket_totals[name].get("code", 0),
            "data": bucket_totals[name].get("data", 0),
            "media": bucket_totals[name].get("media", 0),
            "archive": bucket_totals[name].get("archive", 0),
            "other": bucket_totals[name].get("other", 0),
        }
        macro_element = ELEMENT_BY_BODY.get(name, "Unassigned")
        element_totals[macro_element] += total
        bronze_bodies.append(
            {
                "body": name,
                "records": total,
                "share_of_indexed": round(total / max(len(records), 1), 4),
                "macro_element": macro_element,
                "routing_role": ROLE_BY_BODY.get(name, "unclassified body"),
                "top_extensions": top_extensions(by_top_level[name]),
                "modality_buckets": bucket_counts,
                "dominant_bucket": max(bucket_counts.items(), key=lambda item: (item[1], item[0]))[0],
                "modality_verdict": modality_verdict(bucket_counts),
            }
        )

    satellites = [
        {"body": name, "records": count}
        for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))
        if name not in bronze_names
    ]

    return {
        "generated_at": utc_now(),
        "derivation_version": "2026-03-12.q15.reconciled",
        "source": str(CORPUS_ATLAS_PATH),
        "source_timestamp": file_timestamp(CORPUS_ATLAS_PATH),
        "indexed_witness": len(records),
        "bronze_selection_rule": f"Top {ROOT_BODY_LIMIT} non-dot, non-file-like top-level bodies with more than one indexed record.",
        "bronze_bodies": bronze_bodies,
        "element_totals": dict(sorted(element_totals.items())),
        "satellites": satellites,
    }


def main() -> int:
    payload = derive_body_tensor()
    OUTPUT_JSON_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Wrote body tensor: {OUTPUT_JSON_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
