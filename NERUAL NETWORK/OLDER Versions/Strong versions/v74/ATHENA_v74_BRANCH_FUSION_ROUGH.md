# ATHENA BRANCH FUSION: QUICK ROUGH SYNTHESIS
## Branch 1 (Features/Encoding) + Branch 2 (Regime/Architecture)

---

## BRANCH SUMMARIES

### Branch 1 (What We Built)
**Focus: L0/L1 Feature Engineering**

| Component | Best Result | Key Insight |
|-----------|-------------|-------------|
| TRUE Rotation Invariance | 78.6% GEOMETRIC | Polar + Hu moments |
| Edge Coherence | 63.6% CAMOUFLAGE | Local angle variance |
| Gated Features (v4) | 78%/63% | Features INTERFERE when combined |
| Parallel Hypothesis Learning | Concept validated | Needs structural diversity |

**Core Discovery:** You cannot emerge past broken levels. Fix L0/L1 encoding FIRST.

### Branch 2 (What Was Uploaded)
**Focus: L3-L5 Architecture/Optimization**

| Component | Best Result | Key Insight |
|-----------|-------------|-------------|
| v1 Emergency Reinit | 72% win rate | Best at high LR chaos |
| v3 Stress Mode | +40% perturbation | Trust momentum, don't reinit |
| v7 Full Hierarchy | Over-intervened | Conservative intervention needed |
| Regime Detection | 6 regimes | NORMAL/PERTURBATION/CHAOS/VANISHING/DEAD |

**Core Discovery:** Optimization is REGIME-DEPENDENT. Same symptom, opposite treatment.

---

## THE FUSION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────┐
│ L6: ATHENA META-OBSERVER (NEW)                                      │
│     - Regime detection (Branch 2)                                   │
│     - Feature routing (Branch 1 gating)                             │
│     - Parallel hypothesis coordination                              │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L5: TASK LEVEL (Branch 2)                                           │
│     Observer: accuracy, loss, generalization_gap                    │
│     Corridor: performance bounds, early stopping                    │
│     Nudge: LR schedule, regularization strength                     │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L4: MODULE LEVEL (Branch 2)                                         │
│     Observer: coherence, throughput, feature_diversity              │
│     Corridor: capacity bounds, activation ranges                    │
│     Nudge: dropout rates, batch norm momentum                       │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L3: LAYER LEVEL (Branch 2)                                          │
│     Observer: gradient_flow_ratio, representation_rank              │
│     Corridor: weight bounds, gradient clip                          │
│     Nudge: per-layer LR, reinit threshold                           │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L2: PATTERN LEVEL (Branch 1)                                        │
│     **SPECIALIZED HYPOTHESIS NETWORKS**                             │
│     H1: Structure specialist (Hu moments, topology)                 │
│     H2: Spatial specialist (polar, radial)                          │
│     H3: Texture specialist (edge coherence, LBP)                    │
│     H4: Generalist (all features)                                   │
│     Observer: per-hypothesis confidence, uniqueness                 │
│     Corridor: specialization pressure, overlap penalty              │
│     Nudge: hypothesis weighting, cross-pollination                  │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L1: SIGNAL LEVEL (Branch 1)                                         │
│     **INVARIANT FEATURE EXTRACTION**                                │
│     - Polar histogram (64) - rotation invariant                     │
│     - Radial profile (8) - rotation invariant                       │
│     - Hu moments (7) - affine invariant                             │
│     - Edge coherence map (49) - contrast invariant                  │
│     - Edge chains (5) - structure invariant                         │
│     Observer: feature quality, coverage                             │
│     Corridor: normalization bounds                                  │
│     Nudge: feature selection mask                                   │
└─────────────────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────────────────┐
│ L0: PIXEL LEVEL (Branch 1)                                          │
│     **PREPROCESSING**                                               │
│     - Local contrast normalization                                  │
│     - Rank transform (contrast invariant)                           │
│     - Figure-ground separation                                      │
│     Observer: image statistics, signal-to-noise                     │
│     Corridor: intensity bounds                                      │
│     Nudge: preprocessing strength                                   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## KEY FUSION POINTS

### 1. REGIME-AWARE FEATURE SELECTION

Branch 1 discovered features interfere. Branch 2 provides regime detection.

**Fusion:** Use regime to select features dynamically:

```python
def select_features(regime: Regime, meta_features: dict):
    if regime == Regime.PERTURBATION:
        # During perturbation, use ROBUST features
        # Edge coherence survives noise better than fine structure
        return weight_toward('coherence', 0.8)
    
    elif regime == Regime.NORMAL:
        # During normal operation, use ALL features
        # Let gating learn optimal combination
        return use_all_features()
    
    elif regime == Regime.MODERATE_CHAOS:
        # During chaos, use STABLE features
        # Hu moments are mathematically invariant
        return weight_toward('hu_moments', 0.7)
```

### 2. HYPOTHESIS-REGIME MAPPING

Branch 1: 4 specialized hypotheses (Structure, Spatial, Texture, Generalist)
Branch 2: 6 regimes (NORMAL, PERTURBATION, CHAOS_MOD, CHAOS_EXT, VANISHING, DEAD)

**Fusion:** Each hypothesis specializes for different regimes:

```python
HYPOTHESIS_REGIME_AFFINITY = {
    'H1_structure': [Regime.NORMAL, Regime.MODERATE_CHAOS],      # Hu moments stable
    'H2_spatial': [Regime.NORMAL],                               # Needs clean input
    'H3_texture': [Regime.PERTURBATION, Regime.VANISHING],       # Coherence robust
    'H4_generalist': [Regime.EXTREME_CHAOS],                     # Fallback
}

def route_to_hypothesis(regime: Regime, confidence: float):
    """Route input to best hypothesis for current regime"""
    weights = {}
    for h, affinities in HYPOTHESIS_REGIME_AFFINITY.items():
        if regime in affinities:
            weights[h] = confidence
        else:
            weights[h] = 1 - confidence
    return normalize(weights)
```

### 3. STRESS MODE FOR LOW-CONTRAST

Branch 1: Camouflage = low contrast, hard to see
Branch 2: Stress mode = reduce LR, tight clipping, trust momentum

**Fusion:** Treat camouflage INPUT like perturbation TRAINING:

```python
class ContrastAwareProcessor:
    def process(self, img):
        contrast = img.std()
        
        if contrast < 0.15:  # LOW CONTRAST (camouflage-like)
            # Activate "input stress mode"
            # - Boost edge detection
            # - Use rank transform (contrast invariant)
            # - Weight toward coherence features
            return self.stress_mode_features(img)
        
        else:  # NORMAL CONTRAST
            return self.normal_features(img)
```

### 4. COMPRESSION CONTRACTS FOR FEATURES

Branch 1: 141 features total (polar + radial + hu + coherence + chains)
Branch 2: Compression contracts between levels (summary not raw data)

**Fusion:** Compress features hierarchically:

```python
COMPRESSION_CONTRACTS = {
    'L0_to_L1': {
        'from': 784,  # raw pixels
        'to': 141,    # invariant features
        'summary': ['contrast', 'edge_strength', 'SNR']  # meta
    },
    'L1_to_L2': {
        'from': 141,  # all features
        'to': 4,      # hypothesis confidences
        'summary': ['best_hypothesis', 'confidence', 'agreement']
    },
    'L2_to_L3': {
        'from': 4,    # hypothesis outputs
        'to': 1,      # final prediction
        'summary': ['prediction', 'certainty', 'regime_hint']
    }
}
```

### 5. CONSERVATIVE INTERVENTION POLICY (UNIFIED)

Branch 1: Parallel hypothesis cross-pollination killed diversity
Branch 2: v7 over-intervention (246 nudges) performed WORSE

**Unified Policy:**

```python
class ConservativeIntervention:
    def __init__(self):
        self.confidence_threshold = 0.7
        self.cooldown = 30
        self.last_intervention = -100
        self.t = 0
    
    def should_intervene(self, regime, confidence, level):
        self.t += 1
        
        # Don't intervene on NORMAL
        if regime == Regime.NORMAL:
            return False
        
        # Require high confidence
        if confidence < self.confidence_threshold:
            return False
        
        # Respect cooldown
        if (self.t - self.last_intervention) < self.cooldown:
            return False
        
        # Scale by level fragility
        # Lower levels (L0-L1) more fragile than higher (L4-L5)
        fragility = {0: 2.0, 1: 1.5, 2: 1.0, 3: 0.8, 4: 0.6, 5: 0.5}
        if confidence < self.confidence_threshold * fragility[level]:
            return False
        
        return True
```

---

## SYNERGY ENGINE (COMBINED)

```python
class UnifiedSynergyEngine:
    """
    Coordinates nudges across ALL levels (L0-L5)
    Using BOTH feature selection (Branch 1) AND regime response (Branch 2)
    """
    
    def compile_nudge_package(self, regime, confidence, layer_summaries, feature_stats):
        nudges = []
        
        # L0: Preprocessing nudge
        if feature_stats['contrast'] < 0.15:
            nudges.append(Nudge(level=0, type='PREPROCESSING', 
                               action='boost_edge_detection', magnitude=confidence))
        
        # L1: Feature selection nudge
        if regime == Regime.PERTURBATION:
            nudges.append(Nudge(level=1, type='FEATURE_MASK',
                               action='weight_coherence', magnitude=0.8 * confidence))
        
        # L2: Hypothesis routing nudge
        if regime in [Regime.MODERATE_CHAOS, Regime.EXTREME_CHAOS]:
            nudges.append(Nudge(level=2, type='HYPOTHESIS_WEIGHT',
                               action='favor_stable', magnitude=confidence))
        
        # L3: Gradient nudge (from Branch 2)
        if any(s['health'] == 'exploding' for s in layer_summaries):
            nudges.append(Nudge(level=3, type='GRADIENT_CLIP',
                               action='tighten', magnitude=0.1 * confidence))
        
        # L4: Module nudge
        if feature_stats['diversity'] < 0.3:
            nudges.append(Nudge(level=4, type='REGULARIZATION',
                               action='increase_dropout', magnitude=0.1 * confidence))
        
        # L5: Task nudge
        if regime == Regime.VANISHING:
            nudges.append(Nudge(level=5, type='LR_SCHEDULE',
                               action='boost', magnitude=2.0 * confidence))
        
        return nudges
```

---

## EXPECTED IMPROVEMENTS

| Benchmark | Branch 1 Only | Branch 2 Only | Fused (Expected) |
|-----------|---------------|---------------|------------------|
| GEOMETRIC | 78.6% | N/A | 82-85% |
| CAMOUFLAGE | 63.6% | N/A | 70-75% |
| PERTURBATION | N/A | +40% recovery | +50% recovery |
| HIGH LR | N/A | +15% vs Adam | +20% vs Adam |
| OVERALL | 70.4% avg | 72% win rate | 80%+ target |

---

## IMMEDIATE NEXT STEPS

1. **Implement RegimeAwareFeatureSelector**
   - Combine Branch 2's RegimeDetector with Branch 1's gated features

2. **Implement HypothesisRegimeRouter**  
   - Map hypotheses to regimes
   - Route inputs to best hypothesis based on current regime

3. **Implement UnifiedSynergyEngine**
   - Coordinate nudges across L0-L5
   - Both feature-level and optimization-level

4. **Test on Combined Benchmark**
   - Run Branch 2's full benchmark suite
   - WITH Branch 1's invariant features
   - Measure improvement on BOTH geometric AND perturbation tasks

5. **Tune Conservative Intervention**
   - Start with Branch 2's proven thresholds (0.7 confidence, 30 cooldown)
   - Adjust based on combined benchmark results

---

## FILE STRUCTURE FOR v74

```
athena_v74/
├── core/
│   ├── features.py          # Branch 1: Invariant feature extraction
│   ├── hypotheses.py        # Branch 1: Parallel hypothesis networks
│   ├── regimes.py           # Branch 2: Regime detection
│   ├── optimizer.py         # Branch 2: Regime-aware optimizer
│   └── synergy.py           # FUSION: Unified synergy engine
├── layers/
│   ├── L0_pixel.py          # Preprocessing
│   ├── L1_signal.py         # Feature extraction
│   ├── L2_pattern.py        # Hypothesis networks
│   ├── L3_layer.py          # Gradient control
│   ├── L4_module.py         # Module coordination
│   └── L5_task.py           # Task monitoring
├── benchmarks/
│   ├── geometric.py         # Branch 1 benchmarks
│   ├── perturbation.py      # Branch 2 benchmarks
│   └── combined.py          # FUSION benchmarks
└── athena_v74_unified.py    # Main unified architecture
```

---

## QUICK PROTOTYPE CODE

```python
"""
ATHENA v74 UNIFIED - QUICK PROTOTYPE
Branch 1 (Features) + Branch 2 (Regimes)
"""

from athena_branch2_final import RegimeDetector, Regime, ConfigV3
from athena_v73_1_true_invariance import extract_invariant_features
from athena_v73_4_edge_coherence import edge_coherence_features

class AthenaV74Unified:
    def __init__(self, feature_dim, hidden=128):
        # Branch 1: Feature extraction
        self.feature_extractor = InvariantFeatureExtractor()
        
        # Branch 1: Gated hypotheses
        self.hypotheses = [
            SpecializedNet(feature_dim, hidden, name='structure'),
            SpecializedNet(feature_dim, hidden, name='spatial'),
            SpecializedNet(feature_dim, hidden, name='texture'),
            SpecializedNet(feature_dim, hidden, name='generalist'),
        ]
        
        # Branch 2: Regime detection
        self.regime_detector = RegimeDetector(ConfigV3())
        
        # FUSION: Synergy engine
        self.synergy = UnifiedSynergyEngine()
        
        # Intervention policy
        self.policy = ConservativeIntervention()
    
    def forward(self, X):
        # L0: Preprocess
        X_norm = self.preprocess(X)
        
        # L1: Extract features
        features = self.feature_extractor(X_norm)
        
        # L2: Run all hypotheses
        hypothesis_outputs = [h.forward(features) for h in self.hypotheses]
        confidences = [out.max(1).mean() for out in hypothesis_outputs]
        
        # Detect regime
        regime, regime_confidence = self.regime_detector.detect()
        
        # Route based on regime
        weights = self.route_hypotheses(regime, regime_confidence)
        
        # Combine
        combined = sum(w * out for w, out in zip(weights, hypothesis_outputs))
        return combined
    
    def train_step(self, X, Y, lr):
        # Forward
        pred = self.forward(X)
        loss = cross_entropy(pred, Y)
        acc = (pred.argmax(1) == Y.argmax(1)).mean()
        
        # Update regime detector
        grad_max = self.get_max_gradient()
        self.regime_detector.update(acc, grad_max, loss)
        regime, confidence = self.regime_detector.detect()
        
        # Check if intervention needed
        if self.policy.should_intervene(regime, confidence, level=3):
            # Compile nudge package
            nudges = self.synergy.compile_nudge_package(
                regime, confidence, 
                self.get_layer_summaries(),
                self.get_feature_stats()
            )
            # Apply nudges
            self.apply_nudges(nudges)
            self.policy.record_intervention()
        
        # Backward (with regime-aware LR)
        effective_lr = self.get_effective_lr(regime, lr)
        self.backward(Y, effective_lr)
        
        return loss, acc
```

---

## SUMMARY

**Branch 1 fixes WHAT the network sees (L0-L1)**
**Branch 2 fixes HOW the network learns (L3-L5)**
**FUSION coordinates BOTH simultaneously**

The key insight: **You need invariant features AND regime-aware optimization.**
Neither alone is sufficient. Together, they address the full stack.

---

*ATHENA v74 Fusion - Quick Rough Synthesis*
*Ready for implementation*
