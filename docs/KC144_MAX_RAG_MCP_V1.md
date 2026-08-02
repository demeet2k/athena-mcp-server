# KC144 MAX–RAG MCP Cartridge v1

## Classification

`MAX_RAG_MCP_LOCAL_REVERSIBLE__PROPOSED_NOT_PROMOTED`

This is a separate MCP host layered beside the validated Athena/MMLG.3 host. It does not alter or extend the MMLG.3 catalog, and it does not claim that the control implementation has been merged or promoted.

## Exact lineage

- control repository: `demeet2k/Athena`
- control branch: `agent/kc144-max-rag-v1`
- pinned control head: `10893a9bef5ba17ab65b67f10eef2c9436138f34`
- runtime repository: `demeet2k/athena-mcp-server`
- runtime parent: MMLG.3 head `abd15be02c1153890cc289c9402fabeccf452b61`
- runtime branch: `agent/kc144-max-rag-mcp-v1`

## Authority boundary

The cartridge:

- does not contact GitHub, Drive, websites, or MCP sources;
- does not store raw private source bodies;
- does not write the Guild Hall source board;
- does not dispatch workflows or cross-plane packets;
- does not create external promotion authority;
- does not merge, deploy, or publish a persistent endpoint;
- does not claim foundation-model weight modification.

Every tool is either pure, local validation, or compilation of a non-dispatching packet.

## MCP tools

1. `max_rag_status`
2. `max_rag_registry`
3. `max_rag_query_compile`
4. `max_rag_output_plan`
5. `max_rag_claim_evaluate`
6. `max_rag_score`
7. `max_rag_repair_routes`
8. `max_rag_shadow_manifest`
9. `max_rag_shadow_compare`
10. `max_rag_shadow_suite`
11. `max_rag_successor_compile`

## MCP resources

- `athena://max-rag/v1/status`
- `athena://max-rag/v1/kc144-registry`
- `athena://max-rag/v1/shadow-benchmark`
- `athena://max-rag/v1/contract`

## Preserved KC144 topology

The runtime exposes the exact carrier ranges:

| Carrier | GIDs |
|---|---:|
| H6 | 001–006 |
| X16 | 007–022 |
| BR21 | 023–043 |
| F37 | 044–080 |
| IC10 | 081–090 |
| KC15 | 091–105 |
| KC27 | 106–132 |
| SSN12 | 133–144 |

The phase cycle is `11 → 10 → 00 → 01`, and `Q-SHRINK Core` remains fixed at `GID119`.

## Runtime behavior

### Query compilation

The cartridge compiles intent, entities, literal terms, time constraints, depth, answerability threshold, route budget, and a bounded route ensemble. It does not execute the resulting searches.

### Output planning

A token budget is split into a working budget and a protected 12.5% return reserve. The plan ends with an explicit return-packet phase.

### Claim ceiling

A retrieved claim is not automatically generatable. Its status, support count, source independence, and uncertainty determine whether generation is permitted and which linguistic ceiling applies.

### Score economy

Thirteen normalized dimensions are combined by harmonic quality. JUICE may be nonzero when a hard gate fails, but MAX and Witness Seals remain zero. A passing score returns only `ADMISSION_REVIEW_ELIGIBLE`; it creates no admission.

### Shadow comparison

A candidate is held when it self-witnesses, lacks rollback, has open defects, fails any hard gate, increases unsupported claims, regresses protected dimensions, or lacks a measured gain. An exact digest-bound independent witness is required.

### Shadow suite

Exactly twelve unique passing comparisons are required before the suite may return `CANARY_REVIEW_ELIGIBLE`. This is permission to conduct a separate review, not authority to run or admit a canary.

### Successor return

The cartridge can compile a content-addressed, non-dispatching packet back to the pinned control head. Dispatch, control review, merge, and promotion remain external actions.

## Standalone host

```bash
python MCP/max_rag_mcp_server.py
```

The standalone server exposes only the 11 tools and 4 resources above. It intentionally leaves the main MMLG.3 host unchanged.
