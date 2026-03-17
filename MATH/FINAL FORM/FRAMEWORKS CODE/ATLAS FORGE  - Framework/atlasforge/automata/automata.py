"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         AUTOMATA MODULE                                      ║
║                                                                              ║
║  Finite Automata, Regular Languages, and Formal Grammars                     ║
║                                                                              ║
║  Core Principle:                                                             ║
║    Automata theory provides the foundation for the D-pole (discrete).       ║
║    State machines encode sequential computation, and formal languages       ║
║    capture structural patterns in the framework.                            ║
║                                                                              ║
║  Key Structures:                                                             ║
║    - DFA: Deterministic Finite Automaton                                    ║
║    - NFA: Nondeterministic Finite Automaton                                 ║
║    - Regular expressions: algebraic language description                    ║
║    - Pumping lemma: characterizes regular languages                         ║
║                                                                              ║
║  Connection to Framework:                                                    ║
║    - D-pole ↔ DFA state evolution                                           ║
║    - Gateway hops ↔ state transitions                                       ║
║    - Fold ladder ↔ pushdown automata                                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, List, Dict, Set, FrozenSet, Iterator
from enum import Enum
import numpy as np
from numpy.typing import NDArray


# ═══════════════════════════════════════════════════════════════════════════════
# DETERMINISTIC FINITE AUTOMATON
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class DFA:
    """
    Deterministic Finite Automaton.
    
    M = (Q, Σ, δ, q_0, F) where:
        Q: finite set of states
        Σ: input alphabet
        δ: Q × Σ → Q transition function
        q_0: initial state
        F: set of accepting states
    """
    states: Set[str]
    alphabet: Set[str]
    transitions: Dict[Tuple[str, str], str]  # (state, symbol) → next_state
    initial: str
    accepting: Set[str]
    
    def __post_init__(self):
        if self.initial not in self.states:
            raise ValueError(f"Initial state {self.initial} not in states")
        if not self.accepting.issubset(self.states):
            raise ValueError("Accepting states must be subset of states")
    
    def transition(self, state: str, symbol: str) -> Optional[str]:
        """Get next state for given input."""
        return self.transitions.get((state, symbol))
    
    def run(self, word: str) -> str:
        """Run automaton on input word, return final state."""
        current = self.initial
        for symbol in word:
            next_state = self.transition(current, symbol)
            if next_state is None:
                return None  # No transition defined
            current = next_state
        return current
    
    def accepts(self, word: str) -> bool:
        """Check if automaton accepts the word."""
        final = self.run(word)
        return final is not None and final in self.accepting
    
    def is_complete(self) -> bool:
        """Check if transition function is total."""
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in self.transitions:
                    return False
        return True
    
    def complete(self) -> 'DFA':
        """Add sink state to make automaton complete."""
        if self.is_complete():
            return self
        
        sink = "_sink"
        new_states = self.states | {sink}
        new_transitions = dict(self.transitions)
        
        for state in new_states:
            for symbol in self.alphabet:
                if (state, symbol) not in new_transitions:
                    new_transitions[(state, symbol)] = sink
        
        return DFA(new_states, self.alphabet, new_transitions, 
                  self.initial, self.accepting)
    
    def complement(self) -> 'DFA':
        """DFA accepting complement language."""
        complete_dfa = self.complete()
        new_accepting = complete_dfa.states - complete_dfa.accepting
        return DFA(complete_dfa.states, complete_dfa.alphabet,
                  complete_dfa.transitions, complete_dfa.initial, new_accepting)
    
    def minimize(self) -> 'DFA':
        """Minimize DFA using Hopcroft's algorithm (simplified)."""
        # Remove unreachable states
        reachable = self._reachable_states()
        
        if len(reachable) == len(self.states):
            return self
        
        new_transitions = {k: v for k, v in self.transitions.items() 
                         if k[0] in reachable and v in reachable}
        new_accepting = self.accepting & reachable
        
        return DFA(reachable, self.alphabet, new_transitions,
                  self.initial, new_accepting)
    
    def _reachable_states(self) -> Set[str]:
        """Find all reachable states from initial."""
        reachable = {self.initial}
        frontier = [self.initial]
        
        while frontier:
            state = frontier.pop()
            for symbol in self.alphabet:
                next_state = self.transition(state, symbol)
                if next_state and next_state not in reachable:
                    reachable.add(next_state)
                    frontier.append(next_state)
        
        return reachable
    
    def to_transition_matrix(self) -> Dict[str, NDArray[np.int32]]:
        """Convert to transition matrices for each symbol."""
        state_list = sorted(self.states)
        state_idx = {s: i for i, s in enumerate(state_list)}
        n = len(state_list)
        
        matrices = {}
        for symbol in self.alphabet:
            M = np.zeros((n, n), dtype=np.int32)
            for state in self.states:
                next_state = self.transition(state, symbol)
                if next_state:
                    M[state_idx[state], state_idx[next_state]] = 1
            matrices[symbol] = M
        
        return matrices
    
    @classmethod
    def from_regex_simple(cls, pattern: str) -> 'DFA':
        """
        Create DFA from simple pattern (only concatenation).
        
        For demonstration; full regex would need NFA conversion.
        """
        states = {f"q{i}" for i in range(len(pattern) + 1)}
        alphabet = set(pattern)
        transitions = {}
        
        for i, symbol in enumerate(pattern):
            transitions[(f"q{i}", symbol)] = f"q{i+1}"
        
        return cls(states, alphabet, transitions, "q0", {f"q{len(pattern)}"})


# ═══════════════════════════════════════════════════════════════════════════════
# NONDETERMINISTIC FINITE AUTOMATON
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class NFA:
    """
    Nondeterministic Finite Automaton.
    
    Allows:
        - Multiple transitions for same (state, symbol)
        - ε (epsilon) transitions
    """
    states: Set[str]
    alphabet: Set[str]  # Does not include ε
    transitions: Dict[Tuple[str, Optional[str]], Set[str]]  # None = ε
    initial: str
    accepting: Set[str]
    
    def epsilon_closure(self, states: Set[str]) -> Set[str]:
        """Compute ε-closure of a set of states."""
        closure = set(states)
        stack = list(states)
        
        while stack:
            state = stack.pop()
            eps_next = self.transitions.get((state, None), set())
            for next_state in eps_next:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        
        return closure
    
    def move(self, states: Set[str], symbol: str) -> Set[str]:
        """Compute states reachable by symbol from given states."""
        result = set()
        for state in states:
            next_states = self.transitions.get((state, symbol), set())
            result.update(next_states)
        return result
    
    def accepts(self, word: str) -> bool:
        """Check if NFA accepts the word."""
        current = self.epsilon_closure({self.initial})
        
        for symbol in word:
            current = self.epsilon_closure(self.move(current, symbol))
        
        return bool(current & self.accepting)
    
    def to_dfa(self) -> DFA:
        """Convert NFA to DFA via subset construction."""
        # Initial DFA state is ε-closure of NFA initial
        initial_closure = frozenset(self.epsilon_closure({self.initial}))
        
        dfa_states = set()
        dfa_transitions = {}
        dfa_accepting = set()
        
        # Map frozensets to state names
        state_names = {}
        counter = [0]
        
        def get_name(fs: FrozenSet[str]) -> str:
            if fs not in state_names:
                state_names[fs] = f"q{counter[0]}"
                counter[0] += 1
            return state_names[fs]
        
        frontier = [initial_closure]
        visited = {initial_closure}
        
        while frontier:
            current_set = frontier.pop()
            current_name = get_name(current_set)
            dfa_states.add(current_name)
            
            # Check if accepting
            if current_set & self.accepting:
                dfa_accepting.add(current_name)
            
            for symbol in self.alphabet:
                next_set = frozenset(
                    self.epsilon_closure(self.move(set(current_set), symbol))
                )
                
                if next_set:
                    next_name = get_name(next_set)
                    dfa_transitions[(current_name, symbol)] = next_name
                    
                    if next_set not in visited:
                        visited.add(next_set)
                        frontier.append(next_set)
        
        return DFA(dfa_states, self.alphabet, dfa_transitions,
                  get_name(initial_closure), dfa_accepting)


# ═══════════════════════════════════════════════════════════════════════════════
# REGULAR EXPRESSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class RegexOp(Enum):
    """Regular expression operators."""
    EMPTY = "∅"       # Empty language
    EPSILON = "ε"     # Empty string
    SYMBOL = "a"      # Single symbol
    CONCAT = "·"      # Concatenation
    UNION = "|"       # Union
    STAR = "*"        # Kleene star


@dataclass
class Regex:
    """
    Regular expression AST.
    """
    op: RegexOp
    symbol: Optional[str] = None  # For SYMBOL
    left: Optional['Regex'] = None  # For CONCAT, UNION
    right: Optional['Regex'] = None  # For CONCAT, UNION
    child: Optional['Regex'] = None  # For STAR
    
    def __repr__(self) -> str:
        if self.op == RegexOp.EMPTY:
            return "∅"
        elif self.op == RegexOp.EPSILON:
            return "ε"
        elif self.op == RegexOp.SYMBOL:
            return self.symbol
        elif self.op == RegexOp.CONCAT:
            return f"({self.left}·{self.right})"
        elif self.op == RegexOp.UNION:
            return f"({self.left}|{self.right})"
        elif self.op == RegexOp.STAR:
            return f"({self.child})*"
        return "?"
    
    def to_nfa(self) -> NFA:
        """Convert regex to NFA (Thompson's construction)."""
        if self.op == RegexOp.EMPTY:
            return NFA({"q0", "q1"}, set(), {}, "q0", {"q1"})
        
        elif self.op == RegexOp.EPSILON:
            return NFA({"q0", "q1"}, set(), 
                      {("q0", None): {"q1"}}, "q0", {"q1"})
        
        elif self.op == RegexOp.SYMBOL:
            return NFA({"q0", "q1"}, {self.symbol},
                      {("q0", self.symbol): {"q1"}}, "q0", {"q1"})
        
        elif self.op == RegexOp.CONCAT:
            nfa1 = self.left.to_nfa()
            nfa2 = self.right.to_nfa()
            return self._concat_nfa(nfa1, nfa2)
        
        elif self.op == RegexOp.UNION:
            nfa1 = self.left.to_nfa()
            nfa2 = self.right.to_nfa()
            return self._union_nfa(nfa1, nfa2)
        
        elif self.op == RegexOp.STAR:
            nfa = self.child.to_nfa()
            return self._star_nfa(nfa)
        
        raise ValueError(f"Unknown operator: {self.op}")
    
    def _concat_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """Concatenate two NFAs."""
        # Rename states to avoid conflicts
        prefix1 = "a_"
        prefix2 = "b_"
        
        states1 = {prefix1 + s for s in nfa1.states}
        states2 = {prefix2 + s for s in nfa2.states}
        
        transitions = {}
        
        for (s, sym), targets in nfa1.transitions.items():
            transitions[(prefix1 + s, sym)] = {prefix1 + t for t in targets}
        
        for (s, sym), targets in nfa2.transitions.items():
            transitions[(prefix2 + s, sym)] = {prefix2 + t for t in targets}
        
        # Add ε-transitions from accepting states of nfa1 to initial of nfa2
        for acc in nfa1.accepting:
            key = (prefix1 + acc, None)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(prefix2 + nfa2.initial)
        
        return NFA(
            states1 | states2,
            nfa1.alphabet | nfa2.alphabet,
            transitions,
            prefix1 + nfa1.initial,
            {prefix2 + s for s in nfa2.accepting}
        )
    
    def _union_nfa(self, nfa1: NFA, nfa2: NFA) -> NFA:
        """Union of two NFAs."""
        prefix1 = "a_"
        prefix2 = "b_"
        
        states1 = {prefix1 + s for s in nfa1.states}
        states2 = {prefix2 + s for s in nfa2.states}
        
        new_init = "q_init"
        new_final = "q_final"
        
        transitions = {}
        
        for (s, sym), targets in nfa1.transitions.items():
            transitions[(prefix1 + s, sym)] = {prefix1 + t for t in targets}
        
        for (s, sym), targets in nfa2.transitions.items():
            transitions[(prefix2 + s, sym)] = {prefix2 + t for t in targets}
        
        # ε from new initial to both starts
        transitions[(new_init, None)] = {
            prefix1 + nfa1.initial, 
            prefix2 + nfa2.initial
        }
        
        # ε from both accepts to new final
        for acc in nfa1.accepting:
            key = (prefix1 + acc, None)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(new_final)
        
        for acc in nfa2.accepting:
            key = (prefix2 + acc, None)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(new_final)
        
        return NFA(
            states1 | states2 | {new_init, new_final},
            nfa1.alphabet | nfa2.alphabet,
            transitions,
            new_init,
            {new_final}
        )
    
    def _star_nfa(self, nfa: NFA) -> NFA:
        """Kleene star of NFA."""
        prefix = "a_"
        
        states = {prefix + s for s in nfa.states}
        new_init = "q_init"
        new_final = "q_final"
        
        transitions = {}
        
        for (s, sym), targets in nfa.transitions.items():
            transitions[(prefix + s, sym)] = {prefix + t for t in targets}
        
        # ε from new initial to old initial and new final
        transitions[(new_init, None)] = {prefix + nfa.initial, new_final}
        
        # ε from old accepts to old initial and new final
        for acc in nfa.accepting:
            key = (prefix + acc, None)
            if key not in transitions:
                transitions[key] = set()
            transitions[key].add(prefix + nfa.initial)
            transitions[key].add(new_final)
        
        return NFA(
            states | {new_init, new_final},
            nfa.alphabet,
            transitions,
            new_init,
            {new_final}
        )
    
    @classmethod
    def empty(cls) -> 'Regex':
        """Empty language ∅."""
        return cls(RegexOp.EMPTY)
    
    @classmethod
    def epsilon(cls) -> 'Regex':
        """Empty string ε."""
        return cls(RegexOp.EPSILON)
    
    @classmethod
    def symbol(cls, s: str) -> 'Regex':
        """Single symbol."""
        return cls(RegexOp.SYMBOL, symbol=s)
    
    @classmethod
    def concat(cls, left: 'Regex', right: 'Regex') -> 'Regex':
        """Concatenation."""
        return cls(RegexOp.CONCAT, left=left, right=right)
    
    @classmethod
    def union(cls, left: 'Regex', right: 'Regex') -> 'Regex':
        """Union."""
        return cls(RegexOp.UNION, left=left, right=right)
    
    @classmethod
    def star(cls, child: 'Regex') -> 'Regex':
        """Kleene star."""
        return cls(RegexOp.STAR, child=child)


# ═══════════════════════════════════════════════════════════════════════════════
# LANGUAGE OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

def dfa_intersection(dfa1: DFA, dfa2: DFA) -> DFA:
    """Intersection of two DFAs via product construction."""
    if dfa1.alphabet != dfa2.alphabet:
        raise ValueError("Alphabets must match")
    
    new_states = set()
    new_transitions = {}
    new_accepting = set()
    
    for s1 in dfa1.states:
        for s2 in dfa2.states:
            new_state = f"({s1},{s2})"
            new_states.add(new_state)
            
            if s1 in dfa1.accepting and s2 in dfa2.accepting:
                new_accepting.add(new_state)
            
            for symbol in dfa1.alphabet:
                next1 = dfa1.transition(s1, symbol)
                next2 = dfa2.transition(s2, symbol)
                if next1 and next2:
                    new_transitions[(new_state, symbol)] = f"({next1},{next2})"
    
    new_initial = f"({dfa1.initial},{dfa2.initial})"
    
    return DFA(new_states, dfa1.alphabet, new_transitions, 
              new_initial, new_accepting)


def dfa_union(dfa1: DFA, dfa2: DFA) -> DFA:
    """Union of two DFAs via product construction."""
    if dfa1.alphabet != dfa2.alphabet:
        raise ValueError("Alphabets must match")
    
    new_states = set()
    new_transitions = {}
    new_accepting = set()
    
    for s1 in dfa1.states:
        for s2 in dfa2.states:
            new_state = f"({s1},{s2})"
            new_states.add(new_state)
            
            if s1 in dfa1.accepting or s2 in dfa2.accepting:
                new_accepting.add(new_state)
            
            for symbol in dfa1.alphabet:
                next1 = dfa1.transition(s1, symbol)
                next2 = dfa2.transition(s2, symbol)
                if next1 and next2:
                    new_transitions[(new_state, symbol)] = f"({next1},{next2})"
    
    new_initial = f"({dfa1.initial},{dfa2.initial})"
    
    return DFA(new_states, dfa1.alphabet, new_transitions,
              new_initial, new_accepting)


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def create_dfa(states: Set[str], alphabet: Set[str],
              transitions: Dict[Tuple[str, str], str],
              initial: str, accepting: Set[str]) -> DFA:
    """Create DFA."""
    return DFA(states, alphabet, transitions, initial, accepting)


def regex_to_dfa(regex: Regex) -> DFA:
    """Convert regex to DFA."""
    nfa = regex.to_nfa()
    return nfa.to_dfa()


def accepts_word(dfa: DFA, word: str) -> bool:
    """Check if DFA accepts word."""
    return dfa.accepts(word)


# ═══════════════════════════════════════════════════════════════════════════════
# MODULE EXPORTS
# ═══════════════════════════════════════════════════════════════════════════════

__all__ = [
    # Automata
    'DFA',
    'NFA',
    
    # Regex
    'Regex',
    'RegexOp',
    
    # Operations
    'dfa_intersection',
    'dfa_union',
    
    # Functions
    'create_dfa',
    'regex_to_dfa',
    'accepts_word',
]
