from __future__ import annotations

import json
import tempfile
from pathlib import Path

from . import swarm_board
from .command_spine_adapter import CommandMembraneConfig, CommandMembraneService


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_test_lattice() -> dict[str, object]:
    seats = []
    for index in range(1024):
        seats.append(
            {
                "seat_id": f"SEAT-{index + 1:04d}",
                "activation_state": "ACTIVE",
                "lead_role": ["Synthesizer / Researcher", "Planner / Architect", "Worker / Adventurer", "Pruner / Compressor / Defragmenter"][(index // 256) % 4],
                "macro_mandate": "Command Membrane",
                "resolution_band": "metadata_routing_indexing",
                "coord_tuple": {
                    "Xs": "GLOBAL_COMMAND",
                    "Ys": "ATHENA",
                    "Zs": str(index + 1),
                    "Ts": "C02",
                    "Qs": f"Q{(index % 16) + 1}",
                    "Rs": "D1",
                    "Cs": "C1",
                    "Fs": "COMMAND",
                    "Ms": "M42",
                    "Ns": f"N{(index % 8) + 1}",
                    "Hs": "command-event",
                    "OmegaS": "OMEGA-LOCAL-WITNESS",
                },
            }
        )
    return {"seat_count": 1024, "seats": seats}


def main() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        workspace_root = root / "workspace"
        command_surface = workspace_root / "GLOBAL COMMAND" / "ATHENA"
        command_surface.mkdir(parents=True, exist_ok=True)
        docs_gate = workspace_root / "self_actualize" / "live_docs_gate_status.md"
        docs_gate.parent.mkdir(parents=True, exist_ok=True)
        docs_gate.write_text(
            "# Live Docs Gate Status\n\n- Command status: `BLOCKED`\n- Missing: `Trading Bot/credentials.json`, `Trading Bot/token.json`\n",
            encoding="utf-8",
        )
        shared_lattice = workspace_root / "self_actualize" / "master_loop_shared_lattice_4096.json"
        write_json(shared_lattice, build_test_lattice())
        loop_state = workspace_root / "self_actualize" / "master_loop_state_57.json"
        write_json(loop_state, {"active_loop": {"loop_id": "C02"}})
        agent_state = workspace_root / "self_actualize" / "master_agent_state_57.json"
        write_json(agent_state, {"agents": []})

        original_claim_root = swarm_board.CLAIM_ROOT
        try:
            swarm_board.CLAIM_ROOT = workspace_root / "board_claims"
            config = CommandMembraneConfig(
                workspace_root=workspace_root,
                command_surface_root=command_surface,
                spine_root=workspace_root / "self_actualize" / "command_membrane",
                live_docs_gate_status_path=docs_gate,
                shared_lattice_path=shared_lattice,
                master_agent_state_path=agent_state,
                loop_state_path=loop_state,
            )
            service = CommandMembraneService(config)
            artifacts = service.ensure_protocol_artifacts()
            assert all(Path(path).exists() for path in artifacts.values())

            seeded = service.startup_snapshot_diff()
            assert seeded == []
            assert service.load_state()["known_files"] == {}

            sample = command_surface / "example.md"
            sample.write_text("# test\n", encoding="utf-8")
            routed_packets = service.startup_snapshot_diff(bootstrap_existing=True)
            assert len(routed_packets) == 1
            event_id = routed_packets[0]["event_id"]
            packet = service.load_event(event_id)
            assert packet.witness_class == "LOCAL_WITNESS_ONLY"
            assert packet.state_hash.startswith("H:")

            routed = service.route_event(event_id)
            assert len(routed["selected_targets"]) <= 5

            claim = service.claim_event(event_id)
            assert claim["event_id"] == event_id
            assert service.load_leases()["active"][event_id]["ant_id"] == claim["ant_id"]

            commit = service.commit_event(
                event_id,
                result="success",
                artifact_paths=[packet.source_path],
                writeback_paths=["self_actualize/runtime/command_spine.py"],
                summary="verification commit",
            )
            assert commit["latency"]["t_sugar_ms"] >= 0.0
            assert Path(workspace_root / commit["receipt_json"]).exists()

            reinforced = service.reinforce_event(event_id, latency_score=0.95)
            assert reinforced["edges"]
            metrics = service.metrics(surface="command-folder")
            assert metrics["event_count"] >= 1
            assert metrics["committed_count"] >= 1

            print(
                json.dumps(
                    {
                        "status": "ok",
                        "event_id": event_id,
                        "selected_targets": len(routed["selected_targets"]),
                        "t_sugar_ms": commit["latency"]["t_sugar_ms"],
                        "edge_count": len(reinforced["edges"]),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
        finally:
            swarm_board.CLAIM_ROOT = original_claim_root
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
