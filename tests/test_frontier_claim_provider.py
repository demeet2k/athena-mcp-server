from __future__ import annotations

import base64
import io
import json
import unittest
from urllib import error

from athena_mcp.frontier_claim_provider import (
    GitHubContentsCreateProvider,
    validate_provider_descriptor,
)


def claim_descriptor():
    content = {
        "schema_version": "CLAIM_V1",
        "run_id": "run.test",
        "node_id": "build",
        "worker_role": "builder",
        "attempt": 1,
        "policy_commit": "a" * 40,
        "claimed_at": "2026-08-08T20:40:00Z",
        "lease_expires_at": "2026-08-08T20:50:00Z",
        "input_snapshot_digest": "b" * 64,
        "production_authority": "HOLD",
    }
    return {
        "provider_operation": "CREATE_FILE_IF_ABSENT",
        "kind": "CLAIM_V1",
        "path": "runtime/runs/run.test/claims/build.json",
        "content": content,
        "content_text": json.dumps(content, sort_keys=True, indent=2) + "\n",
    }


def event_descriptor():
    content = {
        "schema_version": "EVENT_V1",
        "event_id": "node-ready-abc",
        "sequence": 3,
        "run_id": "run.test",
        "event_type": "NODE_READY",
        "at": "2026-08-08T20:40:00Z",
        "node_id": "build",
        "data": {},
    }
    return {
        "provider_operation": "CREATE_FILE_IF_ABSENT",
        "kind": "EVENT_V1",
        "path": "runtime/runs/run.test/events/00000003.json",
        "content": content,
        "content_text": json.dumps(content, sort_keys=True, indent=2) + "\n",
    }


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


def existing_payload(content_text, sha="blob-existing"):
    return {
        "sha": sha,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
    }


class FrontierClaimProviderTests(unittest.TestCase):
    def provider(self, opener):
        return GitHubContentsCreateProvider(
            repo="demeet2k/Athena",
            branch="agent/sched-v3-event-journal-v1",
            token="secret-provider-token",
            opener=opener,
        )

    def test_success_is_create_only_and_never_sends_update_sha(self):
        seen = []

        def opener(req, timeout=20):
            seen.append(req)
            self.assertEqual(req.get_method(), "PUT")
            body = json.loads(req.data.decode("utf-8"))
            self.assertNotIn("sha", body)
            self.assertEqual(body["branch"], "agent/sched-v3-event-journal-v1")
            decoded = base64.b64decode(body["content"]).decode("utf-8")
            self.assertEqual(decoded, claim_descriptor()["content_text"])
            self.assertEqual(req.get_header("Authorization"), "Bearer secret-provider-token")
            return Response({"content": {"sha": "blob-new"}, "commit": {"sha": "commit-new"}}, status=201)

        result = self.provider(opener).create_if_absent(claim_descriptor())
        self.assertEqual(result["status"], "CREATED")
        self.assertEqual(result["provider"]["content_sha"], "blob-new")
        self.assertEqual(result["provider"]["commit_sha"], "commit-new")
        self.assertNotIn("secret-provider-token", json.dumps(result, sort_keys=True))
        self.assertEqual(len(seen), 1)

    def test_422_with_identical_existing_content_is_idempotent_observation(self):
        calls = []
        descriptor = claim_descriptor()

        def opener(req, timeout=20):
            calls.append(req.get_method())
            if req.get_method() == "PUT":
                raise error.HTTPError(req.full_url, 422, "exists", hdrs=None, fp=io.BytesIO(b""))
            return Response(existing_payload(descriptor["content_text"]), status=200)

        result = self.provider(opener).create_if_absent(descriptor)
        self.assertEqual(result["status"], "CREATE_EFFECT_OBSERVED")
        self.assertEqual(result["resolution"], "HTTP_422")
        self.assertEqual(calls, ["PUT", "GET"])

    def test_422_with_different_existing_content_is_collision(self):
        descriptor = claim_descriptor()

        def opener(req, timeout=20):
            if req.get_method() == "PUT":
                raise error.HTTPError(req.full_url, 422, "exists", hdrs=None, fp=io.BytesIO(b""))
            return Response(existing_payload("different\n"), status=200)

        result = self.provider(opener).create_if_absent(descriptor)
        self.assertEqual(result["status"], "CREATE_COLLISION")
        self.assertEqual(result["path"], descriptor["path"])

    def test_timeout_then_absent_is_hold_not_blind_retry(self):
        descriptor = claim_descriptor()

        def opener(req, timeout=20):
            if req.get_method() == "PUT":
                raise TimeoutError("provider timeout")
            raise error.HTTPError(req.full_url, 404, "not found", hdrs=None, fp=io.BytesIO(b""))

        result = self.provider(opener).create_if_absent(descriptor)
        self.assertEqual(result["status"], "AMBIGUOUS_CREATE_HOLD")
        self.assertIn("SAFE_TO_BLINDLY_RETRY", result["law"])

    def test_timeout_then_identical_readback_resolves_as_applied(self):
        descriptor = claim_descriptor()

        def opener(req, timeout=20):
            if req.get_method() == "PUT":
                raise TimeoutError("provider timeout")
            return Response(existing_payload(descriptor["content_text"]), status=200)

        result = self.provider(opener).create_if_absent(descriptor)
        self.assertEqual(result["status"], "CREATE_EFFECT_OBSERVED")
        self.assertIn("TimeoutError", result["resolution"])

    def test_arbitrary_path_is_rejected_before_network(self):
        descriptor = claim_descriptor()
        descriptor["path"] = "README.md"
        called = {"value": False}

        def opener(req, timeout=20):
            called["value"] = True
            raise AssertionError("network must not be reached")

        with self.assertRaisesRegex(ValueError, "fixed claim namespace"):
            self.provider(opener).create_if_absent(descriptor)
        self.assertFalse(called["value"])

    def test_claim_path_body_mismatch_is_rejected_before_network(self):
        descriptor = claim_descriptor()
        descriptor["content"]["node_id"] = "other"
        descriptor["content_text"] = json.dumps(descriptor["content"], sort_keys=True, indent=2) + "\n"
        with self.assertRaisesRegex(ValueError, "node_id/path mismatch"):
            self.provider(lambda req, timeout=20: None).create_if_absent(descriptor)

    def test_event_sequence_path_mismatch_is_rejected(self):
        descriptor = event_descriptor()
        descriptor["content"]["sequence"] = 4
        descriptor["content_text"] = json.dumps(descriptor["content"], sort_keys=True, indent=2) + "\n"
        with self.assertRaisesRegex(ValueError, "sequence/path mismatch"):
            validate_provider_descriptor(descriptor)

    def test_event_type_outside_claim_membrane_is_rejected(self):
        descriptor = event_descriptor()
        descriptor["content"]["event_type"] = "RUN_COMMITTED"
        descriptor["content_text"] = json.dumps(descriptor["content"], sort_keys=True, indent=2) + "\n"
        with self.assertRaisesRegex(ValueError, "event_type"):
            validate_provider_descriptor(descriptor)


if __name__ == "__main__":
    unittest.main()
