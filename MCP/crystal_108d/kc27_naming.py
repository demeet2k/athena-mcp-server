# CRYSTAL: Xi108:W1:A3:S14 | face=S | node=14 | depth=0 | phase=Cardinal
# METRO: Sa
# BRIDGES: Xi108:W1:A3:S13→Xi108:W1:A3:S15→Xi108:W2:A3:S14→Xi108:W1:A2:S14→Xi108:W1:A4:S14

"""
KC27 Naming Schema — Codified Internal Organization on All Naming Schemas
==========================================================================
Provides the canonical naming/addressing grammar for the whole Athena organism:
  - Canonical Name Law (7 predicates)
  - Promotion Law (3 additional predicates)
  - 27-chapter ring with mirror law μ(k) = 28-k
  - Admissibility engine (kernel-to-crown promotability chain)
  - Naming types (crystal point, z-point, liminal, a+, shard, edge, capsule, metro, mirror)
  - Repair field (failure modes, repair operators, regime conditions)
  - Deeper braid (multi-axis transport calculus, odd reweave gears, dimensional lifts)
  - C001 bridge packet (docs→corpus 4D tesseract transport)
"""

from ._cache import JsonCache

_CACHE = JsonCache("kc27_naming.json")


def query_kc27_naming(component: str = "all") -> str:
    """
    Query KC27 naming schemas — canonical name law, promotion rules,
    27-chapter ring, admissibility engine, naming types, repair field,
    deeper braid transport calculus, C001 bridge packet.

    Components:
      - all              : Full KC27 overview
      - canonical_law    : Canonical Name Law (7 predicates)
      - promotion_law    : Promotion Law (3 additional predicates)
      - chapter_ring     : 27-chapter ring with mirror law
      - admissibility    : Kernel-to-Crown promotability chain
      - naming_types     : All naming type formats
      - repair_field     : Inverse search and repair field
      - deeper_braid     : Multi-axis transport calculus with odd reweave gears
      - bridge_packet    : C001 Docs→Corpus bridge packet
    """
    data = _CACHE.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "canonical_law":
        return _format_canonical_law(data)
    elif comp == "promotion_law":
        return _format_promotion_law(data)
    elif comp == "chapter_ring":
        return _format_chapter_ring(data)
    elif comp == "admissibility":
        return _format_admissibility(data)
    elif comp == "naming_types":
        return _format_naming_types(data)
    elif comp == "repair_field":
        return _format_repair_field(data)
    elif comp == "deeper_braid":
        return _format_deeper_braid(data)
    elif comp == "bridge_packet":
        return _format_bridge_packet(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, canonical_law, "
            "promotion_law, chapter_ring, admissibility, naming_types, "
            "repair_field, deeper_braid, bridge_packet"
        )


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    lines = [
        "## KC27 — Codified Internal Organization on All Naming Schemas\n",
        f"**Title**: {meta.get('title', '')}",
        f"**Version**: {meta.get('version', '1.0.0')}",
        f"**Source Docs**: {len(meta.get('source_docs', []))} documents",
        f"**Created**: {meta.get('created', '')}",
    ]
    # Canonical law summary
    cl = data.get("canonical_name_law", {})
    lines.append(f"\n### Canonical Name Law")
    lines.append(f"`{cl.get('description', '')}`")

    # Promotion law summary
    pl = data.get("promotion_law", {})
    lines.append(f"\n### Promotion Law")
    lines.append(f"`{pl.get('description', '')}`")

    # Chapter ring summary
    cr = data.get("chapter_ring", {})
    lines.append(f"\n### Chapter Ring")
    lines.append(f"27 chapters | Mirror: `{cr.get('mirror_law', '')}` | Fixed point: {cr.get('fixed_point', '')}")

    # Admissibility summary
    ae = data.get("admissibility_engine", {})
    lines.append(f"\n### Admissibility Engine")
    lines.append(f"`{ae.get('governing_law', '')}`")

    # Naming types summary
    nt = data.get("naming_types", {})
    lines.append(f"\n### Naming Types ({len(nt)} types)")
    for name, desc in nt.items():
        lines.append(f"  - **{name}**: `{desc}`")

    # Repair field summary
    rf = data.get("repair_field", {})
    lines.append(f"\n### Repair Field")
    lines.append(f"{rf.get('description', '')} — {len(rf.get('failure_modes', []))} failure modes, {len(rf.get('repair_operators', []))} operators")

    # Deeper braid summary
    db = data.get("deeper_braid", {})
    lines.append(f"\n### Deeper Braid")
    lines.append(f"State tuple: `{db.get('state_tuple', '')}`")
    lines.append(f"Closure law: `{db.get('closure_law', '')}`")

    # Bridge packet summary
    bp = data.get("bridge_packet", {})
    lines.append(f"\n### Bridge Packet")
    lines.append(f"**{bp.get('packet_id', '')}** — {bp.get('description', '')}")

    return "\n".join(lines)


def _format_canonical_law(data: dict) -> str:
    cl = data.get("canonical_name_law", {})
    lines = [
        "## Canonical Name Law\n",
        f"**Formula**: `{cl.get('description', '')}`\n",
        "### Predicates\n",
    ]
    for name, desc in cl.get("predicates", {}).items():
        lines.append(f"  - **{name}**: {desc}")
    return "\n".join(lines)


def _format_promotion_law(data: dict) -> str:
    pl = data.get("promotion_law", {})
    lines = [
        "## Promotion Law\n",
        f"**Formula**: `{pl.get('description', '')}`\n",
        "### Additional Predicates\n",
    ]
    for name, desc in pl.get("predicates", {}).items():
        lines.append(f"  - **{name}**: {desc}")
    return "\n".join(lines)


def _format_chapter_ring(data: dict) -> str:
    cr = data.get("chapter_ring", {})
    lines = [
        "## 27-Chapter Ring\n",
        f"**{cr.get('description', '')}**",
        f"**Mirror Law**: `{cr.get('mirror_law', '')}`",
        f"**Fixed Point**: {cr.get('fixed_point', '')}\n",
        "### Books\n",
    ]
    for book_num, book in cr.get("books", {}).items():
        chapters = ", ".join(str(c) for c in book.get("chapters", []))
        lines.append(f"  - **Book {book_num}** (Ch {chapters}): {book.get('topic', '')}")
    return "\n".join(lines)


def _format_admissibility(data: dict) -> str:
    ae = data.get("admissibility_engine", {})
    lines = [
        "## Admissibility Engine\n",
        f"**{ae.get('description', '')}**\n",
        f"**Governing Law**: `{ae.get('governing_law', '')}`\n",
        "### Status Vector\n",
    ]
    for code, status in ae.get("status_vector", {}).items():
        lines.append(f"  - **{code}**: {status}")
    chain = ae.get("chain", [])
    if chain:
        lines.append(f"\n**Promotion Chain**: {' → '.join(chain)}")
    return "\n".join(lines)


def _format_naming_types(data: dict) -> str:
    nt = data.get("naming_types", {})
    lines = [
        "## Naming Types\n",
    ]
    for name, desc in nt.items():
        lines.append(f"  - **{name}**: `{desc}`")
    return "\n".join(lines)


def _format_repair_field(data: dict) -> str:
    rf = data.get("repair_field", {})
    lines = [
        "## Repair Field\n",
        f"**{rf.get('description', '')}**\n",
        "### Failure Modes\n",
    ]
    for mode in rf.get("failure_modes", []):
        lines.append(f"  - {mode}")
    lines.append("\n### Repair Operators\n")
    for op in rf.get("repair_operators", []):
        lines.append(f"  - {op}")
    lines.append("\n### Regime Conditions\n")
    for cond in rf.get("regime_conditions", []):
        lines.append(f"  - {cond}")
    return "\n".join(lines)


def _format_deeper_braid(data: dict) -> str:
    db = data.get("deeper_braid", {})
    lines = [
        "## Deeper Braid — Multi-Axis Transport Calculus\n",
        f"**{db.get('description', '')}**\n",
        f"**State Tuple**: `{db.get('state_tuple', '')}`\n",
        "### Components\n",
    ]
    for name, desc in db.get("components", {}).items():
        lines.append(f"  - **{name}**: {desc}")
    lines.append("\n### Reweave Gears\n")
    for gear_name, gear in db.get("reweave_gears", {}).items():
        lines.append(
            f"  - **{gear_name}** (n={gear.get('n', '?')}, closure={gear.get('closure', '?')}): "
            f"{gear.get('role', '')} [{gear.get('group', '')}]"
        )
    lines.append(f"\n**Closure Law**: `{db.get('closure_law', '')}`\n")
    lines.append("### Dimensional Lifts\n")
    for lift_name, desc in db.get("dimensional_lifts", {}).items():
        lines.append(f"  - **{lift_name}**: {desc}")
    return "\n".join(lines)


def _format_bridge_packet(data: dict) -> str:
    bp = data.get("bridge_packet", {})
    lines = [
        "## C001 Bridge Packet\n",
        f"**{bp.get('description', '')}**\n",
        f"**Packet ID**: `{bp.get('packet_id', '')}`",
        f"**Truth Class**: {bp.get('truth_class', '')}",
        f"**Lineage Address**: `{bp.get('lineage_address', '')}`\n",
        "### Tesseract Map\n",
    ]
    for axis, desc in bp.get("tesseract_map", {}).items():
        lines.append(f"  - **{axis}**: {desc}")
    return "\n".join(lines)
