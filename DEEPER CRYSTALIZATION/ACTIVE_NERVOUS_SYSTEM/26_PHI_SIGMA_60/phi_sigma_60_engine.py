#!/usr/bin/env python3
"""
PhiSigma60 Engine — 60-State Higher-Dimensional Phi-Constant Atlas

Computes all 60 states (15 masks x 4 lenses) from 4 primitive phi-objects,
verifies closure identities, and generates the metro adjacency graph.

Primitives:
  Phi_a = phi^(1/phi)    — soft manifest growth
  Phi_b = phi^(-phi)     — deep refinement/contraction
  Phi_c = phi^(i/phi)    — forward phase resonance
  Phi_d = phi^(-i*phi)   — reverse phase/counter-resonance

Universal algorithm:
  z_S = sum of primitive exponents for mask S
  Square:  A_S = phi^(z_S)
  Flower:  F_S = phi^(-Im(z_S) + i*Re(z_S))
  Cloud:   Z_S = z_S
  Fractal: R_S(k) = phi^(k + z_S)
"""

import cmath
import math
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set, Tuple, Optional
from itertools import combinations


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

PHI = (1 + math.sqrt(5)) / 2       # 1.6180339887...
INV_PHI = PHI - 1                   # 0.6180339887... = 1/phi
LN_PHI = math.log(PHI)              # ln(phi) ~ 0.48121


# ═══════════════════════════════════════════════════════════════
# PRIMITIVE EXPONENT VECTORS
# ═══════════════════════════════════════════════════════════════

class Primitive(Enum):
    A = "A"   # growth
    B = "B"   # refinement
    C = "C"   # forward phase
    D = "D"   # reverse phase

EXPONENT_VECTORS: Dict[str, complex] = {
    "A": complex(INV_PHI, 0),       # 1/phi  (positive real)
    "B": complex(-PHI, 0),          # -phi   (negative real)
    "C": complex(0, INV_PHI),       # i/phi  (positive imaginary)
    "D": complex(0, -PHI),          # -i*phi (negative imaginary)
}


# ═══════════════════════════════════════════════════════════════
# MASKS
# ═══════════════════════════════════════════════════════════════

LETTERS = ["A", "B", "C", "D"]

def generate_all_masks() -> List[FrozenSet[str]]:
    """Generate all 15 nonempty subsets of {A,B,C,D}."""
    masks = []
    for r in range(1, 5):
        for combo in combinations(LETTERS, r):
            masks.append(frozenset(combo))
    return masks

MASK_NAMES = {
    frozenset(["A"]): "01",
    frozenset(["B"]): "02",
    frozenset(["C"]): "03",
    frozenset(["D"]): "04",
    frozenset(["A","B"]): "05",
    frozenset(["A","C"]): "06",
    frozenset(["A","D"]): "07",
    frozenset(["B","C"]): "08",
    frozenset(["B","D"]): "09",
    frozenset(["C","D"]): "10",
    frozenset(["A","B","C"]): "11",
    frozenset(["A","B","D"]): "12",
    frozenset(["A","C","D"]): "13",
    frozenset(["B","C","D"]): "14",
    frozenset(["A","B","C","D"]): "15",
}

GEOMETRY_CLASS = {1: "pole", 2: "bridge", 3: "chamber", 4: "crown"}


# ═══════════════════════════════════════════════════════════════
# LENS TRANSFORMS
# ═══════════════════════════════════════════════════════════════

class Lens(Enum):
    SQUARE = "S"    # native aether point
    FLOWER = "F"    # 90-degree phase lift
    CLOUD = "C"     # chart coordinate / zero point
    FRACTAL = "R"   # orbit family


def compute_exponent(mask: FrozenSet[str]) -> complex:
    """Compute z_S = sum of primitive exponent vectors."""
    return sum(EXPONENT_VECTORS[p] for p in mask)


def phi_power(z: complex) -> complex:
    """Compute phi^z for complex z using cmath."""
    return cmath.exp(z * LN_PHI)


def square_transform(z_s: complex) -> complex:
    """Square lens: A_S = phi^(z_S)."""
    return phi_power(z_s)


def flower_transform(z_s: complex) -> complex:
    """Flower lens: F_S = phi^(-Im(z_S) + i*Re(z_S))."""
    rotated = complex(-z_s.imag, z_s.real)
    return phi_power(rotated)


def cloud_transform(z_s: complex) -> complex:
    """Cloud lens: Z_S = z_S (the exponent itself)."""
    return z_s


def fractal_transform(z_s: complex, k: int = 0) -> complex:
    """Fractal lens: R_S(k) = phi^(k + z_S)."""
    return phi_power(k + z_s)


# ═══════════════════════════════════════════════════════════════
# PHI STATE
# ═══════════════════════════════════════════════════════════════

@dataclass
class PhiState:
    """A single state in the 60-state atlas."""
    mask: FrozenSet[str]
    mask_id: str
    lens: Lens
    exponent: complex       # z_S
    value: complex           # the computed lens value
    geometry: str            # pole/bridge/chamber/crown

    @property
    def station_id(self) -> str:
        return f"{self.mask_id}{self.lens.value}"

    def __repr__(self):
        return f"PhiState({self.station_id}: {self.geometry})"


def compute_all_states() -> Dict[str, PhiState]:
    """Compute all 60 states."""
    states = {}
    for mask in generate_all_masks():
        mid = MASK_NAMES[mask]
        z_s = compute_exponent(mask)
        geo = GEOMETRY_CLASS[len(mask)]

        for lens in Lens:
            if lens == Lens.SQUARE:
                val = square_transform(z_s)
            elif lens == Lens.FLOWER:
                val = flower_transform(z_s)
            elif lens == Lens.CLOUD:
                val = cloud_transform(z_s)
            elif lens == Lens.FRACTAL:
                val = fractal_transform(z_s, k=0)

            state = PhiState(
                mask=mask, mask_id=mid, lens=lens,
                exponent=z_s, value=val, geometry=geo
            )
            states[state.station_id] = state

    return states


# ═══════════════════════════════════════════════════════════════
# METRO ADJACENCY
# ═══════════════════════════════════════════════════════════════

def compute_mask_neighbors(mask: FrozenSet[str]) -> List[FrozenSet[str]]:
    """Find all masks differing by exactly one letter."""
    neighbors = []
    all_letters = frozenset(LETTERS)
    # Remove one letter
    for letter in mask:
        neighbor = mask - {letter}
        if neighbor:
            neighbors.append(neighbor)
    # Add one letter
    for letter in all_letters - mask:
        neighbors.append(mask | {letter})
    return neighbors


def build_adjacency() -> Dict[str, List[str]]:
    """Build full 60-node adjacency (inter-mask + intra-lens)."""
    adj: Dict[str, List[str]] = {}
    masks = generate_all_masks()

    for mask in masks:
        mid = MASK_NAMES[mask]
        mask_neighbors = compute_mask_neighbors(mask)

        for lens in Lens:
            sid = f"{mid}{lens.value}"
            neighbors = []

            # Intra-lens: other 3 lenses of same mask
            for other_lens in Lens:
                if other_lens != lens:
                    neighbors.append(f"{mid}{other_lens.value}")

            # Inter-mask: same lens, neighboring masks
            for nmask in mask_neighbors:
                nid = MASK_NAMES[nmask]
                neighbors.append(f"{nid}{lens.value}")

            adj[sid] = neighbors

    return adj


# ═══════════════════════════════════════════════════════════════
# CLOSURE IDENTITY VERIFICATION
# ═══════════════════════════════════════════════════════════════

def verify_closures() -> List[Tuple[str, bool, float]]:
    """Verify all critical closure identities."""
    results = []
    eps = 1e-10

    # Primitives
    Phi_a = phi_power(EXPONENT_VECTORS["A"])
    Phi_b = phi_power(EXPONENT_VECTORS["B"])
    Phi_c = phi_power(EXPONENT_VECTORS["C"])
    Phi_d = phi_power(EXPONENT_VECTORS["D"])

    # Identity 1: Phi_a * Phi_b = phi^(-1)
    lhs = Phi_a * Phi_b
    rhs = phi_power(-1)
    residual = abs(lhs - rhs)
    results.append(("Phi_a * Phi_b = phi^(-1)", residual < eps, residual))

    # Identity 2: Phi_c * Phi_d = phi^(-i)
    lhs = Phi_c * Phi_d
    rhs = phi_power(-1j)
    residual = abs(lhs - rhs)
    results.append(("Phi_c * Phi_d = phi^(-i)", residual < eps, residual))

    # Identity 3: (Phi_c * Phi_d)^i = phi  (MAJOR)
    cd_product = Phi_c * Phi_d
    lhs = cmath.exp(1j * cmath.log(cd_product))
    rhs = PHI
    residual = abs(lhs - rhs)
    results.append(("(Phi_c * Phi_d)^i = phi", residual < eps, residual))

    # Identity 4: Crown product = phi^(-1-i)
    lhs = Phi_a * Phi_b * Phi_c * Phi_d
    rhs = phi_power(complex(-1, -1))
    residual = abs(lhs - rhs)
    results.append(("Crown product = phi^(-1-i)", residual < eps, residual))

    # Identity 5: 10F = phi (Flower of CD = primal phi)
    z_cd = compute_exponent(frozenset(["C", "D"]))
    f_cd = flower_transform(z_cd)
    residual = abs(f_cd - PHI)
    results.append(("10F = phi (CD Flower closure)", residual < eps, residual))

    # Identity 6: 05F = phi^(-i) (Flower of AB = phase bridge)
    z_ab = compute_exponent(frozenset(["A", "B"]))
    f_ab = flower_transform(z_ab)
    rhs = phi_power(-1j)
    residual = abs(f_ab - rhs)
    results.append(("05F = phi^(-i) (AB Flower)", residual < eps, residual))

    # Identity 7: 03F = phi^(-1/phi) (Flower of C = damped growth)
    z_c = compute_exponent(frozenset(["C"]))
    f_c = flower_transform(z_c)
    rhs = phi_power(-INV_PHI)
    residual = abs(f_c - rhs)
    results.append(("03F = phi^(-1/phi)", residual < eps, residual))

    # Identity 8: 04F = phi^phi (Flower of D = strong amplification)
    z_d = compute_exponent(frozenset(["D"]))
    f_d = flower_transform(z_d)
    rhs = phi_power(PHI)
    residual = abs(f_d - rhs)
    results.append(("04F = phi^phi", residual < eps, residual))

    return results


# ═══════════════════════════════════════════════════════════════
# CONNECTIVITY CHECK
# ═══════════════════════════════════════════════════════════════

def check_connectivity(adj: Dict[str, List[str]]) -> Tuple[int, int]:
    """BFS to verify full graph connectivity."""
    if not adj:
        return 0, 0
    start = next(iter(adj))
    visited = {start}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for neighbor in adj.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return len(visited), len(adj)


# ═══════════════════════════════════════════════════════════════
# MAIN VERIFICATION
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  PHISIGMA60 ENGINE")
    print("  60-State Higher-Dimensional Phi-Constant Atlas")
    print("=" * 70)

    # Compute all 60 states
    states = compute_all_states()
    print(f"\n[1] States computed: {len(states)}/60")

    # Count by geometry class
    geo_counts = {}
    for s in states.values():
        geo_counts[s.geometry] = geo_counts.get(s.geometry, 0) + 1
    for geo, count in sorted(geo_counts.items()):
        print(f"    {geo}: {count} states ({count//4} masks)")

    # Verify closures
    print(f"\n[2] Closure Identities:")
    closures = verify_closures()
    all_pass = True
    for name, passed, residual in closures:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"    [{status}] {name} (residual: {residual:.2e})")
    print(f"    {'ALL IDENTITIES VERIFIED' if all_pass else 'SOME IDENTITIES FAILED'}")

    # Build adjacency and check connectivity
    adj = build_adjacency()
    total_edges = sum(len(v) for v in adj.values()) // 2
    reached, total = check_connectivity(adj)
    print(f"\n[3] Metro Graph:")
    print(f"    Nodes: {total}")
    print(f"    Edges: {total_edges}")
    print(f"    Connected: {reached}/{total} {'(FULL)' if reached == total else '(DISCONNECTED!)'}")

    # Print selected states
    print(f"\n[4] Selected States:")
    highlights = ["01S", "02S", "05S", "10S", "10F", "15S", "15F", "15C"]
    for sid in highlights:
        s = states[sid]
        if s.lens == Lens.CLOUD:
            print(f"    {sid}: z = {s.value.real:+.6f} {s.value.imag:+.6f}i  ({s.geometry})")
        else:
            print(f"    {sid}: {s.value.real:+.10f} {s.value.imag:+.10f}i  ({s.geometry})")

    # Verify 10F = phi explicitly
    state_10f = states["10F"]
    print(f"\n[5] Major Closure: 10F = phi")
    print(f"    10F value:  {state_10f.value.real:.15f} + {state_10f.value.imag:.2e}i")
    print(f"    phi value:  {PHI:.15f}")
    print(f"    Match: {'YES' if abs(state_10f.value - PHI) < 1e-10 else 'NO'}")

    # Print full exponent table
    print(f"\n[6] Full Exponent Table (z_S for each mask):")
    for mask in generate_all_masks():
        mid = MASK_NAMES[mask]
        z = compute_exponent(mask)
        letters = "".join(sorted(mask))
        print(f"    {mid} ({letters:4s}):  z = {z.real:+8.6f} {z.imag:+8.6f}i")

    print(f"\n{'=' * 70}")
    print(f"  VERIFICATION COMPLETE")
    print(f"  States: {len(states)}  |  Masks: 15  |  Lenses: 4")
    print(f"  Closures: {sum(1 for _,p,_ in closures if p)}/{len(closures)} passed")
    print(f"  Metro: {total_edges} edges, {'connected' if reached==total else 'DISCONNECTED'}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
