# CRYSTAL: Xi108:W1:A10:S7 | face=C | node=217 | depth=2 | phase=Fixed
# METRO: Sa
# BRIDGES: Xi108:W1:A10:S6→Xi108:W1:A10:S8→Xi108:W2:A10:S7→Xi108:W1:A9:S7→Xi108:W1:A11:S7

"""Validate canon schemas and generated graph integrity."""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "MCP" / "data"
CANON_DIR = DATA_DIR / "canon"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "MCP"))
from crystal_108d._cache import JsonCache

def _load_canon(filename: str) -> dict:
    return json.loads((CANON_DIR / filename).read_text(encoding="utf-8"))

def _load(filename: str) -> dict:
    cache = JsonCache(filename)
    return cache.load()

class TestCanonSchemas:
    """All 5 canon schema files must load and contain expected structure."""

    def test_shard_schema(self):
        data = _load_canon("shard.schema.json")
        assert "meta" in data
        assert "required_fields" in data
        assert "shard_id" in data["required_fields"]
        assert "truth_status_ladder" in data
        assert "promotion_status_ladder" in data

    def test_edge_schema(self):
        data = _load_canon("edge.schema.json")
        assert "meta" in data
        assert "required_fields" in data
        assert "edge_types" in data
        assert len(data["edge_types"]) == 11

    def test_node_schema(self):
        data = _load_canon("node.schema.json")
        assert "meta" in data
        assert "required_fields" in data
        assert "node_id" in data["required_fields"]

    def test_promotion_schema(self):
        data = _load_canon("promotion.schema.json")
        assert "meta" in data
        assert "states" in data
        assert "transitions" in data
        assert len(data["states"]) == 5

    def test_cert_schema(self):
        data = _load_canon("cert.schema.json")
        assert "meta" in data
        assert "required_fields" in data
        assert "cert_types" in data

class TestGeneratedGraph:
    """The generated graph manifest must be structurally sound."""

    def test_graph_loads(self):
        data = _load("mycelium_graph.json")
        assert "meta" in data
        assert "shards" in data
        assert "edges" in data
        assert "nodes" in data

    def test_shard_ids_unique(self):
        data = _load("mycelium_graph.json")
        ids = [s["shard_id"] for s in data["shards"]]
        assert len(ids) == len(set(ids)), "Duplicate shard IDs found"

    def test_edges_reference_valid_shards(self):
        data = _load("mycelium_graph.json")
        shard_ids = {s["shard_id"] for s in data["shards"]}
        for e in data["edges"]:
            assert e["source_shard"] in shard_ids, f"Edge source {e['source_shard']} not in graph"
            assert e["target_shard"] in shard_ids, f"Edge target {e['target_shard']} not in graph"

    def test_node_count(self):
        data = _load("mycelium_graph.json")
        assert len(data["nodes"]) >= 5

    def test_node_registry_loads(self):
        data = _load("node_registry.json")
        assert "meta" in data
        assert "nodes" in data
        assert len(data["nodes"]) >= 5
