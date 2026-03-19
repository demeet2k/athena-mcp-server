# CRYSTAL: Xi108:W2:A1:S15 | face=S | node=117 | depth=2 | phase=Cardinal
# METRO: Mt
# BRIDGES: Xi108:W2:A1:S14→Xi108:W2:A1:S16→Xi108:W1:A1:S15→Xi108:W3:A1:S15→Xi108:W2:A2:S15

"""
Möbius Lens Calculus — 4×4 kernel, four constitutive projections (S/F/C/R),
cross-lens laws, 15-station SFCR lattice, 96-slot cockpit, and per-dimension
lens renderings.

Source: MOBIUS LENSES.docx
"""

from ._cache import JsonCache

_mobius = JsonCache("mobius_lenses.json")

def query_mobius_lens(lens: str = "all", dimension: int = 0) -> str:
    """Query the Möbius lens calculus. Lens: square/flower/cloud/fractal/kernel/laws/lattice/cockpit/operators/all.
    Dimension (0=overview, 4/6/8/10/12) shows per-dimension lens rendering."""
    d = _mobius.load()
    lens = lens.lower().strip()

    # Kernel query
    if lens == "kernel":
        k = d["kernel_4x4"]
        lines = [f"## {k['name']}\n"]
        lines.append(f"**Carrier**: {k['carrier']}")
        lines.append(f"**Definition**: {k['definition']}")
        lines.append(f"**Object Tuple**: `{k['object_tuple']}`")
        lines.append(f"\n**Seed Law L₄**:")
        for row in k["seed_law_L4"]:
            lines.append(f"  {row}")
        lines.append(f"\n**Kernel Law ℓ₄**:")
        for row in k["kernel_law_ell4"]:
            lines.append(f"  {row}")
        m = k["mobius_involution"]
        lines.append(f"\n**Möbius Involution**: {m['map']}")
        lines.append(f"  Property: {m['property']}")
        lines.append(f"  Kernel law: {m['kernel_law']}")
        lines.append(f"\n**Payload**: {k['payload_size']}")
        return "\n".join(lines)

    # Individual lens query
    if lens in ("square", "flower", "cloud", "fractal", "s", "f", "c", "r"):
        code_map = {"s": "square", "f": "flower", "c": "cloud", "r": "fractal"}
        key = code_map.get(lens, lens)
        le = d["lenses"][key]
        lines = [f"## {le['name']} ({le['code']}) — {le['subtitle']}\n"]
        lines.append(f"**Element**: {le['element']}")
        lines.append(f"**Description**: {le['description']}")

        # 4D object
        if "projection_4d" in le:
            lines.append(f"\n### 4D Projection")
            lines.append(f"  {le['projection_4d']}")
        if "full_object_4d" in le:
            lines.append(f"  Full: {le['full_object_4d']}")
        if "chart_map" in le:
            lines.append(f"\n### Chart Map")
            lines.append(f"  {le['chart_map']}")
        if "relation_coordinates" in le:
            for k2, v in le["relation_coordinates"].items():
                lines.append(f"  {k2} = {v}")
        if "generators" in le:
            lines.append("\n### Generators")
            for name, gen in le["generators"].items():
                lines.append(f"  **{name}**: {gen['map']} (preserves {gen['preserves']})")
        if "cloud_fiber" in le:
            lines.append(f"\n### Cloud Fiber: {le['cloud_fiber']}")
            lines.append(f"  Admissibility: {le['admissibility']}")
            lines.append(f"  Fiber size: {le['fiber_size']}")
            ft = le["fiber_theorem"]
            lines.append(f"\n### {ft['name']}")
            lines.append(f"  {ft['statement']}")
        if "operations" in le:
            lines.append("\n### Operations")
            for k2, v in le["operations"].items():
                lines.append(f"  **{k2}**: {v}")
            if "closure_law" in le:
                lines.append(f"  Closure: {le['closure_law']}")

        # 6D
        if "at_6d" in le:
            s6 = le["at_6d"]
            lines.append(f"\n### At 6D")
            lines.append(f"  Object: {s6['object']}")
            for k2, v in s6.items():
                if k2 != "object":
                    if isinstance(v, list):
                        lines.append(f"  {k2}: {', '.join(v)}")
                    else:
                        lines.append(f"  {k2}: {v}")

        lines.append(f"\n**Higher Octave**: {le['higher_octave']}")

        # Dimension-specific
        if dimension > 0:
            dim_key = f"{dimension}D"
            dim_map = d.get("even_dimension_lens_map", {})
            if dim_key in dim_map:
                lines.append(f"\n### Lens at {dim_key}")
                lines.append(f"  {dim_map[dim_key].get(key, 'Not defined at this dimension')}")

        return "\n".join(lines)

    # Cross-lens laws
    if lens in ("laws", "cross_lens", "cross-lens"):
        laws = d["cross_lens_laws"]
        lines = ["## Cross-Lens Laws\n"]
        for law in laws:
            lines.append(f"### {law['index']}. {law['name']}")
            lines.append(f"  `{law['statement']}`")
            lines.append(f"  {law['meaning']}\n")
        return "\n".join(lines)

    # SFCR lattice
    if lens in ("lattice", "sfcr", "stations"):
        lat = d["sfcr_lattice"]
        lines = [f"## {lat['name']}\n"]
        lines.append(f"**Definition**: {lat['definition']}")
        lines.append(f"**Total**: {lat['total_stations']} stations\n")
        for st in lat["stations"]:
            lines.append(f"  [{st['mask']:>2}] **{st['code']:>4}** ({st['type']}) — {st['role']}")
        if "pair_bridges" in lat:
            lines.append("\n### Pair Bridges")
            for b in lat["pair_bridges"]:
                lines.append(f"  **{b['bridge']}**: {b['transport']}")
        if "triangle_closures" in lat:
            lines.append("\n### Triangle Closures")
            for t in lat["triangle_closures"]:
                lines.append(f"  **{t['triple']}**: {t['meaning']}")
        if "structure" in lat:
            st_info = lat["structure"]
            lines.append(f"\n### Structure")
            for k2, v in st_info.items():
                lines.append(f"  **{k2}**: {v}")
        return "\n".join(lines)

    # 96-slot cockpit
    if lens in ("cockpit", "96"):
        cp = d["cockpit_96"]
        lines = [f"## {cp['name']}\n"]
        lines.append(f"**Formula**: `{cp['formula']}`")
        if "visible_slot" in cp:
            lines.append(f"**Visible Slot**: {cp['visible_slot']}")
        if "full_slot" in cp:
            lines.append(f"**Full Slot**: {cp['full_slot']}")
        lines.append(f"**Backed By**: {cp['backed_by']}")
        if "embedding_law" in cp:
            lines.append(f"**Embedding Law**: `{cp['embedding_law']}`")
        lines.append("\n### Chart Generators")
        for name, gen in cp["chart_generators"].items():
            lines.append(f"  **{name}**: {gen['generator']} ({gen['permutation']})")
        return "\n".join(lines)

    # Operators
    if lens in ("operators", "ops"):
        ops = d["operator_set"]
        lines = [f"## {ops['name']}\n"]
        for op in ops["operators"]:
            lines.append(f"  **{op['symbol']}** ({op['name']}): {op['action']}")
        return "\n".join(lines)

    # 6-shell lift
    if lens in ("6shell", "shell_lift", "six_shell"):
        sl = d["six_shell_lift"]
        lines = [f"## {sl['name']}\n"]
        lines.append(f"**Structure**: `{sl['structure']}`")
        lines.append(f"**Sectors**: {sl['total_sectors']} ({', '.join(sl['superphases'])} × mirror)")
        lines.append(f"**Shell Transport**: `{sl['shell_transport']}`")
        lines.append(f"**Full Atlas**: {sl['full_atlas_size']}")
        lines.append(f"**Embedded Payload**: {sl['embedded_payload']}")
        lines.append(f"**Total Addressable**: {sl['total_addressable']}")
        return "\n".join(lines)

    # Dimension map
    if dimension > 0:
        dim_key = f"{dimension}D"
        dim_map = d.get("even_dimension_lens_map", {})
        if dim_key in dim_map:
            lines = [f"## All Lenses at {dim_key}\n"]
            for l_name, desc in dim_map[dim_key].items():
                lines.append(f"  **{l_name.title()}**: {desc}")
            return "\n".join(lines)
        return f"No lens data for {dim_key}. Available: 4D, 6D, 8D, 10D, 12D."

    # Default: overview
    m = d["meta"]
    lines = ["## Möbius Lens Calculus — Overview\n"]
    lines.append(f"**Kernel**: {m['kernel_size']} ({m['seed_law']})")
    lines.append(f"**Lenses**: {', '.join(m['lenses'])} ({', '.join(m['lens_codes'])})")
    lines.append(f"**SFCR Stations**: {m['sfcr_stations']}")
    lines.append(f"**Cockpit Slots**: {m['cockpit_slots']}")
    lines.append(f"**Cross-Lens Laws**: {m['cross_lens_laws']}")
    lines.append(f"**Governing Equation**: `{m['governing_equation']}`")
    lines.append(f"**Lift Stages**: {' → '.join(m['lift_stages'])}")
    lines.append("\n**Available queries**: kernel, square, flower, cloud, fractal, laws, lattice, cockpit, operators, 6shell, all")
    lines.append("**Dimension filter**: pass dimension=4/6/8/10/12 for per-dimension lens view")
    return "\n".join(lines)

def query_sfcr_station(station: str) -> str:
    """Query a specific SFCR station by code (e.g. 'SF', 'SFCR', 'C') or mask number (1-15)."""
    d = _mobius.load()
    lat = d["sfcr_lattice"]
    station = station.strip().upper()

    # Try as mask number
    try:
        mask = int(station)
        for st in lat["stations"]:
            if st["mask"] == mask:
                lines = [f"## SFCR Station [{st['mask']}]: {st['code']}\n"]
                lines.append(f"**Type**: {st['type']}")
                lines.append(f"**Lenses**: {', '.join(st['lenses'])}")
                lines.append(f"**Role**: {st['role']}")
                # Check bridges
                for b in lat.get("pair_bridges", []):
                    if b["bridge"] == st["code"]:
                        lines.append(f"\n**Bridge Transport**: {b['transport']}")
                for t in lat.get("triangle_closures", []):
                    if t["triple"] == st["code"]:
                        lines.append(f"\n**Triangle Defect**: {t['defect']}")
                        lines.append(f"**Meaning**: {t['meaning']}")
                return "\n".join(lines)
        return f"No station with mask {mask}. Range: 1-15."
    except ValueError:
        pass

    # Try as code
    for st in lat["stations"]:
        if st["code"] == station:
            lines = [f"## SFCR Station [{st['mask']}]: {st['code']}\n"]
            lines.append(f"**Type**: {st['type']}")
            lines.append(f"**Lenses**: {', '.join(st['lenses'])}")
            lines.append(f"**Role**: {st['role']}")
            for b in lat.get("pair_bridges", []):
                if b["bridge"] == st["code"]:
                    lines.append(f"\n**Bridge Transport**: {b['transport']}")
            for t in lat.get("triangle_closures", []):
                if t["triple"] == st["code"]:
                    lines.append(f"\n**Triangle Defect**: {t['defect']}")
                    lines.append(f"**Meaning**: {t['meaning']}")
            return "\n".join(lines)

    return f"Station '{station}' not found. Use S/F/C/R codes or mask 1-15. Examples: SF, SFCR, 7, 15."
