from __future__ import annotations

import json
from pathlib import Path
import sys

MCP = Path(__file__).resolve().parents[1] / "MCP"
sys.path.insert(0, str(MCP))

from kc144_meta_v12 import (
    MAPS,
    compress_seed,
    parallel_wave,
    reconstruct_seed,
    route,
    station,
    transform,
    validate,
)
from kc144_navigation_v12 import register_kc144_v12


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(function):
            self.tools[function.__name__] = function
            return function
        return decorator


def test_map_count():
    assert len(MAPS) == 54


def test_grid_is_bijective():
    assert len({station(gid)["grid"] for gid in range(1, 145)}) == 144


def test_d4_inverse_roundtrip_all_stations():
    for gid in range(1, 145):
        rotated = transform(gid, "grid-rotate-90")["output_gid"]
        restored = transform(rotated, "grid-rotate-270")["output_gid"]
        assert restored == gid


def test_full_crystal_seed_roundtrip():
    seed = compress_seed(list(range(1, 145)), maps=["map-of-maps"], label="FULL")
    assert reconstruct_seed(seed)["gids"] == list(range(1, 145))


def test_h06_to_m12_route():
    assert route("H06", "M12")["status"] == "ROUTE_FOUND"


def test_parallel_receipt_is_deterministic():
    query = "quaternion lift proof routing compression return"
    assert parallel_wave(query, 4)["receipt"] == parallel_wave(query, 4)["receipt"]


def test_fourteen_mcp_tools_are_registered():
    mcp = FakeMCP()
    register_kc144_v12(mcp)
    assert len(mcp.tools) == 14
    assert json.loads(mcp.tools["kc144_validate"]())["status"] == "PASS"


def test_v12_validation():
    assert validate()["status"] == "PASS"
