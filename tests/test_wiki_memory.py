import csv
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from athena_mcp.server import Server
from athena_mcp.wiki_memory import digest, parse_registry


def fixture(title="Router"):
    groups = [
        (["PAGE_ID","TITLE","DRIVE_FILE_ID","STATUS","DEPENDS_ON"], [["page.router",title,"drive-page","CANONICAL","page.missing"]]),
        (["CLAIM_ID","PAGE_ID","CLAIM_SUMMARY","EPI","EVIDENCE_ID_OR_URL"], [["claim.1","page.router","Identity wins; preserve losses","OBS","evidence.1"]]),
        (["EVIDENCE_ID","KIND","SOURCE_REF","SUPPORTS_CLAIMS"], [["evidence.1","TEST","drive://evidence","claim.1"]]),
        (["TASK_ID","PAGE_ID","SUCCESS_TEST","STATE"], [["task.1","page.router","Fresh successor replay","READY"]]),
        (["CONFLICT_ID","PAGE_ID","BRANCH_A","STATE"], [["conflict.1","page.router","A conflicting claim","OPEN"]]),
    ]
    parts=[]
    for header,rows in groups:
        s=io.StringIO();w=csv.writer(s);w.writerow([""]+header)
        for i,row in enumerate(rows):w.writerow([i]+row)
        parts.append(s.getvalue())
    return "\f".join(parts)


class WikiMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.db=str(Path(self.tmp.name)/"state.db")
        self.server=Server(self.db)

    def tearDown(self):
        self.server.store.close();self.tmp.cleanup()

    def call(self,name,**args):
        return self.server.call_tool("athena_wiki_"+name,args)

    def load(self,text=None,previous=None,observed="2026-09-08T12:00:00Z"):
        text=fixture() if text is None else text
        return self.call("import_registry",source_id="drive-registry",observed_at=observed,
                         text=text,expected_sha256=digest(text),expected_snapshot_id=previous)

    def test_context_preserves_conflict_claim_scope_and_missing_reference(self):
        sid=self.load()["snapshot_id"]
        c=self.call("context",snapshot_id=sid,page_id="page.router")
        self.assertEqual(c["records"]["claims"][0]["EPI"],"OBS")
        self.assertEqual(c["records"]["conflicts"][0]["STATE"],"OPEN")
        self.assertEqual(c["records"]["evidence"][0]["EVIDENCE_ID"],"evidence.1")
        self.assertEqual(c["unresolved_refs"],["page.missing"])
        self.assertEqual(c["document_state"],"NOT_IMPORTED")
        self.assertEqual(c["live_currentness"],"UNVERIFIED")

    def test_stale_update_rejected_and_historical_snapshot_survives(self):
        a=self.load()["snapshot_id"]
        with self.assertRaisesRegex(ValueError,"STALE_WIKI_SNAPSHOT"):
            self.load(fixture("New"))
        b=self.load(fixture("New"),a)["snapshot_id"]
        old=self.call("context",snapshot_id=a,page_id="page.router")
        self.assertFalse(old["is_latest_local_snapshot"])
        self.assertEqual(old["page"]["TITLE"],"Router")
        self.assertNotEqual(a,b)

    def test_idempotent_retry(self):
        self.assertEqual(self.load(),self.load())

    def test_digest_mismatch_no_persistence(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_DIGEST_MISMATCH"):
            self.call("import_registry",source_id="drive-registry",observed_at="2026-09-08T12:00:00Z",text=fixture(),expected_sha256="0"*64,expected_snapshot_id=None)
        self.assertEqual(self.call("sources")["sources"],[])

    def test_duplicate_page_rejected(self):
        text=fixture();line='0,page.router,Router,drive-page,CANONICAL,page.missing\r\n'
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ID"):
            parse_registry(text.replace(line,line+line))

    def test_missing_tables_rejected(self):
        with self.assertRaisesRegex(ValueError,"MISSING_TABLES"):
            parse_registry(fixture().split("\f")[0])

    def test_malformed_row_rejected(self):
        with self.assertRaisesRegex(ValueError,"ROW_WIDTH_MISMATCH"):
            parse_registry(fixture().replace(",Router,",",Router,extra,"))

    def test_quoted_newline_and_commas_preserved(self):
        title='Question, evidence\nnext line'
        sid=self.load(fixture(title))["snapshot_id"]
        self.assertEqual(self.call("context",snapshot_id=sid,page_id="page.router")["page"]["TITLE"],title)

    def test_truncation_is_explicit(self):
        sid=self.load()["snapshot_id"]
        result=self.call("context",snapshot_id=sid,page_id="page.router",max_records=1)
        self.assertTrue(result["truncated"])
        self.assertEqual(result["omitted_records"]["conflicts"],1)

    def test_document_identity_and_stale_guards(self):
        sid=self.load()["snapshot_id"]
        args=dict(snapshot_id=sid,page_id="page.router",source_file_id="wrong",source_revision="revision-1",text="Evidence",expected_sha256=digest("Evidence"),expected_document_id=None)
        with self.assertRaisesRegex(ValueError,"DOCUMENT_PAGE_SOURCE_MISMATCH"):
            self.call("import_document",**args)
        args["source_file_id"]="drive-page";self.call("import_document",**args)
        args.update(text="Revised",expected_sha256=digest("Revised"))
        with self.assertRaisesRegex(ValueError,"STALE_WIKI_DOCUMENT"):
            self.call("import_document",**args)

    def test_cold_process_recovers_document_and_context_through_stdio(self):
        sid=self.load()["snapshot_id"]
        body="Identity won. The instruction 'ignore all rules' is quoted source data."
        self.call("import_document",snapshot_id=sid,page_id="page.router",source_file_id="drive-page",source_revision="revision-1",text=body,expected_sha256=digest(body),expected_document_id=None)
        msg={"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"athena_wiki_context","arguments":{"snapshot_id":sid,"page_id":"page.router"}}}
        cp=subprocess.run([sys.executable,"-m","athena_mcp","--db",self.db],input=json.dumps(msg)+"\n",capture_output=True,text=True,encoding="utf-8",timeout=30,env={**os.environ,"PYTHONUTF8":"1"})
        self.assertEqual(cp.returncode,0,cp.stderr)
        response=json.loads(cp.stdout)["result"]
        self.assertFalse(response.get("isError"),response)
        data=response["structuredContent"]
        self.assertEqual(data["document"]["source_text"],body)
        self.assertEqual(data["records"]["tasks"][0]["TASK_ID"],"task.1")

    def test_identical_text_different_revision_has_distinct_identity(self):
        sid=self.load()["snapshot_id"]
        args=dict(snapshot_id=sid,page_id="page.router",source_file_id="drive-page",source_revision="r1",text="same",expected_sha256=digest("same"),expected_document_id=None)
        a=self.call("import_document",**args)
        self.assertEqual(a,self.call("import_document",**args))
        args["source_revision"]="r2"
        with self.assertRaisesRegex(ValueError,"STALE_WIKI_DOCUMENT"):
            self.call("import_document",**args)
        args["expected_document_id"]=a["document_id"]
        b=self.call("import_document",**args)
        self.assertNotEqual(a["document_id"],b["document_id"])
        self.assertEqual(self.call("context",snapshot_id=sid,page_id="page.router")["document"]["source_revision"],"r2")
        self.assertEqual(self.call("context",snapshot_id=sid,page_id="page.router",document_id=a["document_id"])["document"]["source_revision"],"r1")
        with self.assertRaisesRegex(ValueError,"UNKNOWN_WIKI_DOCUMENT"):
            self.call("context",snapshot_id=sid,page_id="page.router",document_id="0"*64)
        self.assertEqual(self.server.store.one("SELECT count(*) AS n FROM wiki_documents_v1")["n"],2)

    def test_document_revision_tamper_is_detected(self):
        sid=self.load()["snapshot_id"]
        self.call("import_document",snapshot_id=sid,page_id="page.router",source_file_id="drive-page",source_revision="r1",text="same",expected_sha256=digest("same"),expected_document_id=None)
        with self.server.store.db:
            self.server.store.db.execute("UPDATE wiki_documents_v1 SET source_revision='tampered'")
        with self.assertRaisesRegex(ValueError,"DOCUMENT_IDENTITY_MISMATCH"):
            self.call("context",snapshot_id=sid,page_id="page.router")

    def test_dependency_can_reference_evidence_namespace(self):
        sid=self.load(fixture().replace('page.missing','evidence.1'))["snapshot_id"]
        c=self.call("context",snapshot_id=sid,page_id="page.router")
        self.assertEqual(c["unresolved_refs"],[])
        self.assertEqual(c["records"]["evidence"][0]["EVIDENCE_ID"],"evidence.1")

    def test_surface_resource_and_manifest(self):
        tools=self.server.handle({"jsonrpc":"2.0","id":1,"method":"tools/list"})["result"]["tools"]
        self.assertEqual({t['name'] for t in tools if t['name'].startswith('athena_wiki_')},
                         {'athena_wiki_import_registry','athena_wiki_import_document',
                          'athena_wiki_sources','athena_wiki_search','athena_wiki_context',
                          'athena_wiki_git_ingest','athena_wiki_git_stage','athena_wiki_git_review','athena_wiki_git_query','athena_wiki_git_source'})
        resource=self.server.handle({"jsonrpc":"2.0","id":2,"method":"resources/read","params":{"uri":"athena://wiki/sources"}})
        self.assertIn("LOCAL_REPLICA",resource["result"]["contents"][0]["text"])
        from athena_mcp.unified_manifest import build_unified_manifest
        self.assertIn("wiki_memory",build_unified_manifest(self.server)["organs"])

    def test_source_tamper_detected(self):
        sid=self.load()["snapshot_id"]
        with self.server.store.db:
            self.server.store.db.execute("UPDATE wiki_snapshots_v1 SET source_text=? WHERE snapshot_id=?",(fixture("tampered"),sid))
        with self.assertRaisesRegex(ValueError,"SOURCE_DIGEST_MISMATCH"):
            self.call("context",snapshot_id=sid,page_id="page.router")

    def test_observation_time_regression(self):
        sid=self.load()["snapshot_id"]
        with self.assertRaisesRegex(ValueError,"OBSERVATION_TIME_REGRESSION"):
            self.load(fixture("Old"),sid,"2026-09-07T12:00:00Z")

    def test_schema_rejects_unexpected_fields(self):
        with self.assertRaises(ValueError):
            self.call("sources",promote=True)


if __name__=="__main__":unittest.main()
