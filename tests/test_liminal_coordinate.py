from __future__ import annotations

import unittest

from athena_mcp.liminal_coordinate import (
    COORDINATE_ARTIFACT,
    NOT_APPLICABLE,
    UNKNOWN,
    liminal_delta,
    make_liminal_coordinate,
    trace_liminal_path,
)


def _coordinate(**updates):
    value = {
        "navigator_id": "SOL-LIM-189-NAV01",
        "repository": "demeet2k/Athena",
        "git_head": "c0065074e5ba2f7d0dcc92b0ba9aa202aa769a54",
        "prompt_digest": UNKNOWN,
        "frontier_digest": UNKNOWN,
        "operational_basis_digest": UNKNOWN,
        "issue_pressure_digest": UNKNOWN,
        "source_bundle_digest": NOT_APPLICABLE,
        "pulse_index": NOT_APPLICABLE,
        "phase": "HYDRATED",
        "authority": "READ_ONLY",
        "observed_at": "2026-08-08T21:55:52Z",
        "observation_refs": ["git:c0065074"],
    }
    value.update(updates)
    return make_liminal_coordinate(**value)


class LiminalCoordinateV2Tests(unittest.TestCase):
    def test_coordinate_identity_is_deterministic_and_metadata_invariant(self):
        a = _coordinate()
        b = _coordinate(
            navigator_id="RENAMED-NAVIGATOR",
            observed_at="2099-01-01T00:00:00Z",
            observation_refs=["different:receipt"],
        )
        self.assertEqual(a["artifact"], COORDINATE_ARTIFACT)
        self.assertEqual(a["coordinate_id"], b["coordinate_id"])
        self.assertEqual(liminal_delta(a, b)["hamming_distance"], 0)

    def test_repository_namespace_is_position_bearing(self):
        a = _coordinate()
        b = _coordinate(repository="demeet2k/athena-mcp-server")
        delta = liminal_delta(a, b)
        self.assertEqual(delta["changed_axes"], ["repository"])
        self.assertEqual(delta["hamming_distance"], 1)

    def test_exact_axis_delta_vector_and_before_after_are_replayable(self):
        a = _coordinate()
        b = _coordinate(
            repository="demeet2k/athena-mcp-server",
            git_head="f87c9d9841eddd1fcff0afdc50c07f10b9ae957c",
            source_bundle_digest=UNKNOWN,
            phase="VERIFIED",
            authority="GIT_BRANCH_WRITE",
        )
        delta = liminal_delta(a, b)
        self.assertEqual(
            delta["changed_axes"],
            ["repository", "git_head", "source_bundle_digest", "phase", "authority"],
        )
        self.assertEqual(delta["hamming_distance"], 5)
        self.assertEqual(delta["delta_vector"]["repository"], 1)
        self.assertEqual(delta["delta_vector"]["frontier_digest"], 0)
        by_axis = {row["axis"]: row for row in delta["axis_deltas"]}
        self.assertEqual(by_axis["repository"]["before"], "demeet2k/Athena")
        self.assertEqual(by_axis["repository"]["after"], "demeet2k/athena-mcp-server")

    def test_unknown_and_not_applicable_are_distinct_positions(self):
        a = _coordinate(pulse_index=UNKNOWN)
        b = _coordinate(pulse_index=NOT_APPLICABLE)
        delta = liminal_delta(a, b)
        self.assertEqual(delta["changed_axes"], ["pulse_index"])
        self.assertEqual(delta["hamming_distance"], 1)

    def test_zero_pulse_is_rejected_instead_of_used_as_missing_sentinel(self):
        with self.assertRaisesRegex(ValueError, "use UNKNOWN or N/A instead of 0"):
            _coordinate(pulse_index=0)

    def test_valid_campaign_pulse_range_is_accepted(self):
        for index in (1, 100):
            coordinate = _coordinate(pulse_index=index)
            self.assertEqual(coordinate["axes"]["pulse_index"], index)

    def test_empty_axis_fails_closed_and_names_explicit_missingness(self):
        with self.assertRaisesRegex(ValueError, "use UNKNOWN or N/A explicitly"):
            _coordinate(frontier_digest="")

    def test_trace_sums_segment_distance_and_reports_net_delta(self):
        a = _coordinate()
        b = _coordinate(phase="PRESSURE_RESOLVED")
        c = _coordinate(
            repository="demeet2k/athena-mcp-server",
            git_head="f87c9d9841eddd1fcff0afdc50c07f10b9ae957c",
            phase="VERIFIED",
        )
        trace = trace_liminal_path([a, b, c])
        self.assertEqual(trace["segment_count"], 2)
        self.assertEqual(trace["total_hamming_distance"], 4)
        self.assertEqual(trace["net_delta"]["hamming_distance"], 3)

    def test_singleton_trace_is_stationary(self):
        a = _coordinate()
        trace = trace_liminal_path([a])
        self.assertEqual(trace["segment_count"], 0)
        self.assertEqual(trace["total_hamming_distance"], 0)
        self.assertTrue(trace["net_delta"]["stationary"])


if __name__ == "__main__":
    unittest.main()
