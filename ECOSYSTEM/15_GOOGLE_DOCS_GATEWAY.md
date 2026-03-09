# GOOGLE DOCS GATEWAY

## 1. Objective

The Google Docs gateway extends the local corpus with live document search, retrieval, and witness-bearing intake.

## 2. Current Gate

Known blockers:
- missing `credentials.json`
- missing `token.json`

Observed command surface:
- `C:\\Users\\dmitr\\Documents\\Athena Agent\\Trading Bot\\docs_search.py`

## 3. Bootstrap Contract

Required files:
- `C:\\Users\\dmitr\\Documents\\Athena Agent\\Trading Bot\\credentials.json`
- `C:\\Users\\dmitr\\Documents\\Athena Agent\\Trading Bot\\token.json`

Bootstrap sequence:
1. Create or select Google Cloud project.
2. Enable Google Drive API.
3. Create Desktop App OAuth client.
4. Place client file at `credentials.json`.
5. Run auth flow to mint `token.json`.

## 4. Intake Rules

No Google Docs artifact may be treated as canonical until:
- query is recorded
- document URL is recorded
- modified timestamp is recorded
- owner or source is recorded
- retrieved excerpt is attached as a witness

## 5. Truth Classification

- If the gateway is blocked, document it as AMBIG or FAIL depending on whether a lawful bootstrap path exists.
- If retrieval succeeds but source semantics are uncertain, classify AMBIG.
- If retrieval succeeds with bound excerpt and provenance, classify OK or NEAR.

## 6. Local Mirror Policy

Preferred workflow:
1. query live Docs
2. capture result metadata
3. mirror excerpt into local markdown packet
4. bind excerpt to a local artifact

## 7. Status

The gateway is the live-memory bridge, but until credentials exist it remains a documented gate rather than an active memory surface.
