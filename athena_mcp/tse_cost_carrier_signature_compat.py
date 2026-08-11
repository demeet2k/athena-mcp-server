from __future__ import annotations

import inspect
from typing import Callable

from .rehydration_loop import RehydrationLoopRuntime
from .tse_circulation import TseCirculationRuntime
from .tse_helix_integrity import TseHelixIntegrityRuntime
from .tse_reentry import TseReentryRuntime

SIGNATURE_COMPAT_VERSION = "TSE.COST.CARRIER.SIGNATURE.COMPAT.3"


def _explicit_signature(fn: Callable):
    """Return this callable's own explicit signature, never following wrappers."""
    try:
        sig = inspect.signature(fn, follow_wrapped=False)
    except (TypeError, ValueError):
        return None
    params = list(sig.parameters.values())
    if any(
        param.kind in {inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD}
        for param in params
    ):
        return None
    return sig


def _closure_callables(fn: Callable):
    code = getattr(fn, "__code__", None)
    names = tuple(code.co_freevars or ()) if code is not None else ()
    closure = tuple(getattr(fn, "__closure__", None) or ())
    rows = []
    for name, cell in zip(names, closure):
        try:
            value = cell.cell_contents
        except ValueError:
            continue
        if callable(value):
            priority = 0 if "original" in name or "advance" in name or "start" in name else 1
            rows.append((priority, name, value))
    return [value for _, _, value in sorted(rows, key=lambda row: (row[0], row[1]))]


def _find_explicit_transaction(fn: Callable, seen: set[int] | None = None):
    """Walk wrapper and closure membranes to find an explicit transaction ABI."""
    seen = seen or set()
    identity = id(fn)
    if identity in seen:
        return None
    seen.add(identity)

    sig = _explicit_signature(fn)
    if sig is not None:
        return fn, sig

    wrapped = getattr(fn, "__wrapped__", None)
    if callable(wrapped):
        found = _find_explicit_transaction(wrapped, seen)
        if found is not None:
            return found

    for candidate in _closure_callables(fn):
        found = _find_explicit_transaction(candidate, seen)
        if found is not None:
            return found
    return None


def _rehydration_advance_contract(
    self,
    *,
    loop_id: str,
    expected_checkpoint_head: str,
    expected_state_digest: str,
    expected_prompt_digest: str,
    completion: dict,
    actor: str = "agent",
    allow_no_git_change: bool = False,
    shared_remote_mode: str = "REQUIRED",
    remote: str | None = None,
) -> dict:
    """Pinned ABI witness for the qualified RehydrationLoop V1 advance contract.

    Older successor/terminal wrappers erased Python introspection metadata before
    Cost Carrier existed, even though they continued to delegate this exact
    keyword transaction contract. This function is never executed; it supplies
    an explicit introspection coordinate when no surviving pre-extension wrapper
    retains a recoverable signature.
    """
    raise RuntimeError("signature contract is introspection-only")


PINNED_FALLBACK_SIGNATURES = {
    (RehydrationLoopRuntime, "advance"): inspect.signature(
        _rehydration_advance_contract, follow_wrapped=False
    ),
}


def _restore_signature(cls, method_name: str) -> bool:
    fn = getattr(cls, method_name)
    found = _find_explicit_transaction(fn)
    if found is not None:
        target, sig = found
        fn.__signature__ = sig
        fn.__wrapped__ = target
        fn.__tse_signature_source__ = (
            f"RECOVERED:{target.__module__}.{getattr(target, '__qualname__', target.__name__)}"
        )
        return True

    fallback = PINNED_FALLBACK_SIGNATURES.get((cls, method_name))
    if fallback is None:
        return False
    # Introspection-only fallback: runtime calls still enter the current additive
    # wrapper. The pinned signature is copied from the qualified RehydrationLoop
    # V1 transaction contract and is regression-tested against the MCP surface.
    fn.__signature__ = fallback
    fn.__tse_signature_source__ = "PINNED:ATHENA.REHYDRATION.LOOP.V1.advance"
    return True


def install_tse_cost_carrier_signature_compat() -> None:
    if getattr(RehydrationLoopRuntime, "_athena_tse_cost_carrier_signature_compat_v3_registered", False):
        return

    targets = (
        (RehydrationLoopRuntime, "start"),
        (RehydrationLoopRuntime, "advance"),
        (TseReentryRuntime, "start"),
        (TseHelixIntegrityRuntime, "advance"),
        (TseCirculationRuntime, "observe"),
        (TseCirculationRuntime, "report"),
        (TseCirculationRuntime, "resource"),
    )
    failures = []
    for cls, method_name in targets:
        if not _restore_signature(cls, method_name):
            failures.append(f"{cls.__name__}.{method_name}")

    if failures:
        raise RuntimeError("TSE cost carrier signature restoration failed: " + ",".join(failures))

    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v1_registered = True
    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v2_registered = True
    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v3_registered = True
