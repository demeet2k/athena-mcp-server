"""
storage -- Persistent storage subsystem for the Athena Process Language Compiler.

Modules:
    gawm_writer : Write artifacts to the GLOBAL_ATHENA directory structure.
    atlaspack   : AtlasPack bundle writer (atoms.jsonl + edges.jsonl + manifest.json).
    registry    : Registry for tracking compiled objects by content hash.
"""

from athena_process_compiler.storage.registry import Registry
from athena_process_compiler.storage.atlaspack import AtlasPackWriter, AtlasPackReader

__all__ = ["Registry", "AtlasPackWriter", "AtlasPackReader"]
