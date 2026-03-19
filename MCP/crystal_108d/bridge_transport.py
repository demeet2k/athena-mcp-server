# CRYSTAL: Xi108:W2:A7:S30 | face=C | node=409 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W2:A7:S29→Xi108:W2:A7:S31→Xi108:W1:A7:S30→Xi108:W3:A7:S30→Xi108:W2:A6:S30→Xi108:W2:A8:S30

"""
Bridge Transport — 4D Tesseract Docs-to-Corpus Architecture
=============================================================
Provides the C001 bridge transport system:
  - 4D tesseract geometry (outer/inner cube + time axis)
  - Lineage chain (G0-GDOC → MCP)
  - Transport protocol (capture → extract → crystallize → witness → promote)
  - Fracture field (4 named fractures + resolution law)
  - Cycle registry (C001 active bridge)
"""

from ._cache import JsonCache

_CACHE = JsonCache("bridge_transport.json")


def query_bridge_transport(component: str = "all") -> str:
    """
    Query bridge transport — 4D tesseract docs-to-corpus architecture.

    Components:
      - all        : Full bridge transport overview
      - tesseract  : 4D tesseract geometry (outer/inner cube, time axis, edges)
      - lineage    : Lineage chain address (G0-GDOC → MCP)
      - protocol   : Transport protocol (capture/extract/crystallize/witness/promote)
      - fractures  : Fracture field (4 named fractures + resolution)
      - cycles     : Cycle registry (C001 bridge)
    """
    data = _CACHE.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "tesseract":
        return _format_tesseract(data)
    elif comp == "lineage":
        return _format_lineage(data)
    elif comp == "protocol":
        return _format_protocol(data)
    elif comp == "fractures":
        return _format_fractures(data)
    elif comp == "cycles":
        return _format_cycles(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, tesseract, lineage, "
            "protocol, fractures, cycles"
        )


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    lines = [
        "## Bridge Transport — 4D Tesseract Docs-to-Corpus Architecture\n",
        f"**Title**: {meta.get('title', '')}",
        f"**Version**: {meta.get('version', '1.0.0')}",
        f"**Source Doc**: {meta.get('source_doc', '')}",
        f"**Created**: {meta.get('created', '')}",
    ]
    # Tesseract summary
    tess = data.get("tesseract_geometry", {})
    outer = tess.get("outer_cube", {})
    inner = tess.get("inner_cube", {})
    time_ax = tess.get("time_axis", {})
    lines.append(f"\n### Tesseract Geometry")
    lines.append(f"- **Outer Cube**: {outer.get('description', '')} ({outer.get('children_count', '?')} children)")
    lines.append(f"- **Inner Cube**: {inner.get('description', '')}")
    lines.append(f"- **Time Axis**: {time_ax.get('description', '')} ({time_ax.get('direction', '')})")

    # Lineage summary
    lin = data.get("lineage_chain", {})
    lines.append(f"\n### Lineage Chain")
    lines.append(f"- **Address**: `{lin.get('address', '')}`")

    # Protocol summary
    proto = data.get("transport_protocol", {})
    if proto:
        lines.append(f"\n### Transport Protocol")
        for step_name, step in proto.items():
            if isinstance(step, dict):
                lines.append(f"- **{step_name}**: {step.get('description', '')}")

    # Fractures summary
    frac = data.get("fracture_field", {})
    fractures = frac.get("fractures", {})
    if fractures:
        lines.append(f"\n### Fracture Field")
        for name, desc in fractures.items():
            lines.append(f"- **{name}**: {desc}")
        lines.append(f"- **Resolution**: {frac.get('resolution', '')}")

    # Cycles summary
    cycles = data.get("cycle_registry", {})
    if cycles:
        lines.append(f"\n### Active Cycles")
        for cid, cdata in cycles.items():
            if isinstance(cdata, dict):
                lines.append(f"- **{cid}**: {cdata.get('packet_id', '')} [{cdata.get('status', '')}]")

    return "\n".join(lines)


def _format_tesseract(data: dict) -> str:
    tess = data.get("tesseract_geometry", {})
    outer = tess.get("outer_cube", {})
    inner = tess.get("inner_cube", {})
    time_ax = tess.get("time_axis", {})
    edges = tess.get("transport_edges", {})

    lines = [
        "## 4D Tesseract Geometry\n",
        "### Outer Cube (Live Surface)",
        f"**Description**: {outer.get('description', '')}",
        f"**Cell ID**: `{outer.get('cell_id', '')}`",
        f"**Children**: {outer.get('children_count', '?')} total "
        f"({outer.get('native_docs', '?')} docs, {outer.get('folders', '?')} folders)",
        f"**Contents**: {outer.get('contents', '')}",
        "",
        "### Inner Cube (Stabilized Archive)",
        f"**Description**: {inner.get('description', '')}",
    ]
    layers = inner.get("layers", {})
    if layers:
        lines.append("**Layers**:")
        for name, desc in layers.items():
            lines.append(f"  - **{name}**: {desc}")

    lines.extend([
        "",
        "### Time Axis",
        f"**Description**: {time_ax.get('description', '')}",
        f"**Direction**: {time_ax.get('direction', '')}",
    ])
    ops = time_ax.get("operations", [])
    if ops:
        lines.append(f"**Operations**: {' → '.join(ops)}")

    lines.extend([
        "",
        "### Transport Edges",
        f"**Description**: {edges.get('description', '')}",
    ])
    types = edges.get("types", [])
    if types:
        lines.append(f"**Types**: {', '.join(types)}")

    return "\n".join(lines)


def _format_lineage(data: dict) -> str:
    lin = data.get("lineage_chain", {})
    lines = [
        "## Lineage Chain\n",
        f"**Description**: {lin.get('description', '')}",
        f"**Address**: `{lin.get('address', '')}`",
        "",
        "### Layers",
    ]
    layers = lin.get("layers", {})
    for code, desc in layers.items():
        lines.append(f"- **{code}**: {desc}")
    return "\n".join(lines)


def _format_protocol(data: dict) -> str:
    proto = data.get("transport_protocol", {})
    lines = ["## Transport Protocol\n"]
    step_num = 0
    for step_name, step in proto.items():
        if isinstance(step, dict):
            step_num += 1
            lines.append(f"### Step {step_num}: {step_name}")
            lines.append(f"**Description**: {step.get('description', '')}")
            lines.append(f"**Input**: {step.get('input', '')}")
            lines.append(f"**Output**: {step.get('output', '')}")
            lines.append(f"**Medium**: {step.get('medium', '')}")
            lines.append("")
    return "\n".join(lines)


def _format_fractures(data: dict) -> str:
    frac = data.get("fracture_field", {})
    lines = [
        "## Fracture Field\n",
        f"**Description**: {frac.get('description', '')}",
        "",
        "### Named Fractures",
    ]
    fractures = frac.get("fractures", {})
    for name, desc in fractures.items():
        lines.append(f"- **{name}**: {desc}")
    lines.append(f"\n### Resolution")
    lines.append(frac.get("resolution", ""))
    return "\n".join(lines)


def _format_cycles(data: dict) -> str:
    cycles = data.get("cycle_registry", {})
    lines = ["## Cycle Registry\n"]
    for cid, cdata in cycles.items():
        if isinstance(cdata, dict):
            lines.append(f"### {cid}")
            lines.append(f"**Packet ID**: `{cdata.get('packet_id', '')}`")
            lines.append(f"**Truth Class**: {cdata.get('truth_class', '')}")
            lines.append(f"**Contraction Target**: `{cdata.get('contraction_target', '')}`")
            lines.append(f"**Status**: {cdata.get('status', '')}")
            lines.append("")
    return "\n".join(lines)
