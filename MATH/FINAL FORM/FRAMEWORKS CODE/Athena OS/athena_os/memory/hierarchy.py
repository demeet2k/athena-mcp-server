"""
ATHENA OS - Hierarchical Memory System
======================================
Four-layer memory architecture reflecting ontological status:

Layer 0: ETERNAL   - Immutable (Forms, axioms, universal constants)
Layer 1: ESSENTIAL - Write-once (Type definitions, species identities)
Layer 2: ACCIDENTAL- Mutable (Instance state, runtime variables)
Layer 3: POTENTIAL - Volatile (Unactualized possibilities, futures)

This hierarchy mirrors the Platonic/Aristotelian ontological structure.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set, Generic, TypeVar
from datetime import datetime
import hashlib
import copy

from .bit4 import BIT4, BIT4Word


# =============================================================================
# MEMORY LAYERS
# =============================================================================

class MemoryLayer(IntEnum):
    """Memory hierarchy layers from most to least permanent."""
    ETERNAL = 0      # Immutable - universal constants and forms
    ESSENTIAL = 1    # Write-once - type definitions and identities
    ACCIDENTAL = 2   # Mutable - instance state and variables
    POTENTIAL = 3    # Volatile - possibilities and futures
    
    @property
    def mutability(self) -> str:
        """Describe the mutability of this layer."""
        return {
            MemoryLayer.ETERNAL: "Immutable",
            MemoryLayer.ESSENTIAL: "Write-once",
            MemoryLayer.ACCIDENTAL: "Mutable",
            MemoryLayer.POTENTIAL: "Volatile"
        }[self]
    
    @property
    def ontological_status(self) -> str:
        """Describe what kind of things live at this layer."""
        return {
            MemoryLayer.ETERNAL: "Forms, axioms, universal constants",
            MemoryLayer.ESSENTIAL: "Type definitions, species identities",
            MemoryLayer.ACCIDENTAL: "Instance state, runtime variables",
            MemoryLayer.POTENTIAL: "Unactualized possibilities, futures"
        }[self]


# =============================================================================
# MEMORY CELL
# =============================================================================

T = TypeVar('T')

@dataclass
class MemoryCell(Generic[T]):
    """
    A single memory cell with metadata.
    
    Tracks:
    - Value and type
    - Creation and modification times
    - Access patterns
    - Integrity checksums
    """
    address: int
    layer: MemoryLayer
    value: Optional[T] = None
    type_tag: str = "unknown"
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    access_count: int = 0
    write_count: int = 0
    locked: bool = False
    checksum: Optional[str] = None
    
    def __post_init__(self):
        """Compute initial checksum."""
        self._update_checksum()
    
    def _update_checksum(self) -> None:
        """Update integrity checksum."""
        if self.value is not None:
            data = str(self.value).encode()
            self.checksum = hashlib.sha256(data).hexdigest()[:16]
        else:
            self.checksum = None
    
    def verify_integrity(self) -> bool:
        """Verify the checksum matches current value."""
        if self.value is None:
            return self.checksum is None
        data = str(self.value).encode()
        expected = hashlib.sha256(data).hexdigest()[:16]
        return self.checksum == expected
    
    def read(self) -> Optional[T]:
        """Read the cell value."""
        self.access_count += 1
        return self.value
    
    def write(self, value: T) -> bool:
        """
        Write to the cell. Returns False if write not allowed.
        
        Rules:
        - ETERNAL: Never writable after creation
        - ESSENTIAL: Writable only if currently None
        - ACCIDENTAL: Always writable (unless locked)
        - POTENTIAL: Always writable (unless locked)
        """
        if self.locked:
            return False
        
        if self.layer == MemoryLayer.ETERNAL:
            return False  # Never writable
        
        if self.layer == MemoryLayer.ESSENTIAL:
            if self.value is not None:
                return False  # Write-once
        
        self.value = value
        self.modified_at = datetime.now()
        self.write_count += 1
        self._update_checksum()
        return True
    
    def clear(self) -> bool:
        """Clear the cell. Only works for ACCIDENTAL and POTENTIAL."""
        if self.locked:
            return False
        if self.layer in (MemoryLayer.ETERNAL, MemoryLayer.ESSENTIAL):
            return False
        
        self.value = None
        self.modified_at = datetime.now()
        self._update_checksum()
        return True
    
    def lock(self) -> None:
        """Lock the cell against writes."""
        self.locked = True
    
    def unlock(self) -> bool:
        """Unlock the cell. Cannot unlock ETERNAL."""
        if self.layer == MemoryLayer.ETERNAL:
            return False
        self.locked = False
        return True
    
    def age(self) -> float:
        """Return age in seconds since creation."""
        return (datetime.now() - self.created_at).total_seconds()
    
    def __str__(self) -> str:
        lock_icon = "??" if self.locked else "  "
        val_str = str(self.value)[:20] if self.value else "∅"
        return f"[{self.address:04x}]{lock_icon} {self.layer.name:10} = {val_str}"


# =============================================================================
# MEMORY SEGMENT
# =============================================================================

@dataclass
class MemorySegment:
    """
    A contiguous segment of memory at a specific layer.
    
    Segments have:
    - Base address
    - Size (number of cells)
    - Layer assignment
    - Access permissions
    """
    base_address: int
    size: int
    layer: MemoryLayer
    name: str = ""
    cells: Dict[int, MemoryCell] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize cells for segment."""
        for offset in range(self.size):
            addr = self.base_address + offset
            self.cells[addr] = MemoryCell(
                address=addr,
                layer=self.layer
            )
    
    @property
    def end_address(self) -> int:
        """Return the end address (exclusive)."""
        return self.base_address + self.size
    
    def contains(self, address: int) -> bool:
        """Check if address is in this segment."""
        return self.base_address <= address < self.end_address
    
    def read(self, address: int) -> Optional[Any]:
        """Read from address in segment."""
        if not self.contains(address):
            raise ValueError(f"Address {address:04x} not in segment")
        return self.cells[address].read()
    
    def write(self, address: int, value: Any) -> bool:
        """Write to address in segment."""
        if not self.contains(address):
            raise ValueError(f"Address {address:04x} not in segment")
        return self.cells[address].write(value)
    
    def allocate(self, value: Any = None) -> Optional[int]:
        """Find first empty cell and write to it. Returns address or None."""
        for addr, cell in self.cells.items():
            if cell.value is None:
                if cell.write(value):
                    return addr
        return None
    
    def usage(self) -> Tuple[int, int]:
        """Return (used_cells, total_cells)."""
        used = sum(1 for c in self.cells.values() if c.value is not None)
        return (used, self.size)
    
    def __str__(self) -> str:
        used, total = self.usage()
        return f"Segment[{self.name}] @ {self.base_address:04x}-{self.end_address:04x} ({self.layer.name}) {used}/{total}"


# =============================================================================
# MEMORY MANAGER
# =============================================================================

class MemoryManager:
    """
    The complete ATHENA memory system.
    
    Manages four memory layers with proper isolation and access control.
    Implements the emanation flow from ETERNAL → POTENTIAL.
    """
    
    # Default segment sizes
    ETERNAL_SIZE = 256      # Constants
    ESSENTIAL_SIZE = 1024   # Types
    ACCIDENTAL_SIZE = 4096  # Variables
    POTENTIAL_SIZE = 8192   # Futures
    
    def __init__(self, 
                 eternal_size: int = ETERNAL_SIZE,
                 essential_size: int = ESSENTIAL_SIZE,
                 accidental_size: int = ACCIDENTAL_SIZE,
                 potential_size: int = POTENTIAL_SIZE):
        
        # Create segments at different base addresses
        base = 0x0000
        self.eternal = MemorySegment(
            base_address=base,
            size=eternal_size,
            layer=MemoryLayer.ETERNAL,
            name="eternal"
        )
        
        base += eternal_size
        self.essential = MemorySegment(
            base_address=base,
            size=essential_size,
            layer=MemoryLayer.ESSENTIAL,
            name="essential"
        )
        
        base += essential_size
        self.accidental = MemorySegment(
            base_address=base,
            size=accidental_size,
            layer=MemoryLayer.ACCIDENTAL,
            name="accidental"
        )
        
        base += accidental_size
        self.potential = MemorySegment(
            base_address=base,
            size=potential_size,
            layer=MemoryLayer.POTENTIAL,
            name="potential"
        )
        
        self._segments = [
            self.eternal, self.essential, 
            self.accidental, self.potential
        ]
        
        # Initialize eternal constants
        self._init_eternal_constants()
    
    def _init_eternal_constants(self) -> None:
        """Initialize the eternal memory with universal constants."""
        eternals = {
            0: ("PI", 3.14159265358979323846),
            1: ("E", 2.71828182845904523536),
            2: ("PHI", 1.61803398874989484820),  # Golden ratio
            3: ("SQRT2", 1.41421356237309504880),
            4: ("COMMA", 531441/524288),  # Pythagorean comma
            5: ("UNITY", 1),
            6: ("VOID", 0),
            7: ("N_REGISTERS", 22),
            8: ("N_GATES", 231),
            9: ("N_DAG_NODES", 10),
            10: ("FLUX_N1", 7),   # Flux quantum n₁
            11: ("FLUX_N2", 19),  # Flux quantum n₂
            12: ("WAVE_K1", 17),  # Dilaton wave number k
            13: ("WAVE_K2", 103), # Dilaton wave number k'
            14: ("DIM_CHECKSUM", 114),  # 19×6
            15: ("HAMMING_N", 31),
            16: ("HAMMING_K", 26),
        }
        
        for offset, (name, value) in eternals.items():
            addr = self.eternal.base_address + offset
            cell = self.eternal.cells[addr]
            # Directly set for eternal (bypassing write protection)
            cell.value = value
            cell.type_tag = name
            cell._update_checksum()
            cell.lock()  # Permanently locked
    
    def get_segment(self, address: int) -> Optional[MemorySegment]:
        """Find which segment contains an address."""
        for seg in self._segments:
            if seg.contains(address):
                return seg
        return None
    
    def get_layer(self, address: int) -> Optional[MemoryLayer]:
        """Get the layer for an address."""
        seg = self.get_segment(address)
        return seg.layer if seg else None
    
    def read(self, address: int) -> Optional[Any]:
        """Read from any layer."""
        seg = self.get_segment(address)
        if seg:
            return seg.read(address)
        raise ValueError(f"Invalid address: {address:04x}")
    
    def write(self, address: int, value: Any) -> bool:
        """Write to appropriate layer."""
        seg = self.get_segment(address)
        if seg:
            return seg.write(address, value)
        raise ValueError(f"Invalid address: {address:04x}")
    
    def allocate_eternal(self, name: str, value: Any) -> Optional[int]:
        """
        Allocate in eternal memory (during initialization only).
        This should only be used during system bootstrap.
        """
        for addr, cell in self.eternal.cells.items():
            if cell.value is None:
                cell.value = value
                cell.type_tag = name
                cell._update_checksum()
                cell.lock()
                return addr
        return None
    
    def allocate_essential(self, type_name: str, value: Any) -> Optional[int]:
        """Allocate a type definition (write-once)."""
        for addr, cell in self.essential.cells.items():
            if cell.value is None:
                if cell.write(value):
                    cell.type_tag = type_name
                    return addr
        return None
    
    def allocate_accidental(self, var_name: str, value: Any = None) -> Optional[int]:
        """Allocate a runtime variable."""
        for addr, cell in self.accidental.cells.items():
            if cell.value is None:
                cell.type_tag = var_name
                if value is not None:
                    cell.write(value)
                return addr
        return None
    
    def allocate_potential(self, future_name: str, value: Any = None) -> Optional[int]:
        """Allocate a potential/future value."""
        for addr, cell in self.potential.cells.items():
            if cell.value is None:
                cell.type_tag = future_name
                if value is not None:
                    cell.write(value)
                return addr
        return None
    
    def actualize(self, potential_addr: int, accidental_addr: int) -> bool:
        """
        Move a value from POTENTIAL to ACCIDENTAL.
        This represents the actualization of a possibility.
        """
        if self.get_layer(potential_addr) != MemoryLayer.POTENTIAL:
            return False
        if self.get_layer(accidental_addr) != MemoryLayer.ACCIDENTAL:
            return False
        
        value = self.read(potential_addr)
        if value is None:
            return False
        
        # Write to accidental
        if self.write(accidental_addr, value):
            # Clear potential
            self.potential.cells[potential_addr].clear()
            return True
        return False
    
    def emanate(self, eternal_addr: int) -> Optional[int]:
        """
        Create an essential type from an eternal form.
        Implements the Neoplatonic emanation: ETERNAL → ESSENTIAL.
        """
        if self.get_layer(eternal_addr) != MemoryLayer.ETERNAL:
            return None
        
        form = self.read(eternal_addr)
        if form is None:
            return None
        
        # Create essential instance
        cell = self.eternal.cells[eternal_addr]
        return self.allocate_essential(f"ema_{cell.type_tag}", copy.deepcopy(form))
    
    def instantiate(self, essential_addr: int) -> Optional[int]:
        """
        Create an accidental instance from an essential type.
        Implements: ESSENTIAL → ACCIDENTAL.
        """
        if self.get_layer(essential_addr) != MemoryLayer.ESSENTIAL:
            return None
        
        type_def = self.read(essential_addr)
        if type_def is None:
            return None
        
        cell = self.essential.cells[essential_addr]
        return self.allocate_accidental(f"inst_{cell.type_tag}", copy.deepcopy(type_def))
    
    def potentiate(self, accidental_addr: int) -> Optional[int]:
        """
        Create a potential from an accidental state.
        Implements: ACCIDENTAL → POTENTIAL (branching futures).
        """
        if self.get_layer(accidental_addr) != MemoryLayer.ACCIDENTAL:
            return None
        
        state = self.read(accidental_addr)
        cell = self.accidental.cells[accidental_addr]
        return self.allocate_potential(f"pot_{cell.type_tag}", copy.deepcopy(state))
    
    def usage_summary(self) -> Dict[str, Tuple[int, int]]:
        """Return usage for each layer."""
        return {
            seg.name: seg.usage() for seg in self._segments
        }
    
    def integrity_check(self) -> Dict[str, List[int]]:
        """Check integrity of all cells. Returns addresses of corrupt cells."""
        corrupt = {}
        for seg in self._segments:
            corrupt_addrs = []
            for addr, cell in seg.cells.items():
                if cell.value is not None and not cell.verify_integrity():
                    corrupt_addrs.append(addr)
            if corrupt_addrs:
                corrupt[seg.name] = corrupt_addrs
        return corrupt
    
    def gc_potential(self) -> int:
        """Garbage collect unused potentials. Returns count freed."""
        freed = 0
        for addr, cell in self.potential.cells.items():
            if cell.value is not None and cell.age() > 3600:  # Older than 1 hour
                cell.clear()
                freed += 1
        return freed
    
    def dump_layer(self, layer: MemoryLayer) -> str:
        """Dump contents of a layer."""
        seg = self._segments[layer.value]
        lines = [f"=== {layer.name} Memory ({seg.usage()[0]}/{seg.size} used) ==="]
        for addr, cell in seg.cells.items():
            if cell.value is not None:
                lines.append(f"  {cell}")
        return '\n'.join(lines)
    
    def __str__(self) -> str:
        lines = ["ATHENA Memory System:"]
        for seg in self._segments:
            used, total = seg.usage()
            pct = (used / total * 100) if total > 0 else 0
            lines.append(f"  {seg.layer.name:10} {used:5}/{total:5} ({pct:5.1f}%)")
        return '\n'.join(lines)


# =============================================================================
# MEMORY OPERATIONS
# =============================================================================

def copy_between_layers(mm: MemoryManager, 
                        src_addr: int, 
                        dst_layer: MemoryLayer) -> Optional[int]:
    """
    Copy value from one address to a new allocation in another layer.
    
    Only allows "downward" copies (toward POTENTIAL) in normal operation.
    """
    src_layer = mm.get_layer(src_addr)
    if src_layer is None:
        return None
    
    # Normally only allow downward flow
    if dst_layer.value < src_layer.value:
        return None  # Can't copy "upward" in the hierarchy
    
    value = mm.read(src_addr)
    if value is None:
        return None
    
    # Allocate in destination layer
    if dst_layer == MemoryLayer.ESSENTIAL:
        return mm.allocate_essential("copy", value)
    elif dst_layer == MemoryLayer.ACCIDENTAL:
        return mm.allocate_accidental("copy", value)
    elif dst_layer == MemoryLayer.POTENTIAL:
        return mm.allocate_potential("copy", value)
    
    return None


# =============================================================================
# VALIDATION
# =============================================================================

def validate_memory_hierarchy() -> bool:
    """Validate memory system properties."""
    mm = MemoryManager(
        eternal_size=16,
        essential_size=32,
        accidental_size=64,
        potential_size=128
    )
    
    # Eternal is read-only
    eternal_addr = mm.eternal.base_address
    assert not mm.write(eternal_addr, 999), "Eternal should be immutable"
    
    # Essential is write-once
    ess_addr = mm.allocate_essential("test_type", {"x": 1})
    assert ess_addr is not None, "Should allocate essential"
    assert not mm.write(ess_addr, {"x": 2}), "Essential should be write-once"
    
    # Accidental is mutable
    acc_addr = mm.allocate_accidental("test_var", 100)
    assert acc_addr is not None
    assert mm.write(acc_addr, 200), "Accidental should be mutable"
    assert mm.read(acc_addr) == 200
    
    # Potential is mutable
    pot_addr = mm.allocate_potential("test_future", "maybe")
    assert pot_addr is not None
    assert mm.write(pot_addr, "definitely"), "Potential should be mutable"
    
    # Emanation flow works
    ema_addr = mm.emanate(eternal_addr)
    assert ema_addr is not None, "Emanation should work"
    
    return True


if __name__ == "__main__":
    print("Validating memory hierarchy...")
    assert validate_memory_hierarchy()
    print("✓ Memory hierarchy validated")
    
    # Demo
    print("\n=== Memory System Demo ===")
    mm = MemoryManager()
    
    # Show eternal constants
    print(mm.dump_layer(MemoryLayer.ETERNAL))
    
    # Allocate and use
    type_addr = mm.allocate_essential("Point", {"x": 0, "y": 0})
    print(f"\nAllocated type at {type_addr:04x}")
    
    inst_addr = mm.instantiate(type_addr)
    print(f"Instantiated at {inst_addr:04x}")
    mm.write(inst_addr, {"x": 10, "y": 20})
    print(f"Updated: {mm.read(inst_addr)}")
    
    future_addr = mm.potentiate(inst_addr)
    print(f"Potentiated at {future_addr:04x}")
    
    # Summary
    print("\n" + str(mm))
