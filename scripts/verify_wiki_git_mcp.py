"""Replay the actual semantic Wiki through fresh MCP and compiler processes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--semantic-root", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    semantic = Path(args.semantic_root).resolve()
    runtime = Path(__file__).resolve().parent.parent
    when = "2026-09-08T14:00:00Z"
    # Separate scoped scaffold; no creation or mutation is applied.
    paths = {"root":"", "raw_root":"/raw", "wiki_root":"/wiki", "meta_root":"/wiki/_meta",
             "schema_path":"/WIKI.schema.json", "index_path":"/wiki/index.md", "log_path":"/wiki/log.md",
             "source_ledger_path":"/wiki/_meta/sources.jsonl", "claim_ledger_path":"/wiki/_meta/claims.jsonl",
             "contradiction_ledger_path":"/wiki/_meta/contradictions.jsonl"}
    wiki = {key:"knowledge_mcp_replay"+suffix for key,suffix in paths.items()}
    requests = [
        {"operation":"INIT", "wiki":wiki, "observed_at":when},
        {"operation":"QUERY", "query":"replication", "pages":[], "sources":[], "claims":[
            {"claim_id":"fixture.old", "statement":"The method improves replication.", "epistemic_status":"HYP", "observed_at":when, "superseded_by":["fixture.new"]},
            {"claim_id":"fixture.new", "statement":"Replication gain remains unknown.", "epistemic_status":"UNK", "observed_at":when, "supersedes":["fixture.old"]},
        ]},
        {"operation":"QUERY", "query":"unanswered", "pages":[], "sources":[], "claims":[]},
    ]
    with tempfile.TemporaryDirectory() as temporary:
        db = str(Path(temporary)/"mcp.db")
        receipts = []
        for request in requests:
            messages = [
                {"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-11-25","capabilities":{},"clientInfo":{"name":"git-wiki-replay","version":"1"}}},
                {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"athena_git_wiki_compile","arguments":{"expected_git_head":args.expected_head,"request":request}}},
            ]
            process = subprocess.run([sys.executable,"-B","-m","athena_mcp","--db",db,"--git-root",str(semantic)],
                input="".join(json.dumps(m)+"\n" for m in messages),text=True,encoding="utf-8",capture_output=True,
                cwd=runtime,env={**os.environ,"PYTHONUTF8":"1","PYTHONDONTWRITEBYTECODE":"1"},timeout=210)
            assert process.returncode == 0, process.stderr
            responses = {r["id"]:r for r in map(json.loads,process.stdout.splitlines())}
            result = responses[1]["result"]
            assert not result.get("isError"), result
            receipt = result["structuredContent"]
            assert receipt["git_head"] == args.expected_head
            assert receipt["standing"] == "COMPLETE", receipt
            assert receipt["mutation_applied"] is False
            assert receipt["active_room_worker_admitted"] is False
            assert receipt["behavioral_gain"] == "UNKNOWN"
            receipts.append(receipt)
    init, query, missing = [r["execution_receipt"]["outputs"][0]["result"] for r in receipts]
    assert init["standing"] == "READY" and len(init["mutation_plan"]) == 8
    assert not (semantic/"knowledge_mcp_replay").exists()
    claims = {c["claim_id"]:c for c in query["minimum_decision_cone"]["claims"]}
    assert claims["fixture.old"]["current"] is False
    assert claims["fixture.old"]["epistemic_status"] == "HYP"
    assert claims["fixture.new"]["current"] is True
    assert claims["fixture.new"]["epistemic_status"] == "UNK"
    assert missing["standing"] == receipts[2]["wiki_standing"] == "HOLD"
    report = {"standing":"PASS","semantic_head":args.expected_head,
              "init_plan_actions":8,"scaffold_applied":False,
              "historical_hypothesis_preserved":True,"current_unknown_preserved":True,
              "missing_evidence_holds":True,"fixtures_are_research_evidence":False,
              "receipts":receipts}
    if args.output:
        Path(args.output).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="receipts"},indent=2))


if __name__ == "__main__":
    main()
