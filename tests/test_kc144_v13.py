from __future__ import annotations
import json
import sys
import zipfile
from pathlib import Path

MCP = Path(__file__).resolve().parents[1] / "MCP"
sys.path.insert(0, str(MCP))

from kc144_harness_v13 import Harness, HARNESS_MAPS, depth, scan, tunnel, validate
from kc144_navigation_v13 import register_kc144_v13


class FakeMCP:
    def __init__(self):
        self.tools = {}

    def tool(self):
        def decorator(function):
            self.tools[function.__name__] = function
            return function
        return decorator


def test_maps_depth_and_tunnel():
    assert len(HARNESS_MAPS) == 18
    assert depth(3)["rows"][-1]["br"] == 1 + 20 * 4 ** 3
    assert tunnel("KC", {"digits": [13]}, 4, 2)["output"]["depth"] == 4
    assert validate()["status"] == "PASS"


def test_scan_run_and_replay(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("quaternion proof source compression return")
    bundle = tmp_path / "bundle.zip"
    with zipfile.ZipFile(bundle, "w") as archive:
        archive.writestr("README.md", "mycelium replay")
    scanned = scan([tmp_path])
    assert scanned["registry"]["count"] == 2
    assert scanned["registry"]["body_count"] == 2
    harness = Harness(tmp_path / "harness.sqlite")
    run = harness.run("quaternion proof compression return", [tmp_path])
    assert run["replay"]["verified"]
    assert harness.replay(run["run_id"])["verified"]
    assert run["return_packet"]["production_evidence"] == [0, 86, 0, 1, 0]
    assert run["return_packet"]["i10_receipt"] is None


def test_deterministic_receipt(tmp_path):
    source = tmp_path / "x.md"
    source.write_text("source fiber return")
    first = Harness().run("source fiber return", [source])
    second = Harness().run("source fiber return", [source])
    assert first["merge_receipt"] == second["merge_receipt"]


def test_registration():
    fake = FakeMCP()
    register_kc144_v13(fake)
    assert len(fake.tools) == 22
    assert json.loads(fake.tools["kc144_harness_status_v13"]())["maps"] == 72
