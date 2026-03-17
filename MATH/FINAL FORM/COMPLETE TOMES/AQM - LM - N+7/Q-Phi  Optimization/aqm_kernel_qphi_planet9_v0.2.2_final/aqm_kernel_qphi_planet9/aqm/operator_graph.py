from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .canonical import canonical_json_bytes
from .hashing import hash_bytes

@dataclass(frozen=True, slots=True)
class PortRef:
    node_id: str
    port: str

@dataclass
class OperatorNode:
    node_id: str
    op_card: str  # reference ID/name for OperatorCard
    inputs: Dict[str, PortRef] = field(default_factory=dict)
    params: Dict[str, Any] = field(default_factory=dict)

    def to_canonical_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "op_card": self.op_card,
            "inputs": {k: {"node_id": v.node_id, "port": v.port} for k, v in sorted(self.inputs.items())},
            "params": self.params,
        }

@dataclass
class OperatorGraph:
    nodes: List[OperatorNode] = field(default_factory=list)
    outputs: Dict[str, PortRef] = field(default_factory=dict)
    policy_id: str = "default"

    def canonicalize(self) -> None:
        # Deterministic topological-ish ordering by node_id
        self.nodes.sort(key=lambda n: n.node_id)
        self.outputs = dict(sorted(self.outputs.items()))

    def to_canonical_dict(self) -> Dict[str, Any]:
        self.canonicalize()
        return {
            "policy_id": self.policy_id,
            "nodes": [n.to_canonical_dict() for n in self.nodes],
            "outputs": {k: {"node_id": v.node_id, "port": v.port} for k, v in self.outputs.items()},
        }

    def hash(self) -> str:
        return hash_bytes(canonical_json_bytes(self.to_canonical_dict()))
