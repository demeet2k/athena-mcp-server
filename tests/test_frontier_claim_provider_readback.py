from __future__ import annotations

import base64
import io
import json
import unittest
from urllib import error

from athena_mcp.frontier_claim import FrontierClaimRuntime, _provider_packet
from athena_mcp.frontier_claim_provider import GitHubContentsCreateProvider
from athena_mcp.frontier_claim_provider_guard import install_frontier_claim_provider_guard
from athena_mcp.frontier_claim_provider_readback import install_frontier_claim_provider_readback


class DummyRuntime:
    def __init__(self):
        self.environ = {"GITHUB_TOKEN": "readback-secret"}


class Response:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def claim_packet(*, authority="HOLD", extra=False):
    content = {
        "schema_version": "CLAIM_V1",
        "run_id": "run.test",
        "node_id": "claim",
        "worker_role": "verifier",
        "attempt": 1,
        "policy_commit": "a" * 40,
        "claimed_at": "2026-08-08T21:10:00Z",
        "lease_expires_at": "2026-08-08T21:20:00Z",
        "input_snapshot_digest": "b" * 64,
        "production_authority": authority,
    }
    if extra:
        content["unexpected"] = "no"
    return _provider_packet(
        "runtime/runs/run.test/claims/claim.json",
        content,
        kind="CLAIM_V1",
    )


def existing_payload(content_text, sha="blob-existing"):
    return {
        "sha": sha,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
    }


class FrontierClaimProviderReadbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # The guard must precede readback so HTTP-200 update-like semantics remain
        # a hard HOLD rather than being laundered by an identical GET response.
        install_frontier_claim_provider_guard(FrontierClaimRuntime)
        install_frontier_claim_provider_readback(FrontierClaimRuntime)

    def provider(self, opener):
        return GitHubContentsCreateProvider(DummyRuntime(), opener=opener)

    def test_422_identical_readback_is_observed_effect_not_new_create(self):
        packet = claim_packet()
        calls = []

        def opener(req, timeout=20):
            calls.append(req.get_method())
            if req.get_method() == "PUT":
                raise error.HTTPError(req.full_url, 422, "exists", {}, io.BytesIO(b"{}"))
            return Response(existing_payload(packet["content_text"]), status=200)

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=packet,
        )
        self.assertEqual(result["status"], "CREATED")
        self.assertEqual(result["provider_effect_standing"], "CREATE_EFFECT_OBSERVED")
        self.assertFalse(result["provider_effect_newly_created"])
        self.assertEqual(calls, ["PUT", "GET"])
        self.assertNotIn("readback-secret", json.dumps(result, sort_keys=True))

    def test_422_different_readback_remains_collision(self):
        packet = claim_packet()

        def opener(req, timeout=20):
            if req.get_method() == "PUT":
                raise error.HTTPError(req.full_url, 422, "exists", {}, io.BytesIO(b"{}"))
            return Response(existing_payload("different\n"), status=200)

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=packet,
        )
        self.assertEqual(result["status"], "EXISTS")
        self.assertEqual(result["provider_effect_standing"], "CREATE_COLLISION")
        self.assertFalse(result["provider_effect_newly_created"])

    def test_timeout_identical_readback_resolves_without_blind_retry(self):
        packet = claim_packet()
        calls = []

        def opener(req, timeout=20):
            calls.append(req.get_method())
            if req.get_method() == "PUT":
                raise TimeoutError("provider timeout")
            return Response(existing_payload(packet["content_text"]), status=200)

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=packet,
        )
        self.assertEqual(result["status"], "CREATED")
        self.assertEqual(result["provider_effect_standing"], "CREATE_EFFECT_OBSERVED")
        self.assertFalse(result["provider_effect_newly_created"])
        self.assertEqual(calls, ["PUT", "GET"])

    def test_timeout_then_absent_is_ambiguous_hold(self):
        packet = claim_packet()

        def opener(req, timeout=20):
            if req.get_method() == "PUT":
                raise TimeoutError("provider timeout")
            raise error.HTTPError(req.full_url, 404, "absent", {}, io.BytesIO(b"{}"))

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=packet,
        )
        self.assertEqual(result["status"], "PROVIDER_HOLD")
        self.assertEqual(result["provider_effect_standing"], "AMBIGUOUS_CREATE_HOLD")
        self.assertIn("SAFE_TO_BLINDLY_RETRY", result["law"])

    def test_exact_claim_key_set_is_required_before_network(self):
        called = {"value": False}

        def opener(req, timeout=20):
            called["value"] = True
            raise AssertionError("network must not run")

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=claim_packet(extra=True),
        )
        self.assertEqual(result["status"], "PROVIDER_PACKET_REJECTED")
        self.assertIn("keys mismatch", result["reason"])
        self.assertFalse(called["value"])

    def test_initial_claim_authority_must_remain_hold(self):
        called = {"value": False}

        def opener(req, timeout=20):
            called["value"] = True
            raise AssertionError("network must not run")

        result = self.provider(opener).create(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            packet=claim_packet(authority="PRODUCTION"),
        )
        self.assertEqual(result["status"], "PROVIDER_PACKET_REJECTED")
        self.assertIn("HOLD authority only", result["reason"])
        self.assertFalse(called["value"])


if __name__ == "__main__":
    unittest.main()
