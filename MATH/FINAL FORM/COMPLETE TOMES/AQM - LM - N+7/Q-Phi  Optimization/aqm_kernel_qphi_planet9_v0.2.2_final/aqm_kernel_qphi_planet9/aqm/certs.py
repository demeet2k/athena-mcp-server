from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .canonical import canonical_json_bytes
from .hashing import hash_bytes

@dataclass(frozen=True, slots=True)
class Obligation:
    # A lightweight obligation record (e.g., "CPTP_VALID", "RN_ADMISSIBLE", etc.)
    obligation_id: str
    description: str
    deps: List[str] = field(default_factory=list)

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {"obligation_id": self.obligation_id, "description": self.description, "deps": self.deps}

@dataclass
class CertificateBundle:
    obligations: List[Obligation] = field(default_factory=list)
    witnesses: List[Dict[str, Any]] = field(default_factory=list)

    def add_obligation(self, obligation_id: str, description: str, deps: Optional[List[str]] = None) -> None:
        if deps is None:
            deps = []
        self.obligations.append(Obligation(obligation_id=obligation_id, description=description, deps=deps))

    def add_witness(self, witness: Dict[str, Any]) -> None:
        self.witnesses.append(witness)

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "obligations": [o.to_canonical_dict() for o in self.obligations],
            "witnesses": self.witnesses,
        }

    def hash(self) -> str:
        return hash_bytes(canonical_json_bytes(self.to_canonical_dict()))

    def summary(self) -> Dict[str, Any]:
        return {
            "cert_hash": self.hash(),
            "num_obligations": len(self.obligations),
            "num_witnesses": len(self.witnesses),
        }
