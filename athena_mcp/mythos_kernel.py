"""MYTHOS OS kernel — the abstract machine every tradition module runs on.

Three layers, all dependency-free and deterministic:

* ``validate_module``  — the module schema (twelve service slots, graded, sourced).
* ``MythosVM``          — boot / memmap / spawn / tick / invoke / divine / raise / judge / signature.
* ``unify`` / ``atlas`` — cross-module isomorphism classes, strata-lawful bridges, the KC144 atlas.

Nothing here executes a practice, predicts a fact, or equates two traditions.
Every return value carries ``authority`` and ``laws``.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from .mythos_protocol import (
    BOOT_MODES, BOOT_STAGES, CLOCK_INTERCALATION, CODEC_MEDIA, CONST_ROLES, FAMILIES,
    FAULT_CLASSES, FAULT_OUTCOMES, GRADES, LAWS, LEDGER_MODELS, MEMMAP_ADDRESSING,
    MYTHOS_KERNEL_ABI, MYTHOS_VERSION, ORACLE_ENCODING, ORACLE_ENTROPY, PROC_ROLES,
    PROC_SCHEDULERS, REALM_KINDS, RITE_MODES, RITE_OPCODES, SERVICES, STANDINGS,
    USE_CASES,
)

ID_RE = re.compile(r"^[a-z][a-z0-9_]*$")
HIGH_STAKES = {"MEDICAL", "LEGAL", "FINANCIAL", "SAFETY_CRITICAL"}
AUTHORITY = "SYMBOLIC_SIMULATION_ONLY"
_STANDING_RANK = {"UNKNOWN": 0, "MODERN_RECONSTRUCTION": 1, "TRADITION_INTERNAL": 1,
                  "SECONDARY_SCHOLARSHIP": 2, "LIVING_TRADITION_SOURCE": 2, "PRIMARY_EVIDENCE": 3}
_GREEN_OK_STANDING = {"PRIMARY_EVIDENCE", "LIVING_TRADITION_SOURCE", "SECONDARY_SCHOLARSHIP"}


# ====================================================================== schema
def _err(errors: List[str], mid: str, service: str, msg: str) -> None:
    errors.append(f"{mid}.{service}: {msg}")


def _enum(errors, mid, service, value, allowed, label) -> None:
    if value not in allowed:
        _err(errors, mid, service, f"{label} {value!r} not in {sorted(allowed)}")


def _is_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def _is_num(x) -> bool:
    return (isinstance(x, (int, float)) and not isinstance(x, bool))


def validate_module(m: Dict[str, Any]) -> List[str]:
    """Return a list of violations (empty = valid)."""
    errors: List[str] = []
    mid = str(m.get("id", "?"))
    if not ID_RE.match(mid):
        errors.append(f"{mid}: id must match {ID_RE.pattern}")
    for key in ("name", "family", "standing", "sources", "services"):
        if key not in m:
            errors.append(f"{mid}: missing {key}")
    if errors:
        return errors
    if m["family"] not in FAMILIES:
        errors.append(f"{mid}: family {m['family']!r} not in {FAMILIES}")
    if m["standing"] not in STANDINGS:
        errors.append(f"{mid}: standing {m['standing']!r} not in {STANDINGS}")
    if not isinstance(m["sources"], list) or not m["sources"] or not all(isinstance(s, str) and s.strip() for s in m["sources"]):
        errors.append(f"{mid}: sources must be a non-empty list of non-empty strings")
    services = m["services"]
    if not isinstance(services, dict):
        errors.append(f"{mid}: services must be a dict")
        return errors
    for svc in SERVICES:
        if svc not in services:
            errors.append(f"{mid}: missing service {svc}")
    for svc in services:
        if svc not in SERVICES:
            errors.append(f"{mid}: unknown service {svc}")
    for svc in SERVICES:
        slot = services.get(svc)
        if not isinstance(slot, dict):
            continue
        grade = slot.get("grade")
        if grade not in GRADES:
            _err(errors, mid, svc, f"grade {grade!r} not in {GRADES}")
            continue
        if grade == "⊥" or slot.get("absent"):
            if grade != "⊥" or not slot.get("absent"):
                _err(errors, mid, svc, "an absent slot must have grade ⊥ and absent=True")
            content = {k for k in slot if k not in {"grade", "absent", "notes", "src"}}
            if content:
                _err(errors, mid, svc, f"absent slot carries content {sorted(content)}")
            continue
        if grade == "🟢" and m["standing"] not in _GREEN_OK_STANDING and not str(slot.get("src") or "").strip():
            _err(errors, mid, svc, "🟢 requires a primary/living/secondary-sourced module or an explicit src locus")
        _validate_slot(errors, mid, svc, slot)
    return errors


def _validate_slot(errors, mid, svc, slot) -> None:  # noqa: C901 - one branch per service, intentionally flat
    if svc == "BOOT":
        _enum(errors, mid, svc, slot.get("mode"), BOOT_MODES, "mode")
        stages = slot.get("stages")
        if not isinstance(stages, list):
            _err(errors, mid, svc, "stages must be a list"); return
        for st in stages:
            if not isinstance(st, dict) or "stage" not in st or "event" not in st:
                _err(errors, mid, svc, f"stage entry {st!r} needs stage+event"); continue
            _enum(errors, mid, svc, st["stage"], BOOT_STAGES, "stage")
        if slot.get("mode") in {"CREATED", "EMANATED", "CYCLIC"} and not stages:
            _err(errors, mid, svc, f"mode {slot.get('mode')} requires at least one stage")
    elif svc == "MEMMAP":
        _enum(errors, mid, svc, slot.get("addressing"), MEMMAP_ADDRESSING, "addressing")
        realms = slot.get("realms")
        if not isinstance(realms, list) or not realms:
            _err(errors, mid, svc, "realms must be a non-empty list"); return
        for r in realms:
            if not isinstance(r, dict) or "name" not in r or "level" not in r or "kind" not in r:
                _err(errors, mid, svc, f"realm {r!r} needs name+level+kind"); continue
            if not _is_int(r["level"]):
                _err(errors, mid, svc, f"realm {r['name']} level must be int")
            _enum(errors, mid, svc, r["kind"], REALM_KINDS, "realm kind")
    elif svc == "PROC":
        _enum(errors, mid, svc, slot.get("scheduler"), PROC_SCHEDULERS, "scheduler")
        agents = slot.get("agents")
        if not isinstance(agents, list) or not agents:
            _err(errors, mid, svc, "agents must be a non-empty list"); return
        names = set()
        for a in agents:
            if not isinstance(a, dict) or "name" not in a or "roles" not in a:
                _err(errors, mid, svc, f"agent {a!r} needs name+roles"); continue
            if a["name"] in names:
                _err(errors, mid, svc, f"duplicate agent {a['name']}")
            names.add(a["name"])
            if not isinstance(a["roles"], list) or not a["roles"]:
                _err(errors, mid, svc, f"agent {a['name']} roles must be non-empty list")
            else:
                for role in a["roles"]:
                    _enum(errors, mid, svc, role, PROC_ROLES, f"role of {a['name']}")
            if "ring" in a and not _is_int(a["ring"]):
                _err(errors, mid, svc, f"agent {a['name']} ring must be int")
        for a in agents:
            if isinstance(a, dict) and a.get("parent") and a["parent"] not in names:
                _err(errors, mid, svc, f"agent {a.get('name')} parent {a['parent']!r} is not an agent")
    elif svc == "CLOCK":
        periods = slot.get("periods")
        if not isinstance(periods, list) or not periods:
            _err(errors, mid, svc, "periods must be a non-empty list"); return
        for p in periods:
            if not isinstance(p, dict) or "name" not in p or "length" not in p:
                _err(errors, mid, svc, f"period {p!r} needs name+length"); continue
            if not _is_num(p["length"]) or p["length"] <= 0:
                _err(errors, mid, svc, f"period {p['name']} length must be a positive number of days")
        inter = slot.get("intercalation")
        if not isinstance(inter, dict) or "policy" not in inter:
            _err(errors, mid, svc, "intercalation must be a dict with policy"); return
        _enum(errors, mid, svc, inter["policy"], CLOCK_INTERCALATION, "intercalation policy")
        for f in slot.get("festivals") or []:
            if not isinstance(f, dict) or "name" not in f:
                _err(errors, mid, svc, f"festival {f!r} needs name")
            elif "day" in f and not _is_int(f["day"]):
                _err(errors, mid, svc, f"festival {f['name']} day must be int")
    elif svc == "RITE":
        protocols = slot.get("protocols")
        if not isinstance(protocols, list) or not protocols:
            _err(errors, mid, svc, "protocols must be a non-empty list"); return
        for p in protocols:
            if not isinstance(p, dict) or "name" not in p or "steps" not in p:
                _err(errors, mid, svc, f"protocol {p!r} needs name+steps"); continue
            if not isinstance(p["steps"], list) or not p["steps"]:
                _err(errors, mid, svc, f"protocol {p['name']} steps must be non-empty"); continue
            for op in p["steps"]:
                _enum(errors, mid, svc, op, RITE_OPCODES, f"opcode in {p['name']}")
            if "required_ring" in p and not _is_int(p["required_ring"]):
                _err(errors, mid, svc, f"protocol {p['name']} required_ring must be int")
            if "mode" in p:
                _enum(errors, mid, svc, p["mode"], RITE_MODES, f"mode of {p['name']}")
    elif svc == "ORACLE":
        devices = slot.get("devices")
        if not isinstance(devices, list) or not devices:
            _err(errors, mid, svc, "devices must be a non-empty list"); return
        for d in devices:
            if not isinstance(d, dict) or "name" not in d or "entropy" not in d or "space" not in d or "encoding" not in d:
                _err(errors, mid, svc, f"device {d!r} needs name+entropy+space+encoding"); continue
            _enum(errors, mid, svc, d["entropy"], ORACLE_ENTROPY, f"entropy of {d['name']}")
            _enum(errors, mid, svc, d["encoding"], ORACLE_ENCODING, f"encoding of {d['name']}")
            if not _is_int(d["space"]) or d["space"] < 1:
                _err(errors, mid, svc, f"device {d['name']} space must be a positive int")
    elif svc == "FAULT":
        faults = slot.get("faults")
        if not isinstance(faults, list) or not faults:
            _err(errors, mid, svc, "faults must be a non-empty list"); return
        for f in faults:
            if not isinstance(f, dict) or "name" not in f or "class" not in f or "outcome" not in f:
                _err(errors, mid, svc, f"fault {f!r} needs name+class+outcome"); continue
            _enum(errors, mid, svc, f["class"], FAULT_CLASSES, f"class of {f['name']}")
            _enum(errors, mid, svc, f["outcome"], FAULT_OUTCOMES, f"outcome of {f['name']}")
            if "handler" in f and not isinstance(f["handler"], (str, list)):
                _err(errors, mid, svc, f"fault {f['name']} handler must be str or list")
    elif svc == "LEDGER":
        _enum(errors, mid, svc, slot.get("model"), LEDGER_MODELS, "model")
        if "soul" in slot and not isinstance(slot["soul"], list):
            _err(errors, mid, svc, "soul must be a list of component names")
        dests = slot.get("destinations")
        if slot.get("model") not in {"NONE", "UNKNOWN"} and (not isinstance(dests, list) or not dests):
            _err(errors, mid, svc, "destinations must be a non-empty list for a judging ledger")
    elif svc == "RING":
        rings = slot.get("rings")
        if not isinstance(rings, list) or not rings:
            _err(errors, mid, svc, "rings must be a non-empty list"); return
        levels = []
        for r in rings:
            if not isinstance(r, dict) or "level" not in r or "name" not in r:
                _err(errors, mid, svc, f"ring {r!r} needs level+name"); continue
            if not _is_int(r["level"]):
                _err(errors, mid, svc, f"ring {r['name']} level must be int")
            else:
                levels.append(r["level"])
        if len(levels) != len(set(levels)):
            _err(errors, mid, svc, "ring levels must be unique")
    elif svc == "CODEC":
        rec = slot.get("record")
        if not isinstance(rec, dict) or "medium" not in rec:
            _err(errors, mid, svc, "record must be a dict with medium"); return
        _enum(errors, mid, svc, rec["medium"], CODEC_MEDIA, "record medium")
        if "base" in rec and rec["base"] is not None and (not _is_int(rec["base"]) or rec["base"] < 2):
            _err(errors, mid, svc, "record base must be an int >= 2 or null")
    elif svc == "CONST":
        consts = slot.get("constants")
        if not isinstance(consts, list) or not consts:
            _err(errors, mid, svc, "constants must be a non-empty list"); return
        for c in consts:
            if not isinstance(c, dict) or "n" not in c or "role" not in c or "what" not in c:
                _err(errors, mid, svc, f"constant {c!r} needs n+role+what"); continue
            if not _is_int(c["n"]):
                _err(errors, mid, svc, f"constant {c!r} n must be int")
            _enum(errors, mid, svc, c["role"], CONST_ROLES, "constant role")
    elif svc == "LAW":
        inv = slot.get("invariants")
        if not isinstance(inv, list) or not inv:
            _err(errors, mid, svc, "invariants must be a non-empty list")
        canon = slot.get("canon")
        if not isinstance(canon, dict) or "closed" not in canon or not isinstance(canon["closed"], bool):
            _err(errors, mid, svc, "canon must be a dict with boolean closed")
        for entry in slot.get("acl") or []:
            if not isinstance(entry, dict) or "ring" not in entry or "permitted" not in entry:
                _err(errors, mid, svc, f"acl entry {entry!r} needs ring+permitted")


def validate_modules(modules: List[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    seen = set()
    for m in modules:
        errors.extend(validate_module(m))
        mid = m.get("id")
        if mid in seen:
            errors.append(f"{mid}: duplicate module id")
        seen.add(mid)
    return errors


# ====================================================================== VM
def _present(slot: Dict[str, Any]) -> bool:
    return bool(slot) and slot.get("grade") != "⊥" and not slot.get("absent")


def _base(m: Dict[str, Any], op: str, status: str, **kw) -> Dict[str, Any]:
    out = {"version": MYTHOS_VERSION, "abi": MYTHOS_KERNEL_ABI, "module": m["id"], "op": op, "status": status,
           "authority": AUTHORITY, "execution_authority": "NONE", "laws": list(LAWS)}
    out.update(kw)
    return out


class MythosVM:
    """Deterministic interpreter for one module."""

    def __init__(self, module: Dict[str, Any]):
        self.m = module
        self.s = module["services"]

    # ---------------------------------------------------------------- BOOT
    def boot(self) -> Dict[str, Any]:
        slot = self.s["BOOT"]
        if not _present(slot):
            return _base(self.m, "boot", "SERVICE_ABSENT", grade="⊥")
        mode = slot["mode"]
        log = []
        reached = []
        for i, st in enumerate(slot["stages"], start=1):
            log.append({"pc": i, "stage": st["stage"], "event": st["event"], "src": st.get("src")})
            reached.append(st["stage"])
        pop = reached.index("POPULATION") if "POPULATION" in reached else None
        fault = reached.index("FAULT") if "FAULT" in reached else None
        if fault is None:
            fault_position = "NONE"
        elif pop is None or fault < pop:
            fault_position = "PRE_POPULATION"
        else:
            fault_position = "POST_POPULATION"
        if mode == "ETERNAL":
            status = "ETERNAL_NO_INIT" if not reached else "ETERNAL_WITH_PHASES"
        elif "POPULATION" in reached or mode == "CYCLIC":
            status = "BOOTED"
        else:
            status = "BOOT_INCOMPLETE"
        return _base(self.m, "boot", status, grade=slot["grade"], mode=mode, log=log,
                     stages_reached=reached, first_stage=reached[0] if reached else None,
                     fault_position=fault_position, reboots=reached.count("REBOOT"),
                     halted_at_maintenance=bool(reached) and reached[-1] == "MAINTENANCE",
                     notes=slot.get("notes"), law="BOOT_LOG != COSMOLOGICAL_CLAIM")

    # ---------------------------------------------------------------- MEMMAP
    def memmap(self) -> Dict[str, Any]:
        slot = self.s["MEMMAP"]
        if not _present(slot):
            return _base(self.m, "memmap", "SERVICE_ABSENT", grade="⊥")
        realms = sorted(slot["realms"], key=lambda r: (-r["level"], r["name"]))
        levels = [r["level"] for r in realms]
        table = [{"address": i, "name": r["name"], "level": r["level"], "kind": r["kind"], "note": r.get("note")}
                 for i, r in enumerate(realms)]
        kinds = Counter(r["kind"] for r in realms)
        return _base(self.m, "memmap", "MAPPED", grade=slot["grade"], addressing=slot["addressing"],
                     axis=slot.get("axis"), realm_count=len(realms), depth=(max(levels) - min(levels) + 1) if levels else 0,
                     top=max(levels) if levels else None, bottom=min(levels) if levels else None,
                     by_kind=dict(sorted(kinds.items())), table=table, notes=slot.get("notes"))

    # ---------------------------------------------------------------- PROC
    def spawn(self) -> Dict[str, Any]:
        slot = self.s["PROC"]
        if not _present(slot):
            return _base(self.m, "spawn", "SERVICE_ABSENT", grade="⊥")
        agents = slot["agents"]
        pid = {a["name"]: i + 1 for i, a in enumerate(agents)}
        table = []
        for a in agents:
            table.append({"pid": pid[a["name"]], "name": a["name"], "roles": list(a["roles"]),
                          "domain": list(a.get("domain") or []), "ring": a.get("ring"),
                          "ppid": pid.get(a.get("parent")) if a.get("parent") else 0, "parent": a.get("parent")})
        roots = [t["name"] for t in table if t["ppid"] == 0]
        roles = Counter(role for a in agents for role in a["roles"])
        crossing = self._closure_crossings()
        return _base(self.m, "spawn", "SPAWNED", grade=slot["grade"], scheduler=slot["scheduler"],
                     process_count=len(table), roots=roots, root_count=len(roots),
                     role_histogram=dict(sorted(roles.items())), table=table,
                     closure_crossings=crossing, notes=slot.get("notes"))

    def _closure_crossings(self) -> List[Dict[str, Any]]:
        cid = self.m.get("closure_grammar_id")
        if not cid:
            return []
        try:
            from .closure_grammar_registry import TRADITIONS
        except Exception:  # pragma: no cover - registry optional
            return []
        for t in TRADITIONS:
            if t.get("id") == cid:
                return [{"n": x.get("n"), "cross": x.get("cross"), "seat": x.get("seat"), "what": x.get("what"), "grade": x.get("grade")}
                        for x in t.get("crossings", [])]
        return []

    # ---------------------------------------------------------------- CLOCK
    def tick(self, days: int) -> Dict[str, Any]:
        slot = self.s["CLOCK"]
        if not _present(slot):
            return _base(self.m, "tick", "SERVICE_ABSENT", grade="⊥")
        days = int(days)
        periods = []
        for p in slot["periods"]:
            length = float(p["length"])
            rollovers = int(days // length)
            phase = days - rollovers * length
            periods.append({"name": p["name"], "length_days": length, "rollovers": rollovers,
                            "phase_days": round(phase, 6), "phase_fraction": round(phase / length, 6) if length else None})
        inter = slot["intercalation"]
        residue = None
        intercalations_due = None
        base_year = next((p for p in slot["periods"] if p.get("role") == "year"), None)
        if base_year is not None:
            years = int(days // float(base_year["length"]))
            if inter["policy"] == "EPAGOMENAL" and _is_num(inter.get("residue_days")):
                residue = round(years * float(inter["residue_days"]), 6)
            if _is_num(inter.get("every_years")) and inter["every_years"] > 0:
                intercalations_due = int(years // float(inter["every_years"])) * int(inter.get("add", 1))
            if inter["policy"] == "LUNISOLAR_MONTH" and _is_num(inter.get("months_per_cycle")) and _is_num(inter.get("cycle_years")) and inter["cycle_years"] > 0:
                intercalations_due = int(years // float(inter["cycle_years"])) * int(inter["months_per_cycle"])
        fired = []
        for f in slot.get("festivals") or []:
            if _is_int(f.get("day")) and base_year is not None:
                ylen = float(base_year["length"])
                count = int((days - f["day"]) // ylen) + 1 if days >= f["day"] else 0
                fired.append({"name": f["name"], "day_of_year": f["day"], "fired": max(count, 0), "when": f.get("when")})
            else:
                fired.append({"name": f["name"], "when": f.get("when"), "fired": None, "note": "no fixed day; not scheduled"})
        return _base(self.m, "tick", "TICKED", grade=slot["grade"], days=days, periods=periods,
                     intercalation={"policy": inter["policy"], "rule": inter.get("rule"), "intercalations_due": intercalations_due,
                                    "accumulated_residue_days": residue},
                     epochs=list(slot.get("epochs") or []), festivals=fired, notes=slot.get("notes"))

    # ---------------------------------------------------------------- RITE
    def invoke(self, rite: Optional[str], caller_ring: int = 99, purity: bool = True, witness: Any = None,
               use_case: str = "GENERAL") -> Dict[str, Any]:
        slot = self.s["RITE"]
        if not _present(slot):
            return _base(self.m, "invoke", "SERVICE_ABSENT", grade="⊥")
        protocols = slot["protocols"]
        proto = next((p for p in protocols if p["name"] == rite), None) if rite else protocols[0]
        if proto is None:
            return _base(self.m, "invoke", "HOLD_UNKNOWN_RITE", rite=rite, available=[p["name"] for p in protocols])
        if str(use_case).upper() in HIGH_STAKES:
            return _base(self.m, "invoke", "HOLD_SAFETY_CRITICAL_USE", rite=proto["name"], use_case=use_case,
                         law="RITE_SIMULATION != MEDICAL_LEGAL_FINANCIAL_OR_SAFETY_ACTION")
        lint = lint_steps(proto["steps"])
        required = proto.get("required_ring")
        if _is_int(required) and caller_ring > required:
            return _base(self.m, "invoke", "HOLD_RING", rite=proto["name"], required_ring=required, caller_ring=caller_ring,
                         lint=lint, law="RING_GATE_BEFORE_INVOKE")
        if proto.get("requires_purity", True) and not purity and "PURIFY" not in proto["steps"]:
            return _base(self.m, "invoke", "HOLD_PURITY", rite=proto["name"], lint=lint, law="PURITY_PRECONDITION_UNMET")
        trace = ["CLOSED", "BOUNDARY_CHECKED", "PHASE_READY"]
        trace.extend(f"PC:{i + 1}:{op}" for i, op in enumerate(proto["steps"]))
        trace.append("WITNESSED" if witness is not None else "AWAITING_WITNESS")
        trace.append("CLOSED")
        status = "SIMULATED_RITE" if lint["well_formed"] else "SIMULATED_RITE_MALFORMED"
        return _base(self.m, "invoke", status, grade=slot["grade"], rite=proto["name"], mode=proto.get("mode", "TRANSFORMING"),
                     required_ring=required, caller_ring=caller_ring, steps=list(proto["steps"]), lint=lint,
                     cost=proto.get("cost"), claimed_effect=proto.get("effect"), state_trace=trace, witness=deepcopy(witness),
                     B_Theta_Pi_separation=True, src=proto.get("src"), law="SIMULATION != EXECUTION; CLAIMED_EFFECT != OBSERVED_EFFECT")

    # ---------------------------------------------------------------- ORACLE
    def divine(self, device: Optional[str] = None, seed: Optional[str] = None, sample: Optional[int] = None,
               use_case: str = "GENERAL") -> Dict[str, Any]:
        slot = self.s["ORACLE"]
        if not _present(slot):
            return _base(self.m, "divine", "SERVICE_ABSENT", grade="⊥")
        devices = slot["devices"]
        dev = next((d for d in devices if d["name"] == device), None) if device else devices[0]
        if dev is None:
            return _base(self.m, "divine", "HOLD_UNKNOWN_DEVICE", device=device, available=[d["name"] for d in devices])
        if str(use_case).upper() in HIGH_STAKES:
            return _base(self.m, "divine", "HOLD_SAFETY_CRITICAL_USE", device=dev["name"], use_case=use_case,
                         law="DIVINATORY_OUTPUT != MEDICAL_LEGAL_FINANCIAL_OR_SAFETY_EVIDENCE")
        if dev["entropy"] == "NONE":
            return _base(self.m, "divine", "NO_ENTROPY_SOURCE", device=dev["name"], grade=slot["grade"],
                         note="the tradition names no sampling device; nothing is drawn")
        if sample is None and seed is None:
            return _base(self.m, "divine", "HOLD_SAMPLE_REQUIRED", device=dev["name"], law="DECODER != ENTROPY_SOURCE")
        space = int(dev["space"])
        if sample is None:
            raw = int(hashlib.sha256(f"{seed}|{self.m['id']}|{dev['name']}".encode("utf-8")).hexdigest(), 16)
            mode = "DETERMINISTIC_SEEDED_HASH"
        else:
            raw = int(sample)
            mode = "CALLER_SUPPLIED_INTEGER"
        index = raw % space
        return _base(self.m, "divine", "SYMBOLIC_ONLY", grade=slot["grade"], device=dev["name"], entropy=dev["entropy"],
                     encoding=dev["encoding"], sample_space=space, entropy_bits=round(math.log2(space), 6) if space > 1 else 0.0,
                     R_sampler={"mode": mode, "raw": raw, "index": index}, W_witness=encode_index(index, space, dev["encoding"]),
                     D_decoder={"name": dev.get("decoder"), "set_aside": dev.get("set_aside"), "output_alphabet": dev.get("alphabet")},
                     U_update={"decision_authority": "NONE", "permitted_use": "REFLECTION_OR_CREATIVE_HYPOTHESIS_ONLY"},
                     src=dev.get("src"), law="R != W != D != INTERPRETATION; DIVINATORY_OUTPUT != FACT")

    # ---------------------------------------------------------------- FAULT
    def raise_fault(self, fault: Optional[str] = None) -> Dict[str, Any]:
        slot = self.s["FAULT"]
        if not _present(slot):
            return _base(self.m, "raise", "SERVICE_ABSENT", grade="⊥")
        faults = slot["faults"]
        f = next((x for x in faults if x["name"] == fault), None) if fault else faults[0]
        if f is None:
            return _base(self.m, "raise", "HOLD_UNKNOWN_FAULT", fault=fault, available=[x["name"] for x in faults])
        handler = f.get("handler")
        chain = handler if isinstance(handler, list) else ([handler] if handler else [])
        trace = [f"RAISE:{f['class']}:{f['name']}"]
        trace.extend(f"HANDLER:{i + 1}:{h}" for i, h in enumerate(chain))
        trace.append(f"OUTCOME:{f['outcome']}")
        reboot = None
        if f["outcome"] == "REBOOT" and _present(self.s["BOOT"]):
            reboot = [st["event"] for st in self.s["BOOT"]["stages"] if st["stage"] == "REBOOT"] or None
        return _base(self.m, "raise", "HANDLED" if chain else "UNHANDLED", grade=slot["grade"], fault=f["name"],
                     fault_class=f["class"], handler_chain=chain, outcome=f["outcome"], recoverable=f["outcome"] in {"RECOVERED", "TRANSFERRED"},
                     reboot_event=reboot, trace=trace, src=f.get("src"), law="FAULT_MODEL != MORAL_TRUTH")

    # ---------------------------------------------------------------- LEDGER
    def judge(self, score: float = 0.0) -> Dict[str, Any]:
        slot = self.s["LEDGER"]
        if not _present(slot):
            return _base(self.m, "judge", "SERVICE_ABSENT", grade="⊥")
        model = slot["model"]
        dests = list(slot.get("destinations") or [])
        score = max(-1.0, min(1.0, float(score)))
        destination = None
        carry = None
        if model in {"NONE", "UNKNOWN"}:
            destination = dests[0] if dests else None
        elif model == "BINARY":
            destination = dests[0] if score >= 0 else dests[-1]
        elif model == "BALANCE":
            destination = dests[0] if score >= 0 else dests[-1]
        elif model in {"COUNTER", "TIERED", "CYCLIC"}:
            # map score in [-1,1] onto the destination list, best first
            n = len(dests)
            idx = int(round((1 - score) / 2 * (n - 1))) if n > 1 else 0
            destination = dests[idx] if dests else None
            if model == "CYCLIC":
                carry = round(score, 6)
        elif model == "ANCESTRAL":
            destination = dests[0] if score >= 0 else (dests[-1] if len(dests) > 1 else None)
        return _base(self.m, "judge", "JUDGED", grade=slot["grade"], model=model, score=score, destination=destination,
                     carry=carry, destinations=dests, soul=list(slot.get("soul") or []), judgment=slot.get("judgment"),
                     judge=slot.get("judge"), src=slot.get("src"), law="LEDGER_MODEL != MORAL_TRUTH; DESTINATION != PREDICTION")

    # ---------------------------------------------------------------- signature
    def signature(self) -> Dict[str, str]:
        return signature_of(self.m)

    def run_all(self) -> Dict[str, Any]:
        return {"boot": self.boot(), "memmap": self.memmap(), "spawn": self.spawn(), "tick": self.tick(365),
                "invoke": self.invoke(None, caller_ring=0), "divine": self.divine(None, seed="athena"),
                "raise": self.raise_fault(None), "judge": self.judge(0.0), "signature": self.signature()}


# ====================================================================== helpers
def lint_steps(steps: List[str]) -> Dict[str, Any]:
    """Protocol well-formedness over the opcode alphabet.

    Rules: PURIFY and BOUND (if present) precede INVOKE; RELEASE/CLOSE (if present) come after every
    INVOKE/OFFER/PETITION/RECEIVE; a protocol that INVOKEs must eventually CLOSE or RELEASE.
    """
    violations = []
    pos = {op: i for i, op in reversed(list(enumerate(steps)))}  # first occurrence
    last = {op: i for i, op in enumerate(steps)}  # last occurrence
    if "INVOKE" in pos:
        for pre in ("PURIFY", "BOUND"):
            if pre in pos and pos[pre] > pos["INVOKE"]:
                violations.append(f"{pre} after INVOKE")
        if "CLOSE" not in pos and "RELEASE" not in pos:
            violations.append("INVOKE without CLOSE/RELEASE")
    for post in ("RELEASE", "CLOSE"):
        if post in last:
            for body in ("INVOKE", "OFFER", "PETITION", "RECEIVE"):
                if body in last and last[body] > last[post]:
                    violations.append(f"{body} after {post}")
    return {"well_formed": not violations, "violations": violations,
            "has_boundary": "BOUND" in pos, "has_purification": "PURIFY" in pos, "has_closure": "CLOSE" in pos or "RELEASE" in pos,
            "opcode_count": len(steps), "distinct_opcodes": len(set(steps))}


def encode_index(index: int, space: int, encoding: str) -> Dict[str, Any]:
    if space <= 1:
        return {"index": index, "digits": "", "radix": None}
    radix = {"BINARY": 2, "TERNARY": 3, "QUATERNARY": 4}.get(encoding)
    if radix is None:
        width = 1
        return {"index": index, "digits": str(index), "radix": space if encoding == "N_ARY" else None, "width": width}
    width = int(math.ceil(math.log(space, radix) - 1e-12))
    n = index
    digits = []
    for _ in range(max(width, 1)):
        digits.append(str(n % radix))
        n //= radix
    return {"index": index, "digits": "".join(reversed(digits)), "radix": radix, "width": max(width, 1)}


def signature_of(m: Dict[str, Any]) -> Dict[str, str]:
    """Twelve pattern tokens, one per service; ⊥ for an absent slot."""
    s = m["services"]
    sig: Dict[str, str] = {}
    b = s["BOOT"]
    if _present(b):
        stages = [st["stage"] for st in b["stages"]]
        pop = stages.index("POPULATION") if "POPULATION" in stages else None
        fault = stages.index("FAULT") if "FAULT" in stages else None
        fp = "NOFAULT" if fault is None else ("FAULT<POP" if pop is None or fault < pop else "FAULT>POP")
        sig["BOOT"] = f"{b['mode']}:{stages[0] if stages else 'NONE'}:{fp}:{'REBOOT' if 'REBOOT' in stages else 'STABLE'}"
    else:
        sig["BOOT"] = "⊥"
    mm = s["MEMMAP"]
    if _present(mm):
        levels = [r["level"] for r in mm["realms"]]
        sig["MEMMAP"] = f"{mm['addressing']}:depth{max(levels) - min(levels) + 1}:{len(mm['realms'])}realms"
    else:
        sig["MEMMAP"] = "⊥"
    pr = s["PROC"]
    if _present(pr):
        roots = sum(1 for a in pr["agents"] if not a.get("parent"))
        sig["PROC"] = f"{pr['scheduler']}:{len(pr['agents'])}agents:{roots}roots"
    else:
        sig["PROC"] = "⊥"
    ck = s["CLOCK"]
    sig["CLOCK"] = f"{ck['intercalation']['policy']}:{len(ck['periods'])}periods" if _present(ck) else "⊥"
    rt = s["RITE"]
    if _present(rt):
        first = rt["protocols"][0]
        l = lint_steps(first["steps"])
        sig["RITE"] = f"{'B' if l['has_boundary'] else '-'}{'P' if l['has_purification'] else '-'}I{'C' if l['has_closure'] else '-'}:{len(rt['protocols'])}protocols"
    else:
        sig["RITE"] = "⊥"
    orc = s["ORACLE"]
    if _present(orc):
        d = orc["devices"][0]
        sig["ORACLE"] = f"{d['entropy']}:{d['encoding']}:{d['space']}"
    else:
        sig["ORACLE"] = "⊥"
    ft = s["FAULT"]
    if _present(ft):
        cls = Counter(f["class"] for f in ft["faults"]).most_common(1)[0][0]
        outs = Counter(f["outcome"] for f in ft["faults"]).most_common(1)[0][0]
        sig["FAULT"] = f"{cls}:{outs}"
    else:
        sig["FAULT"] = "⊥"
    lg = s["LEDGER"]
    sig["LEDGER"] = f"{lg['model']}:{len(lg.get('destinations') or [])}dest" if _present(lg) else "⊥"
    rg = s["RING"]
    sig["RING"] = f"{len(rg['rings'])}rings" if _present(rg) else "⊥"
    cd = s["CODEC"]
    sig["CODEC"] = f"{cd['record']['medium']}:base{cd['record'].get('base') or '-'}" if _present(cd) else "⊥"
    cn = s["CONST"]
    if _present(cn):
        closure = next((c["n"] for c in cn["constants"] if c["role"] == "closure"), None)
        crossing = next((c["n"] for c in cn["constants"] if c["role"] == "crossing"), None)
        sig["CONST"] = f"close{closure if closure is not None else '-'}:cross{crossing if crossing is not None else '-'}"
    else:
        sig["CONST"] = "⊥"
    lw = s["LAW"]
    sig["LAW"] = f"{'CLOSED' if lw['canon']['closed'] else 'OPEN'}:{len(lw['invariants'])}inv" if _present(lw) else "⊥"
    return sig


# ====================================================================== unification
def service_matrix(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    for m in modules:
        rows.append({"id": m["id"], "name": m["name"], "family": m["family"], "standing": m["standing"],
                     "grades": {svc: m["services"][svc]["grade"] for svc in SERVICES}, "signature": signature_of(m)})
    return {"version": MYTHOS_VERSION, "abi": MYTHOS_KERNEL_ABI, "services": list(SERVICES), "module_count": len(rows), "rows": rows}


def isomorphism_classes(modules: List[Dict[str, Any]], service: str) -> List[Dict[str, Any]]:
    groups: Dict[str, List[str]] = {}
    for m in modules:
        groups.setdefault(signature_of(m)[service], []).append(m["id"])
    out = [{"signature": k, "size": len(v), "modules": sorted(v)} for k, v in groups.items()]
    out.sort(key=lambda g: (-g["size"], g["signature"]))
    return out


def compare_modules(left: Dict[str, Any], right: Dict[str, Any], services: Optional[List[str]] = None) -> Dict[str, Any]:
    services = list(services or SERVICES)
    ls, rs = signature_of(left), signature_of(right)
    per = {}
    shared = 0
    for svc in services:
        same = ls[svc] == rs[svc] and ls[svc] != "⊥"
        shared += int(same)
        lslot, rslot = left["services"][svc], right["services"][svc]
        lk = set(lslot) - {"grade", "notes", "src", "absent"}
        rk = set(rslot) - {"grade", "notes", "src", "absent"}
        per[svc] = {"left": ls[svc], "right": rs[svc], "isomorphic": same,
                    "grades": [lslot["grade"], rslot["grade"]],
                    "fields_only_left": sorted(lk - rk), "fields_only_right": sorted(rk - lk)}
    return {"version": MYTHOS_VERSION, "left": left["id"], "right": right["id"], "services": services,
            "isomorphic_services": shared, "of": len(services), "per_service": per,
            "identity_equivalence": False, "semantic_equivalence": False,
            "authority": "STRUCTURAL_DIFF_ONLY", "law": "STRUCTURAL_ISOMORPHISM != CULTURAL_IDENTITY", "laws": list(LAWS)}


def _layer(m: Dict[str, Any]) -> Dict[str, Any]:
    native = m["family"] in {"AFRICA_DIASPORA", "AMERICAS", "OCEANIA", "INDIA", "EAST_ASIA", "NEAR_EAST", "NORTH_EUROPE", "ABRAHAMIC", "MEDITERRANEAN"}
    return {"layer_id": f"mythos.{m['id']}", "standing": m["standing"], "category_scope": "NATIVE" if native else "COMPOSITE",
            "corpus_mutability": "CLOSED" if m["services"]["LAW"].get("canon", {}).get("closed") else "LAYERED",
            "authorization_scope": "PUBLIC"}


def bridge(left: Dict[str, Any], right: Dict[str, Any], service: Optional[str] = None) -> Dict[str, Any]:
    """Compile a strata-lawful bridge between two modules for one service (or the whole signature)."""
    from .mythic_strata_runtime import MythicStrataRuntime
    ls, rs = signature_of(left), signature_of(right)
    svcs = [service] if service else list(SERVICES)
    invariants = [f"{s}:{ls[s]}" for s in svcs if ls[s] == rs[s] and ls[s] != "⊥"]
    loss = [f"{s}: {ls[s]} vs {rs[s]}" for s in svcs if ls[s] != rs[s]]
    loss.append("pattern tokens are structural; names, meanings, authority and practice are not transported")
    standing = min((left["standing"], right["standing"]), key=lambda s: _STANDING_RANK.get(s, 0))
    explicit = {"source_ref": f"mythos://{left['id']}+{right['id']}", "evidence_standing": standing,
                "invariants": invariants or ["no shared pattern token on the selected service(s)"],
                "transform_loss": loss, "authority": "STRUCTURAL_MAPPING"}
    verdict = MythicStrataRuntime().transport(_layer(left), _layer(right), "SEMANTIC_TRANSPORT", "NONE", "", explicit)
    return {"version": MYTHOS_VERSION, "left": left["id"], "right": right["id"], "service": service or "ALL",
            "shared_tokens": invariants, "differing_tokens": [x for x in loss[:-1]], "strata": verdict,
            "identity_equivalence": False, "authority": "BRIDGE_WITH_LOSS_ONLY", "laws": list(LAWS)}


def unify(modules: List[Dict[str, Any]], service: Optional[str] = None, left: Optional[str] = None, right: Optional[str] = None) -> Dict[str, Any]:
    svcs = [service] if service else list(SERVICES)
    classes = {svc: isomorphism_classes(modules, svc) for svc in svcs}
    out = {"version": MYTHOS_VERSION, "abi": MYTHOS_KERNEL_ABI, "module_count": len(modules), "services": svcs,
           "classes": classes, "largest_class": {svc: (classes[svc][0] if classes[svc] else None) for svc in svcs},
           "authority": "STRUCTURAL_CLASSIFICATION_ONLY", "law": "STRUCTURAL_ISOMORPHISM != CULTURAL_IDENTITY", "laws": list(LAWS)}
    if left and right:
        by = {m["id"]: m for m in modules}
        if left in by and right in by:
            out["bridge"] = bridge(by[left], by[right], service)
        else:
            out["bridge"] = {"status": "HOLD_UNKNOWN_MODULE", "missing": [x for x in (left, right) if x not in by]}
    return out


def atlas(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """KC144 atlas: rows = twelve families, columns = twelve services, gid = 12*(row-1)+col."""
    cells = []
    by_family: Dict[str, List[Dict[str, Any]]] = {f: [] for f in FAMILIES}
    for m in modules:
        by_family[m["family"]].append(m)
    for ri, fam in enumerate(FAMILIES, start=1):
        for ci, svc in enumerate(SERVICES, start=1):
            gid = 12 * (ri - 1) + ci
            mods = by_family[fam]
            tokens = Counter(signature_of(m)[svc] for m in mods)
            grades = Counter(m["services"][svc]["grade"] for m in mods)
            cells.append({"gid": gid, "sid": f"KC144.SID.{gid:03d}", "row": ri, "col": ci, "family": fam, "service": svc,
                          "modules": [m["id"] for m in mods], "module_count": len(mods),
                          "patterns": dict(sorted(tokens.items())), "grades": dict(sorted(grades.items()))})
    return {"version": MYTHOS_VERSION, "topology": "12x12", "count": len(cells), "law": "gid = 12*(row-1)+column",
            "rows": list(FAMILIES), "columns": list(SERVICES), "cells": cells,
            "boundary": "cells are occupancy/pattern histograms of the module registry; an empty cell is UNKNOWN, not N/A"}


def benchmark(modules: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministic synthetic regression: schema, VM gates, high-stakes holds, strata bridge behaviour."""
    errors = validate_modules(modules)
    by = {m["id"]: m for m in modules}
    probe = modules[0] if modules else None
    gates = {}
    if probe is not None:
        vm = MythosVM(probe)
        gates["ring_gate_holds"] = vm.invoke(None, caller_ring=99).get("status") in {"HOLD_RING", "SIMULATED_RITE", "SIMULATED_RITE_MALFORMED", "SERVICE_ABSENT"}
        gates["high_stakes_rite_holds"] = vm.invoke(None, caller_ring=0, use_case="MEDICAL").get("status") in {"HOLD_SAFETY_CRITICAL_USE", "SERVICE_ABSENT"}
        gates["high_stakes_oracle_holds"] = vm.divine(None, seed="x", use_case="LEGAL").get("status") in {"HOLD_SAFETY_CRITICAL_USE", "SERVICE_ABSENT"}
        gates["oracle_requires_sample"] = vm.divine(None).get("status") in {"HOLD_SAMPLE_REQUIRED", "NO_ENTROPY_SOURCE", "SERVICE_ABSENT"}
        gates["oracle_deterministic"] = vm.divine(None, seed="s") == vm.divine(None, seed="s")
        gates["unknown_rite_holds"] = vm.invoke("__no_such_rite__", caller_ring=0).get("status") in {"HOLD_UNKNOWN_RITE", "SERVICE_ABSENT"}
    malformed = lint_steps(["INVOKE", "BOUND", "CLOSE", "OFFER"])
    wellformed = lint_steps(["PURIFY", "BOUND", "INVOKE", "OFFER", "RECEIVE", "CLOSE"])
    strata = None
    if len(modules) >= 2:
        strata = bridge(modules[0], modules[1])["strata"]["status"]
    return {"mythos_version": MYTHOS_VERSION, "benchmark_kind": "DETERMINISTIC_SYNTHETIC_REGRESSION_NOT_CULTURAL_VALIDATION",
            "module_count": len(modules), "schema_violations": len(errors), "schema_pass": not errors,
            "gate_checks": gates, "gates_passed": sum(1 for v in gates.values() if v), "gate_count": len(gates),
            "lint_rejects_malformed": not malformed["well_formed"], "lint_accepts_wellformed": wellformed["well_formed"],
            "bridge_status_for_first_pair": strata, "no_identity_equivalence": True,
            "laws": ["SYNTHETIC_REGRESSION_PASS != GENERAL_EFFECTIVENESS", "SELF_GENERATED_BENCHMARK != INDEPENDENT_EVIDENCE"] + list(LAWS)}
