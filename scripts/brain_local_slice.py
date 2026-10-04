"""Run or cold-reconstruct the explicit local brain/MCP/Athena slice."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from athena_mcp.brain_slice import read_json, reconstruct, run

parser = argparse.ArgumentParser()
parser.add_argument("mode", choices=["run", "reconstruct"])
parser.add_argument("--directory", required=True)
parser.add_argument("--spec")
parser.add_argument("--task-digest")
parser.add_argument("--receipt-digest")
args = parser.parse_args()
if args.mode == "run":
    result = run(read_json(Path(args.spec).read_bytes()), args.directory)
else:
    result = reconstruct(args.directory, expected_task_sha256=args.task_digest,
                         expected_receipt_sha256=args.receipt_digest)
print(json.dumps(result, sort_keys=True))
