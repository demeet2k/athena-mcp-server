# KC144 Hybrid Harness V7

V7 adds redacted keyless model-boundary recordings, a BAML prompt/type/client revision journal, fallback attempt receipts, configured cost/latency routing, and a streaming organ-coalition scheduler.

## Replay boundary

`RECORDED_REPLAY != FRESH_EXTERNAL_WITNESS`

Fixtures test parsing, validation, fallback, streaming and integration behavior. They do not create new evidence or authority.

## Routing

Models are ordered by reliability, expected latency, then configured cost. These are local estimates, not live provider pricing.

## Run

```bash
cd MCP
python -m unittest -v tests/test_kc144_v7_runtime.py
python athena_mcp_server_kc144_v7.py
```

## Status

`<SUPPORTED, PASS, RESEARCH_ONLY, TESTED>`; production `HOLD`; authority effect `NONE`; I10 receipt absent; M12 certificate held.
