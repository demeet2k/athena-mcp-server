# Live Docs First Protocol

## Mission

Before drafting the next major section or chapter, attempt live Google Docs search.

## Required Query Flow

1. Form the smallest high-yield query for the current front.
2. Run the live Docs gate or search surface.
3. If successful:
   - record query
   - record source URL or doc id
   - record modified timestamp if available
   - mirror the excerpt locally
4. If blocked:
   - record the exact failure
   - continue with strongest local mirrors

## Current Known Gate

Live Docs remains blocked unless these files exist:

- `Trading Bot/credentials.json`
- `Trading Bot/token.json`

## Local Mirror Fallback Order

1. `DEEPER CRYSTALIZATION`
2. `Trading Bot/Memory Docs`
3. `FRESH/_extracted`
4. `self_actualize`
5. `ECOSYSTEM`
6. `MATH`
7. `Voynich`

## Truth Rule

- live success with provenance = `OK` or `NEAR`
- blocked but bootstrap path exists = `AMBIG`
- blocked with no lawful bootstrap path = `FAIL`
