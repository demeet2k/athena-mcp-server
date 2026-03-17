"""
atlaspack.py -- AtlasPack bundle writer for the Athena Process Language Compiler.

An AtlasPack is a self-contained bundle of compiled artifacts stored as
three files inside a pack directory:

    <pack_dir>/
        atoms.jsonl    -- one JSON object per line; each atom is a token, IR,
                          or render artifact
        edges.jsonl    -- one JSON object per line; typed edges linking atoms
                          (REF, EQUIV, DUAL, MIGRATE, PROOF)
        manifest.json  -- pack-level metadata, counts, and integrity fingerprint

Edge kinds:
    REF     -- an atom references another (e.g. IR -> source token)
    EQUIV   -- two atoms are semantically equivalent across lenses
    DUAL    -- two atoms form an alchemical dual pair (e.g. fire <-> water)
    MIGRATE -- an atom was tunnelled from another project/pack
    PROOF   -- a verification bundle proves an IR node

AtlasPacks are written to GAWM_PACKS (GLOBAL_ATHENA/02_PACKS/).

Usage:
    >>> from athena_process_compiler.storage.atlaspack import AtlasPackWriter, make_atom, make_edge
    >>> writer = AtlasPackWriter("my_pack")
    >>> writer.add_atom(make_atom("tok-001", "operator_ir", ir.to_dict()))
    >>> writer.add_edge(make_edge("tok-001", "tok-002", "REF"))
    >>> pack_dir = writer.flush()
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Literal

from athena_process_compiler.schemas.tokens import RawToken, ParseCandidate, ParsedToken, Truth
from athena_process_compiler.schemas.ir import OperatorIR
from athena_process_compiler.schemas.artifacts import NativeRender, VerificationBundle
from athena_process_compiler.config import (
    GAWM_PACKS,
    HASH_ALGORITHM,
    JSON_INDENT,
    JSON_ENSURE_ASCII,
    ensure_gawm_dirs,
)

# ---------------------------------------------------------------------------
# Edge kind enumeration
# ---------------------------------------------------------------------------

EdgeKind = Literal["REF", "EQUIV", "DUAL", "MIGRATE", "PROOF"]

VALID_EDGE_KINDS: frozenset[str] = frozenset({"REF", "EQUIV", "DUAL", "MIGRATE", "PROOF"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_bytes(data: bytes) -> str:
    """Compute a content hash from raw bytes."""
    return hashlib.new(HASH_ALGORITHM, data).hexdigest()


def _hash_line(line: str) -> str:
    """Hash a single JSONL line for integrity checking."""
    return _hash_bytes(line.encode("utf-8"))


def _hash_file(path: Path) -> str:
    """Compute the content hash of an entire file."""
    h = hashlib.new(HASH_ALGORITHM)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _canonical_json(payload: dict[str, Any]) -> str:
    """Produce a deterministic canonical JSON string for fingerprinting."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


# ---------------------------------------------------------------------------
# Atom and Edge builders
# ---------------------------------------------------------------------------

def make_atom(
    atom_id: str,
    kind: str,
    payload: dict[str, Any],
    *,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create an atom record for inclusion in atoms.jsonl.

    Each atom represents a single artifact: a RawToken, OperatorIR node,
    NativeRender, or VerificationBundle.

    Args:
        atom_id: Unique identifier for this atom (typically a content hash
                 or token_id).
        kind:    Atom type. One of ``"raw_token"``, ``"operator_ir"``,
                 ``"native_render"``, ``"verification_bundle"``, or a
                 custom type.
        payload: The artifact data as a JSON-serialisable dict.
        tags:    Optional classification tags (e.g. element, corridor).

    Returns:
        A dict ready to be serialised as a JSONL line.
    """
    fp = _hash_bytes(_canonical_json(payload).encode("utf-8"))
    return {
        "atom_id": atom_id,
        "kind": kind,
        "fingerprint": fp,
        "tags": tags or [],
        "payload": payload,
    }


def make_atom_from_ir(ir: OperatorIR) -> dict[str, Any]:
    """Convenience: create an atom directly from an OperatorIR node.

    Uses the token_id as atom_id and populates tags from element and
    corridor information.
    """
    tags = [ir.element, ir.lens, f"level:{ir.level}"]
    tags.extend(ir.corridor_tags)
    return make_atom(
        atom_id=ir.token_id,
        kind="operator_ir",
        payload=ir.to_dict(),
        tags=tags,
    )


def make_atom_from_render(render: NativeRender, ir_id: str) -> dict[str, Any]:
    """Convenience: create an atom from a NativeRender.

    Args:
        render: The NativeRender to wrap.
        ir_id:  The token_id of the OperatorIR this render belongs to.
    """
    atom_id = f"{ir_id}:render:{render.backend}"
    return make_atom(
        atom_id=atom_id,
        kind="native_render",
        payload=render.to_dict(),
        tags=[render.backend, render.status],
    )


def make_atom_from_verification(vb: VerificationBundle) -> dict[str, Any]:
    """Convenience: create an atom from a VerificationBundle."""
    return make_atom(
        atom_id=f"{vb.ir_id}:verification",
        kind="verification_bundle",
        payload=vb.to_dict(),
        tags=[vb.status],
    )


def make_edge(
    source_id: str,
    target_id: str,
    edge_kind: str,
    *,
    weight: float = 1.0,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create an edge record for inclusion in edges.jsonl.

    Args:
        source_id: atom_id of the source node.
        target_id: atom_id of the target node.
        edge_kind: Relationship type. Should be one of the VALID_EDGE_KINDS:
                   ``"REF"``, ``"EQUIV"``, ``"DUAL"``, ``"MIGRATE"``, ``"PROOF"``.
        weight:    Edge weight in [0.0, 1.0].
        metadata:  Optional edge metadata.

    Returns:
        A dict ready to be serialised as a JSONL line.

    Raises:
        ValueError: If edge_kind is not in VALID_EDGE_KINDS.
    """
    if edge_kind not in VALID_EDGE_KINDS:
        raise ValueError(
            f"Invalid edge_kind {edge_kind!r}. "
            f"Must be one of: {sorted(VALID_EDGE_KINDS)}"
        )
    return {
        "source_id": source_id,
        "target_id": target_id,
        "edge_kind": edge_kind,
        "weight": weight,
        "metadata": metadata or {},
    }


# ---------------------------------------------------------------------------
# AtlasPack writer
# ---------------------------------------------------------------------------

class AtlasPackWriter:
    """Accumulates atoms and edges, then flushes them as an AtlasPack bundle.

    Usage::

        writer = AtlasPackWriter("my_pack")
        writer.add_atom(make_atom("tok-001", "operator_ir", ir.to_dict()))
        writer.add_edge(make_edge("tok-001", "tok-002", "REF"))
        pack_dir = writer.flush()
    """

    def __init__(self, pack_name: str, *, base_dir: Path | None = None) -> None:
        """Initialise the writer.

        Args:
            pack_name: Human-readable name for the pack (used as directory name).
            base_dir:  Override for GAWM_PACKS (useful in tests).
        """
        self.pack_name = pack_name
        self.base_dir = base_dir or GAWM_PACKS
        self._atoms: list[dict[str, Any]] = []
        self._edges: list[dict[str, Any]] = []

    # -- accumulation -------------------------------------------------------

    def add_atom(self, atom: dict[str, Any]) -> None:
        """Append an atom record to the pack."""
        self._atoms.append(atom)

    def add_atoms(self, atoms: list[dict[str, Any]]) -> None:
        """Append multiple atom records to the pack."""
        self._atoms.extend(atoms)

    def add_edge(self, edge: dict[str, Any]) -> None:
        """Append an edge record to the pack."""
        self._edges.append(edge)

    def add_edges(self, edges: list[dict[str, Any]]) -> None:
        """Append multiple edge records to the pack."""
        self._edges.extend(edges)

    def add_ir_chain(
        self,
        ir_nodes: list[OperatorIR],
        renders: dict[str, list[NativeRender]] | None = None,
        verifications: list[VerificationBundle] | None = None,
    ) -> None:
        """Add a full IR chain with optional renders and verifications.

        Automatically creates atoms for each IR node, sequential REF edges,
        render atoms with REF edges, and verification atoms with PROOF edges.

        Args:
            ir_nodes:       Ordered list of OperatorIR nodes.
            renders:        Optional dict mapping backend names to render lists.
            verifications:  Optional list of VerificationBundles.
        """
        renders = renders or {}
        verifications = verifications or []

        # Add IR atoms and sequential edges
        for i, ir in enumerate(ir_nodes):
            self.add_atom(make_atom_from_ir(ir))
            if i > 0:
                self.add_edge(make_edge(
                    ir_nodes[i - 1].token_id, ir.token_id, "REF",
                    metadata={"relation": "sequential"},
                ))

        # Add render atoms and edges
        for backend, render_list in renders.items():
            for render in render_list:
                atom = make_atom_from_render(render, render.backend)
                self.add_atom(atom)
                # Find matching IR by ir_id if possible
                for ir in ir_nodes:
                    self.add_edge(make_edge(
                        ir.token_id, atom["atom_id"], "REF",
                        metadata={"relation": "rendered_by", "backend": backend},
                    ))
                    break  # Link to first IR only (simplification)

        # Add verification atoms and proof edges
        for vb in verifications:
            atom = make_atom_from_verification(vb)
            self.add_atom(atom)
            self.add_edge(make_edge(
                vb.ir_id, atom["atom_id"], "PROOF",
                metadata={"consistency": vb.cross_backend_consistency},
            ))

    @property
    def atom_count(self) -> int:
        """Number of atoms accumulated so far."""
        return len(self._atoms)

    @property
    def edge_count(self) -> int:
        """Number of edges accumulated so far."""
        return len(self._edges)

    # -- flush --------------------------------------------------------------

    def flush(self) -> Path:
        """Write the accumulated atoms and edges to disk as an AtlasPack.

        Creates:
            ``<base_dir>/<pack_name>/atoms.jsonl``
            ``<base_dir>/<pack_name>/edges.jsonl``
            ``<base_dir>/<pack_name>/manifest.json``

        Returns:
            Path to the pack directory.
        """
        ensure_gawm_dirs()
        pack_dir = self.base_dir / self.pack_name
        pack_dir.mkdir(parents=True, exist_ok=True)

        atoms_path = pack_dir / "atoms.jsonl"
        edges_path = pack_dir / "edges.jsonl"
        manifest_path = pack_dir / "manifest.json"

        # Write atoms.jsonl -- one JSON object per line
        with open(atoms_path, "w", encoding="utf-8") as f:
            for atom in self._atoms:
                f.write(json.dumps(atom, sort_keys=True, ensure_ascii=False))
                f.write("\n")

        # Write edges.jsonl -- one JSON object per line
        with open(edges_path, "w", encoding="utf-8") as f:
            for edge in self._edges:
                f.write(json.dumps(edge, sort_keys=True, ensure_ascii=False))
                f.write("\n")

        # Compute file hashes for integrity verification
        atoms_hash = _hash_file(atoms_path)
        edges_hash = _hash_file(edges_path)

        # Compute pack-level fingerprint from both file hashes
        pack_fingerprint = _hash_bytes(
            f"{atoms_hash}:{edges_hash}".encode("utf-8")
        )

        # Collect atom kinds for the manifest
        kind_counts: dict[str, int] = {}
        for atom in self._atoms:
            k = atom.get("kind", "unknown")
            kind_counts[k] = kind_counts.get(k, 0) + 1

        edge_kind_counts: dict[str, int] = {}
        for edge in self._edges:
            ek = edge.get("edge_kind", "unknown")
            edge_kind_counts[ek] = edge_kind_counts.get(ek, 0) + 1

        # Write manifest.json
        manifest: dict[str, Any] = {
            "pack_name": self.pack_name,
            "fingerprint": pack_fingerprint,
            "atom_count": len(self._atoms),
            "edge_count": len(self._edges),
            "atom_kinds": kind_counts,
            "edge_kinds": edge_kind_counts,
            "files": {
                "atoms.jsonl": {"hash": atoms_hash, "lines": len(self._atoms)},
                "edges.jsonl": {"hash": edges_hash, "lines": len(self._edges)},
            },
            "hash_algorithm": HASH_ALGORITHM,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=JSON_INDENT, ensure_ascii=JSON_ENSURE_ASCII),
            encoding="utf-8",
        )

        return pack_dir


# ---------------------------------------------------------------------------
# AtlasPack reader
# ---------------------------------------------------------------------------

class AtlasPackReader:
    """Read and query an AtlasPack bundle from disk.

    Usage::

        reader = AtlasPackReader(Path("path/to/pack"))
        atoms = reader.atoms()
        edges = reader.edges()
    """

    def __init__(self, pack_dir: Path) -> None:
        """Initialise the reader.

        Args:
            pack_dir: Path to the AtlasPack directory.
        """
        self.pack_dir = pack_dir

    def manifest(self) -> dict[str, Any]:
        """Load and return the pack manifest."""
        path = self.pack_dir / "manifest.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def atoms(self) -> list[dict[str, Any]]:
        """Load all atoms from atoms.jsonl."""
        path = self.pack_dir / "atoms.jsonl"
        result: list[dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    result.append(json.loads(line))
        return result

    def edges(self) -> list[dict[str, Any]]:
        """Load all edges from edges.jsonl."""
        path = self.pack_dir / "edges.jsonl"
        result: list[dict[str, Any]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    result.append(json.loads(line))
        return result

    def atoms_by_kind(self, kind: str) -> list[dict[str, Any]]:
        """Return all atoms matching a given kind."""
        return [a for a in self.atoms() if a.get("kind") == kind]

    def edges_by_kind(self, edge_kind: str) -> list[dict[str, Any]]:
        """Return all edges matching a given edge_kind."""
        return [e for e in self.edges() if e.get("edge_kind") == edge_kind]


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_pack(pack_dir: Path) -> tuple[bool, list[str]]:
    """Verify the integrity of an existing AtlasPack on disk.

    Checks that atoms.jsonl and edges.jsonl match the hashes recorded
    in manifest.json.

    Args:
        pack_dir: Path to the AtlasPack directory.

    Returns:
        ``(ok, errors)`` where *ok* is True if all checks pass.
    """
    manifest_path = pack_dir / "manifest.json"
    errors: list[str] = []

    if not manifest_path.exists():
        return False, ["manifest.json not found"]

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for filename, info in manifest.get("files", {}).items():
        file_path = pack_dir / filename
        if not file_path.exists():
            errors.append(f"{filename} not found")
            continue
        actual_hash = _hash_file(file_path)
        if actual_hash != info["hash"]:
            errors.append(
                f"{filename} hash mismatch: "
                f"expected {info['hash'][:16]}..., got {actual_hash[:16]}..."
            )

    return len(errors) == 0, errors
