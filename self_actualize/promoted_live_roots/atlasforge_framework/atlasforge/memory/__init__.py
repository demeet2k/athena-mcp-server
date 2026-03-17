"""AtlasForge Memory Bank.

This subpackage turns AtlasForge into a *practical* memory bank for mathematical
work: you can persist short notes, longer derivations, and links to recipes/
proof packs.

The assistant itself cannot persist memory across chats, but this store can.
"""

from atlasforge.memory.entry import MemoryEntry
from atlasforge.memory.knowledge import KnowledgeKind, KnowledgeRecord
from atlasforge.memory.addressing import normalize_address, parse_crystal_address_string
from atlasforge.memory.index import MemoryIndex, MemoryIndexHit
from atlasforge.memory.graph import GraphStore, GraphEdge
from atlasforge.memory.session import SessionRecord, SessionStore
from atlasforge.memory.store import MemoryStore

__all__ = [
    "MemoryEntry",
    "KnowledgeKind",
    "KnowledgeRecord",
    "normalize_address",
    "parse_crystal_address_string",
    "MemoryIndex",
    "MemoryIndexHit",
    "GraphStore",
    "GraphEdge",
    "SessionRecord",
    "SessionStore",
    "MemoryStore",
]
