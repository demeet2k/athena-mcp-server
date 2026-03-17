# Query Surface

The deeper neural net can be queried locally through the CLI entrypoint:

```powershell
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" doc DOC0000
```

## Runtime indices

- `../09_RUNTIME/03_query_index.json`: exact and fuzzy lookup aliases.
- `../09_RUNTIME/04_facet_index.json`: element, family, chapter, appendix, gate, and source-layer slices.
- `../09_RUNTIME/05_neighbor_index.json`: strongest overall, cross-element, and cross-family neighbors per document.
- `../09_RUNTIME/06_zero_point_index.json`: highest-yield convergence routes near the zero-point cluster.
- `../../06_RUNTIME/13_chapter_frontier_manifest.json`: chapter frontier compiler receipt and generated pack targets.
- `../../14_PARALLEL_PLANS/04_plan_manifest.json`: materialized `frontier4` plan lattice for the frontier quartet.

## Output modes

- Default: markdown to stdout.
- `--json`: JSON to stdout.
- `--write`: writes both markdown and JSON to `last/` with deterministic filenames.
