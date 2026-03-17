from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .liminal_coord import load_config


def _registry_root() -> Path:
    return Path(load_config().registry_root)


def _receipts_root() -> Path:
    return Path(load_config().receipts_root)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def event_ledger_path() -> Path:
    return _registry_root() / "event_ledger.jsonl"


def claim_ledger_path() -> Path:
    return _registry_root() / "claim_ledger.jsonl"


def route_receipts_path() -> Path:
    return _registry_root() / "route_receipts.jsonl"


def temple_fronts_path() -> Path:
    return _registry_root() / "temple_fronts.jsonl"


def hall_fronts_path() -> Path:
    return _registry_root() / "hall_fronts.jsonl"


def front_memory_path() -> Path:
    return _registry_root() / "front_memory_v1.json"


def promotion_receipts_path() -> Path:
    return _registry_root() / "promotion_receipts.jsonl"


def capillary_memory_path() -> Path:
    return _registry_root() / "capillary_memory_v1.json"


def install_receipt_path() -> Path:
    return _receipts_root() / "INSTALL_RECEIPT.md"


def blocked_docs_receipt_path() -> Path:
    return _receipts_root() / "BLOCKED_DOCS_RECEIPT.md"


def latency_receipt_path() -> Path:
    return _receipts_root() / "LATENCY_BENCHMARK_V1.json"
