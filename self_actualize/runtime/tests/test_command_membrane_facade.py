from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from self_actualize.runtime import command_membrane as cm
from self_actualize.runtime import swarm_board
from self_actualize.runtime.command_spine_adapter import CommandMembraneConfig


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_test_lattice() -> dict[str, object]:
    seats = []
    roles = [
        "Synthesizer / Researcher",
        "Planner / Architect",
        "Worker / Adventurer",
        "Pruner / Compressor / Defragmenter",
    ]
    for index in range(1024):
        seats.append(
            {
                "seat_id": f"SEAT-{index + 1:04d}",
                "activation_state": "ACTIVE",
                "lead_role": roles[(index // 256) % 4],
                "macro_mandate": "Command Membrane",
                "resolution_band": "metadata_routing_indexing",
                "coord_tuple": {
                    "Xs": "GLOBAL_COMMAND",
                    "Ys": "ATHENA",
                    "Zs": str(index + 1),
                    "Ts": "L01",
                    "Qs": f"Q{(index % 16) + 1}",
                    "Rs": "ROUTE",
                    "Cs": "OPEN",
                    "Fs": "COMMAND",
                    "Ms": "M42",
                    "Ns": f"N{(index % 8) + 1}",
                    "Hs": "command-event",
                    "OmegaS": "OMEGA-LOCAL-WITNESS",
                },
            }
        )
    return {"seat_count": 1024, "seats": seats}


class CommandMembraneFacadeTests(unittest.TestCase):
    def make_service(self):
        tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(tempdir.cleanup)
        workspace_root = Path(tempdir.name) / "workspace"
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
        write_json(loop_state, {"active_loop": {"loop_id": "L02"}})
        agent_state = workspace_root / "self_actualize" / "master_agent_state_57.json"
        write_json(agent_state, {"agents": []})

        original_claim_root = swarm_board.CLAIM_ROOT
        self.addCleanup(setattr, swarm_board, "CLAIM_ROOT", original_claim_root)
        swarm_board.CLAIM_ROOT = workspace_root / "board_claims"

        config = CommandMembraneConfig(
            workspace_root=workspace_root,
            command_surface_root=workspace_root / "GLOBAL COMMAND",
            spine_root=workspace_root / "self_actualize" / "command_membrane",
            live_docs_gate_status_path=docs_gate,
            shared_lattice_path=shared_lattice,
            master_agent_state_path=agent_state,
            loop_state_path=loop_state,
        )
        original_default = cm.DEFAULT_CONFIG
        self.addCleanup(setattr, cm, "DEFAULT_CONFIG", original_default)
        cm.DEFAULT_CONFIG = config
        service = cm.make_service()
        return service

    def test_facade_exposes_event_route_claim_commit_and_reinforce(self) -> None:
        service = self.make_service()
        cm.build()

        target = service.config.command_surface_root / "ATHENA" / "protocol.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("alpha\n", encoding="utf-8")

        change = cm.build_change_record(target, "created")
        packet, detect_ms, encode_ms = cm.build_event_packet(change=change)
        self.assertEqual(packet.docs_gate_status, "BLOCKED")
        self.assertEqual(packet.canonical_addr_6d, "A1.B1.C1.D1.E1.F1")
        self.assertTrue({"earth", "astro", "runtime", "liminal", "coord12_labels"}.issubset(set(packet.coord12_frame)))
        self.assertGreaterEqual(detect_ms, 0.0)
        self.assertGreaterEqual(encode_ms, 0.0)

        candidates, route_ms = cm.rank_worker_candidates(packet)
        self.assertTrue(candidates)
        self.assertLessEqual(len(candidates), 5)
        self.assertIn("score", candidates[0])
        self.assertGreaterEqual(route_ms, 0.0)

        claim_payload = cm.claim(packet.event_id)
        self.assertEqual(claim_payload["event_id"], packet.event_id)

        commit_payload = cm.commit(
            packet.event_id,
            result="success",
            summary="facade commit",
            artifact_paths=[packet.source_path],
            writeback_paths=["self_actualize/runtime/command_membrane.py"],
        )
        self.assertIn("latency", commit_payload)
        self.assertGreaterEqual(commit_payload["latency"]["t_sugar_ms"], 0.0)

        reinforce_payload = cm.reinforce(packet.event_id, latency_score=0.95)
        self.assertTrue(reinforce_payload["edges"])
        self.assertTrue(
            any(edge.get("grade") in {"route", "capillary", "vein"} or edge.get("classification") in {"route", "capillary", "vein"} for edge in reinforce_payload["edges"])
        )


if __name__ == "__main__":
    unittest.main()
