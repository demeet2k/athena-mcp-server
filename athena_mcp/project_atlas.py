from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote

from .identity import digest
from .kc144 import station, stable_gid

SCHEMA = "ATHENA.KC144.PROJECT_ATLAS.v1"
ADDRESS_SCHEMA = "ATHENA.KC144.PROJECT_ADDRESS.v1"

# PROJECT_KC144 is a typed semantic chart on the existing immutable 12x12 host.
# It does not replace canonical KC144 reference projection or native Git identity.
ROW_AXIS = {
    1: "ORIGIN_CONSTITUTION",
    2: "IDENTITY_SCHEMA",
    3: "ADMIT_INGEST",
    4: "HYDRATE_RETRIEVE",
    5: "NAVIGATE_COORDINATE",
    6: "TRANSFORM_COMPILE",
    7: "EXECUTE_RUNTIME",
    8: "VERIFY_TEST",
    9: "LEARN_MEMORY",
    10: "COHERE_COORDINATE",
    11: "PROMOTE_RELEASE",
    12: "OBSERVE_RETURN",
}
COLUMN_AXIS = {
    1: "ROOT_CONTROL",
    2: "CONFIG_MANIFEST",
    3: "SOURCE_CODE",
    4: "TOOL_API",
    5: "DATA_REGISTRY",
    6: "SCHEMA_SPEC",
    7: "TEST_WITNESS",
    8: "DOCUMENTATION",
    9: "STATE_EVENT",
    10: "WORKFLOW_CI",
    11: "ASSET_EXTERNAL",
    12: "META_OTHER",
}

_CONTROL_NAMES = {
    "agents.md", "athena.manifest.json", "prompt.manifest.json", "pyproject.toml",
    "readme.md", "license", "license.md", ".gitignore", ".gitattributes",
}
_ROW_HINTS = [
    (1, ("constitution", "policy", "policies", "agent", "manifest", "authority_ceiling")),
    (2, ("identity", "schema", "schemas", "registry", "oid", "vid", "mid", "cid")),
    (3, ("ingest", "admit", "bootstrap", "import", "input", "seed")),
    (4, ("hydrate", "rehydrat", "retrieve", "search", "query", "rag", "fetch")),
    (5, ("navigation", "navigate", "coordinate", "kc144", "polycoord", "graph", "route", "jspace", "atlas")),
    (6, ("transform", "compile", "compiler", "mapping", "mapper", "convert", "render")),
    (7, ("runtime", "server", "dispatch", "executor", "execute", "orchestration", "deploy", "worker")),
    (8, ("test", "tests", "verify", "validator", "validation", "check", "ci", "witness")),
    (9, ("learn", "learning", "memory", "developments", "development", "knowledge")),
    (10, ("swarm", "cohesion", "message_board", "message-board", "party", "campaign", "coordination", "beacon")),
    (11, ("release", "promotion", "promote", "package", "distribution", "publish")),
    (12, ("ledger", "state", "event", "events", "log", "observ", "return", "report", "receipt")),
]


def _tokens(path: str) -> set[str]:
    p = path.lower().replace("\\", "/")
    return {x for x in re.split(r"[^a-z0-9]+", p) if x}


def _normalize_git_path(path: str) -> str:
    """Normalize caller convenience prefixes without altering legal Git dot-paths."""
    p = path.replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    if p.startswith("/"):
        raise ValueError("Git project path must be repository-relative")
    if p in {"", ".", ".."} or any(part == ".." for part in PurePosixPath(p).parts):
        raise ValueError("Git project path must be a non-empty normalized repository-relative path")
    return p


def classify_row(path: str, kind: str = "blob") -> int:
    p = path.lower().replace("\\", "/")
    name = PurePosixPath(p).name
    if kind in {"repository", "ref", "commit"} or name in _CONTROL_NAMES:
        return 1
    tokens = _tokens(p)
    priority = (8, 11, 12, 5, 2, 4, 3, 6, 10, 9, 7, 1)
    hints = {row: words for row, words in _ROW_HINTS}
    for row in priority:
        if any((w in p if "_" in w or "-" in w else w in tokens) for w in hints[row]):
            return row
    return 7 if kind == "blob" else 5


def classify_col(path: str, kind: str = "blob") -> int:
    p = path.lower().replace("\\", "/")
    pp = PurePosixPath(p)
    name, suffix, tokens = pp.name, pp.suffix.lower(), _tokens(p)
    if kind in {"repository", "ref", "commit"} or name in _CONTROL_NAMES:
        return 1
    if ".github/workflows/" in p or "workflow" in tokens or suffix in {".yml", ".yaml"} and ".github" in p:
        return 10
    if "tests" in tokens or name.startswith("test_") or name.endswith("_test.py") or "fixture" in tokens:
        return 7
    if "schemas" in tokens or "spec" in tokens or name.endswith(".schema.json"):
        return 6
    if "registry" in tokens or "data" in tokens or suffix in {".csv", ".tsv", ".sqlite", ".db"}:
        return 5
    if suffix in {".md", ".rst", ".txt", ".adoc"} or "docs" in tokens or "documentation" in tokens:
        return 8
    if "state" in tokens or "ledger" in tokens or "events" in tokens or "runtime" in tokens and suffix == ".json":
        return 9
    if "api" in tokens or "tool" in tokens or "tools" in tokens or "protocol" in tokens or "server" in tokens or "dispatch" in tokens:
        return 4
    if suffix in {".json", ".toml", ".ini", ".cfg", ".conf", ".env"} or "config" in tokens or "manifest" in tokens:
        return 2
    if suffix in {".py", ".pyi", ".js", ".jsx", ".ts", ".tsx", ".rs", ".go", ".java", ".c", ".cc", ".cpp", ".h", ".hpp", ".sh", ".ps1"}:
        return 3
    if suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg", ".pdf", ".zip", ".gz", ".tar", ".wasm"}:
        return 11
    return 12


def semantic_station(path: str, kind: str = "blob") -> dict:
    row, col = classify_row(path, kind), classify_col(path, kind)
    st = station(12 * (row - 1) + col)
    return {
        **asdict(st), "row_semantic": ROW_AXIS[row], "col_semantic": COLUMN_AXIS[col],
        "chart": "PROJECT_KC144", "projection": "lifecycle_row_x_carrier_column",
    }


def reference_station(native_key: str) -> dict:
    st = station(stable_gid(native_key))
    return {**asdict(st), "chart": "KC144", "projection": "stable_gid_sha256_64_mod_144"}


def _normalize_repo_key(remote: str | None, root: str | Path | None = None) -> str:
    raw = (remote or "").strip()
    if raw:
        raw = re.sub(r"^git@([^:]+):", r"\1/", raw)
        raw = re.sub(r"^[a-z]+://", "", raw, flags=re.I).rstrip("/")
        return raw[:-4] if raw.endswith(".git") else raw
    return f"local/{Path(root).resolve().name}" if root is not None else "local/unknown"


def _git(root: Path, *args: str, binary: bool = False):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=not binary)
    if p.returncode:
        err = p.stderr.decode() if binary and isinstance(p.stderr, bytes) else p.stderr
        out = p.stdout.decode() if binary and isinstance(p.stdout, bytes) else p.stdout
        raise RuntimeError((err or out or "git command failed").strip())
    return p.stdout


def _entry_id(repo_key: str, path: str, kind: str) -> str:
    return "POID." + digest({"repo": repo_key, "path": path, "kind": kind}, 24)


def _fiber(repo_key: str, path: str, kind: str) -> str:
    return digest({"repo": repo_key, "path": path, "kind": kind}, 32)


def _version_fiber(repo_key: str, path: str, object_sha: str, head: str) -> str:
    return digest({"repo": repo_key, "path": path, "object_sha": object_sha, "head": head}, 32)


def _prefix_route(repo_key: str, path: str, kind: str) -> list[dict]:
    root_key = f"repo:{repo_key}"
    route = [{"locator": root_key, **reference_station(root_key)}]
    if not path:
        return route
    parts = list(PurePosixPath(path).parts)
    for i in range(1, len(parts) + 1):
        prefix = "/".join(parts[:i])
        k = "tree" if i < len(parts) or kind == "tree" else kind
        route.append({"locator": prefix, **reference_station(f"{repo_key}:{k}:{prefix}")})
    return route


def _grid_neighbors(gid: int, wrap: bool) -> dict[str, int | None]:
    st = station(gid)

    def at(row: int, col: int):
        if wrap:
            row, col = ((row - 1) % 12) + 1, ((col - 1) % 12) + 1
        elif not (1 <= row <= 12 and 1 <= col <= 12):
            return None
        return 12 * (row - 1) + col

    return {"N": at(st.row - 1, st.col), "E": at(st.row, st.col + 1), "S": at(st.row + 1, st.col), "W": at(st.row, st.col - 1)}


def _station_path(src_gid: int, dst_gid: int, wrap: bool = False) -> list[int]:
    src, dst = station(src_gid), station(dst_gid)
    r, c, out = src.row, src.col, [src_gid]

    def steps(a: int, b: int):
        direct = b - a
        if not wrap:
            return [1 if direct > 0 else -1] * abs(direct)
        forward, backward = direct % 12, (-direct) % 12
        return [1] * forward if forward <= backward else [-1] * backward

    for dr in steps(r, dst.row):
        r = ((r - 1 + dr) % 12) + 1 if wrap else r + dr
        out.append(12 * (r - 1) + c)
    for dc in steps(c, dst.col):
        c = ((c - 1 + dc) % 12) + 1 if wrap else c + dc
        out.append(12 * (r - 1) + c)
    return out


@dataclass(frozen=True)
class NativeGitCoordinate:
    repo: str
    ref: str
    head: str
    tree: str
    path: str
    object_sha: str
    git_type: str
    mode: str


def project_coordinate(*, repo_key: str, ref: str, head: str, tree: str, path: str,
                       object_sha: str, git_type: str = "blob", mode: str = "100644") -> dict:
    path = _normalize_git_path(path)
    native = NativeGitCoordinate(repo_key, ref, head, tree, path, object_sha, git_type, mode)
    semantic, reference = semantic_station(path, git_type), reference_station(f"{repo_key}:{git_type}:{path}")
    fiber = _fiber(repo_key, path, git_type)
    version_fiber = _version_fiber(repo_key, path, object_sha, head)
    poid = _entry_id(repo_key, path, git_type)
    quoted = quote(path, safe="/-._~")
    return_uri = f"athena+git://{quote(repo_key, safe='/-._~')}@{head}/{quoted}?object={object_sha}&type={git_type}"
    address = f"PROJECT_KC144.G{semantic['gid']:03d}.R{semantic['row']:02d}.C{semantic['col']:02d}/F:{fiber}/POID:{poid}/VF:{version_fiber}"
    return {
        "schema": ADDRESS_SCHEMA, "poid": poid, "native": asdict(native),
        "project_kc144": semantic, "kc144_reference": reference,
        "fiber": fiber, "version_fiber": version_fiber, "address": address,
        "route": _prefix_route(repo_key, path, git_type),
        "grid_neighbors": _grid_neighbors(semantic["gid"], False),
        "torus_neighbors": _grid_neighbors(semantic["gid"], True),
        "return": {
            "uri": return_uri,
            "git_show": f"{head}:{path}" if git_type == "blob" else object_sha,
            "law": "RETURN resolves by native Git witness; KC144 coordinates never replace Git identity.",
        },
        "laws": [
            "KC144_STATION != OBJECT_IDENTITY", "PATH_IDENTITY != CONTENT_IDENTITY",
            "BLOB_EQUIVALENCE != OBJECT_IDENTITY", "HEAD != VID",
            "PROJECT_KC144 != CANONICAL_KC144_REFERENCE", "RETURN_REQUIRES_NATIVE_WITNESS",
        ],
    }


def _parse_ls_tree(raw: bytes) -> list[dict]:
    entries = []
    for rec in raw.split(b"\0"):
        if not rec:
            continue
        meta, path_b = rec.split(b"\t", 1)
        mode_b, type_b, sha_b = meta.split(b" ", 2)
        entries.append({"mode": mode_b.decode(), "git_type": type_b.decode(), "object_sha": sha_b.decode(), "path": path_b.decode("utf-8", "surrogateescape")})
    return entries


def compile_git_atlas(root: str | Path, ref: str = "HEAD", include_trees: bool = True) -> dict:
    root = Path(root).resolve()
    head = _git(root, "rev-parse", ref).strip()
    tree = _git(root, "rev-parse", f"{head}^{{tree}}").strip()
    branch = _git(root, "branch", "--show-current").strip()
    try:
        remote = _git(root, "remote", "get-url", "origin").strip()
    except RuntimeError:
        remote = ""
    repo_key = _normalize_repo_key(remote, root)
    args = ["ls-tree", "-r", "-z"]
    if include_trees:
        args.append("-t")
    args.append(head)
    entries = _parse_ls_tree(_git(root, *args, binary=True))
    records = [project_coordinate(repo_key=repo_key, ref=ref, head=head, tree=tree, **e) for e in entries]
    records.sort(key=lambda r: (r["native"]["path"], r["native"]["git_type"]))

    by_station, by_reference_station, by_blob, by_dir = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    by_poid = {}
    for i, rec in enumerate(records):
        path = rec["native"]["path"]
        rec["ordinal"] = i
        rec["navigation"] = {
            "previous": records[i - 1]["poid"] if i else None,
            "next": records[i + 1]["poid"] if i + 1 < len(records) else None,
            "parent_path": str(PurePosixPath(path).parent) if "/" in path else "",
        }
        sg, rg = f"G{rec['project_kc144']['gid']:03d}", f"G{rec['kc144_reference']['gid']:03d}"
        by_station[sg].append(rec["poid"])
        by_reference_station[rg].append(rec["poid"])
        if rec["native"]["git_type"] == "blob":
            by_blob[rec["native"]["object_sha"]].append(rec["poid"])
        by_dir[rec["navigation"]["parent_path"]].append(rec["poid"])
        by_poid[rec["poid"]] = path

    offsets = defaultdict(int)
    for rec in records:
        sg = f"G{rec['project_kc144']['gid']:03d}"
        rec["navigation"]["station_ordinal"] = offsets[sg]
        rec["navigation"]["station_population"] = len(by_station[sg])
        offsets[sg] += 1

    repository = {
        "repo_key": repo_key, "root_name": root.name, "ref": ref, "branch": branch,
        "head": head, "tree": tree, "dirty": bool(_git(root, "status", "--porcelain").strip()),
    }
    atlas = {
        "schema": SCHEMA, "status": "GENERATED",
        "repository": repository,
        "coordinate_system": {
            "host": "KC144 12x12 immutable station geometry",
            "project_chart": "PROJECT_KC144 = lifecycle_row x carrier_column",
            "row_axis": ROW_AXIS, "column_axis": COLUMN_AXIS,
            "fiber": "SHA256-derived POID/fiber preserves exact object address inside shared seats",
            "reference_projection": "existing stable_gid SHA256-64 mod 144 retained as separate KC144 reference chart",
        },
        "counts": {
            "entries": len(records),
            "blobs": sum(r["native"]["git_type"] == "blob" for r in records),
            "trees": sum(r["native"]["git_type"] == "tree" for r in records),
            "occupied_project_stations": len(by_station), "occupied_reference_stations": len(by_reference_station),
        },
        "records": records,
        "indexes": {
            "by_project_station": dict(sorted(by_station.items())),
            "by_reference_station": dict(sorted(by_reference_station.items())),
            "by_blob": dict(sorted(by_blob.items())), "by_directory": dict(sorted(by_dir.items())),
            "by_poid": dict(sorted(by_poid.items())),
        },
        "laws": [
            "EVERY_TRACKED_ENTRY_HAS_EXACT_NATIVE_AND_PROJECT_COORDINATES",
            "KC144_STATION != OBJECT_IDENTITY", "PROJECT_KC144_SEMANTIC_CHART != KC144_HASH_REFERENCE_CHART",
            "SAME_BLOB != SAME_OBJECT", "RENAME_CHANGES_PATH_MANIFESTATION_COORDINATE",
            "HEAD_CHANGE_INVALIDATES_VERSION_FIBER_UNTIL_RECOMPILE", "RETURN_MUST_END_AT_NATIVE_GIT_WITNESS",
        ],
    }
    digest_repository = {k: repository[k] for k in ("repo_key", "ref", "head", "tree")}
    atlas["atlas_digest_basis"] = "repo_key+ref+head+tree+native/project record identity; excludes checkout root, branch label and dirty worktree state"
    atlas["atlas_digest"] = digest({
        "repository": digest_repository,
        "records": [{"poid": r["poid"], "native": r["native"], "project_kc144": r["project_kc144"], "fiber": r["fiber"]} for r in records],
    }, 32)
    validate_atlas(atlas)
    return atlas


def mcp_surface_atlas(*, repo_key: str, head: str, server_name: str, tools: list[dict], prompts: list[dict] | None = None) -> dict:
    prompts, items = prompts or [], []
    for kind, rows in (("tool", tools), ("prompt", prompts)):
        for row in rows:
            name = row["name"]
            path = f"mcp/{server_name}/{kind}/{name}"
            object_sha = digest({"kind": kind, "definition": row}, 40).lower()
            rec = project_coordinate(repo_key=repo_key, ref="MCP_SURFACE", head=head, tree="VIRTUAL", path=path,
                                     object_sha=object_sha, git_type=f"mcp_{kind}", mode="virtual")
            rec["mcp"] = {"server": server_name, "kind": kind, "name": name, "definition_digest": object_sha}
            rec["return"] = {
                "uri": f"athena+mcp://{quote(server_name, safe='-._~')}/{kind}/{quote(name, safe='-._~')}?head={head}&definition={object_sha}",
                "runtime_head": head,
                "definition_digest": object_sha,
                "law": "RETURN resolves to the head-qualified MCP surface definition; MCP virtual object is not a Git blob.",
            }
            items.append(rec)
    items.sort(key=lambda r: (r["mcp"]["kind"], r["mcp"]["name"]))
    return {
        "schema": "ATHENA.KC144.MCP_SURFACE_ATLAS.v1", "repo_key": repo_key, "head": head,
        "server": server_name, "count": len(items), "records": items,
        "surface_digest": digest([{"poid": r["poid"], "mcp": r["mcp"], "project_kc144": r["project_kc144"]} for r in items], 32),
    }


def federate_atlases(atlases: list[dict], mcp_surfaces: list[dict] | None = None) -> dict:
    roots = []
    for atlas in atlases:
        repo = atlas["repository"]
        roots.append({
            "kind": "git_repository", "repo_key": repo["repo_key"], "head": repo["head"], "tree": repo["tree"],
            "atlas_digest": atlas["atlas_digest"], "kc144_reference": reference_station(f"repo:{repo['repo_key']}@{repo['head']}"),
        })
    for surface in mcp_surfaces or []:
        roots.append({
            "kind": "mcp_surface", "repo_key": surface["repo_key"], "head": surface["head"], "server": surface["server"],
            "surface_digest": surface["surface_digest"], "kc144_reference": reference_station(f"mcp:{surface['server']}@{surface['head']}"),
        })
    roots.sort(key=lambda r: (r["kind"], r.get("repo_key", ""), r["head"]))
    return {
        "schema": "ATHENA.KC144.PROJECT_FEDERATION.v1", "roots": roots, "count": len(roots),
        "federation_digest": digest(roots, 32),
        "law": "CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD; semantic station equality never erases repository frontier identity.",
    }


def route_records(src: dict, dst: dict, wrap: bool = False) -> dict:
    gids = _station_path(src["project_kc144"]["gid"], dst["project_kc144"]["gid"], wrap=wrap)
    return {
        "src": src["poid"], "dst": dst["poid"], "wrap": wrap,
        "station_route": [{**asdict(station(g)), "row_semantic": ROW_AXIS[station(g).row], "col_semantic": COLUMN_AXIS[station(g).col]} for g in gids],
        "hops": max(0, len(gids) - 1), "return": [src["return"], dst["return"]],
        "law": "STATION_ROUTE_IS_NAVIGATION_NOT_OBJECT_EQUIVALENCE",
    }


def validate_atlas(atlas: dict) -> dict:
    records, seen_path_type, seen_poid = atlas.get("records", []), set(), set()
    for rec in records:
        native, st = rec["native"], rec["project_kc144"]
        key = (native["path"], native["git_type"])
        if key in seen_path_type:
            raise ValueError(f"duplicate Git tree entry {key}")
        seen_path_type.add(key)
        if rec["poid"] in seen_poid:
            raise ValueError(f"POID collision {rec['poid']}")
        seen_poid.add(rec["poid"])
        if st["gid"] != 12 * (st["row"] - 1) + st["col"] or st["sid"] != f"KC144.SID.{st['gid']:03d}":
            raise ValueError(f"broken station roundtrip for {native['path']}")
        expected_return = f"{native['head']}:{native['path']}" if native["git_type"] == "blob" else native["object_sha"]
        if rec["return"]["git_show"] != expected_return:
            raise ValueError(f"broken RETURN for {native['path']}")
    if atlas.get("counts") and atlas["counts"].get("entries") != len(records):
        raise ValueError("entry count mismatch")
    return {"status": "PASS", "entries": len(records), "poids": len(seen_poid)}


def compile_runtime_atlas(root: str | Path, ref: str = "HEAD", include_trees: bool = True) -> dict:
    git_atlas = compile_git_atlas(root, ref, include_trees=include_trees)
    try:
        from .protocol import PROMPTS, SERVER_INFO, TOOLS
    except Exception as exc:
        return {"schema": "ATHENA.KC144.RUNTIME_PROJECT_ATLAS.v1", "git": git_atlas, "mcp_surface": {"status": "HOLD", "reason": f"protocol import failed: {exc}"}}
    repo = git_atlas["repository"]
    surface = mcp_surface_atlas(repo_key=repo["repo_key"], head=repo["head"], server_name=SERVER_INFO.get("name", "athena-canonical-mcp"), tools=TOOLS, prompts=PROMPTS)
    return {
        "schema": "ATHENA.KC144.RUNTIME_PROJECT_ATLAS.v1", "git": git_atlas, "mcp_surface": surface,
        "federation": federate_atlases([git_atlas], [surface]),
    }


def _main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Compile exact Git + KC144 project coordinates for every tracked object.")
    ap.add_argument("repo", nargs="?", default=".", help="Git checkout root")
    ap.add_argument("--ref", default="HEAD", help="Git ref/commit to coordinate")
    ap.add_argument("--no-trees", action="store_true", help="Coordinate blobs only")
    ap.add_argument("--output", "-o", help="Write JSON atlas to this path; stdout if omitted")
    ap.add_argument("--include-mcp-surface", action="store_true", help="Also coordinate every installed MCP tool and prompt")
    args = ap.parse_args(argv)
    atlas = compile_runtime_atlas(args.repo, args.ref, not args.no_trees) if args.include_mcp_surface else compile_git_atlas(args.repo, args.ref, not args.no_trees)
    text = json.dumps(atlas, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
