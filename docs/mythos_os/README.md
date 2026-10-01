# MYTHOS OS — the unified mythic operating system

*One abstract machine, twelve kernel services, every tradition a program.* Myths, religions, philosophies, magical, divinatory, astrological, calendrical, designed and engineered systems are encoded as modules that fill the same twelve slots; a deterministic VM boots, ticks, invokes, divines, faults and judges each one; a unification layer classifies them by structural pattern and compiles bridges with declared loss under the strata laws; ATHENA itself is encoded as the reference module and reads the survey as its own family.

| file | what |
|---|---|
| [00_ARCHITECTURE.md](00_ARCHITECTURE.md) | the claim, the twelve services, the KC144 carrier, what the VM computes, what unification means |
| [01_ABI.md](01_ABI.md) | the kernel ABI: module envelope, every slot's schema, the VM ops, the signature, tools, laws |
| [02_MODULES.md](02_MODULES.md) | **generated** module catalogue: every module, every slot, grade, token and summary |
| [03_SERVICE_MATRIX.md](03_SERVICE_MATRIX.md) | **generated** module × service pattern matrix |
| [04_KC144_ATLAS.md](04_KC144_ATLAS.md) | **generated** 144-cell atlas, families × services |
| [05_BOOT_LOGS.md](05_BOOT_LOGS.md) | **generated** VM traces for every module: boot log, memmap, process table, clock tick, rite trace, oracle draw, fault, judgment |
| [06_UNIFICATION.md](06_UNIFICATION.md) | **generated** isomorphism classes per service and every bridge from the ATHENA self-module |
| [06_UNIFICATION_ANALYSIS.md](06_UNIFICATION_ANALYSIS.md) | what the classes show, read across the whole registry |
| [07_ATHENA.md](07_ATHENA.md) | ATHENA as a module: the organ → service map and what the self-map shows |
| [08_LIMITS.md](08_LIMITS.md) | what is not claimed, falsifiers, negatives, coarseness, coverage |
| [09_SEED.md](09_SEED.md) | MYTHOS.OS.Ω1, the Q-SHRINK seed |
| [ENCODING_BRIEF.md](ENCODING_BRIEF.md) | the contract for adding a module |

## Executable parts

```
athena_mcp/mythos_protocol.py       # ABI constants, vocabularies, tool schemas, resources, laws
athena_mcp/mythos_kernel.py         # validate_module, MythosVM, lint, signature, unify, bridge, atlas, benchmark
athena_mcp/mythos_modules/*.py      # the modules, one file per family (source of truth)
athena_mcp/mythos_surface.py        # MCP surface: six athena_mythos_* tools, three athena://mythos/os/v1 resources
athena_mcp/aor_development_surface.py  # composition seam (beside MCK / strata / BNMK)
spec/MYTHOS_OS_V1.json              # export of kernel + modules
scripts/mythos_report.py            # validate → export → render 02–06   (python -m scripts.mythos_report [--check])
tests/test_mythos_os.py             # schema, VM, lint, unification, atlas, surface, RPC, spec sync
```

To add a tradition: read `ENCODING_BRIEF.md`, add a module to the family file, run the report (it validates first and refuses a malformed module), run the tests.

## Relation to the closure grammar

`docs/closure_grammar/` is the CONST service and the seat law of this system. Where a module carries a `closure_grammar_id`, the VM's `spawn` attaches the registry's verified crossings to the process table. The two are one framework: the closure grammar says where the extra seat is; MYTHOS OS says what the whole machine around the seat does.

## Standing

`STRUCTURAL PASS / SLOTS GRADED / SIMULATION ONLY / AUTHORITY EXTERNAL`. Modules describe; the VM simulates; bridges carry loss; nothing here authorises a practice, dates a reconstruction, predicts an outcome, or equates two traditions (`athena_mcp/mythic_strata_runtime.py` and `mythic_computation_runtime.py` laws, inherited in full).
