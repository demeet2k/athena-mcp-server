"""
ATHENA OS - Memory Module
=========================
Hierarchical memory system based on ontological layers.

Components:
- hierarchy: Four-layer memory (ETERNAL, ESSENTIAL, ACCIDENTAL, POTENTIAL)
"""

from .hierarchy import (
    MemoryLayer,
    MemoryCell,
    MemorySegment,
    MemoryManager,
    copy_between_layers,
)

__all__ = [
    'MemoryLayer',
    'MemoryCell',
    'MemorySegment',
    'MemoryManager',
    'copy_between_layers',
]
