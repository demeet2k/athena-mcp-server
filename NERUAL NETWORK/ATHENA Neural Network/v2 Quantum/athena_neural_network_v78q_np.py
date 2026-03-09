
"""
ATHENA NEURAL NETWORK v78Q-NP
============================

Pure NumPy/SciPy "Quantum-like" Emergence Compiler upgrade of athena_neural_network.py.

Key upgrades vs v76.1 optimized baseline:
- 6-mode anisotropic attention (base-6 frame charts)
- Multi-hypothesis bank (modes × thresholds) with flow–prune scheduling
- Batched feature extraction across hypotheses (vectorized HOG + Polar)
- True branch disagreement (JS divergence) and energy-based amplitude collapse
- Deeper compression prior: PCA/MDL on *masked rank images* + Hadamard sketch prior
- Deterministic, reproducible hypothesis selection; optional prime-stability tie-break

Notes:
- Keeps invariant core features (HOG 441 + Polar 64 + Topology 12 + Struct 6 = 523)
- Training retains feature caching; mask selection uses multi-hypothesis search.

Author: Emergence Compiler Framework
Version: v78Q-NP
"""

import numpy as np
from scipy import ndimage
from scipy.special import softmax as scipy_softmax

# =============================================================================
# FOUNDATIONAL TRANSFORMS
# =============================================================================

def rank_transform(img: np.ndarray) -> np.ndarray:
    """Convert intensity to ordinal ranks in [0,1]."""
    flat = img.reshape(-1)
    ranks = np.empty_like(flat)
    sorted_idx = np.argsort(flat, kind="mergesort")
    ranks[sorted_idx] = np.linspace(0.0, 1.0, flat.size, dtype=flat.dtype)
    return ranks.reshape(img.shape)

def compute_gradients(img: np.ndarray):
    """Sobel gradients."""
    gy = ndimage.sobel(img, axis=0)
    gx = ndimage.sobel(img, axis=1)
    mag = np.sqrt(gx * gx + gy * gy)
    ang = np.arctan2(gy, gx)
    return mag, ang, gx, gy

# =============================================================================
# MATH TRICK 1: FAST ANISOTROPIC DIFFUSION (Ω operator)
# =============================================================================

def _divergence(c_x, c_y, ux_f, ux_b, uy_f, uy_b):
    # div(c * grad u) with forward/back differences
    return (c_x * ux_f - c_x * ux_b) + (c_y * uy_f - c_y * uy_b)

def anisotropic_diffuse(u: np.ndarray, gx: np.ndarray, gy: np.ndarray,
                        kappa: float = 0.12, dt: float = 0.18, steps: int = 10,
                        bias: str | None = None) -> np.ndarray:
    """
    Perona–Malik style diffusion of u with conductance from |∇R|.
    bias: None | 'x' | 'y' to favor smoothing along one axis.
    """
    # Conductance fields derived from rank gradients (fixed for an image)
    ax = np.abs(gx)
    ay = np.abs(gy)

    # Base conductances
    c_x = 1.0 / (1.0 + (ax / (kappa + 1e-8)) ** 2)
    c_y = 1.0 / (1.0 + (ay / (kappa + 1e-8)) ** 2)

    if bias == 'x':
        c_x = np.clip(c_x * 1.25, 0.0, 1.0)
        c_y = np.clip(c_y * 0.75, 0.0, 1.0)
    elif bias == 'y':
        c_y = np.clip(c_y * 1.25, 0.0, 1.0)
        c_x = np.clip(c_x * 0.75, 0.0, 1.0)

    # Border damping mask (prevents wrap artifacts)
    border = np.ones_like(u, dtype=u.dtype)
    border[:2, :] *= 0.2
    border[-2:, :] *= 0.2
    border[:, :2] *= 0.2
    border[:, -2:] *= 0.2

    out = u.copy()
    for _ in range(steps):
        # forward/back diffs (reflect-like via roll + border damping)
        ux_f = np.roll(out, -1, axis=1) - out
        ux_b = out - np.roll(out, 1, axis=1)
        uy_f = np.roll(out, -1, axis=0) - out
        uy_b = out - np.roll(out, 1, axis=0)

        div = _divergence(c_x, c_y, ux_f, ux_b, uy_f, uy_b)
        out = out + dt * div
        out = out * (0.6 + 0.4 * border)  # keep borders quiet
        out = np.clip(out, 0.0, 1.0)

    return out

def generate_attention_modes(R: np.ndarray, gx: np.ndarray, gy: np.ndarray, base_iters: int = 8):
    """
    6 attention modes (base-6 frame charts):
    0 isotropic, 1 strong smoothing, 2 x-biased, 3 y-biased, 4 contrast manifest, 5 conservative
    """
    y, x = np.ogrid[:28, :28]
    center = np.exp(-((y - 13.5) ** 2 + (x - 13.5) ** 2) / 150.0)
    u0 = np.clip(0.65 * R + 0.35 * center, 0.0, 1.0)

    # Mode params (kappa, steps, bias, manifest)
    modes = [
        (0.12, base_iters, None, False),
        (0.09, base_iters + 4, None, False),
        (0.11, base_iters, 'x', False),
        (0.11, base_iters, 'y', False),
        (0.12, base_iters, None, True),
        (0.14, base_iters - 2, None, False),
    ]

    outs = []
    for kappa, steps, bias, manifest in modes:
        u = u0.copy()
        if manifest:
            # "Manifestation": contrast lift before diffusion
            u = 1.0 / (1.0 + np.exp(-6.0 * (u - 0.5)))
        u = anisotropic_diffuse(u, gx=gx, gy=gy, kappa=kappa, dt=0.18, steps=steps, bias=bias)
        # normalize
        u = (u - u.min()) / (u.max() - u.min() + 1e-8)
        outs.append(u.astype(np.float32))
    return outs

# =============================================================================
# DISCRETE SUPERVISOR D: HYPOTHESIS MASKS (batched-friendly)
# =============================================================================

def generate_mask_from_u(u: np.ndarray, R: np.ndarray, tau: float) -> np.ndarray:
    """
    Deterministic mask projection: threshold u + rank fallback, then cleanup.
    """
    mask = ((u >= tau) | (R >= tau + 0.12)).astype(np.float32)
    if mask.sum() < 10:
        return np.zeros_like(mask, dtype=np.float32)

    # Cleanup (fast)
    mask = ndimage.binary_opening(mask, structure=np.ones((2, 2))).astype(np.float32)

    # Keep largest component
    labeled, num = ndimage.label(mask)
    if num > 0:
        sizes = ndimage.sum(mask, labeled, range(1, num + 1))
        largest = int(np.argmax(sizes) + 1)
        mask = (labeled == largest).astype(np.float32)

    # Fill holes
    mask = ndimage.binary_fill_holes(mask).astype(np.float32)
    return mask

def mask_quality(mag: np.ndarray, mask: np.ndarray) -> float:
    """Cheap quality score for flow–prune (edge strength + compactness + area sanity)."""
    area = float(mask.sum()) + 1e-8
    edge = float((mag * mask).sum()) / area

    # Perimeter proxy: boundary = mask - erode(mask)
    er = ndimage.binary_erosion(mask, structure=np.ones((3, 3))).astype(np.float32)
    boundary = mask - er
    per = float(boundary.sum()) + 1e-8

    # Compactness proxy
    comp = area / (per * per)

    # Penalize extreme areas (digits occupy ~5%..40% usually in 28x28)
    frac = area / 784.0
    area_pen = abs(frac - 0.18)

    return edge + 1.5 * comp - 0.8 * area_pen

# =============================================================================
# MATH TRICK 2: BATCHED HOG VIA SINGLE ADD.AT (no cell/bin loops)
# =============================================================================

# Precompute cell ids for 7x7 cells of size 4
_Y, _X = np.indices((28, 28))
_CELL_ID = ((_Y // 4) * 7 + (_X // 4)).astype(np.int32).ravel()

def extract_hog_batch(mag: np.ndarray, angle: np.ndarray, masks: np.ndarray, bins: int = 9) -> np.ndarray:
    """
    Batched HOG (H, 441) for masks shape (H,28,28).
    Uses joint index = cell_id*bins + bin_idx and accumulates by np.add.at.
    """
    H = masks.shape[0]
    bin_idx = (((angle + np.pi) / (2.0 * np.pi) * bins).astype(np.int32) % bins).ravel()
    joint = (_CELL_ID * bins + bin_idx).astype(np.int32)  # (784,)

    weights = (mag[None, :, :] * masks).reshape(H, -1).astype(np.float32)  # (H,784)

    hog = np.zeros((H, 7 * 7 * bins), dtype=np.float32)
    idx_h = np.repeat(np.arange(H, dtype=np.int32), joint.size)
    idx_joint = np.tile(joint, H)
    np.add.at(hog, (idx_h, idx_joint), weights.reshape(-1))

    # normalize per hypothesis
    norm = np.sqrt((hog * hog).sum(axis=1, keepdims=True) + 1e-8)
    hog = hog / norm
    return hog

# =============================================================================
# MATH TRICK 3: BATCHED POLAR HISTOGRAM (vectorized across hypotheses)
# =============================================================================

def extract_polar_batch(R: np.ndarray, masks: np.ndarray, radial: int = 8, angular: int = 8) -> np.ndarray:
    """
    Batched polar histogram (H, 64) using weighted COM per mask.
    """
    H = masks.shape[0]
    y_idx, x_idx = np.ogrid[:28, :28]
    y_grid = y_idx.astype(np.float32)
    x_grid = x_idx.astype(np.float32)

    weighted = (R[None, :, :] * masks).astype(np.float32)
    total = weighted.sum(axis=(1, 2)) + 1e-8

    cy = (weighted * y_grid[None, :, :]).sum(axis=(1, 2)) / total
    cx = (weighted * x_grid[None, :, :]).sum(axis=(1, 2)) / total

    cy = cy[:, None, None]
    cx = cx[:, None, None]

    dy = y_grid[None, :, :] - cy
    dx = x_grid[None, :, :] - cx

    rr = np.sqrt(dy * dy + dx * dx)
    tt = np.arctan2(dy, dx)

    r_max = rr.reshape(H, -1).max(axis=1) + 1e-8
    r_bins = (rr / r_max[:, None, None] * radial).astype(np.int32)
    r_bins = np.clip(r_bins, 0, radial - 1)

    t_bins = (((tt + np.pi) / (2.0 * np.pi) * angular)).astype(np.int32)
    t_bins = np.clip(t_bins, 0, angular - 1)

    bin_index = (r_bins * angular + t_bins).reshape(H, -1).astype(np.int32)  # (H,784)
    weights = weighted.reshape(H, -1)

    polar = np.zeros((H, radial * angular), dtype=np.float32)
    idx_h = np.repeat(np.arange(H, dtype=np.int32), bin_index.shape[1])
    idx_b = bin_index.reshape(-1)
    np.add.at(polar, (idx_h, idx_b), weights.reshape(-1))

    denom = polar.sum(axis=1, keepdims=True) + 1e-8
    polar = polar / denom
    return polar

# =============================================================================
# TOPOLOGY & STRUCTURE (cheap loops; only used on pruned hypothesis set)
# =============================================================================

def extract_topology(mask: np.ndarray) -> np.ndarray:
    """Topology features from mask (12 dims)."""
    features = []

    for thresh in [0.3, 0.5, 0.7]:
        binary = mask > thresh
        labeled, num_comp = ndimage.label(binary)

        filled = ndimage.binary_fill_holes(binary)
        holes = filled.astype(int) - binary.astype(int)
        _, num_holes = ndimage.label(holes)

        features.extend([num_comp / 3.0, num_holes / 2.0])

    total = float(mask.sum()) + 1e-8
    features.append(float(mask[:14, :].sum()) / total)
    features.append(float(mask[14:, :].sum()) / total)
    features.append(float(mask[:, :14].sum()) / total)
    features.append(float(mask[:, 14:].sum()) / total)

    if mask.sum() > 0:
        cy, cx = ndimage.center_of_mass(mask)
        features.extend([float(cy) / 28.0, float(cx) / 28.0])
    else:
        features.extend([0.5, 0.5])

    return np.array(features, dtype=np.float32)

def extract_structure_batch(R: np.ndarray, masks: np.ndarray) -> np.ndarray:
    """Structural features (H,6): 2×2 quadrant mass + compactness + area."""
    H = masks.shape[0]
    feats = np.zeros((H, 6), dtype=np.float32)
    weighted = R[None, :, :] * masks

    # 2x2 quadrant sums (scaled)
    feats[:, 0] = weighted[:, :14, :14].sum(axis=(1, 2)) / 50.0
    feats[:, 1] = weighted[:, :14, 14:].sum(axis=(1, 2)) / 50.0
    feats[:, 2] = weighted[:, 14:, :14].sum(axis=(1, 2)) / 50.0
    feats[:, 3] = weighted[:, 14:, 14:].sum(axis=(1, 2)) / 50.0

    # compactness proxy + area
    for i in range(H):
        m = masks[i]
        if m.sum() > 0:
            dil = ndimage.binary_dilation(m, iterations=2).astype(np.float32)
            feats[i, 4] = float(m.sum()) / (float(dil.sum()) + 1e-8)
        feats[i, 5] = float(m.sum()) / 784.0

    return feats

def extract_all_features_batch(img: np.ndarray, masks: np.ndarray) -> np.ndarray:
    """
    Batched feature extraction for selected masks.
    Output: (H,523)
    """
    R = rank_transform(img)
    mag, ang, _, _ = compute_gradients(R)

    hog = extract_hog_batch(mag, ang, masks)           # (H,441)
    polar = extract_polar_batch(R, masks)              # (H,64)

    topo = np.zeros((masks.shape[0], 12), dtype=np.float32)
    for i in range(masks.shape[0]):
        topo[i] = extract_topology(masks[i])

    struct = extract_structure_batch(R, masks)         # (H,6)
    return np.concatenate([hog, polar, topo, struct], axis=1)

# =============================================================================
# MATH TRICK 4: FAST WALSH–HADAMARD SKETCH PRIOR (compression-as-knowledge)
# =============================================================================

def fwht(x: np.ndarray) -> np.ndarray:
    """In-place fast Walsh–Hadamard transform for 1D vectors (len power of 2)."""
    h = 1
    y = x.copy()
    n = y.shape[0]
    while h < n:
        for i in range(0, n, h * 2):
            a = y[i:i+h]
            b = y[i+h:i+2*h]
            y[i:i+h] = a + b
            y[i+h:i+2*h] = a - b
        h *= 2
    return y

class SketchPrior:
    """
    Hadamard sketch + class mean templates.
    Extremely fast, robust to camouflage texture if using rank+mask.
    """
    def __init__(self, out_dim: int = 128, pad_dim: int = 1024, seed: int = 123):
        self.out_dim = out_dim
        self.pad_dim = pad_dim
        rng = np.random.RandomState(seed)
        self.sign = rng.choice([-1.0, 1.0], size=(pad_dim,)).astype(np.float32)
        self.means = None
        self.trained = False

    def _sketch_one(self, x_flat: np.ndarray) -> np.ndarray:
        v = np.zeros(self.pad_dim, dtype=np.float32)
        n = min(x_flat.size, self.pad_dim)
        v[:n] = x_flat[:n].astype(np.float32)
        v *= self.sign
        hv = fwht(v)
        # Normalize sketch
        hv = hv / (np.sqrt(self.pad_dim) + 1e-8)
        return hv[:self.out_dim]

    def train(self, X_flat: np.ndarray, Y_onehot: np.ndarray):
        labels = Y_onehot.argmax(1)
        means = np.zeros((10, self.out_dim), dtype=np.float32)
        counts = np.zeros(10, dtype=np.int32)

        for x, d in zip(X_flat, labels):
            s = self._sketch_one(x)
            means[d] += s
            counts[d] += 1

        for d in range(10):
            if counts[d] > 0:
                means[d] /= counts[d]
            else:
                means[d] = 0.0

        self.means = means
        self.trained = True

    def get_logits_batch(self, X_flat_batch: np.ndarray) -> np.ndarray:
        if not self.trained:
            return np.zeros((X_flat_batch.shape[0], 10), dtype=np.float32)

        H = X_flat_batch.shape[0]
        sketches = np.zeros((H, self.out_dim), dtype=np.float32)
        for i in range(H):
            sketches[i] = self._sketch_one(X_flat_batch[i])

        # Negative squared distance to class means
        # logits = -||s - mean||^2
        diffs = sketches[:, None, :] - self.means[None, :, :]
        logits = -np.sum(diffs * diffs, axis=2)
        return logits.astype(np.float32)

# =============================================================================
# MDL COMPRESSION PRIOR (batched + masked rank support)
# =============================================================================

class CompressionPrior:
    """PCA/MDL prior (pattern + sparse exceptions)."""
    def __init__(self, pca_rank=8):
        self.pca_rank = pca_rank
        self.templates = {}
        self.bases = {}
        self.trained = False

    def train(self, X_flat, Y):
        labels = Y.argmax(1)
        for d in range(10):
            mask = labels == d
            if mask.sum() < self.pca_rank + 2:
                continue

            X_d = X_flat[mask]
            mu = X_d.mean(0)
            self.templates[d] = mu.astype(np.float32)

            centered = (X_d - mu).astype(np.float32)
            try:
                U, S, Vt = np.linalg.svd(centered, full_matrices=False)
                self.bases[d] = Vt[:self.pca_rank].T.astype(np.float32)  # (784,rank)
            except Exception:
                self.bases[d] = np.eye(784, self.pca_rank, dtype=np.float32)

        self.trained = True

    def get_logits_batch(self, X_flat_batch: np.ndarray) -> np.ndarray:
        """
        Batched logits for inputs (H,784).
        Uses masked rank images during inference for camouflage robustness.
        """
        H = X_flat_batch.shape[0]
        logits = np.full((H, 10), -100.0, dtype=np.float32)
        if not self.trained:
            return logits

        for d in range(10):
            if d not in self.templates:
                continue
            mu = self.templates[d]
            B = self.bases[d]  # (784,rank)

            centered = (X_flat_batch - mu[None, :]).astype(np.float32)
            coeffs = centered @ B  # (H,rank)
            recon = mu[None, :] + coeffs @ B.T  # (H,784)
            residual = np.abs(X_flat_batch - recon)

            coeff_cost = np.sum(np.abs(coeffs), axis=1) * 0.10
            exception_cost = np.sum(residual > 0.15, axis=1) * 0.30
            residual_cost = np.sum(residual, axis=1) * 0.15

            logits[:, d] = -(coeff_cost + exception_cost + residual_cost)

        return logits

# =============================================================================
# NEURAL CLASSIFIER (same as baseline, but supports batch)
# =============================================================================

class NeuralClassifier:
    """Efficient 3-layer MLP."""
    def __init__(self, input_dim, hidden1=128, hidden2=64, seed=42):
        rng = np.random.RandomState(seed)
        self.W1 = rng.randn(input_dim, hidden1) * np.sqrt(2.0 / input_dim)
        self.b1 = np.zeros(hidden1)
        self.W2 = rng.randn(hidden1, hidden2) * np.sqrt(2.0 / hidden1)
        self.b2 = np.zeros(hidden2)
        self.W3 = rng.randn(hidden2, 10) * np.sqrt(2.0 / hidden2)
        self.b3 = np.zeros(10)

    def forward(self, X):
        h1 = np.maximum(0, X @ self.W1 + self.b1)
        h2 = np.maximum(0, h1 @ self.W2 + self.b2)
        logits = h2 @ self.W3 + self.b3
        logits = logits - logits.max(axis=-1, keepdims=True)
        exp_logits = np.exp(logits)
        probs = exp_logits / (exp_logits.sum(axis=-1, keepdims=True) + 1e-10)
        self._cache = (X, h1, h2, probs)
        return probs

    def backward(self, lr=0.01, wd=0.001, Y=None):
        X, h1, h2, probs = self._cache
        batch = X.shape[0]
        dlogits = (probs - Y) / batch

        dW3 = h2.T @ dlogits + wd * self.W3
        db3 = dlogits.sum(0)
        dh2 = dlogits @ self.W3.T
        dh2[h2 <= 0] = 0

        dW2 = h1.T @ dh2 + wd * self.W2
        db2 = dh2.sum(0)
        dh1 = dh2 @ self.W2.T
        dh1[h1 <= 0] = 0

        dW1 = X.T @ dh1 + wd * self.W1
        db1 = dh1.sum(0)

        self.W3 -= lr * dW3; self.b3 -= lr * db3
        self.W2 -= lr * dW2; self.b2 -= lr * db2
        self.W1 -= lr * dW1; self.b1 -= lr * db1

# =============================================================================
# ATHENA v78Q-NP
# =============================================================================

def js_divergence(P: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """
    Jensen–Shannon divergence across branch distributions.
    P shape: (H, B, 10)
    returns: (H,)
    """
    P = np.clip(P, eps, 1.0)
    P = P / P.sum(axis=2, keepdims=True)
    M = P.mean(axis=1)  # (H,10)
    kl = np.sum(P * (np.log(P) - np.log(M[:, None, :])), axis=2)  # (H,B)
    js = kl.mean(axis=1)
    return js


def iou(a: np.ndarray, b: np.ndarray) -> float:
    a = a.astype(bool)
    b = b.astype(bool)
    inter = np.logical_and(a, b).sum()
    union = np.logical_or(a, b).sum() + 1e-8
    return float(inter) / float(union)

class AthenaNeuralNetworkV78Q:
    """
    Pure NumPy/SciPy quantum-like emergence engine.

    - 6 attention modes (frame charts)
    - K thresholds per mode => H hypotheses
    - flow–prune (keep top N)
    - branch fusion: classifier × MDL × sketch, disagreement gating
    - amplitude collapse
    """

    def __init__(self):
        self.feature_dim = 523
        self.classifier = NeuralClassifier(self.feature_dim, hidden1=128, hidden2=64)
        self.mdl_prior = CompressionPrior(pca_rank=8)
        self.sketch_prior = SketchPrior(out_dim=128, pad_dim=1024, seed=123)

        self.feat_mean = None
        self.feat_std = None

        # Hypothesis parameters
        self.taus = np.linspace(0.25, 0.80, 8).tolist()  # 8 thresholds
        self.keep_top = 12  # flow–prune

        # Fusion temperatures
        self.mdl_temp = 0.6
        self.sketch_temp = 0.6

        # Energy weights
        self.w_js = 1.2
        self.w_cmp = 0.15
        self.w_spin = 0.35  # commutator defect weight (Ω∘D vs D∘Ω)
        self.w_nll = 1.0

    def _generate_hypotheses(self, img):
        R = rank_transform(img)
        mag, ang, gx, gy = compute_gradients(R)
        att_modes = generate_attention_modes(R, gx=gx, gy=gy, base_iters=7)

        masks = []
        qualities = []
        meta = []  # (mode_idx, tau)
        for mi, u in enumerate(att_modes):
            for tau in self.taus:
                m = generate_mask_from_u(u, R, float(tau))
                if m.sum() < 15:
                    continue
                q = mask_quality(mag, m)
                masks.append(m)
                qualities.append(q)
                meta.append((mi, float(tau)))

        if len(masks) == 0:
            # fallback
            m = (R > 0.3).astype(np.float32)
            masks = [m]
            qualities = [0.0]
            meta = [(0, 0.3)]

        masks = np.stack(masks, axis=0).astype(np.float32)  # (H,28,28)
        qualities = np.array(qualities, dtype=np.float32)
        return R, mag, ang, gx, gy, att_modes, masks, qualities, meta

    def train(self, X_train, Y_train, epochs=20, lr=0.03, batch_size=32, verbose=True):
        """
        Training with feature caching. Mask selection uses multi-hypothesis search (top quality).
        """
        n = len(X_train)
        rng = np.random.RandomState(42)

        if verbose:
            print("  Training MDL prior (rank-space)...")
        # Train priors on rank-transformed images for noise/camouflage robustness
        X_rank = np.zeros_like(X_train, dtype=np.float32)
        for i in range(n):
            X_rank[i] = rank_transform(X_train[i].reshape(28,28)).reshape(-1)
        self.mdl_prior.train(X_rank, Y_train)
        self.sketch_prior.train(X_rank, Y_train)

        if verbose:
            print("  Extracting features (cached, best hypothesis)...")

        all_features = np.zeros((n, self.feature_dim), dtype=np.float32)

        for i in range(n):
            img = X_train[i].reshape(28, 28).astype(np.float32)
            R, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses(img)
            best = int(np.argmax(qualities))
            feats = extract_all_features_batch(img, masks[best:best+1])[0]
            all_features[i] = feats

        self.feat_mean = all_features.mean(0)
        self.feat_std = all_features.std(0) + 1e-8
        Xn = (all_features - self.feat_mean) / self.feat_std

        if verbose:
            print("  Training classifier...")
        for ep in range(epochs):
            idx = rng.permutation(n)
            epoch_loss = 0.0
            n_batches = 0

            for start in range(0, n, batch_size):
                bidx = idx[start:start+batch_size]
                Xb = Xn[bidx]
                Yb = Y_train[bidx]

                probs = self.classifier.forward(Xb)
                loss = -np.sum(Yb * np.log(probs + 1e-10)) / len(Yb)
                epoch_loss += loss
                n_batches += 1
                self.classifier.backward(lr=lr, wd=0.002, Y=Yb)

            if verbose and (ep + 1) % 5 == 0:
                print(f"    Epoch {ep+1}: loss={epoch_loss/n_batches:.4f}")

    def forward(self, img: np.ndarray):
        """
        Quantum-like multi-hypothesis inference with energy-based amplitude collapse.
        """
        img = img.astype(np.float32)
        R, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses(img)

        # Flow–prune: keep top hypotheses by quality
        order = np.argsort(-qualities)
        keep = order[:min(self.keep_top, len(order))]
        masks_k = masks[keep]
        qual_k = qualities[keep]

        # Full features in batch
        feats = extract_all_features_batch(img, masks_k)
        if self.feat_mean is not None:
            feats = (feats - self.feat_mean) / self.feat_std

        # Branch 1: classifier
        p_cls = self.classifier.forward(feats)  # (H,10)

        # Branch 2: MDL prior on masked rank images
        X_flat = (R[None, :, :] * masks_k).reshape(masks_k.shape[0], -1).astype(np.float32)
        mdl_logits = self.mdl_prior.get_logits_batch(X_flat)
        p_mdl = scipy_softmax(mdl_logits * self.mdl_temp, axis=1)

        # Branch 3: Hadamard sketch prior (masked rank)
        sk_logits = self.sketch_prior.get_logits_batch(X_flat)
        p_skw = scipy_softmax(sk_logits * self.sketch_temp, axis=1)

        # Branch weights by entropy (lower entropy => higher weight)
        def entropy(p):
            p = np.clip(p, 1e-10, 1.0)
            return -np.sum(p * np.log(p), axis=1)

        H_cls = entropy(p_cls)
        H_mdl = entropy(p_mdl)
        H_skw = entropy(p_skw)

        w_cls = 1.0 / (H_cls + 0.6)
        w_mdl = 1.0 / (H_mdl + 0.6)
        w_skw = 1.0 / (H_skw + 0.6)
        w_sum = w_cls + w_mdl + w_skw
        w_cls /= w_sum; w_mdl /= w_sum; w_skw /= w_sum

        # Fuse: product-of-experts with weights (log domain)
        logp = (w_cls[:, None] * np.log(np.clip(p_cls, 1e-10, 1.0)) +
                w_mdl[:, None] * np.log(np.clip(p_mdl, 1e-10, 1.0)) +
                w_skw[:, None] * np.log(np.clip(p_skw, 1e-10, 1.0)))
        fused = np.exp(logp - logp.max(axis=1, keepdims=True))
        fused = fused / (fused.sum(axis=1, keepdims=True) + 1e-10)

        # Disagreement: JS divergence among branches
        P_stack = np.stack([p_cls, p_mdl, p_skw], axis=1)  # (H,3,10)
        js = js_divergence(P_stack)

        # Complexity proxy: penalize extreme masks + boundary noise
        comp = np.zeros_like(qual_k)
        for i in range(masks_k.shape[0]):
            m = masks_k[i]
            area = m.sum() / 784.0
            er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.float32)
            boundary = m - er
            per = boundary.sum() / 784.0
            comp[i] = abs(area - 0.18) + 0.8 * per

        # Energy: NLL + disagreement + complexity + spin/holonomy (lower is better)
        top = fused.max(axis=1)
        nll = -np.log(np.clip(top, 1e-10, 1.0))

        # Spin / commutator defect (Ω∘D vs D∘Ω) for kept hypotheses
        spin = np.zeros_like(js, dtype=np.float32)
        for i, orig_idx in enumerate(keep):
            mi, tau = meta[int(orig_idx)]
            u_mode = att_modes[int(mi)]
            # Ω∘D: diffuse u then project
            u_om = anisotropic_diffuse(u_mode, gx=gx, gy=gy, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_om = generate_mask_from_u(u_om, R, float(tau))
            # D∘Ω: project then diffuse the binary mask and re-threshold
            m_base = masks_k[i]
            u_m = anisotropic_diffuse(m_base, gx=gx, gy=gy, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_mo = (u_m > 0.5).astype(np.float32)
            spin[i] = 1.0 - iou(m_om, m_mo)
        energy = self.w_nll * nll + self.w_js * js + self.w_cmp * comp + self.w_spin * spin

        # Amplitude collapse (soft)
        amps = scipy_softmax(-energy * 2.5)

        final = (amps[:, None] * fused).sum(axis=0)
        final = final / (final.sum() + 1e-10)

        # Confidence: peak prob × peak amplitude
        confidence = float(final.max() * amps.max())

        pred = int(final.argmax())
        return pred, final, confidence

    def predict(self, X):
        preds = np.zeros(len(X), dtype=np.int32)
        for i in range(len(X)):
            preds[i] = self.forward(X[i].reshape(28, 28))[0]
        return preds

    def evaluate(self, X_test, Y_test, verbose=True):
        correct = 0
        n = len(X_test)
        for i in range(n):
            pred, _, _ = self.forward(X_test[i].reshape(28, 28))
            if pred == int(Y_test[i].argmax()):
                correct += 1
        acc = correct / n
        if verbose:
            print(f"  Accuracy: {acc*100:.1f}%")
        return acc

    def get_param_count(self):
        # classifier params
        clf = (self.classifier.W1.size + self.classifier.b1.size +
               self.classifier.W2.size + self.classifier.b2.size +
               self.classifier.W3.size + self.classifier.b3.size)
        # priors are templates/bases (approx count)
        mdl = 10 * 784 + 10 * 784 * 8
        sk = 10 * 128
        return int(clf + mdl + sk)

# =============================================================================
# Synthetic benchmark helpers (copied/adapted from baseline)
# =============================================================================

def draw_digit(d):
    img = np.zeros((28, 28), dtype=np.float32)

    def line(y0, x0, y1, x1):
        n = max(abs(y1-y0), abs(x1-x0), 1)
        for i in range(n+1):
            y = int(y0 + (y1-y0)*i/n)
            x = int(x0 + (x1-x0)*i/n)
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0,y-1):min(28,y+2), max(0,x-1):min(28,x+2)] = 1.0

    def circle(cy, cx, r):
        for angle in np.linspace(0, 2*np.pi, int(2*np.pi*r*2)):
            y, x = int(cy + r*np.sin(angle)), int(cx + r*np.cos(angle))
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0,y-1):min(28,y+2), max(0,x-1):min(28,x+2)] = 1.0

    if d == 0: circle(14, 14, 8)
    elif d == 1: line(6, 14, 22, 14)
    elif d == 2:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 14, 10)
        for i in range(8): img[14, 10+i] = 1.0
        line(14, 10, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 3:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 14, 14)
        for i in range(5): img[14, 12+i] = 1.0
        line(14, 14, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 4:
        line(6, 10, 14, 10)
        line(14, 10, 14, 18)
        line(6, 18, 22, 18)
    elif d == 5:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 10, 14, 10)
        for i in range(8): img[14, 10+i] = 1.0
        line(14, 17, 22, 17)
        for i in range(8): img[22, 10+i] = 1.0
    elif d == 6:
        circle(16, 14, 6)
        line(6, 10, 16, 10)
    elif d == 7:
        for i in range(8): img[6, 10+i] = 1.0
        line(6, 17, 22, 12)
    elif d == 8:
        circle(10, 14, 4)
        circle(18, 14, 4)
    elif d == 9:
        circle(10, 14, 5)
        line(10, 19, 22, 19)

    img = ndimage.gaussian_filter(img, 0.8)
    return img / (img.max() + 1e-8)

def aug_geometric(img, rng):
    angle = rng.uniform(-25, 25)
    scale = rng.uniform(0.9, 1.1)
    img = ndimage.rotate(img, angle, reshape=False, mode='constant')
    img = ndimage.zoom(img, scale, mode='constant')
    h, w = img.shape
    if h > 28:
        s = (h - 28) // 2
        img = img[s:s+28, s:s+28]
    elif h < 28:
        pad = (28 - h) // 2
        img = np.pad(img, ((pad, 28-h-pad), (pad, 28-w-pad)), mode='constant')
    return np.clip(img[:28, :28], 0, 1)

def aug_adversarial(img, rng):
    noise = rng.randn(*img.shape) * 0.25
    return np.clip(img + noise, 0, 1)

def aug_cluttered(img, rng):
    out = img.copy()
    for _ in range(rng.randint(3, 7)):
        y, x = rng.randint(0, 24), rng.randint(0, 24)
        s = rng.randint(2, 4)
        out[y:y+s, x:x+s] = rng.uniform(0.1, 0.3)
    return out

def aug_camouflage(img, rng):
    freq = rng.uniform(0.3, 0.6)
    phase = rng.uniform(0, 2*np.pi)
    y, x = np.ogrid[:28, :28]
    texture = 0.5 + 0.25 * np.sin(freq * x + phase) * np.cos(freq * y + phase * 0.7)
    texture += rng.randn(28, 28) * 0.08
    contrast = rng.uniform(0.15, 0.28)
    fg = texture + contrast
    bg = texture
    mask = img > 0.3
    out = np.where(mask, fg, bg)
    return np.clip(out, 0, 1)

def generate_data(n, aug_fn, seed):
    rng = np.random.RandomState(seed)
    X = np.zeros((n, 784), dtype=np.float32)
    Y = np.zeros((n, 10), dtype=np.float32)
    for i in range(n):
        d = rng.randint(0, 10)
        X[i] = aug_fn(draw_digit(d), rng).flatten()
        Y[i, d] = 1
    return X, Y

def run_benchmark():
    import time
    benchmarks = [
        ('GEOMETRIC', aug_geometric),
        ('ADVERSARIAL', aug_adversarial),
        ('CLUTTERED', aug_cluttered),
        ('CAMOUFLAGE', aug_camouflage),
    ]

    results = {}
    for name, aug_fn in benchmarks:
        print(f"\n{'='*50}\n{name.center(50)}\n{'='*50}")
        X_train, Y_train = generate_data(1000, aug_fn, 42)
        X_test, Y_test = generate_data(250, aug_fn, 142)

        model = AthenaNeuralNetworkV78Q()
        t0 = time.time()
        model.train(X_train, Y_train, epochs=15, lr=0.03, verbose=True)
        train_time = time.time() - t0

        t0 = time.time()
        acc = model.evaluate(X_test, Y_test, verbose=True)
        infer_time = time.time() - t0

        results[name] = acc
        print(f"Train time: {train_time:.2f}s | Infer: {infer_time/len(X_test)*1000:.2f} ms/sample | Params: {model.get_param_count():,}")

    print("\nFINAL RESULTS")
    for k, v in results.items():
        print(f"{k:<12}: {v*100:5.1f}%")
    print(f"AVG       : {np.mean(list(results.values()))*100:5.1f}%")
    return results

if __name__ == "__main__":
    run_benchmark()
