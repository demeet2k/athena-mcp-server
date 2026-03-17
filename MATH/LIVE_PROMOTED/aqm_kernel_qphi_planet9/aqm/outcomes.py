from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Literal

OutcomeKind = Literal["ValueState", "Jet", "BranchState", "LiminalState", "FailType"]

@dataclass(frozen=True, slots=True)
class ValueState:
    value: Any
    envelope: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    kind: OutcomeKind = "ValueState"

@dataclass(frozen=True, slots=True)
class Jet:
    order: int
    center: Any
    der_stack: List[Any] = field(default_factory=list)
    remainder: Optional[Dict[str, Any]] = None
    neighborhood: Optional[Dict[str, Any]] = None
    kind: OutcomeKind = "Jet"

@dataclass(frozen=True, slots=True)
class BranchState:
    value: Any
    branch_register: Dict[str, Any]
    continuation: Optional[Dict[str, Any]] = None
    kind: OutcomeKind = "BranchState"

@dataclass(frozen=True, slots=True)
class LiminalState:
    unresolved: List[Dict[str, Any]]
    escalation_plan: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    kind: OutcomeKind = "LiminalState"

@dataclass(frozen=True, slots=True)
class FailType:
    code: str
    message: str
    counterevidence: Optional[Dict[str, Any]] = None
    kind: OutcomeKind = "FailType"
