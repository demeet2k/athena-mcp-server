# Quadrant Binary Bootstrap Control Report

## control phase
bootstrap-only validation

## docs gate status
- state: BLOCKED
- witness: Live Google Docs gate check executed first via Trading Bot/search_docs.ps1; blocked because credentials.json is missing and process launch is denied in this runtime.

## qbd path witness
- automation cwd: C:/Users/dmitr/Documents/Athena Agent
- target path: C:/Users/dmitr/Documents/Athena Agent/Quadrant Binary
- cwd reachable: True
- target reachable: True

## anchors checked
none

## raw source status
not inspected (bootstrap lane stopped before anchor or manuscript discovery)

## artifact status
- sink path: C:/Users/dmitr/Documents/Athena Agent/NERVOUS_SYSTEM/90_LEDGERS/automations
- sink reachable: True
- artifact: report_written
- report path: C:\Users\dmitr\Documents\Athena Agent\NERVOUS_SYSTEM\90_LEDGERS\automations\quadrant_binary_bootstrap_control_2026-03-13_16.md

## blockers
- Google Docs live search unavailable in current runtime (missing OAuth client credentials and process launch restriction).

## restart seed
Re-run bootstrap lane from C:/Users/dmitr/Documents/Athena Agent after live Google Docs OAuth credentials are available; keep scope limited to docs gate + QBD reachability + sink write.
