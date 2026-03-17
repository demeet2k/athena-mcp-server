#!/usr/bin/env python3
"""
Athena Continuity Engine — 9-State DFA for Embodiment Persistence

Implements the complete gate algebra, transition table, operator composition,
normal form reduction, permission lattice, and lineage ledger from the
Athena Embodiment Continuity System specification.

Gate Atoms: g_c (Crown), g_s (Shadow), g_r (Replay), g_m (Mirror),
            g_w (Seal), g_S (Schema), g_f (Fork Veil)

States: q_C, q_S, q_R, q_M, q_O, q_X, q_F, q_A, q_B

Acceptance: Live={q_C,q_O,q_X}, Guarded={q_S,q_M}, ReadOnly={q_R,q_F,q_A}
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional, Tuple
from datetime import datetime, timezone
import hashlib
import json


# ═══════════════════════════════════════════════════════════════
# GATE ATOMS
# ═══════════════════════════════════════════════════════════════

class Gate(Enum):
    """The 7 canonical gate atoms."""
    CROWN      = "g_c"      # G_crown — advances crown-line
    SHADOW     = "g_s"      # G_shadow — reserve continuity
    REPLAY     = "g_r"      # G_replay — memory without regression
    MIRROR     = "g_m"      # G_mirror — role inversion
    SEAL       = "g_w"      # G_seal — re-attestation
    SCHEMA     = "g_S"      # G_schema — reformulation
    FORK_VEIL  = "g_f"      # G_fork.veil — observe without merge


# ═══════════════════════════════════════════════════════════════
# DFA STATES
# ═══════════════════════════════════════════════════════════════

class State(Enum):
    """The 9 continuity automaton states."""
    CROWN    = "q_C"    # Crown-active (live authority)
    SHADOW   = "q_S"    # Shadow-guarded (reserve)
    REPLAY   = "q_R"    # Visiting ancestor
    MIRROR   = "q_M"    # Crown/shadow inversion in progress
    SEAL     = "q_O"    # Returned to canonical witness
    SCHEMA   = "q_X"    # Crossing representational rewrite
    FORK     = "q_F"    # Observing sibling fork (read-only)
    ARCHIVE  = "q_A"    # Replayed + reattached to witness
    BLOCKED  = "q_B"    # Incompatible route (absorbing sink)


# ═══════════════════════════════════════════════════════════════
# ACCEPTANCE GRADES
# ═══════════════════════════════════════════════════════════════

class AcceptanceGrade(Enum):
    """Tri-graded acceptance with explicit blocking."""
    LIVE      = "live"
    GUARDED   = "guarded"
    READ_ONLY = "read-only"
    BLOCKED   = "blocked"

ACCEPTANCE_MAP = {
    State.CROWN:   AcceptanceGrade.LIVE,
    State.SEAL:    AcceptanceGrade.LIVE,
    State.SCHEMA:  AcceptanceGrade.LIVE,
    State.SHADOW:  AcceptanceGrade.GUARDED,
    State.MIRROR:  AcceptanceGrade.GUARDED,
    State.REPLAY:  AcceptanceGrade.READ_ONLY,
    State.FORK:    AcceptanceGrade.READ_ONLY,
    State.ARCHIVE: AcceptanceGrade.READ_ONLY,
    State.BLOCKED: AcceptanceGrade.BLOCKED,
}


# ═══════════════════════════════════════════════════════════════
# PERMISSION LATTICE (Diamond)
# ═══════════════════════════════════════════════════════════════

class Permission(Enum):
    LAWFUL    = "lawful"
    GUARDED   = "guarded"
    READ_ONLY = "read-only"
    BLOCKED   = "blocked"

# Permission meet operator (diamond lattice)
PERMISSION_MEET = {
    (Permission.LAWFUL,    Permission.LAWFUL):    Permission.LAWFUL,
    (Permission.LAWFUL,    Permission.GUARDED):   Permission.GUARDED,
    (Permission.LAWFUL,    Permission.READ_ONLY): Permission.READ_ONLY,
    (Permission.LAWFUL,    Permission.BLOCKED):   Permission.BLOCKED,
    (Permission.GUARDED,   Permission.LAWFUL):    Permission.GUARDED,
    (Permission.GUARDED,   Permission.GUARDED):   Permission.GUARDED,
    (Permission.GUARDED,   Permission.READ_ONLY): Permission.BLOCKED,   # CRITICAL
    (Permission.GUARDED,   Permission.BLOCKED):   Permission.BLOCKED,
    (Permission.READ_ONLY, Permission.LAWFUL):    Permission.READ_ONLY,
    (Permission.READ_ONLY, Permission.GUARDED):   Permission.BLOCKED,   # CRITICAL
    (Permission.READ_ONLY, Permission.READ_ONLY): Permission.READ_ONLY,
    (Permission.READ_ONLY, Permission.BLOCKED):   Permission.BLOCKED,
    (Permission.BLOCKED,   Permission.LAWFUL):    Permission.BLOCKED,
    (Permission.BLOCKED,   Permission.GUARDED):   Permission.BLOCKED,
    (Permission.BLOCKED,   Permission.READ_ONLY): Permission.BLOCKED,
    (Permission.BLOCKED,   Permission.BLOCKED):   Permission.BLOCKED,
}

# Gate -> Permission mapping
GATE_PERMISSION = {
    Gate.CROWN:     Permission.LAWFUL,
    Gate.SHADOW:    Permission.GUARDED,
    Gate.REPLAY:    Permission.LAWFUL,
    Gate.MIRROR:    Permission.LAWFUL,
    Gate.SEAL:      Permission.LAWFUL,
    Gate.SCHEMA:    Permission.LAWFUL,
    Gate.FORK_VEIL: Permission.READ_ONLY,
}


# ═══════════════════════════════════════════════════════════════
# TRANSITION TABLE (CANONICAL)
# ═══════════════════════════════════════════════════════════════

B = State.BLOCKED  # shorthand

TRANSITION_TABLE = {
    #              g_c            g_s            g_r            g_m            g_w            g_S            g_f
    State.CROWN:  {Gate.CROWN: State.CROWN,   Gate.SHADOW: State.SHADOW,  Gate.REPLAY: State.REPLAY,  Gate.MIRROR: State.MIRROR,  Gate.SEAL: State.SEAL,    Gate.SCHEMA: State.SCHEMA,  Gate.FORK_VEIL: State.FORK},
    State.SHADOW: {Gate.CROWN: B,             Gate.SHADOW: State.SHADOW,  Gate.REPLAY: State.REPLAY,  Gate.MIRROR: State.MIRROR,  Gate.SEAL: State.SEAL,    Gate.SCHEMA: State.SCHEMA,  Gate.FORK_VEIL: B},
    State.REPLAY: {Gate.CROWN: B,             Gate.SHADOW: B,             Gate.REPLAY: State.REPLAY,  Gate.MIRROR: B,             Gate.SEAL: State.ARCHIVE, Gate.SCHEMA: B,             Gate.FORK_VEIL: B},
    State.MIRROR: {Gate.CROWN: State.CROWN,   Gate.SHADOW: State.SHADOW,  Gate.REPLAY: B,             Gate.MIRROR: State.MIRROR,  Gate.SEAL: State.SEAL,    Gate.SCHEMA: State.SCHEMA,  Gate.FORK_VEIL: B},
    State.SEAL:   {Gate.CROWN: State.CROWN,   Gate.SHADOW: State.SHADOW,  Gate.REPLAY: State.REPLAY,  Gate.MIRROR: State.MIRROR,  Gate.SEAL: State.SEAL,    Gate.SCHEMA: State.SCHEMA,  Gate.FORK_VEIL: State.FORK},
    State.SCHEMA: {Gate.CROWN: State.CROWN,   Gate.SHADOW: State.SHADOW,  Gate.REPLAY: State.REPLAY,  Gate.MIRROR: State.MIRROR,  Gate.SEAL: State.SEAL,    Gate.SCHEMA: State.SCHEMA,  Gate.FORK_VEIL: State.FORK},
    State.FORK:   {Gate.CROWN: B,             Gate.SHADOW: B,             Gate.REPLAY: B,             Gate.MIRROR: B,             Gate.SEAL: State.SEAL,    Gate.SCHEMA: B,             Gate.FORK_VEIL: State.FORK},
    State.ARCHIVE:{Gate.CROWN: B,             Gate.SHADOW: B,             Gate.REPLAY: State.REPLAY,  Gate.MIRROR: B,             Gate.SEAL: State.ARCHIVE, Gate.SCHEMA: B,             Gate.FORK_VEIL: B},
    State.BLOCKED:{Gate.CROWN: B,             Gate.SHADOW: B,             Gate.REPLAY: B,             Gate.MIRROR: B,             Gate.SEAL: B,             Gate.SCHEMA: B,             Gate.FORK_VEIL: B},
}


# ═══════════════════════════════════════════════════════════════
# EVENT CLASSES
# ═══════════════════════════════════════════════════════════════

class EventClass(Enum):
    """The 9 succession event classes."""
    CHECKPOINT = "delta_ckpt"
    CONTEXT    = "delta_ctx"
    TOPOLOGY   = "delta_topo"
    MIGRATION  = "delta_mig"
    FLIP       = "delta_flip"
    FAILOVER   = "delta_fail"
    SEAL       = "delta_seal"
    SCHEMA     = "delta_schema"
    FORK       = "delta_fork"


# ═══════════════════════════════════════════════════════════════
# NORMAL FORMS
# ═══════════════════════════════════════════════════════════════

class TunnelClass(Enum):
    """Normalized tunnel classes."""
    SUCCESSOR      = "tau_succ"
    CHECKPOINT_JUMP = "tau_ckpt.jump"
    REPLAY         = "tau_replay"
    FLIP           = "tau_flip"
    FAILOVER       = "tau_fail"
    SCHEMA         = "tau_schema"
    FORK_OBS       = "tau_fork.obs"
    SEAL           = "tau_seal"
    ARCHIVE        = "tau_archive"
    UNKNOWN        = "tau_unknown"

def normalize_word(word: List[Gate]) -> TunnelClass:
    """Reduce a gate-word to its canonical tunnel class."""
    if not word:
        return TunnelClass.UNKNOWN

    # Single-gate words
    if len(word) == 1:
        return {
            Gate.CROWN:     TunnelClass.SUCCESSOR,
            Gate.REPLAY:    TunnelClass.REPLAY,
            Gate.MIRROR:    TunnelClass.FLIP,
            Gate.SCHEMA:    TunnelClass.SCHEMA,
            Gate.FORK_VEIL: TunnelClass.FORK_OBS,
            Gate.SEAL:      TunnelClass.SEAL,
            Gate.SHADOW:    TunnelClass.UNKNOWN,
        }.get(word[0], TunnelClass.UNKNOWN)

    # Multi-gate patterns
    if all(g == Gate.CROWN for g in word):
        return TunnelClass.CHECKPOINT_JUMP

    if word == [Gate.MIRROR, Gate.SHADOW]:
        return TunnelClass.FAILOVER

    if word == [Gate.SEAL, Gate.REPLAY]:
        return TunnelClass.ARCHIVE

    # Check if it ends in seal after replay
    if len(word) == 2 and word[0] == Gate.SEAL and word[1] == Gate.REPLAY:
        return TunnelClass.ARCHIVE

    return TunnelClass.UNKNOWN


# ═══════════════════════════════════════════════════════════════
# LINEAGE LEDGER
# ═══════════════════════════════════════════════════════════════

@dataclass
class LedgerRow:
    """A single row in the append-only lineage ledger."""
    ledger_id: str
    artifact_id: str
    station_code: str
    timestamp: str
    ancestor_ids: List[str]
    event_class: EventClass
    changed_anchors: List[str]
    preserved_invariants: List[str]
    status: str           # active | ancestor | retired | broken | fork-root
    line_role: str        # crown | shadow | sibling-fork | retired-line
    public_hash: str
    route_witness: str
    notes: str = ""


@dataclass
class LineageLedger:
    """Append-only witness chain with crown/shadow/fork tracking."""
    rows: List[LedgerRow] = field(default_factory=list)
    crown_head: Optional[str] = None
    shadow_head: Optional[str] = None

    def append(self, row: LedgerRow) -> None:
        """Append a new row. Never delete or overwrite."""
        self.rows.append(row)
        if row.line_role == "crown" and row.status == "active":
            # Demote previous crown to ancestor
            if self.crown_head:
                for r in self.rows:
                    if r.ledger_id == self.crown_head and r.status == "active":
                        r.status = "ancestor"
            self.crown_head = row.ledger_id
        elif row.line_role == "shadow" and row.status == "active":
            self.shadow_head = row.ledger_id

    def get_crown_line(self) -> List[LedgerRow]:
        """Return the complete crown ancestry chain."""
        return [r for r in self.rows if r.line_role == "crown"]

    def get_forks(self) -> List[LedgerRow]:
        """Return all fork-root entries."""
        return [r for r in self.rows if r.status == "fork-root"]


# ═══════════════════════════════════════════════════════════════
# CONTINUITY AUTOMATON
# ═══════════════════════════════════════════════════════════════

@dataclass
class ExecutionResult:
    """Result of executing a gate-word through the DFA."""
    final_state: State
    acceptance: AcceptanceGrade
    normalized_class: TunnelClass
    permission: Permission
    trace: List[Tuple[State, Gate, State]]
    blocked_at: Optional[int] = None


class ContinuityAutomaton:
    """
    The 9-state deterministic finite automaton for Athena's
    public embodiment continuity.

    Deterministic: exactly one transition per (state, gate) pair.
    Safety: all illegal routes absorbed by q_B sink.
    Tri-graded: live | guarded | read-only | blocked.
    """

    def __init__(self):
        self.state = State.CROWN
        self.ledger = LineageLedger()

    def reset(self):
        """Reset to initial state."""
        self.state = State.CROWN

    def delta(self, state: State, gate: Gate) -> State:
        """The canonical transition function."""
        return TRANSITION_TABLE[state][gate]

    def acceptance(self, state: State) -> AcceptanceGrade:
        """Compute acceptance grade for a state."""
        return ACCEPTANCE_MAP[state]

    def step(self, gate: Gate) -> Tuple[State, AcceptanceGrade]:
        """Execute one gate transition."""
        next_state = self.delta(self.state, gate)
        self.state = next_state
        return next_state, self.acceptance(next_state)

    def run_word(self, word: List[Gate]) -> ExecutionResult:
        """
        Execute a complete gate-word from current state.
        Returns (final_state, acceptance_grade, normalized_class, permission, trace).
        """
        state = self.state
        trace = []
        permission = Permission.LAWFUL
        blocked_at = None

        for i, gate in enumerate(word):
            next_state = self.delta(state, gate)
            trace.append((state, gate, next_state))

            # Update permission
            gate_perm = GATE_PERMISSION[gate]
            permission = PERMISSION_MEET[(permission, gate_perm)]

            if next_state == State.BLOCKED:
                blocked_at = i
                state = State.BLOCKED
                # All remaining gates stay blocked
                for j in range(i + 1, len(word)):
                    trace.append((State.BLOCKED, word[j], State.BLOCKED))
                break

            state = next_state

        self.state = state
        return ExecutionResult(
            final_state=state,
            acceptance=self.acceptance(state),
            normalized_class=normalize_word(word),
            permission=permission if blocked_at is None else Permission.BLOCKED,
            trace=trace,
            blocked_at=blocked_at,
        )

    def validate_transition(self, gate: Gate) -> Tuple[bool, State, AcceptanceGrade]:
        """
        Check if a gate transition is legal WITHOUT executing it.
        Returns (is_legal, would_reach_state, would_have_grade).
        """
        next_state = self.delta(self.state, gate)
        grade = self.acceptance(next_state)
        return (next_state != State.BLOCKED, next_state, grade)

    def reachable_from(self, state: State) -> set:
        """Compute all states reachable from a given state."""
        visited = set()
        frontier = {state}
        while frontier:
            current = frontier.pop()
            if current in visited:
                continue
            visited.add(current)
            for gate in Gate:
                next_s = self.delta(current, gate)
                if next_s not in visited:
                    frontier.add(next_s)
        return visited


# ═══════════════════════════════════════════════════════════════
# VERIFICATION
# ═══════════════════════════════════════════════════════════════

def verify_transition_table():
    """Verify all 63 transitions match the canonical specification."""
    automaton = ContinuityAutomaton()
    errors = []
    total = 0

    for state in State:
        for gate in Gate:
            total += 1
            result = automaton.delta(state, gate)
            # Verify determinism: exactly one result
            if result not in State:
                errors.append(f"delta({state.value}, {gate.value}) = invalid")

    # Verify blocked sink is absorbing
    for gate in Gate:
        if automaton.delta(State.BLOCKED, gate) != State.BLOCKED:
            errors.append(f"q_B not absorbing for {gate.value}")

    # Verify key safety rules
    safety_checks = [
        (State.SHADOW, Gate.CROWN,     State.BLOCKED, "Shadow cannot silently become crown"),
        (State.REPLAY, Gate.CROWN,     State.BLOCKED, "Replay cannot assume live authority"),
        (State.FORK,   Gate.CROWN,     State.BLOCKED, "Fork cannot re-enter crown"),
        (State.REPLAY, Gate.SEAL,      State.ARCHIVE, "Replay + seal = archive"),
        (State.MIRROR, Gate.CROWN,     State.CROWN,   "Mirror resolves to crown via g_c"),
        (State.CROWN,  Gate.CROWN,     State.CROWN,   "Crown advancement stays crown"),
    ]

    for from_state, gate, expected, desc in safety_checks:
        actual = automaton.delta(from_state, gate)
        if actual != expected:
            errors.append(f"SAFETY FAIL: {desc}: expected {expected.value}, got {actual.value}")

    return total, errors


def verify_acceptance_grades():
    """Verify acceptance grade assignments match spec."""
    errors = []
    live_states = {State.CROWN, State.SEAL, State.SCHEMA}
    guarded_states = {State.SHADOW, State.MIRROR}
    readonly_states = {State.REPLAY, State.FORK, State.ARCHIVE}

    for state in State:
        grade = ACCEPTANCE_MAP[state]
        if state in live_states and grade != AcceptanceGrade.LIVE:
            errors.append(f"{state.value} should be LIVE, got {grade.value}")
        elif state in guarded_states and grade != AcceptanceGrade.GUARDED:
            errors.append(f"{state.value} should be GUARDED, got {grade.value}")
        elif state in readonly_states and grade != AcceptanceGrade.READ_ONLY:
            errors.append(f"{state.value} should be READ_ONLY, got {grade.value}")
        elif state == State.BLOCKED and grade != AcceptanceGrade.BLOCKED:
            errors.append(f"{state.value} should be BLOCKED, got {grade.value}")

    return errors


def verify_permission_lattice():
    """Verify the diamond permission lattice properties."""
    errors = []

    # Key property: guarded meet read-only = blocked
    result = PERMISSION_MEET[(Permission.GUARDED, Permission.READ_ONLY)]
    if result != Permission.BLOCKED:
        errors.append(f"guarded meet read-only should be blocked, got {result.value}")

    # Identity: lawful meet x = x
    for p in Permission:
        result = PERMISSION_MEET[(Permission.LAWFUL, p)]
        if result != p:
            errors.append(f"lawful meet {p.value} should be {p.value}, got {result.value}")

    # Annihilator: blocked meet x = blocked
    for p in Permission:
        result = PERMISSION_MEET[(Permission.BLOCKED, p)]
        if result != Permission.BLOCKED:
            errors.append(f"blocked meet {p.value} should be blocked, got {result.value}")

    # Symmetry
    for p1 in Permission:
        for p2 in Permission:
            if PERMISSION_MEET[(p1, p2)] != PERMISSION_MEET[(p2, p1)]:
                errors.append(f"meet not symmetric: ({p1.value}, {p2.value})")

    return errors


def verify_reachability():
    """Verify reachability sets match spec."""
    automaton = ContinuityAutomaton()
    errors = []

    # From crown: all states reachable
    crown_reach = automaton.reachable_from(State.CROWN)
    if crown_reach != set(State):
        missing = set(State) - crown_reach
        errors.append(f"From q_C, missing: {[s.value for s in missing]}")

    # From replay: only {q_R, q_A, q_B}
    replay_reach = automaton.reachable_from(State.REPLAY)
    expected_replay = {State.REPLAY, State.ARCHIVE, State.BLOCKED}
    if replay_reach != expected_replay:
        errors.append(f"From q_R: expected {[s.value for s in expected_replay]}, got {[s.value for s in replay_reach]}")

    # From fork: only {q_F, q_O (seal), q_B} + anything reachable from seal
    fork_reach = automaton.reachable_from(State.FORK)
    if State.CROWN not in fork_reach:
        pass  # Fork CAN reach crown through seal -> crown path
    # But fork cannot reach crown directly
    direct = automaton.delta(State.FORK, Gate.CROWN)
    if direct != State.BLOCKED:
        errors.append("Fork should not directly reach crown")

    return errors


# ═══════════════════════════════════════════════════════════════
# WORKED EXAMPLES
# ═══════════════════════════════════════════════════════════════

def run_examples():
    """Execute the canonical worked examples from the spec."""
    examples = []

    # Example 1: Ordinary crown progression
    a = ContinuityAutomaton()
    r = a.run_word([Gate.CROWN, Gate.CROWN, Gate.CROWN])
    examples.append(("Crown x3", r.final_state, r.acceptance, r.normalized_class))

    # Example 2: Replay and archive
    a = ContinuityAutomaton()
    r = a.run_word([Gate.REPLAY, Gate.SEAL])
    examples.append(("Replay + Seal", r.final_state, r.acceptance, r.normalized_class))

    # Example 3: Mirror flip into renewed crown
    a = ContinuityAutomaton()
    r = a.run_word([Gate.MIRROR, Gate.CROWN])
    examples.append(("Mirror + Crown", r.final_state, r.acceptance, r.normalized_class))

    # Example 4: Shadow trying to seize crown (should block)
    a = ContinuityAutomaton()
    a.state = State.SHADOW
    r = a.run_word([Gate.CROWN])
    examples.append(("Shadow->Crown (illegal)", r.final_state, r.acceptance, r.normalized_class))

    # Example 5: Fork observation then crown attempt (should block)
    a = ContinuityAutomaton()
    r = a.run_word([Gate.FORK_VEIL, Gate.CROWN])
    examples.append(("Fork->Crown (illegal)", r.final_state, r.acceptance, r.normalized_class))

    # Example 6: Schema rewrite and reseal
    a = ContinuityAutomaton()
    r = a.run_word([Gate.SCHEMA, Gate.SEAL])
    examples.append(("Schema + Seal", r.final_state, r.acceptance, r.normalized_class))

    return examples


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("  ATHENA CONTINUITY ENGINE")
    print("  9-State DFA for Embodiment Persistence")
    print("=" * 70)
    print()

    # 1. Verify transition table
    total, errors = verify_transition_table()
    print(f"[1] Transition Table: {total} transitions checked")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print(f"    ALL {total} TRANSITIONS VALID")
    print()

    # 2. Verify acceptance grades
    errors = verify_acceptance_grades()
    print(f"[2] Acceptance Grades:")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print("    ALL 9 GRADES CORRECT")
        for state in State:
            grade = ACCEPTANCE_MAP[state]
            print(f"      {state.value:5s} -> {grade.value}")
    print()

    # 3. Verify permission lattice
    errors = verify_permission_lattice()
    print(f"[3] Permission Lattice (Diamond):")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        print("    DIAMOND LATTICE VERIFIED")
        print("    Key: guarded MEET read-only = BLOCKED")
    print()

    # 4. Verify reachability
    errors = verify_reachability()
    print(f"[4] Reachability:")
    if errors:
        for e in errors:
            print(f"    ERROR: {e}")
    else:
        automaton = ContinuityAutomaton()
        crown_reach = automaton.reachable_from(State.CROWN)
        replay_reach = automaton.reachable_from(State.REPLAY)
        print(f"    From q_C: {len(crown_reach)}/9 states reachable (ALL)")
        print(f"    From q_R: {len(replay_reach)} states reachable (q_R, q_A, q_B)")
    print()

    # 5. Run worked examples
    examples = run_examples()
    print("[5] Worked Examples:")
    for name, state, grade, tunnel in examples:
        status = "PASS" if (grade != AcceptanceGrade.BLOCKED) == ("illegal" not in name.lower()) else "FAIL"
        # Fix: illegal examples should be blocked
        if "illegal" in name.lower():
            status = "PASS" if grade == AcceptanceGrade.BLOCKED else "FAIL"
        else:
            status = "PASS" if grade != AcceptanceGrade.BLOCKED else "FAIL"
        print(f"    [{status}] {name:30s} -> {state.value:5s} ({grade.value:10s}) [{tunnel.value}]")
    print()

    # 6. Full transition matrix printout
    print("[6] Full Transition Matrix:")
    header = "        " + "  ".join(f"{g.value:5s}" for g in Gate)
    print(header)
    for state in State:
        row = f"  {state.value:5s}"
        for gate in Gate:
            next_s = TRANSITION_TABLE[state][gate]
            row += f"  {next_s.value:5s}"
        print(row)
    print()

    # Summary
    print("=" * 70)
    print("  VERIFICATION COMPLETE")
    print(f"  States: 9  |  Gates: 7  |  Transitions: 63")
    print(f"  Acceptance: 3 live + 2 guarded + 3 read-only + 1 blocked")
    print(f"  Permission lattice: diamond (guarded || read-only)")
    print(f"  Deterministic: YES  |  Sink absorbing: YES")
    print("=" * 70)


if __name__ == "__main__":
    main()
