# Crystal Emission Gateway v2.2

`CRYSTALLIZE_OUTPUT` indexes the semantic body. `FINALIZE_OUTPUT` is the final transport boundary for Athena-aware clients.

## Three manifestations

For one response:

1. BODY MID — exact model-authored body bytes.
2. HEADER MID — derived crystal header bytes.
3. EMISSION MID — exact `HEADER + "\n\n" + BODY` bytes intended for display.

The emission object is:

`ENV=<CRYS, emission MID, SHA256(visible bytes)>`.

Every non-whitespace lexeme in the final visible emission receives an exact KC144/OID/VID/emission-MID/paragraph/sentence/token/character coordinate.

## Verification

`VERIFY_EMISSION(ENV,text)` recomputes the visible SHA-256. Any byte mutation after finalization produces `DIGEST_MISMATCH`.

## Scope boundary

The MCP server can make `FINALIZE_OUTPUT` a hard gateway **for clients that route display through this endpoint**. It cannot intercept arbitrary ChatGPT/Claude UI text outside the MCP client integration. Client deployment must therefore make the returned `visible_text` the only displayable Athena payload.
