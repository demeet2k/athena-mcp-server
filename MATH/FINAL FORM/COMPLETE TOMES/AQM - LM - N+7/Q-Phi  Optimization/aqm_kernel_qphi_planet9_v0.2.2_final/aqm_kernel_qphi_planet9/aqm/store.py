from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .canonical import canonical_json_bytes
from .hashing import hash_bytes
from .kernel import KernelObject

class StoreError(RuntimeError):
    pass

@dataclass
class StoredBlob:
    obj_hash: str
    data: bytes

class MerkleStore:
    """Content-addressed store for KernelObjects.

    - Canonical serialization => hash => filename
    - Dependencies are explicit hashes stored in KernelObject.deps
    """

    def __init__(self, root_dir: Optional[str] = None) -> None:
        self._mem: Dict[str, bytes] = {}
        self.root_dir = root_dir
        if self.root_dir:
            os.makedirs(self.root_dir, exist_ok=True)

    def put(self, obj: KernelObject) -> str:
        data = obj.canonical_bytes()
        h = hash_bytes(data)
        self._mem[h] = data
        if self.root_dir:
            path = os.path.join(self.root_dir, f"{h}.json")
            if not os.path.exists(path):
                with open(path, "wb") as f:
                    f.write(data)
        return h

    def get_bytes(self, h: str) -> bytes:
        if h in self._mem:
            return self._mem[h]
        if self.root_dir:
            path = os.path.join(self.root_dir, f"{h}.json")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    data = f.read()
                # cache in memory
                self._mem[h] = data
                return data
        raise StoreError(f"Unknown hash: {h}")

    def has(self, h: str) -> bool:
        if h in self._mem:
            return True
        if self.root_dir:
            path = os.path.join(self.root_dir, f"{h}.json")
            return os.path.exists(path)
        return False

    def closure(self, root_hash: str) -> List[str]:
        """Return the transitive dependency closure (including root) as a stable list."""
        visited: Set[str] = set()
        order: List[str] = []

        def visit(h: str) -> None:
            if h in visited:
                return
            visited.add(h)
            data = self.get_bytes(h)
            obj = self._unsafe_decode_minimal(data)
            for dep in obj.get("deps", []):
                visit(dep)
            order.append(h)

        visit(root_hash)
        return order

    def _unsafe_decode_minimal(self, data: bytes) -> Dict:
        # Minimal JSON decode for closure. Canonical bytes are JSON.
        import json
        return json.loads(data.decode("utf-8"))

    def verify_hash(self, h: str) -> bool:
        data = self.get_bytes(h)
        return hash_bytes(data) == h
