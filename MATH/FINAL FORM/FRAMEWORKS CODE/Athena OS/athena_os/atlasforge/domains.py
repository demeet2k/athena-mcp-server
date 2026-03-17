"""
ATHENA OS - AtlasForge
======================
Domain Objects: Intervals, Unions, Graphs, Manifolds

From AtlasForge.docx §2.1:

DOMAIN DEFINITION:
    D = (|D|, ??) where:
    - |D| is the carrier set
    - ?? is minimal structure for obligations
    
DOMAIN KINDS:
    - Interval: [a,b] with topology and metric
    - Union: ⋃ of intervals
    - Graph: discrete topology
    - Manifold: smooth structure

LEGALITY:
    Domains must satisfy structural requirements
    for declared obligations.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Set, Any, Callable, Union
from enum import Enum, auto
import math


# =============================================================================
# DOMAIN KINDS
# =============================================================================

class DomainKind(Enum):
    """Types of domains in AtlasForge."""
    
    INTERVAL = "interval"
    UNION = "union"
    GRAPH = "graph"
    MANIFOLD = "manifold"
    POINT = "point"
    PRODUCT = "product"


class BoundaryType(Enum):
    """Boundary openness."""
    
    CLOSED = "closed"       # [a, b]
    OPEN_LEFT = "open_left"  # (a, b]
    OPEN_RIGHT = "open_right"  # [a, b)
    OPEN = "open"           # (a, b)


# =============================================================================
# INTERVAL DOMAIN
# =============================================================================

@dataclass
class Interval:
    """
    Interval domain [a, b] with structure.
    
    D_int = ([a,b], ??_int)
    """
    
    a: float = 0.0          # Left endpoint
    b: float = 1.0          # Right endpoint
    
    # Boundary flags
    open_left: bool = False
    open_right: bool = False
    
    # Assumptions
    assumptions: Set[str] = field(default_factory=set)
    
    def __post_init__(self):
        if self.a > self.b:
            self.a, self.b = self.b, self.a
    
    @property
    def boundary_type(self) -> BoundaryType:
        """Get boundary type."""
        if self.open_left and self.open_right:
            return BoundaryType.OPEN
        elif self.open_left:
            return BoundaryType.OPEN_LEFT
        elif self.open_right:
            return BoundaryType.OPEN_RIGHT
        return BoundaryType.CLOSED
    
    @property
    def length(self) -> float:
        """Interval length b - a."""
        return self.b - self.a
    
    @property
    def midpoint(self) -> float:
        """Midpoint (a + b) / 2."""
        return (self.a + self.b) / 2
    
    def contains(self, x: float) -> bool:
        """Check if x ∈ [a, b]."""
        left_ok = x > self.a if self.open_left else x >= self.a
        right_ok = x < self.b if self.open_right else x <= self.b
        return left_ok and right_ok
    
    def distance(self, x: float, y: float) -> float:
        """Standard metric |x - y|."""
        return abs(x - y)
    
    def clamp(self, x: float) -> float:
        """Clamp x to interval."""
        return max(self.a, min(self.b, x))
    
    def sample(self, n: int = 10) -> List[float]:
        """Sample n uniform points."""
        if n <= 1:
            return [self.midpoint]
        return [self.a + i * self.length / (n - 1) for i in range(n)]
    
    def split(self, point: float) -> Tuple['Interval', 'Interval']:
        """Split at point into two intervals."""
        if not self.contains(point):
            raise ValueError(f"Split point {point} not in interval")
        
        left = Interval(self.a, point, self.open_left, False)
        right = Interval(point, self.b, False, self.open_right)
        
        return left, right
    
    def intersect(self, other: 'Interval') -> Optional['Interval']:
        """Intersection of two intervals."""
        new_a = max(self.a, other.a)
        new_b = min(self.b, other.b)
        
        if new_a > new_b:
            return None
        
        open_left = (new_a == self.a and self.open_left) or \
                   (new_a == other.a and other.open_left)
        open_right = (new_b == self.b and self.open_right) or \
                    (new_b == other.b and other.open_right)
        
        return Interval(new_a, new_b, open_left, open_right)
    
    def __repr__(self) -> str:
        left = "(" if self.open_left else "["
        right = ")" if self.open_right else "]"
        return f"{left}{self.a}, {self.b}{right}"
    
    @classmethod
    def unit(cls) -> 'Interval':
        """Unit interval [0, 1]."""
        return cls(0.0, 1.0)
    
    @classmethod
    def real_line(cls) -> 'Interval':
        """Extended real line (-∞, ∞)."""
        return cls(-float('inf'), float('inf'), True, True)


# =============================================================================
# UNION DOMAIN
# =============================================================================

@dataclass
class UnionDomain:
    """
    Union of intervals ⋃ I_k.
    """
    
    intervals: List[Interval] = field(default_factory=list)
    
    @property
    def num_components(self) -> int:
        return len(self.intervals)
    
    def add_interval(self, interval: Interval) -> None:
        """Add interval to union."""
        self.intervals.append(interval)
        self._simplify()
    
    def _simplify(self) -> None:
        """Merge overlapping intervals."""
        if len(self.intervals) <= 1:
            return
        
        # Sort by left endpoint
        self.intervals.sort(key=lambda i: i.a)
        
        merged = [self.intervals[0]]
        for interval in self.intervals[1:]:
            last = merged[-1]
            if interval.a <= last.b:
                # Overlapping - merge
                merged[-1] = Interval(
                    last.a, 
                    max(last.b, interval.b),
                    last.open_left,
                    interval.open_right if interval.b > last.b else last.open_right
                )
            else:
                merged.append(interval)
        
        self.intervals = merged
    
    def contains(self, x: float) -> bool:
        """Check if x is in any interval."""
        return any(i.contains(x) for i in self.intervals)
    
    def total_length(self) -> float:
        """Total length of union."""
        return sum(i.length for i in self.intervals)
    
    @classmethod
    def from_intervals(cls, *intervals: Interval) -> 'UnionDomain':
        """Create from list of intervals."""
        u = cls()
        for i in intervals:
            u.add_interval(i)
        return u


# =============================================================================
# GRAPH DOMAIN
# =============================================================================

@dataclass
class GraphDomain:
    """
    Discrete graph domain.
    
    Nodes with edge connections.
    """
    
    nodes: Set[int] = field(default_factory=set)
    edges: Set[Tuple[int, int]] = field(default_factory=set)
    
    @property
    def num_nodes(self) -> int:
        return len(self.nodes)
    
    @property
    def num_edges(self) -> int:
        return len(self.edges)
    
    def add_node(self, n: int) -> None:
        """Add node."""
        self.nodes.add(n)
    
    def add_edge(self, u: int, v: int) -> None:
        """Add edge (undirected)."""
        self.nodes.add(u)
        self.nodes.add(v)
        self.edges.add((min(u, v), max(u, v)))
    
    def neighbors(self, n: int) -> Set[int]:
        """Get neighbors of node."""
        result = set()
        for u, v in self.edges:
            if u == n:
                result.add(v)
            elif v == n:
                result.add(u)
        return result
    
    def degree(self, n: int) -> int:
        """Degree of node."""
        return len(self.neighbors(n))
    
    def distance(self, u: int, v: int) -> int:
        """Graph distance (BFS)."""
        if u == v:
            return 0
        if u not in self.nodes or v not in self.nodes:
            return -1
        
        # BFS
        visited = {u}
        queue = [(u, 0)]
        
        while queue:
            node, dist = queue.pop(0)
            for neighbor in self.neighbors(node):
                if neighbor == v:
                    return dist + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        
        return -1  # Not connected


# =============================================================================
# MANIFOLD DOMAIN
# =============================================================================

@dataclass
class ManifoldDomain:
    """
    Smooth manifold domain.
    
    Supports differential structure for derivative obligations.
    """
    
    dimension: int = 1
    charts: List[Dict[str, Any]] = field(default_factory=list)
    
    # Boundary if applicable
    boundary: Optional['ManifoldDomain'] = None
    
    @property
    def has_boundary(self) -> bool:
        return self.boundary is not None
    
    def add_chart(self, name: str, 
                  domain: Interval,
                  coord_map: Optional[Callable] = None) -> None:
        """Add coordinate chart."""
        self.charts.append({
            "name": name,
            "domain": domain,
            "map": coord_map or (lambda x: x)
        })
    
    @classmethod
    def circle(cls) -> 'ManifoldDomain':
        """Create S¹ (circle)."""
        m = cls(dimension=1)
        m.add_chart("north", Interval(-math.pi, math.pi))
        return m
    
    @classmethod
    def line(cls) -> 'ManifoldDomain':
        """Create ℝ (real line)."""
        m = cls(dimension=1)
        m.add_chart("global", Interval.real_line())
        return m


# =============================================================================
# DOMAIN WRAPPER
# =============================================================================

@dataclass
class Domain:
    """
    General domain D = (|D|, ??).
    
    Wraps specific domain types.
    """
    
    kind: DomainKind
    carrier: Union[Interval, UnionDomain, GraphDomain, ManifoldDomain]
    structure: Dict[str, Any] = field(default_factory=dict)
    
    # Assumptions for this domain
    assumptions: Set[str] = field(default_factory=set)
    
    @property
    def is_compact(self) -> bool:
        """Check if domain is compact."""
        if self.kind == DomainKind.INTERVAL:
            i = self.carrier
            return not (i.open_left or i.open_right or 
                       abs(i.a) == float('inf') or abs(i.b) == float('inf'))
        elif self.kind == DomainKind.GRAPH:
            return self.carrier.num_nodes < float('inf')
        return False
    
    @property
    def is_connected(self) -> bool:
        """Check if domain is connected."""
        if self.kind == DomainKind.INTERVAL:
            return True
        elif self.kind == DomainKind.UNION:
            return self.carrier.num_components == 1
        return True  # Assume connected
    
    def add_assumption(self, assumption: str) -> None:
        """Add assumption to domain."""
        self.assumptions.add(assumption)
    
    def has_structure(self, structure_type: str) -> bool:
        """Check if domain has required structure."""
        return structure_type in self.structure
    
    def add_structure(self, structure_type: str, data: Any) -> None:
        """Add structure to domain."""
        self.structure[structure_type] = data
    
    @classmethod
    def interval(cls, a: float, b: float, **kwargs) -> 'Domain':
        """Create interval domain."""
        return cls(
            kind=DomainKind.INTERVAL,
            carrier=Interval(a, b, **kwargs)
        )
    
    @classmethod
    def unit_interval(cls) -> 'Domain':
        """Create [0, 1]."""
        return cls.interval(0.0, 1.0)
    
    @classmethod
    def graph(cls, nodes: Set[int], edges: Set[Tuple[int, int]]) -> 'Domain':
        """Create graph domain."""
        return cls(
            kind=DomainKind.GRAPH,
            carrier=GraphDomain(nodes, edges)
        )


# =============================================================================
# VALIDATION
# =============================================================================

def validate_domains() -> bool:
    """Validate domains module."""
    
    # Test Interval
    i = Interval(0, 1)
    assert i.length == 1.0
    assert i.contains(0.5)
    assert not i.contains(1.5)
    
    # Test open intervals
    open_i = Interval(0, 1, open_left=True, open_right=True)
    assert not open_i.contains(0)
    assert open_i.contains(0.5)
    
    # Test split
    left, right = i.split(0.5)
    assert left.b == 0.5
    assert right.a == 0.5
    
    # Test intersection
    i1 = Interval(0, 2)
    i2 = Interval(1, 3)
    inter = i1.intersect(i2)
    assert inter.a == 1 and inter.b == 2
    
    # Test UnionDomain
    u = UnionDomain.from_intervals(
        Interval(0, 1),
        Interval(2, 3)
    )
    assert u.num_components == 2
    assert u.contains(0.5)
    assert not u.contains(1.5)
    
    # Test GraphDomain
    g = GraphDomain()
    g.add_edge(1, 2)
    g.add_edge(2, 3)
    assert g.num_nodes == 3
    assert g.distance(1, 3) == 2
    
    # Test Domain wrapper
    d = Domain.unit_interval()
    assert d.kind == DomainKind.INTERVAL
    assert d.is_compact
    
    return True


if __name__ == "__main__":
    print("Validating AtlasForge Domains...")
    assert validate_domains()
    print("✓ Domains module validated")
