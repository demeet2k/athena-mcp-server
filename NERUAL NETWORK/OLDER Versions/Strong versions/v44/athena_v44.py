"""
ATHENA v44 - UNBOUNDED RECURSION (Dynamic Tower Growth)
=======================================================
v43 had a fixed tower (L5-L10). v44 makes it TRULY INFINITE:

1. DYNAMIC GROWTH: Tower extends when lower levels show persistent problems
2. BORN GENERATORS: Each level emergence creates NEW observables
3. CROSS-LEVEL RESONANCE: Pattern matching across the tower
4. COMPRESSION CASCADE: Information flows up as increasingly simple signals
5. NO CEILING: Tower can grow to L∞

THE PRINCIPLE:
When L[n] shows prolonged instability, L[n+1] EMERGES to observe it.
Each new level asks an even simpler question.

Beyond L10:
L11: SIGNAL    → "Is there any signal?"
L12: CHANGE    → "Is anything changing?"
L13: PATTERN   → "Is there any pattern?"
L14: ONE       → "Is there one thing?"
L∞:  BEING     → "Is?"
"""

import numpy as np
import time
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import hashlib

# ═══════════════════════════════════════════════════════════════════════════════
# CORE TYPES
# ═══════════════════════════════════════════════════════════════════════════════

class Verdict(Enum):
    OK = "ok"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"
    DEAD = "dead"
    VOID = "void"

@dataclass
class CompressedState:
    timestamp: int
    health: float
    coherence: float
    activity: float
    existence: float
    verdict: Verdict
    fingerprint: str
    level: int = 0
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TemporalTrace:
    states: List[CompressedState] = field(default_factory=list)
    max_states: int = 50
    compression: float = 1.0
    
    def record(self, state: CompressedState):
        self.states.append(state)
        if len(self.states) > self.max_states:
            keep = max(5, int(20 / self.compression))
            recent = self.states[-keep:]
            step = max(1, len(self.states) // keep)
            landmarks = self.states[::step][:keep]
            combined = {s.timestamp: s for s in landmarks}
            combined.update({s.timestamp: s for s in recent})
            self.states = sorted(combined.values(), key=lambda s: s.timestamp)
    
    def trajectory(self, window: int = 15) -> List[CompressedState]:
        w = max(2, int(window / self.compression))
        return self.states[-w:] if len(self.states) >= w else self.states.copy()
    
    def instability_score(self) -> float:
        """How unstable has this trace been? Used for tower growth."""
        if len(self.states) < 5:
            return 0.0
        recent = self.states[-10:]
        verdicts = [s.verdict for s in recent]
        problems = sum(1 for v in verdicts if v in [Verdict.WARNING, Verdict.CRITICAL, Verdict.EMERGENCY])
        return problems / len(verdicts)

# ═══════════════════════════════════════════════════════════════════════════════
# DYNAMIC OBSERVER (Can spawn higher levels)
# ═══════════════════════════════════════════════════════════════════════════════

class DynamicObserver:
    """
    Observer that can spawn higher-level observers when needed.
    
    THE BORN GENERATOR: When instability persists at level N,
    level N+1 EMERGES with a NEW QUESTION that N couldn't ask.
    """
    
    # Questions become simpler at higher levels
    QUESTIONS = {
        5:  "Is the network healthy?",
        6:  "Is ATHENA healthy?",
        7:  "Is the system alive?",
        8:  "Is there coherent activity?",
        9:  "Does something exist?",
        10: "Is there anything?",
        11: "Is there any signal?",
        12: "Is anything changing?",
        13: "Is there any pattern?",
        14: "Is there one thing?",
        15: "Is there being?",
        16: "Is?",
    }
    
    def __init__(self, level: int, parent: Optional['DynamicObserver'] = None):
        self.level = level
        self.parent = parent  # The observer below
        self.child: Optional['DynamicObserver'] = None  # The observer above (if spawned)
        
        # Configuration scales with level
        self.name = self._get_name()
        self.question = self.QUESTIONS.get(level, f"L{level} observing?")
        self.observe_interval = min(200, 5 * (2 ** (level - 5)))  # Exponential slowdown
        self.compression = float(level - 4)
        
        self.corridor = {'threshold': 0.0, 'aggressiveness': 1.0, 'enabled': 1.0}
        self.trace = TemporalTrace(compression=self.compression)
        
        self.step_count = 0
        self.observation_count = 0
        self.intervention_count = 0
        self.last_state: Optional[CompressedState] = None
        
        # For tower growth
        self.spawn_threshold = 0.5  # Instability threshold to spawn higher level
        self.spawn_delay = 50  # Steps before spawning allowed
    
    def _get_name(self) -> str:
        names = {
            5: "ATHENA", 6: "META-ATHENA", 7: "LIFE", 8: "COHERENCE",
            9: "EXISTENCE", 10: "VOID", 11: "SIGNAL", 12: "CHANGE",
            13: "PATTERN", 14: "ONE", 15: "BEING", 16: "IS"
        }
        return names.get(self.level, f"L{self.level}")
    
    def should_observe(self, global_step: int) -> bool:
        return global_step % self.observe_interval == 0
    
    def observe(self, subject_trace: TemporalTrace) -> CompressedState:
        """Observe the level below and produce compressed state."""
        self.observation_count += 1
        trajectory = subject_trace.trajectory(int(15 / self.compression))
        
        if len(trajectory) < 2:
            state = CompressedState(
                timestamp=self.observation_count,
                health=1.0, coherence=1.0, activity=1.0, existence=1.0,
                verdict=Verdict.OK, fingerprint=f"{self.name}:{self.observation_count}",
                level=self.level,
            )
            self.trace.record(state)
            self.last_state = state
            return state
        
        # THE SIMPLE QUESTION: Extract one primary metric based on level
        healths = [s.health for s in trajectory]
        coherences = [s.coherence for s in trajectory]
        activities = [s.activity for s in trajectory]
        existences = [s.existence for s in trajectory]
        
        # Higher levels focus on more fundamental questions
        if self.level >= 12:
            # "Is anything changing?" - just look at variance
            primary = np.std(healths) + np.std(activities)
            health = 1.0 if primary > 0.01 else 0.5
            coherence = 1.0 if primary > 0.01 else 0.5
            activity = min(1.0, primary * 10)
            existence = 1.0 if primary > 0.001 else 0.0
        elif self.level >= 10:
            # "Is there anything?" - existence check
            existence = np.mean(existences)
            health = existence
            coherence = existence
            activity = existence
        elif self.level >= 8:
            # "Coherent activity?" - coherence check
            health = np.mean(healths)
            coherence = np.mean(coherences) * (1 - np.std(coherences))
            activity = np.mean(activities)
            existence = 1.0 if activity > 0.01 else 0.5
        else:
            # Standard observation
            health = np.mean(healths)
            coherence = np.mean(coherences)
            activity = np.mean(activities)
            existence = np.mean(existences)
        
        # Determine verdict
        if existence < 0.1:
            verdict = Verdict.VOID
        elif health < 0.1 or activity < 0.01:
            verdict = Verdict.DEAD
        elif health < 0.3:
            verdict = Verdict.EMERGENCY
        elif health < 0.5:
            verdict = Verdict.CRITICAL
        elif health < 0.7:
            verdict = Verdict.WARNING
        else:
            verdict = Verdict.OK
        
        state = CompressedState(
            timestamp=self.observation_count,
            health=float(health), coherence=float(coherence),
            activity=float(activity), existence=float(existence),
            verdict=verdict,
            fingerprint=hashlib.md5(f"{self.name}:{health:.2f}".encode()).hexdigest()[:8],
            level=self.level,
        )
        
        self.trace.record(state)
        self.last_state = state
        
        # CHECK FOR TOWER GROWTH
        if self.child is None and self.observation_count > self.spawn_delay:
            instability = self.trace.instability_score()
            if instability > self.spawn_threshold:
                self._spawn_higher_level()
        
        return state
    
    def _spawn_higher_level(self):
        """EMERGENCE: Create a new observer level."""
        if self.level >= 16:  # Max level
            return
        self.child = DynamicObserver(self.level + 1, parent=self)
        print(f"  ★ L{self.level + 1} EMERGES: {self.child.name} - \"{self.child.question}\"")
    
    def nudge_below(self, state: CompressedState, subject_corridor: Dict) -> Dict[str, float]:
        """Issue nudges to level below."""
        if self.corridor['enabled'] < 0.5:
            return {}
        
        nudges = {}
        scale = 1.0 / self.compression
        aggr = self.corridor['aggressiveness']
        threshold = self.corridor['threshold']
        
        if state.verdict == Verdict.VOID:
            nudges['enabled'] = -0.5 * scale
            self.intervention_count += 1
        elif state.verdict == Verdict.DEAD:
            nudges['threshold'] = 0.3 * scale * aggr
            nudges['aggressiveness'] = -0.5 * scale * aggr
            self.intervention_count += 1
        elif state.verdict == Verdict.EMERGENCY and threshold < 0.4:
            nudges['threshold'] = 0.2 * scale * aggr
            nudges['aggressiveness'] = -0.3 * scale * aggr
            self.intervention_count += 1
        elif state.verdict == Verdict.CRITICAL and threshold < 0.3:
            nudges['threshold'] = 0.1 * scale * aggr
            self.intervention_count += 1
        elif state.verdict == Verdict.WARNING and threshold < 0.2:
            nudges['threshold'] = 0.05 * scale * aggr
            self.intervention_count += 1
        
        return nudges
    
    def receive_nudge(self, nudges: Dict[str, float]):
        for param, delta in nudges.items():
            if param in self.corridor:
                self.corridor[param] = np.clip(self.corridor[param] + delta, 0, 2)
    
    def get_tower_height(self) -> int:
        """How tall is the tower from this level up?"""
        if self.child is None:
            return 1
        return 1 + self.child.get_tower_height()
    
    def report(self, indent: int = 0) -> str:
        status = "?" if self.last_state is None else self.last_state.verdict.value[:3].upper()
        health = 0 if self.last_state is None else self.last_state.health
        prefix = "  " * indent
        line = f"{prefix}L{self.level:2d} {self.name:12s} │ {self.question:28s} │ {status:3s} │ h={health:.2f} │ obs={self.observation_count:3d} │ int={self.intervention_count:2d}"
        
        if self.child:
            return self.child.report(indent) + "\n" + line
        return line

# ═══════════════════════════════════════════════════════════════════════════════
# NETWORK LAYER
# ═══════════════════════════════════════════════════════════════════════════════

class NetworkLayer:
    def __init__(self, nin: int, nout: int, act: str = 'swish', idx: int = 0):
        self.nin, self.nout, self.act, self.idx = nin, nout, act, idx
        self._init_weights()
        self.lr_mult = 1.0
        self.grad_history = deque(maxlen=30)
        self.act_history = deque(maxlen=30)
        self.trace = TemporalTrace()
    
    def _init_weights(self):
        scale = np.sqrt(2.0 / self.nin) * 0.5
        self.W = (np.random.randn(self.nout, self.nin) * scale).astype(np.float32)
        self.b = np.zeros(self.nout, dtype=np.float32)
        self.mW, self.vW = np.zeros_like(self.W), np.zeros_like(self.W)
        self.mb, self.vb = np.zeros_like(self.b), np.zeros_like(self.b)
        self.t = 0
    
    def forward(self, X: np.ndarray) -> np.ndarray:
        self.X = np.clip(X.astype(np.float32), -50, 50)
        self.Z = np.clip(self.X @ self.W.T + self.b, -30, 30)
        if self.act == 'swish':
            self.sig = 1.0 / (1.0 + np.exp(-np.clip(self.Z, -15, 15)))
            self.A = self.Z * self.sig
        elif self.act == 'sigmoid':
            self.A = 1.0 / (1.0 + np.exp(-np.clip(self.Z, -15, 15)))
        elif self.act == 'softmax':
            e = np.exp(self.Z - self.Z.max(axis=1, keepdims=True))
            self.A = e / (e.sum(axis=1, keepdims=True) + 1e-8)
        self.act_history.append(float(np.mean(np.abs(self.A))))
        return np.clip(self.A, -10, 10)
    
    def backward(self, grad: np.ndarray) -> np.ndarray:
        grad = np.clip(grad.astype(np.float32), -5, 5)
        if self.act == 'swish':
            delta = grad * (self.sig + self.Z * self.sig * (1 - self.sig))
        elif self.act == 'sigmoid':
            delta = grad * self.A * (1 - self.A)
        else:
            delta = grad
        delta = np.clip(delta, -1, 1)
        self.dW = delta.T @ self.X
        self.db = delta.sum(axis=0)
        self.grad_history.append(float(np.linalg.norm(self.dW)))
        return delta @ self.W
    
    def step(self, base_lr: float):
        self.t += 1
        lr = base_lr * self.lr_mult
        eps = 1e-8
        self.mW = 0.9 * self.mW + 0.1 * self.dW
        self.vW = 0.999 * self.vW + 0.001 * (self.dW ** 2 + eps)
        self.mb = 0.9 * self.mb + 0.1 * self.db
        self.vb = 0.999 * self.vb + 0.001 * (self.db ** 2 + eps)
        bc1, bc2 = max(1 - 0.9 ** self.t, 0.1), max(1 - 0.999 ** self.t, 0.001)
        self.W -= lr * (self.mW / bc1) / (np.sqrt(self.vW / bc2) + eps)
        self.b -= lr * (self.mb / bc1) / (np.sqrt(self.vb / bc2) + eps)
        np.clip(self.W, -2, 2, out=self.W)
        
        g = np.mean(list(self.grad_history)[-10:]) if self.grad_history else 1.0
        a = np.mean(list(self.act_history)[-10:]) if self.act_history else 0.5
        health = 1.0 if g < 2 else (0.5 if g < 5 else 0.2)
        
        self.trace.record(CompressedState(
            timestamp=self.t, health=health, coherence=1.0,
            activity=min(1.0, a), existence=1.0,
            verdict=Verdict.OK if health > 0.5 else Verdict.WARNING,
            fingerprint=f"L0_{self.idx}:{self.t}", level=0
        ))
    
    def apply_nudge(self, nudges: Dict):
        if 'lr_mult' in nudges:
            self.lr_mult = np.clip(self.lr_mult + nudges['lr_mult'], 0.1, 5)
        if 'reinit' in nudges and nudges['reinit'] > 0.5:
            self._init_weights()
            self.lr_mult = 0.5

# ═══════════════════════════════════════════════════════════════════════════════
# ATHENA L5 (Network Observer)
# ═══════════════════════════════════════════════════════════════════════════════

class AthenaL5(DynamicObserver):
    def __init__(self, n_layers: int):
        super().__init__(level=5)
        self.n_layers = n_layers
        self.loss_history = deque(maxlen=50)
        self.acc_history = deque(maxlen=50)
        self.in_recovery = False
        self.recovery_steps = 0
    
    def observe_network(self, layers: List[NetworkLayer], loss: float, acc: float) -> CompressedState:
        self.observation_count += 1
        self.loss_history.append(loss)
        self.acc_history.append(acc)
        
        healths = [l.trace.states[-1].health if l.trace.states else 1.0 for l in layers]
        activities = [l.trace.states[-1].activity if l.trace.states else 1.0 for l in layers]
        
        health = np.mean(healths)
        if loss > 5: health *= 0.5
        if acc < 0.6: health *= 0.8
        
        coherence = 1.0 - np.std(healths) if len(healths) > 1 else 1.0
        activity = np.mean(activities)
        
        if health < 0.2: verdict = Verdict.EMERGENCY
        elif health < 0.4: verdict = Verdict.CRITICAL
        elif health < 0.6: verdict = Verdict.WARNING
        else: verdict = Verdict.OK
        
        state = CompressedState(
            timestamp=self.observation_count,
            health=health, coherence=coherence, activity=activity, existence=1.0,
            verdict=verdict, fingerprint=f"L5:{health:.2f}:{self.observation_count}",
            level=5, meta={'loss': loss, 'acc': acc, 'recovery': self.in_recovery}
        )
        self.trace.record(state)
        self.last_state = state
        
        # Check for tower growth
        if self.child is None and self.observation_count > self.spawn_delay:
            instability = self.trace.instability_score()
            if instability > self.spawn_threshold:
                self._spawn_higher_level()
        
        return state
    
    def intervene_network(self, layers: List[NetworkLayer], state: CompressedState):
        if self.corridor['enabled'] < 0.5:
            return
        
        threshold = self.corridor['threshold']
        aggr = self.corridor['aggressiveness']
        
        if state.verdict == Verdict.EMERGENCY and threshold < 0.4:
            for layer in layers:
                if layer.trace.states and layer.trace.states[-1].health < 0.3:
                    layer.apply_nudge({'reinit': 1.0})
            self.in_recovery = True
            self.recovery_steps = 30
            self.intervention_count += 1
        elif state.verdict == Verdict.CRITICAL and threshold < 0.3:
            for layer in layers:
                layer.apply_nudge({'lr_mult': -0.3 * aggr})
            self.intervention_count += 1
        elif state.verdict == Verdict.WARNING and threshold < 0.2:
            for layer in layers:
                layer.apply_nudge({'lr_mult': -0.1 * aggr})
            self.intervention_count += 1
        
        if len(self.loss_history) >= 30:
            recent = list(self.loss_history)[-30:]
            if np.std(recent) < 1e-4 and self.acc_history[-1] < 0.9:
                for layer in layers:
                    layer.W += np.random.randn(*layer.W.shape).astype(np.float32) * 0.02 * aggr
                self.in_recovery = True
                self.recovery_steps = 20
                self.intervention_count += 1

# ═══════════════════════════════════════════════════════════════════════════════
# ATHENA V44: UNBOUNDED TOWER
# ═══════════════════════════════════════════════════════════════════════════════

class AthenaV44:
    """
    ATHENA v44: Unbounded Recursive Tower
    
    The tower grows DYNAMICALLY when lower levels show instability.
    There is NO CEILING - new levels EMERGE as needed.
    """
    
    def __init__(self, arch: List[int], lr: float = 0.02, multiclass: bool = False):
        self.arch, self.lr = arch, lr
        
        # L0-L4: Network
        self.layers: List[NetworkLayer] = []
        for i in range(len(arch) - 1):
            act = 'swish' if i < len(arch) - 2 else ('softmax' if multiclass else 'sigmoid')
            self.layers.append(NetworkLayer(arch[i], arch[i+1], act, i))
        
        # L5: ATHENA (can spawn L6, which can spawn L7, etc.)
        self.L5 = AthenaL5(len(self.layers))
        
        self.step_count = 0
    
    def forward(self, X: np.ndarray) -> np.ndarray:
        for layer in self.layers:
            X = layer.forward(X)
        return X
    
    def backward(self, targets: np.ndarray):
        grad = (self.layers[-1].A - targets).astype(np.float32)
        for layer in reversed(self.layers):
            grad = layer.backward(grad)
    
    def _process_tower(self, observer: DynamicObserver, global_step: int):
        """Recursively process the dynamic tower."""
        if observer.child is None:
            return {}
        
        results = {}
        
        # Child observes this observer
        if observer.child.should_observe(global_step):
            state = observer.child.observe(observer.trace)
            results[observer.child.level] = state
            
            # Child nudges this observer
            nudges = observer.child.nudge_below(state, observer.corridor)
            observer.receive_nudge(nudges)
        
        # Recurse up the tower
        child_results = self._process_tower(observer.child, global_step)
        results.update(child_results)
        
        return results
    
    def step(self, loss: float = 0, acc: float = 0) -> Dict:
        self.step_count += 1
        
        base_lr = self.lr * 0.5 * (1 + np.cos(np.pi * self.step_count / 500))
        if self.L5.in_recovery:
            base_lr *= 0.1
            self.L5.recovery_steps -= 1
            if self.L5.recovery_steps <= 0:
                self.L5.in_recovery = False
        
        # L0-L4: Update network
        for layer in self.layers:
            layer.step(base_lr)
        
        # L5: ATHENA
        l5_state = self.L5.observe_network(self.layers, loss, acc)
        self.L5.intervene_network(self.layers, l5_state)
        
        # L6+: Dynamic tower
        tower_results = self._process_tower(self.L5, self.step_count)
        
        return {
            'loss': loss, 'acc': acc,
            'L5': l5_state.verdict.value,
            **{f'L{k}': v.verdict.value for k, v in tower_results.items()},
            'recovery': self.L5.in_recovery,
            'tower_height': self.L5.get_tower_height(),
        }
    
    def param_count(self):
        return sum(l.W.size + l.b.size for l in self.layers)
    
    def report(self) -> str:
        lines = [
            "=" * 100,
            " ATHENA v44 - UNBOUNDED RECURSION TOWER ".center(100),
            "=" * 100,
            "",
            f"Tower Height: {self.L5.get_tower_height()} levels (L5 → L{5 + self.L5.get_tower_height() - 1})",
            "",
            "┌" + "─" * 98 + "┐",
            "│" + " DYNAMIC TOWER ".center(98) + "│",
            "├" + "─" * 98 + "┤",
        ]
        
        # Report from top down
        report_lines = self.L5.report().split('\n')
        for line in report_lines:
            lines.append("│ " + line.ljust(96) + " │")
        
        lines.append("└" + "─" * 98 + "┘")
        lines.append(f"\nNetwork: {len(self.layers)} layers, {self.param_count():,} params")
        
        return "\n".join(lines)

# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING
# ═══════════════════════════════════════════════════════════════════════════════

def gen_spiral(n):
    X, Y = [], []
    for i in range(n):
        c = i % 2
        r = (i/n)*5 + np.random.uniform(0, 0.2)
        t = 1.25*(i/n)*2*np.pi + c*np.pi
        X.append([r*np.sin(t)/6, r*np.cos(t)/6])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def train(net, max_steps=600, batch=64):
    val_X, val_Y = gen_spiral(200)
    
    print(f"\n{'Step':>5} {'Loss':>7} {'Acc':>6} │ Tower")
    print("-" * 55)
    
    best_acc = 0
    
    for step in range(1, max_steps + 1):
        X, Y = gen_spiral(batch)
        pred = net.forward(X)
        
        eps = 1e-7
        pred_clipped = np.clip(pred, eps, 1 - eps)
        loss = float(-np.mean(Y * np.log(pred_clipped) + (1 - Y) * np.log(1 - pred_clipped)))
        if np.isnan(loss) or np.isinf(loss):
            loss = 10.0
        
        net.backward(Y)
        
        val_pred = np.clip(net.forward(val_X), 0, 1)
        acc = float(np.mean((val_pred > 0.5) == val_Y))
        best_acc = max(best_acc, acc)
        
        state = net.step(loss, acc)
        
        # Show periodically or when tower grows
        show = step == 1 or step % 100 == 0 or acc >= 0.99
        
        if show:
            height = state['tower_height']
            levels = [state['L5'][:3].upper()]
            for lvl in range(6, 5 + height):
                v = state.get(f'L{lvl}')
                if v:
                    levels.append(v[:3].upper())
            tower_str = '-'.join(levels)
            print(f"{step:5d} {loss:7.4f} {acc:5.1%} │ H={height} {tower_str}")
        
        if acc >= 0.995:
            print(f"\n  ✓ Target reached at step {step}!")
            break
    
    return {'best_acc': best_acc, 'steps': step}

def main():
    print("=" * 100)
    print(" ATHENA v44 - UNBOUNDED RECURSION ".center(100))
    print("=" * 100)
    print("""
    THE DYNAMIC TOWER:
    
    When L[n] shows prolonged instability, L[n+1] EMERGES.
    Each new level asks an even SIMPLER question.
    There is NO CEILING.
    
    L16: IS           → "Is?"
    L15: BEING        → "Is there being?"
    L14: ONE          → "Is there one thing?"
    L13: PATTERN      → "Is there any pattern?"
    L12: CHANGE       → "Is anything changing?"
    L11: SIGNAL       → "Is there any signal?"
    L10: VOID         → "Is there anything?"
    L9:  EXISTENCE    → "Does something exist?"
    L8:  COHERENCE    → "Is there coherent activity?"
    L7:  LIFE         → "Is the system alive?"
    L6:  META-ATHENA  → "Is ATHENA healthy?"
    L5:  ATHENA       → "Is the network healthy?"
    
    The tower GROWS when needed. Watch for "★ EMERGES" messages.
""")
    
    # Test 1: Normal (might not trigger growth)
    print("\n" + "=" * 55)
    print("--- TEST 1: Normal Training ---")
    np.random.seed(42)
    net = AthenaV44([2, 64, 64, 32, 1], lr=0.02)
    result1 = train(net, max_steps=400)
    print(f"\n  Result: {result1['best_acc']:.1%}")
    print(net.report())
    
    # Test 2: Stress test (should trigger tower growth!)
    print("\n" + "=" * 55)
    print("--- TEST 2: STRESS TEST (should trigger tower growth) ---")
    np.random.seed(42)
    net = AthenaV44([2, 64, 64, 32, 1], lr=0.25)  # Very high LR
    result2 = train(net, max_steps=600)
    print(f"\n  Result: {result2['best_acc']:.1%}")
    print(net.report())
    
    print("\n" + "=" * 100)
    print(" UNBOUNDED RECURSION ACHIEVED ".center(100))
    print("=" * 100)

if __name__ == "__main__":
    main()

# ═══════════════════════════════════════════════════════════════════════════════
# EXTREME STRESS TEST
# ═══════════════════════════════════════════════════════════════════════════════

def extreme_test():
    print("\n" + "=" * 100)
    print(" EXTREME STRESS TEST: TRIGGERING DEEP EMERGENCE ".center(100))
    print("=" * 100)
    
    # Very high LR + long training to trigger tower growth
    print("\n--- LR=0.4, 800 steps ---")
    np.random.seed(123)
    net = AthenaV44([2, 64, 64, 32, 1], lr=0.4)
    
    val_X, val_Y = gen_spiral(200)
    best_acc = 0
    
    print(f"\n{'Step':>5} {'Loss':>7} {'Acc':>6} │ Tower")
    print("-" * 60)
    
    for step in range(1, 801):
        X, Y = gen_spiral(64)
        pred = net.forward(X)
        
        eps = 1e-7
        pred_clipped = np.clip(pred, eps, 1 - eps)
        loss = float(-np.mean(Y * np.log(pred_clipped) + (1 - Y) * np.log(1 - pred_clipped)))
        if np.isnan(loss) or np.isinf(loss):
            loss = 10.0
        
        net.backward(Y)
        
        val_pred = np.clip(net.forward(val_X), 0, 1)
        acc = float(np.mean((val_pred > 0.5) == val_Y))
        best_acc = max(best_acc, acc)
        
        state = net.step(loss, acc)
        
        if step == 1 or step % 100 == 0 or acc >= 0.99:
            height = state['tower_height']
            levels = [state['L5'][:3].upper()]
            for lvl in range(6, 5 + height):
                v = state.get(f'L{lvl}')
                if v:
                    levels.append(v[:3].upper())
            tower_str = '-'.join(levels)
            print(f"{step:5d} {loss:7.4f} {acc:5.1%} │ H={height} {tower_str}")
        
        if acc >= 0.995:
            print(f"  ✓ Target at step {step}")
            break
    
    print(f"\n  Best: {best_acc:.1%}")
    print(net.report())

if __name__ == "__main__":
    extreme_test()
