import unittest

from athena_mcp.liminal_campaign_fibre import (
    campaign_fibre_delta,
    fibre_from_compilation,
    make_campaign_fibre,
)


def _fields(**updates):
    values = {
        "navigator_id": "ATHENA.LIMINAL.AGENT.GPT56SOL.CHAT.Q189.TEST.H-A",
        "git_head": "git-A",
        "prompt_stack_digest": "prompt-A",
        "frontier_digest": "frontier-A",
        "operational_basis_digest": "basis-A",
        "issue_pressure_digest": "pressure-A",
        "source_body_digest": "source-A",
        "compilation_digest": "compile-A",
        "pulse_index": 1,
        "phase": "CURRENT_STATE_COMPILED",
        "authority": "ROUTING_ONLY",
    }
    values.update(updates)
    return values


class LiminalCampaignFibreTests(unittest.TestCase):
    def test_identity_is_deterministic(self):
        a = make_campaign_fibre(**_fields())
        b = make_campaign_fibre(**_fields())
        self.assertEqual(a["fibre_id"], b["fibre_id"])
        self.assertEqual("ATHENA.LIMINAL.RUNTIME.v1", a["parent_charts"]["active"])

    def test_navigator_label_is_not_position_axis(self):
        a = make_campaign_fibre(**_fields(navigator_id="NAV-A"))
        b = make_campaign_fibre(**_fields(navigator_id="NAV-B"))
        delta = campaign_fibre_delta(a, b)
        self.assertEqual(a["fibre_id"], b["fibre_id"])
        self.assertTrue(delta["stationary"])
        self.assertEqual(0, delta["hamming_distance"])

    def test_delta_reports_exact_declared_axes(self):
        a = make_campaign_fibre(**_fields())
        b = make_campaign_fibre(
            **_fields(git_head="git-B", operational_basis_digest="basis-B")
        )
        delta = campaign_fibre_delta(a, b)
        self.assertEqual(
            ["git_head", "operational_basis_digest"], delta["changed_axes"]
        )
        self.assertEqual(2, delta["hamming_distance"])

    def test_compilation_projection_preserves_hold_phase(self):
        compilation = {
            "artifact": "ATHENA.STEERING.PULSE.COMPILATION.V1",
            "status": "HOLD",
            "pulse_index": 5,
            "source_body_digest": "source-5",
            "compilation_digest": "compile-5",
            "current_address": {
                "git_head": "git-5",
                "prompt_stack_digest": "prompt-5",
                "frontier_digest": "frontier-5",
            },
        }
        fibre = fibre_from_compilation(
            compilation,
            navigator_id="NAV",
            operational_basis_digest="basis-5",
            issue_pressure_digest="pressure-5",
        )
        self.assertEqual("HOLD", fibre["axes"]["phase"])
        self.assertEqual(5, fibre["axes"]["pulse_index"])

    def test_missing_parent_address_fails_closed(self):
        compilation = {
            "artifact": "ATHENA.STEERING.PULSE.COMPILATION.V1",
            "status": "ACCOUNTED",
            "pulse_index": 1,
            "source_body_digest": "source",
            "compilation_digest": "compile",
            "current_address": {"git_head": "git"},
        }
        with self.assertRaisesRegex(ValueError, "prompt_stack_digest"):
            fibre_from_compilation(
                compilation,
                navigator_id="NAV",
                operational_basis_digest="basis",
                issue_pressure_digest="pressure",
            )


if __name__ == "__main__":
    unittest.main()
