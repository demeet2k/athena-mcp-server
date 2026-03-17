from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

from .canonical import canonical_json_bytes
from .hashing import hash_bytes
from .addressing import TileAddress

SCHEMA_VERSION = "0.1"

@dataclass
class KernelObject:
    kind: str
    schema_version: str = SCHEMA_VERSION
    seed: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)
    deps: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    cert: Optional[Dict[str, Any]] = None
    ledger: Optional[Dict[str, Any]] = None

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "schema_version": self.schema_version,
            "seed": self.seed,
            "meta": self.meta,
            "deps": self.deps,
            "payload": self.payload,
            "cert": self.cert,
            "ledger": self.ledger,
        }

    def canonical_bytes(self) -> bytes:
        return canonical_json_bytes(self.to_canonical_dict())

    def content_hash(self) -> str:
        return hash_bytes(self.canonical_bytes())

@dataclass
class Tile(KernelObject):
    address: TileAddress = field(default_factory=lambda: TileAddress.for_chapter(1,"S",1))
    # Required by the AQM "tile contract"
    output_types: List[str] = field(default_factory=lambda: ["ValueState","Jet","BranchState","LiminalState","FailType"])
    cert_hooks: List[str] = field(default_factory=list)
    ledger_hooks: List[str] = field(default_factory=list)
    escalation_policy: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.kind = "Tile"
        # Put address into meta for indexing
        self.meta = dict(self.meta)
        self.meta.setdefault("address", self.address.to_ascii())
        self.meta.setdefault("lens", self.address.lens)
        self.meta.setdefault("facet", self.address.facet)
        self.meta.setdefault("chapter", self.address.chapter)
        self.meta.setdefault("base4", self.address.digits4)

    def to_canonical_dict(self) -> Dict[str, Any]:
        d = super().to_canonical_dict()
        d.update({
            "address": self.address.to_ascii(),
            "output_types": self.output_types,
            "cert_hooks": self.cert_hooks,
            "ledger_hooks": self.ledger_hooks,
            "escalation_policy": self.escalation_policy,
        })
        return d

class Builder(Protocol):
    def build(self, seed: Dict[str, Any], meta: Dict[str, Any], store: "MerkleStore") -> KernelObject: ...

class BuilderRegistry:
    def __init__(self) -> None:
        self._builders: Dict[str, Builder] = {}

    def register(self, kind: str, builder: Builder) -> None:
        self._builders[kind] = builder

    def get(self, kind: str) -> Optional[Builder]:
        return self._builders.get(kind)
