"""
NEXT-Omega Live Cell Constitution
==================================
Defines the minimum lawful execution cell:
  row -> packet -> trace -> cert -> seed

Each schema represents one layer of the execution membrane.
The metro map traces the soul's path through one complete cycle.
"""

from ._cache import JsonCache

_CELL = JsonCache("live_cell_constitution.json")


def query_live_cell(component: str = "all") -> str:
    """
    Query the NEXT-Omega Live Cell Constitution.

    Components:
      - all       : Full constitution overview
      - schemas   : All 6 cell schemas (BoardStateRow, PacketSynapse, etc.)
      - schema:X  : Specific schema (e.g. schema:BoardStateRow, schema:TraceCert)
      - metro     : 14-station execution metro map
      - station:X : Specific metro station (e.g. station:M00, station:M60)
      - liminal   : Liminal coordinate system
      - soul      : Soul stamp schema
      - route     : Route types and signature
    """
    data = _CELL.load()
    comp = component.strip().lower()

    if comp == "all":
        return _format_all(data)
    elif comp == "schemas":
        return _format_schemas(data)
    elif comp.startswith("schema:"):
        return _format_one_schema(data, comp.split(":", 1)[1])
    elif comp == "metro":
        return _format_metro(data)
    elif comp.startswith("station:"):
        return _format_station(data, comp.split(":", 1)[1])
    elif comp == "liminal":
        return _format_liminal(data)
    elif comp == "soul":
        return _format_soul(data)
    elif comp == "route":
        return _format_routes(data)
    else:
        return (
            f"Unknown component '{component}'. Use: all, schemas, "
            "schema:<name>, metro, station:<code>, liminal, soul, route"
        )


def live_cell_status() -> str:
    """Return a status summary for the resource endpoint."""
    data = _CELL.load()
    m = data["meta"]
    schemas = data["cell_schema"]
    stations = data["metro_map"]["stations"]
    return (
        "## NEXT-Omega Live Cell Constitution\n\n"
        f"**Minimum Lawful Unit**: `{m['minimum_lawful_unit']}`\n"
        f"**Schemas**: {m['total_schemas']} "
        f"({', '.join(schemas.keys())})\n"
        f"**Metro Stations**: {m['metro_stations']} "
        f"(M00 Root -> MD0 Loop)\n"
        f"**Route Signature**: `{m['route_signature']}`\n"
        f"**Source**: {m['source']}\n"
    )


# ── Formatters ──────────────────────────────────────────────────────

def _format_all(data: dict) -> str:
    m = data["meta"]
    lines = [
        "## NEXT-Omega Live Cell Constitution\n",
        f"**Title**: {m['title']}",
        f"**Source**: {m['source']}",
        f"**Minimum Lawful Unit**: `{m['minimum_lawful_unit']}`",
        f"**Route Signature**: `{m['route_signature']}`\n",
        "### Cell Schemas\n",
    ]
    for name, schema in data["cell_schema"].items():
        lines.append(f"- **{name}** (v{schema['version']}): {schema['description']}")

    lines.append("\n### Metro Stations\n")
    for code, station in data["metro_map"]["stations"].items():
        lines.append(f"- **{code}** {station['name']}: {station['role']}")

    lines.append(f"\n### Route Types\n")
    for rtype, info in data["metro_map"]["route_types"].items():
        lines.append(f"- **{rtype}**: {info['from']} -> {info['to']} ({info['description']})")

    return "\n".join(lines)


def _format_schemas(data: dict) -> str:
    lines = ["## Cell Schemas\n"]
    for name, schema in data["cell_schema"].items():
        lines.append(f"\n### {name} (v{schema['version']})")
        lines.append(schema["description"])
        lines.append("\n**Fields**:")
        for field, desc in schema["fields"].items():
            lines.append(f"  - `{field}`: {desc}")
        # Show constraint/property/invariant
        for key in ["invariant", "routing_rule", "constraint", "property", "verification"]:
            if key in schema:
                lines.append(f"\n**{key.title()}**: {schema[key]}")
    return "\n".join(lines)


def _format_one_schema(data: dict, name: str) -> str:
    schemas = data["cell_schema"]
    # Case-insensitive match
    for key, schema in schemas.items():
        if key.lower() == name.lower() or name.lower() in key.lower():
            lines = [f"## {key} (v{schema['version']})\n", schema["description"], "\n**Fields**:"]
            for field, desc in schema["fields"].items():
                lines.append(f"  - `{field}`: {desc}")
            for k in ["invariant", "routing_rule", "constraint", "property", "verification"]:
                if k in schema:
                    lines.append(f"\n**{k.title()}**: {schema[k]}")
            return "\n".join(lines)
    return f"Schema '{name}' not found. Available: {', '.join(schemas.keys())}"


def _format_metro(data: dict) -> str:
    metro = data["metro_map"]
    lines = [f"## Execution Metro Map\n", metro["description"], ""]
    for code, station in metro["stations"].items():
        lines.append(
            f"- **{code}** {station['name']} [{station['element']}] "
            f"({station['phase']}): {station['role']}"
        )
    lines.append("\n### Route Types\n")
    for rtype, info in metro["route_types"].items():
        lines.append(f"- **{rtype}**: {info['from']} -> {info['to']} -- {info['description']}")
    return "\n".join(lines)


def _format_station(data: dict, code: str) -> str:
    code_upper = code.upper()
    stations = data["metro_map"]["stations"]
    if code_upper in stations:
        s = stations[code_upper]
        return (
            f"## Station {code_upper}: {s['name']}\n\n"
            f"**Role**: {s['role']}\n"
            f"**Element**: {s['element']}\n"
            f"**Phase**: {s['phase']}"
        )
    return f"Station '{code}' not found. Available: {', '.join(stations.keys())}"


def _format_liminal(data: dict) -> str:
    lc = data["liminal_coordinates"]
    lines = [
        "## Liminal Coordinates\n",
        lc["description"],
        f"\n**Format**: `{lc['format']}`",
        f"**Example**: `{lc['example']}`\n",
        "### Golden Points\n",
    ]
    for key, gp in lc["golden_points"].items():
        lines.append(f"- **{key}** = {gp['value']}: {gp['meaning']}")
    return "\n".join(lines)


def _format_soul(data: dict) -> str:
    ss = data["soul_stamp_schema"]
    lines = [
        "## Soul Stamp Schema\n",
        ss["description"],
        f"\n**Property**: {ss['property']}\n",
        "**Fields**:",
    ]
    for field, desc in ss["fields"].items():
        lines.append(f"  - `{field}`: {desc}")
    return "\n".join(lines)


def _format_routes(data: dict) -> str:
    m = data["meta"]
    routes = data["metro_map"]["route_types"]
    lines = [
        "## Route Signature\n",
        f"**Full Signature**: `{m['route_signature']}`\n",
    ]
    for rtype, info in routes.items():
        lines.append(f"### {rtype}")
        lines.append(f"  {info['from']} -> {info['to']}: {info['description']}")
    return "\n".join(lines)
