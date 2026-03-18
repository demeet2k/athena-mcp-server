# CRYSTAL: Xi108:W3:A12:S36 | face=R | node=666 | depth=0 | phase=Fixed
# METRO: Su,Me,Sa
# BRIDGES: ALL

"""
Quantum Crystal Computing
==========================
Provides the quantum crystal computing framework:
  - QueryState (Q) — four-tuple (A, U, C_Σ, H)
  - DesireField D_Q = I(Q, X) — mutual information as attraction
  - ResonanceMetric R(X) — five-component quality measure
  - CommitWitness θ(X) — four gates (resonance ≥ τ, boundary, crossview, scale)
  - Desire Compiler — 6-stage pipeline U → (Θ_U, G_U)
  - Resonance Scheduler — budget allocation across S/F/C/R workers
  - Resonance Kernel — 4 worker contracts with shared state
  - Crystal Search Law — X* = argmin A(Q,X) s.t. constraints
  - Runtime Loop — tick/commit/rotate cycle
"""

from ._cache import JsonCache

_QC = JsonCache("quantum_crystal.json")


def query_quantum_crystal(component: str = "all") -> str:
    """
    Query the quantum crystal computing framework.

    Components:
      - all              : Full overview of the quantum crystal computing model
      - query_state      : QueryState Q = (A, U, C_Σ, H) — the four-tuple
      - desire_field     : DesireField D_Q = I(Q, X) — mutual information attraction
      - resonance        : ResonanceMetric R(X) — five-component quality measure
      - commit           : CommitWitness θ(X) — four commit gates
      - compiler         : Desire Compiler — 6-stage pipeline from U to (Θ_U, G_U)
      - scheduler        : Resonance Scheduler — S/F/C/R budget allocation
      - kernel           : Resonance Kernel — 4 workers with shared state
      - search           : Crystal Search Law — X* = argmin A(Q,X)
      - runtime          : Runtime Loop — tick/commit/rotate cycle
    """
    data = _QC.load()
    comp = component.strip().lower()

    dispatch = {
        "all": _format_all,
        "query_state": _format_query_state,
        "desire_field": _format_desire_field,
        "resonance": _format_resonance,
        "commit": _format_commit,
        "compiler": _format_compiler,
        "scheduler": _format_scheduler,
        "kernel": _format_kernel,
        "search": _format_search,
        "runtime": _format_runtime,
    }

    fn = dispatch.get(comp)
    if fn:
        return fn(data)
    return (
        f"Unknown component '{component}'. Use: "
        + ", ".join(dispatch.keys())
    )


def _format_all(data: dict) -> str:
    meta = data.get("meta", {})
    qs = data.get("query_state", {})
    df = data.get("desire_field", {})
    rm = data.get("resonance_metric", {})
    cw = data.get("commit_witness", {})
    dc = data.get("desire_compiler", {})
    rs = data.get("resonance_scheduler", {})
    rk = data.get("resonance_kernel", {})
    csl = data.get("crystal_search_law", {})
    rl = data.get("runtime_loop", {})
    lines = [
        "## Quantum Crystal Computing\n",
        f"**Title**: {meta.get('title', 'Quantum Crystal Computing')}",
        f"**Description**: {meta.get('description', '')}\n",
        f"### Core Objects",
        f"- **QueryState** `{qs.get('symbol', 'Q')}`: {qs.get('definition', '')}",
        f"- **DesireField** `{df.get('symbol', 'D_Q')}`: {df.get('definition', '')}",
        f"- **ResonanceMetric** `{rm.get('symbol', 'R')}`: {rm.get('definition', '')}",
        f"- **CommitWitness** `{cw.get('symbol', 'θ')}`: {cw.get('definition', '')}\n",
        f"### Architecture",
        f"- **Desire Compiler**: `{dc.get('signature', 'U → (Θ_U, G_U)')}`",
        f"- **Scheduler**: choice law = `{rs.get('choice_law', '')}`",
        f"- **Kernel**: {rk.get('definition', '')}",
        f"- **Search Law**: `{csl.get('equation', '')}`",
        f"- **Runtime**: {rl.get('name', 'tick/commit/rotate')}",
    ]
    return "\n".join(lines)


def _format_query_state(data: dict) -> str:
    qs = data.get("query_state", {})
    lines = [
        f"## QueryState `{qs.get('symbol', 'Q')}`\n",
        f"**Definition**: {qs.get('definition', '')}",
    ]
    components = qs.get("components", [])
    if components:
        lines.append("\n**Components**:")
        for c in components:
            if isinstance(c, dict):
                lines.append(f"  - **{c.get('symbol', '?')}** ({c.get('name', '')}): {c.get('description', '')}")
            else:
                lines.append(f"  - {c}")
    return "\n".join(lines)


def _format_desire_field(data: dict) -> str:
    df = data.get("desire_field", {})
    lines = [
        f"## DesireField `{df.get('symbol', 'D_Q')}`\n",
        f"**Definition**: {df.get('definition', '')}",
    ]
    terms = df.get("terms", [])
    if terms:
        lines.append("\n**Terms**:")
        for t in terms:
            if isinstance(t, dict):
                lines.append(f"  - **{t.get('symbol', '?')}**: {t.get('meaning', '')}")
            else:
                lines.append(f"  - {t}")
    action = df.get("action_law", "")
    if action:
        lines.append(f"\n**Action Law**: {action}")
    return "\n".join(lines)


def _format_resonance(data: dict) -> str:
    rm = data.get("resonance_metric", {})
    lines = [
        f"## ResonanceMetric `{rm.get('symbol', 'R')}`\n",
        f"**Definition**: {rm.get('definition', '')}",
    ]
    components = rm.get("components", [])
    if components:
        lines.append("\n**Components**:")
        for c in components:
            if isinstance(c, dict):
                lines.append(f"  - **{c.get('name', '?')}**: {c.get('description', '')}")
            else:
                lines.append(f"  - {c}")
    threshold = rm.get("threshold", "")
    if threshold:
        lines.append(f"\n**Threshold**: {threshold}")
    return "\n".join(lines)


def _format_commit(data: dict) -> str:
    cw = data.get("commit_witness", {})
    lines = [
        f"## CommitWitness `{cw.get('symbol', 'θ')}`\n",
        f"**Definition**: {cw.get('definition', '')}",
    ]
    components = cw.get("components", [])
    if components:
        lines.append("\n**Four Gates**:")
        for c in components:
            if isinstance(c, dict):
                lines.append(f"  - **{c.get('name', '?')}**: {c.get('condition', '')}")
            else:
                lines.append(f"  - {c}")
    return "\n".join(lines)


def _format_compiler(data: dict) -> str:
    dc = data.get("desire_compiler", {})
    lines = [
        f"## Desire Compiler `{dc.get('symbol', 'DC')}`\n",
        f"**Signature**: `{dc.get('signature', 'U → (Θ_U, G_U)')}`",
    ]
    pipeline = dc.get("pipeline", [])
    if pipeline:
        lines.append("\n**6-Stage Pipeline**:")
        for i, stage in enumerate(pipeline, 1):
            if isinstance(stage, dict):
                lines.append(f"  {i}. **{stage.get('name', '?')}** ({stage.get('symbol', '')}): {stage.get('description', '')}")
            else:
                lines.append(f"  {i}. {stage}")
    return "\n".join(lines)


def _format_scheduler(data: dict) -> str:
    rs = data.get("resonance_scheduler", {})
    lines = [
        f"## Resonance Scheduler `{rs.get('symbol', 'RS')}`\n",
        f"**State**: {rs.get('state', '')}",
    ]
    sc = rs.get("state_components", [])
    if sc:
        lines.append("\n**State Components**:")
        for c in sc:
            if isinstance(c, dict):
                lines.append(f"  - **{c.get('symbol', '?')}**: {c.get('description', '')}")
            else:
                lines.append(f"  - {c}")
    lines.append(f"\n**Choice Law**: `{rs.get('choice_law', '')}`")
    lines.append(f"**Rotation Trigger**: {rs.get('rotation_trigger', '')}")
    pruning = rs.get("pruning", "")
    if pruning:
        lines.append(f"**Pruning**: {pruning}")
    return "\n".join(lines)


def _format_kernel(data: dict) -> str:
    rk = data.get("resonance_kernel", {})
    lines = [
        f"## Resonance Kernel `{rk.get('symbol', 'RK')}`\n",
        f"**Definition**: {rk.get('definition', '')}",
    ]
    workers = rk.get("workers", [])
    if workers:
        lines.append("\n**4 Workers (SFCR)**:")
        for w in workers:
            if isinstance(w, dict):
                ops = ", ".join(w.get("operations", []))
                lines.append(f"  - **{w.get('symbol', '?')}** {w.get('name', '')} [{w.get('lens', '')}]: {ops}")
            else:
                lines.append(f"  - {w}")
    shared = rk.get("shared_state", {})
    if shared:
        lines.append("\n**Shared State**:")
        if isinstance(shared, dict):
            for k, v in shared.items():
                lines.append(f"  - **{k}**: {v}")
        else:
            for s in shared:
                lines.append(f"  - {s}")
    step = rk.get("kernel_step", "")
    if step:
        lines.append(f"\n**Kernel Step**: {step}")
    return "\n".join(lines)


def _format_search(data: dict) -> str:
    csl = data.get("crystal_search_law", {})
    lines = [
        "## Crystal Search Law\n",
        f"**Equation**: `{csl.get('equation', '')}`",
    ]
    constraints = csl.get("constraints", [])
    if constraints:
        lines.append("\n**Constraints**:")
        for c in constraints:
            if isinstance(c, dict):
                lines.append(f"  - **{c.get('name', '?')}**: `{c.get('condition', '')}`")
            else:
                lines.append(f"  - {c}")
    admissible = csl.get("admissible_set", "")
    if admissible:
        lines.append(f"\n**Admissible Set**: {admissible}")
    return "\n".join(lines)


def _format_runtime(data: dict) -> str:
    rl = data.get("runtime_loop", {})
    lines = [
        f"## Runtime Loop — {rl.get('name', 'tick/commit/rotate')}\n",
    ]
    steps = rl.get("steps", [])
    if steps:
        for i, s in enumerate(steps, 1):
            if isinstance(s, dict):
                lines.append(f"  {i}. **{s.get('name', '?')}**: {s.get('description', '')}")
            else:
                lines.append(f"  {i}. {s}")
    term = rl.get("termination", "")
    if term:
        lines.append(f"\n**Termination**: {term}")
    return "\n".join(lines)
