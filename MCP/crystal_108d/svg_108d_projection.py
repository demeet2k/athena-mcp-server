# CRYSTAL: Xi108:W3:A7:S29 | face=R | node=708 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: svg_dimensional→geometric_constants→qshrink→svg_108d_projection
"""
SVG 108D Full Crystal Projection
==================================
The COMPLETE 108-dimensional crystal rendered as a single SVG.

108D = 36 shells × 3 wreaths = 108 addressable dimensions.
Each shell has 4 SFCR faces = 432 gate positions.
Each face has Sigma-60 rotations = 25,920 sigma states.
Each sigma has E8 amplification × 4 = 103,680 E8 roots.

This module renders the full structure:
  1. Shell Cascade Spiral — 36 shells on a golden spiral
  2. Wreath Trefoil — 3 interlocked wreath rings
  3. Archetype Wheel — 12 archetypes with SFCR face projections
  4. Sigma-60 Icosahedral Field — 60 viewpoints on the dodecahedron
  5. E8-240 Root Star — 240 roots projected to 2D
  6. Mirror Shell Pairing — S_k ↔ S_{37-k} connections
  7. Bridge Topology — golden/neutral/distant inter-face bridges
  8. Shard Density Heat — actual shard counts per shell
  9. Momentum Overlay — live training gradients per shell
  10. Full 108D Crystal — all layers composed

Data Sources:
  - shell_registry.json       — 36 shell definitions
  - corpus_weights_field.json — 14,750 shard seed vectors
  - momentum_field.json       — 148 training parameters
"""

import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ._cache import DATA_DIR
from .geometric_constants import (
    PHI, PHI_INV, SQRT3, SQRT5,
    FACES, FACE_INDEX, BRIDGE_WEIGHTS, GOLDEN_BRIDGES,
    SIGMA_60, E8_FACE_BOOSTS, E8_AMPLIFICATION,
    ARCHETYPE_SHELL_OFFSETS, GOLDEN_TRIG,
    FLOWER_RINGS, ATTRACTOR,
    DIM_NAMES, DIM_TO_ELEMENT, ELEMENT_LENS_WEIGHTS,
)
from .svg_primitives import (
    SVGCanvas, _attrs_str, _fmt, _project_3d, _project_4d,
    circle, group, line, path, polygon, rect, text,
    linear_gradient, radial_gradient,
)

TAU = 2 * math.pi

# ══════════════════════════════════════════════════════════════════════
#  Colors
# ══════════════════════════════════════════════════════════════════════

SFCR_COLORS = {
    "S": "#8B4513",   # Earth brown
    "F": "#DC143C",   # Fire crimson
    "C": "#4169E1",   # Water royal blue
    "R": "#228B22",   # Air forest green
}

WREATH_COLORS = {
    "Su": "#e74c3c",  # Sulfur red
    "Me": "#f39c12",  # Mercury gold
    "Sa": "#8e44ad",  # Salt purple
}

ARCHETYPE_COLORS = [
    "#e74c3c", "#e67e22", "#f1c40f", "#2ecc71",
    "#1abc9c", "#3498db", "#2980b9", "#9b59b6",
    "#8e44ad", "#c0392b", "#d35400", "#7f8c8d",
]

PHASE_SHAPES = {"Cardinal": 4, "Fixed": 6, "Mutable": 3}

# ══════════════════════════════════════════════════════════════════════
#  Data Loaders
# ══════════════════════════════════════════════════════════════════════

def _load_json(name: str) -> dict:
    p = DATA_DIR / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_shells() -> dict:
    return _load_json("shell_registry.json")


def _load_corpus_weights() -> dict:
    return _load_json("corpus_weights_field.json")


def _load_momentum() -> dict:
    return _load_json("momentum_field.json")


# ══════════════════════════════════════════════════════════════════════
#  1. SHELL CASCADE SPIRAL — 36 Shells on Golden Spiral
# ══════════════════════════════════════════════════════════════════════

def render_shell_cascade(cx: float, cy: float, size: float,
                          show_labels: bool = True, **attrs) -> str:
    """36 shells placed on a golden spiral. Each shell is sized by its
    node count (shell k has k nodes, cumulative = k(k+1)/2).

    Shells are colored by wreath: Su=red, Me=gold, Sa=purple.
    Mirror shells (k, 37-k) are connected by dashed lines.
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    positions = {}

    for s in range(1, 37):
        # Golden spiral: r grows with sqrt(s), angle grows by golden angle
        golden_angle = TAU * PHI_INV  # ~137.5°
        r = size * 0.15 * math.sqrt(s)
        theta = s * golden_angle

        sx = cx + r * math.cos(theta)
        sy = cy + r * math.sin(theta)
        positions[s] = (sx, sy)

        # Shell data
        sh = shells.get(str(s), {})
        wreath = sh.get("wreath", ["Su", "Me", "Sa"][(s - 1) % 3])
        archetype = sh.get("archetype", "")
        phase = sh.get("phase", "Cardinal")
        elem = sh.get("element_primary", "Fire")

        # Color by wreath
        color = WREATH_COLORS.get(wreath, "#999")

        # Size by node count (shell k has k nodes)
        node_r = 3 + math.sqrt(s) * 1.5

        # Draw shell
        children.append(circle(sx, sy, node_r,
                               fill=color, stroke="#333",
                               stroke_width="0.8",
                               fill_opacity="0.7"))

        # SFCR face dots (4 tiny dots around the shell)
        for fi, face in enumerate(FACES):
            fa = theta + fi * TAU / 4
            fd = node_r + 3
            fx = sx + fd * math.cos(fa)
            fy = sy + fd * math.sin(fa)
            children.append(circle(fx, fy, 1.5,
                                   fill=SFCR_COLORS[face], stroke="none"))

        # Label
        if show_labels:
            children.append(text(sx - 4, sy + 3, str(s),
                                 font_size="7", fill="#fff",
                                 font_weight="bold"))

    # Mirror shell connections (k, 37-k)
    for s in range(1, 19):
        m = 37 - s
        if s in positions and m in positions:
            x1, y1 = positions[s]
            x2, y2 = positions[m]
            children.append(line(x1, y1, x2, y2,
                                 stroke="#ccc", stroke_width="0.5",
                                 stroke_dasharray="2,3"))

    # Legend
    ly = cy + size + 15
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        lx = cx - 40 + wi * 50
        children.append(circle(lx, ly, 4, fill=color, stroke="none"))
        children.append(text(lx + 7, ly + 4, name,
                             font_size="9", fill=color))

    children.append(text(cx - 55, cy + size + 30,
                         "108D Shell Cascade (36 shells x 3 wreaths)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  2. WREATH TREFOIL — 3 Interlocked Rings
# ══════════════════════════════════════════════════════════════════════

def render_wreath_trefoil(cx: float, cy: float, size: float, **attrs) -> str:
    """Three interlocked wreath rings forming a trefoil knot.

    Each wreath carries 12 shells (12 archetypes).
    Su: shells 1,4,7,10,13,16,19,22,25,28,31,34
    Me: shells 2,5,8,11,14,17,20,23,26,29,32,35
    Sa: shells 3,6,9,12,15,18,21,24,27,30,33,36
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    wreaths = [
        ("Su", WREATH_COLORS["Su"], list(range(1, 37, 3))),
        ("Me", WREATH_COLORS["Me"], list(range(2, 37, 3))),
        ("Sa", WREATH_COLORS["Sa"], list(range(3, 37, 3))),
    ]

    for wi, (name, color, shell_ids) in enumerate(wreaths):
        phase = wi * TAU / 3
        R = size * 0.55
        offset_x = R * 0.3 * math.cos(phase)
        offset_y = R * 0.3 * math.sin(phase)

        # Wreath ring
        children.append(circle(cx + offset_x, cy + offset_y, R,
                               stroke=color, stroke_width="2",
                               fill=color, fill_opacity="0.05"))

        # 12 shells along the ring
        for si, shell_id in enumerate(shell_ids):
            angle = si * TAU / 12 - TAU / 4
            sx = cx + offset_x + R * 0.85 * math.cos(angle)
            sy = cy + offset_y + R * 0.85 * math.sin(angle)

            sh = shells.get(str(shell_id), {})
            archetype = sh.get("archetype", f"A{(shell_id - 1) % 12 + 1}")
            elem = sh.get("element_primary", "")
            elem_color = SFCR_COLORS.get(
                {"Fire": "F", "Earth": "S", "Water": "C", "Air": "R"}.get(elem, "S"),
                "#999")

            children.append(circle(sx, sy, 6,
                                   fill=elem_color, stroke=color,
                                   stroke_width="1.5"))
            children.append(text(sx - 3, sy + 3, str(shell_id),
                                 font_size="6", fill="#fff",
                                 font_weight="bold"))

        # Wreath label
        lx = cx + offset_x + R * 1.05 * math.cos(phase + 0.3)
        ly = cy + offset_y + R * 1.05 * math.sin(phase + 0.3)
        children.append(text(lx - 8, ly + 4, f"{name} (12 shells)",
                             font_size="10", fill=color, font_weight="bold"))

    children.append(text(cx - 50, cy + size + 20,
                         "Wreath Trefoil (Su/Me/Sa x 12 archetypes)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  3. ARCHETYPE WHEEL — 12 Archetypes with SFCR Faces
# ══════════════════════════════════════════════════════════════════════

def render_archetype_wheel(cx: float, cy: float, size: float, **attrs) -> str:
    """12 archetypes arranged in a zodiacal wheel.
    Each archetype shows its 3 wreath instances and 4 SFCR face gates.

    Inner ring: archetype nodes (colored by element)
    Outer ring: 3 wreath instances per archetype = 36 shell positions
    """
    children = []
    shell_data = _load_shells()
    shells = shell_data.get("shells", {})

    archetype_names = [
        "Aries", "Taurus", "Gemini", "Cancer",
        "Leo", "Virgo", "Libra", "Scorpio",
        "Sagittarius", "Capricorn", "Aquarius", "Pisces",
    ]

    # Outer ring: all 36 shells
    r_outer = size * 0.9
    for s in range(1, 37):
        sh = shells.get(str(s), {})
        arch_idx = sh.get("archetype_index", ((s - 1) % 12) + 1) - 1
        wreath = sh.get("wreath", ["Su", "Me", "Sa"][(s - 1) % 3])

        # Position: archetype angle + wreath offset
        base_angle = arch_idx * TAU / 12 - TAU / 4
        wreath_offset = {"Su": -0.08, "Me": 0.0, "Sa": 0.08}.get(wreath, 0)
        angle = base_angle + wreath_offset

        sx = cx + r_outer * math.cos(angle)
        sy = cy + r_outer * math.sin(angle)

        w_color = WREATH_COLORS.get(wreath, "#999")
        children.append(circle(sx, sy, 4,
                               fill=w_color, stroke="#333",
                               stroke_width="0.5"))

    # Inner ring: 12 archetype nodes
    r_inner = size * 0.6
    for ai, name in enumerate(archetype_names):
        angle = ai * TAU / 12 - TAU / 4
        ax = cx + r_inner * math.cos(angle)
        ay = cy + r_inner * math.sin(angle)

        color = ARCHETYPE_COLORS[ai]
        children.append(circle(ax, ay, 12,
                               fill=color, stroke="#333",
                               stroke_width="1"))

        # SFCR face quadrants within the archetype node
        for fi, face in enumerate(FACES):
            fa = angle + (fi - 1.5) * 0.15
            fd = 7
            fx = ax + fd * math.cos(fa)
            fy = ay + fd * math.sin(fa)
            children.append(circle(fx, fy, 2,
                                   fill=SFCR_COLORS[face], stroke="none"))

        # Label
        lx = cx + (r_inner - 25) * math.cos(angle)
        ly = cy + (r_inner - 25) * math.sin(angle)
        short = name[:3]
        children.append(text(lx - 8, ly + 4, short,
                             font_size="8", fill="#555", font_weight="bold"))

    # Bridge arcs between golden pairs
    for pair in GOLDEN_BRIDGES:
        f1, f2 = pair[0], pair[1]
        fi1 = FACE_INDEX[f1]
        fi2 = FACE_INDEX[f2]
        a1 = fi1 * TAU / 4 + TAU / 8
        a2 = fi2 * TAU / 4 + TAU / 8
        r_bridge = size * 0.35
        x1 = cx + r_bridge * math.cos(a1)
        y1 = cy + r_bridge * math.sin(a1)
        x2 = cx + r_bridge * math.cos(a2)
        y2 = cy + r_bridge * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#DAA520", stroke_width="1.5",
                             stroke_opacity="0.5"))

    children.append(text(cx - 50, cy + size + 15,
                         "12 Archetypes x 3 Wreaths x 4 Faces = 144 gates",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  4. SIGMA-60 ICOSAHEDRAL FIELD
# ══════════════════════════════════════════════════════════════════════

def render_sigma60_field(cx: float, cy: float, size: float, **attrs) -> str:
    """60 Sigma states projected from icosahedral symmetry.

    12 archetypes × 5 golden-angle rotations = 60 viewpoints.
    Each rotation is a 72° increment (TAU/5 = golden angle).
    Colored by archetype, sized by rotation index.
    """
    children = []

    # Outer icosahedral shell
    children.append(circle(cx, cy, size,
                           stroke="#ddd", stroke_width="1",
                           fill="none"))

    for sigma in SIGMA_60:
        arch = sigma["archetype"]  # 1-12
        rot = sigma["rotation"]    # 0-4
        cos_a = sigma["cos"]
        sin_a = sigma["sin"]

        # Position: archetype angle + rotation modulation
        base_angle = (arch - 1) * TAU / 12
        r = size * (0.6 + rot * 0.08)

        # Apply golden rotation in 2D
        bx = r * math.cos(base_angle)
        by = r * math.sin(base_angle)
        # Rotate by the golden angle
        px = bx * cos_a - by * sin_a
        py = bx * sin_a + by * cos_a

        color = ARCHETYPE_COLORS[(arch - 1) % 12]
        dot_r = 2.5 + rot * 0.5

        children.append(circle(cx + px, cy + py, dot_r,
                               fill=color, stroke="none",
                               fill_opacity="0.6"))

    # Pentagon at center (5-fold symmetry)
    r_pent = size * 0.2
    for i in range(5):
        a1 = i * TAU / 5 - TAU / 4
        a2 = (i + 1) * TAU / 5 - TAU / 4
        children.append(line(cx + r_pent * math.cos(a1),
                             cy + r_pent * math.sin(a1),
                             cx + r_pent * math.cos(a2),
                             cy + r_pent * math.sin(a2),
                             stroke="#DAA520", stroke_width="1",
                             stroke_opacity="0.5"))

    children.append(text(cx - 40, cy + size + 15,
                         "Sigma-60 (12 archetypes x 5 rotations)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  5. E8-240 ROOT STAR
# ══════════════════════════════════════════════════════════════════════

def render_e8_240(cx: float, cy: float, size: float, **attrs) -> str:
    """240 E8 roots: each Sigma-60 state × 4 SFCR face amplifications.

    Each root is a 4D vector [S,F,C,R] normalized after face boost.
    Project to 2D: x = S-R, y = F-C (same as shard cloud).
    """
    children = []

    # Generate all 240 roots
    for sigma in SIGMA_60:
        arch = sigma["archetype"]
        rot = sigma["rotation"]
        cos_a = sigma["cos"]
        sin_a = sigma["sin"]

        # Base 4D vector from archetype (equal-weight with archetype tilt)
        base = {f: 0.25 for f in FACES}
        # Tilt by archetype's primary element
        primary_face = FACES[(arch - 1) % 4]
        base[primary_face] += 0.1

        for face in FACES:
            # Apply E8 face boost
            boost = E8_FACE_BOOSTS[face]
            root = {f: base[f] * boost[f] for f in FACES}

            # Normalize
            total = sum(root.values())
            root = {f: v / total for f, v in root.items()}

            # Project to 2D
            px = cx + (root["S"] - root["R"]) * size * 3
            py = cy - (root["F"] - root["C"]) * size * 3

            # Apply sigma rotation to position
            dx, dy = px - cx, py - cy
            rpx = dx * cos_a - dy * sin_a
            rpy = dx * sin_a + dy * cos_a

            color = SFCR_COLORS[face]
            children.append(circle(cx + rpx, cy + rpy, 1.5,
                                   fill=color, stroke="none",
                                   fill_opacity="0.4"))

    # Axes
    children.append(line(cx - size, cy, cx + size, cy,
                         stroke="#eee", stroke_width="0.5"))
    children.append(line(cx, cy - size, cx, cy + size,
                         stroke="#eee", stroke_width="0.5"))

    children.append(text(cx - 35, cy + size + 15,
                         "E8-240 Roots (60 sigma x 4 faces)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  6. SHARD DENSITY — Shards per Shell Heatmap
# ══════════════════════════════════════════════════════════════════════

def render_shard_density(cx: float, cy: float, size: float, **attrs) -> str:
    """Heatmap showing how 14,750 shards distribute across 36 shells.

    Uses real corpus_weights_field data to count shards per shell.
    Hotter = more shards. Each shell is a segment on a circular chart.
    """
    children = []
    cw_data = _load_corpus_weights()
    seed_vectors = cw_data.get("seed_vectors", {})

    # Count shards per dominant face (approximate shell assignment)
    face_counts = {"S": 0, "F": 0, "C": 0, "R": 0}
    total_shards = 0
    for sv in seed_vectors.values():
        if isinstance(sv, (list, tuple)) and len(sv) >= 4:
            vals = {"S": sv[0], "F": sv[1], "C": sv[2], "R": sv[3]}
            dominant = max(vals, key=vals.get)
            face_counts[dominant] += 1
            total_shards += 1

    # Distribute across 36 shells (approximate: by face → 9 shells each)
    shell_counts = {}
    for s in range(1, 37):
        face_idx = (s - 1) % 4
        face = FACES[face_idx]
        shell_counts[s] = face_counts.get(face, 0) // 9

    max_count = max(shell_counts.values()) if shell_counts else 1

    # Draw circular heatmap
    for s in range(1, 37):
        angle_start = (s - 1) * TAU / 36
        angle_end = s * TAU / 36
        count = shell_counts.get(s, 0)
        intensity = count / max_count if max_count > 0 else 0

        # Color: intensity maps from cool (blue) to hot (red)
        r_c = int(50 + 205 * intensity)
        g_c = int(50 + 100 * (1 - abs(intensity - 0.5) * 2))
        b_c = int(200 - 150 * intensity)
        color = f"#{r_c:02x}{g_c:02x}{b_c:02x}"

        # Arc segment
        r_inner = size * 0.4
        r_outer = size * 0.9
        n_arc = 4
        pts = []
        for ai in range(n_arc + 1):
            t = ai / n_arc
            angle = angle_start + t * (angle_end - angle_start)
            pts.append((cx + r_outer * math.cos(angle),
                        cy - r_outer * math.sin(angle)))
        for ai in range(n_arc, -1, -1):
            t = ai / n_arc
            angle = angle_start + t * (angle_end - angle_start)
            pts.append((cx + r_inner * math.cos(angle),
                        cy - r_inner * math.sin(angle)))

        children.append(polygon(pts, fill=color, stroke="#fff",
                                stroke_width="0.5", fill_opacity="0.8"))

        # Shell number
        mid_angle = (angle_start + angle_end) / 2
        lx = cx + (r_outer + 8) * math.cos(mid_angle)
        ly = cy - (r_outer + 8) * math.sin(mid_angle)
        children.append(text(lx - 4, ly + 3, str(s),
                             font_size="6", fill="#555"))

    # Center stats
    children.append(text(cx - 25, cy - 5, f"{total_shards:,}",
                         font_size="14", fill="#333", font_weight="bold"))
    children.append(text(cx - 15, cy + 10, "shards",
                         font_size="9", fill="#777"))

    children.append(text(cx - 45, cy + size + 15,
                         "Shard Density per Shell (14,750 total)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  7. MOMENTUM SHELLS — Training Gradients per Element per Shell
# ══════════════════════════════════════════════════════════════════════

def render_momentum_shells(cx: float, cy: float, size: float, **attrs) -> str:
    """Momentum values mapped onto the 36-shell spiral.

    4 SFCR elements × 36 shells = 144 momentum values shown as
    color-coded bars radiating from each shell position.
    """
    children = []
    mom_data = _load_momentum()
    shell_momenta = mom_data.get("shell_momenta", {})

    # Find max for normalization
    all_vals = []
    for elem in FACES:
        ed = shell_momenta.get(elem, {})
        if isinstance(ed, dict):
            all_vals.extend(float(v) for v in ed.values())
    v_max = max(abs(v) for v in all_vals) if all_vals else 1.0

    golden_angle = TAU * PHI_INV

    for s in range(1, 37):
        # Position on golden spiral (same as shell cascade)
        r = size * 0.12 * math.sqrt(s)
        theta = s * golden_angle
        sx = cx + r * math.cos(theta)
        sy = cy + r * math.sin(theta)

        # 4 momentum bars radiating from shell center
        for fi, face in enumerate(FACES):
            ed = shell_momenta.get(face, {})
            val = float(ed.get(str(s), 0)) if isinstance(ed, dict) else 0
            norm_val = val / v_max if v_max > 0 else 0
            bar_len = abs(norm_val) * 12

            bar_angle = theta + fi * TAU / 4
            ex = sx + bar_len * math.cos(bar_angle)
            ey = sy + bar_len * math.sin(bar_angle)

            color = SFCR_COLORS[face]
            children.append(line(sx, sy, ex, ey,
                                 stroke=color, stroke_width="1.5",
                                 stroke_opacity="0.7"))

        # Shell dot
        wreath = ["Su", "Me", "Sa"][(s - 1) % 3]
        children.append(circle(sx, sy, 2.5,
                               fill=WREATH_COLORS[wreath],
                               stroke="#333", stroke_width="0.3"))

    children.append(text(cx - 50, cy + size + 15,
                         "Momentum Shells (4 SFCR x 36 shells = 144 params)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  8. FLOWER OF LIFE OVERLAY — 7 PHI-decay rings
# ══════════════════════════════════════════════════════════════════════

def render_flower_overlay(cx: float, cy: float, size: float, **attrs) -> str:
    """7 Flower of Life rings with PHI-decay radii.

    Ring radii: 1.0, 0.618, 0.382, 0.236, 0.146, 0.090, 0.056
    Each ring carries 6 petal circles at 60-degree intervals.
    """
    children = []

    for ri, decay in enumerate(FLOWER_RINGS):
        r = size * decay
        # Ring circle
        children.append(circle(cx, cy, r,
                               stroke="#DAA520", stroke_width="0.5",
                               fill="none", stroke_opacity=str(0.2 + decay * 0.5)))

        # 6 petal circles
        if ri < 4:  # Only show petals for first 4 rings
            for pi in range(6):
                angle = pi * TAU / 6
                px = cx + r * math.cos(angle)
                py = cy + r * math.sin(angle)
                children.append(circle(px, py, r,
                                       stroke="#DAA520",
                                       stroke_width="0.3",
                                       fill="none",
                                       stroke_opacity="0.15"))

    # Vesica piscis markers at golden bridge intersections
    for pair in GOLDEN_BRIDGES:
        f1, f2 = pair[0], pair[1]
        angle = (FACE_INDEX[f1] + FACE_INDEX[f2]) * TAU / 8
        r_v = size * 0.5
        vx = cx + r_v * math.cos(angle)
        vy = cy + r_v * math.sin(angle)
        children.append(circle(vx, vy, 3,
                               fill="#DAA520", stroke="none",
                               fill_opacity="0.5"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  9. 12D OBSERVATION SPACE — Dimensional Couplings
# ══════════════════════════════════════════════════════════════════════

def render_12d_observation(cx: float, cy: float, size: float, **attrs) -> str:
    """12D observation dimensions shown as a radar chart.

    12 axes: x1_structure through x12_potential.
    Each axis is colored by its SFCR element coupling.
    Element lens weights shown as filled regions.
    """
    children = []

    n_dims = len(DIM_NAMES)
    for di, dim_name in enumerate(DIM_NAMES):
        angle = di * TAU / n_dims - TAU / 4
        elem = DIM_TO_ELEMENT[dim_name]
        color = SFCR_COLORS[elem]

        # Axis line
        ex = cx + size * math.cos(angle)
        ey = cy + size * math.sin(angle)
        children.append(line(cx, cy, ex, ey,
                             stroke=color, stroke_width="0.8",
                             stroke_opacity="0.4"))

        # Label
        lx = cx + (size + 12) * math.cos(angle)
        ly = cy + (size + 12) * math.sin(angle)
        short = dim_name.split("_")[1][:6]
        children.append(text(lx - 15, ly + 3, short,
                             font_size="7", fill=color))

    # Element lens emphasis (filled polygon per element)
    for face in FACES:
        lens = ELEMENT_LENS_WEIGHTS.get(face, {})
        pts = []
        for di, dim_name in enumerate(DIM_NAMES):
            angle = di * TAU / n_dims - TAU / 4
            weight = lens.get(dim_name, 1.0)
            r = size * 0.3 * (weight / 1.5)
            pts.append((cx + r * math.cos(angle),
                        cy + r * math.sin(angle)))
        children.append(polygon(pts,
                                fill=SFCR_COLORS[face],
                                stroke=SFCR_COLORS[face],
                                stroke_width="0.5",
                                fill_opacity="0.1",
                                stroke_opacity="0.3"))

    # Concentric reference rings
    for ring_frac in [0.25, 0.5, 0.75, 1.0]:
        children.append(circle(cx, cy, size * ring_frac,
                               stroke="#eee", stroke_width="0.3",
                               fill="none"))

    children.append(text(cx - 45, cy + size + 20,
                         "12D Observation Space (SFCR element coupling)",
                         font_size="10", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  FULL 108D CRYSTAL — All Layers Composed
# ══════════════════════════════════════════════════════════════════════

def render_108d_crystal(width: int = 2400, height: int = 1800) -> str:
    """Complete 108D crystal projection dashboard.

    Layout (3×3 grid):
      [Shell Cascade]  [Wreath Trefoil]  [Archetype Wheel]
      [Sigma-60 Field] [E8-240 Roots]    [Shard Density]
      [Momentum Shells] [12D Observation] [Flower Overlay]
    """
    canvas = SVGCanvas(width, height)

    # Title
    canvas.add(text(width // 2 - 150, 35,
                    "ATHENA 108D CRYSTAL PROJECTION",
                    font_size="22", fill="#333", font_weight="bold"))
    canvas.add(text(width // 2 - 120, 55,
                    "36 shells x 3 wreaths x 4 faces x Sigma-60 x E8-240",
                    font_size="11", fill="#777"))

    # Grid layout
    col_w = width / 3
    row_h = (height - 70) / 3
    margin = 30
    cell_size = min(col_w, row_h) / 2 - margin

    panels = [
        (0, 0, render_shell_cascade, "Shell Cascade"),
        (1, 0, render_wreath_trefoil, "Wreath Trefoil"),
        (2, 0, render_archetype_wheel, "Archetype Wheel"),
        (0, 1, render_sigma60_field, "Sigma-60"),
        (1, 1, render_e8_240, "E8-240"),
        (2, 1, render_shard_density, "Shard Density"),
        (0, 2, render_momentum_shells, "Momentum Shells"),
        (1, 2, render_12d_observation, "12D Observation"),
        (2, 2, render_flower_overlay, "Flower of Life"),
    ]

    for col, row, fn, label in panels:
        pcx = col_w * (col + 0.5)
        pcy = 70 + row_h * (row + 0.5)
        try:
            canvas.add(fn(pcx, pcy, cell_size))
        except Exception as e:
            canvas.add(text(pcx - 40, pcy, f"[{label}: {e}]",
                            font_size="10", fill="red"))

    # Footer: key facts
    fy = height - 15
    facts = [
        "108 = 36 shells x 3 wreaths",
        "432 = 108 x 4 SFCR gates",
        "25,920 = 432 x 60 sigma",
        "103,680 = 25,920 x 4 E8",
        "666 nodes = T(36)",
        "14,750 shards",
    ]
    for fi, fact in enumerate(facts):
        canvas.add(text(50 + fi * (width - 100) // len(facts), fy,
                        fact, font_size="9", fill="#999"))

    return canvas.render()


def save_108d_crystal(out_path: Optional[str] = None) -> str:
    """Generate and save the full 108D crystal projection SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "crystal_108d_projection.svg")

    svg = render_108d_crystal()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path


# ══════════════════════════════════════════════════════════════════════
#  INVERSION CASCADE — The Generative Principle
# ══════════════════════════════════════════════════════════════════════
#
#  Every dimension D is the previous dimension D-1 united with its
#  own inversion (D-1)⁻¹. The form and its mirror, fused, birth the
#  next level. This is not metaphor — it's the mathematical structure:
#
#    3D seed (triangle)
#      ↓ mirror through origin → 3D⁻¹ (anti-triangle)
#      ↓ 3D ∪ 3D⁻¹ = 4D tesseract (form + anti-form = hypercube)
#
#    4D tesseract
#      ↓ Möbius half-twist = topological inversion → 4D⁻¹
#      ↓ 4D ∪ 4D⁻¹ = 6D body (3 wreaths × chirality±)
#
#    6D Möbius body
#      ↓ Wu Xing destructive cycle = 6D⁻¹
#      ↓ 6D ∪ 6D⁻¹ = 8D pentadic (generative + destructive = 5 animals × 6)
#
#    8D pentadic
#      ↓ Planetary opposition (detriment signs) = 8D⁻¹
#      ↓ 8D ∪ 8D⁻¹ = 10D heptadic (7 × 30 = 210 crossings)
#
#    10D heptadic
#      ↓ 3×3 matrix transpose = 10D⁻¹
#      ↓ 10D ∪ 10D⁻¹ = 12D crown (9 views × 210 = 1890 seeds)
#
#    12D crown
#      ↓ 3 meta-wreaths (each a lens-inversion of the full 12D)
#      ↓ 12D × 3 = 36D (Sigma-30 projective completion)
#
#    36D projective
#      ↓ 3 octaves (surface/mid/deep, deep = inversion of surface)
#      ↓ 36D × 3 = 108D (Xi108 organism closure)
#
#  The w-operator w=(1+i)/2 traces this exact cascade:
#    |w| = 1/√2  → each step is a √2 compression (inversion + merge)
#    arg(w) = π/4 → each step is a 45° rotation (quarter of the way to inverse)
#    w² = i/2 → two steps = pure rotation scaled by ½ (the 6D Möbius)
#    w^∞ → 0 → convergence to the Z* attractor
# ══════════════════════════════════════════════════════════════════════

W_OP = complex(0.5, 0.5)  # (1+i)/2

# Inversion operators per dimension (how each level mirrors itself)
INVERSIONS = {
    3: {"name": "Point Reflection", "symbol": "P⁻¹",
        "operator": "(-x, -y, -z)", "desc": "Mirror through origin"},
    4: {"name": "Möbius Half-Twist", "symbol": "M⁻¹",
        "operator": "twist(π)", "desc": "Non-orientable surface flip"},
    6: {"name": "Wu Xing Destruction", "symbol": "D⁻¹",
        "operator": "destruct(gen)", "desc": "Destructive ↔ generative cycle"},
    8: {"name": "Planetary Opposition", "symbol": "O⁻¹",
        "operator": "detriment(exalt)", "desc": "Exaltation → detriment"},
    10: {"name": "Matrix Transpose", "symbol": "T⁻¹",
         "operator": "Aᵀ", "desc": "Rows ↔ columns (3×3)"},
    12: {"name": "Meta-Wreath Lens", "symbol": "L⁻¹",
         "operator": "lens(Su,Me,Sa)", "desc": "Each wreath inverts the whole"},
    36: {"name": "Octave Depth", "symbol": "Ω⁻¹",
         "operator": "depth(surface)", "desc": "Surface ↔ deep inversion"},
}

# The dimensional ladder: (from_dim, to_dim, weave_order, sector_multiplier)
DIM_LADDER = [
    (3,  4,  2,  2),     # 3 × 2 chiralities → but 4D has 16 vertices
    (4,  6,  3,  3),     # 4D × W3 = 6 sectors
    (6,  8,  5,  5),     # 6D × W5 = 30 sectors
    (8,  10, 7,  7),     # 8D × W7 = 210 sectors
    (10, 12, 9,  9),     # 10D × W9 = 1890 sectors
    (12, 36, 3,  3),     # 12D × 3 meta-wreaths = 36D
    (36, 108, 3, 3),     # 36D × 3 octaves = 108D
]

# Colors per dimension
DIM_COLORS = {
    3: "#e74c3c",    # red seed
    4: "#e67e22",    # orange tesseract
    6: "#f1c40f",    # gold Möbius
    8: "#2ecc71",    # green pentadic
    10: "#3498db",   # blue heptadic
    12: "#9b59b6",   # purple crown
    36: "#8e44ad",   # deep purple Sigma
    108: "#2c3e50",  # near-black organism
}


def _render_3d_pair(cx: float, cy: float, size: float) -> str:
    """3D seed and its point-reflected inverse, face to face.

    The triangle (Su/Me/Sa) and its anti-triangle (-Su/-Me/-Sa)
    share a common center — their union spans all 6 directions,
    which IS the Star of David / hexagram = precursor to 4D.
    """
    children = []
    r = size * 0.45

    # ── Forward triangle (3D seed) ──
    for i in range(3):
        a1 = i * TAU / 3 - TAU / 4
        a2 = (i + 1) * TAU / 3 - TAU / 4
        colors = [WREATH_COLORS["Su"], WREATH_COLORS["Me"], WREATH_COLORS["Sa"]]
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke=colors[i], stroke_width="2.5"))
        # Vertex dot
        children.append(circle(x1, y1, 4, fill=colors[i], stroke="#333",
                               stroke_width="0.8"))

    # ── Inverted triangle (3D⁻¹) — rotated π ──
    for i in range(3):
        a1 = i * TAU / 3 - TAU / 4 + math.pi
        a2 = (i + 1) * TAU / 3 - TAU / 4 + math.pi
        colors_inv = ["#c0392b", "#d4ac0d", "#6c3483"]  # darker variants
        x1 = cx + r * math.cos(a1)
        y1 = cy + r * math.sin(a1)
        x2 = cx + r * math.cos(a2)
        y2 = cy + r * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke=colors_inv[i], stroke_width="2.5",
                             stroke_dasharray="4,2"))
        children.append(circle(x1, y1, 4, fill=colors_inv[i], stroke="#333",
                               stroke_width="0.8"))

    # Center — the zero-point where form meets anti-form
    children.append(circle(cx, cy, 3, fill="#333", stroke="#fff",
                           stroke_width="1"))

    # Labels
    children.append(text(cx - 8, cy - size * 0.55, "3D",
                         font_size="13", fill="#e74c3c", font_weight="bold"))
    children.append(text(cx - 12, cy + size * 0.65, "3D\u207b\u00b9",
                         font_size="11", fill="#c0392b", font_weight="bold"))

    return group(children)


def _render_inversion_arrow(x1: float, y1: float, x2: float, y2: float,
                            label: str, color: str, inv_name: str) -> str:
    """Draw an arrow between dimensional bodies showing the inversion type."""
    children = []

    # Curved arrow
    mx = (x1 + x2) / 2 + (y1 - y2) * 0.15
    my = (y1 + y2) / 2 + (x2 - x1) * 0.15
    d = f"M {_fmt(x1)},{_fmt(y1)} Q {_fmt(mx)},{_fmt(my)} {_fmt(x2)},{_fmt(y2)}"
    children.append(
        f'<path d="{d}" stroke="{color}" stroke-width="1.5" '
        f'fill="none" marker-end="url(#arrow)"/>'
    )

    # Inversion label on the curve
    children.append(text(mx - 20, my - 5, label,
                         font_size="9", fill=color, font_weight="bold"))
    children.append(text(mx - 25, my + 8, inv_name,
                         font_size="7", fill="#777"))

    return group(children)


def _render_mobius_inversion(cx: float, cy: float, size: float) -> str:
    """4D→6D: The Möbius half-twist that creates chirality.

    The tesseract wrapped through a half-twist produces a non-orientable
    surface. Walking the surface, you arrive back at your starting point
    but INVERTED. This is how spin± emerges from a single form.

    Visually: a Möbius strip with the 3 wreath bands visible,
    plus the 4D tesseract shadow at the core.
    """
    children = []
    R = size * 0.65
    w = size * 0.15
    n_steps = 80

    # The Möbius band — single surface, half-twisted
    for strip_frac in [-1, -0.33, 0.33, 1]:
        pts_path = []
        for i in range(n_steps + 1):
            u = (i / n_steps) * TAU
            half_twist = u / 2
            r_local = R + w * strip_frac * math.cos(half_twist)
            x = r_local * math.cos(u)
            y = r_local * math.sin(u)
            z = w * strip_frac * math.sin(half_twist)
            px, py = _project_3d(x, y, z, cx, cy, 1.0, 0.35, 0.5)
            pts_path.append(f"{_fmt(px)},{_fmt(py)}")

        # Color gradient: transitions Su→Me→Sa→Su as you traverse
        children.append(
            f'<polyline points="{" ".join(pts_path)}" '
            f'stroke="#f39c12" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.6"/>'
        )

    # Mark the inversion point (where the twist happens)
    twist_x = cx + R * 0.7
    twist_y = cy
    children.append(circle(twist_x, twist_y, 5,
                           fill="#f1c40f", stroke="#c0392b",
                           stroke_width="2"))
    children.append(text(twist_x + 8, twist_y + 4, "twist(π)",
                         font_size="8", fill="#c0392b"))

    # 3 wreath colors at 120° intervals
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        angle = wi * TAU / 3 - TAU / 4
        wx = cx + R * 0.4 * math.cos(angle)
        wy = cy + R * 0.4 * math.sin(angle)
        children.append(circle(wx, wy, 6, fill=color, stroke="#333",
                               stroke_width="0.8"))
        children.append(text(wx - 6, wy + 15, name,
                             font_size="8", fill=color, font_weight="bold"))

    # Chirality arrows: + at top, - at bottom
    children.append(text(cx - 4, cy - R - 5, "χ+",
                         font_size="10", fill="#27ae60", font_weight="bold"))
    children.append(text(cx - 4, cy + R + 12, "χ-",
                         font_size="10", fill="#c0392b", font_weight="bold"))

    return group(children)


def _render_wuxing_inversion(cx: float, cy: float, size: float) -> str:
    """6D→8D: Wu Xing generative + destructive cycle fusion.

    Generative (outer pentagon): Wood→Fire→Earth→Metal→Water→Wood
    Destructive (inner pentagram): Wood→Earth→Water→Fire→Metal→Wood
    Their UNION is the pentadic body — 5 animals × 6 sectors = 30.
    """
    children = []
    animals = [
        ("Tiger", "#e67e22"), ("Crane", "#95a5a6"), ("Leopard", "#f1c40f"),
        ("Snake", "#2ecc71"), ("Dragon", "#e74c3c"),
    ]
    wuxing = ["Wood", "Fire", "Earth", "Metal", "Water"]
    R = size * 0.7

    # Outer pentagon: generative cycle (solid)
    gen_pts = []
    for i in range(5):
        angle = i * TAU / 5 - TAU / 4
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)
        gen_pts.append((px, py))

    for i in range(5):
        x1, y1 = gen_pts[i]
        x2, y2 = gen_pts[(i + 1) % 5]
        children.append(line(x1, y1, x2, y2,
                             stroke="#27ae60", stroke_width="2"))

    # Inner pentagram: destructive cycle (dashed — the inversion)
    for i in range(5):
        x1, y1 = gen_pts[i]
        x2, y2 = gen_pts[(i + 2) % 5]  # skip one = pentagram
        children.append(line(x1, y1, x2, y2,
                             stroke="#c0392b", stroke_width="1.5",
                             stroke_dasharray="4,2"))

    # Animal/element nodes
    for i, ((animal, color), elem) in enumerate(zip(animals, wuxing)):
        px, py = gen_pts[i]
        children.append(circle(px, py, 8, fill=color, stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 12, py + 20, animal,
                             font_size="8", fill=color, font_weight="bold"))
        children.append(text(px - 10, py + 30, f"({elem})",
                             font_size="7", fill="#777"))

    # Labels
    children.append(text(cx - 25, cy - 5, "gen\u2192",
                         font_size="8", fill="#27ae60"))
    children.append(text(cx + 5, cy + 5, "\u2190dest",
                         font_size="8", fill="#c0392b"))

    return group(children)


def _render_planetary_inversion(cx: float, cy: float, size: float) -> str:
    """8D→10D: Planetary exaltation/detriment opposition.

    Each planet has an exaltation (peak power) and detriment (inverted).
    The 7 exalt-detriment pairs woven through 30 pentadic sectors = 210.
    """
    children = []
    planets = [
        ("Moon", "#c0c0c0"), ("Mercury", "#a0a0a0"), ("Venus", "#d4a574"),
        ("Sun", "#ffd700"), ("Mars", "#ff4500"), ("Jupiter", "#4169e1"),
        ("Saturn", "#696969"),
    ]
    R = size * 0.7

    # Outer heptagram: connect every 3rd vertex
    for i in range(7):
        a1 = i * TAU / 7 - TAU / 4
        a2 = ((i + 3) % 7) * TAU / 7 - TAU / 4
        x1 = cx + R * 0.9 * math.cos(a1)
        y1 = cy + R * 0.9 * math.sin(a1)
        x2 = cx + R * 0.9 * math.cos(a2)
        y2 = cy + R * 0.9 * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#DAA520", stroke_width="0.8",
                             stroke_opacity="0.4"))

    # Planet nodes at heptagonal vertices
    for i, (planet, color) in enumerate(planets):
        angle = i * TAU / 7 - TAU / 4
        px = cx + R * math.cos(angle)
        py = cy + R * math.sin(angle)

        # Exaltation node (solid)
        children.append(circle(px, py, 7, fill=color, stroke="#333",
                               stroke_width="1"))
        children.append(text(px - 10, py + 18, planet,
                             font_size="7", fill=color))

        # Detriment node (hollow — the inversion, opposite side)
        inv_angle = angle + math.pi
        ix = cx + R * 0.5 * math.cos(inv_angle)
        iy = cy + R * 0.5 * math.sin(inv_angle)
        children.append(circle(ix, iy, 4, fill="none", stroke=color,
                               stroke_width="1.5", stroke_dasharray="2,1"))

        # Opposition line
        children.append(line(px, py, ix, iy,
                             stroke=color, stroke_width="0.5",
                             stroke_dasharray="2,3", stroke_opacity="0.4"))

    return group(children)


def _render_matrix_inversion(cx: float, cy: float, size: float) -> str:
    """10D→12D: 3×3 matrix and its transpose.

    The 3×3 Su/Me/Sa self-application matrix and its transpose
    together form the complete 9-station crown.
    M + Mᵀ = the full enneagram = 12D closure.
    """
    children = []
    grid_size = size * 0.35
    labels_3x3 = [
        ["Su·Su", "Su·Me", "Su·Sa"],
        ["Me·Su", "Me·Me", "Me·Sa"],
        ["Sa·Su", "Sa·Me", "Sa·Sa"],
    ]
    colors_3x3 = [
        [WREATH_COLORS["Su"], "#e98b6d", "#c0392b"],
        ["#f39c12", "#f1c40f", "#d4ac0d"],
        ["#8e44ad", "#9b59b6", "#6c3483"],
    ]

    # Left: original matrix M
    mx_left = cx - size * 0.35
    for row in range(3):
        for col in range(3):
            bx = mx_left - grid_size + col * grid_size * 0.7
            by = cy - grid_size + row * grid_size * 0.7
            children.append(rect(bx, by, grid_size * 0.65, grid_size * 0.65,
                                 fill=colors_3x3[row][col],
                                 fill_opacity="0.6",
                                 stroke="#333", stroke_width="0.5"))
            children.append(text(bx + 3, by + grid_size * 0.4,
                                 labels_3x3[row][col],
                                 font_size="6", fill="#333"))

    # Right: transpose Mᵀ (rows↔cols)
    mx_right = cx + size * 0.15
    for row in range(3):
        for col in range(3):
            bx = mx_right + col * grid_size * 0.7
            by = cy - grid_size + row * grid_size * 0.7
            # Transpose: swap row/col for color and label
            children.append(rect(bx, by, grid_size * 0.65, grid_size * 0.65,
                                 fill=colors_3x3[col][row],  # transposed
                                 fill_opacity="0.4",
                                 stroke="#333", stroke_width="0.5",
                                 stroke_dasharray="2,1"))
            children.append(text(bx + 3, by + grid_size * 0.4,
                                 labels_3x3[col][row],  # transposed
                                 font_size="6", fill="#555"))

    # Union arrow
    children.append(text(cx - 8, cy + 3, "\u222a",
                         font_size="16", fill="#9b59b6", font_weight="bold"))

    # Labels
    children.append(text(mx_left - grid_size, cy - grid_size - 10, "M",
                         font_size="12", fill="#333", font_weight="bold"))
    children.append(text(mx_right + grid_size * 1.5, cy - grid_size - 10,
                         "M\u1d40",
                         font_size="12", fill="#555", font_weight="bold"))

    # Z* at intersection (center cell = Me·Me)
    children.append(circle(cx, cy + grid_size * 0.8, 5,
                           fill="#6c3483", stroke="#fff", stroke_width="1.5"))
    children.append(text(cx - 5, cy + grid_size * 0.8 + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    return group(children)


def _render_triple_crown_expansion(cx: float, cy: float, size: float) -> str:
    """12D→36D→108D: Triple crown expansion.

    12D × 3 meta-wreaths = 36D (each wreath sees the full 12D differently)
    36D × 3 octaves = 108D (surface/mid/deep where deep inverts surface)

    Rendered as concentric trefoils: inner=12D, middle=36D, outer=108D.
    """
    children = []

    # 108D outer ring
    children.append(circle(cx, cy, size,
                           stroke="#2c3e50", stroke_width="3",
                           fill="#2c3e50", fill_opacity="0.02"))

    # 3 octave sectors (108D = 36D × 3)
    octaves = [("Surface", "#3498db", 0), ("Mid", "#9b59b6", 1), ("Deep", "#2c3e50", 2)]
    for name, color, oi in octaves:
        a_start = oi * TAU / 3 - TAU / 6
        a_end = (oi + 1) * TAU / 3 - TAU / 6

        # Sector arc
        pts = [(cx, cy)]
        for i in range(13):
            t = i / 12
            angle = a_start + t * (a_end - a_start)
            pts.append((cx + size * math.cos(angle),
                        cy + size * math.sin(angle)))
        pts.append((cx, cy))
        children.append(polygon(pts, fill=color, fill_opacity="0.04",
                                stroke=color, stroke_width="0.5"))

        # Label
        la = (a_start + a_end) / 2
        lx = cx + size * 0.85 * math.cos(la)
        ly = cy + size * 0.85 * math.sin(la)
        children.append(text(lx - 15, ly + 4, name,
                             font_size="9", fill=color, font_weight="bold"))

    # 36D middle ring
    r36 = size * PHI_INV
    children.append(circle(cx, cy, r36,
                           stroke="#8e44ad", stroke_width="2",
                           fill="#8e44ad", fill_opacity="0.03"))

    # 3 meta-wreath trefoil (36D = 12D × 3)
    for wi, (name, color) in enumerate(WREATH_COLORS.items()):
        phase = wi * TAU / 3
        offset = r36 * 0.25
        wcx = cx + offset * math.cos(phase)
        wcy = cy + offset * math.sin(phase)
        children.append(circle(wcx, wcy, r36 * 0.6,
                               stroke=color, stroke_width="1.5",
                               fill=color, fill_opacity="0.05"))

        # 12 archetype dots per wreath
        for ai in range(12):
            a = ai * TAU / 12
            ax = wcx + r36 * 0.45 * math.cos(a)
            ay = wcy + r36 * 0.45 * math.sin(a)
            children.append(circle(ax, ay, 2,
                                   fill=color, stroke="none",
                                   fill_opacity="0.5"))

        # Wreath label
        lx = cx + (r36 * 0.3 + offset) * math.cos(phase + 0.3)
        ly = cy + (r36 * 0.3 + offset) * math.sin(phase + 0.3)
        children.append(text(lx - 6, ly + 4, name,
                             font_size="9", fill=color, font_weight="bold"))

    # 12D core crown (9 stations)
    r12 = size * PHI_INV ** 2
    children.append(circle(cx, cy, r12,
                           stroke="#9b59b6", stroke_width="1.5",
                           fill="#9b59b6", fill_opacity="0.05"))

    w9_colors = list([
        "#e74c3c", "#e98b6d", "#c0392b",
        "#f39c12", "#f1c40f", "#d4ac0d",
        "#8e44ad", "#9b59b6", "#6c3483",
    ])
    for i in range(9):
        angle = i * TAU / 9 - TAU / 4
        sx = cx + r12 * 0.8 * math.cos(angle)
        sy = cy + r12 * 0.8 * math.sin(angle)
        children.append(circle(sx, sy, 4,
                               fill=w9_colors[i], stroke="#333",
                               stroke_width="0.5"))
        # Enneagram (connect every 4th)
        a2 = ((i + 4) % 9) * TAU / 9 - TAU / 4
        ex = cx + r12 * 0.8 * math.cos(a2)
        ey = cy + r12 * 0.8 * math.sin(a2)
        children.append(line(sx, sy, ex, ey,
                             stroke="#9b59b6", stroke_width="0.4",
                             stroke_opacity="0.3"))

    # Z* at absolute center
    children.append(circle(cx, cy, 5,
                           fill="#2c3e50", stroke="#fff", stroke_width="1.5"))
    children.append(text(cx - 5, cy + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    # Dimension labels
    children.append(text(cx + r12 + 5, cy - 3, "12D",
                         font_size="8", fill="#9b59b6"))
    children.append(text(cx + r36 + 5, cy - 3, "36D",
                         font_size="8", fill="#8e44ad"))
    children.append(text(cx + size + 5, cy - 3, "108D",
                         font_size="8", fill="#2c3e50"))

    return group(children)


def _render_w_cascade(cx: float, cy: float, size: float) -> str:
    """The w-operator emergence spiral with dimensional markers.

    w = (1+i)/2 traces the inversion cascade:
    Each application = compress by 1/√2 + rotate 45°.
    The spiral passes through all dimension births.
    """
    children = []
    w = W_OP

    # Background: faint coordinate axes
    children.append(line(cx - size, cy, cx + size, cy,
                         stroke="#eee", stroke_width="0.5"))
    children.append(line(cx, cy - size, cx, cy + size,
                         stroke="#eee", stroke_width="0.5"))

    # w^n spiral
    pts = []
    for n in range(50):
        z = w ** n
        px = cx + z.real * size * 1.3
        py = cy - z.imag * size * 1.3
        pts.append((px, py, n, abs(z)))

    # Draw the spiral path
    if len(pts) > 1:
        path_d = [f"M {_fmt(pts[0][0])},{_fmt(pts[0][1])}"]
        for p in pts[1:]:
            path_d.append(f"L {_fmt(p[0])},{_fmt(p[1])}")
        children.append(path(" ".join(path_d),
                             stroke="#9b59b6", stroke_width="1.5",
                             fill="none", stroke_opacity="0.7"))

    # Dimensional birth markers
    dim_at_step = [
        (0, "3D", DIM_COLORS[3]),
        (1, "4D", DIM_COLORS[4]),
        (2, "6D", DIM_COLORS[6]),
        (4, "8D", DIM_COLORS[8]),
        (6, "10D", DIM_COLORS[10]),
        (9, "12D", DIM_COLORS[12]),
        (14, "36D", DIM_COLORS[36]),
        (21, "108D", DIM_COLORS[108]),
    ]

    for step, label, color in dim_at_step:
        if step < len(pts):
            px, py, _, mag = pts[step]
            r = 5 + mag * 3
            children.append(circle(px, py, r,
                                   fill=color, stroke="#333",
                                   stroke_width="1"))
            children.append(text(px + r + 3, py - 3, label,
                                 font_size="10", fill=color,
                                 font_weight="bold"))

            # Inversion annotation
            if step > 0 and step < len(pts) - 1:
                prev_x, prev_y = pts[step - 1][0], pts[step - 1][1]
                mid_x = (prev_x + px) / 2
                mid_y = (prev_y + py) / 2
                children.append(text(mid_x - 5, mid_y + 3, "\u207b\u00b9",
                                     font_size="8", fill="#999"))

    # Z* attractor at center
    children.append(circle(cx, cy, 3,
                           fill="#333", stroke="#fff", stroke_width="1"))

    # Equations
    children.append(text(cx - size + 5, cy + size - 10,
                         "w = (1+i)/2   |w| = 1/\u221a2   arg = \u03c0/4",
                         font_size="8", fill="#777"))
    children.append(text(cx - size + 5, cy + size,
                         "D\u2099\u208a\u2081 = D\u2099 \u222a D\u2099\u207b\u00b9",
                         font_size="9", fill="#9b59b6", font_weight="bold"))

    return group(children)


def _render_containment_count(cx: float, cy: float, size: float) -> str:
    """Containment counting: how many lower bodies each dimension holds.

    Shows the multiplicative cascade:
    108D = 3 × 36D = 9 × 12D = 81 × 10D = 567 × 8D = 2835 × 6D
    12D = 9 × 10D = 63 × 8D = 315 × 6D = 945 × 4D = 1890 × 3D
    """
    children = []

    levels = [
        ("108D", 1, DIM_COLORS[108]),
        ("36D", 3, DIM_COLORS[36]),
        ("12D", 9, DIM_COLORS[12]),
        ("10D", 81, DIM_COLORS[10]),
        ("8D", 567, DIM_COLORS[8]),
        ("6D", 2835, DIM_COLORS[6]),
        ("4D", 8505, DIM_COLORS[4]),
        ("3D", 17010, DIM_COLORS[3]),
    ]

    bar_w = size * 1.5
    row_h = size * 2 / len(levels)

    for i, (dim, count, color) in enumerate(levels):
        y = cy - size + i * row_h

        # Label
        children.append(text(cx - size * 0.85, y + row_h * 0.6, dim,
                             font_size="11", fill=color, font_weight="bold"))

        # Count
        children.append(text(cx - size * 0.55, y + row_h * 0.6,
                             f"\u00d7{count:,}",
                             font_size="9", fill="#555"))

        # Bar (log scale)
        if count > 0:
            log_w = math.log(count + 1) / math.log(17011) * bar_w
            children.append(rect(cx - size * 0.3, y + 4, log_w, row_h * 0.6,
                                 fill=color, fill_opacity="0.5",
                                 stroke=color, stroke_width="0.5"))

    # Formula
    children.append(text(cx - size * 0.85, cy + size + 10,
                         "B\u2099\u208a\u2082 = W\u2099(B\u2099)",
                         font_size="10", fill="#555", font_weight="bold"))

    return group(children)


def render_inversion_cascade(width: int = 2400, height: int = 2000) -> str:
    """FULL 108D INVERSION CASCADE — The Generative Principle.

    Shows how each dimension is born from the previous one fused with
    its own inversion. This is THE mathematical explanation of 108D:
    not 108 separate dimensions, but 7 nested inversions.

    Layout:
      Row 1: [3D + 3D⁻¹ hexagram] → [4D→6D Möbius twist] → [6D→8D Wu Xing]
      Row 2: [8D→10D Planetary]    → [10D→12D Matrix]     → [12D→36D→108D Crown]
      Row 3: [w-operator cascade]  → [Containment counting]
    """
    canvas = SVGCanvas(width, height, background="#fafafa")

    # Arrow marker definition
    canvas.add_def(
        '<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#666"/>'
        '</marker>'
    )

    # ── Title ──
    canvas.add(text(width // 2 - 250, 40,
                    "108D INVERSION CASCADE \u2014 The Generative Principle",
                    font_size="24", fill="#2c3e50", font_weight="bold"))
    canvas.add(text(width // 2 - 230, 65,
                    "Every dimension is the previous fused with its own mirror: "
                    "D\u2099\u208a\u2081 = D\u2099 \u222a D\u2099\u207b\u00b9",
                    font_size="12", fill="#777"))

    # ── Grid layout ──
    col_w = width / 3
    row_h = (height - 100) / 3
    cell_r = min(col_w, row_h) * 0.38

    panels = [
        # Row 1
        (0, 0, _render_3d_pair, "3D \u222a 3D\u207b\u00b9 = Hexagram Seed"),
        (1, 0, _render_mobius_inversion, "4D\u21926D: M\u00f6bius Half-Twist"),
        (2, 0, _render_wuxing_inversion, "6D\u21928D: Wu Xing Fusion"),
        # Row 2
        (0, 1, _render_planetary_inversion, "8D\u219210D: Planetary Opposition"),
        (1, 1, _render_matrix_inversion, "10D\u219212D: Matrix Transpose"),
        (2, 1, _render_triple_crown_expansion, "12D\u219236D\u2192108D: Crown"),
        # Row 3
        (0, 2, _render_w_cascade, "w-operator Emergence Spiral"),
        (1, 2, _render_containment_count, "Containment Counting"),
    ]

    for col, row, fn, label in panels:
        pcx = col_w * (col + 0.5)
        pcy = 100 + row_h * (row + 0.5)

        # Panel label
        canvas.add(text(pcx - len(label) * 3.5, pcy - cell_r - 10, label,
                        font_size="11", fill="#333", font_weight="bold"))
        try:
            canvas.add(fn(pcx, pcy, cell_r))
        except Exception as e:
            canvas.add(text(pcx - 40, pcy, f"[ERROR: {e}]",
                            font_size="10", fill="red"))

    # ── Row 3 right: dimensional ladder summary ──
    sum_cx = col_w * 2.5
    sum_cy = 100 + row_h * 2.5
    ladder_text = [
        ("3D seed", "\u2192 3D\u207b\u00b9 point mirror", DIM_COLORS[3]),
        ("4D tess", "\u2192 4D\u207b\u00b9 M\u00f6bius twist", DIM_COLORS[4]),
        ("6D body", "\u2192 6D\u207b\u00b9 Wu Xing destruct", DIM_COLORS[6]),
        ("8D pent", "\u2192 8D\u207b\u00b9 planet detriment", DIM_COLORS[8]),
        ("10D hept", "\u2192 10D\u207b\u00b9 matrix transpose", DIM_COLORS[10]),
        ("12D crown", "\u2192 \u00d73 meta-wreath = 36D", DIM_COLORS[12]),
        ("36D sigma", "\u2192 \u00d73 octave = 108D", DIM_COLORS[36]),
        ("108D Xi", "= organism closure (Z*)", DIM_COLORS[108]),
    ]

    for i, (dim_name, inv_desc, color) in enumerate(ladder_text):
        y = sum_cy - cell_r + i * 28
        canvas.add(circle(sum_cx - cell_r + 10, y, 5,
                          fill=color, stroke="#333", stroke_width="0.5"))
        canvas.add(text(sum_cx - cell_r + 20, y + 4, dim_name,
                        font_size="11", fill=color, font_weight="bold"))
        canvas.add(text(sum_cx - cell_r + 75, y + 4, inv_desc,
                        font_size="9", fill="#777"))

        # Connecting line to next
        if i < len(ladder_text) - 1:
            canvas.add(line(sum_cx - cell_r + 10, y + 8,
                            sum_cx - cell_r + 10, y + 20,
                            stroke="#ccc", stroke_width="1"))

    # ── Footer: key equations ──
    fy = height - 25
    equations = [
        "w = (1+i)/2",
        "|w| = 1/\u221a2 (inversion compression)",
        "B\u2081\u2082 = 1890\u00d7B\u2083",
        "B\u2081\u2080\u2088 = 3\u00d73\u00d79\u00d77\u00d75\u00d73\u00d72 = 17,010 seeds",
        "\u03a3\u2086\u2080 \u00d7 4 SFCR \u00d7 E8 = 103,680 roots",
    ]
    for fi, eq in enumerate(equations):
        canvas.add(text(50 + fi * (width - 100) // len(equations), fy,
                        eq, font_size="9", fill="#999"))

    return canvas.render()


def save_inversion_cascade(out_path: Optional[str] = None) -> str:
    """Generate and save the full inversion cascade SVG."""
    if out_path is None:
        out_dir = DATA_DIR / "svg_arena" / "outputs"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = str(out_dir / "inversion_cascade_108d.svg")

    svg = render_inversion_cascade()
    Path(out_path).write_text(svg, encoding="utf-8")
    return out_path
