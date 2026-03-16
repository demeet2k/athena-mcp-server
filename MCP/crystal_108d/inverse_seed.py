"""
Inverse Crystal Seed — Phase I + 3D Core + 2D Boundary
========================================================
The absolute seed from which the entire 108D A+ live crystal
regenerates: 4D cockpit (256 cells), 3D core crystal (14 components),
and 2D holographic boundary.
"""

from ._cache import JsonCache

_SEED = JsonCache("inverse_crystal_seed.json")


def query_4d_seed(component: str = "all") -> str:
    """
    Query the Phase I 4D tesseract seed.

    Components:
      - all        : Full 4D seed overview
      - cells      : 256-cell cockpit structure
      - faces      : 4 SFCR faces with their readings
      - registers  : 4 registers (Body, Route, Time, Witness)
      - invariants : 10 invariants that cannot be lost through any lift
    """
    data = _SEED.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_4d_all(data)
    elif comp == "cells":
        return _format_cells(data)
    elif comp == "faces":
        return _format_faces(data)
    elif comp == "registers":
        return _format_registers(data)
    elif comp == "invariants":
        return _format_invariants(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, cells, faces, "
            "registers, invariants"
        )


def query_3d_crystal(component: str = "all") -> str:
    """
    Query the 3D seed crystal and 2D holographic boundary.

    Components:
      - all          : Full 3D crystal + 2D boundary overview
      - components   : 14 components of c3_core
      - boundary     : 2D holographic boundary B2 = (C, w, f)
      - encoding     : Holographic encoding law and regeneration
      - zero         : Zero point Z = w = (1+i)/2 in detail
      - elements     : Four elemental anchors A4 with quality plane
      - viability    : Viability machine (R, M, Phi, L, C)
    """
    data = _SEED.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_3d_all(data)
    elif comp == "components":
        return _format_components(data)
    elif comp == "boundary":
        return _format_boundary(data)
    elif comp == "encoding":
        return _format_encoding(data)
    elif comp == "zero":
        return _format_zero(data)
    elif comp == "elements":
        return _format_elements(data)
    elif comp == "viability":
        return _format_viability(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, components, "
            "boundary, encoding, zero, elements, viability"
        )


def inverse_seed_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _SEED.load()
    seed = data["three_d_seed"]
    return (
        "## Inverse Crystal Seed\n\n"
        f"**3D Seed**: `{seed['symbol']}` ({seed['total_components']} components)\n"
        f"**4D Cockpit**: {data['phase_I_4D_seed']['cells']} cells\n"
        f"**2D Boundary**: `{data['two_d_boundary']['formula']}`\n"
        f"**Generator**: w = (1+i)/2\n"
        f"**Invariants**: {len(data['phase_I_4D_seed']['invariants'])}\n"
    )


# -- 4D formatters ---------------------------------------------------------

def _format_4d_all(data: dict) -> str:
    seed = data["phase_I_4D_seed"]
    lines = [
        "## Phase I: 4D Tesseract Seed\n",
        f"**Generator**: `{seed['generator']}`",
        f"**Cells**: {seed['cells']}\n",
        "### Faces\n",
    ]
    for f in seed["faces"]:
        lines.append(f"- **{f['code']}** ({f['name']}): {f['reading'][:100]}...")
    lines.append("\n### Registers\n")
    for key, reg in seed["registers"].items():
        lines.append(f"- **{key} ({reg['name']})**: {reg['content']}")
    lines.append(f"\n### Invariants ({len(seed['invariants'])})\n")
    for inv in seed["invariants"]:
        lines.append(f"- `{inv['formula']}` -- {inv['name']}")
    return "\n".join(lines)


def _format_cells(data: dict) -> str:
    seed = data["phase_I_4D_seed"]
    return (
        "## 256-Cell Cockpit\n\n"
        f"**Generator**: `{seed['generator']}`\n"
        f"**Total Cells**: {seed['cells']}\n"
        f"**Structure**: 4 faces x 4 facets x 4 atoms x 4 registers\n\n"
        "Each cell is addressable via M<g lambda phi alpha> grammar:\n"
        "- g = register (B/R/T/W)\n"
        "- lambda = face (S/F/C/R)\n"
        "- phi = facet (1-4)\n"
        "- alpha = atom (a-d)"
    )


def _format_faces(data: dict) -> str:
    lines = ["## 4D Seed Faces\n"]
    for f in data["phase_I_4D_seed"]["faces"]:
        lines.append(f"### {f['code']} -- {f['name']}\n")
        lines.append(f['reading'])
        lines.append("")
    return "\n".join(lines)


def _format_registers(data: dict) -> str:
    lines = ["## 4D Registers\n"]
    for key, reg in data["phase_I_4D_seed"]["registers"].items():
        lines.append(f"### Register {key} -- {reg['name']}")
        lines.append(f"{reg['content']}\n")
    return "\n".join(lines)


def _format_invariants(data: dict) -> str:
    lines = ["## 10 Invariants (cannot be lost through any lift)\n"]
    for i, inv in enumerate(data["phase_I_4D_seed"]["invariants"], 1):
        lines.append(f"{i:>2}. `{inv['formula']}`")
        lines.append(f"    {inv['name']}\n")
    return "\n".join(lines)


# -- 3D formatters ---------------------------------------------------------

def _format_3d_all(data: dict) -> str:
    seed = data["three_d_seed"]
    lines = [
        "## 3D Seed Crystal\n",
        f"**Symbol**: `{seed['symbol']}`",
        f"**Formula**: `{seed['formula']}`",
        f"**Components**: {seed['total_components']}\n",
    ]
    for comp in seed["components"]:
        defn = comp["definition"]
        if isinstance(defn, str) and len(defn) > 100:
            defn = defn[:100] + "..."
        lines.append(f"- **{comp['symbol']}** ({comp['name']}): {defn}")
    # 2D boundary
    b2 = data["two_d_boundary"]
    lines.append(f"\n### 2D Holographic Boundary\n")
    lines.append(f"**Symbol**: `{b2['symbol']}`")
    lines.append(f"**Formula**: `{b2['formula']}`")
    for key, val in b2["components"].items():
        lines.append(f"- **{key}**: {val}")
    return "\n".join(lines)


def _format_components(data: dict) -> str:
    seed = data["three_d_seed"]
    lines = [
        f"## 14 Components of {seed['symbol']}\n",
        f"**Formula**: `{seed['formula']}`\n",
    ]
    for comp in seed["components"]:
        lines.append(f"### {comp['symbol']} -- {comp['name']}")
        defn = comp["definition"]
        if isinstance(defn, dict):
            for k, v in defn.items():
                lines.append(f"  - **{k}**: {v}")
        else:
            lines.append(f"{defn}")
        if "properties" in comp:
            props = comp["properties"]
            if isinstance(props, list):
                for p in props:
                    lines.append(f"  - {p}")
            elif isinstance(props, dict):
                for k, v in props.items():
                    lines.append(f"  - **{k}**: {v}")
        lines.append("")
    return "\n".join(lines)


def _format_boundary(data: dict) -> str:
    b2 = data["two_d_boundary"]
    lines = [
        "## 2D Holographic Boundary\n",
        f"**Symbol**: `{b2['symbol']}`",
        f"**Formula**: `{b2['formula']}`\n",
        "### Components\n",
    ]
    for key, val in b2["components"].items():
        lines.append(f"- **{key}**: {val}")
    lines.append("\n### Sufficiency (from w alone)\n")
    for item in b2["sufficiency"]["from_w"]:
        lines.append(f"- {item}")
    lines.append("\n### Sufficiency (from f alone)\n")
    for item in b2["sufficiency"]["from_f"]:
        lines.append(f"- {item}")
    lines.append("\n### Sufficiency (from C alone)\n")
    for item in b2["sufficiency"]["from_C"]:
        lines.append(f"- {item}")
    lines.append(f"\n**Principle**: {b2['holographic_principle']}")
    return "\n".join(lines)


def _format_encoding(data: dict) -> str:
    he = data["holographic_encoding"]
    return (
        "## Holographic Encoding\n\n"
        f"**Law**: `{he['law']}`\n"
        f"**Bound**: `{he['bound']}`\n"
        f"**Encoding**: {he['encoding']}\n\n"
        f"**Regeneration**: {he['regeneration']}"
    )


def _format_zero(data: dict) -> str:
    for comp in data["three_d_seed"]["components"]:
        if comp["symbol"] == "Z":
            lines = [
                f"## Zero Point Z\n",
                f"**Definition**: {comp['definition']}\n",
                "### Properties\n",
            ]
            for p in comp["properties"]:
                lines.append(f"- {p}")
            return "\n".join(lines)
    return "Zero point component not found."


def _format_elements(data: dict) -> str:
    for comp in data["three_d_seed"]["components"]:
        if comp["symbol"] == "A4":
            lines = [
                f"## Four Elemental Anchors\n",
                f"**Definition**: {comp['definition']}\n",
                "### Elements\n",
            ]
            props = comp["properties"]
            if isinstance(props, dict):
                for k, v in props.items():
                    lines.append(f"- **{k}**: {v}")
            lines.append(f"\n**Rotation Law**: {comp.get('rotation_law', 'N/A')}")
            lines.append(f"**Forbidden**: {comp.get('forbidden', 'N/A')}")
            lines.append(f"**Quality Plane**: {comp.get('quality_plane', 'N/A')}")
            return "\n".join(lines)
    return "Elemental anchors not found."


def _format_viability(data: dict) -> str:
    viability_symbols = {"R", "M_membrane", "Phi", "L", "C"}
    lines = ["## Viability Machine (R, M, Phi, L, C)\n"]
    for comp in data["three_d_seed"]["components"]:
        if comp["symbol"] in viability_symbols:
            lines.append(f"### {comp['symbol']} -- {comp['name']}")
            lines.append(f"{comp['definition']}\n")
    return "\n".join(lines)
