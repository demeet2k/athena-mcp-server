from __future__ import annotations

import unittest

from athena_mcp.rehydration_promotion_observation import (
    REHYDRATION_PROMOTION_OBSERVATION_TOOL_NAMES,
    RehydrationPromotionObserver,
)


HEAD = "a" * 40
WORK = "b" * 40
CHECKPOINT = "c" * 40


class _Git:
    enabled = True
    def head(self):
        return HEAD


class _Loop:
    def _read_state(self, loop_id):
        return ({
            "loop_id": loop_id,
            "status": "ACTIVE",
            "step_index": 1,
            "state_digest": "state-1",
            "chain_digest": "chain-1",
            "receipt_paths": [f"prompts/rehydration/{loop_id}/receipts/0001.json"],
        }, {"state": f"prompts/rehydration/{loop_id}/state.json"})

    def _path_last_commit(self, rel):
        return CHECKPOINT

    def _read_json(self, rel):
        return {
            "work_head": WORK,
            "receipt_digest": "receipt-1",
            "completion": {
                "successor_baton": {"artifact": "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1", "status": "SELECTED"},
                "_rehydration_control": {
                    "cycle_gate": {
                        "state": "VERIFIED_CYCLE",
                        "promotion_qualified": False,
                        "authority": "LOCAL_CYCLE_ONLY",
                    }
                },
            },
        }

    def verify(self, loop_id, **kwargs):
        return {"status": "PASS", "loop_id": loop_id, "chain_digest": "chain-1"}


class _Store:
    def __init__(self, rows):
        self._rows = list(rows)
    def rows(self, sql, params):
        head, limit = params
        return [row for row in self._rows if row.get("git_head") == head][:limit]


class _Promotion:
    def __init__(self, rows):
        self.s = _Store(rows)
        self._rows = {row["run_id"]: row for row in rows}
        self.evaluate_called = False
    def replay(self, run_id):
        row = self._rows[run_id]
        return {"run_id": run_id, "status": "REPLAY_MATCH", "match": row.get("replay_match", True), "git_head": row["git_head"]}
    def evaluate(self, *args, **kwargs):
        self.evaluate_called = True
        raise AssertionError("observer must never evaluate promotion")


class _Verifier:
    def __init__(self, verified=True, status=None):
        self.verified = verified
        self.status = status or ("VERIFIED" if verified else "NO_QUALIFYING_CHECK_SUITE")
        self.calls = []
    def verify(self, head, timeout_s=12.0):
        self.calls.append((head, timeout_s))
        return {
            "version": "ATHENA.GITHUB.PROMOTION.VERIFIER.1",
            "status": self.status,
            "verified": self.verified,
            "head_sha": head,
            "verification_ref": "github-check-suite://example/1" if self.verified else None,
        }


def _observer(rows=(), verifier=None):
    promotion = _Promotion(rows)
    return RehydrationPromotionObserver(
        git=_Git(), loop=_Loop(), promotion=promotion, verifier=verifier or _Verifier()
    ), promotion


class RehydrationPromotionObservationTests(unittest.TestCase):
    def test_qualified_persisted_run_is_observed_without_evaluation(self):
        observer, promotion = _observer([{
            "run_id": "PROMRUN.qualified",
            "candidate_server": "Server",
            "git_head": HEAD,
            "status": "QUALIFIED",
            "decision_digest": "d1",
            "eid": "e1",
            "created_at": 2.0,
        }])
        value = observer.observe(loop_id="RHL-test")
        self.assertEqual(value["status"], "PERSISTED_QUALIFIED_OBSERVED")
        self.assertEqual(value["persisted_promotion"]["standing"]["status"], "QUALIFIED")
        self.assertFalse(value["authority"]["may_evaluate_promotion"])
        self.assertFalse(value["authority"]["may_merge"])
        self.assertFalse(promotion.evaluate_called)

    def test_verified_checks_do_not_mint_qualification(self):
        observer, promotion = _observer([])
        value = observer.observe(loop_id="RHL-test")
        self.assertEqual(value["status"], "CHECKS_VERIFIED_PROMOTION_UNQUALIFIED")
        self.assertEqual(value["persisted_promotion"]["standing"]["status"], "UNOBSERVED")
        self.assertTrue(value["external_checks"]["verified"])
        self.assertFalse(promotion.evaluate_called)

    def test_conflicting_persisted_statuses_remain_contested(self):
        rows = [
            {"run_id": "PROMRUN.new", "candidate_server": "Server", "git_head": HEAD, "status": "BLOCKED", "decision_digest": "d2", "eid": "e2", "created_at": 2.0},
            {"run_id": "PROMRUN.old", "candidate_server": "Server", "git_head": HEAD, "status": "QUALIFIED", "decision_digest": "d1", "eid": "e1", "created_at": 1.0},
        ]
        observer, _ = _observer(rows)
        value = observer.observe(loop_id="RHL-test", check_external=False)
        self.assertEqual(value["status"], "PROMOTION_CONTESTED")
        self.assertEqual(value["persisted_promotion"]["standing"]["valid_statuses"], ["BLOCKED", "QUALIFIED"])
        self.assertTrue(value["persisted_promotion"]["standing"]["contested"])

    def test_target_modes_are_explicit(self):
        observer, _ = _observer([])
        cycle = observer.observe(loop_id="RHL-test", target_head_mode="CYCLE_WORK", check_external=False)
        self.assertEqual(cycle["promotion_target"]["head"], WORK)
        checkpoint = observer.observe(loop_id="RHL-test", target_head_mode="LOOP_CHECKPOINT", check_external=False)
        self.assertEqual(checkpoint["promotion_target"]["head"], CHECKPOINT)
        explicit = observer.observe(loop_id="RHL-test", target_head_mode="EXPLICIT", explicit_head="d" * 40, check_external=False)
        self.assertEqual(explicit["promotion_target"]["head"], "d" * 40)

    def test_cycle_gate_and_routing_baton_are_observed_but_not_promoted(self):
        observer, _ = _observer([])
        value = observer.observe(loop_id="RHL-test", check_external=False)
        self.assertEqual(value["loop"]["cycle_gate"]["state"], "VERIFIED_CYCLE")
        self.assertFalse(value["loop"]["cycle_gate"]["promotion_qualified"])
        self.assertEqual(value["loop"]["routing_successor"]["artifact"], "ATHENA.REHYDRATION.SUCCESSOR.BATON.V1")
        self.assertEqual(value["authority"]["mode"], "OBSERVATION_ONLY")

    def test_replay_divergence_blocks_persisted_standing(self):
        observer, _ = _observer([{
            "run_id": "PROMRUN.bad",
            "candidate_server": "Server",
            "git_head": HEAD,
            "status": "QUALIFIED",
            "decision_digest": "d1",
            "eid": "e1",
            "created_at": 1.0,
            "replay_match": False,
        }], verifier=_Verifier(False))
        value = observer.observe(loop_id="RHL-test")
        self.assertEqual(value["status"], "PROMOTION_REPLAY_HOLD")
        self.assertEqual(value["persisted_promotion"]["standing"]["status"], "REPLAY_HOLD")

    def test_tool_surface_is_single_read_only_observer(self):
        self.assertEqual(REHYDRATION_PROMOTION_OBSERVATION_TOOL_NAMES, {"athena_rehydration_promotion_observe"})


if __name__ == "__main__":
    unittest.main()
