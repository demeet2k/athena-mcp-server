from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATHENA_PACKAGE_ROOT = ROOT / "ATHENA Neural Network"
if str(ATHENA_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(ATHENA_PACKAGE_ROOT))

from athena_neural_network import AthenaNeuralNetwork, aug_geometric, draw_digit, generate_data  # noqa: E402
from athenachka import AthenachkaOrganismV0  # noqa: E402
from athenachka.immune.truth_lattice import classify_truth  # noqa: E402
from athenachka.runtime.questing import build_macro_quest_bundle  # noqa: E402


def main() -> int:
    X_train, Y_train = generate_data(40, aug_geometric, 42)
    model = AthenaNeuralNetwork()
    model.train(X_train, Y_train, epochs=1, lr=0.03, batch_size=16, verbose=False)

    organism = AthenachkaOrganismV0(kernel=model)
    img = draw_digit(8)

    fast = organism.forward(img, mode="fast")
    full = organism.forward(img, mode="full")
    bundle = build_macro_quest_bundle()

    mock_trace = {"legacy_confidence": 0.74, "legacy_probs": [0.4, 0.35, 0.25]}
    ambiguity = classify_truth(
        trace=mock_trace,
        contradictions={"flags": ["multi_hypothesis_class_conflict"]},
        witness_bundle={"strength": 0.8},
        corridor_profile={"ambiguity_margin": 0.12, "near_confidence": 0.7, "ok_confidence": 0.9},
        self_contract={"legal": True},
    )

    report = {
        "fast_truth": fast.truth_type,
        "full_truth": full.truth_type,
        "fast_elemental_keys": sorted(fast.elemental_state.keys()),
        "fast_pairwise_count": len(fast.symmetry_state["active_fusions"]),
        "full_pairwise_count": len(full.symmetry_state["active_fusions"]),
        "fast_loop_count": len(fast.lineage_delta["active_loops"]),
        "full_loop_count": len(full.lineage_delta["active_loops"]),
        "full_seed_present": "lift_seed" in organism.last_state.replay,
        "fast_born_coordinates": len(fast.born_coordinates),
        "full_born_coordinates": len(full.born_coordinates),
        "quest_macro": bundle["macro_quest"]["quest_id"],
        "quest_packet_count": len(bundle["packets"]),
        "current_wave_id": bundle["current_wave_id"],
        "available_waves": sorted(bundle["wave_specs"].keys()),
        "active_packet_count": len(bundle["active_packets"]),
        "parked_packet_count": len(bundle["parked_packets"]),
        "first_active_packet_id": bundle["active_packets"][0]["quest_id"],
        "last_active_packet_id": bundle["active_packets"][-1]["quest_id"],
        "wave_assignment_count": len(bundle["wave_activation"]["assignments"]),
        "guildmaster_active_claims": bundle["wave_activation"]["owner_summary"]["guildmaster"]["active_claims"],
        "elemental_owner_claims": bundle["wave_activation"]["owner_summary"]["elemental_pod_leads"]["active_claims"],
        "controller_owner_claims": bundle["wave_activation"]["owner_summary"]["controller_auditors"]["active_claims"],
        "verification_owner_claims": bundle["wave_activation"]["owner_summary"]["verification_replay_stewards"]["active_claims"],
        "appendix_owner_claims": bundle["wave_activation"]["owner_summary"]["appendix_service_stewards"]["active_claims"],
        "ambiguity_gate": ambiguity,
    }

    assert report["fast_elemental_keys"] == ["air", "earth", "fire", "water"]
    assert report["fast_pairwise_count"] <= 3
    assert report["full_pairwise_count"] <= 6
    assert report["fast_loop_count"] <= 4
    assert report["full_loop_count"] <= 8
    assert len(fast.born_coordinates) == 0
    assert report["full_seed_present"] is True
    assert bundle["macro_quest"]["quest_id"] == "Q43"
    assert report["current_wave_id"] == "Q50-wave7"
    assert report["available_waves"] == [
        "Q44-wave1",
        "Q45-wave2",
        "Q46-wave3",
        "Q47-wave4",
        "Q48-wave5",
        "Q49-wave6",
        "Q50-wave7",
    ]
    assert report["active_packet_count"] == 16
    assert report["parked_packet_count"] == 64
    assert report["first_active_packet_id"] == "Q43-145"
    assert report["last_active_packet_id"] == "Q43-160"
    assert report["wave_assignment_count"] == 16
    assert report["guildmaster_active_claims"] == 0
    assert report["elemental_owner_claims"] == 4
    assert report["controller_owner_claims"] == 4
    assert report["verification_owner_claims"] == 4
    assert report["appendix_owner_claims"] == 4
    assert report["ambiguity_gate"] != "OK"

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
