from __future__ import annotations

import hashlib
import json
import unittest
from urllib import error

from athena_mcp.agent_bootstrap import GitHubIssuePressureProvider


class _Headers(dict):
    def get(self, key, default=None):
        return super().get(key, default)


class _Response:
    def __init__(self, payload, *, etag='"fixture-etag"', status=200):
        self._raw = json.dumps(payload).encode("utf-8")
        self.headers = _Headers({"ETag": etag})
        self.status = status

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _DummyGit:
    enabled = False


class IssuePressureProviderTests(unittest.TestCase):
    def _issues(self):
        return [
            {
                "number": 160,
                "title": "P0 child: One-call cold-start agent bootstrap",
                "body": "PRIVATE ISSUE BODY that must never be copied into the boot packet",
                "labels": [{"name": "P0"}, {"name": "runtime"}],
                "updated_at": "2026-08-08T20:00:00Z",
                "state": "open",
                "html_url": "https://example.invalid/issues/160",
            },
            {
                "number": 999,
                "title": "Bootstrap PR masquerading as an issue",
                "body": "must be filtered",
                "labels": [],
                "updated_at": "2026-08-08T20:01:00Z",
                "state": "open",
                "html_url": "https://example.invalid/pull/999",
                "pull_request": {"url": "https://api.example.invalid/pulls/999"},
            },
        ]

    def test_token_and_raw_issue_body_never_enter_snapshot(self):
        token = "ghp_SUPER_SECRET_TEST_TOKEN_SHOULD_NOT_LEAK"
        issues = self._issues()

        def opener(req, timeout=15):
            self.assertEqual(req.get_header("Authorization"), f"Bearer {token}")
            return _Response(issues)

        provider = GitHubIssuePressureProvider(
            _DummyGit(),
            opener=opener,
            environ={"ATHENA_GITHUB_TOKEN": token},
        )
        packet = provider.snapshot(
            task="cold-start bootstrap",
            issue_repo="demeet2k/Athena",
            limit=10,
        )

        serialized = json.dumps(packet, sort_keys=True)
        self.assertNotIn(token, serialized)
        self.assertNotIn("PRIVATE ISSUE BODY", serialized)
        self.assertNotIn("must be filtered", serialized)
        self.assertTrue(packet["witness"]["authenticated"])
        self.assertEqual(len(packet["relevant"]), 1)
        self.assertEqual(packet["relevant"][0]["issue_number"], 160)
        self.assertEqual(packet["relevant"][0]["standing"], "PRESSURE_ONLY")
        self.assertEqual(
            packet["relevant"][0]["body_digest"],
            hashlib.sha256(issues[0]["body"].encode("utf-8")).hexdigest(),
        )

    def test_pressure_digest_excludes_retrieval_witness_noise(self):
        calls = {"n": 0}

        def opener(req, timeout=15):
            calls["n"] += 1
            return _Response(self._issues(), etag=f'"etag-{calls["n"]}"')

        provider = GitHubIssuePressureProvider(_DummyGit(), opener=opener, environ={})
        first = provider.snapshot(
            task="cold-start bootstrap",
            issue_repo="demeet2k/Athena",
        )
        second = provider.snapshot(
            task="cold-start bootstrap",
            issue_repo="demeet2k/Athena",
        )

        self.assertEqual(first["digest"], second["digest"])
        self.assertNotEqual(first["witness"]["etag"], second["witness"]["etag"])
        self.assertFalse(first["witness"]["authenticated"])

    def test_provider_failure_holds_without_secret_material(self):
        token = "ghp_FAILURE_PATH_SECRET"

        def opener(req, timeout=15):
            raise error.HTTPError(req.full_url, 403, "Forbidden", hdrs=None, fp=None)

        provider = GitHubIssuePressureProvider(
            _DummyGit(),
            opener=opener,
            environ={"GITHUB_TOKEN": token},
        )
        packet = provider.snapshot(
            task="bootstrap",
            issue_repo="demeet2k/Athena",
        )

        self.assertEqual(packet["status"], "ISSUE_PRESSURE_UNAVAILABLE_HOLD")
        self.assertFalse(packet["fresh"])
        self.assertTrue(packet["witness"]["authenticated"])
        self.assertNotIn(token, json.dumps(packet, sort_keys=True))
        self.assertEqual(packet["law"], "ISSUE_PRESSURE != SCHED_READY")


if __name__ == "__main__":
    unittest.main()
