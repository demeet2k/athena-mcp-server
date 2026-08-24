from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from athena_mcp.federation_ephemeral_bridge import decode_handoff_ref, encode_handoff_ref, project_post_args

ROOT=Path(__file__).resolve().parents[1]
FIXTURE=ROOT/"tests/fixtures/federation_synapse_transport_conformance_v1.json"
ATHENA_CANONICAL_VECTOR_BLOB_SHA="1d46ccf2694f15f174ef7f2e9a47b709883c01ce"


def athena_digest(value):
    raw=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode("utf-8")
    return "sha256:"+hashlib.sha256(raw).hexdigest()


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob "+str(len(raw)).encode("ascii")+b"\0"+raw).hexdigest()


class FederationSynapseTransportConformanceTests(unittest.TestCase):
    def raw(self):
        return FIXTURE.read_bytes()

    def payload(self):
        return json.loads(self.raw().decode("utf-8"))

    def test_fixture_is_byte_identical_to_canonical_athena_blob(self):
        self.assertEqual(git_blob_sha(self.raw()),ATHENA_CANONICAL_VECTOR_BLOB_SHA)

    def test_vector_set_digest_uses_athena_canonical_json(self):
        payload=self.payload()
        self.assertEqual(
            athena_digest({"vectors":payload["vectors"],"laws":payload["laws"]}),
            payload["expected_vector_set_digest"],
        )

    def test_mcp_transport_projection_matches_every_athena_vector(self):
        for vector in self.payload()["vectors"]:
            self.assertEqual(athena_digest(vector["source_cursor"]),vector["expected_source_cursor_digest"])
            self.assertEqual(athena_digest(vector["handoff"]),vector["expected_handoff_digest"])
            self.assertEqual(vector["handoff"]["source_cursor_digest"],vector["expected_source_cursor_digest"])
            self.assertEqual(
                encode_handoff_ref(vector["expected_handoff_digest"],vector["expected_source_cursor_digest"]),
                vector["expected_mcp_transport_ref"],
            )
            decoded=decode_handoff_ref(vector["expected_mcp_transport_ref"])
            self.assertEqual(decoded.handoff_digest,vector["expected_handoff_digest"])
            self.assertEqual(decoded.source_cursor_digest,vector["expected_source_cursor_digest"])
            post,projection=project_post_args({
                "sender_aid":"conformance-producer",
                "recipient_aids":["conformance-consumer"],
                "handoff_digest":vector["expected_handoff_digest"],
                "source_cursor_digest":vector["expected_source_cursor_digest"],
                "lamport":1,
            })
            self.assertEqual(projection.transport_ref,vector["expected_mcp_transport_ref"])
            self.assertEqual(post["packet_digest_or_ref"],vector["expected_mcp_transport_ref"])
            self.assertTrue(all(granted is False for _,granted in vector["handoff"]["authority"]))

    def test_unicode_vector_survives_utf8_without_ascii_escape_contract_drift(self):
        raw=self.raw()
        self.assertIn("source:μ".encode("utf-8"),raw)
        self.assertIn("node:α".encode("utf-8"),raw)
        self.assertNotIn(b"\\u03bc",raw)


if __name__=="__main__":
    unittest.main()
