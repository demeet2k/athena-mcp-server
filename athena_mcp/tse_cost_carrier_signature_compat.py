from __future__ import annotations

import inspect
from typing import Callable

from .rehydration_loop import RehydrationLoopRuntime
from .tse_circulation import TseCirculationRuntime
from .tse_helix_integrity import TseHelixIntegrityRuntime
from .tse_reentry import TseReentryRuntime

SIGNATURE_COMPAT_VERSION = "TSE.COST.CARRIER.SIGNATURE.COMPAT.2"


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
            # Prefer transaction lineage cells over helpers when traversing a
            # wrapper graph, but preserve deterministic fallback order.
            priority = 0 if "original" in name or "advance" in name or "start" in name else 1
            rows.append((priority, name, value))
    return [value for _, _, value in sorted(rows, key=lambda row: (row[0], row[1]))]


def _find_explicit_transaction(fn: Callable, seen: set[int] | None = None):
    """Walk a wrapper/closure graph until a real transaction signature is found.

    ATHENA's older continuation extensions predate functools.wraps and therefore
    form several nested generic *args/**kwargs membranes. A one-hop __wrapped__
    assignment is insufficient for `advance`: the captured callable can itself
    be generic. This walker follows both explicit __wrapped__ links and callable
    closure cells, with cycle protection, until it reaches the underlying typed
    transaction function.
    """
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


def _restore_signature(fn: Callable) -> bool:
    found = _find_explicit_transaction(fn)
    if found is None:
        return False
    target, sig = found
    # __signature__ is an introspection coordinate only; runtime execution stays
    # on the additive Cost Carrier wrapper. Preserve the deepest explicit source
    # callable as provenance without routing calls around the wrapper.
    fn.__signature__ = sig
    fn.__wrapped__ = target
    fn.__tse_signature_source__ = f"{target.__module__}.{getattr(target, '__qualname__', target.__name__)}"
    return True


def install_tse_cost_carrier_signature_compat() -> None:
    if getattr(RehydrationLoopRuntime, "_athena_tse_cost_carrier_signature_compat_v2_registered", False):
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
        fn = getattr(cls, method_name)
        if not _restore_signature(fn):
            failures.append(f"{cls.__name__}.{method_name}")

    if failures:
        raise RuntimeError("TSE cost carrier signature restoration failed: " + ",".join(failures))

    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v1_registered = True
    RehydrationLoopRuntime._athena_tse_cost_carrier_signature_compat_v2_registered = True
