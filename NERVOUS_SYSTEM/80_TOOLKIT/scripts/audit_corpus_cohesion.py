from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path


WORKSPACE_ROOT = Path(r"C:\Users\dmitr\Documents\Athena Agent")
CODEX_ROOT = Path(r"C:\Users\dmitr\.codex")
OUTPUT_PATH = WORKSPACE_ROOT / "NERVOUS_SYSTEM" / "90_LEDGERS" / "audits" / "2026-03-12_corpus_cohesion_audit.json"
SCAN_ROOTS = [
    WORKSPACE_ROOT / "NERVOUS_SYSTEM",
    WORKSPACE_ROOT / "self_actualize" / "mycelium_brain",
    CODEX_ROOT / "skills",
]
FILE_GLOBS = ("*.md", "SKILL.md")
HISTORICAL_MARKERS = [
    "DEEPER CRYSTALIZATION\\_build\\nervous_system",
    "DEEPER CRYSTALIZATION/_build/nervous_system",
    "ACTIVE_NERVOUS_SYSTEM",
    "DEEPER_INTEGRATED_NEURAL_NETWORK",
    "DEEPER_INTEGRATED_NEURAL_NET_ATHENA",
    "mycelial_4d_cross_corpus/",
]
IGNORE_PREFIXES = ("http://", "https://", "```", "...", "--", "python ", "powershell ")
KNOWN_GATE_BLOCKERS = {
    "Trading Bot/credentials.json",
    "Trading Bot/token.json",
}
RELATIVE_ROOTS = {child.name for child in WORKSPACE_ROOT.iterdir()}
RELATIVE_ROOTS.update({"VOID_CH11.md", "MYCELIUM_TOME_PART1.md", "FULL_PROJECT_TESSERACT_SYNTHESIS_2026-03-11.md"})
CODE_SPAN_PATTERN = re.compile(r"`([^`\n]+)`")


def candidate_paths(text: str) -> list[str]:
    return [match.group(1).strip() for match in CODE_SPAN_PATTERN.finditer(text)]


def should_skip(token: str) -> bool:
    return (
        not token
        or any(token.startswith(prefix) for prefix in IGNORE_PREFIXES)
        or "..." in token
        or "/" not in token
        and "\\" not in token
    )


def resolve_reference(token: str) -> Path | None:
    normalized = token.strip().strip('"').strip("'")
    if should_skip(normalized):
        return None
    if normalized.startswith(str(WORKSPACE_ROOT)):
        return Path(normalized)
    if normalized.startswith(str(CODEX_ROOT)):
        return Path(normalized)
    if normalized.startswith(".codex/") or normalized.startswith(".codex\\"):
        return CODEX_ROOT / normalized.split(".", 1)[1].lstrip("/\\")
    first_segment = re.split(r"[\\/]", normalized, maxsplit=1)[0]
    if first_segment in RELATIVE_ROOTS:
        return WORKSPACE_ROOT / normalized.replace("/", "\\")
    return None


def is_gate_blocker_path(path: Path) -> bool:
    normalized = str(path).replace("/", "\\")
    return normalized.endswith(r"Trading Bot\credentials.json") or normalized.endswith(r"Trading Bot\token.json")


def scan_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    spans = candidate_paths(text)
    missing = []
    historical = []
    blockers = []
    for marker in HISTORICAL_MARKERS:
        if marker in text:
            historical.append(marker)
    for token in spans:
        if token in KNOWN_GATE_BLOCKERS:
            blockers.append(token)
            continue
        resolved = resolve_reference(token)
        if resolved is None:
            continue
        if is_gate_blocker_path(resolved):
            blockers.append(token)
            continue
        if not resolved.exists():
            missing.append(
                {
                    "token": token,
                    "resolved_path": str(resolved),
                }
            )
    return {
        "path": str(path),
        "code_span_count": len(spans),
        "missing_refs": missing,
        "gate_blockers": sorted(set(blockers)),
        "historical_markers": sorted(set(historical)),
    }


def main() -> None:
    records = []
    stats = defaultdict(int)
    skill_files_flagged = []
    doc_files_flagged = []

    for scan_root in SCAN_ROOTS:
        for pattern in FILE_GLOBS:
            for path in scan_root.rglob(pattern):
                if path.is_dir():
                    continue
                record = scan_file(path)
                records.append(record)
                stats["files_scanned"] += 1
                stats["code_spans_scanned"] += record["code_span_count"]
                stats["missing_ref_count"] += len(record["missing_refs"])
                stats["gate_blocker_count"] += len(record["gate_blockers"])
                stats["historical_marker_count"] += len(record["historical_markers"])
                if record["gate_blockers"]:
                    stats["gate_blocker_file_count"] += 1
                if record["missing_refs"] or record["historical_markers"]:
                    if str(path).startswith(str(CODEX_ROOT)):
                        skill_files_flagged.append(record["path"])
                    else:
                        doc_files_flagged.append(record["path"])

    records.sort(
        key=lambda item: (
            -(len(item["missing_refs"]) + len(item["historical_markers"]) + len(item["gate_blockers"])),
            item["path"],
        )
    )
    payload = {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "workspace_root": str(WORKSPACE_ROOT),
        "docs_gate": "BLOCKED",
        "stats": {
            **stats,
            "files_flagged": len(skill_files_flagged) + len(doc_files_flagged),
            "skill_files_flagged": len(set(skill_files_flagged)),
            "doc_files_flagged": len(set(doc_files_flagged)),
        },
        "top_flagged_files": records[:40],
        "skill_files_flagged": sorted(set(skill_files_flagged)),
        "doc_files_flagged": sorted(set(doc_files_flagged)),
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload["stats"], indent=2))


if __name__ == "__main__":
    main()
