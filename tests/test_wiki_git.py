import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import Mock, patch

from athena_mcp.server import Server
from athena_mcp.wiki_git import ARTIFACT, GitWikiCompiler, canonical

HEAD = "a" * 40
REQUEST = {"operation": "QUERY", "query": "negative result", "pages": [], "claims": [], "sources": []}


class GitWikiCompilerTests(unittest.TestCase):
    def setUp(self):
        self.git = Mock(enabled=True, root=Path.cwd())
        self.git.status.return_value = {"head": HEAD, "dirty": False}
        self.compiler = GitWikiCompiler(self.git)

    def response(self, **changes):
        result = {"artifact": ARTIFACT, "git_head": HEAD,
                  "request_sha256": hashlib.sha256(canonical(REQUEST)).hexdigest(),
                  "operation": "QUERY", "standing": "COMPLETE", "mutation_applied": False,
                  "execution_receipt": {"standing": "COMPLETE", "outputs": []}}
        result.update(changes)
        return subprocess.CompletedProcess([], 0, json.dumps(result).encode(), b"")

    def compile(self, **changes):
        return self.compiler.compile(**{"expected_git_head": HEAD, "request": REQUEST, **changes})

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_fixed_worker_uses_owned_json_and_preserves_receipt(self, run):
        run.return_value = self.response()
        result = self.compile()
        args, kwargs = run.call_args
        self.assertIn("-I", args[0])
        self.assertIn("-B", args[0])
        self.assertTrue(args[0][3].endswith("wiki_git_worker.py"))
        self.assertEqual(json.loads(kwargs["input"]), REQUEST)
        self.assertEqual(result["execution_receipt"], {"standing": "COMPLETE", "outputs": []})
        self.assertEqual(self.git.status.call_count, 2)

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_missing_root_stale_and_dirty_hold_before_execution(self, run):
        for enabled, state, error in [
            (False, {"head": HEAD, "dirty": False}, "ROOT_NOT_CONFIGURED"),
            (True, {"head": "b"*40, "dirty": False}, "STALE_HEAD"),
            (True, {"head": HEAD, "dirty": True}, "WORKTREE_NOT_CLEAN"),
        ]:
            with self.subTest(error=error):
                self.git.enabled = enabled
                self.git.status.return_value = state
                with self.assertRaisesRegex(ValueError, error):
                    self.compile()
        run.assert_not_called()

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_nonfinite_or_oversized_request_and_arbitrary_operation_are_rejected(self, run):
        for request in [{"operation":"QUERY","limit":float("nan")},
                        {"operation":"QUERY","query":"x"*1_000_000},
                        {"operation":"SHELL","command":"anything"}]:
            with self.subTest(operation=request["operation"]), self.assertRaises(ValueError):
                self.compile(request=request)
        with self.assertRaisesRegex(ValueError, "EXACT_COMMIT_REQUIRED"):
            self.compile(expected_git_head="main")
        run.assert_not_called()

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_changed_checkout_rejects_successful_worker_result(self, run):
        run.return_value = self.response()
        for state in [{"head":"b"*40,"dirty":False},{"head":HEAD,"dirty":True}]:
            self.git.status.side_effect = [{"head":HEAD,"dirty":False},state]
            with self.assertRaisesRegex(ValueError, "STATE_CHANGED_DURING_EXECUTION"):
                self.compile()

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_worker_response_is_bound_to_commit_request_operation_and_no_apply(self, run):
        for mismatch in [{"git_head":"b"*40},{"request_sha256":"0"*64},
                         {"operation":"INIT"},{"mutation_applied":True},{"artifact":"other"}]:
            with self.subTest(mismatch=mismatch):
                run.return_value = self.response(**mismatch)
                with self.assertRaisesRegex(ValueError, "RESPONSE_BINDING_MISMATCH"):
                    self.compile()

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_timeout_malformed_excessive_and_failed_workers_are_not_success(self, run):
        run.side_effect = subprocess.TimeoutExpired("worker",180)
        with self.assertRaisesRegex(ValueError,"EXECUTION_TIMEOUT"):
            self.compile()
        run.side_effect = None
        for output, code, error in [(b"not json",0,"INVALID_WORKER_RESPONSE"),
                                    (b"x"*4_000_001,0,"RESPONSE_TOO_LARGE"),
                                    (b"",1,"WORKER_FAILED")]:
            run.return_value = subprocess.CompletedProcess([],code,output,b"bounded failure")
            with self.subTest(error=error), self.assertRaisesRegex(ValueError,error):
                self.compile()

    @patch("athena_mcp.wiki_git.subprocess.run")
    def test_holds_are_preserved_without_success_promotion(self, run):
        receipt = {"standing":"HOLD","runtime_holds":[{"reason":"UNKNOWN_SOURCE"}],"outputs":[]}
        run.return_value = self.response(standing="HOLD",execution_receipt=receipt)
        result = self.compile()
        self.assertEqual(result["standing"],"HOLD")
        self.assertEqual(result["execution_receipt"],receipt)


class GitWikiSurfaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.server = Server(str(Path(self.tmp.name)/"state.db"))

    def tearDown(self):
        self.server.store.close()
        self.tmp.cleanup()

    def test_tool_is_composed_once_and_manifest_preserves_wiki_memory(self):
        tools = self.server.handle({"jsonrpc":"2.0","id":1,"method":"tools/list"})["result"]["tools"]
        self.assertEqual(sum(t["name"]=="athena_git_wiki_compile" for t in tools),1)
        from athena_mcp.unified_manifest import build_unified_manifest
        organs = build_unified_manifest(self.server)["organs"]
        self.assertIn("wiki_memory", organs)
        self.assertIn("git_wiki", organs)

    def test_schema_rejects_module_override_and_accepts_each_declared_operation(self):
        with patch("athena_mcp.wiki_git_extension.GitWikiCompiler.compile",return_value={"standing":"HOLD"}) as call:
            for operation in ("INIT","INGEST","QUERY","REINDEX","LINT"):
                request = {"operation":operation}
                if operation=="LINT":
                    request["index_paths"]=[]
                self.server.call_tool("athena_git_wiki_compile",{"expected_git_head":HEAD,"request":request})
            self.assertEqual(call.call_count,5)
            for extra in [{"module":"arbitrary"},{"entrypoint":"arbitrary"},{"apply":True}]:
                with self.assertRaises(ValueError):
                    self.server.call_tool("athena_git_wiki_compile",{"expected_git_head":HEAD,"request":{**REQUEST,**extra}})
            self.assertEqual(call.call_count,5)


if __name__ == "__main__":
    unittest.main()
