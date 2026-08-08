from __future__ import annotations

from .kc144_polyatlas import GRAPH_LAYERS

POLYATLAS_TOOLS = [
    {
        "name": "athena_kc144_polyatlas_status",
        "description": "Return the executable KC144 polyatlas identity, source-bound state, cardinalities, coordinate/decomposition counts, and epistemic boundary.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_kc144_polyatlas_manifest",
        "description": "Return the complete 16-coordinate Rosetta manifest, four simultaneous KC144 decompositions, KC27 shell law, resolution family, sphere summary, and source lineage.",
        "inputSchema": {"type": "object", "additionalProperties": False},
    },
    {
        "name": "athena_kc144_polyatlas_seat",
        "description": "Resolve one immutable KC144 GID through matrix, semantic, 6x3x8 spherical, 4x36 elemental, wheel, mirror, cubed-sphere, and Riemann coordinates.",
        "inputSchema": {
            "type": "object",
            "required": ["gid"],
            "properties": {
                "gid": {"type": "integer", "minimum": 1, "maximum": 144},
                "radius": {"type": "number", "exclusiveMinimum": 0},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_polyatlas_rosetta",
        "description": "Compile one chapter/shelf locus into the exact C01..C16 Rosetta address, including reversible GID729 serialization, KC144 host fibre, sphere/Riemann chart, KC54, KC108, and exact resolution transport.",
        "inputSchema": {
            "type": "object",
            "required": ["chapter", "shelf"],
            "properties": {
                "chapter": {"type": "integer", "minimum": 1, "maximum": 27},
                "shelf": {"type": "integer", "minimum": 1, "maximum": 27},
                "conjugate": {"type": "integer", "minimum": 0, "maximum": 1},
                "element": {"type": "integer", "minimum": 0, "maximum": 3},
                "target_resolution": {"type": "integer", "minimum": 3},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_resolution_transport",
        "description": "Transport a station between odd 3*m resolutions without rounding, returning exact normalized/centered fractions and reversible two-point barycentric support.",
        "inputSchema": {
            "type": "object",
            "required": ["source_resolution", "target_resolution", "station"],
            "properties": {
                "source_resolution": {"type": "integer", "minimum": 3},
                "target_resolution": {"type": "integer", "minimum": 3},
                "station": {"type": "integer", "minimum": 1},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_resolution_family",
        "description": "Generate a bounded segment of the N=3m, m odd resolution family with centers, mirror laws, species, and predecessor/successor resolutions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "start_multiplier": {"type": "integer", "minimum": 1},
                "count": {"type": "integer", "minimum": 1, "maximum": 200},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_sphere_atlas",
        "description": "Read a bounded page of the 144-cell six-face gnomonic/Riemann sphere atlas, with exact cell solid angle, area, radial wedge volume, and reserved portal fibre.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "minimum": 0, "maximum": 143},
                "limit": {"type": "integer", "minimum": 1, "maximum": 144},
                "radius": {"type": "number", "exclusiveMinimum": 0},
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_polyatlas_route",
        "description": "Route between KC144 seats by deterministic BFS over explicitly selected matrix, wheel, mirror, face-grid, or spherical-proximity layers. Reachability is never promoted into proof.",
        "inputSchema": {
            "type": "object",
            "required": ["src", "dst"],
            "properties": {
                "src": {"type": "integer", "minimum": 1, "maximum": 144},
                "dst": {"type": "integer", "minimum": 1, "maximum": 144},
                "layers": {
                    "type": "array",
                    "items": {"type": "string", "enum": list(GRAPH_LAYERS)},
                    "uniqueItems": True,
                    "minItems": 1,
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "athena_kc144_polyatlas_validate",
        "description": "Run executable bijection, inversion, shell, GID729, exact transport, sphere-volume, and typed-route checks; emit a digest-bound local validation receipt without self-promotion.",
        "inputSchema": {
            "type": "object",
            "properties": {"include_details": {"type": "boolean"}},
            "additionalProperties": False,
        },
    },
]

POLYATLAS_RESOURCES = [
    {"uri": "athena://kc144/polyatlas/status", "name": "KC144 Polyatlas Status", "mimeType": "application/json"},
    {"uri": "athena://kc144/polyatlas/manifest", "name": "KC144 16-Coordinate Polyatlas Manifest", "mimeType": "application/json"},
    {"uri": "athena://kc144/polyatlas/sources", "name": "KC144 Polyatlas Source Lineage", "mimeType": "application/json"},
    {"uri": "athena://kc144/polyatlas/sphere", "name": "KC144 Riemann Sphere Summary", "mimeType": "application/json"},
    {"uri": "athena://kc144/polyatlas/family", "name": "KC144 Odd-Ternary Resolution Family", "mimeType": "application/json"},
    {"uri": "athena://kc144/polyatlas/validation", "name": "KC144 Polyatlas Validation Receipt", "mimeType": "application/json"},
]
