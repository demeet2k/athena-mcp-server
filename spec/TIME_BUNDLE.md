# Time / Liminal Address Bundle

Every crystallized output receives:

`Tau=<UTC,UNIX_NS,TAI,TT,JD_UTC,logical,liminal,ephemeris,provenance>`.

At the rebuild epoch the configured civil/atomic relation is `TAI = UTC + 37 s`, with provenance pinned to IERS Bulletin C 72 (2026-07-06). `TT = TAI + 32.184 s`.

The runtime also records a causal/logical event count and the liminal address `LIMINAL/<agent>/<task>/SEQ:<n>`.

Astronomical/astrological ephemeris coordinates are not fabricated. If no external/native ephemeris solution is supplied, the field remains `UNKNOWN`; Julian Date is still computed from UTC as an astronomical time coordinate.
