"""MYTHOS OS surface — MCP adapter for the unified mythic operating system.

Composed into ``AorDevelopmentSurface`` beside MCK / strata / BNMK.  No surface
receives authority from the others by sharing the dispatcher; the mythos VM
simulates, classifies and bridges, and never executes a practice.
"""
from __future__ import annotations

from typing import Any, Dict

from .mythos_kernel import (
    MythosVM, atlas, benchmark, compare_modules, service_matrix, signature_of, unify, validate_modules,
)
from .mythos_protocol import (
    BOOT_MODES, BOOT_STAGE_GLOSS, BOOT_STAGES, CLOCK_INTERCALATION, CODEC_MEDIA, CONST_ROLES, FAMILIES,
    FAULT_CLASSES, FAULT_OUTCOMES, GRADE_GLOSS, GRADES, LAWS, LEDGER_MODELS, MEMMAP_ADDRESSING,
    MYTHOS_ATLAS_RESOURCE, MYTHOS_KERNEL_ABI, MYTHOS_MATRIX_RESOURCE, MYTHOS_RESOURCE, MYTHOS_RESOURCES,
    MYTHOS_RESOURCE_URIS, MYTHOS_TOOL_NAMES, MYTHOS_TOOLS, MYTHOS_VERSION, ORACLE_ENCODING, ORACLE_ENTROPY,
    PROC_ROLES, PROC_SCHEDULERS, REALM_KINDS, RITE_MODES, RITE_OPCODES, SERVICE_GLOSS, SERVICES, STANDINGS,
)

ATHENA_ORGAN_MAP = {
    "BOOT": "HYDRATE → RECONRUN/OMEGA → organs constructed → CYCLE (bootstrap.py, reconstruction.py, server.py)",
    "MEMMAP": "KC144 bands as realms; SCALE S0–S5 as the ladder; JSPACE edges as pointers (kc144.py, dispatch.py athena://scale)",
    "PROC": "AOR (WHAT) · Collective V1–V15 (HOW) · Y1 (authority) · EQ1 (equivalence) · CYCLE · Message Board · Crystal ABI · MCK · strata · verifier",
    "CLOCK": "the sixteen-phase CYCLE as the year; WAITING_* as the inserted second (cycle_protocol.py)",
    "RITE": "tools/call = BOUND(rate/schema) → PURIFY(validate) → INVOKE → RECEIVE → WITNESS(meter) → CLOSE; finalize_output; Y1 promotion",
    "ORACLE": "MCK oracle_decode and the V5–V15 posteriors, both under PREDICTION != OBSERVATION",
    "FAULT": "STALE_TARGET / STALE_GIT_HEAD / WAITING_* / HOLD_* / REJECTED / Internal error, each with its handler",
    "LEDGER": "Y1 tiers ? + ! # with the promotion conditions as the judgment function",
    "RING": "trusted verification > canonical authority > witnessed > model/shadow > caller attestation",
    "CODEC": "Crystal ABI: identity fiber, lexeme index, ENV envelope with a third emission MID",
    "CONST": "144 = 12 × 12 stations; 16 phases; 6 SCALE levels; 8 bands; 4 Y1 states",
    "LAW": "the firewalls (UNKNOWN != 0, CONSENSUS != EVIDENCE, …) and the additive, never-rewritten canon",
}


def _modules():
    from .mythos_modules import MODULES, MODULE_INDEX
    return MODULES, MODULE_INDEX


def _hold_unknown(module_id: str) -> Dict[str, Any]:
    modules, _ = _modules()
    return {"version": MYTHOS_VERSION, "status": "HOLD_UNKNOWN_MODULE", "module": module_id,
            "available": sorted(m["id"] for m in modules), "authority": "NONE", "laws": list(LAWS)}


def kernel_abi() -> Dict[str, Any]:
    return {
        "version": MYTHOS_VERSION, "abi": MYTHOS_KERNEL_ABI,
        "services": [{"index": i + 1, "name": s, "gloss": SERVICE_GLOSS[s]} for i, s in enumerate(SERVICES)],
        "families": list(FAMILIES), "grades": [{"glyph": g, "gloss": GRADE_GLOSS[g]} for g in GRADES], "standings": list(STANDINGS),
        "vocabularies": {
            "BOOT": {"modes": BOOT_MODES, "stages": [{"stage": s, "gloss": BOOT_STAGE_GLOSS[s]} for s in BOOT_STAGES]},
            "MEMMAP": {"addressing": MEMMAP_ADDRESSING, "realm_kinds": REALM_KINDS},
            "PROC": {"schedulers": PROC_SCHEDULERS, "roles": PROC_ROLES},
            "CLOCK": {"intercalation": CLOCK_INTERCALATION},
            "RITE": {"opcodes": RITE_OPCODES, "modes": RITE_MODES,
                     "lint": "PURIFY/BOUND precede INVOKE; RELEASE/CLOSE follow the body; an INVOKE must CLOSE or RELEASE"},
            "ORACLE": {"entropy": ORACLE_ENTROPY, "encoding": ORACLE_ENCODING},
            "FAULT": {"classes": FAULT_CLASSES, "outcomes": FAULT_OUTCOMES},
            "LEDGER": {"models": LEDGER_MODELS},
            "CODEC": {"media": CODEC_MEDIA},
            "CONST": {"roles": CONST_ROLES},
        },
        "kc144": {"rows": "families", "columns": "services", "law": "gid = 12*(row-1)+column"},
        "laws": list(LAWS),
    }


class MythosSurface:
    def __init__(self):
        self.abi = kernel_abi()

    # ------------------------------------------------------------ tools
    def call_tool(self, name: str, args: Dict[str, Any]):
        if name not in MYTHOS_TOOL_NAMES:
            return False, None
        if name == "athena_mythos_catalog":
            return True, self.catalog(args.get("family"), bool(args.get("include_atlas")), bool(args.get("include_matrix")))
        if name == "athena_mythos_module":
            return True, self.module(args["module_id"], args.get("service"))
        if name == "athena_mythos_run":
            return True, self.run(args["module_id"], args["op"], args)
        if name == "athena_mythos_compare":
            return True, self.compare(args["left"], args["right"], args.get("services"))
        if name == "athena_mythos_unify":
            return True, self.unify(args.get("service"), args.get("left"), args.get("right"))
        if name == "athena_mythos_athena":
            return True, self.athena(args.get("op", "signature"))
        return False, None

    def catalog(self, family=None, include_atlas=False, include_matrix=False) -> Dict[str, Any]:
        modules, _ = _modules()
        rows = [m for m in modules if not family or m["family"] == family]
        listing = [{"id": m["id"], "name": m["name"], "family": m["family"], "standing": m["standing"],
                    "grades": {s: m["services"][s]["grade"] for s in SERVICES}, "sources": len(m["sources"]),
                    "closure_grammar_id": m.get("closure_grammar_id")} for m in rows]
        fam = {}
        for m in modules:
            fam[m["family"]] = fam.get(m["family"], 0) + 1
        grade_totals = {}
        for m in modules:
            for s in SERVICES:
                g = m["services"][s]["grade"]
                grade_totals[g] = grade_totals.get(g, 0) + 1
        out = {"version": MYTHOS_VERSION, "abi": self.abi, "module_count": len(modules), "by_family": dict(sorted(fam.items())),
               "slot_grades": dict(sorted(grade_totals.items())), "filter": family, "modules": listing,
               "authority": "CATALOG_ONLY", "laws": list(LAWS)}
        if include_matrix:
            out["matrix"] = service_matrix(modules)
        if include_atlas:
            out["atlas"] = atlas(modules)
        return out

    def module(self, module_id: str, service=None) -> Dict[str, Any]:
        _, index = _modules()
        m = index.get(module_id)
        if m is None:
            return _hold_unknown(module_id)
        if service:
            return {"version": MYTHOS_VERSION, "module": module_id, "service": service, "slot": m["services"][service],
                    "signature": signature_of(m)[service], "authority": "DESCRIPTION_ONLY", "laws": list(LAWS)}
        return {"version": MYTHOS_VERSION, "module": m, "signature": signature_of(m), "authority": "DESCRIPTION_ONLY", "laws": list(LAWS)}

    def run(self, module_id: str, op: str, args: Dict[str, Any]) -> Dict[str, Any]:
        _, index = _modules()
        m = index.get(module_id)
        if m is None:
            return _hold_unknown(module_id)
        vm = MythosVM(m)
        if op == "boot":
            return vm.boot()
        if op == "memmap":
            return vm.memmap()
        if op == "spawn":
            return vm.spawn()
        if op == "tick":
            return vm.tick(args.get("days", 365))
        if op == "invoke":
            return vm.invoke(args.get("rite"), args.get("caller_ring", 99), args.get("purity", True), args.get("witness"), args.get("use_case", "GENERAL"))
        if op == "divine":
            return vm.divine(args.get("device"), args.get("seed"), args.get("sample"), args.get("use_case", "GENERAL"))
        if op == "raise":
            return vm.raise_fault(args.get("fault"))
        if op == "judge":
            return vm.judge(args.get("score", 0.0))
        if op == "signature":
            return {"version": MYTHOS_VERSION, "module": module_id, "op": "signature", "signature": vm.signature(),
                    "authority": "STRUCTURAL_SIGNATURE_ONLY", "laws": list(LAWS)}
        if op == "all":
            out = vm.run_all()
            out.update({"version": MYTHOS_VERSION, "module": module_id, "op": "all", "authority": "SYMBOLIC_SIMULATION_ONLY", "laws": list(LAWS)})
            return out
        raise KeyError(op)

    def compare(self, left: str, right: str, services=None) -> Dict[str, Any]:
        _, index = _modules()
        if left not in index:
            return _hold_unknown(left)
        if right not in index:
            return _hold_unknown(right)
        return compare_modules(index[left], index[right], services)

    def unify(self, service=None, left=None, right=None) -> Dict[str, Any]:
        modules, _ = _modules()
        return unify(modules, service, left, right)

    def athena(self, op: str = "signature") -> Dict[str, Any]:
        _, index = _modules()
        m = index.get("athena")
        if m is None:
            return _hold_unknown("athena")
        result = self.run("athena", op, {"days": 16, "caller_ring": 0, "seed": "athena", "score": 1.0})
        return {"version": MYTHOS_VERSION, "self_module": "athena", "organ_map": ATHENA_ORGAN_MAP, "op": op, "result": result,
                "law": "ATHENA_SELF_MODULE != ATHENA_AUTHORITY; the self-map describes the runtime, it does not govern it",
                "authority": "SELF_DESCRIPTION_ONLY", "laws": list(LAWS)}

    # ------------------------------------------------------------ resources
    def read_resource(self, uri: str):
        modules, _ = _modules()
        if uri == MYTHOS_RESOURCE["uri"]:
            errors = validate_modules(modules)
            return {"version": MYTHOS_VERSION, "abi": self.abi, "module_count": len(modules),
                    "modules": [{"id": m["id"], "name": m["name"], "family": m["family"], "standing": m["standing"]} for m in modules],
                    "schema": {"violations": len(errors), "first": errors[:5]}, "athena_organ_map": ATHENA_ORGAN_MAP,
                    "benchmark": benchmark(modules), "docs": "docs/mythos_os/", "spec": "spec/MYTHOS_OS_V1.json",
                    "authority": "UNIFIED_DESCRIPTIVE_KERNEL_ONLY; SIMULATION != EXECUTION; ISOMORPHISM != IDENTITY", "laws": list(LAWS)}
        if uri == MYTHOS_MATRIX_RESOURCE["uri"]:
            return service_matrix(modules)
        if uri == MYTHOS_ATLAS_RESOURCE["uri"]:
            return atlas(modules)
        raise KeyError(uri)

    def benchmark(self) -> Dict[str, Any]:
        modules, _ = _modules()
        return {"mythos": benchmark(modules)}


__all__ = ["MythosSurface", "MYTHOS_TOOLS", "MYTHOS_RESOURCES", "MYTHOS_TOOL_NAMES", "MYTHOS_RESOURCE_URIS", "kernel_abi", "ATHENA_ORGAN_MAP"]
