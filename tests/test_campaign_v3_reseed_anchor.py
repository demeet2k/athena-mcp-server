from __future__ import annotations

import hashlib
import json
import unittest

from athena_mcp.campaign_v3_ledger import PULSE_ARTIFACT
from athena_mcp.campaign_v3_reseed_anchor import (
    ATHENA_RESEED_SCHEMA_BLOB,
    ATHENA_RESEED_SCRIPT_BLOB,
    ATHENA_RESEED_SOURCE_HEAD,
    SCHEMA_VERSION,
    compile_campaign_v3_reseed_anchor,
    reseed_anchor_digest,
    validate_campaign_v3_reseed_anchor,
)


def _sha(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _pulse(index=1, *, holds=None):
    actions = []
    for step, horizon, state in (
        (1, "I", "SATISFIED"),
        (2, "I", "SUPERSEDED"),
        (3, "I", "RESIDUAL"),
        (4, "I", "RESIDUAL"),
        (5, "M", "RESIDUAL"),
        (6, "M", "RESIDUAL"),
        (7, "M", "RESIDUAL"),
        (8, "L", "RESIDUAL"),
        (9, "L", "RESIDUAL"),
        (10, "L", "RESIDUAL"),
    ):
        actions.append({
            "step": step if index == 1 else (index - 1) * 10 + step,
            "horizon": horizon,
            "text": f"historical action {step if index == 1 else (index - 1) * 10 + step}",
            "current_state": state,
            "history_preserved": True,
        })
    value = {
        "artifact": PULSE_ARTIFACT,
        "ledger_digest": "ledger-digest",
        "source_issue": 177,
        "verification_issue": 185,
        "pulse_index": index,
        "step_start": actions[0]["step"],
        "step_end": actions[-1]["step"],
        "historical_horizon_coverage": {"I": 4, "M": 3, "L": 3},
        "current_status_counts": {},
        "actions": actions,
        "residual_steps": [row["step"] for row in actions if row["current_state"] == "RESIDUAL"],
        "hold_steps": [],
        "current_coordinates": {"git_head": "runtime-head", "shared_fresh": True},
        "operational_basis_status": "PASS",
        "operational_basis_digest": "basis-digest",
        "execution_authorized": False,
        "authority_resolution_required": True,
        "holds": list(holds or []),
        "must_reseed_from_then_current_state": index == 100,
        "mission_complete_claim_allowed": False,
        "laws": ["PULSE_100_RESEED_REQUIRED"],
    }
    value["pulse_digest"] = _sha(value)
    return value


def _positions(runtime_head="runtime-head", athena_head="athena-head"):
    return [
        {
            "repo": "demeet2k/athena-mcp-server",
            "ref": "refs/heads/master",
            "head": runtime_head,
            "tree": "runtime-tree",
        },
        {
            "repo": "demeet2k/Athena",
            "ref": "refs/heads/main",
            "head": athena_head,
            "tree": "athena-tree",
        },
    ]


def _compile(**overrides):
    kwargs = dict(
        pulse=_pulse(),
        campaign_id="RHC-1",
        campaign_state_digest="campaign-state",
        campaign_checkpoint_head="campaign-head",
        loop_id="LOOP-1",
        loop_state_digest="loop-state",
        anchor_id="RA-CV3-1",
        run_id="RUN-1",
        agent_coordinate_name="ATHENA-CV3",
        reseed_epoch=1,
        pulse_age_before=10,
        git_positions=_positions(),
        primary_repo="demeet2k/athena-mcp-server",
        primary_ref="refs/heads/master",
        primary_head_before="runtime-old",
        prompt_digest="prompt-digest",
        issue_pressure_digest="issue-digest",
        durable_returns=["runtime:commit:e487", "athena:issue:189:comment:1"],
        witnesses=["ci:PASS", "readback:PASS"],
        continuation_value_class="CONTINUE_POSITIVE_FRONTIER",
        selected_successor="campaign-v3:pulse:2",
        stop_class="CONTINUE_POSITIVE_FRONTIER",
        reverse_route=["campaign-v3:pulse:1"],
        then_current_rehydrated=True,
    )
    kwargs.update(overrides)
    return compile_campaign_v3_reseed_anchor(**kwargs)


class CampaignV3ReseedAnchorTests(unittest.TestCase):
    def test_positive_anchor_matches_canonical_reseed_shape_and_is_digestible(self):
        anchor = _compile()
        self.assertEqual(anchor["schema_version"], SCHEMA_VERSION)
        self.assertEqual(anchor["pulse_age_after"], 0)
        self.assertFalse(anchor["platform_counter_reset_claimed"])
        self.assertEqual(anchor["continuation_value_class"], "CONTINUE_POSITIVE_FRONTIER")
        self.assertEqual(anchor["selected_successor"], "campaign-v3:pulse:2")
        self.assertEqual(anchor["stop_class"], "CONTINUE_POSITIVE_FRONTIER")
        self.assertEqual(anchor["git"]["head_after"], "runtime-head")
        self.assertTrue(anchor["git"]["changed"])
        self.assertEqual(len(anchor["git_positions"]), 2)
        self.assertIn("step:0001:SATISFIED:historical action 1", anchor["satisfied_work"])
        self.assertIn("step:0002:SUPERSEDED:historical action 2", anchor["satisfied_work"])
        self.assertTrue(any(value.startswith("step:0003:I:") for value in anchor["residuals"]))
        self.assertEqual([], validate_campaign_v3_reseed_anchor(anchor))
        self.assertEqual(64, len(reseed_anchor_digest(anchor)))

    def test_target_versions_bind_campaign_pulse_loop_and_allow_unique_extras(self):
        anchor = _compile(extra_target_versions=[{"id": "athena.reseed_schema_blob", "version": ATHENA_RESEED_SCHEMA_BLOB}])
        versions = {row["id"]: row["version"] for row in anchor["target_versions"]}
        self.assertEqual(versions["campaign_v3.campaign_id"], "RHC-1")
        self.assertEqual(versions["campaign_v3.campaign_state_digest"], "campaign-state")
        self.assertEqual(versions["campaign_v3.pulse_digest"], _pulse()["pulse_digest"])
        self.assertEqual(versions["campaign_v3.loop_state_digest"], "loop-state")
        self.assertEqual(versions["athena.reseed_schema_blob"], ATHENA_RESEED_SCHEMA_BLOB)
        with self.assertRaisesRegex(ValueError, "duplicate target id"):
            _compile(extra_target_versions=[{"id": "campaign_v3.pulse_digest", "version": "other"}])

    def test_pins_exact_canonical_athena_reseed_contract_identity(self):
        self.assertEqual(ATHENA_RESEED_SOURCE_HEAD, "9c369d8c9cbcb7463469bcbbfd93597bffec0275")
        self.assertEqual(ATHENA_RESEED_SCHEMA_BLOB, "6d9f2da5bd900239dcce01d455123675202f3b09")
        self.assertEqual(ATHENA_RESEED_SCRIPT_BLOB, "8eb274cc8d7f966e8778da5677fa0207233ae39b")

    def test_positive_frontier_requires_successor_and_zero_holds(self):
        with self.assertRaisesRegex(ValueError, "explicit successor"):
            _compile(selected_successor=None)
        with self.assertRaisesRegex(ValueError, "holds remain"):
            _compile(pulse=_pulse(holds=["AUTHORITY_HOLD"]))
        with self.assertRaisesRegex(ValueError, "conflicting stop"):
            _compile(stop_class="NO_POSITIVE_FRONTIER")

    def test_nonpositive_frontier_requires_typed_stop_and_no_successor(self):
        anchor = _compile(
            continuation_value_class="NONPOSITIVE",
            selected_successor=None,
            stop_class="NO_POSITIVE_FRONTIER",
        )
        self.assertEqual(anchor["continuation_value_class"], "NONPOSITIVE")
        self.assertIsNone(anchor["selected_successor"])
        self.assertEqual(anchor["stop_class"], "NO_POSITIVE_FRONTIER")
        self.assertEqual([], validate_campaign_v3_reseed_anchor(anchor))
        with self.assertRaisesRegex(ValueError, "cannot emit successor"):
            _compile(
                continuation_value_class="NONPOSITIVE",
                selected_successor="illegal",
                stop_class="NO_POSITIVE_FRONTIER",
            )
        with self.assertRaisesRegex(ValueError, "typed Campaign-compatible stop"):
            _compile(
                continuation_value_class="NONPOSITIVE",
                selected_successor=None,
                stop_class=None,
            )

    def test_bounded_campaign_pulse_cannot_self_certify_success(self):
        with self.assertRaisesRegex(ValueError, "cannot self-certify"):
            _compile(
                continuation_value_class="NONPOSITIVE",
                selected_successor=None,
                stop_class="SUCCESS_CLOSED",
            )

    def test_pulse_100_requires_then_current_rehydration_before_any_anchor(self):
        with self.assertRaisesRegex(ValueError, "then-current rehydration"):
            _compile(pulse=_pulse(100), then_current_rehydrated=False)
        anchor = _compile(
            pulse=_pulse(100),
            then_current_rehydrated=True,
            selected_successor="campaign-v3:reseed:post-1000",
        )
        self.assertEqual(anchor["selected_successor"], "campaign-v3:reseed:post-1000")
        self.assertNotEqual(anchor["stop_class"], "SUCCESS_CLOSED")

    def test_parent_epoch_must_advance_monotonically(self):
        parent = _compile(anchor_id="RA-E1", reseed_epoch=1)
        child = _compile(
            anchor_id="RA-E2",
            reseed_epoch=2,
            parent_anchor=parent,
        )
        self.assertEqual(child["parent_anchor_id"], "RA-E1")
        self.assertEqual(child["parent_reseed_epoch"], 1)
        with self.assertRaisesRegex(ValueError, "advance beyond parent"):
            _compile(reseed_epoch=1, parent_anchor=parent)

    def test_primary_git_coordinate_must_be_ref_scoped_and_changed_flag_is_consistent(self):
        anchor = _compile(primary_head_before="runtime-head")
        self.assertFalse(anchor["git"]["changed"])
        with self.assertRaisesRegex(ValueError, "primary Git coordinate"):
            _compile(primary_repo="missing/repo")
        with self.assertRaisesRegex(ValueError, "duplicate git position"):
            _compile(git_positions=_positions() + [_positions()[0]])

    def test_missing_durable_return_or_witness_fails_before_anchor_creation(self):
        with self.assertRaisesRegex(ValueError, "durable return"):
            _compile(durable_returns=[])
        with self.assertRaisesRegex(ValueError, "readback/witness"):
            _compile(witnesses=[])

    def test_tampered_or_authoritative_pulse_is_rejected(self):
        pulse = _pulse()
        pulse["actions"][0]["text"] = "tampered"
        with self.assertRaisesRegex(ValueError, "tampered"):
            _compile(pulse=pulse)
        pulse = _pulse()
        pulse["execution_authorized"] = True
        pulse.pop("pulse_digest")
        pulse["pulse_digest"] = _sha(pulse)
        with self.assertRaisesRegex(ValueError, "non-authoritative"):
            _compile(pulse=pulse)

    def test_compiler_never_invents_platform_reset_or_private_reasoning_fields(self):
        anchor = _compile()
        encoded = json.dumps(anchor, sort_keys=True)
        self.assertNotIn("private_chain_of_thought", encoded)
        self.assertNotIn("token_reset", encoded)
        self.assertNotIn("context_reset", encoded)
        self.assertFalse(anchor["platform_counter_reset_claimed"])


if __name__ == "__main__":
    unittest.main()
