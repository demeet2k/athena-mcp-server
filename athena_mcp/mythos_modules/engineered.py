"""MYTHOS OS modules — family ENGINEERED (R12): designed systems, and ATHENA itself.

``athena`` is the reference module: the runtime described in README.md,
ARCHITECTURE.md, ``athena_mcp/kc144.py``, ``cycle_protocol``, ``crystal*.py``
and ``unified_manifest.py`` fills the same twelve slots as every tradition.
The code is the primary source, so the module stands as PRIMARY_EVIDENCE;
it carries no runtime authority (ATHENA_SELF_MODULE != ATHENA_AUTHORITY).
"""
from __future__ import annotations

MODULES = [
    {
        "id": "athena",
        "name": "ATHENA canonical MCP runtime (ATHENA.RUNTIME.UNIFIED.11) read as a mythos module",
        "family": "ENGINEERED",
        "standing": "PRIMARY_EVIDENCE",
        "sources": [
            "README.md (runtime cycle, constitutional braid, firewalls)",
            "ARCHITECTURE.md (identity/coordinate/transaction law)",
            "athena_mcp/kc144.py (BANDS, station law)",
            "athena_mcp/aor_development_surface.py (CYCLE phases)",
            "spec/CRYSTAL_OUTPUT_ABI.md (identity fiber, unknown law)",
            "athena_mcp/orchestration_authority.py via athena://authority (Y1 progression ? + ! #)",
            "athena_mcp/mythic_strata_runtime.py, mythic_computation_runtime.py (laws)",
        ],
        "corpus_refs": [],
        "closure_grammar_id": None,
        "services": {
            "BOOT": {
                "grade": "🟢", "mode": "CYCLIC", "src": "README.md 'Runtime cycle'; aor_development_surface.py CYCLE phases",
                "stages": [
                    {"stage": "VOID", "event": "no hydrated state: an empty store with no head", "src": "bootstrap.py"},
                    {"stage": "SEPARATION", "event": "HYDRATE: head, registry, JSPACE summary, SCALE, pending mutations separated from the Git frontier", "src": "athena_hydrate"},
                    {"stage": "ORDERING", "event": "RECONSTRUCT / OMEGA: canonical RECONRUN fixes the coordinate charts, KC144 stations, identity fiber", "src": "reconstruction.py"},
                    {"stage": "POPULATION", "event": "organs constructed: AOR, Collective V1–V15, Y1 authority, EQ1, CYCLE, prompt runtime, MCK, strata, BNMK", "src": "server.py __init__"},
                    {"stage": "FAULT", "event": "a typed WAITING_* / HOLD_* / STALE_* state: missing measurement, authority, worker or test", "src": "cycle_protocol.py"},
                    {"stage": "MAINTENANCE", "event": "MEASURE → AOR → COLLECTIVE → EXECUTE → VERIFY → LEARN → SUCCESSOR → COMPLETE", "src": "CYCLE phases"},
                    {"stage": "REBOOT", "event": "SUCCESSOR / rehydration: a fresh session re-hydrates from the Git head and continues", "src": "rehydration_* organs"},
                ],
                "notes": "FAULT is POST_POPULATION and typed: the organism fail-closes into WAITING states instead of simulating.",
            },
            "MEMMAP": {
                "grade": "🟢", "addressing": "NESTED", "axis": "KC144 station identity SID; gid = 12*(row-1)+column", "src": "kc144.py BANDS; dispatch.py athena://scale",
                "realms": [
                    {"name": "SSN12 (gid 133–144)", "level": 8, "kind": "HEAVEN", "note": "12 stations"},
                    {"name": "KC27 (gid 106–132)", "level": 7, "kind": "HEAVEN", "note": "27 stations"},
                    {"name": "KC15 (gid 91–105)", "level": 6, "kind": "HEAVEN", "note": "15 stations"},
                    {"name": "IC10 (gid 81–90)", "level": 5, "kind": "LIMINAL", "note": "10 stations: the gates"},
                    {"name": "F37 (gid 44–80)", "level": 4, "kind": "MIDDLE", "note": "37 stations"},
                    {"name": "BR21 (gid 23–43)", "level": 3, "kind": "MIDDLE", "note": "21 stations"},
                    {"name": "X16 (gid 7–22)", "level": 2, "kind": "MIDDLE", "note": "16 stations"},
                    {"name": "H6 (gid 1–6)", "level": 1, "kind": "UNDER", "note": "6 stations: the root band"},
                    {"name": "S0 RAW_EVENT … S5 ORGAN_NATIVE_LAW (SCALE ladder)", "level": 0, "kind": "ABSOLUTE", "note": "the representation ladder every object climbs"},
                ],
                "notes": "eight bands partition 144 = 6+16+21+37+10+15+27+12; JSPACE edges/hyperedges are the pointers between addresses.",
            },
            "PROC": {
                "grade": "🟢", "scheduler": "COUNCIL", "src": "README.md 'Constitutional braid'; composition_integrity.py organ lists",
                "agents": [
                    {"name": "Server", "roles": ["SOVEREIGN", "SCHEDULER"], "domain": ["one composed runtime", "dispatch"], "ring": 0, "parent": None},
                    {"name": "AOR", "roles": ["JUDGE"], "domain": ["WHAT is developmentally eligible"], "ring": 0, "parent": "Server"},
                    {"name": "Collective V1–V15", "roles": ["WORKER", "STEWARD"], "domain": ["HOW capacity is organised", "science/inference/control"], "ring": 1, "parent": "Server"},
                    {"name": "Y1 authority", "roles": ["JUDGE", "WITNESS"], "domain": ["canonical claim authority ? + ! #"], "ring": 0, "parent": "Server"},
                    {"name": "EQ1 equivalence", "roles": ["GATE"], "domain": ["witnessed equivalence collapse"], "ring": 1, "parent": "Server"},
                    {"name": "CYCLE", "roles": ["SCHEDULER"], "domain": ["sixteen phases, fail-closed"], "ring": 1, "parent": "Server"},
                    {"name": "Prompt runtime", "roles": ["SCRIBE"], "domain": ["Git-native modular prompts"], "ring": 1, "parent": "Server"},
                    {"name": "Message Board", "roles": ["MESSENGER"], "domain": ["sole coordination authority"], "ring": 1, "parent": "Server"},
                    {"name": "Crystal ABI", "roles": ["SCRIBE", "WITNESS"], "domain": ["crystallize, finalize, verify emission"], "ring": 1, "parent": "Server"},
                    {"name": "MCK", "roles": ["ORACLE"], "domain": ["bounded symbolic computation", "oracle decode"], "ring": 2, "parent": "Server"},
                    {"name": "Strata membrane", "roles": ["GATE"], "domain": ["cross-layer transport with loss"], "ring": 2, "parent": "Server"},
                    {"name": "GitHub promotion verifier", "roles": ["WITNESS", "GATE"], "domain": ["host-bound trusted qualification"], "ring": 0, "parent": None},
                    {"name": "Successor", "roles": ["PSYCHOPOMP"], "domain": ["rehydration, handoff, baton"], "ring": 1, "parent": "Server"},
                ],
                "notes": "COUNCIL: AOR decides WHAT, Collective HOW, Y1 what is true, the verifier what is qualified; no organ inherits another's authority by adjacency.",
            },
            "CLOCK": {
                "grade": "🟢", "src": "aor_development_surface.py read_resource(CYCLE); .github/workflows/ci.yml",
                "periods": [
                    {"name": "tools/call (one metered invocation)", "length": 1, "unit": "step"},
                    {"name": "CYCLE (sixteen phases HYDRATE…COMPLETE)", "length": 16, "unit": "step", "role": "year"},
                    {"name": "session (start → end, Git checkpoint)", "length": 64, "unit": "step"},
                    {"name": "release (3.x.0 qualification)", "length": 1024, "unit": "step"},
                ],
                "intercalation": {"policy": "LEAP_SECOND", "rule": "a WAITING_* phase inserts an unscheduled step; the cycle resumes at the same phase after the prerequisite is witnessed", "every_years": 0},
                "epochs": ["Ω13 → Ω14 → Ω15 (architecture generations)", "3.2.0 → 3.3.0 → 3.4.0 (releases)"],
                "festivals": [{"name": "HYDRATE", "day": 1}, {"name": "VERIFY", "day": 13}, {"name": "COMPLETE", "day": 16}],
                "notes": "lengths are step counts, not days; the CYCLE is the year.",
            },
            "RITE": {
                "grade": "🟢", "src": "dispatch.py tools/call; protocol.py athena_finalize_output / athena_verify_emission",
                "protocols": [
                    {"name": "tools/call", "required_ring": 2, "mode": "TRANSFORMING",
                     "steps": ["BOUND", "PURIFY", "INVOKE", "RECEIVE", "WITNESS", "CLOSE"],
                     "cost": "one rate-limit token; one metered runtime-usage record", "effect": "a JSON result plus structuredContent; nothing else is mutated unless the tool is a write tool"},
                    {"name": "finalize_output (emission gateway)", "required_ring": 1, "mode": "TRANSFORMING",
                     "steps": ["BOUND", "TRANSFORM", "RECITE", "WITNESS", "CLOSE"],
                     "cost": "a crystal, a header, a third emission MID over the visible bytes", "effect": "an ENV envelope whose visible bytes can be re-verified"},
                    {"name": "claim promotion (Y1)", "required_ring": 0, "mode": "TRANSFORMING",
                     "steps": ["BOUND", "PETITION", "WITNESS", "RECEIVE", "CLOSE"],
                     "cost": "verified evidence, then witnessed execution, then explicit canonical authority", "effect": "? → + → ! → #"},
                ],
            },
            "ORACLE": {
                "grade": "🟢", "src": "mythic_computation_runtime.py oracle_decode; collective V5–V15 posteriors",
                "devices": [
                    {"name": "MCK oracle_decode (seeded SHA-256 over a caller codebook)", "entropy": "COMPUTED", "space": 256, "encoding": "BINARY",
                     "decoder": "caller-supplied codebook; R != W != D != INTERPRETATION", "set_aside": None},
                    {"name": "Collective posterior (GP / BMA / TMLE)", "entropy": "COMPUTED", "space": 2, "encoding": "BINARY",
                     "decoder": "PREDICTION / POSTERIOR / PLAN != OBSERVATION / TRUTH / EXECUTION", "set_aside": "UNKNOWN != 0"},
                ],
            },
            "FAULT": {
                "grade": "🟢", "src": "dispatch.py error taxonomy; cycle_protocol.py WAITING_* states; mythic_strata_runtime.py HOLD_*",
                "faults": [
                    {"name": "STALE_TARGET (expected VID mismatch)", "class": "OATH_BREACH", "handler": ["reject the mutation", "re-resolve the head", "retry with the current VID"], "outcome": "RECOVERED"},
                    {"name": "STALE_GIT_HEAD", "class": "OATH_BREACH", "handler": ["refuse the checkpoint", "fetch the shared frontier", "retry expected-head CAS"], "outcome": "RECOVERED"},
                    {"name": "WAITING_* (missing measurement/authority/worker/test)", "class": "NEGLECT", "handler": ["halt the phase", "name the prerequisite", "resume when witnessed"], "outcome": "RECOVERED"},
                    {"name": "HOLD_* (authority mint, hazard, cross-layer equivalence)", "class": "HUBRIS", "handler": "refuse; return the law violated", "outcome": "UNRECOVERABLE"},
                    {"name": "REJECTED (schema/validation)", "class": "TRANSGRESSION", "handler": "isError with the validator's message", "outcome": "RECOVERED"},
                    {"name": "Internal error", "class": "COSMIC", "handler": ["-32603", "stderr", "successor rehydration"], "outcome": "REBOOT"},
                ],
            },
            "LEDGER": {
                "grade": "🟢", "model": "TIERED", "src": "athena://authority law; README 'Y1 progression'",
                "soul": ["CID capability", "OID object", "VID version", "MID manifestation", "CRYS crystal", "EID event", "SID station"],
                "judgment": "? → + on verified evidence; + → ! on witnessed execution; ! → # on explicit authorized canonicalization; challenges block automatic routing",
                "judge": "Y1 authority registry",
                "destinations": ["# canonical", "! witnessed", "+ verified", "? registered"],
            },
            "RING": {
                "grade": "🟢", "src": "README firewalls; promotion_protocol.py; surface_contract.py",
                "rings": [
                    {"level": 0, "name": "trusted external verification (host-bound GitHub check-suite)"},
                    {"level": 1, "name": "canonical authority (Y1 #, explicit authorized canonicalization)"},
                    {"level": 2, "name": "witnessed / verified state (+, !)"},
                    {"level": 3, "name": "model / science-shadow state (V5–V15, athena_discovery_claim_*)"},
                    {"level": 4, "name": "caller attestation (ATTESTED_READY != QUALIFIED)"},
                ],
            },
            "CODEC": {
                "grade": "🟢", "src": "spec/CRYSTAL_OUTPUT_ABI.md; emission.py",
                "record": {"medium": "DIGITAL", "script": "JSON-RPC 2025-11-25 over stdio; Git objects", "base": 2},
                "hull": "the ENV envelope: HEADER+BODY with a third emission MID over the exact visible bytes, verifiable by SHA-256",
                "compilers": ["CRYSTALLIZE_OUTPUT = Identity ∘ CASVersion ∘ Manifest ∘ LexemeIndex ∘ MathRegister ∘ GraphDelta ∘ HypergraphDelta ∘ PolyAtlas ∘ TimeBundle ∘ CrystalManifest ∘ DerivedHeader",
                              "coordinate_text: every lexeme gets KC144.G###.R##.C##/OID/VID/MID/P/S/T/C"],
            },
            "CONST": {
                "grade": "🟢",
                "constants": [
                    {"n": 144, "role": "closure", "what": "KC144 stations, 12 × 12"},
                    {"n": 12, "role": "order", "what": "rows, columns, kernel services"},
                    {"n": 16, "role": "order", "what": "CYCLE phases"},
                    {"n": 6, "role": "order", "what": "SCALE levels S0–S5; H6 band"},
                    {"n": 8, "role": "record", "what": "KC144 bands"},
                    {"n": 4, "role": "passage", "what": "Y1 states ? + ! #"},
                    {"n": 1, "role": "crossing", "what": "the third emission MID over HEADER+BODY: the record that is not part of the record"},
                ],
            },
            "LAW": {
                "grade": "🟢", "src": "README 'Core firewalls'; ARCHITECTURE.md §2",
                "invariants": ["UNKNOWN != 0", "CONSENSUS != EVIDENCE", "PREDICTION / POSTERIOR / PLAN != OBSERVATION / TRUTH / EXECUTION",
                               "MODEL_GRAPH != CANONICAL_JSPACE_GRAPH", "CALLER_ATTESTATION != TRUSTED_EXTERNAL_VERIFICATION", "ATTESTED_READY != QUALIFIED",
                               "SID != OID != MID != VID != CID != EID != CRYS != ENV", "LOOKUP != DERIVATION"],
                "acl": [{"ring": 0, "permitted": ["qualify a promotion"]}, {"ring": 1, "permitted": ["canonicalize a claim"]},
                        {"ring": 2, "permitted": ["mutate with expected-VID CAS"]}, {"ring": 3, "permitted": ["propose, predict, plan"]}],
                "canon": {"closed": False, "note": "Git-versioned, additive; prior versions preserved rather than rewritten"},
            },
        },
    },
]
