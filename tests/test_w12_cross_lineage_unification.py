import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def test_source_mount_and_activation_lineages_coexist():
    mounts = load("MCP/data/w11_source_mounts.json")
    packet = load("deploy/p10/activation-packet.example.json")
    receipt = load(".athena/receipts/w12-cross-lineage-unification.json")
    assert len(mounts["mounts"]) == 2
    assert mounts["control"]["integration_candidate"]["commit"] == (
        "473ea6d4e30f78a7147a9b453382637a244200fe"
    )
    assert packet["state"] == "UNRESOLVED"
    assert packet["authority"]["live_witness_authorized"] is False
    assert receipt["capabilities"]["execute_live_witness_default"] is False
    assert receipt["capabilities"]["witness_plan"] == {
        "sample_count": 3, "interval_seconds": 20, "minimum_span_seconds": 40
    }

def test_no_success_laundering_across_w12_gates():
    receipt = load(".athena/receipts/w12-cross-lineage-unification.json")
    assert receipt["evidence"]["live_provider_return"] == "PASS_LIVE_PROVIDER_RETURN_NO_DRIFT"
    assert receipt["evidence"]["internal_blind_recall"] == (
        "HOLD_COLD_RECALL_EXACT_TUPLES_NOT_RECOVERED"
    )
    assert receipt["authority"]["endpoint_claimed"] is False
    assert receipt["authority"]["deployment_claimed"] is False
    assert receipt["authority"]["promotion_claimed"] is False
