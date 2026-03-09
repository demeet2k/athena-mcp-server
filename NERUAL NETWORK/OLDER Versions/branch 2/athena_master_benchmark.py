"""
╔══════════════════════════════════════════════════════════════════════════════════════════╗
║                    ATHENA BRANCH 2 - MASTER BENCHMARK SUITE                               ║
║                         Deep Diagnostic Testing Framework                                 ║
╚══════════════════════════════════════════════════════════════════════════════════════════╝

PURPOSE:
========
This is the DEFINITIVE benchmark suite for ATHENA Branch 2. It tests every aspect of 
neural network optimization under every conceivable condition. The deeper our testing,
the better we understand where each strategy excels and fails.

TEST CATEGORIES:
================
1.  CONVERGENCE TESTS          - Basic learning on 8 datasets
2.  LEARNING RATE STRESS       - 12 LR levels from 0.001 to 2.0
3.  PERTURBATION RECOVERY      - 10 magnitudes from 0.1 to 5.0
4.  ARCHITECTURE TESTS         - 12 network configurations
5.  MULTI-PERTURBATION         - Repeated shocks (1-20)
6.  REGIME TRANSITION          - Force regime changes mid-training
7.  RECOVERY DYNAMICS          - Time-to-recovery analysis
8.  GRADIENT PATHOLOGY         - Exploding/vanishing scenarios
9.  NOISE ROBUSTNESS           - Label noise, input noise
10. LONG-RUN STABILITY         - 1000+ step training
11. WARMUP SENSITIVITY         - Different warmup strategies
12. MOMENTUM ANALYSIS          - Momentum coefficient variations
13. BATCH SIZE EFFECTS         - From 8 to 512
14. INITIALIZATION TESTS       - Different init strategies
15. COMBINED STRESS            - Multiple stressors simultaneously
16. EDGE CASES                 - Extreme conditions

TOTAL TESTS: 200+ configurations
ESTIMATED TIME: ~10 minutes (full), ~2 minutes (quick)

USAGE:
======
    python athena_master_benchmark.py                    # Quick benchmark
    python athena_master_benchmark.py --full             # Full benchmark
    python athena_master_benchmark.py --category lr      # Specific category
    python athena_master_benchmark.py --export results   # Export to CSV
"""

import numpy as np
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum, auto
import time
import sys
import json

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 1: IMPORTS FROM BRANCH 2 FINAL (inline for standalone use)
# ═══════════════════════════════════════════════════════════════════════════════════════════

class Regime(Enum):
    NORMAL = auto()
    PERTURBATION = auto()
    MODERATE_CHAOS = auto()
    EXTREME_CHAOS = auto()
    VANISHING = auto()
    DEAD = auto()

class HealthStatus(Enum):
    HEALTHY = "healthy"
    STRESSED = "stressed"
    VANISHING = "vanishing"
    EXPLODING = "exploding"
    DEAD = "dead"

class NudgeType(Enum):
    CORRIDOR = auto()
    BUDGET = auto()
    SALIENCE = auto()
    COUPLING = auto()

@dataclass
class ConfigV1:
    explosion_threshold: float = 100.0
    consecutive_required: int = 3
    warmup_steps: int = 20
    warmup_min: float = 0.1
    vanishing_threshold: float = 0.01
    vanishing_steps: int = 30
    vanishing_boost: float = 2.0

@dataclass
class ConfigV3:
    explosion_threshold: float = 100.0
    consecutive_required: int = 5
    dead_threshold: float = 0.001
    stress_lr_mult: float = 0.2
    stress_duration: int = 30
    stress_grad_clip: float = 0.1
    vanishing_threshold: float = 0.01
    vanishing_steps: int = 30
    vanishing_boost: float = 2.0

@dataclass
class ConfigV7:
    explosion_threshold: float = 100.0
    vanishing_threshold: float = 0.001
    dead_threshold: float = 0.0001
    confidence_threshold: float = 0.7
    cooldown_steps: int = 30
    explosion_window: int = 5
    vanishing_window: int = 30
    perturbation_drop: float = 0.25
    stable_threshold: float = 0.85
    output_fragility: float = 2.0
    hidden_fragility: float = 1.0
    input_fragility: float = 1.5

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 2: CORE LAYER CLASS
# ═══════════════════════════════════════════════════════════════════════════════════════════

class Layer:
    def __init__(self, nin: int, nout: int, act: str = 'swish', seed: int = 42,
                 init: str = 'he'):
        self.nin, self.nout, self.act, self.seed = nin, nout, act, seed
        rng = np.random.RandomState(seed)
        
        # Initialization
        if init == 'he':
            self.W = rng.randn(nout, nin).astype(np.float32) * np.sqrt(2.0 / nin)
        elif init == 'xavier':
            self.W = rng.randn(nout, nin).astype(np.float32) * np.sqrt(2.0 / (nin + nout))
        elif init == 'small':
            self.W = rng.randn(nout, nin).astype(np.float32) * 0.01
        elif init == 'large':
            self.W = rng.randn(nout, nin).astype(np.float32) * 1.0
        else:
            self.W = rng.randn(nout, nin).astype(np.float32) * np.sqrt(2.0 / nin)
        
        self.b = np.zeros(nout, dtype=np.float32)
        self.mW = np.zeros_like(self.W)
        self.vW = np.zeros_like(self.W)
        self.mb = np.zeros_like(self.b)
        self.vb = np.zeros_like(self.b)
        self.t = 0
        self.grad_norm = 0.0
        self.reinits = 0
        self.dW = None
        self.db = None
    
    def forward(self, X: np.ndarray) -> np.ndarray:
        self.X = np.clip(X.astype(np.float32), -50, 50)
        self.Z = np.clip(self.X @ self.W.T + self.b, -30, 30)
        if self.act == 'swish':
            self.sig = 1.0 / (1.0 + np.exp(-np.clip(self.Z, -15, 15)))
            self.A = self.Z * self.sig
        elif self.act == 'relu':
            self.A = np.maximum(0, self.Z)
        elif self.act == 'tanh':
            self.A = np.tanh(self.Z)
        else:
            self.A = 1.0 / (1.0 + np.exp(-np.clip(self.Z, -15, 15)))
        return np.clip(self.A, -10, 10)
    
    def backward(self, grad: np.ndarray, clip: float = 1.0) -> np.ndarray:
        grad = np.clip(grad.astype(np.float32), -5, 5)
        if self.act == 'swish':
            delta = grad * (self.sig + self.Z * self.sig * (1 - self.sig))
        elif self.act == 'relu':
            delta = grad * (self.Z > 0).astype(np.float32)
        elif self.act == 'tanh':
            delta = grad * (1 - self.A ** 2)
        else:
            delta = grad * self.A * (1 - self.A)
        delta = np.clip(delta, -clip, clip)
        self.dW = delta.T @ self.X
        self.db = delta.sum(axis=0)
        self.grad_norm = float(np.linalg.norm(self.dW))
        return delta @ self.W
    
    def step(self, lr: float, momentum: float = 0.9):
        self.t += 1
        eps = 1e-8
        self.mW = momentum * self.mW + (1 - momentum) * self.dW
        self.vW = 0.999 * self.vW + 0.001 * (self.dW ** 2 + eps)
        self.mb = momentum * self.mb + (1 - momentum) * self.db
        self.vb = 0.999 * self.vb + 0.001 * (self.db ** 2 + eps)
        bc1 = max(1 - momentum ** self.t, 0.1)
        bc2 = max(1 - 0.999 ** self.t, 0.001)
        self.W -= lr * (self.mW / bc1) / (np.sqrt(self.vW / bc2) + eps)
        self.b -= lr * (self.mb / bc1) / (np.sqrt(self.vb / bc2) + eps)
        np.clip(self.W, -2, 2, out=self.W)
    
    def reinit(self):
        self.reinits += 1
        rng = np.random.RandomState(self.seed + self.reinits * 100)
        self.W = rng.randn(self.nout, self.nin).astype(np.float32) * np.sqrt(2.0 / self.nin)
        self.b = np.zeros(self.nout, dtype=np.float32)
        self.mW.fill(0); self.vW.fill(0); self.mb.fill(0); self.vb.fill(0)
        self.t = 0

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 3: ATHENA VERSIONS
# ═══════════════════════════════════════════════════════════════════════════════════════════

class AthenaB2V1:
    """V1: Emergency Reinit - Best at high LR"""
    def __init__(self, arch: List[int], lr: float = 0.02, cfg: ConfigV1 = None,
                 init: str = 'he', momentum: float = 0.9):
        self.arch, self.base_lr, self.cfg = arch, lr, cfg or ConfigV1()
        self.momentum = momentum
        self.layers = [Layer(arch[i], arch[i+1], 
                            'swish' if i < len(arch)-2 else 'sigmoid',
                            i*1000+42, init) for i in range(len(arch)-1)]
        self.t = self.consec_explosions = self.consec_vanishing = 0
        self.in_warmup = self.in_boost = False
        self.warmup_step = self.emergencies = self.boosts = 0
        self.acc_history = []
        self.grad_history = []
    
    def forward(self, X):
        for layer in self.layers: X = layer.forward(X)
        return X
    
    def backward(self, Y):
        grad = (self.layers[-1].A - Y).astype(np.float32)
        clip = 0.1 if self.consec_explosions > 0 else 1.0
        for layer in reversed(self.layers): grad = layer.backward(grad, clip)
    
    def step(self, loss, acc):
        self.t += 1
        self.acc_history.append(acc)
        grad_max = max(l.grad_norm for l in self.layers)
        grad_mean = np.mean([l.grad_norm for l in self.layers])
        self.grad_history.append(grad_mean)
        
        if grad_max > self.cfg.explosion_threshold or loss > 5:
            self.consec_explosions += 1
            self.consec_vanishing = 0
            if self.consec_explosions >= self.cfg.consecutive_required:
                self.emergencies += 1
                for layer in self.layers: layer.reinit()
                self.in_warmup, self.warmup_step, self.consec_explosions = True, 0, 0
        else:
            self.consec_explosions = max(0, self.consec_explosions - 1)
            if grad_mean < self.cfg.vanishing_threshold and not self.in_warmup:
                self.consec_vanishing += 1
                if self.consec_vanishing >= self.cfg.vanishing_steps and not self.in_boost:
                    self.in_boost, self.boosts = True, self.boosts + 1
            else:
                self.consec_vanishing = 0
                if self.in_boost and grad_mean > self.cfg.vanishing_threshold * 10:
                    self.in_boost = False
        
        lr = self.base_lr * 0.5 * (1 + np.cos(np.pi * self.t / 500))
        if self.in_warmup:
            self.warmup_step += 1
            progress = self.warmup_step / self.cfg.warmup_steps
            lr *= self.cfg.warmup_min + (1 - self.cfg.warmup_min) * (1 - np.cos(np.pi * progress)) / 2
            if self.warmup_step >= self.cfg.warmup_steps: self.in_warmup = False
        elif self.in_boost:
            lr *= self.cfg.vanishing_boost
        
        for layer in self.layers: layer.step(lr, self.momentum)
        return {'emergencies': self.emergencies, 'boosts': self.boosts}
    
    def perturb(self, mag=0.5):
        for layer in self.layers:
            layer.W += np.random.randn(*layer.W.shape).astype(np.float32) * mag

class AthenaB2V3:
    """V3: Stress Mode - Best at perturbation recovery"""
    def __init__(self, arch: List[int], lr: float = 0.02, cfg: ConfigV3 = None,
                 init: str = 'he', momentum: float = 0.9):
        self.arch, self.base_lr, self.cfg = arch, lr, cfg or ConfigV3()
        self.momentum = momentum
        self.layers = [Layer(arch[i], arch[i+1],
                            'swish' if i < len(arch)-2 else 'sigmoid',
                            i*1000+42, init) for i in range(len(arch)-1)]
        self.t = self.consec_explosions = self.consec_vanishing = 0
        self.in_stress = self.in_boost = False
        self.stress_step = 0
        self.emergencies = self.stress_triggers = self.boosts = 0
        self.acc_history = []
        self.grad_history = []
    
    def forward(self, X):
        for layer in self.layers: X = layer.forward(X)
        return X
    
    def backward(self, Y):
        grad = (self.layers[-1].A - Y).astype(np.float32)
        clip = self.cfg.stress_grad_clip if self.in_stress else 1.0
        for layer in reversed(self.layers): grad = layer.backward(grad, clip)
    
    def step(self, loss, acc):
        self.t += 1
        self.acc_history.append(acc)
        grad_max = max(l.grad_norm for l in self.layers)
        grad_mean = np.mean([l.grad_norm for l in self.layers])
        self.grad_history.append(grad_mean)
        
        if grad_mean < self.cfg.dead_threshold and self.t > 50:
            self.emergencies += 1
            for layer in self.layers: layer.reinit()
            self.in_stress, self.stress_step, self.consec_explosions = True, 0, 0
        elif grad_max > self.cfg.explosion_threshold or loss > 5:
            self.consec_explosions += 1
            self.consec_vanishing = 0
            if self.consec_explosions >= self.cfg.consecutive_required and not self.in_stress:
                self.in_stress, self.stress_step = True, 0
                self.stress_triggers += 1
                self.consec_explosions = 0
        else:
            self.consec_explosions = max(0, self.consec_explosions - 1)
            if grad_mean < self.cfg.vanishing_threshold and not self.in_stress:
                self.consec_vanishing += 1
                if self.consec_vanishing >= self.cfg.vanishing_steps and not self.in_boost:
                    self.in_boost, self.boosts = True, self.boosts + 1
            else:
                self.consec_vanishing = 0
                if self.in_boost and grad_mean > self.cfg.vanishing_threshold * 10:
                    self.in_boost = False
        
        if self.in_stress:
            self.stress_step += 1
            if self.stress_step >= self.cfg.stress_duration: self.in_stress = False
        
        lr = self.base_lr * 0.5 * (1 + np.cos(np.pi * self.t / 500))
        if self.in_stress:
            lr *= self.cfg.stress_lr_mult
        elif self.in_boost:
            lr *= self.cfg.vanishing_boost
        
        for layer in self.layers: layer.step(lr, self.momentum)
        return {'emergencies': self.emergencies, 'stress': self.stress_triggers}
    
    def perturb(self, mag=0.5):
        for layer in self.layers:
            layer.W += np.random.randn(*layer.W.shape).astype(np.float32) * mag

class Adam:
    """Standard Adam baseline"""
    def __init__(self, arch: List[int], lr: float = 0.02, init: str = 'he',
                 momentum: float = 0.9, **kwargs):
        self.arch, self.lr, self.t = arch, lr, 0
        self.momentum = momentum
        self.layers = []
        for i in range(len(arch) - 1):
            rng = np.random.RandomState(i * 1000 + 42)
            if init == 'he':
                W = rng.randn(arch[i+1], arch[i]).astype(np.float32) * np.sqrt(2.0 / arch[i])
            elif init == 'xavier':
                W = rng.randn(arch[i+1], arch[i]).astype(np.float32) * np.sqrt(2.0 / (arch[i] + arch[i+1]))
            else:
                W = rng.randn(arch[i+1], arch[i]).astype(np.float32) * np.sqrt(2.0 / arch[i])
            self.layers.append({
                'W': W, 'b': np.zeros(arch[i+1], dtype=np.float32),
                'mW': np.zeros_like(W), 'vW': np.zeros_like(W),
                'mb': np.zeros(arch[i+1], dtype=np.float32),
                'vb': np.zeros(arch[i+1], dtype=np.float32)
            })
        self.acc_history = []
        self.grad_history = []
        self.emergencies = 0
    
    def forward(self, X):
        self.acts = [X.astype(np.float32)]
        A = X.astype(np.float32)
        for i, l in enumerate(self.layers):
            Z = np.clip(A @ l['W'].T + l['b'], -30, 30)
            if i < len(self.layers) - 1:
                sig = 1.0 / (1.0 + np.exp(-np.clip(Z, -15, 15)))
                A = Z * sig
            else:
                A = 1.0 / (1.0 + np.exp(-np.clip(Z, -15, 15)))
            self.acts.append(A)
        return A
    
    def backward(self, Y):
        self.t += 1
        delta = self.acts[-1] - Y
        grads = []
        for i in reversed(range(len(self.layers))):
            grads.insert(0, (delta.T @ self.acts[i], delta.sum(axis=0)))
            if i > 0:
                Z = self.acts[i]
                sig = 1.0 / (1.0 + np.exp(-np.clip(Z, -15, 15)))
                delta = (delta @ self.layers[i]['W']) * (sig + Z * sig * (1 - sig))
        
        lr = self.lr * 0.5 * (1 + np.cos(np.pi * self.t / 500))
        grad_norms = []
        for l, (dW, db) in zip(self.layers, grads):
            grad_norms.append(np.linalg.norm(dW))
            eps = 1e-8
            l['mW'] = self.momentum * l['mW'] + (1 - self.momentum) * dW
            l['vW'] = 0.999 * l['vW'] + 0.001 * (dW ** 2 + eps)
            l['mb'] = self.momentum * l['mb'] + (1 - self.momentum) * db
            l['vb'] = 0.999 * l['vb'] + 0.001 * (db ** 2 + eps)
            bc1, bc2 = max(1 - self.momentum ** self.t, 0.1), max(1 - 0.999 ** self.t, 0.001)
            l['W'] -= lr * (l['mW'] / bc1) / (np.sqrt(l['vW'] / bc2) + eps)
            l['b'] -= lr * (l['mb'] / bc1) / (np.sqrt(l['vb'] / bc2) + eps)
            np.clip(l['W'], -2, 2, out=l['W'])
        self.grad_history.append(np.mean(grad_norms))
    
    def step(self, loss, acc):
        self.acc_history.append(acc)
        return {}
    
    def perturb(self, mag=0.5):
        for l in self.layers:
            l['W'] += np.random.randn(*l['W'].shape).astype(np.float32) * mag

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 4: DATASET GENERATORS (Extended)
# ═══════════════════════════════════════════════════════════════════════════════════════════

def spiral(n, noise=0.0):
    X, Y = [], []
    for i in range(n):
        c = i % 2
        r = (i / n) * 5 + np.random.uniform(0, 0.1)
        t = 1.25 * (i / n) * 2 * np.pi + c * np.pi
        x = r * np.sin(t) / 6 + np.random.randn() * noise
        y = r * np.cos(t) / 6 + np.random.randn() * noise
        X.append([x, y])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def checkerboard(n, noise=0.0):
    X, Y = [], []
    for _ in range(n):
        x, y = np.random.uniform(-1, 1), np.random.uniform(-1, 1)
        c = (int((x + 1) * 2) + int((y + 1) * 2)) % 2
        X.append([x + np.random.randn() * noise, y + np.random.randn() * noise])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def moons(n, noise=0.0):
    X, Y = [], []
    for i in range(n):
        if i % 2 == 0:
            theta = np.random.uniform(0, np.pi)
            X.append([np.cos(theta) + np.random.randn() * noise,
                     np.sin(theta) + np.random.randn() * noise])
            Y.append([0.0])
        else:
            theta = np.random.uniform(0, np.pi)
            X.append([1 - np.cos(theta) + np.random.randn() * noise,
                     0.5 - np.sin(theta) + np.random.randn() * noise])
            Y.append([1.0])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def rings(n, noise=0.0):
    X, Y = [], []
    for _ in range(n):
        r = np.random.uniform(0, 1)
        theta = np.random.uniform(0, 2 * np.pi)
        c = 0 if r < 0.5 else 1
        X.append([r * np.cos(theta) + np.random.randn() * noise,
                 r * np.sin(theta) + np.random.randn() * noise])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def xor(n, noise=0.0):
    X, Y = [], []
    centers = [(-0.5, -0.5, 0), (-0.5, 0.5, 1), (0.5, -0.5, 1), (0.5, 0.5, 0)]
    for i in range(n):
        cx, cy, c = centers[i % 4]
        X.append([cx + np.random.randn() * (0.1 + noise),
                 cy + np.random.randn() * (0.1 + noise)])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def gaussian_clusters(n, n_clusters=4, noise=0.0):
    """Random Gaussian clusters - varying difficulty"""
    X, Y = [], []
    rng = np.random.RandomState(42)
    centers = rng.uniform(-1, 1, (n_clusters, 2))
    for i in range(n):
        c = i % n_clusters
        label = c % 2
        X.append([centers[c, 0] + rng.randn() * (0.2 + noise),
                 centers[c, 1] + rng.randn() * (0.2 + noise)])
        Y.append([float(label)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def sine_wave(n, noise=0.0):
    """Points above/below sine wave"""
    X, Y = [], []
    for _ in range(n):
        x = np.random.uniform(-np.pi, np.pi)
        y = np.random.uniform(-1.5, 1.5)
        c = 1 if y > np.sin(x) else 0
        X.append([x / np.pi + np.random.randn() * noise,
                 y / 1.5 + np.random.randn() * noise])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

def nested_circles(n, noise=0.0):
    """Three nested circles"""
    X, Y = [], []
    for i in range(n):
        r = np.random.choice([0.3, 0.6, 0.9])
        theta = np.random.uniform(0, 2 * np.pi)
        c = 0 if r == 0.6 else 1
        X.append([r * np.cos(theta) + np.random.randn() * noise,
                 r * np.sin(theta) + np.random.randn() * noise])
        Y.append([float(c)])
    return np.array(X, dtype=np.float32), np.array(Y, dtype=np.float32)

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 5: TRAINING UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════════════════

@dataclass
class TrainingResult:
    """Comprehensive training result"""
    final_acc: float
    best_acc: float
    steps_to_95: int
    steps_to_90: int
    steps_to_80: int
    emergencies: int
    stress_triggers: int
    boosts: int
    final_grad_norm: float
    avg_grad_norm: float
    max_grad_norm: float
    min_grad_norm: float
    acc_variance: float
    recovery_time: int  # Steps to recover after perturbation
    total_steps: int
    training_time: float
    acc_history: List[float]
    grad_history: List[float]

def train_detailed(net, ds_fn, steps: int = 250, batch: int = 64,
                   perturbation: Optional[Tuple[int, float]] = None,
                   label_noise: float = 0.0,
                   input_noise: float = 0.0) -> TrainingResult:
    """
    Detailed training with comprehensive metrics.
    
    Args:
        net: Network to train
        ds_fn: Dataset function
        steps: Total training steps
        batch: Batch size
        perturbation: Optional (step, magnitude) for mid-training perturbation
        label_noise: Probability of flipping labels
        input_noise: Gaussian noise added to inputs
    """
    start_time = time.time()
    val_X, val_Y = ds_fn(200)
    
    best_acc = 0.0
    t95, t90, t80 = 9999, 9999, 9999
    pre_perturb_acc = 0.0
    recovery_time = 0
    recovering = False
    
    acc_history = []
    grad_history = []
    
    for step in range(1, steps + 1):
        X, Y = ds_fn(batch)
        
        # Add input noise
        if input_noise > 0:
            X = X + np.random.randn(*X.shape).astype(np.float32) * input_noise
        
        # Add label noise
        if label_noise > 0:
            flip_mask = np.random.random(len(Y)) < label_noise
            Y = Y.copy()
            Y[flip_mask] = 1 - Y[flip_mask]
        
        # Forward
        pred = net.forward(X)
        loss = float(-np.mean(
            Y * np.log(np.clip(pred, 1e-7, 1 - 1e-7)) +
            (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1 - 1e-7))
        ))
        if np.isnan(loss):
            loss = 10.0
        
        # Backward
        net.backward(Y)
        
        # Validate
        val_pred = net.forward(val_X)
        acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
        acc_history.append(acc)
        
        # Track gradients
        if hasattr(net, 'layers'):
            if isinstance(net.layers[0], dict):
                grad_norm = np.mean([np.linalg.norm(l.get('mW', 0)) for l in net.layers])
            else:
                grad_norm = np.mean([l.grad_norm for l in net.layers])
        else:
            grad_norm = 0.0
        grad_history.append(grad_norm)
        
        # Update
        if hasattr(net, 'step'):
            net.step(loss, acc)
        
        # Track milestones
        best_acc = max(best_acc, acc)
        if acc >= 0.95 and t95 == 9999:
            t95 = step
        if acc >= 0.90 and t90 == 9999:
            t90 = step
        if acc >= 0.80 and t80 == 9999:
            t80 = step
        
        # Apply perturbation
        if perturbation and step == perturbation[0]:
            pre_perturb_acc = acc
            net.perturb(perturbation[1])
            recovering = True
        
        # Track recovery
        if recovering and acc >= pre_perturb_acc * 0.95:
            recovery_time = step - perturbation[0]
            recovering = False
    
    training_time = time.time() - start_time
    
    return TrainingResult(
        final_acc=acc_history[-1] if acc_history else 0.0,
        best_acc=best_acc,
        steps_to_95=t95,
        steps_to_90=t90,
        steps_to_80=t80,
        emergencies=getattr(net, 'emergencies', 0),
        stress_triggers=getattr(net, 'stress_triggers', 0),
        boosts=getattr(net, 'boosts', 0),
        final_grad_norm=grad_history[-1] if grad_history else 0.0,
        avg_grad_norm=np.mean(grad_history) if grad_history else 0.0,
        max_grad_norm=np.max(grad_history) if grad_history else 0.0,
        min_grad_norm=np.min(grad_history) if grad_history else 0.0,
        acc_variance=np.var(acc_history[-50:]) if len(acc_history) >= 50 else 0.0,
        recovery_time=recovery_time,
        total_steps=steps,
        training_time=training_time,
        acc_history=acc_history,
        grad_history=grad_history
    )

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 6: BENCHMARK CATEGORIES
# ═══════════════════════════════════════════════════════════════════════════════════════════

class BenchmarkSuite:
    """Master benchmark suite with all test categories"""
    
    def __init__(self, versions: Dict[str, type] = None, verbose: bool = True):
        self.versions = versions or {
            'v1': AthenaB2V1,
            'v3': AthenaB2V3,
            'Adam': Adam
        }
        self.verbose = verbose
        self.results = {}
    
    def _print(self, msg: str):
        if self.verbose:
            print(msg)
    
    def _header(self, title: str):
        self._print("\n" + "=" * 90)
        self._print(f"  {title}")
        self._print("=" * 90)
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 1: CONVERGENCE TESTS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_convergence(self) -> Dict:
        """Test convergence on 8 datasets"""
        self._header("CATEGORY 1: CONVERGENCE TESTS (8 datasets)")
        
        datasets = {
            'Spiral': lambda n: spiral(n),
            'Checkerboard': lambda n: checkerboard(n),
            'Moons': lambda n: moons(n),
            'Rings': lambda n: rings(n),
            'XOR': lambda n: xor(n),
            'Gaussian-4': lambda n: gaussian_clusters(n, 4),
            'Gaussian-8': lambda n: gaussian_clusters(n, 8),
            'SineWave': lambda n: sine_wave(n),
        }
        
        results = {}
        arch = [2, 64, 32, 1]
        
        for ds_name, ds_fn in datasets.items():
            results[ds_name] = {}
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, ds_fn, steps=250)
                results[ds_name][v_name] = {
                    'acc': res.best_acc,
                    't95': res.steps_to_95,
                    'emergencies': res.emergencies
                }
            
            self._print(f"\n{ds_name}:")
            for v_name, res in results[ds_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}% (t95={res['t95']})")
        
        self.results['convergence'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 2: LEARNING RATE STRESS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_learning_rate(self) -> Dict:
        """Test 12 learning rate levels"""
        self._header("CATEGORY 2: LEARNING RATE STRESS (12 levels)")
        
        learning_rates = [0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0]
        results = {}
        arch = [2, 64, 32, 1]
        
        for lr in learning_rates:
            results[lr] = {}
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=lr)
                res = train_detailed(net, spiral, steps=250)
                results[lr][v_name] = {
                    'acc': res.best_acc,
                    'emergencies': res.emergencies,
                    'max_grad': res.max_grad_norm,
                    'variance': res.acc_variance
                }
            
            self._print(f"\nLR={lr}:")
            for v_name, res in results[lr].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}% (em={res['emergencies']})")
        
        self.results['learning_rate'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 3: PERTURBATION RECOVERY
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_perturbation(self) -> Dict:
        """Test 10 perturbation magnitudes"""
        self._header("CATEGORY 3: PERTURBATION RECOVERY (10 magnitudes)")
        
        magnitudes = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0]
        results = {}
        arch = [2, 64, 32, 1]
        
        for mag in magnitudes:
            results[mag] = {}
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, spiral, steps=300, perturbation=(100, mag))
                results[mag][v_name] = {
                    'acc': res.best_acc,
                    'recovery_time': res.recovery_time,
                    'emergencies': res.emergencies
                }
            
            self._print(f"\nMagnitude={mag}:")
            for v_name, res in results[mag].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}% (recovery={res['recovery_time']})")
        
        self.results['perturbation'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 4: ARCHITECTURE TESTS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_architectures(self) -> Dict:
        """Test 12 network architectures"""
        self._header("CATEGORY 4: ARCHITECTURE TESTS (12 configs)")
        
        architectures = {
            'Tiny-1L': [2, 8, 1],
            'Tiny-2L': [2, 16, 1],
            'Small': [2, 32, 16, 1],
            'Medium': [2, 64, 32, 1],
            'Large': [2, 128, 64, 1],
            'XLarge': [2, 256, 128, 1],
            'Deep-3': [2, 32, 32, 32, 1],
            'Deep-4': [2, 32, 32, 32, 32, 1],
            'Deep-5': [2, 32, 32, 32, 32, 32, 1],
            'Wide': [2, 256, 1],
            'XWide': [2, 512, 1],
            'Bottleneck': [2, 128, 8, 128, 1],
        }
        
        results = {}
        for arch_name, arch in architectures.items():
            results[arch_name] = {}
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, spiral, steps=250)
                results[arch_name][v_name] = {
                    'acc': res.best_acc,
                    't95': res.steps_to_95,
                    'params': sum(arch[i] * arch[i+1] for i in range(len(arch)-1))
                }
            
            self._print(f"\n{arch_name}:")
            for v_name, res in results[arch_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['architectures'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 5: MULTI-PERTURBATION
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_multi_perturbation(self) -> Dict:
        """Test repeated perturbations"""
        self._header("CATEGORY 5: MULTI-PERTURBATION (1-20 shocks)")
        
        counts = [1, 2, 3, 5, 7, 10, 15, 20]
        results = {}
        arch = [2, 64, 32, 1]
        
        for count in counts:
            results[count] = {}
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                val_X, val_Y = spiral(200)
                
                # Initial training
                for step in range(50):
                    X, Y = spiral(64)
                    pred = net.forward(X)
                    loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                         (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                    net.backward(Y)
                    if hasattr(net, 'step'):
                        net.step(loss, 0.0)
                
                # Multiple perturbations
                for p in range(count):
                    net.perturb(0.5)
                    for step in range(20):
                        X, Y = spiral(64)
                        pred = net.forward(X)
                        loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                             (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                        net.backward(Y)
                        val_pred = net.forward(val_X)
                        acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                        if hasattr(net, 'step'):
                            net.step(loss, acc)
                
                val_pred = net.forward(val_X)
                final_acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                results[count][v_name] = {'acc': final_acc}
            
            self._print(f"\n{count} perturbations:")
            for v_name, res in results[count].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['multi_perturbation'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 6: REGIME TRANSITION
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_regime_transitions(self) -> Dict:
        """Test forced regime transitions mid-training"""
        self._header("CATEGORY 6: REGIME TRANSITIONS")
        
        scenarios = {
            'Normal→Perturbation': {'perturbation': (100, 1.5)},
            'Normal→HighLR': {'lr_change': (100, 0.5)},
            'Normal→Chaos': {'lr_change': (100, 1.0)},
            'Stable→MultiShock': {'multi_perturb': [(100, 1.0), (150, 1.0), (200, 1.0)]},
        }
        
        results = {}
        arch = [2, 64, 32, 1]
        
        for scenario_name, params in scenarios.items():
            results[scenario_name] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                val_X, val_Y = spiral(200)
                
                current_lr = 0.02
                acc_history = []
                
                for step in range(1, 301):
                    X, Y = spiral(64)
                    pred = net.forward(X)
                    loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                         (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                    net.backward(Y)
                    val_pred = net.forward(val_X)
                    acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                    acc_history.append(acc)
                    
                    if hasattr(net, 'step'):
                        net.step(loss, acc)
                    
                    # Apply transitions
                    if 'perturbation' in params and step == params['perturbation'][0]:
                        net.perturb(params['perturbation'][1])
                    
                    if 'lr_change' in params and step == params['lr_change'][0]:
                        net.base_lr = params['lr_change'][1]
                    
                    if 'multi_perturb' in params:
                        for p_step, p_mag in params['multi_perturb']:
                            if step == p_step:
                                net.perturb(p_mag)
                
                results[scenario_name][v_name] = {
                    'final_acc': acc_history[-1],
                    'min_acc_after': min(acc_history[100:]) if len(acc_history) > 100 else 0,
                    'recovery': max(acc_history[150:]) if len(acc_history) > 150 else 0
                }
            
            self._print(f"\n{scenario_name}:")
            for v_name, res in results[scenario_name].items():
                self._print(f"  {v_name}: final={res['final_acc']*100:.1f}%, min={res['min_acc_after']*100:.1f}%")
        
        self.results['regime_transitions'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 7: RECOVERY DYNAMICS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_recovery_dynamics(self) -> Dict:
        """Detailed time-to-recovery analysis"""
        self._header("CATEGORY 7: RECOVERY DYNAMICS")
        
        magnitudes = [0.5, 1.0, 1.5, 2.0, 3.0]
        results = {}
        arch = [2, 64, 32, 1]
        
        for mag in magnitudes:
            results[mag] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                val_X, val_Y = spiral(200)
                
                # Train to stability
                pre_acc = 0
                for step in range(100):
                    X, Y = spiral(64)
                    pred = net.forward(X)
                    loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                         (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                    net.backward(Y)
                    val_pred = net.forward(val_X)
                    pre_acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                    if hasattr(net, 'step'):
                        net.step(loss, pre_acc)
                
                # Perturb and track recovery
                net.perturb(mag)
                
                recovery_steps = 0
                acc_50 = 0
                acc_75 = 0
                acc_90 = 0
                
                for step in range(200):
                    X, Y = spiral(64)
                    pred = net.forward(X)
                    loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                         (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                    net.backward(Y)
                    val_pred = net.forward(val_X)
                    acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                    if hasattr(net, 'step'):
                        net.step(loss, acc)
                    
                    if acc >= pre_acc * 0.5 and acc_50 == 0:
                        acc_50 = step
                    if acc >= pre_acc * 0.75 and acc_75 == 0:
                        acc_75 = step
                    if acc >= pre_acc * 0.9 and acc_90 == 0:
                        acc_90 = step
                    if acc >= pre_acc * 0.95 and recovery_steps == 0:
                        recovery_steps = step
                
                results[mag][v_name] = {
                    'pre_acc': pre_acc,
                    'recovery_95': recovery_steps,
                    'recovery_90': acc_90,
                    'recovery_75': acc_75,
                    'recovery_50': acc_50
                }
            
            self._print(f"\nMagnitude={mag}:")
            for v_name, res in results[mag].items():
                self._print(f"  {v_name}: 50%={res['recovery_50']}, 75%={res['recovery_75']}, "
                           f"90%={res['recovery_90']}, 95%={res['recovery_95']}")
        
        self.results['recovery_dynamics'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 8: GRADIENT PATHOLOGY
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_gradient_pathology(self) -> Dict:
        """Test under gradient pathologies"""
        self._header("CATEGORY 8: GRADIENT PATHOLOGY")
        
        scenarios = {
            'Normal': {'init': 'he'},
            'Small-Init': {'init': 'small'},
            'Large-Init': {'init': 'large'},
            'Deep-Vanishing': {'arch': [2, 16, 16, 16, 16, 16, 16, 1], 'init': 'small'},
            'Wide-Exploding': {'arch': [2, 512, 512, 1], 'init': 'large', 'lr': 0.1},
        }
        
        results = {}
        
        for scenario_name, params in scenarios.items():
            results[scenario_name] = {}
            arch = params.get('arch', [2, 64, 32, 1])
            init = params.get('init', 'he')
            lr = params.get('lr', 0.02)
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=lr, init=init)
                res = train_detailed(net, spiral, steps=250)
                results[scenario_name][v_name] = {
                    'acc': res.best_acc,
                    'max_grad': res.max_grad_norm,
                    'min_grad': res.min_grad_norm,
                    'emergencies': res.emergencies
                }
            
            self._print(f"\n{scenario_name}:")
            for v_name, res in results[scenario_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}% (max_grad={res['max_grad']:.1f})")
        
        self.results['gradient_pathology'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 9: NOISE ROBUSTNESS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_noise_robustness(self) -> Dict:
        """Test robustness to label and input noise"""
        self._header("CATEGORY 9: NOISE ROBUSTNESS")
        
        noise_configs = {
            'Clean': {'label': 0.0, 'input': 0.0},
            'Label-5%': {'label': 0.05, 'input': 0.0},
            'Label-10%': {'label': 0.10, 'input': 0.0},
            'Label-20%': {'label': 0.20, 'input': 0.0},
            'Input-0.05': {'label': 0.0, 'input': 0.05},
            'Input-0.1': {'label': 0.0, 'input': 0.1},
            'Input-0.2': {'label': 0.0, 'input': 0.2},
            'Combined': {'label': 0.1, 'input': 0.1},
        }
        
        results = {}
        arch = [2, 64, 32, 1]
        
        for config_name, params in noise_configs.items():
            results[config_name] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, spiral, steps=250,
                                    label_noise=params['label'],
                                    input_noise=params['input'])
                results[config_name][v_name] = {
                    'acc': res.best_acc,
                    'variance': res.acc_variance
                }
            
            self._print(f"\n{config_name}:")
            for v_name, res in results[config_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['noise_robustness'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 10: LONG-RUN STABILITY
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_long_run(self) -> Dict:
        """Test stability over 1000+ steps"""
        self._header("CATEGORY 10: LONG-RUN STABILITY")
        
        step_counts = [250, 500, 750, 1000, 1500]
        results = {}
        arch = [2, 64, 32, 1]
        
        for steps in step_counts:
            results[steps] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, spiral, steps=steps)
                results[steps][v_name] = {
                    'acc': res.best_acc,
                    'final_acc': res.final_acc,
                    'variance': res.acc_variance,
                    'time': res.training_time
                }
            
            self._print(f"\n{steps} steps:")
            for v_name, res in results[steps].items():
                self._print(f"  {v_name}: best={res['acc']*100:.1f}%, final={res['final_acc']*100:.1f}%")
        
        self.results['long_run'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 11: BATCH SIZE EFFECTS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_batch_sizes(self) -> Dict:
        """Test different batch sizes"""
        self._header("CATEGORY 11: BATCH SIZE EFFECTS")
        
        batch_sizes = [8, 16, 32, 64, 128, 256, 512]
        results = {}
        arch = [2, 64, 32, 1]
        
        for batch in batch_sizes:
            results[batch] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02)
                res = train_detailed(net, spiral, steps=250, batch=batch)
                results[batch][v_name] = {
                    'acc': res.best_acc,
                    't95': res.steps_to_95,
                    'time': res.training_time
                }
            
            self._print(f"\nBatch={batch}:")
            for v_name, res in results[batch].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}% (t95={res['t95']})")
        
        self.results['batch_sizes'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 12: MOMENTUM ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_momentum(self) -> Dict:
        """Test different momentum values"""
        self._header("CATEGORY 12: MOMENTUM ANALYSIS")
        
        momentums = [0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99]
        results = {}
        arch = [2, 64, 32, 1]
        
        for mom in momentums:
            results[mom] = {}
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=0.02, momentum=mom)
                res = train_detailed(net, spiral, steps=250)
                results[mom][v_name] = {
                    'acc': res.best_acc,
                    't95': res.steps_to_95
                }
            
            self._print(f"\nMomentum={mom}:")
            for v_name, res in results[mom].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['momentum'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 13: COMBINED STRESS
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_combined_stress(self) -> Dict:
        """Test multiple stressors simultaneously"""
        self._header("CATEGORY 13: COMBINED STRESS")
        
        scenarios = {
            'HighLR+Perturb': {'lr': 0.3, 'perturb': (100, 1.0)},
            'HighLR+Noise': {'lr': 0.3, 'label_noise': 0.1},
            'Perturb+Noise': {'perturb': (100, 1.0), 'label_noise': 0.1},
            'Triple-Stress': {'lr': 0.3, 'perturb': (100, 0.5), 'label_noise': 0.05},
            'Deep+HighLR': {'arch': [2, 32, 32, 32, 32, 1], 'lr': 0.3},
            'Wide+Perturb': {'arch': [2, 256, 1], 'perturb': (100, 1.5)},
        }
        
        results = {}
        
        for scenario_name, params in scenarios.items():
            results[scenario_name] = {}
            arch = params.get('arch', [2, 64, 32, 1])
            lr = params.get('lr', 0.02)
            perturb = params.get('perturb', None)
            label_noise = params.get('label_noise', 0.0)
            
            for v_name, v_class in self.versions.items():
                net = v_class(arch, lr=lr)
                res = train_detailed(net, spiral, steps=300,
                                    perturbation=perturb,
                                    label_noise=label_noise)
                results[scenario_name][v_name] = {
                    'acc': res.best_acc,
                    'emergencies': res.emergencies,
                    'recovery': res.recovery_time
                }
            
            self._print(f"\n{scenario_name}:")
            for v_name, res in results[scenario_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['combined_stress'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # CATEGORY 14: EDGE CASES
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def test_edge_cases(self) -> Dict:
        """Test extreme edge cases"""
        self._header("CATEGORY 14: EDGE CASES")
        
        cases = {
            'Tiny-LR': {'lr': 0.0001},
            'Huge-LR': {'lr': 5.0},
            'Single-Sample': {'batch': 1},
            'Huge-Batch': {'batch': 1000},
            'Rapid-Perturb': {'multi_perturb': 50},  # Perturb every 5 steps
            'Extreme-Perturb': {'perturb_mag': 10.0},
            '1-Layer': {'arch': [2, 1]},
            '10-Layer': {'arch': [2, 16, 16, 16, 16, 16, 16, 16, 16, 16, 1]},
        }
        
        results = {}
        
        for case_name, params in cases.items():
            results[case_name] = {}
            arch = params.get('arch', [2, 64, 32, 1])
            lr = params.get('lr', 0.02)
            batch = params.get('batch', 64)
            
            for v_name, v_class in self.versions.items():
                try:
                    net = v_class(arch, lr=lr)
                    
                    if 'multi_perturb' in params:
                        # Rapid perturbation test
                        val_X, val_Y = spiral(200)
                        for step in range(250):
                            X, Y = spiral(batch)
                            pred = net.forward(X)
                            loss = float(-np.mean(Y * np.log(np.clip(pred, 1e-7, 1-1e-7)) +
                                                 (1 - Y) * np.log(np.clip(1 - pred, 1e-7, 1-1e-7))))
                            net.backward(Y)
                            val_pred = net.forward(val_X)
                            acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                            if hasattr(net, 'step'):
                                net.step(loss, acc)
                            if step > 50 and step % 5 == 0:
                                net.perturb(0.3)
                        val_pred = net.forward(val_X)
                        final_acc = float(np.mean((np.clip(val_pred, 0, 1) > 0.5) == val_Y))
                        results[case_name][v_name] = {'acc': final_acc}
                    
                    elif 'perturb_mag' in params:
                        res = train_detailed(net, spiral, steps=300,
                                            perturbation=(100, params['perturb_mag']))
                        results[case_name][v_name] = {'acc': res.best_acc}
                    
                    else:
                        res = train_detailed(net, spiral, steps=250, batch=batch)
                        results[case_name][v_name] = {'acc': res.best_acc}
                
                except Exception as e:
                    results[case_name][v_name] = {'acc': 0.0, 'error': str(e)}
            
            self._print(f"\n{case_name}:")
            for v_name, res in results[case_name].items():
                self._print(f"  {v_name}: {res['acc']*100:.1f}%")
        
        self.results['edge_cases'] = results
        return results
    
    # ─────────────────────────────────────────────────────────────────────────────────────
    # FULL BENCHMARK
    # ─────────────────────────────────────────────────────────────────────────────────────
    
    def run_all(self, quick: bool = False) -> Dict:
        """Run all benchmark categories"""
        
        self._print("╔" + "═" * 88 + "╗")
        self._print("║" + " ATHENA BRANCH 2 - MASTER BENCHMARK SUITE ".center(88) + "║")
        self._print("║" + f" Testing {len(self.versions)} versions ".center(88) + "║")
        self._print("╚" + "═" * 88 + "╝")
        
        start_time = time.time()
        
        # Core tests (always run)
        self.test_convergence()
        self.test_learning_rate()
        self.test_perturbation()
        
        if not quick:
            # Extended tests
            self.test_architectures()
            self.test_multi_perturbation()
            self.test_regime_transitions()
            self.test_recovery_dynamics()
            self.test_gradient_pathology()
            self.test_noise_robustness()
            self.test_long_run()
            self.test_batch_sizes()
            self.test_momentum()
            self.test_combined_stress()
            self.test_edge_cases()
        
        total_time = time.time() - start_time
        
        # Summary
        self._header("FINAL SUMMARY")
        self._print(f"\nTotal time: {total_time:.1f} seconds")
        
        # Calculate win rates
        self._calculate_wins()
        
        return self.results
    
    def _calculate_wins(self):
        """Calculate and display win statistics"""
        wins = {v: 0 for v in self.versions}
        ties = {v: 0 for v in self.versions}
        total_tests = 0
        
        for category, cat_results in self.results.items():
            for test_name, test_results in cat_results.items():
                if not test_results:
                    continue
                
                accs = {v: r.get('acc', 0) for v, r in test_results.items()}
                best_acc = max(accs.values())
                
                total_tests += 1
                for v_name, acc in accs.items():
                    if acc >= best_acc - 0.01:
                        if acc == best_acc:
                            wins[v_name] += 1
                        else:
                            ties[v_name] += 1
        
        self._print(f"\nTotal tests: {total_tests}")
        self._print("\nWin counts (best or within 1%):")
        for v_name in sorted(wins.keys(), key=lambda x: -wins[x]):
            self._print(f"  {v_name}: {wins[v_name]} wins, {ties[v_name]} ties "
                       f"({100*wins[v_name]/max(1,total_tests):.1f}%)")
    
    def export_results(self, filename: str = 'benchmark_results.json'):
        """Export results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        self._print(f"\nResults exported to {filename}")

# ═══════════════════════════════════════════════════════════════════════════════════════════
# SECTION 7: MAIN
# ═══════════════════════════════════════════════════════════════════════════════════════════

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='ATHENA Branch 2 Master Benchmark Suite')
    parser.add_argument('--full', action='store_true', help='Run full benchmark (all 14 categories)')
    parser.add_argument('--quick', action='store_true', help='Run quick benchmark (3 core categories)')
    parser.add_argument('--category', type=str, help='Run specific category')
    parser.add_argument('--export', type=str, help='Export results to file')
    parser.add_argument('--quiet', action='store_true', help='Minimal output')
    
    args = parser.parse_args()
    
    suite = BenchmarkSuite(verbose=not args.quiet)
    
    if args.category:
        method_name = f'test_{args.category}'
        if hasattr(suite, method_name):
            getattr(suite, method_name)()
        else:
            print(f"Unknown category: {args.category}")
            print("Available: convergence, learning_rate, perturbation, architectures, "
                  "multi_perturbation, regime_transitions, recovery_dynamics, "
                  "gradient_pathology, noise_robustness, long_run, batch_sizes, "
                  "momentum, combined_stress, edge_cases")
    elif args.quick:
        suite.run_all(quick=True)
    else:
        suite.run_all(quick=not args.full)
    
    if args.export:
        suite.export_results(args.export)

if __name__ == '__main__':
    main()
