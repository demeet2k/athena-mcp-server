from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .canonical import canonical_json_bytes
from .hashing import hash_bytes

@dataclass(frozen=True, slots=True)
class LedgerEvent:
    seq: int
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {"seq": self.seq, "event_type": self.event_type, "data": self.data}

@dataclass
class Ledger:
    events: List[LedgerEvent] = field(default_factory=list)

    def append(self, event_type: str, data: Optional[Dict[str, Any]] = None) -> None:
        if data is None:
            data = {}
        seq = len(self.events) + 1
        self.events.append(LedgerEvent(seq=seq, event_type=event_type, data=data))

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {"events": [e.to_canonical_dict() for e in self.events]}

    def hash(self) -> str:
        return hash_bytes(canonical_json_bytes(self.to_canonical_dict()))

    def anchor(self) -> Dict[str, Any]:
        return {"ledger_hash": self.hash(), "num_events": len(self.events)}
