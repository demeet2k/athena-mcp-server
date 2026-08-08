from __future__ import annotations

COLLECTIVE_TOOLS = [
    {
        "name": "athena_collective_plan",
        "description": "Select HIVE/SWARM/PACK/FLOCK/HERD/POD geometry, right-size active workers by marginal utility, preserve reserve capacity, allocate roles/topology, and return a COLLECTIVE coordinate packet.",
        "inputSchema": {
            "type": "object",
            "required": ["signals"],
            "properties": {
                "signals": {
                    "type": "object",
                    "properties": {
                        "hardness": {"type": "number", "minimum": 0, "maximum": 1},
                        "uncertainty": {"type": "number", "minimum": 0, "maximum": 1},
                        "divisibility": {"type": "number", "minimum": 0, "maximum": 1},
                        "coupling": {"type": "number", "minimum": 0, "maximum": 1},
                        "volatility": {"type": "number", "minimum": 0, "maximum": 1},
                        "risk": {"type": "number", "minimum": 0, "maximum": 1},
                        "migration": {"type": "number", "minimum": 0, "maximum": 1},
                        "repetition": {"type": "number", "minimum": 0, "maximum": 1},
                        "reuse": {"type": "number", "minimum": 0, "maximum": 1},
                        "innovation": {"type": "number", "minimum": 0, "maximum": 1},
                        "latency_sensitivity": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence_sensitivity": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "additionalProperties": False
                },
                "max_workers": {"type": "integer", "minimum": 1, "maximum": 256},
                "reserve_fraction": {"type": "number", "minimum": 0, "maximum": 0.8},
                "unit_cost": {"type": "number", "minimum": 0},
                "lineage": {"type": ["string", "null"]}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_collective_evaluate",
        "description": "Score a concrete group organization with explicit cost/output vectors and return-on-group-organization; exposes dense-connectivity, duplication, switching, contagion and maintenance penalties.",
        "inputSchema": {
            "type": "object",
            "required": ["configuration"],
            "properties": {
                "configuration": {
                    "type": "object",
                    "required": ["workers"],
                    "properties": {
                        "workers": {"type": "integer", "minimum": 1, "maximum": 256},
                        "avg_degree": {"type": "integer", "minimum": 0, "maximum": 255},
                        "coupling": {"type": "number", "minimum": 0, "maximum": 1},
                        "specialization": {"type": "number", "minimum": 0, "maximum": 1},
                        "diversity": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence_quality": {"type": "number", "minimum": 0, "maximum": 1},
                        "redundancy": {"type": "number", "minimum": 0, "maximum": 1},
                        "reserve_fraction": {"type": "number", "minimum": 0, "maximum": 1},
                        "reuse": {"type": "number", "minimum": 0, "maximum": 1},
                        "volatility": {"type": "number", "minimum": 0, "maximum": 1},
                        "duplication": {"type": "number", "minimum": 0, "maximum": 1},
                        "switching": {"type": "number", "minimum": 0, "maximum": 1},
                        "maintenance": {"type": "number", "minimum": 0, "maximum": 1},
                        "failure_exposure": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_collective_quorum",
        "description": "Run evidence-sensitive quorum selection with explicit cross-inhibition, contradiction blocking, risk-dependent threshold and required winning margin; consensus alone cannot commit.",
        "inputSchema": {
            "type": "object",
            "required": ["candidates"],
            "properties": {
                "candidates": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 128,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "support": {"type": "number", "minimum": 0, "maximum": 1},
                            "evidence_quality": {"type": "number", "minimum": 0, "maximum": 1},
                            "inhibition": {"type": "number", "minimum": 0, "maximum": 1},
                            "contradiction": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "additionalProperties": False
                    }
                },
                "risk": {"type": "number", "minimum": 0, "maximum": 1},
                "evidence_sensitivity": {"type": "number", "minimum": 0, "maximum": 1},
                "inhibition_gain": {"type": ["number", "null"], "minimum": 0, "maximum": 1}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_stigmergy_update",
        "description": "Update artifact/routing priority through evidence/reuse/downstream reinforcement plus age, staleness and contradiction evaporation.",
        "inputSchema": {
            "type": "object",
            "required": ["current_score", "observations"],
            "properties": {
                "current_score": {"type": "number", "minimum": 0, "maximum": 1},
                "observations": {
                    "type": "object",
                    "properties": {
                        "quality": {"type": "number", "minimum": 0, "maximum": 1},
                        "novelty": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "reuse": {"type": "number", "minimum": 0, "maximum": 1},
                        "bridge_value": {"type": "number", "minimum": 0, "maximum": 1},
                        "downstream_gain": {"type": "number", "minimum": 0, "maximum": 1},
                        "staleness": {"type": "number", "minimum": 0, "maximum": 1},
                        "contradiction": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "additionalProperties": False
                },
                "age": {"type": "number", "minimum": 0},
                "evaporation_rate": {"type": "number", "minimum": 0, "maximum": 1},
                "deposit_gain": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "additionalProperties": False
        }
    },
    {
        "name": "athena_collective_health",
        "description": "Evaluate collective homeostasis and emit concrete corrective actions for saturation, duplication, latency, error, staleness, contagion, reserve depletion, weak evidence, bridge overhead and coordination drag.",
        "inputSchema": {
            "type": "object",
            "required": ["metrics"],
            "properties": {
                "metrics": {
                    "type": "object",
                    "properties": {
                        "context_saturation": {"type": "number", "minimum": 0, "maximum": 1},
                        "duplication": {"type": "number", "minimum": 0, "maximum": 1},
                        "latency": {"type": "number", "minimum": 0, "maximum": 1},
                        "error_rate": {"type": "number", "minimum": 0, "maximum": 1},
                        "stale_ratio": {"type": "number", "minimum": 0, "maximum": 1},
                        "contagion": {"type": "number", "minimum": 0, "maximum": 1},
                        "reserve_fraction": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence_quality": {"type": "number", "minimum": 0, "maximum": 1},
                        "bridge_overhead": {"type": "number", "minimum": 0, "maximum": 1},
                        "coordination_overhead": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        }
    }
]
