from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .canonical import canonical_json_bytes
from .hashing import hash_bytes

@dataclass
class ExtractionManifest:
    manifest_id: str
    chapter: int
    tiles: List[Dict[str, Any]] = field(default_factory=list)  # [{address, tile_hash, tags...}]
    deps: List[str] = field(default_factory=list)

    def add_tile(self, address: str, tile_hash: str, tags: Optional[Dict[str, Any]] = None) -> None:
        if tags is None:
            tags = {}
        self.tiles.append({"address": address, "tile_hash": tile_hash, "tags": tags})

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "manifest_id": self.manifest_id,
            "chapter": self.chapter,
            "tiles": sorted(self.tiles, key=lambda x: x["address"]),
            "deps": sorted(self.deps),
        }

    def hash(self) -> str:
        return hash_bytes(canonical_json_bytes(self.to_canonical_dict()))
