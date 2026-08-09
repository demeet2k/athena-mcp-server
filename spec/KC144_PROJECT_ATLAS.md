# KC144 Project Atlas V1

`ATHENA.KC144.PROJECT_ATLAS.v1` gives every tracked Git object and every MCP surface object an exact, reversible address while preserving the existing identity laws.

## Why this chart exists

KC144 is an immutable 12×12 reference geometry. A station can host many objects and is never object identity. A whole repository therefore cannot be made exact by assigning one bare GID to each file.

Project Atlas factors the address instead:

`NATIVE_GIT × PROJECT_KC144 × KC144_REFERENCE × FIBER × VERSION_FIBER × ROUTE × RETURN`.

The exact native witness is:

`<repo, ref, head, tree, path, object_sha, git_type, mode>`.

`PROJECT_KC144` is a typed semantic chart on the same 12×12 geometry:

`gid = 12*(row-1)+col`.

The existing SHA256-based KC144 station projection remains a separate `KC144_REFERENCE` coordinate. No silent chart replacement occurs.

## Row axis — lifecycle/navigation phase

1. ORIGIN_CONSTITUTION
2. IDENTITY_SCHEMA
3. ADMIT_INGEST
4. HYDRATE_RETRIEVE
5. NAVIGATE_COORDINATE
6. TRANSFORM_COMPILE
7. EXECUTE_RUNTIME
8. VERIFY_TEST
9. LEARN_MEMORY
10. COHERE_COORDINATE
11. PROMOTE_RELEASE
12. OBSERVE_RETURN

## Column axis — artifact carrier

1. ROOT_CONTROL
2. CONFIG_MANIFEST
3. SOURCE_CODE
4. TOOL_API
5. DATA_REGISTRY
6. SCHEMA_SPEC
7. TEST_WITNESS
8. DOCUMENTATION
9. STATE_EVENT
10. WORKFLOW_CI
11. ASSET_EXTERNAL
12. META_OTHER

This creates 144 semantic project seats. Multiple objects may lawfully occupy one seat. Exactness inside a seat comes from `POID`, `fiber`, native Git identity, and the head-qualified `version_fiber`.

## Navigation

Every record exposes simultaneous routes:

- native Git route: repository → ref/head → tree → path → object SHA;
- hierarchical KC144 route: repository root → every path prefix → leaf;
- semantic station route: lifecycle row × carrier column;
- grid neighbors: N/E/S/W without wrap;
- toroidal neighbors: N/E/S/W with 12×12 wrap;
- deterministic previous/next tree-order links and local indexes.

`route_records(src,dst)` gives a deterministic row-then-column route in `PROJECT_KC144`. The route is navigation only; it does not assert semantic equivalence between objects occupying visited stations.

## Exact Git-path preservation

Git paths are native identity witnesses. Project Atlas removes only explicit caller convenience prefixes such as `./`; it never strips a legal leading dot. Therefore `.github/workflows/ci.yml` remains exactly `.github/workflows/ci.yml` through address generation and RETURN.

Absolute paths and parent escapes are rejected rather than silently normalized into another repository object.

## Frontier digest factorization

The atlas compiles the committed Git tree selected by `ref`, not the mutable checkout. Its digest therefore binds:

`<repo_key, ref, head, tree, record identities>`.

It deliberately excludes local checkout root, current branch label, and dirty/untracked worktree state. Those remain visible observation metadata, but they cannot mutate the identity of an unchanged committed frontier.

This preserves:

`SAME_REPO_REF_HEAD_TREE -> SAME_ATLAS_DIGEST`

across agents and checkout paths while still exposing `dirty=true` when local uncommitted state exists.

## MCP surface

`mcp_surface_atlas(...)` coordinates tools and prompts as virtual objects:

`mcp/<server>/<tool|prompt>/<name>`.

A virtual MCP record is head-qualified to the runtime repository frontier and has a definition digest. It is not falsely represented as a Git blob.

Its RETURN is an `athena+mcp://...` locator carrying runtime HEAD and definition digest, not an `athena+git://...` blob locator.

`compile_runtime_atlas(...)` combines the exact Git tree atlas and the installed `TOOLS`/`PROMPTS` surface, then emits a federation root.

## Cross-repository federation

`federate_atlases(...)` keeps each repository's exact `repo_key`, `head`, `tree`, and atlas digest. Two repositories at equal KC144 stations remain distinct. Two different heads of one repository remain distinct.

## RETURN

Every Git record contains a reversible native locator and `git_show` witness. KC144 coordinates are never sufficient RETURN authority by themselves. MCP virtual objects terminate at a head-qualified MCP definition witness instead.

## Laws

```text
KC144_STATION != OBJECT_IDENTITY
PROJECT_KC144 != CANONICAL_KC144_REFERENCE
PATH_IDENTITY != CONTENT_IDENTITY
BLOB_EQUIVALENCE != OBJECT_IDENTITY
HEAD != VID
SAME_STATION != SAME_OBJECT
RENAME_CHANGES_PATH_MANIFESTATION_COORDINATE
HEAD_CHANGE_INVALIDATES_VERSION_FIBER_UNTIL_RECOMPILE
SAME_REPO_REF_HEAD_TREE -> SAME_ATLAS_DIGEST
CHECKOUT_DIRTY_STATE != COMMITTED_FRONTIER_IDENTITY
MCP_VIRTUAL_OBJECT != GIT_BLOB
CROSS_REPO_ROUTE_REQUIRES_EXACT_REPO_HEAD
RETURN_REQUIRES_NATIVE_WITNESS
COORDINATE_NAVIGATION != PROMOTION_AUTHORITY
```

## CLI

Generate the exact Git atlas for a checkout:

```bash
athena-project-atlas . --ref HEAD -o project-atlas.json
```

Include the installed MCP tool/prompt surface:

```bash
athena-project-atlas . --ref HEAD --include-mcp-surface -o runtime-project-atlas.json
```

The generated atlas is a frontier-qualified observation. If HEAD changes, recompile before using version fibers or cross-repository routes for consequential work.
