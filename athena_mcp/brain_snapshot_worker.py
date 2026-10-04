"""Fixed, isolated, read-only brain snapshot consumer (not an OS sandbox)."""
import json
from pathlib import Path
import subprocess
import sys


def main():
    spec = json.loads(sys.stdin.buffer.read(1_000_001))
    root = Path(spec["brain_root"])
    def clean():
        head = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"]).decode().strip()
        dirty = subprocess.check_output(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"])
        if head != spec["brain_head"] or dirty:
            raise ValueError("BRAIN_CODE_DRIFT")
    clean()
    sys.path.insert(0, str(root / "src"))
    from athenachka_brain.snapshot import load_snapshot, query_snapshot
    snapshot = load_snapshot(spec["snapshot_root"], spec["snapshot_digest"])
    answer = query_snapshot(snapshot, spec["query"], spec["state_root"])
    clean()
    sys.stdout.buffer.write(json.dumps(answer, ensure_ascii=False, allow_nan=False).encode())


if __name__ == "__main__":
    main()
