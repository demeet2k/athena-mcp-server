"""Create an explicitly synthetic fixture for an immutable local route delivery."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

BRAIN_HEAD = "9d46dafb8d17a5afaae31fd6eb9501a70fa43867"
ATHENA_HEAD = "32e7eb9b8da14987bc37dc1af62a126b6c92abe5"
ADAPTER_BASELINE_HEAD = "cacc660071da1c9ba5513b950f94742563f0b13a"


def commit_sha(value):
    if re.fullmatch(r"[0-9a-f]{40}", value) is None:
        raise argparse.ArgumentTypeError("expected a complete lowercase 40-character Git commit SHA")
    return value


def verify_checkout(root, expected, label):
    actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                     text=True, timeout=15).strip()
    if actual != expected:
        raise ValueError(f"{label}: checkout HEAD differs from requested immutable pin")
    dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                                    text=True, timeout=15)
    if dirty.strip():
        raise ValueError(f"{label}: tracked source edits must be reviewed before running")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("brain", "mcp", "athena", "output"):
        p.add_argument("--" + name, required=True, type=Path)
    p.add_argument("--mcp-head", required=True, type=commit_sha,
                   help="immutable published delivery commit; no branch names or implicit baseline")
    a = p.parse_args(argv)
    roots = {name: getattr(a, name).resolve() for name in ("brain", "mcp", "athena")}
    for name, pin in (("brain", BRAIN_HEAD), ("mcp", a.mcp_head), ("athena", ATHENA_HEAD)):
        verify_checkout(roots[name], pin, name)
    sys.path.insert(0, str(roots["brain"] / "src"))
    from athenachka_brain.snapshot import HEADERS, import_capture, write_snapshot

    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    state = "SYNTHETIC-PUBLIC-DEMO-V1"
    stamp = "2026-10-04T00:00:00Z"
    rows = {
        "CLAIMS": [{"CLAIM_ID": "DEMO.C001", "PAGE_ID": "DEMO.PAGE", "EPI": "SIM",
            "CLAIM_SUMMARY": "Synthetic fixture: the public demonstration has one inert claim.",
            "EVIDENCE_ID_OR_URL": "DEMO.EVIDENCE", "VERIFICATION": "SYNTHETIC_ONLY"}],
        "PAGES": [{"PAGE_ID": "DEMO.PAGE", "TITLE": "Synthetic public demonstration", "EPI_SCOPE": "SIM"}],
        "EVIDENCE": [{"EVIDENCE_ID": "DEMO.EVIDENCE", "KIND": "SYNTHETIC_FIXTURE",
            "TITLE": "Demonstration data, not a scientific observation", "EPI": "SIM"}],
        "CONFLICTS": [],
        "CONFIG": [{"KEY": "STATE_ROOT_VERSION", "VALUE": state, "TYPE": "STRING"}],
    }
    tables, sheets = {}, []
    for index, (name, headers) in enumerate(HEADERS.items()):
        values = [headers] + [[row.get(key, "") for key in headers] for row in rows[name]]
        last = chr(64 + len(headers))
        tables[name] = {"truncated": False, "pagination_complete": True,
            "response": {"range": f"{name}!A1:{last}{len(values)}", "majorDimension": "ROWS", "values": values},
            "tail": {"range": f"{name}!A{len(values)+1}:A100", "majorDimension": "ROWS", "values": []}}
        sheets.append({"properties": {"title": name, "sheetId": index,
            "gridProperties": {"columnCount": len(headers), "rowCount": 100}}})
    capture = {"schema": "ATHENACHKA.CAPTURE.INPUT.V1", "spreadsheet_id": "SYNTHETIC_PUBLIC_DEMO",
        "metadata": {"spreadsheetId": "SYNTHETIC_PUBLIC_DEMO", "sheets": sheets},
        "observed_at": stamp, "acquisition_started_at": stamp, "revision_bound": False,
        "provider_revision": "SYNTHETIC_1", "provider_revision_before": "SYNTHETIC_1",
        "provider_revision_after": "SYNTHETIC_1", "tables": tables}
    snapshot = import_capture(capture)
    sha = write_snapshot(snapshot, out / "snapshot")
    pins = {"brain": BRAIN_HEAD,
        "mcp": a.mcp_head,
        "athena": ATHENA_HEAD}
    spec = {key: str(value) for key, value in
        [(f"{name}_root", root) for name, root in roots.items()]}
    spec.update({f"{name}_head": pin for name, pin in pins.items()})
    spec.update(snapshot_root=str(out / "snapshot"), snapshot_digest=sha,
        state_root=state, query="DEMO.C001", observed_at="2026-10-03T20:00:00-04:00")
    (out / "capture.json").write_text(json.dumps(capture, indent=2), encoding="utf-8")
    (out / "spec.json").write_text(json.dumps(spec, indent=2), encoding="utf-8")
    print(json.dumps({"spec": str(out / "spec.json"), "snapshot_digest": sha,
        "scope": "SYNTHETIC_PUBLIC_DEMO_ONLY"}))


if __name__ == "__main__":
    main()
