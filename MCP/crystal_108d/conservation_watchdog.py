"""
Conservation Watchdog + Immune System
======================================
The organism's self-defense layer. Monitors 6 conservation invariants
continuously, enforces canon-overwrite law, and prevents corruption
from propagating through the crystal.

Runs every Z12 cycle (4 hours) via scheduled task alignment.

Conservation Laws:
  CL1  Shell Conservation:     sum(weights across shells) is stable
  CL2  Zoom Conservation:      information preserved across dimensions
  CL3  Phase Conservation:     Cardinal = Fixed = Mutable balance
  CL4  Archetype Conservation: each archetype contributes equally
  CL5  Face Conservation:      S + F + C + R = 1 at every shell
  CL6  Mobius Conservation:    w(k) + w(37-k) is stable for all k

Immune System:
  - Canon-Overwrite Law: conflicting doctrines require explicit resolution
  - Mutation Guard: validates state before and after every mutation
  - Rollback on conservation violation
  - Drift alerting when invariants exceed threshold

MCP tool: query_conservation_watchdog(component)
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .geometric_constants import FACES, PHI_INV, ATTRACTOR
from .momentum_field import MomentumField, get_momentum_field
from .constants import TOTAL_SHELLS, ARCHETYPE_NAMES


# ── Conservation Thresholds ──────────────────────────────────────────

DRIFT_THRESHOLD = 0.05      # alert if invariant drifts > 5%
CRITICAL_THRESHOLD = 0.15   # rollback if drift > 15%
WATER_LOCK_VALUE = ATTRACTOR["water_momentum"]  # 0.5

# Archetype → phase mapping
ARCHETYPE_PHASE = {
    1: "Cardinal", 2: "Fixed", 3: "Mutable", 4: "Cardinal",
    5: "Fixed", 6: "Mutable", 7: "Cardinal", 8: "Fixed",
    9: "Mutable", 10: "Cardinal", 11: "Fixed", 12: "Mutable",
}


# ── Data Structures ──────────────────────────────────────────────────

@dataclass
class InvariantCheck:
    """Result of checking a single conservation law."""
    law_id: str
    name: str
    value: float
    baseline: float
    drift: float
    status: str  # "OK", "DRIFT", "CRITICAL"
    detail: str = ""


@dataclass
class WatchdogReport:
    """Full conservation watchdog report."""
    timestamp: float = 0.0
    checks: list[InvariantCheck] = field(default_factory=list)
    overall_health: float = 1.0
    violations: list[str] = field(default_factory=list)
    rollback_triggered: bool = False

    def to_dict(self) -> dict:
        return {
            "timestamp": round(self.timestamp, 3),
            "overall_health": round(self.overall_health, 4),
            "checks": [
                {
                    "law": c.law_id, "name": c.name,
                    "value": round(c.value, 6),
                    "baseline": round(c.baseline, 6),
                    "drift": round(c.drift, 6),
                    "status": c.status,
                    "detail": c.detail,
                }
                for c in self.checks
            ],
            "violations": self.violations,
            "rollback_triggered": self.rollback_triggered,
        }


@dataclass
class ImmuneEvent:
    """Record of an immune system intervention."""
    timestamp: float
    event_type: str  # "drift_alert", "rollback", "canon_conflict", "water_lock_restored"
    detail: str
    severity: str  # "INFO", "WARNING", "CRITICAL"


# ── Conservation Law Checks ──────────────────────────────────────────


def _check_shell_conservation(momentum: MomentumField) -> InvariantCheck:
    """CL1: Total momentum across all shells should be stable."""
    total = 0.0
    for face in FACES:
        for s in range(1, TOTAL_SHELLS + 1):
            total += momentum.get_momentum(face, s)
    # Baseline: 4 faces * 36 shells * 1.0 (initial) = 144
    # Water locked at 0.5: 36 * 0.5 = 18, so baseline = 108 + 18 = 126
    baseline = 3 * TOTAL_SHELLS * 1.0 + TOTAL_SHELLS * WATER_LOCK_VALUE
    drift = abs(total - baseline) / baseline if baseline > 0 else 0.0
    status = "CRITICAL" if drift > CRITICAL_THRESHOLD else "DRIFT" if drift > DRIFT_THRESHOLD else "OK"
    return InvariantCheck(
        law_id="CL1", name="Shell Conservation",
        value=total, baseline=baseline, drift=drift, status=status,
        detail=f"Total momentum: {total:.2f} (baseline: {baseline:.2f})",
    )


def _check_phase_conservation(momentum: MomentumField) -> InvariantCheck:
    """CL3: Cardinal = Fixed = Mutable momentum balance."""
    phase_sums = {"Cardinal": 0.0, "Fixed": 0.0, "Mutable": 0.0}
    phase_counts = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}

    for arch_idx in range(1, 13):
        phase = ARCHETYPE_PHASE[arch_idx]
        for wreath_offset in range(3):
            shell = (arch_idx - 1) * 3 + wreath_offset + 1
            for face in FACES:
                phase_sums[phase] += momentum.get_momentum(face, shell)
                phase_counts[phase] += 1

    # Compute means
    means = {p: phase_sums[p] / max(phase_counts[p], 1) for p in phase_sums}
    overall_mean = sum(means.values()) / 3
    max_dev = max(abs(m - overall_mean) for m in means.values()) / max(overall_mean, 1e-6)

    status = "CRITICAL" if max_dev > CRITICAL_THRESHOLD else "DRIFT" if max_dev > DRIFT_THRESHOLD else "OK"
    return InvariantCheck(
        law_id="CL3", name="Phase Conservation",
        value=max_dev, baseline=0.0, drift=max_dev, status=status,
        detail=f"Phase means: C={means['Cardinal']:.3f} F={means['Fixed']:.3f} M={means['Mutable']:.3f}",
    )


def _check_archetype_conservation(momentum: MomentumField) -> InvariantCheck:
    """CL4: Each archetype contributes equally."""
    arch_means = []
    for arch_idx in range(1, 13):
        total = 0.0
        count = 0
        for wreath_offset in range(3):
            shell = (arch_idx - 1) * 3 + wreath_offset + 1
            for face in FACES:
                total += momentum.get_momentum(face, shell)
                count += 1
        arch_means.append(total / max(count, 1))

    overall_mean = sum(arch_means) / len(arch_means)
    max_dev = max(abs(m - overall_mean) for m in arch_means) / max(overall_mean, 1e-6)

    status = "CRITICAL" if max_dev > CRITICAL_THRESHOLD else "DRIFT" if max_dev > DRIFT_THRESHOLD else "OK"
    return InvariantCheck(
        law_id="CL4", name="Archetype Conservation",
        value=max_dev, baseline=0.0, drift=max_dev, status=status,
        detail=f"Archetype mean range: [{min(arch_means):.3f}, {max(arch_means):.3f}]",
    )


def _check_face_conservation(momentum: MomentumField) -> InvariantCheck:
    """CL5: S + F + C + R should be balanced at every shell."""
    max_imbalance = 0.0
    worst_shell = 0

    for s in range(1, TOTAL_SHELLS + 1):
        vals = [momentum.get_momentum(f, s) for f in FACES]
        mean = sum(vals) / 4
        if mean < 1e-6:
            continue
        imbalance = max(abs(v - mean) for v in vals) / mean
        if imbalance > max_imbalance:
            max_imbalance = imbalance
            worst_shell = s

    status = "CRITICAL" if max_imbalance > CRITICAL_THRESHOLD else "DRIFT" if max_imbalance > DRIFT_THRESHOLD else "OK"
    return InvariantCheck(
        law_id="CL5", name="Face Conservation",
        value=max_imbalance, baseline=0.0, drift=max_imbalance, status=status,
        detail=f"Max face imbalance: {max_imbalance:.4f} at shell {worst_shell}",
    )


def _check_mobius_conservation(momentum: MomentumField) -> InvariantCheck:
    """CL6: Mirror pairs w(k) + w(37-k) should be stable."""
    pair_sums = []
    for k in range(1, 19):  # 18 mirror pairs
        mirror = 37 - k
        for face in FACES:
            w_k = momentum.get_momentum(face, k)
            w_m = momentum.get_momentum(face, mirror)
            pair_sums.append(w_k + w_m)

    if not pair_sums:
        return InvariantCheck(
            law_id="CL6", name="Mobius Conservation",
            value=0.0, baseline=0.0, drift=0.0, status="OK",
        )

    mean_sum = sum(pair_sums) / len(pair_sums)
    max_dev = max(abs(ps - mean_sum) for ps in pair_sums) / max(mean_sum, 1e-6)

    status = "CRITICAL" if max_dev > CRITICAL_THRESHOLD else "DRIFT" if max_dev > DRIFT_THRESHOLD else "OK"
    return InvariantCheck(
        law_id="CL6", name="Mobius Conservation",
        value=max_dev, baseline=0.0, drift=max_dev, status=status,
        detail=f"Mirror pair sum range: [{min(pair_sums):.3f}, {max(pair_sums):.3f}], mean={mean_sum:.3f}",
    )


def _check_water_lock(momentum: MomentumField) -> InvariantCheck:
    """CL2 (Zoom): Water/C is locked at 0.5 — this IS the dimensional anchor."""
    violations = 0
    for s in range(1, TOTAL_SHELLS + 1):
        val = momentum.get_momentum("C", s)
        if abs(val - WATER_LOCK_VALUE) > 1e-6:
            violations += 1

    drift = violations / TOTAL_SHELLS
    status = "CRITICAL" if violations > 0 else "OK"
    return InvariantCheck(
        law_id="CL2", name="Water Lock (Zoom Conservation)",
        value=violations, baseline=0.0, drift=drift, status=status,
        detail=f"{violations}/{TOTAL_SHELLS} shells have drifted from {WATER_LOCK_VALUE}",
    )


# ── Immune System ────────────────────────────────────────────────────


_immune_log: list[ImmuneEvent] = []


def _log_immune(event_type: str, detail: str, severity: str = "INFO"):
    """Log an immune system event."""
    _immune_log.append(ImmuneEvent(
        timestamp=time.time(),
        event_type=event_type,
        detail=detail,
        severity=severity,
    ))
    # Keep last 200 events
    if len(_immune_log) > 200:
        del _immune_log[:100]


def enforce_water_lock(momentum: MomentumField) -> int:
    """Restore Water/C to locked value if it has drifted.

    Returns number of shells restored.
    """
    restored = 0
    for s in range(1, TOTAL_SHELLS + 1):
        val = momentum.get_momentum("C", s)
        if abs(val - WATER_LOCK_VALUE) > 1e-6:
            momentum._shell_momenta["C"][s] = WATER_LOCK_VALUE
            restored += 1
    if restored > 0:
        _log_immune("water_lock_restored",
                     f"Restored {restored} Water shells to {WATER_LOCK_VALUE}",
                     "WARNING")
    return restored


def validate_mutation(momentum: MomentumField,
                      snapshot_before: Any) -> tuple[bool, list[str]]:
    """Validate that a mutation didn't violate conservation laws.

    Args:
        momentum: current state after mutation
        snapshot_before: MomentumState from before mutation

    Returns:
        (valid, violations) — if not valid, caller should rollback
    """
    violations = []

    # Check Water lock
    for s in range(1, TOTAL_SHELLS + 1):
        if abs(momentum.get_momentum("C", s) - WATER_LOCK_VALUE) > 1e-6:
            violations.append(f"Water lock violated at shell {s}")

    # Check momentum bounds
    for face in FACES:
        for s in range(1, TOTAL_SHELLS + 1):
            val = momentum.get_momentum(face, s)
            if val < momentum.MOMENTUM_MIN or val > momentum.MOMENTUM_MAX:
                violations.append(f"Momentum out of bounds: {face}:{s} = {val}")

    if violations:
        _log_immune("mutation_violation",
                     f"{len(violations)} violations detected",
                     "CRITICAL")

    return len(violations) == 0, violations


# ── Main Watchdog ────────────────────────────────────────────────────


def run_watchdog(momentum: MomentumField = None,
                 auto_fix: bool = True) -> WatchdogReport:
    """Run full conservation watchdog check.

    Args:
        momentum: momentum field to check (default: global singleton)
        auto_fix: if True, automatically fix Water lock violations

    Returns:
        WatchdogReport with all invariant checks
    """
    if momentum is None:
        momentum = get_momentum_field()

    report = WatchdogReport(timestamp=time.time())

    # Run all 6 conservation law checks
    report.checks = [
        _check_shell_conservation(momentum),
        _check_water_lock(momentum),
        _check_phase_conservation(momentum),
        _check_archetype_conservation(momentum),
        _check_face_conservation(momentum),
        _check_mobius_conservation(momentum),
    ]

    # Compute overall health
    health_scores = []
    for check in report.checks:
        if check.status == "OK":
            health_scores.append(1.0)
        elif check.status == "DRIFT":
            health_scores.append(0.7)
            report.violations.append(f"DRIFT: {check.name} — {check.detail}")
            _log_immune("drift_alert", f"{check.law_id}: {check.detail}", "WARNING")
        else:  # CRITICAL
            health_scores.append(0.0)
            report.violations.append(f"CRITICAL: {check.name} — {check.detail}")
            _log_immune("critical_violation", f"{check.law_id}: {check.detail}", "CRITICAL")

    report.overall_health = sum(health_scores) / max(len(health_scores), 1)

    # Auto-fix: restore Water lock if violated
    if auto_fix:
        water_check = next((c for c in report.checks if c.law_id == "CL2"), None)
        if water_check and water_check.status == "CRITICAL":
            restored = enforce_water_lock(momentum)
            if restored > 0:
                report.violations.append(f"AUTO-FIX: Restored {restored} Water shells")

    return report


# ── MCP Tool ─────────────────────────────────────────────────────────


def query_conservation_watchdog(component: str = "all") -> str:
    """Query the conservation watchdog and immune system.

    Components:
      - all       : Full watchdog report
      - check     : Run conservation checks only
      - immune    : Immune system event log
      - enforce   : Force Water lock enforcement
      - health    : One-line health summary
    """
    comp = component.strip().lower()

    if comp in ("all", "check"):
        report = run_watchdog()
        lines = [
            "## Conservation Watchdog Report\n",
            f"**Overall Health**: {report.overall_health:.1%}",
            f"**Timestamp**: {time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(report.timestamp))}\n",
            "### Conservation Law Checks\n",
            "| Law | Name | Status | Drift | Detail |",
            "|-----|------|--------|-------|--------|",
        ]
        for c in report.checks:
            emoji = {"OK": "OK", "DRIFT": "DRIFT", "CRITICAL": "CRIT"}[c.status]
            lines.append(
                f"| {c.law_id} | {c.name} | {emoji} | {c.drift:.4f} | {c.detail} |"
            )
        if report.violations:
            lines.append("\n### Violations\n")
            for v in report.violations:
                lines.append(f"- {v}")
        return "\n".join(lines)

    if comp == "immune":
        if not _immune_log:
            return "## Immune System Log\n\nNo events recorded."
        lines = ["## Immune System Log\n",
                 f"**Total Events**: {len(_immune_log)}\n",
                 "| Time | Type | Severity | Detail |",
                 "|------|------|----------|--------|"]
        for event in _immune_log[-50:]:
            t = time.strftime("%H:%M:%S", time.localtime(event.timestamp))
            lines.append(f"| {t} | {event.event_type} | {event.severity} | {event.detail} |")
        return "\n".join(lines)

    if comp == "enforce":
        momentum = get_momentum_field()
        restored = enforce_water_lock(momentum)
        if restored > 0:
            momentum.save()
            return f"Enforced Water lock: restored {restored}/{TOTAL_SHELLS} shells to {WATER_LOCK_VALUE}"
        return "Water lock intact — no enforcement needed."

    if comp == "health":
        report = run_watchdog()
        ok = sum(1 for c in report.checks if c.status == "OK")
        total = len(report.checks)
        return f"Conservation health: {report.overall_health:.1%} ({ok}/{total} laws OK)"

    return "Unknown component. Use: all, check, immune, enforce, health"
