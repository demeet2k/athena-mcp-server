from __future__ import annotations

import hashlib
from typing import Literal

HashAlg = Literal["sha256", "blake2b"]

def hash_bytes(data: bytes, alg: HashAlg = "sha256") -> str:
    if alg == "sha256":
        return hashlib.sha256(data).hexdigest()
    if alg == "blake2b":
        return hashlib.blake2b(data).hexdigest()
    raise ValueError(f"Unsupported hash alg: {alg}")
