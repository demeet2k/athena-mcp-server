from __future__ import annotations

import unittest

from athena_mcp.shso_readonly import (
    BEHAVIORAL_TREATMENT_EFFECT,
    PUBLIC_RUNTIME_RECONCILIATION_COMMIT,
    benchmark,
    manifest,
    project_organism_pressure,
)


def health(phase: str = "RESPONSIVE", **extra):
    out = {
        "kind": "HEALTH_ADVISORY",
        "diagnostic_phase": phase,
        "criticality_proven": False,
        "phase_is_heuristic": True,
        "behavioral_gain_proven": False,
        "execution_authority_granted": False,
    }
    out.update(extra)
    return out


def ecology(status: str = "CLASSIFIED", **extra):
    out = {
        "kind": "ECOLOGY_ADVISORY",
        "status": status,
        "world_truth_proven": False,
        "morphology_mutation_performed": False,
    }
    out.update(extra)
    return out


def project(*, phase="RESPONSIVE", status="CLASSIFIED", ready=False, previous=(), due=False, mandatory=False):
    return project_organism_pressure(
        health(phase),
        ecology(status),
        ready_build_exists=ready,
        previous_transition_classes=list(previous),
        verification_barrier_due=due,
        verification_barrier_mandatory=mandatory,
    )


class ShsoReadonlyProjectionTests(unittest.TestCase):
    def test_hard_gate_compromise_has_top_precedence(self):
        out = project(
            phase="HARD_GATE_COMPROMISED",
            ready=True,
            previous=("VERIFY", "META"),
            due=True,
            mandatory=True,
        )
        self.assertEqual(out["primary_pressure"], "HOLD_HARD_GATE")
        self.assertTrue(out["builder_starvation_detected"])
        self.assertFalse(out["morphology_action_allowed"])
        self.assertFalse(out["execution_authority_granted"])
        self.assertFalse(out["scheduler_mutation_performed"])

    def test_mandatory_verification_precedes_builder_starvation(self):
        out = project(
            ready=True,
            previous=("VERIFY", "CONTROL"),
            due=True,
            mandatory=True,
        )
        self.assertEqual(out["primary_pressure"], "VERIFY_MANDATORY_BARRIER_ADVISORY")
        self.assertTrue(out["builder_starvation_detected"])

    def test_builder_starvation_precedes_batch_verification(self):
        out = project(
            ready=True,
            previous=("VERIFY", "SELF_PLAY"),
            due=True,
            mandatory=False,
        )
        self.assertEqual(out["primary_pressure"], "BUILD_PIVOT_ADVISORY")

    def test_batch_verification_when_due_without_starvation(self):
        out = project(due=True)
        self.assertEqual(out["primary_pressure"], "VERIFY_BATCH_ADVISORY")

    def test_health_phase_translations(self):
        expected = {
            "HERDED": "PRESERVE_NEUTRAL_SCOUT",
            "BRITTLE": "PRESERVE_RESERVE_ADVISORY",
            "FRAGMENTED": "BRIDGE_LOCAL_GUILDS_ADVISORY",
            "SATURATED": "REDUCE_COORDINATION_ADVISORY",
            "RECOVERING": "RECOVERY_RESERVE_ADVISORY",
        }
        for phase, pressure in expected.items():
            with self.subTest(phase=phase):
                out = project(phase=phase)
                self.assertEqual(out["primary_pressure"], pressure)
                self.assertIn(pressure, out["secondary_pressures"])
                self.assertFalse(out["worker_dispatched"])

    def test_ready_build_continues_without_dispatch(self):
        out = project(ready=True, previous=("BUILD",))
        self.assertEqual(out["primary_pressure"], "BUILD_CONTINUE_ADVISORY")
        self.assertFalse(out["dispatch_authority_granted"])
        self.assertFalse(out["prompt_candidate_activated"])

    def test_no_specific_pressure(self):
        out = project()
        self.assertEqual(out["primary_pressure"], "NO_ORGANISM_ACTION")
        self.assertEqual(out["behavioral_treatment_effect"], "UNKNOWN")

    def test_unknown_or_ambiguous_ecology_blocks_morphology_action(self):
        for status in (
            "AMBIGUOUS",
            "UNKNOWN_INSUFFICIENT_COVERAGE",
            "UNKNOWN_LOW_SIGNAL",
        ):
            with self.subTest(status=status):
                out = project(phase="HERDED", status=status)
                self.assertFalse(out["morphology_action_allowed"])
                self.assertIn("ecology_uncertain_no_morphology_action", out["reasons"])

    def test_classified_ecology_only_marks_action_allowed_not_performed(self):
        out = project(status="CLASSIFIED")
        self.assertTrue(out["morphology_action_allowed"])
        self.assertFalse(out["morphology_mutation_performed"])

    def test_only_last_two_transition_classes_drive_starvation(self):
        out = project(ready=True, previous=("BUILD", "VERIFY", "META"))
        self.assertTrue(out["builder_starvation_detected"])
        self.assertEqual(out["previous_transition_classes"], ["VERIFY", "META"])

    def test_bad_health_standing_fails_closed(self):
        with self.assertRaises(ValueError):
            project_organism_pressure(
                health("HERDED", criticality_proven=True),
                ecology(),
                ready_build_exists=False,
                previous_transition_classes=[],
                verification_barrier_due=False,
                verification_barrier_mandatory=False,
            )

    def test_bad_ecology_truth_claim_fails_closed(self):
        with self.assertRaises(ValueError):
            project_organism_pressure(
                health(),
                ecology(world_truth_proven=True),
                ready_build_exists=False,
                previous_transition_classes=[],
                verification_barrier_due=False,
                verification_barrier_mandatory=False,
            )

    def test_private_reasoning_key_fails_closed(self):
        packet = health()
        packet["scratchpad"] = "hidden"
        with self.assertRaises(ValueError):
            project_organism_pressure(
                packet,
                ecology(),
                ready_build_exists=False,
                previous_transition_classes=[],
                verification_barrier_due=False,
                verification_barrier_mandatory=False,
            )

    def test_authority_assertion_key_fails_closed(self):
        packet = ecology()
        packet["execution_authority"] = True
        with self.assertRaises(ValueError):
            project_organism_pressure(
                health(),
                packet,
                ready_build_exists=False,
                previous_transition_classes=[],
                verification_barrier_due=False,
                verification_barrier_mandatory=False,
            )

    def test_manifest_preserves_semantic_runtime_and_behavioral_separation(self):
        value = manifest()
        self.assertEqual(value["private_semantic_contract"], "ATHENA.SHSO.READONLY.BRIDGE.V1")
        self.assertEqual(value["public_runtime_base_head"], "2ca4b01c2a8591bc7159ae1c941e7d80fa007343")
        self.assertEqual(value["public_runtime_reconciliation_commit"], PUBLIC_RUNTIME_RECONCILIATION_COMMIT)
        self.assertEqual(PUBLIC_RUNTIME_RECONCILIATION_COMMIT, "80bda63556da7158f93874eee724fda38313e7e1")
        self.assertFalse(value["ports_full_private_shso_reducers"])
        self.assertEqual(value["behavioral_treatment_effect"], "UNKNOWN")
        self.assertFalse(value["behavioral_gain_proven"])

    def test_contract_benchmark_passes_without_claiming_behavioral_gain(self):
        value = benchmark()
        self.assertTrue(value)
        self.assertTrue(all(value.values()))
        self.assertEqual(BEHAVIORAL_TREATMENT_EFFECT, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
