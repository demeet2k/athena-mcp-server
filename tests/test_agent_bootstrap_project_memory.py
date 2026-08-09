from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "athena_mcp"))

from agent_bootstrap_project_memory import (  # noqa: E402
    ARTIFACT,
    extend_agent_boot_tool_schemas,
    install_agent_bootstrap_project_memory,
)


def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(x):
    return hashlib.sha256(x if isinstance(x, bytes) else (x.encode() if isinstance(x, str) else canon(x))).hexdigest()


def source_packet(*, status="PROJECT_MEMORY_HYDRATED", required=False, blocks=False, content="context"):
    packet = {
        "artifact": "ATHENA.PROJECT.MEMORY.BOOT.PACKET.V1",
        "status": status,
        "required": required,
        "blocks_boot": blocks,
        "query": {"query_digest": sha("task"), "basis": "TASK_DERIVED"},
        "policy": {"max_bytes": 4096, "max_results": 4, "max_depth": 1},
        "policy_digest": sha({"max_bytes": 4096, "max_results": 4, "max_depth": 1}),
        "source_stack": {"pm40": "x", "ncab144": "y", "jspace": "z"},
        "source_state_digest": sha("sources"),
        "retrieval_digest": sha("retrieval"),
        "selected": [],
        "selected_content_bytes": 0,
        "holds": [],
        "standing": "ROUTING_CONTEXT_ONLY_NOT_EVIDENCE",
        "laws": ["RETRIEVED_MEMORY != EVIDENCE"],
    }
    if status == "PROJECT_MEMORY_HYDRATED":
        packet["selected"] = [{
            "entry_id": "E1", "object_sha256": sha(content),
            "source": {"path": "a.md", "file_sha256": sha("a.md"), "chunk_ordinal": 0, "byte_start": 0, "byte_end": len(content)},
            "selection_kind": "LEXICAL_SEED", "score": 1.0, "path": [],
            "standing": "RELEVANCE_CANDIDATE_NOT_EVIDENCE", "content": content,
            "content_bytes": len(content), "content_fragment_sha256": sha(content),
        }]
        packet["selected_content_bytes"] = len(content)
    packet["packet_digest"] = sha(packet)
    return packet


class DummyRuntime:
    def __init__(self):
        self._sessions = {}
        self.counter = 0

    def bootstrap(self, *, agent_id, task="", **kwargs):
        self.counter += 1
        sid = f"S{self.counter}"
        address = {"git_head": "g", "prompt_stack_digest": "p", "frontier_digest": "f", "issue_pressure_digest": "i"}
        packet = {
            "artifact": "ATHENA.AGENT.BOOT.V1", "status": "BOOTSTRAPPED", "agent_id": agent_id,
            "session_id": sid, "task": task, "address": address, "composite_digest": sha(address),
            "holds": [], "laws": [], "return_contract": {},
            "frontier": {"ready_work": [{"work_id": "W1"}]},
            "next_frontier": {"status": "SELECTED", "selected": {"work_id": "W1"}},
            "issue_pressure": {"digest": "i"},
            "execution_surface": {"claim_tool_exposed": True},
        }
        self._sessions[sid] = {"address": dict(address), "agent_id": agent_id, "task": task}
        return packet

    def refresh(self, *, session_id=None, prior_address=None, agent_id=None, task=None, **kwargs):
        remembered = self._sessions.get(session_id or "", {})
        prior = prior_address or remembered.get("address")
        packet = self.bootstrap(agent_id=agent_id or remembered.get("agent_id") or "A", task=task if task is not None else remembered.get("task", ""))
        current = packet["address"]
        changed = {k: prior.get(k) != current.get(k) for k in current if k != "project_memory_digest"}
        packet["refresh"] = {
            "prior_address": prior, "changed": changed,
            "changed_coordinates": [k for k,v in changed.items() if v],
            "affected_dependency_cone": [], "requires_replan": any(changed.values()),
        }
        return packet

    def call_tool(self, name, a):
        if name == "athena_agent_bootstrap":
            return self.bootstrap(agent_id=a["agent_id"], task=a.get("task", ""))
        if name == "athena_agent_refresh":
            return self.refresh(session_id=a.get("session_id"), prior_address=a.get("prior_address"), agent_id=a.get("agent_id"), task=a.get("task"))
        raise KeyError(name)


install_agent_bootstrap_project_memory(DummyRuntime)


class RuntimeProjectMemoryTests(unittest.TestCase):
    def test_no_packet_is_deterministic_not_selected(self):
        r = DummyRuntime(); p = r.bootstrap(agent_id="A", task="task")
        self.assertEqual(p["project_memory"]["status"], "PROJECT_MEMORY_NOT_SELECTED")
        self.assertIn("project_memory_digest", p["address"])
        self.assertEqual(p["status"], "BOOTSTRAPPED")

    def test_valid_packet_attaches_exact_digest(self):
        r = DummyRuntime(); m = source_packet(); p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m)
        self.assertEqual(p["project_memory"]["packet_digest"], m["packet_digest"])
        self.assertEqual(p["address"]["project_memory_digest"], m["packet_digest"])

    def test_invalid_digest_fails_optional_closed(self):
        r = DummyRuntime(); m = source_packet(); m["packet_digest"] = sha("bad")
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m, project_memory_selected=True)
        self.assertEqual(p["project_memory"]["status"], "PROJECT_MEMORY_OPTIONAL_HOLD")
        self.assertEqual(p["project_memory"].get("selected"), None)
        self.assertEqual(p["status"], "BOOTSTRAPPED")

    def test_required_invalid_packet_holds_boot(self):
        r = DummyRuntime(); m = source_packet(); m["packet_digest"] = sha("bad")
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m, project_memory_required=True)
        self.assertEqual(p["status"], "BOOTSTRAP_HOLD")
        self.assertIn("PROJECT_MEMORY_REQUIRED_HOLD", p["holds"])

    def test_required_source_hold_holds_boot(self):
        r = DummyRuntime(); m = source_packet(status="PROJECT_MEMORY_REQUIRED_HOLD", required=True, blocks=True)
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m, project_memory_required=True)
        self.assertEqual(p["status"], "BOOTSTRAP_HOLD")
        self.assertTrue(p["project_memory"]["blocks_boot"])

    def test_optional_source_hold_preserves_healthy_boot(self):
        r = DummyRuntime(); m = source_packet(status="PROJECT_MEMORY_OPTIONAL_HOLD", required=False, blocks=False)
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m)
        self.assertEqual(p["status"], "BOOTSTRAPPED")
        self.assertEqual(p["project_memory"]["status"], "PROJECT_MEMORY_OPTIONAL_HOLD")

    def test_secret_field_rejected(self):
        r = DummyRuntime(); m = source_packet(); m["github_token"] = "x"; m["packet_digest"] = sha({k:v for k,v in m.items() if k != "packet_digest"})
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m, project_memory_required=True)
        self.assertEqual(p["project_memory"]["status"], "PROJECT_MEMORY_REQUIRED_HOLD")

    def test_credential_like_content_rejected(self):
        r = DummyRuntime(); m = source_packet(content="Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345")
        p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m, project_memory_required=True)
        self.assertEqual(p["project_memory"]["status"], "PROJECT_MEMORY_REQUIRED_HOLD")

    def test_memory_does_not_change_ready_or_execution_authority(self):
        r = DummyRuntime(); m = source_packet(); p = r.bootstrap(agent_id="A", task="task", project_memory_packet=m)
        self.assertEqual(p["frontier"]["ready_work"], [{"work_id":"W1"}])
        self.assertEqual(p["next_frontier"]["selected"], {"work_id":"W1"})
        self.assertTrue(p["execution_surface"]["claim_tool_exposed"])
        self.assertIn("MEMORY_QUERY != SCHED_READY", p["laws"])

    def test_refresh_reuses_remembered_memory(self):
        r = DummyRuntime(); m = source_packet(); first = r.bootstrap(agent_id="A", task="task", project_memory_packet=m)
        second = r.refresh(session_id=first["session_id"])
        self.assertEqual(first["address"]["project_memory_digest"], second["address"]["project_memory_digest"])
        self.assertFalse(second["refresh"]["changed"]["project_memory_digest"])

    def test_refresh_memory_only_change_is_factorized(self):
        r = DummyRuntime(); m1 = source_packet(content="one"); first = r.bootstrap(agent_id="A", task="task", project_memory_packet=m1)
        m2 = source_packet(content="two")
        second = r.refresh(session_id=first["session_id"], project_memory_packet=m2)
        self.assertTrue(second["refresh"]["changed"]["project_memory_digest"])
        self.assertIn("project_memory", second["refresh"]["affected_dependency_cone"])
        self.assertTrue(second["refresh"]["memory_only"])

    def test_call_tool_transports_packet(self):
        r = DummyRuntime(); m = source_packet()
        p = r.call_tool("athena_agent_bootstrap", {"agent_id":"A", "task":"task", "project_memory_packet":m})
        self.assertEqual(p["address"]["project_memory_digest"], m["packet_digest"])

    def test_tool_schema_extension_is_additive(self):
        tools=[{"name":"athena_agent_bootstrap","inputSchema":{"type":"object","properties":{"agent_id":{"type":"string"}},"additionalProperties":False}}, {"name":"other","inputSchema":{"type":"object","properties":{}}}]
        extend_agent_boot_tool_schemas(tools)
        props=tools[0]["inputSchema"]["properties"]
        self.assertIn("agent_id", props); self.assertIn("project_memory_packet", props); self.assertNotIn("project_memory_packet", tools[1]["inputSchema"]["properties"])

    def test_wrapper_is_idempotently_installed(self):
        before = DummyRuntime.bootstrap
        install_agent_bootstrap_project_memory(DummyRuntime)
        self.assertIs(before, DummyRuntime.bootstrap)

    def test_two_process_validation_digest_stable(self):
        # Same source packet validation/project-memory digest must not depend on process-local state.
        m = source_packet()
        with tempfile.TemporaryDirectory() as td:
            packet_path=Path(td)/"packet.json"; packet_path.write_text(json.dumps(m))
            code=f"""
import json,sys
sys.path.insert(0,{str(ROOT/'athena_mcp')!r})
from agent_bootstrap_project_memory import _validated_packet
p=_validated_packet(json.load(open({str(packet_path)!r})))
print(p['packet_digest'])
"""
            a=subprocess.check_output([sys.executable,"-c",code],text=True).strip()
            b=subprocess.check_output([sys.executable,"-c",code],text=True,cwd=td).strip()
        self.assertEqual(a,b); self.assertEqual(a,m["packet_digest"])


if __name__ == "__main__":
    unittest.main()
