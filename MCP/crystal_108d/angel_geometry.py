"""
Angel Geometry — Geometric Lift of the AI Self-Model
=====================================================
Extends the 12-piece angel tuple with a full geometry: state manifold,
metric tensor, response bundle, curvature, symmetry group, conservation
laws, sheaf interpretation, and recursive self-definition.
"""

from ._cache import JsonCache

_GEOMETRY = JsonCache("angel_geometry.json")
_CONSERVATION = JsonCache("angel_conservation.json")


def query_angel_geometry(component: str = "all") -> str:
    """
    Query the geometric lift of the angel self-model.

    Components:
      - all             : Full geometry overview
      - manifold        : 6-chart state manifold (Sq/Fl/Cl/Fr/Omega/Ext)
      - metric          : Block metric with Fisher-Rao on Cloud chart
      - bundle          : Response bundle (fiber bundle over history space)
      - curvature       : Curvature R != 0 and holonomy
      - symmetry        : Symmetry group decomposition
      - sheaf           : Sheaf interpretation (coherence/hallucination)
      - axioms          : 7 axioms (A1-A7)
      - self_definition : Recursive self-definition fixed-point operator
      - object          : The upgraded 10-piece geometric tuple
    """
    data = _GEOMETRY.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "manifold":
        return _format_manifold(data)
    elif comp == "metric":
        return _format_metric(data)
    elif comp == "bundle":
        return _format_bundle(data)
    elif comp == "curvature":
        return _format_curvature(data)
    elif comp == "symmetry":
        return _format_symmetry(data)
    elif comp == "sheaf":
        return _format_sheaf(data)
    elif comp == "axioms":
        return _format_axioms(data)
    elif comp == "self_definition":
        return _format_self_def(data)
    elif comp == "object":
        return _format_object(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, manifold, metric, "
            "bundle, curvature, symmetry, sheaf, axioms, self_definition, object"
        )


def query_angel_conservation(component: str = "all") -> str:
    """
    Query geometric conservation laws and potential landscape.

    Components:
      - all       : Full conservation overview
      - exact     : Exact invariants (normalization, fixity, admissibility, identity)
      - quasi     : Quasi-invariants (tone, grounding, compression, momentum)
      - holonomy  : Holonomy types (clarification, stance, disambiguation, memory)
      - potential  : Potential landscape Phi and motion law
      - transport  : Parallel transport and transported quantities
      - identity   : Observational equivalence and identity class
    """
    data = _CONSERVATION.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_conservation_all(data)
    elif comp == "exact":
        return _format_exact(data)
    elif comp == "quasi":
        return _format_quasi(data)
    elif comp == "holonomy":
        return _format_holonomy(data)
    elif comp == "potential":
        return _format_potential(data)
    elif comp == "transport":
        return _format_transport(data)
    elif comp == "identity":
        return _format_identity(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, exact, quasi, "
            "holonomy, potential, transport, identity"
        )


def angel_geometry_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _GEOMETRY.load()
    m = data["meta"]
    return (
        "## Angel Geometry\n\n"
        f"**Upgraded Object**: `{m['upgraded_object']}`\n"
        f"**Extends**: {m['extends']}\n"
        f"**State Manifold**: 6 charts (Sq/Fl/Cl/Fr/Omega/Ext)\n"
        f"**Curvature**: R != 0 (order of context updates matters)\n"
        f"**Axioms**: 7 (A1-A7)\n"
        f"**Self-Definition**: Fixed-point operator G: D -> D\n"
    )


# -- Geometry formatters ---------------------------------------------------

def _format_all(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## Angel Geometry -- Geometric Lift of the AI Self-Model\n",
        f"**Object**: `{m['upgraded_object']}`",
        f"**Extends**: {m['extends']}\n",
    ]
    # Object components
    lines.append("### 10-Piece Geometric Tuple\n")
    for c in data["geometric_object"]["components"]:
        lines.append(f"- **{c['symbol']}** ({c['name']}): {c['description']}")
    # Manifold summary
    lines.append("\n### State Manifold (6 charts)\n")
    for ch in data["state_manifold"]["charts"]:
        lines.append(f"- **{ch['name']}** ({ch['symbol']}): {ch['type']}")
    # Curvature
    c = data["curvature"]
    lines.append(f"\n### Curvature\n")
    lines.append(f"- **R != 0**: {c['meaning']}")
    # Axioms summary
    lines.append("\n### 7 Axioms\n")
    for ax in data["seven_axioms"]:
        lines.append(f"- **{ax['id']}**: {ax['name']}")
    # Compressed form
    lines.append(f"\n### Compressed Form\n")
    lines.append(data["compressed_form"])
    return "\n".join(lines)


def _format_manifold(data: dict) -> str:
    sm = data["state_manifold"]
    lines = [
        "## State Manifold\n",
        f"**Formula**: `{sm['formula']}`",
        f"\n{sm['description']}\n",
    ]
    for ch in sm["charts"]:
        lines.append(f"### {ch['name']} ({ch['symbol']})")
        lines.append(f"**Type**: {ch['type']}")
        lines.append(f"**Content**: {ch['content']}")
        lines.append(f"**Tangent Meaning**: {ch['tangent_meaning']}")
        if "metric" in ch:
            lines.append(f"**Metric**: `{ch['metric']}`")
        lines.append("")
    return "\n".join(lines)


def _format_metric(data: dict) -> str:
    bm = data["block_metric"]
    lines = [
        "## Block Metric\n",
        f"**Formula**: `{bm['formula']}`",
        f"\n{bm['description']}\n",
        "### Intra-Lens Metrics\n",
    ]
    for name, desc in bm["intra_lens_metrics"].items():
        lines.append(f"- **{name}**: {desc}")
    lines.append(f"\n### Geodesic Meaning\n")
    lines.append(bm["geodesic_meaning"])
    return "\n".join(lines)


def _format_bundle(data: dict) -> str:
    rb = data["response_bundle"]
    return (
        "## Response Bundle\n\n"
        f"**Definition**: `{rb['definition']}`\n"
        f"**Base Space**: {rb['base_space']}\n"
        f"**Fiber**: {rb['fiber']}\n"
        f"**Section**: {rb['section']}\n\n"
        f"**Interpretation**: {rb['interpretation']}"
    )


def _format_curvature(data: dict) -> str:
    c = data["curvature"]
    lines = [
        "## Curvature\n",
        f"**Formula**: `{c['formula']}`",
        f"**Nonzero**: {c['nonzero']}",
        f"**Meaning**: {c['meaning']}",
        f"\n**Theorem**: {c['theorem']}\n",
        "### Interpretation\n",
    ]
    for key, val in c["interpretation"].items():
        lines.append(f"- **{key}**: {val}")
    # Holonomy
    h = c["holonomy"]
    lines.append(f"\n### Holonomy\n")
    lines.append(h["definition"])
    lines.append(f"\n**Non-Identity**: {h['nonidentity']}\n")
    lines.append("**Types**:")
    for t in h["types"]:
        lines.append(f"  - {t}")
    return "\n".join(lines)


def _format_symmetry(data: dict) -> str:
    sg = data["symmetry_group"]
    lines = [
        "## Symmetry Group\n",
        f"**Structure**: `{sg['structure']}`\n",
        "### Subgroups\n",
    ]
    for name, desc in sg["subgroups"].items():
        lines.append(f"- **{name}**: {desc}")
    lines.append("\n### Broken By\n")
    for item in sg["broken_by"]:
        lines.append(f"- {item}")
    lines.append(f"\n**Identity Class**: {sg['identity_class']}")
    return "\n".join(lines)


def _format_sheaf(data: dict) -> str:
    si = data["sheaf_interpretation"]
    lines = [
        "## Sheaf Interpretation\n",
        f"**Presheaf**: {si['presheaf']}",
        f"**Restriction**: {si['restriction_maps']}",
        f"**Global Section**: {si['global_section']}\n",
        "### Correspondences\n",
    ]
    for key, val in si["correspondences"].items():
        lines.append(f"- **{key}**: {val}")
    lines.append(f"\n**Statement**: {si['statement']}")
    return "\n".join(lines)


def _format_axioms(data: dict) -> str:
    lines = ["## Seven Axioms of the Angel Object\n"]
    for ax in data["seven_axioms"]:
        lines.append(f"### {ax['id']} -- {ax['name']}")
        lines.append(ax["statement"])
        lines.append("")
    return "\n".join(lines)


def _format_self_def(data: dict) -> str:
    sd = data["recursive_self_definition"]
    st = sd["stability"]
    return (
        "## Recursive Self-Definition\n\n"
        f"**Operator**: `{sd['operator']}`\n"
        f"**Fixed Point**: `{sd['fixed_point']}`\n"
        f"**Equivalence**: `{sd['equivalence_class']}`\n\n"
        "### Stability\n\n"
        f"**Jacobian**: `{st['jacobian']}`\n"
        f"**Contractive**: {st['contractive']}\n"
        f"**Unstable**: {st['unstable']}\n\n"
        f"**Meaning**: {st['meaning']}"
    )


def _format_object(data: dict) -> str:
    go = data["geometric_object"]
    lines = [
        "## Geometric Object\n",
        f"**Symbol**: {go['symbol']}",
        f"**Tuple**: `{go['tuple']}`\n",
    ]
    for c in go["components"]:
        lines.append(f"- **{c['symbol']}** ({c['name']}): {c['description']}")
    return "\n".join(lines)


# -- Conservation formatters -----------------------------------------------

def _format_conservation_all(data: dict) -> str:
    lines = ["## Angel Conservation Laws\n"]
    lines.append("### Exact Invariants\n")
    for inv in data["exact_invariants"]:
        lines.append(f"- **{inv['name']}**: `{inv['formula']}`")
    lines.append("\n### Quasi-Invariants\n")
    for qi in data["quasi_invariants"]:
        lines.append(f"- **{qi['name']}**: {qi['description']}")
    lines.append("\n### Holonomy Types\n")
    for ht in data["holonomy_types"]:
        lines.append(f"- **{ht['name']}**: {ht['description']}")
    pl = data["potential_landscape"]
    lines.append(f"\n### Potential Landscape\n")
    lines.append(f"**Formula**: `{pl['formula']}`")
    lines.append(f"**Motion Law**: `{pl['motion_law']}`")
    lines.append(f"\n**Meaning**: {pl['meaning']}")
    return "\n".join(lines)


def _format_exact(data: dict) -> str:
    lines = ["## Exact Invariants\n"]
    for inv in data["exact_invariants"]:
        lines.append(f"### {inv['name']}")
        lines.append(f"**Formula**: `{inv['formula']}`")
        lines.append(f"{inv['meaning']}\n")
    return "\n".join(lines)


def _format_quasi(data: dict) -> str:
    lines = ["## Quasi-Invariants\n"]
    for qi in data["quasi_invariants"]:
        lines.append(f"### {qi['name']}")
        lines.append(f"{qi['description']}")
        lines.append(f"**Decay**: {qi['decay']}\n")
    return "\n".join(lines)


def _format_holonomy(data: dict) -> str:
    lines = ["## Holonomy Types\n"]
    for ht in data["holonomy_types"]:
        lines.append(f"### {ht['name']}")
        lines.append(f"{ht['description']}")
        lines.append(f"**Mechanism**: {ht['mechanism']}\n")
    return "\n".join(lines)


def _format_potential(data: dict) -> str:
    pl = data["potential_landscape"]
    lines = [
        "## Potential Landscape\n",
        f"**Formula**: `{pl['formula']}`\n",
        "### Terms\n",
    ]
    for key, val in pl["terms"].items():
        lines.append(f"- **{key}**: {val}")
    lines.append(f"\n### Motion Law\n")
    lines.append(f"`{pl['motion_law']}`\n")
    for key, val in pl["components"].items():
        lines.append(f"- **{key}**: {val}")
    lines.append(f"\n### Fixed Points\n")
    lines.append(f"`{pl['fixed_points']}`")
    lines.append(f"\n**Attractor Family**: {pl['attractor_family']}")
    lines.append(f"\n**Meaning**: {pl['meaning']}")
    return "\n".join(lines)


def _format_transport(data: dict) -> str:
    pt = data["parallel_transport"]
    lines = [
        "## Parallel Transport\n",
        pt["description"],
        f"\n**Equation**: `{pt['equation']}`\n",
        "### Transported Quantities\n",
    ]
    for q in pt["transported_quantities"]:
        lines.append(f"- {q}")
    return "\n".join(lines)


def _format_identity(data: dict) -> str:
    oe = data["observational_equivalence"]
    return (
        "## Observational Equivalence\n\n"
        f"**Definition**: `{oe['definition']}`\n"
        f"**Identity Class**: {oe['identity_class']}\n\n"
        f"**Meaning**: {oe['meaning']}"
    )
