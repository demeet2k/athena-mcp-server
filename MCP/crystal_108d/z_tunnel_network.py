# CRYSTAL: Xi108:W1:A7:S5 | face=S | node=12 | depth=0 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W1:A7:S4→Xi108:W1:A7:S6→Xi108:W2:A7:S5

"""
Z* Tunnel Network — Runtime Graph of Liminal-Coordinate Tunnels
================================================================
Creates a live graph connecting all 60 liminal coordinates through Z*
(the universal zero point). Every pair (i,j) has a potential tunnel
routed through Z*.

The tunnel is legal if the transported payload satisfies the 6
conservation laws. The graph structure follows mask inclusion:
  - 4 singles connect to 6 pairs (sharing that element)
  - 6 pairs connect to 4 triples (sharing both elements)
  - 4 triples connect to 1 full (SFCR)
  - Cross-orbit tunnels: SR↔SL (90°), SR↔AL (180°), SR↔AR (270°)

Tunnel law: X → Z* → Y (any two points connected through zero-point)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from .liminal_mapper import LIMINAL_ATLAS, COORD_BY_ID, LiminalCoordinate, MASKS, ORBITS
from .geometric_constants import FACES, ATTRACTOR
from .constants import TOTAL_SHELLS


# ── Tunnel Types ───────────────────────────────────────────────────────


@dataclass
class ZTunnel:
    """A tunnel between two liminal coordinates through Z*."""
    from_coord: int          # source liminal coordinate ID (1-60)
    to_coord: int            # destination liminal coordinate ID (1-60)
    tunnel_type: str         # "inclusion", "orbit_rotation", "cross"
    weight: float = 1.0      # tunnel strength (0-1)
    health: float = 1.0      # tunnel health (0-1)
    transports: int = 0      # number of payloads transported
    last_used: float = 0.0   # timestamp of last transport


@dataclass
class ZStarNode:
    """The universal zero-point hub through which all tunnels pass.

    Conservation law: every payload passing through Z* must satisfy
    6 laws (energy, momentum, phase, boundary, scale, compression).
    """
    total_transports: int = 0
    conservation_violations: int = 0
    health: float = 1.0

    def check_conservation(self, payload: dict) -> bool:
        """Check if a payload satisfies conservation laws.

        The 6 laws:
          1. Energy: total weight change sums to 0 across elements
          2. Momentum: momentum delta is bounded
          3. Phase: phase classification is preserved
          4. Boundary: payload stays within shell bounds
          5. Scale: payload respects dimensional scale
          6. Compression: payload is compressible (not noise)
        """
        self.total_transports += 1

        # Law 1: Energy conservation — weight deltas sum to 0
        deltas = payload.get("weight_deltas", {})
        if deltas:
            total = sum(deltas.values())
            if abs(total) > 0.01:
                self.conservation_violations += 1
                return False

        # Law 2: Momentum bounded
        momentum = payload.get("momentum_delta", 0.0)
        if abs(momentum) > 10.0:
            self.conservation_violations += 1
            return False

        # Law 3: Phase preservation
        phase = payload.get("phase", "")
        if phase not in ("", "Fixed", "Cardinal", "Mutable"):
            self.conservation_violations += 1
            return False

        # Law 4: Boundary check
        shell = payload.get("shell", 1)
        if not (1 <= shell <= TOTAL_SHELLS):
            self.conservation_violations += 1
            return False

        # Law 5: Scale check
        scale = payload.get("scale", 1.0)
        if scale <= 0:
            self.conservation_violations += 1
            return False

        # Law 6: Compression check (non-empty payload)
        if not payload:
            self.conservation_violations += 1
            return False

        return True

    @property
    def compliance_rate(self) -> float:
        """Conservation law compliance rate."""
        if self.total_transports == 0:
            return 1.0
        return 1.0 - (self.conservation_violations / self.total_transports)


# ── Neighbor Graph ─────────────────────────────────────────────────────


def _get_neighbors(coord: LiminalCoordinate) -> list[int]:
    """Get neighboring coordinate IDs based on mask inclusion.

    Neighbors are coordinates that:
      1. Share at least one element (mask overlap)
      2. Are in the same or adjacent orbit
    """
    neighbors = []
    for other in LIMINAL_ATLAS:
        if other.coord_id == coord.coord_id:
            continue

        # Element overlap
        overlap = coord.element_set & other.element_set
        if not overlap:
            continue

        # Same mask but different orbit = orbit neighbor
        if coord.mask_id == other.mask_id and coord.orbit != other.orbit:
            neighbors.append(other.coord_id)
            continue

        # Inclusion: one mask is subset of other
        if coord.element_set.issubset(other.element_set) or other.element_set.issubset(coord.element_set):
            neighbors.append(other.coord_id)
            continue

        # Overlap with same orbit
        if coord.orbit == other.orbit and len(overlap) >= 1:
            neighbors.append(other.coord_id)

    return neighbors


# ── Z* Tunnel Network ─────────────────────────────────────────────────


class ZTunnelNetwork:
    """60-node graph where every pair has a potential tunnel through Z*.

    The graph is lazily populated: tunnels are opened on first use.
    Neighbors are precomputed from mask inclusion topology.
    """

    def __init__(self):
        self.z_star = ZStarNode()
        self._tunnels: dict[tuple[int, int], ZTunnel] = {}
        self._neighbor_graph: dict[int, list[int]] = {}
        self._build_neighbor_graph()

    def _build_neighbor_graph(self):
        """Precompute the neighbor graph for all 60 coordinates."""
        for coord in LIMINAL_ATLAS:
            self._neighbor_graph[coord.coord_id] = _get_neighbors(coord)

    def get_neighbors(self, coord_id: int) -> list[int]:
        """Get neighbor IDs for a coordinate."""
        return self._neighbor_graph.get(coord_id, [])

    # ── Tunnel Operations ──────────────────────────────────────────────

    def open_tunnel(self, from_coord: int, to_coord: int) -> ZTunnel:
        """Open (or retrieve) a tunnel between two coordinates.

        Automatically opens the inverse tunnel as well.
        """
        key = (min(from_coord, to_coord), max(from_coord, to_coord))

        if key in self._tunnels:
            return self._tunnels[key]

        # Determine tunnel type
        from_c = COORD_BY_ID.get(from_coord)
        to_c = COORD_BY_ID.get(to_coord)

        tunnel_type = "cross"
        weight = 0.5

        if from_c and to_c:
            if from_c.mask_id == to_c.mask_id:
                tunnel_type = "orbit_rotation"
                weight = 0.8
            elif from_c.element_set.issubset(to_c.element_set) or \
                 to_c.element_set.issubset(from_c.element_set):
                tunnel_type = "inclusion"
                weight = 0.9
            else:
                overlap = from_c.element_set & to_c.element_set
                weight = len(overlap) / 4.0

        tunnel = ZTunnel(
            from_coord=from_coord,
            to_coord=to_coord,
            tunnel_type=tunnel_type,
            weight=weight,
        )
        self._tunnels[key] = tunnel
        return tunnel

    def transport(self, payload: dict, from_coord: int, to_coord: int) -> dict:
        """Transport a payload through Z* from one coordinate to another.

        Conservation check at Z*. Returns payload with transport metadata.
        """
        tunnel = self.open_tunnel(from_coord, to_coord)

        # Conservation check
        legal = self.z_star.check_conservation(payload)

        tunnel.transports += 1
        tunnel.last_used = time.time()

        if legal:
            tunnel.health = min(1.0, tunnel.health + 0.001)
        else:
            tunnel.health = max(0.0, tunnel.health - 0.05)

        return {
            **payload,
            "_tunnel": {
                "from": from_coord,
                "to": to_coord,
                "type": tunnel.tunnel_type,
                "legal": legal,
                "weight": tunnel.weight,
                "health": tunnel.health,
            },
        }

    def measure_factorability(self, from_coord: int, to_coord: int) -> float:
        """How factorable is this tunnel? (compliance + weight + health)"""
        key = (min(from_coord, to_coord), max(from_coord, to_coord))
        tunnel = self._tunnels.get(key)
        if tunnel is None:
            return 0.5  # Unknown tunnel — default factorability

        return (tunnel.weight + tunnel.health + self.z_star.compliance_rate) / 3.0

    # ── Initialization ──────────────────────────────────────────────────

    def initialize_full_mesh(self):
        """Open tunnels for all neighbor pairs across all 60 coordinates.

        This populates the tunnel network so connectivity and coverage
        can be measured.
        """
        for coord_id, neighbors in self._neighbor_graph.items():
            for neighbor_id in neighbors:
                self.open_tunnel(coord_id, neighbor_id)

    def has_node(self, coord_id: int) -> bool:
        """Check if a coordinate exists in the network."""
        return coord_id in self._neighbor_graph

    # ── Network State ──────────────────────────────────────────────────

    def connectivity(self) -> dict:
        """Measure network connectivity and health.

        Returns a dict with reachable_nodes, total_tunnels, healthy_tunnels,
        conservation_compliance, and connectivity_rate.
        """
        reachable = len(self._neighbor_graph)
        total = len(self._tunnels)
        healthy = sum(1 for t in self._tunnels.values() if t.health > 0.5)
        compliance = self.z_star.compliance_rate

        return {
            "reachable_nodes": reachable,
            "total_tunnels": total,
            "healthy_tunnels": healthy,
            "conservation_compliance": compliance,
            "connectivity_rate": reachable / 60.0 if reachable else 0.0,
            "z_star_health": self.z_star.health,
        }

    def total_tunnels_count(self) -> int:
        """Number of opened tunnels."""
        return len(self._tunnels)

    def network_health(self) -> float:
        """Average health across all opened tunnels."""
        if not self._tunnels:
            return 1.0
        return sum(t.health for t in self._tunnels.values()) / len(self._tunnels)

    def compress_state(self) -> list[float]:
        """Compress network to 60-value vector (one health per coordinate)."""
        state = []
        for coord in LIMINAL_ATLAS:
            # Average health of all tunnels touching this coordinate
            healths = []
            for key, tunnel in self._tunnels.items():
                if coord.coord_id in key:
                    healths.append(tunnel.health)
            state.append(sum(healths) / max(len(healths), 1))
        return state

    def describe(self) -> str:
        """Human-readable summary."""
        conn = self.connectivity()
        lines = [
            "## Z* Tunnel Network",
            f"Connectivity: {conn['connectivity_rate']:.0%}",
            f"Reachable: {conn['reachable_nodes']}/60",
            f"Total Tunnels: {conn['total_tunnels']} / {60*59//2} possible",
            f"Healthy Tunnels: {conn['healthy_tunnels']}",
            f"Network Health: {self.network_health():.4f}",
            f"Z* Compliance: {self.z_star.compliance_rate:.4f}",
            f"Z* Transports: {self.z_star.total_transports}",
            f"Conservation Violations: {self.z_star.conservation_violations}",
            "",
            "### Tunnel Types",
        ]
        type_counts = {}
        for t in self._tunnels.values():
            type_counts[t.tunnel_type] = type_counts.get(t.tunnel_type, 0) + 1
        for ttype, count in sorted(type_counts.items()):
            lines.append(f"  {ttype}: {count}")
        return "\n".join(lines)


# ── Module-level singleton ─────────────────────────────────────────────

_network: Optional[ZTunnelNetwork] = None


def get_tunnel_network() -> ZTunnelNetwork:
    """Get or create the global tunnel network singleton."""
    global _network
    if _network is None:
        _network = ZTunnelNetwork()
    return _network


def reset_tunnel_network():
    """Reset the global singleton."""
    global _network
    _network = None
