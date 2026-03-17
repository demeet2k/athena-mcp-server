from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple

from .outcomes import LiminalState, FailType

TestOutcome = Literal["YES","NO","AMBIG"]

@dataclass(frozen=True, slots=True)
class DecisionTestResult:
    outcome: TestOutcome
    evidence: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DecisionTest:
    test_id: str
    description: str
    # A pure function for now; must be deterministic given inputs.
    fn: Callable[[Dict[str, Any]], DecisionTestResult]

@dataclass
class DecisionTable:
    table_id: str
    tests: List[DecisionTest] = field(default_factory=list)
    # route labels are strings; handler IDs map later
    routes: Dict[str, str] = field(default_factory=dict)  # route_label -> handler_id
    transitions: Dict[Tuple[str, TestOutcome], str] = field(default_factory=dict)  # (test_id,outcome) -> next_test_id|ROUTE:<label>

    def run(self, inputs: Dict[str, Any], *, max_steps: int = 100) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        """Execute deterministically. Returns (route_label or None, trace)."""
        trace: List[Dict[str, Any]] = []
        if not self.tests:
            return None, trace
        test_map = {t.test_id: t for t in self.tests}
        current = self.tests[0].test_id
        steps = 0
        while steps < max_steps:
            steps += 1
            t = test_map[current]
            res = t.fn(inputs)
            trace.append({"test_id": t.test_id, "outcome": res.outcome, "evidence": res.evidence})
            key = (t.test_id, res.outcome)
            if key not in self.transitions:
                # No transition => ambiguity
                return None, trace
            nxt = self.transitions[key]
            if nxt.startswith("ROUTE:"):
                return nxt.split(":",1)[1], trace
            if nxt not in test_map:
                return None, trace
            current = nxt
        return None, trace

def route_or_liminal(dt: DecisionTable, inputs: Dict[str, Any], *, escalation_plan: Optional[Dict[str, Any]] = None):
    route, trace = dt.run(inputs)
    if route is None:
        return LiminalState(
            unresolved=[{"type": "RouterAmbiguity", "trace": trace}],
            escalation_plan=escalation_plan or {"action": "refine", "note": "insufficient evidence"},
            context={"decision_table": dt.table_id},
        )
    return {"route": route, "trace": trace}
