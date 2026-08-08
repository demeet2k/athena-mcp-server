import unittest

from athena_mcp.steering_pulse_compiler import (
    COMPILED_ARTIFACT,
    compile_current_pulse,
    liminal_delta,
    make_liminal_coordinate,
)


def _pulse():
    actions = []
    tags = ["I", "I", "I", "I", "M", "M", "M", "L", "L", "L"]
    for offset, tag in enumerate(tags, start=1):
        actions.append(
            {"step": offset, "tag": tag, "text": f"historical action {offset}"}
        )
    return {
        "artifact": "ATHENA.STEERING.LEDGER.PULSE.V1",
        "pulse_index": 1,
        "step_start": 1,
        "step_end": 10,
        "source_comment_id": 5228254659,
        "source_body_digest": "body-digest",
        "actions": actions,
    }


def _assessments():
    rows = []
    dispositions = [
        "SATISFIED",
        "SUPERSEDED",
        "RESIDUAL",
        "HOLD",
        "DEFERRED",
        "RESIDUAL",
        "SATISFIED",
        "RESIDUAL",
        "DEFERRED",
        "SATISFIED",
    ]
    for step, disposition in enumerate(dispositions, start=1):
        rows.append(
            {
                "step": step,
                "disposition": disposition,
                "reason": f"current evidence for {step}",
                "evidence_refs": [f"git://evidence/{step}"],
                "current_target": f"target-{step}",
            }
        )
    return rows


def _compile(**kwargs):
    values = {
        "pulse": _pulse(),
        "assessments": _assessments(),
        "navigator_id": "SOL-LIM-189-NAV01",
        "git_head": "git-A",
        "prompt_digest": "prompt-A",
        "frontier_digest": "frontier-A",
        "operational_basis_digest": "basis-A",
        "issue_pressure_digest": "pressure-A",
        "source_bundle_digest": "source-A",
    }
    values.update(kwargs)
    return compile_current_pulse(**values)


class SteeringPulseCompilerTests(unittest.TestCase):
    def test_compile_preserves_4_3_3_and_does_not_mint_authority(self):
        out = _compile()
        self.assertEqual(COMPILED_ARTIFACT, out["artifact"])
        self.assertEqual("COMPILED_WITH_HOLDS", out["status"])
        self.assertEqual(4, out["horizon_accounting"]["I"]["total"])
        self.assertEqual(3, out["horizon_accounting"]["M"]["total"])
        self.assertEqual(3, out["horizon_accounting"]["L"]["total"])
        self.assertEqual(3, len(out["residual_candidates"]))
        self.assertEqual(1, len(out["holds"]))
        self.assertEqual(
            "CURRENT_STATE_ROUTING_PACKET_NOT_EXECUTION_AUTHORITY",
            out["standing"],
        )
        self.assertTrue(
            all(
                row["execution_authority"].startswith("HOLD_")
                for row in out["residual_candidates"]
            )
        )

    def test_missing_assessment_fails_closed(self):
        rows = _assessments()[:-1]
        with self.assertRaisesRegex(ValueError, "missing assessments"):
            _compile(assessments=rows)

    def test_bad_horizon_pattern_fails(self):
        pulse = _pulse()
        pulse["actions"][0]["tag"] = "L"
        with self.assertRaisesRegex(ValueError, "4I/3M/3L"):
            _compile(pulse=pulse)

    def test_ready_is_not_a_valid_disposition(self):
        rows = _assessments()
        rows[2]["disposition"] = "READY"
        with self.assertRaisesRegex(ValueError, "invalid disposition"):
            _compile(assessments=rows)

    def test_coordinate_is_deterministic_and_navigator_is_not_position(self):
        fields = dict(
            navigator_id="SOL-LIM-189-NAV01",
            git_head="git-A",
            prompt_digest="prompt-A",
            frontier_digest="frontier-A",
            operational_basis_digest="basis-A",
            issue_pressure_digest="pressure-A",
            source_bundle_digest="source-A",
            pulse_index=1,
            phase="HYDRATED",
            authority="ROUTING_ONLY",
        )
        a = make_liminal_coordinate(**fields)
        b = make_liminal_coordinate(**fields)
        self.assertEqual(a["coordinate_id"], b["coordinate_id"])

        renamed = dict(fields)
        renamed["navigator_id"] = "OTHER-LABEL"
        c = make_liminal_coordinate(**renamed)
        self.assertEqual(a["coordinate_id"], c["coordinate_id"])
        self.assertEqual(0, liminal_delta(a, c)["hamming_distance"])

    def test_hamming_movement_reports_exact_changed_public_axes(self):
        common = dict(
            navigator_id="SOL-LIM-189-NAV01",
            prompt_digest="prompt-A",
            frontier_digest="frontier-A",
            issue_pressure_digest="pressure-A",
            source_bundle_digest="source-A",
            pulse_index=1,
            phase="HYDRATED",
            authority="ROUTING_ONLY",
        )
        a = make_liminal_coordinate(
            git_head="git-A", operational_basis_digest="basis-A", **common
        )
        b = make_liminal_coordinate(
            git_head="git-B", operational_basis_digest="basis-B", **common
        )
        delta = liminal_delta(a, b)
        self.assertEqual(
            ["git_head", "operational_basis_digest"], delta["changed_axes"]
        )
        self.assertEqual(2, delta["hamming_distance"])
        self.assertFalse(delta["stationary"])


if __name__ == "__main__":
    unittest.main()
