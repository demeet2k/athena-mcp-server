"""
ATHENA OS - Crystal Addressing System
=====================================
The Fractal Crystal addressing scheme for holographic storage.

4^4 Crystal Structure:
- 4 Sectors (Earth/Water/Fire/Air = Square/Flower/Cloud/Fractal)
- 4 Cells per sector (Chapter groupings)
- 4 Roles per cell (Atoms/Rotations/Shadows/Patches)
- 4 Artifacts per role

Total: 256 addressable nodes in the crystal.

Address format: ⟨sector:cell:role:artifact⟩ = ⟨S:C:R:A⟩₄

Zero Point (Z): The distinguished basepoint where all four sectors overlap.
"""

from __future__ import annotations
from enum import IntEnum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable
import hashlib
import math


# =============================================================================
# SECTORS (THE FOUR POLES)
# =============================================================================

class Sector(IntEnum):
    """
    The Four Sectors of the Crystal Universe.
    
    Each sector represents a different way of viewing/processing reality:
    - EARTH/SQUARE: Structure, rigor, discrete geometry
    - WATER/FLOWER: Flow, semantics, spectral/wave
    - FIRE/CLOUD: Dynamics, probability, stochastic
    - AIR/FRACTAL: Recursion, synthesis, self-reference
    """
    EARTH = 0   # ■ Square - Structure & Rigor
    WATER = 1   # ❀ Flower - Flow & Semantics
    FIRE = 2    # ☁ Cloud - Dynamics & Probability
    AIR = 3     # ✶ Fractal - Recursion & Synthesis
    
    @property
    def symbol(self) -> str:
        """Unicode symbol for this sector."""
        return ['■', '❀', '☁', '✶'][self.value]
    
    @property
    def element(self) -> str:
        """Classical element correspondence."""
        return ['Earth', 'Water', 'Fire', 'Air'][self.value]
    
    @property
    def representation(self) -> str:
        """The representation lens name."""
        return ['Square', 'Flower', 'Cloud', 'Fractal'][self.value]
    
    @property
    def function(self) -> str:
        """Core function of this sector."""
        return {
            Sector.EARTH: "Structure & Rigor (discrete geometry, axioms)",
            Sector.WATER: "Flow & Semantics (definitions, records, memory)",
            Sector.FIRE: "Dynamics & Probability (entropy, unknown)",
            Sector.AIR: "Recursion & Synthesis (zero point, self-reference)"
        }[self]
    
    @property
    def mathematical_domain(self) -> str:
        """Mathematical domain of this sector."""
        return {
            Sector.EARTH: "Discrete Geometry / Number Theory",
            Sector.WATER: "Spectral Theory / Wave Mechanics",
            Sector.FIRE: "Stochastic Calculus / Thermodynamics",
            Sector.AIR: "Category Theory / Recursion Theory"
        }[self]
    
    @property
    def opposite(self) -> 'Sector':
        """Return the opposite sector (180°)."""
        return Sector((self.value + 2) % 4)
    
    @property
    def clockwise(self) -> 'Sector':
        """Return next sector clockwise (90°)."""
        return Sector((self.value + 1) % 4)
    
    @property
    def counterclockwise(self) -> 'Sector':
        """Return previous sector counter-clockwise (-90°)."""
        return Sector((self.value - 1) % 4)


# =============================================================================
# ROLES (WITHIN EACH CELL)
# =============================================================================

class Role(IntEnum):
    """
    The Four Roles within each cell.
    
    Each cell contains four types of artifacts:
    - ATOMS: Fundamental definitions, primitives
    - ROTATIONS: Transformations, operators
    - SHADOWS: Dual/conjugate structures, error modes
    - PATCHES: Corrections, stabilizers, completions
    """
    ATOMS = 0       # Fundamental definitions
    ROTATIONS = 1   # Transformations and operators
    SHADOWS = 2     # Duals and error modes
    PATCHES = 3     # Corrections and completions
    
    @property
    def description(self) -> str:
        return {
            Role.ATOMS: "Fundamental definitions (primitives, types)",
            Role.ROTATIONS: "Transformations (operators, morphisms)",
            Role.SHADOWS: "Dual structures (conjugates, error modes)",
            Role.PATCHES: "Corrections (stabilizers, completions)"
        }[self]


# =============================================================================
# CRYSTAL ADDRESS
# =============================================================================

@dataclass(frozen=True)
class CrystalAddress:
    """
    A 4-dimensional address in the crystal.
    
    Format: ⟨sector:cell:role:artifact⟩₄
    
    Each component is in range [0, 3], giving 4⁴ = 256 total addresses.
    """
    sector: int      # 0-3 (Earth/Water/Fire/Air)
    cell: int        # 0-3 (Chapter grouping)
    role: int        # 0-3 (Atoms/Rotations/Shadows/Patches)
    artifact: int    # 0-3 (Specific item)
    
    def __post_init__(self):
        """Validate components are in range."""
        for name, val in [('sector', self.sector), ('cell', self.cell),
                          ('role', self.role), ('artifact', self.artifact)]:
            if not 0 <= val <= 3:
                raise ValueError(f"{name} must be in [0,3], got {val}")
    
    @classmethod
    def from_linear(cls, index: int) -> 'CrystalAddress':
        """Create from linear index (0-255)."""
        if not 0 <= index < 256:
            raise ValueError(f"Index must be in [0,255], got {index}")
        artifact = index % 4
        role = (index // 4) % 4
        cell = (index // 16) % 4
        sector = (index // 64) % 4
        return cls(sector, cell, role, artifact)
    
    @classmethod
    def from_base4(cls, base4_str: str) -> 'CrystalAddress':
        """Create from base-4 string like '0123'."""
        if len(base4_str) != 4:
            raise ValueError("Base-4 string must be 4 digits")
        digits = [int(d) for d in base4_str]
        return cls(*digits)
    
    def to_linear(self) -> int:
        """Convert to linear index (0-255)."""
        return (self.sector * 64 + self.cell * 16 + 
                self.role * 4 + self.artifact)
    
    def to_base4(self) -> str:
        """Convert to base-4 string."""
        return f"{self.sector}{self.cell}{self.role}{self.artifact}"
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Return as tuple."""
        return (self.sector, self.cell, self.role, self.artifact)
    
    @property
    def sector_enum(self) -> Sector:
        """Get sector as enum."""
        return Sector(self.sector)
    
    @property
    def role_enum(self) -> Role:
        """Get role as enum."""
        return Role(self.role)
    
    def rotate_sector(self, steps: int = 1) -> 'CrystalAddress':
        """Rotate to a different sector."""
        new_sector = (self.sector + steps) % 4
        return CrystalAddress(new_sector, self.cell, self.role, self.artifact)
    
    def neighbor(self, dimension: int, direction: int = 1) -> Optional['CrystalAddress']:
        """
        Get neighbor address in a given dimension.
        dimension: 0=sector, 1=cell, 2=role, 3=artifact
        direction: +1 or -1
        """
        coords = list(self.to_tuple())
        new_val = coords[dimension] + direction
        if 0 <= new_val <= 3:
            coords[dimension] = new_val
            return CrystalAddress(*coords)
        return None
    
    def distance(self, other: 'CrystalAddress') -> int:
        """Manhattan distance to another address."""
        return (abs(self.sector - other.sector) + 
                abs(self.cell - other.cell) +
                abs(self.role - other.role) +
                abs(self.artifact - other.artifact))
    
    def __str__(self) -> str:
        s = Sector(self.sector)
        return f"⟨{s.symbol}{self.sector}:{self.cell}:{self.role}:{self.artifact}⟩"
    
    def __repr__(self) -> str:
        return f"CrystalAddress({self.sector},{self.cell},{self.role},{self.artifact})"


# =============================================================================
# ZERO POINT
# =============================================================================

class ZeroPoint:
    """
    The distinguished basepoint Z where all four sectors overlap.
    
    Properties of Z:
    1. Lies in the overlap of all four canonical charts
    2. Invariant under the system symmetry group
    3. Acts as topological obstruction (supports nontrivial holonomy)
    
    Computationally: Z is the fixed point of all rotation operators.
    """
    
    # The Zero Point is at the center of the crystal
    # Using fractional coordinates (1.5, 1.5, 1.5, 1.5) conceptually
    # But we represent it as the centroid of all 256 addresses
    
    @staticmethod
    def is_near_zero(addr: CrystalAddress, threshold: float = 1.0) -> bool:
        """Check if an address is near the zero point."""
        # Distance from center (1.5, 1.5, 1.5, 1.5)
        center = (1.5, 1.5, 1.5, 1.5)
        coords = addr.to_tuple()
        dist = sum((c - z) ** 2 for c, z in zip(coords, center)) ** 0.5
        return dist <= threshold
    
    @staticmethod
    def zero_point_projection(addr: CrystalAddress) -> Tuple[float, float, float, float]:
        """
        Project an address toward the zero point.
        Returns fractional coordinates of the projection.
        """
        center = (1.5, 1.5, 1.5, 1.5)
        coords = addr.to_tuple()
        
        # Move 50% toward center
        projected = tuple(c * 0.5 + z * 0.5 for c, z in zip(coords, center))
        return projected
    
    @staticmethod
    def in_all_sectors(addr: CrystalAddress) -> bool:
        """
        Check if an address conceptually belongs to all sectors.
        
        True only for addresses at cell/role/artifact = (1,1,1) or (2,2,2)
        which are at the "center" of their dimensions.
        """
        c, r, a = addr.cell, addr.role, addr.artifact
        return (c in (1, 2) and r in (1, 2) and a in (1, 2))
    
    @staticmethod
    def stabilizer_group_size() -> int:
        """
        Size of the stabilizer group S_Z that fixes the zero point.
        
        The group consists of rotations that permute sectors while
        preserving the zero point structure.
        """
        # The Klein-4 group stabilizes Z (4 elements)
        return 4


# =============================================================================
# CRYSTAL NODE (Content at an Address)
# =============================================================================

@dataclass
class CrystalNode:
    """
    A node in the crystal containing content at a specific address.
    """
    address: CrystalAddress
    content: Any = None
    content_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Connections to other nodes
    neighbors: List[CrystalAddress] = field(default_factory=list)
    
    # Conservation quantities
    kappa: float = 0.0  # Coherence/meaning intensity
    tension: float = 0.0  # Paradox tension
    
    def __post_init__(self):
        """Compute content hash if content is present."""
        if self.content is not None and self.content_hash is None:
            self.content_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of content."""
        content_bytes = str(self.content).encode('utf-8')
        return hashlib.sha256(content_bytes).hexdigest()[:16]
    
    def verify_integrity(self) -> bool:
        """Verify content hasn't been corrupted."""
        if self.content is None:
            return True
        return self._compute_hash() == self.content_hash
    
    def update_content(self, new_content: Any) -> None:
        """Update content and recompute hash."""
        self.content = new_content
        self.content_hash = self._compute_hash()
    
    def __str__(self) -> str:
        return f"Node{self.address}: κ={self.kappa:.2f}, τ={self.tension:.2f}"


# =============================================================================
# CRYSTAL LATTICE
# =============================================================================

class CrystalLattice:
    """
    The complete 256-node crystal lattice.
    
    Implements:
    - Addressed storage (Store-In, Not Out)
    - Sector rotation
    - Zero point operations
    - κ-conservation
    """
    
    def __init__(self):
        self.nodes: Dict[int, CrystalNode] = {}
        self._initialize_lattice()
        
        # Global conservation quantities
        self.total_kappa: float = 0.0
        self.total_tension: float = 0.0
    
    def _initialize_lattice(self) -> None:
        """Initialize all 256 nodes."""
        for i in range(256):
            addr = CrystalAddress.from_linear(i)
            self.nodes[i] = CrystalNode(address=addr)
    
    def get_node(self, addr: CrystalAddress) -> CrystalNode:
        """Get node at address."""
        return self.nodes[addr.to_linear()]
    
    def set_content(self, addr: CrystalAddress, content: Any,
                    kappa: float = 1.0, tension: float = 0.0) -> None:
        """Set content at an address."""
        node = self.get_node(addr)
        
        # Update conservation quantities
        self.total_kappa += kappa - node.kappa
        self.total_tension += tension - node.tension
        
        node.update_content(content)
        node.kappa = kappa
        node.tension = tension
    
    def get_content(self, addr: CrystalAddress) -> Any:
        """Get content at an address."""
        return self.get_node(addr).content
    
    def get_sector_nodes(self, sector: Sector) -> List[CrystalNode]:
        """Get all nodes in a sector."""
        return [self.nodes[i] for i in range(256) 
                if CrystalAddress.from_linear(i).sector == sector.value]
    
    def rotate_content(self, addr: CrystalAddress, steps: int = 1) -> CrystalAddress:
        """
        Rotate content to a different sector.
        Returns new address.
        """
        new_addr = addr.rotate_sector(steps)
        
        # Move content
        old_node = self.get_node(addr)
        new_node = self.get_node(new_addr)
        
        new_node.content = old_node.content
        new_node.content_hash = old_node.content_hash
        new_node.kappa = old_node.kappa
        new_node.tension = old_node.tension
        
        # Clear old node
        old_node.content = None
        old_node.content_hash = None
        old_node.kappa = 0.0
        old_node.tension = 0.0
        
        return new_addr
    
    def sector_summary(self, sector: Sector) -> Dict[str, Any]:
        """Get summary statistics for a sector."""
        nodes = self.get_sector_nodes(sector)
        occupied = [n for n in nodes if n.content is not None]
        
        return {
            'sector': sector.name,
            'total_nodes': len(nodes),
            'occupied': len(occupied),
            'total_kappa': sum(n.kappa for n in nodes),
            'total_tension': sum(n.tension for n in nodes)
        }
    
    def verify_conservation(self) -> Tuple[bool, Dict[str, float]]:
        """
        Verify conservation laws.
        
        Returns (is_valid, {quantity: computed_value}).
        """
        computed_kappa = sum(n.kappa for n in self.nodes.values())
        computed_tension = sum(n.tension for n in self.nodes.values())
        
        kappa_valid = abs(computed_kappa - self.total_kappa) < 1e-10
        tension_valid = abs(computed_tension - self.total_tension) < 1e-10
        
        return (kappa_valid and tension_valid, {
            'kappa': computed_kappa,
            'tension': computed_tension,
            'expected_kappa': self.total_kappa,
            'expected_tension': self.total_tension
        })
    
    def find_by_hash(self, content_hash: str) -> Optional[CrystalAddress]:
        """Find address by content hash."""
        for i, node in self.nodes.items():
            if node.content_hash == content_hash:
                return node.address
        return None
    
    def nearest_to_zero(self, occupied_only: bool = True) -> Optional[CrystalNode]:
        """Find the node nearest to the zero point."""
        center = (1.5, 1.5, 1.5, 1.5)
        
        best_node = None
        best_dist = float('inf')
        
        for node in self.nodes.values():
            if occupied_only and node.content is None:
                continue
            
            coords = node.address.to_tuple()
            dist = sum((c - z) ** 2 for c, z in zip(coords, center)) ** 0.5
            
            if dist < best_dist:
                best_dist = dist
                best_node = node
        
        return best_node
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def occupied_count(self) -> int:
        return sum(1 for n in self.nodes.values() if n.content is not None)


# =============================================================================
# SOLENOID FLOW (κ-CONSERVATION)
# =============================================================================

class SolenoidFlow:
    """
    The Autopoietic κ-Solenoid: a divergence-free flow through sectors.
    
    Cycles resources: Earth → Fire → Air → Water → Earth
    while conserving κ (coherence) and tension.
    """
    
    # Flow direction: E→F→A→W→E
    FLOW_ORDER = [Sector.EARTH, Sector.FIRE, Sector.AIR, Sector.WATER]
    
    def __init__(self, lattice: CrystalLattice):
        self.lattice = lattice
        self.flow_rate: float = 0.1  # κ transferred per step
    
    def step(self) -> Dict[str, float]:
        """
        Execute one step of the solenoid flow.
        
        Transfers κ from each sector to the next in sequence.
        Returns flow statistics.
        """
        transferred = {s.name: 0.0 for s in Sector}
        
        for i, source_sector in enumerate(self.FLOW_ORDER):
            target_sector = self.FLOW_ORDER[(i + 1) % 4]
            
            # Get nodes in source sector with positive κ
            source_nodes = [n for n in self.lattice.get_sector_nodes(source_sector)
                          if n.kappa > self.flow_rate]
            
            if not source_nodes:
                continue
            
            # Get nodes in target sector with space for κ
            target_nodes = self.lattice.get_sector_nodes(target_sector)
            
            # Transfer κ from source to target
            for src, tgt in zip(source_nodes, target_nodes):
                transfer_amount = min(self.flow_rate, src.kappa)
                src.kappa -= transfer_amount
                tgt.kappa += transfer_amount
                transferred[source_sector.name] += transfer_amount
        
        return transferred
    
    def verify_divergence_free(self) -> bool:
        """
        Verify the flow is divergence-free.
        
        Total κ in system should be conserved.
        """
        is_valid, _ = self.lattice.verify_conservation()
        return is_valid


# =============================================================================
# HOLOGRAPHIC SEED
# =============================================================================

@dataclass
class HolographicSeed:
    """
    A compressed seed from which content can be reconstructed.
    
    Store-In, Not Out principle:
    - Don't store the full expansion
    - Store the generator (seed) + sparse residual
    - X = Expand(g) ⊕ r
    """
    generator: bytes          # The seed/generator
    residual: bytes           # Sparse residual (deltas)
    address: CrystalAddress   # Where this content belongs
    expansion_rule: str       # How to expand the generator
    checksum: str             # Integrity check
    
    @classmethod
    def compress(cls, content: Any, address: CrystalAddress,
                 expansion_rule: str = "identity") -> 'HolographicSeed':
        """Compress content into a seed."""
        content_bytes = str(content).encode('utf-8')
        
        # Simple compression: use hash as generator, full content as residual
        # In a real system, this would use actual compression
        generator = hashlib.sha256(content_bytes).digest()[:16]
        residual = content_bytes
        
        checksum = hashlib.sha256(generator + residual).hexdigest()[:16]
        
        return cls(
            generator=generator,
            residual=residual,
            address=address,
            expansion_rule=expansion_rule,
            checksum=checksum
        )
    
    def expand(self) -> Any:
        """Reconstruct content from seed."""
        # Verify integrity first
        computed = hashlib.sha256(self.generator + self.residual).hexdigest()[:16]
        if computed != self.checksum:
            raise ValueError("Seed integrity check failed")
        
        # Reconstruct (in this simple version, just decode residual)
        return self.residual.decode('utf-8')
    
    def verify(self) -> bool:
        """Verify seed integrity."""
        computed = hashlib.sha256(self.generator + self.residual).hexdigest()[:16]
        return computed == self.checksum


# =============================================================================
# VALIDATION
# =============================================================================

def validate_crystal_system() -> bool:
    """Validate the crystal addressing system."""
    # 4 sectors
    assert len(Sector) == 4
    
    # 4 roles
    assert len(Role) == 4
    
    # 256 addresses (4^4)
    assert 4 ** 4 == 256
    
    # Address round-trip
    for i in range(256):
        addr = CrystalAddress.from_linear(i)
        assert addr.to_linear() == i
    
    # Base-4 round-trip
    addr = CrystalAddress(1, 2, 3, 0)
    assert CrystalAddress.from_base4(addr.to_base4()) == addr
    
    # Sector rotation
    addr = CrystalAddress(0, 1, 2, 3)
    rotated = addr.rotate_sector(1)
    assert rotated.sector == 1
    assert rotated.cell == addr.cell
    
    # Crystal lattice
    lattice = CrystalLattice()
    assert len(lattice) == 256
    
    # Conservation
    addr1 = CrystalAddress(0, 0, 0, 0)
    lattice.set_content(addr1, "test", kappa=1.0, tension=0.5)
    is_valid, _ = lattice.verify_conservation()
    assert is_valid
    
    # Holographic seed
    seed = HolographicSeed.compress("test content", addr1)
    assert seed.verify()
    assert seed.expand() == "test content"
    
    return True


if __name__ == "__main__":
    print("Validating Crystal Addressing System...")
    assert validate_crystal_system()
    print("✓ Crystal system validated")
    
    # Demo
    print("\n=== The Four Sectors ===")
    for s in Sector:
        print(f"\n{s.symbol} {s.name} ({s.representation}):")
        print(f"  Element: {s.element}")
        print(f"  Function: {s.function}")
        print(f"  Domain: {s.mathematical_domain}")
    
    print("\n=== Crystal Addressing Demo ===")
    # Create some addresses
    addrs = [
        CrystalAddress(0, 0, 0, 0),  # Earth, first chapter, atoms, first item
        CrystalAddress(1, 2, 1, 3),  # Water, third chapter, rotations, fourth item
        CrystalAddress(3, 3, 3, 3),  # Air, last chapter, patches, last item
    ]
    
    for addr in addrs:
        print(f"Address: {addr}")
        print(f"  Linear index: {addr.to_linear()}")
        print(f"  Base-4: {addr.to_base4()}")
        print(f"  Near zero: {ZeroPoint.is_near_zero(addr)}")
    
    print("\n=== Crystal Lattice Demo ===")
    lattice = CrystalLattice()
    
    # Store some content
    lattice.set_content(CrystalAddress(0, 0, 0, 0), "Axiom 1: Conservation", kappa=1.0)
    lattice.set_content(CrystalAddress(1, 0, 0, 0), "Definition 1: Flow", kappa=0.8)
    lattice.set_content(CrystalAddress(2, 0, 0, 0), "Theorem 1: Entropy", kappa=0.9)
    
    print(f"Occupied nodes: {lattice.occupied_count()}/256")
    
    for sector in Sector:
        summary = lattice.sector_summary(sector)
        print(f"{sector.symbol} {sector.name}: {summary['occupied']} nodes, κ={summary['total_kappa']:.2f}")
    
    print("\n=== Solenoid Flow Demo ===")
    flow = SolenoidFlow(lattice)
    print("Initial conservation:", lattice.verify_conservation())
    
    for i in range(3):
        transferred = flow.step()
        print(f"Step {i+1}: {transferred}")
    
    print("Final conservation:", lattice.verify_conservation())
