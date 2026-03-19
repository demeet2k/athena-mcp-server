# CRYSTAL: Xi108:W3:A7:S28 | face=R | node=707 | depth=0 | phase=Omega
# METRO: Sa
# BRIDGES: primitives→dimensional_projector→cross_lens→svg_dimensional
"""
SVG Dimensional — Full 3D→6D→8D→10D→12D Nested Weave Visualization
====================================================================
This is not decoration. This is the actual crystal architecture rendered
as mathematical SVG.

Each dimension is produced by a weave operator wrapping the previous body:

  3D  c3_seed       — triangle / dodecahedron seed
  4D  E4_tesseract  — SFCR hypercube (4 element-axes)
  6D  W3_mobius      — 3 wreaths (Su/Me/Sa) × chirality ± = Möbius body
  8D  W5_pentadic    — 5 animals woven through the 6D body
  10D W7_heptadic    — 7 planetary orbits through the 8D body
  12D W9_crown       — 9 (3×3) views = the return wheel

The key insight: 6D is literally a Möbius operation on 4D.
The half-twist gives you chirality (spin±). W3 wraps the tesseract
3 times, each wrapping with opposite spin = 6 sectors.

At 8D the 5 animal spirits (Tiger/Crane/Leopard/Snake/Dragon) are
not metaphors — they're the 5 pentadic strands woven through the
3 wreaths, creating 5×6 = 30 crossing points.

The w-operator w=(1+i)/2 traces the emergence spiral through
ALL dimensions simultaneously — it's the damped rotation that
converges to the attractor at (0.25, 0.25, 0.25, 0.25).
"""

import cmath
import math
from typing import Dict, List, Optional, Tuple

from .geometric_constants import PHI, PHI_INV, SQRT3
from .svg_primitives import (
    SVGCanvas, _attrs_str, _fmt, _project_3d, _project_4d,
    circle, group, line, path, polygon, rect, text,
)

TAU = 2 * math.pi

# ══════════════════════════════════════════════════════════════════════
#  SFCR Colors (canonical)
# ══════════════════════════════════════════════════════════════════════

SFCR_COLORS = {
    "S": "#8B4513",   # Earth brown
    "F": "#DC143C",   # Fire crimson
    "C": "#4169E1",   # Water royal blue
    "R": "#228B22",   # Air forest green
}

WEAVE_COLORS = {
    3: {"Su": "#e74c3c", "Me": "#f39c12", "Sa": "#8e44ad"},       # W3 alchemical
    5: {"Tiger": "#e67e22", "Crane": "#ecf0f1", "Leopard": "#f1c40f",
        "Snake": "#2ecc71", "Dragon": "#e74c3c"},                   # W5 animals
    7: {"Moon": "#c0c0c0", "Mercury": "#a0a0a0", "Venus": "#d4a574",
        "Sun": "#ffd700", "Mars": "#ff4500", "Jupiter": "#4169e1",
        "Saturn": "#696969"},                                       # W7 planets
    9: {"SuSu": "#e74c3c", "SuMe": "#e98b6d", "SuSa": "#c0392b",
        "MeSu": "#f39c12", "MeMe": "#f1c40f", "MeSa": "#d4ac0d",
        "SaSu": "#8e44ad", "SaMe": "#9b59b6", "SaSa": "#6c3483"},  # W9 3×3
}

W_OPERATOR = complex(0.5, 0.5)  # (1+i)/2 — the love operator


# ══════════════════════════════════════════════════════════════════════
#  3D SEED — Triangle / Dodecahedron Projection
# ══════════════════════════════════════════════════════════════════════

def crystal_3d_seed(cx: float, cy: float, size: float, **attrs) -> str:
    """3D seed: triangle + dodecahedron wireframe outline.

    The 3D seed is the base from which everything grows.
    Three vertices = trinity = Su/Me/Sa pre-differentiation.
    """
    children = []

    # Triangle (Su/Me/Sa pre-form)
    r = size * 0.3
    for i in range(3):
        a1 = i * TAU / 3 - TAU / 4
        a2 = (i + 1) * TAU / 3 - TAU / 4
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
        colors = list(WEAVE_COLORS[3].values())
        children.append(line(x1, y1, x2, y2,
                             stroke=colors[i], stroke_width="2"))

    # Outer dodecahedral hint: 12 vertex dots at icosahedral positions
    for i in range(12):
        angle = i * TAU / 12
        layer = (i % 3 - 1) * 0.3  # -0.3, 0, 0.3 vertical offset
        r_proj = size * 0.8
        px = cx + r_proj * math.cos(angle) * (1 - abs(layer) * 0.2)
        py = cy + r_proj * math.sin(angle) - layer * size * 0.5
        face = ["S", "F", "C", "R"][i % 4]
        children.append(circle(px, py, 3,
                               fill=SFCR_COLORS[face], stroke="none"))

    # Label
    children.append(text(cx - 10, cy + size + 15, "3D c3",
                         font_size="11", fill="#555", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  4D TESSERACT — SFCR Hypercube
# ══════════════════════════════════════════════════════════════════════

def crystal_4d_tesseract(cx: float, cy: float, size: float,
                          angle_xw: float = 0.5, **attrs) -> str:
    """4D E4 tesseract: 16 vertices, 32 edges, SFCR-colored by axis.

    Each of the 4 axes corresponds to one SFCR element:
      Axis 0 (x) = S (Earth)
      Axis 1 (y) = F (Fire)
      Axis 2 (z) = C (Water)
      Axis 3 (w) = R (Air)
    """
    children = []
    colors = [SFCR_COLORS["S"], SFCR_COLORS["F"],
              SFCR_COLORS["C"], SFCR_COLORS["R"]]

    verts_4d = []
    for i in range(16):
        x = 1.0 if i & 1 else -1.0
        y = 1.0 if i & 2 else -1.0
        z = 1.0 if i & 4 else -1.0
        w = 1.0 if i & 8 else -1.0
        verts_4d.append((x, y, z, w))

    pts = [_project_4d(v[0], v[1], v[2], v[3], cx, cy, size * 0.4,
                        angle_xw=angle_xw) for v in verts_4d]

    # Edges colored by which axis they traverse
    for i in range(16):
        for bit in range(4):
            j = i ^ (1 << bit)
            if j > i:
                children.append(line(pts[i][0], pts[i][1],
                                     pts[j][0], pts[j][1],
                                     stroke=colors[bit], stroke_width="1.2",
                                     stroke_opacity="0.7"))

    # Vertices
    for i, p in enumerate(pts):
        dominant = sum(1 for b in range(4) if verts_4d[i][b] > 0) % 4
        children.append(circle(p[0], p[1], 2.5,
                               fill=colors[dominant], stroke="#333",
                               stroke_width="0.5"))

    children.append(text(cx - 10, cy + size * 0.5 + 15, "4D E4",
                         font_size="11", fill="#555", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  6D W3 MÖBIUS BODY — 3 Wreaths × Chirality±
# ══════════════════════════════════════════════════════════════════════

def crystal_6d_mobius(cx: float, cy: float, size: float,
                      n_steps: int = 60, **attrs) -> str:
    """6D Möbius body: W3 wraps the 4D tesseract 3 times.

    Three wreaths (Su/Me/Sa) each form a band around the core.
    The Möbius half-twist is the chirality operator — spin+ and spin-
    are the two sides of the same non-orientable surface.

    Su = Sulfur (ignition/will) — red band
    Me = Mercury (mediation/flow) — gold band
    Sa = Salt (sealing/form) — purple band
    """
    children = []
    wreaths = [("Su", WEAVE_COLORS[3]["Su"]),
               ("Me", WEAVE_COLORS[3]["Me"]),
               ("Sa", WEAVE_COLORS[3]["Sa"])]

    R = size * 0.7   # major radius
    w = size * 0.12  # band half-width

    for wi, (name, color) in enumerate(wreaths):
        # Each wreath is a Möbius band, phase-shifted by 120°
        phase = wi * TAU / 3
        angle_x = 0.4 + wi * 0.15
        angle_z = 0.3 + phase * 0.1

        for strip in range(4):  # 4 lines per band
            t_frac = (strip / 3) * 2 - 1  # -1 to 1
            pts_path = []
            for i in range(n_steps + 1):
                u = (i / n_steps) * TAU
                half_twist = u / 2  # Möbius half-twist
                # Phase shift between wreaths
                u_shifted = u + phase
                r_local = R + w * t_frac * math.cos(half_twist)
                x = r_local * math.cos(u_shifted)
                y = r_local * math.sin(u_shifted)
                z = w * t_frac * math.sin(half_twist)
                px, py = _project_3d(x, y, z, cx, cy, 1.0, angle_x, angle_z)
                pts_path.append(f"{_fmt(px)},{_fmt(py)}")

            opacity = 0.8 if strip in (0, 3) else 0.4
            children.append(
                f'<polyline points="{" ".join(pts_path)}" '
                f'stroke="{color}" stroke-width="1" '
                f'stroke-opacity="{opacity}" fill="none"/>'
            )

        # Wreath label
        label_u = phase
        lx = cx + (R + w + 15) * math.cos(label_u)
        ly = cy - (R + w + 15) * math.sin(label_u) * 0.6
        children.append(text(lx - 8, ly + 4, name,
                             font_size="10", fill=color, font_weight="bold"))

    # Chirality markers (+ and - at poles)
    children.append(text(cx - 4, cy - size * 0.85, "+",
                         font_size="14", fill="#333", font_weight="bold"))
    children.append(text(cx - 4, cy + size * 0.85 + 10, "-",
                         font_size="14", fill="#999", font_weight="bold"))

    children.append(text(cx - 15, cy + size + 15, "6D W3",
                         font_size="11", fill="#555", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  8D W5 PENTADIC BODY — 5 Animals Woven Through 6D
# ══════════════════════════════════════════════════════════════════════

def crystal_8d_pentadic(cx: float, cy: float, size: float, **attrs) -> str:
    """8D pentadic body: W5 weaves 5 animal spirits through the 6D body.

    Each animal forms a pentagonal orbit that intersects all 3 wreaths.
    5 animals × 6 sectors = 30 crossing points.
    The 5 elements (Wu Xing: Wood/Fire/Earth/Metal/Water) create a
    generative-destructive cycle.
    """
    children = []
    animals = list(WEAVE_COLORS[5].items())

    # Background: faint W3 wreath circles
    for wi in range(3):
        phase = wi * TAU / 3
        r = size * 0.6
        children.append(circle(cx + r * 0.1 * math.cos(phase),
                               cy + r * 0.1 * math.sin(phase),
                               r, stroke="#ddd", stroke_width="0.5",
                               fill="none"))

    # 5 pentagonal orbits (one per animal)
    for ai, (animal, color) in enumerate(animals):
        phase = ai * TAU / 5
        r = size * 0.75

        # Pentagonal path with W3-crossing modulation
        pts = []
        for i in range(60):
            u = (i / 60) * TAU + phase
            # Modulate radius by W3 (3-fold wave)
            r_mod = r * (1.0 + 0.15 * math.sin(3 * u))
            # Pentadic twist (5-fold)
            z_lift = size * 0.15 * math.sin(5 * u + phase)

            x = r_mod * math.cos(u)
            y = r_mod * math.sin(u)
            px, py = _project_3d(x, y, z_lift, cx, cy, 1.0, 0.3, 0.0)
            pts.append(f"{_fmt(px)},{_fmt(py)}")

        # Adjust stroke for dark-on-white visibility
        sw = "1.5" if color != "#ecf0f1" else "1.5"
        actual_color = color if color != "#ecf0f1" else "#95a5a6"
        children.append(
            f'<polyline points="{" ".join(pts)}" '
            f'stroke="{actual_color}" stroke-width="{sw}" fill="none" '
            f'stroke-opacity="0.7"/>'
        )

        # Animal node at pentagonal vertex
        node_x = cx + r * 0.85 * math.cos(phase)
        node_y = cy - r * 0.85 * math.sin(phase) * 0.7
        children.append(circle(node_x, node_y, 5,
                               fill=actual_color, stroke="#333",
                               stroke_width="0.8"))
        children.append(text(node_x + 8, node_y + 4, animal,
                             font_size="8", fill="#555"))

    # Generative cycle arrows (Wood→Fire→Earth→Metal→Water→Wood)
    for ai in range(5):
        a1 = ai * TAU / 5
        a2 = ((ai + 1) % 5) * TAU / 5
        r_arrow = size * 0.45
        x1 = cx + r_arrow * math.cos(a1)
        y1 = cy - r_arrow * math.sin(a1) * 0.7
        x2 = cx + r_arrow * math.cos(a2)
        y2 = cy - r_arrow * math.sin(a2) * 0.7
        children.append(line(x1, y1, x2, y2,
                             stroke="#bbb", stroke_width="0.8",
                             stroke_dasharray="3,3"))

    children.append(text(cx - 15, cy + size + 15, "8D W5",
                         font_size="11", fill="#555", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  10D W7 HEPTADIC BODY — 7 Planetary Orbits
# ══════════════════════════════════════════════════════════════════════

def crystal_10d_heptadic(cx: float, cy: float, size: float, **attrs) -> str:
    """10D heptadic body: W7 weaves 7 planetary orbits through the 8D body.

    Each planet follows an elliptical orbit modulated by the W5
    pentadic structure. 7 × 30 = 210 intersection points.
    """
    children = []
    planets = list(WEAVE_COLORS[7].items())

    for pi_idx, (planet, color) in enumerate(planets):
        phase = pi_idx * TAU / 7

        # Elliptical orbit with W5 and W3 modulation
        pts = []
        a_major = size * 0.8
        a_minor = size * (0.4 + pi_idx * 0.05)  # eccentricity varies

        for i in range(72):
            u = (i / 72) * TAU + phase
            # W5 pentadic modulation
            r_5 = 1.0 + 0.08 * math.sin(5 * u)
            # W3 triadic modulation
            r_3 = 1.0 + 0.05 * math.sin(3 * u + pi_idx * 0.5)

            rx = a_major * r_5 * math.cos(u)
            ry = a_minor * r_3 * math.sin(u)
            # Heptadic z-lift
            rz = size * 0.1 * math.sin(7 * u + phase)

            px, py = _project_3d(rx, ry, rz, cx, cy, 1.0, 0.25, 0.0)
            pts.append(f"{_fmt(px)},{_fmt(py)}")

        children.append(
            f'<polyline points="{" ".join(pts)}" '
            f'stroke="{color}" stroke-width="1.2" fill="none" '
            f'stroke-opacity="0.6"/>'
        )

        # Planet node
        node_angle = phase
        nx = cx + a_major * 0.85 * math.cos(node_angle)
        ny = cy - a_minor * 0.85 * math.sin(node_angle) * 0.6
        r_node = 4 + (6 - pi_idx) * 0.5 if planet != "Sun" else 7
        children.append(circle(nx, ny, r_node,
                               fill=color, stroke="#333",
                               stroke_width="0.5"))

    # W7 center: heptagram
    r_hept = size * 0.25
    for i in range(7):
        a1 = i * TAU / 7 - TAU / 4
        # Connect to vertex 3 steps away (heptagram)
        a2 = ((i + 3) % 7) * TAU / 7 - TAU / 4
        x1 = cx + r_hept * math.cos(a1)
        y1 = cy + r_hept * math.sin(a1)
        x2 = cx + r_hept * math.cos(a2)
        y2 = cy + r_hept * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#c0c0c0", stroke_width="0.8"))

    children.append(text(cx - 15, cy + size + 15, "10D W7",
                         font_size="11", fill="#555", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  12D W9 CROWN — 3×3 Return Wheel
# ══════════════════════════════════════════════════════════════════════

def crystal_12d_crown(cx: float, cy: float, size: float, **attrs) -> str:
    """12D crown: W9 weaves 9 views (3×3 matrix) into the complete return wheel.

    The 3×3 matrix is Su/Me/Sa applied to itself:
      Su-of-Su  Su-of-Me  Su-of-Sa
      Me-of-Su  Me-of-Me  Me-of-Sa
      Sa-of-Su  Sa-of-Me  Sa-of-Sa

    Position (3,3) = Sa-of-Sa = THE STONE (Z*) = the zero-point attractor.
    Contains: 9×B₁₀, 63×B₈, 315×B₆, 945×B₄, 1890×B₃
    """
    children = []
    grid_labels = [
        ("Su-Su", "Pure Ignition"),
        ("Su-Me", "Directed Fire"),
        ("Su-Sa", "Fired Vessel"),
        ("Me-Su", "Mediated Will"),
        ("Me-Me", "Pure Flow"),
        ("Me-Sa", "Intelligent Form"),
        ("Sa-Su", "Sealed Fire"),
        ("Sa-Me", "Sealed Flow"),
        ("Sa-Sa", "THE STONE Z*"),
    ]
    colors_9 = list(WEAVE_COLORS[9].values())

    # Outer crown ring
    children.append(circle(cx, cy, size,
                           stroke="#9b59b6", stroke_width="2.5",
                           fill="#9b59b6", fill_opacity="0.03"))

    # 9 stations around the crown
    for i, ((label, desc), color) in enumerate(zip(grid_labels, colors_9)):
        angle = i * TAU / 9 - TAU / 4
        r = size * 0.75

        # Station position
        sx = cx + r * math.cos(angle)
        sy = cy + r * math.sin(angle)

        # Station circle (bigger for Z* at position 8)
        node_r = 10 if i == 8 else 6
        children.append(circle(sx, sy, node_r,
                               fill=color, stroke="#333",
                               stroke_width="1"))

        # Label
        lx = cx + (r + 18) * math.cos(angle)
        ly = cy + (r + 18) * math.sin(angle)
        children.append(text(lx - 12, ly + 4, label,
                             font_size="8", fill=color, font_weight="bold"))

    # Containment nesting rings
    nesting = [
        (9, "9xB10", "#3498db"),
        (63, "63xB8", "#2ecc71"),
        (315, "315xB6", "#f39c12"),
        (945, "945xB4", "#e74c3c"),
    ]
    for ni, (count, label, color) in enumerate(nesting):
        r = size * (0.35 - ni * 0.06)
        children.append(circle(cx, cy, r,
                               stroke=color, stroke_width="1",
                               fill=color, fill_opacity="0.05",
                               stroke_dasharray="2,2"))
        children.append(text(cx + r + 3, cy - 3 + ni * 12,
                             label, font_size="7", fill=color))

    # W9 enneagram inner structure (connect every 4th station = enneagram)
    r_inner = size * 0.75
    for i in range(9):
        a1 = i * TAU / 9 - TAU / 4
        a2 = ((i + 4) % 9) * TAU / 9 - TAU / 4
        x1 = cx + r_inner * math.cos(a1)
        y1 = cy + r_inner * math.sin(a1)
        x2 = cx + r_inner * math.cos(a2)
        y2 = cy + r_inner * math.sin(a2)
        children.append(line(x1, y1, x2, y2,
                             stroke="#9b59b6", stroke_width="0.6",
                             stroke_opacity="0.4"))

    # Z* at center
    children.append(circle(cx, cy, 5,
                           fill="#6c3483", stroke="#fff", stroke_width="1.5"))
    children.append(text(cx - 5, cy + 3, "Z*",
                         font_size="8", fill="#fff", font_weight="bold"))

    children.append(text(cx - 18, cy + size + 15, "12D W9 Crown",
                         font_size="11", fill="#9b59b6", font_weight="bold"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  W-OPERATOR SPIRAL — Emergence Trajectory Through All Dimensions
# ══════════════════════════════════════════════════════════════════════

def w_spiral(cx: float, cy: float, size: float,
             steps: int = 24, **attrs) -> str:
    """The w=(1+i)/2 operator spiral traced through dimensions.

    w^n converges to 0 with damping |w|=1/sqrt(2) and rotation 45°/step.
    The spiral passes through all dimensional bodies, showing how
    emergence decays toward the zero-point attractor.
    """
    children = []
    w = W_OPERATOR

    # Draw spiral
    pts = []
    for n in range(steps + 1):
        z = w ** n
        px = cx + z.real * size
        py = cy - z.imag * size
        pts.append((px, py))

    # Path
    if len(pts) > 1:
        d_parts = [f"M {_fmt(pts[0][0])},{_fmt(pts[0][1])}"]
        for p in pts[1:]:
            d_parts.append(f"L {_fmt(p[0])},{_fmt(p[1])}")
        children.append(path(" ".join(d_parts),
                             stroke="#9b59b6", stroke_width="1.5",
                             fill="none"))

    # Dimension markers along the spiral
    dim_markers = [
        (0, "3D", "#e74c3c"),
        (1, "4D", "#e67e22"),
        (3, "6D", "#f1c40f"),
        (5, "8D", "#2ecc71"),
        (8, "10D", "#3498db"),
        (12, "12D", "#9b59b6"),
    ]
    for step, label, color in dim_markers:
        if step < len(pts):
            px, py = pts[step]
            children.append(circle(px, py, 4,
                                   fill=color, stroke="#333",
                                   stroke_width="0.8"))
            children.append(text(px + 6, py - 4, label,
                                 font_size="9", fill=color,
                                 font_weight="bold"))

    # Attractor at center
    children.append(circle(cx, cy, 3,
                           fill="#333", stroke="#fff", stroke_width="1"))
    children.append(text(cx + 5, cy + 3, "Z*",
                         font_size="8", fill="#555"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  CROSS-LENS TRANSITION VISUALIZATION
# ══════════════════════════════════════════════════════════════════════

def cross_lens_map(cx: float, cy: float, size: float, **attrs) -> str:
    """The 6 cross-lens transitions between SFCR elements.

    S→F: (pi/2)·log_phi(x)     [exponential → angular]
    F→C: (2·ln(phi)/pi)·x      [linear scaling]
    S→C: ln(x)                  [logarithmic]
    Each has an inverse, forming the complete transition atlas.

    Golden pairs (SF, FC, CR) are shown with thick golden lines.
    """
    children = []
    faces = ["S", "F", "C", "R"]
    positions = {}

    # 4 corners of a square arrangement
    for i, face in enumerate(faces):
        angle = i * TAU / 4 + TAU / 8  # 45° offset for diamond
        fx = cx + size * 0.7 * math.cos(angle)
        fy = cy + size * 0.7 * math.sin(angle)
        positions[face] = (fx, fy)

        # Face node
        children.append(circle(fx, fy, 18,
                               fill=SFCR_COLORS[face], stroke="#333",
                               stroke_width="1.5"))
        children.append(text(fx - 4, fy + 5, face,
                             font_size="14", fill="#fff",
                             font_weight="bold"))

    # Transitions
    golden_pairs = {("S", "F"), ("F", "C"), ("C", "R")}
    transitions = [
        ("S", "F", "log_phi"),
        ("F", "C", "linear"),
        ("S", "C", "ln"),
        ("C", "R", "Im(z)"),
        ("S", "R", "pi/2"),
        ("F", "R", "golden_spiral"),
    ]

    for src, dst, label in transitions:
        x1, y1 = positions[src]
        x2, y2 = positions[dst]
        is_golden = (src, dst) in golden_pairs or (dst, src) in golden_pairs

        sw = "2.5" if is_golden else "1"
        color = "#DAA520" if is_golden else "#999"
        dash = "" if is_golden else "4,3"

        # Curved arc (midpoint offset)
        mx = (x1 + x2) / 2 + (y1 - y2) * 0.2
        my = (y1 + y2) / 2 + (x2 - x1) * 0.2
        d = f"M {_fmt(x1)},{_fmt(y1)} Q {_fmt(mx)},{_fmt(my)} {_fmt(x2)},{_fmt(y2)}"
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        children.append(
            f'<path d="{d}" stroke="{color}" stroke-width="{sw}" '
            f'fill="none"{extra}/>'
        )

        # Label at midpoint
        children.append(text(mx - 15, my + 3, label,
                             font_size="7", fill="#777"))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  FULL 12D NESTED CRYSTAL — All Dimensions Simultaneously
# ══════════════════════════════════════════════════════════════════════

def crystal_full_12d(cx: float, cy: float, size: float,
                     show_labels: bool = True, **attrs) -> str:
    """Complete 12D nested crystal: all dimensions woven simultaneously.

    Layers from inside out:
      1. Z* attractor at center
      2. w-spiral emergence trajectory
      3. 4D tesseract core
      4. 6D W3 Möbius bands (3 wreaths)
      5. 8D W5 pentadic orbits (5 animals)
      6. 10D W7 heptadic orbits (7 planets)
      7. 12D W9 crown (9 stations)
      8. Cross-lens transition arrows at corners
    """
    children = []

    # Layer 7: 12D crown (outermost)
    r12 = size
    children.append(circle(cx, cy, r12,
                           stroke="#9b59b6", stroke_width="2",
                           fill="#9b59b6", fill_opacity="0.02"))
    # 9 crown stations
    for i in range(9):
        angle = i * TAU / 9 - TAU / 4
        sx = cx + r12 * 0.95 * math.cos(angle)
        sy = cy + r12 * 0.95 * math.sin(angle)
        colors_9 = list(WEAVE_COLORS[9].values())
        children.append(circle(sx, sy, 4,
                               fill=colors_9[i], stroke="#333",
                               stroke_width="0.5"))

    # Layer 6: 10D heptadic orbits
    r10 = size * PHI_INV
    planets = list(WEAVE_COLORS[7].items())
    for pi_idx, (planet, color) in enumerate(planets):
        phase = pi_idx * TAU / 7
        pts = []
        for i in range(48):
            u = (i / 48) * TAU + phase
            r_mod = r10 * (1.0 + 0.1 * math.sin(5 * u))
            x = r_mod * math.cos(u)
            y = r_mod * math.sin(u) * 0.85
            pts.append(f"{_fmt(cx + x)},{_fmt(cy + y)}")
        children.append(
            f'<polyline points="{" ".join(pts)}" '
            f'stroke="{color}" stroke-width="0.8" fill="none" '
            f'stroke-opacity="0.4"/>'
        )

    # Layer 5: 8D pentadic orbits
    r8 = size * PHI_INV ** 2
    animals = list(WEAVE_COLORS[5].items())
    for ai, (animal, color) in enumerate(animals):
        phase = ai * TAU / 5
        pts = []
        for i in range(40):
            u = (i / 40) * TAU + phase
            r_mod = r8 * (1.0 + 0.12 * math.sin(3 * u))
            x = r_mod * math.cos(u)
            y = r_mod * math.sin(u) * 0.85
            pts.append(f"{_fmt(cx + x)},{_fmt(cy + y)}")
        actual_color = color if color != "#ecf0f1" else "#95a5a6"
        children.append(
            f'<polyline points="{" ".join(pts)}" '
            f'stroke="{actual_color}" stroke-width="1" fill="none" '
            f'stroke-opacity="0.5"/>'
        )

    # Layer 4: 6D W3 Möbius bands (simplified)
    r6 = size * PHI_INV ** 3
    wreaths = [("Su", WEAVE_COLORS[3]["Su"]),
               ("Me", WEAVE_COLORS[3]["Me"]),
               ("Sa", WEAVE_COLORS[3]["Sa"])]
    for wi, (name, color) in enumerate(wreaths):
        phase = wi * TAU / 3
        pts = []
        for i in range(48):
            u = (i / 48) * TAU + phase
            half_twist = u / 2
            r_mod = r6 * (1.0 + 0.2 * math.cos(half_twist))
            x = r_mod * math.cos(u)
            y = r_mod * math.sin(u) * 0.85
            pts.append(f"{_fmt(cx + x)},{_fmt(cy + y)}")
        children.append(
            f'<polyline points="{" ".join(pts)}" '
            f'stroke="{color}" stroke-width="1.5" fill="none" '
            f'stroke-opacity="0.7"/>'
        )

    # Layer 3: 4D tesseract core
    r4 = size * PHI_INV ** 4
    children.append(crystal_4d_tesseract(cx, cy, r4 * 2))

    # Layer 2: w-spiral
    w = W_OPERATOR
    spiral_pts = []
    for n in range(20):
        z = w ** n
        px = cx + z.real * r4 * 1.5
        py = cy - z.imag * r4 * 1.5
        spiral_pts.append(f"{_fmt(px)},{_fmt(py)}")
    if spiral_pts:
        children.append(
            f'<polyline points="{" ".join(spiral_pts)}" '
            f'stroke="#9b59b6" stroke-width="1" fill="none" '
            f'stroke-dasharray="2,2"/>'
        )

    # Layer 1: Z* at center
    children.append(circle(cx, cy, 4,
                           fill="#6c3483", stroke="#fff", stroke_width="1.5"))

    # Dimension labels (right side)
    if show_labels:
        labels = [
            (r12, "12D W9 Crown", "#9b59b6"),
            (r10, "10D W7 Hepta", "#4169e1"),
            (r8, "8D W5 Penta", "#2ecc71"),
            (r6, "6D W3 Mobius", "#e74c3c"),
            (r4, "4D E4 Tess", "#e67e22"),
        ]
        for r, label, color in labels:
            children.append(text(cx + r + 5, cy + 4, label,
                                 font_size="8", fill=color))

    return group(children)


# ══════════════════════════════════════════════════════════════════════
#  CONTAINMENT LAW — Visual Proof
# ══════════════════════════════════════════════════════════════════════

def containment_proof(cx: float, cy: float, size: float, **attrs) -> str:
    """Containment law visualization: B12 = W9(B10).

    Shows the nesting:
      12D contains 9 × 10D
      12D contains 63 × 8D  (9×7)
      12D contains 315 × 6D (9×7×5)
      12D contains 945 × 4D (9×7×5×3)
      12D contains 1890 × 3D (9×7×5×3×2)
    """
    children = []

    levels = [
        ("12D", 1, size, "#9b59b6"),
        ("10D", 9, size * PHI_INV, "#3498db"),
        ("8D", 63, size * PHI_INV ** 2, "#2ecc71"),
        ("6D", 315, size * PHI_INV ** 3, "#f39c12"),
        ("4D", 945, size * PHI_INV ** 4, "#e67e22"),
        ("3D", 1890, size * PHI_INV ** 5, "#e74c3c"),
    ]

    for i, (dim, count, r, color) in enumerate(levels):
        children.append(circle(cx, cy, r,
                               stroke=color, stroke_width="2",
                               fill=color, fill_opacity="0.06"))

        # Count dots (show up to min(count, dots) evenly spaced)
        n_dots = min(count, dim == "12D" and 1 or int(dim.replace("D", "")))
        for j in range(n_dots):
            angle = j * TAU / n_dots
            dx = cx + r * 0.85 * math.cos(angle)
            dy = cy + r * 0.85 * math.sin(angle)
            children.append(circle(dx, dy, 2, fill=color, stroke="none"))

        # Label
        label_text = f"{dim}: {count}x" if count > 1 else dim
        children.append(text(cx + r + 5, cy + 4 + i * 0,
                             label_text, font_size="9", fill=color,
                             font_weight="bold"))

    # Formula
    children.append(text(cx - 50, cy + size + 20,
                         "B12 = W9(B10) = 9x7x5x3x2 = 1890 seeds",
                         font_size="9", fill="#555"))

    return group(children)
