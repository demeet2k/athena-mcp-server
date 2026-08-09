# Σ04 BUILD-TOPOLOGY V1 — exact symbol and entrypoint coordinates

Status: **candidate child of qualified-but-unmerged Project Atlas V3; not canonical, not published, not deployed**.

Private work order: `demeet2k/Athena#528`.

Exact parent:

- repository: `demeet2k/athena-mcp-server`
- V3 integration PR: `#335`
- V3 head: `48a9af3deef7bb5db31fa7188b61b5e0cd0b932d`
- V3 CI witness: `31336608806` — success
- V3 V3.4 release-distribution witness: `31336608789` — success

## 1. Why Σ04 exists

Project Atlas V1–V3 now supplies several distinct but composable coordinate layers:

```text
POID   = stable project path/kind identity
PVTX   = exact <plane,repo,head,POID> manifestation
KC144  = geometric projection/navigation
PEDGE  = exact witnessed structural relation
PATLASG3 = replay/CAS identity for the observed structural graph
```

The next missing topology lives *inside source artifacts*. A Git blob can contain many separately addressable definitions. A pyproject entrypoint does not target an entire file; it targets a particular Python binding inside a particular module.

Therefore Σ04 adds a symbol coordinate without overloading any existing identity:

```text
PSYM = digest(PVTX, qualified_symbol, source_span_digest)
```

Law:

`PSYM != POID != PVTX != OID`.

This is a structural code coordinate. It is not a runtime object identity, semantic OID, or authority claim.

## 2. Exact Python symbol projection

Carrier: Python AST from the exact Git blob referenced by the parent PVTX.

V1 symbol classes are deliberately bounded to top-level bindings:

- function definitions;
- async function definitions;
- class definitions;
- assignments to one simple name;
- annotated assignments to one simple name.

For a symbol `s` in exact source vertex `v`:

```text
span = <lineno,col_offset,end_lineno,end_col_offset>
span_digest = H(
  exact Git object SHA,
  symbol kind,
  span,
  exact AST source segment
)

PSYM = H(
  SYMBOL_SCHEMA,
  PVTX(v),
  qualified_symbol,
  span_digest
)
```

The symbol receipt retains:

```text
<
  PSYM,
  parent PVTX,
  parent POID,
  plane,
  repo,
  head,
  path,
  module,
  name,
  qualified_symbol,
  definition kind,
  exact source span,
  span digest,
  exact object SHA,
  RETURN
>
```

RETURN preserves the exact Git object URI and appends a source-span fragment.

### Duplicate bindings

Python source may redefine the same top-level name. Σ04 does not silently pretend the first or last AST node is the unique build target. It preserves every definition as a distinct PSYM and emits:

`HOLD_AMBIGUOUS_SYMBOL`.

This is intentionally more conservative than Python runtime name rebinding. Determining the actually bound runtime object would require an execution/import model and belongs in a later layer.

`DUPLICATE_TOP_LEVEL_BINDING -> HOLD_AMBIGUOUS_SYMBOL`.

## 3. Exact module coordinate

A Python source path receives a path-derived module projection:

```text
athena_mcp/server.py          -> athena_mcp.server
athena_mcp/project_atlas.py   -> athena_mcp.project_atlas
pkg/__init__.py               -> pkg
```

This projection is resolved only inside the same exact `<plane,repo,head>` frontier as the declaration that requests it.

A module name alone is not identity:

`MODULE_NAME_MATCH != MODULE_IDENTITY`.

Possible resolution outcomes:

```text
one exact local module PVTX      -> RESOLVED
multiple local module PVTXs      -> HOLD_AMBIGUOUS_MODULE
no local module PVTX             -> HOLD_ENTRYPOINT_MODULE
```

The no-local-module state deliberately does not say “external dependency definitely exists.” It says the declared module is not a uniquely resolved local project module on this exact frontier.

## 4. PEP 621 entrypoint extractor

Σ04 V1 parses exact TOML using Python's stdlib `tomllib`.

Observed declaration surfaces:

- `[project.scripts]`
- `[project.gui-scripts]`
- `[project.entry-points.<group>]`

Supported V1 target grammar:

```text
module.path:top_level_attribute
```

Example:

```text
athena-mcp = "athena_mcp.server:main"
```

Resolution pipeline:

```text
pyproject PVTX
   |
   | TOML exact declaration
   v
<group,name,target>
   |
   | parse exact module:attribute syntax
   v
module name
   |
   | exact same-frontier module lookup
   v
module PVTX
   |
   | exact top-level AST binding lookup
   v
PSYM
   |
   v
PYPROJECT_ENTRYPOINT_RESOLVES_TO_SYMBOL edge
```

A build edge is emitted **only after every step resolves uniquely**.

Evidence class:

`EXACT_TOML_DECLARATION + EXACT_PVTX_MODULE + PYTHON_AST_SYMBOL`.

Extractor version:

`pep621_toml_entrypoint_to_python_ast_symbol_v1`.

## 5. Build edge contract

```text
PBUILD = <
  edge_id,
  kind=PYPROJECT_ENTRYPOINT_RESOLVES_TO_SYMBOL,
  source pyproject PVTX/POID,
  destination module PVTX/POID,
  destination PSYM,
  exact parent PATLASG3,
  exact PATLASV2 snapshot,
  extractor,
  evidence,
  witness,
  authority,
  loss,
  RETURN(source,destination)
>
```

Witness fields include the exact group, entrypoint name, raw target, resolved module PVTX, and resolved PSYM.

Loss witness:

`ENTRYPOINT_DECLARATION_DOES_NOT_PROVE_INSTALL_OR_EXECUTION_SUCCESS`.

Thus:

`BUILD_EDGE != EXECUTION`.

## 6. Hold lattice

V1 preserves the following non-success states:

- `HOLD_SYMBOL_SOURCE`
- `HOLD_AMBIGUOUS_SYMBOL`
- `HOLD_PYPROJECT_SOURCE`
- `HOLD_ENTRYPOINT_SYNTAX`
- `HOLD_ENTRYPOINT_MODULE`
- `HOLD_AMBIGUOUS_MODULE`
- `HOLD_ENTRYPOINT_SYMBOL`
- `HOLD_NESTED_ENTRYPOINT_SYMBOL`

Nested attribute entrypoints such as `pkg.module:Class.method` are not guessed. The current PSYM index models top-level bindings only, so such a declaration is conserved as `HOLD_NESTED_ENTRYPOINT_SYMBOL` until a nested-symbol coordinate calculus is explicitly added.

## 7. Exact live-repository witness

At the V3 parent frontier, `pyproject.toml` declares exactly:

```text
athena-mcp           -> athena_mcp.server:main
athena-project-atlas -> athena_mcp.project_atlas:_main
```

Σ04's live repository test recompiles the tracked tree and requires:

```text
athena-mcp
  -> module PVTX: athena_mcp/server.py
  -> PSYM: athena_mcp.server.main

athena-project-atlas
  -> module PVTX: athena_mcp/project_atlas.py
  -> PSYM: athena_mcp.project_atlas._main
```

Each destination must retain the exact Git head, object SHA, source span, and RETURN URI.

This is materially stronger than asserting that the strings `main` and `_main` appear somewhere in source.

## 8. Build-topology replay identity

The symbol index has its own replay coordinate:

```text
PSYMI1 = H(
  parent PATLASG3,
  exact sorted PSYM receipts,
  symbol holds,
  source failures
)
```

The V1 build topology has:

```text
PBUILDG1 = H(
  BUILD_SCHEMA/version,
  parent PATLASG3,
  PSYMI1,
  exact pyproject PVTX set,
  exact build edges,
  exact holds,
  exact extractor versions
)
```

The build graph is an observation receipt, not an authority receipt:

`BUILD_GRAPH != PROMOTION_AUTHORITY`.

## 9. Deferred workflow topology

This first Σ04 tranche intentionally does **not** parse GitHub Actions YAML or shell commands.

Deferred edge families include:

- `WORKFLOW_STEP_USES_ACTION`
- `WORKFLOW_RUNS_COMMAND`
- `WORKFLOW_REFERENCES_EXACT_PATH`
- `WORKFLOW_CALLS_WORKFLOW`
- `WORKFLOW_SELECTS_TEST`

Reason: the project currently has no runtime Python dependencies. Adding YAML parsing silently would alter package assumptions, while ad-hoc text parsing would be too weak for shell interpolation, heredocs, quoting, `$VAR`, `${{ ... }}`, command substitution, and glob expansion.

Required laws for the next tranche:

- `COMMAND_TEXT != EXECUTED_EFFECT`
- `UNRESOLVED_INTERPOLATION -> CONSERVE_UNKNOWN`

The workflow layer must earn its own parser/evidence contract rather than leaking heuristic strings into the structural graph.

## 10. Promotion membrane

Σ04 V1 begins as a child of **qualified but unmerged** V3 head `48a9af3d...`.

Before any canonical use:

1. preserve exact V3 ancestry;
2. open a child integration PR to the V3 branch;
3. use a separate master-targeted qualification-only PR to execute repository CI;
4. pass full CI on one exact Σ04 head;
5. pass current V3.4 release distribution on the same exact head;
6. prove clean wheel installation outside the repository;
7. return the exact qualification receipt to private work order #528;
8. require a separate ABI/package decision before any MCP RPC exposure;
9. require separate publication and deployment authority.

No Σ04 code path grants itself merge, RPC, publication, deployment, or canonical authority.
