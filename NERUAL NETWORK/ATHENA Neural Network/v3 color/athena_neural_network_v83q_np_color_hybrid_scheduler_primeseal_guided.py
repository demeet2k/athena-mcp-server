
"""
ATHENA NEURAL NETWORK v83Q-NP-COLOR-HYBRID-SCHED-PRIMEGUIDE
============================

Pure NumPy/SciPy "Quantum-like" Emergence Compiler upgrade of athena_neural_network.py.

Key upgrades vs v76.1 optimized baseline:
- 6-mode anisotropic attention (base-6 frame charts)
- Multi-hypothesis bank (modes × thresholds) with flow–prune scheduling
- Batched feature extraction across hypotheses (vectorized HOG + Polar)
- True branch disagreement (JS divergence) and energy-based amplitude collapse
- Deeper compression prior: PCA/MDL on *masked rank images* + Hadamard sketch prior
- Deterministic prime tunnel scheduler (braiders → lock bursts)
- PrimeSeal tie-break (modular parity + micro-perturbation stability)
- NEW: PrimeSeal-guided lock selection (choose 65 vs 133 vs 385 by expected seal+tri-lock)

Notes:
- Keeps invariant core features.

Author: Emergence Compiler Framework
Version: v83Q-NP-COLOR-HYBRID-SCHED-PRIMEGUIDE
"""

from __future__ import annotations
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

# =============================================================================
# COLOR VISION UTILITIES (RGB → YUV opponents) + general input handling
# =============================================================================

def ensure_rgb(img: np.ndarray) -> np.ndarray:
    """Return an RGB float32 image in [0,1] with shape (H,W,3)."""
    if img.ndim == 2:
        x = img.astype(np.float32)
        x = np.clip(x, 0.0, 1.0)
        return np.repeat(x[:, :, None], 3, axis=2)
    if img.ndim == 3:
        x = img[..., :3].astype(np.float32)
        # If input looks like 0..255, normalize
        if x.max() > 1.5:
            x = x / 255.0
        return np.clip(x, 0.0, 1.0)
    raise ValueError(f"Unsupported image shape: {img.shape}")

def rgb_to_yuv(rgb: np.ndarray):
    """Convert RGB in [0,1] to a YUV/opponent-like space."""
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]
    # Luminance (Rec.709)
    Y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    # Opponents (simple, stable)
    U = r - g
    V = 0.5 * (r + g) - b
    return Y.astype(np.float32), U.astype(np.float32), V.astype(np.float32)

def chroma_mag(U: np.ndarray, V: np.ndarray) -> np.ndarray:
    return np.sqrt(U * U + V * V).astype(np.float32)

def as_image(x: np.ndarray, side: int = 28) -> np.ndarray:
    """Accept flat (784 or 2352) or shaped images; return RGB (side,side,3)."""
    if x.ndim == 1:
        if x.size == side * side:
            return ensure_rgb(x.reshape(side, side))
        if x.size == side * side * 3:
            return ensure_rgb(x.reshape(side, side, 3))
        raise ValueError(f"Unsupported flat length: {x.size}")
    return ensure_rgb(x)

def compute_gradients(img: np.ndarray):
    """
    Gradients for grayscale or RGB images.
    - If img is (H,W): Sobel on img.
    - If img is (H,W,3): Di Zenzo color gradient on (Y,U,V) opponent channels.
    Returns: mag, ang, gx, gy (all float32, shape HxW).
    """
    if img.ndim == 2:
        gy = ndimage.sobel(img, axis=0)
        gx = ndimage.sobel(img, axis=1)
        mag = np.sqrt(gx * gx + gy * gy)
        ang = np.arctan2(gy, gx)
        return mag.astype(np.float32), ang.astype(np.float32), gx.astype(np.float32), gy.astype(np.float32)

    rgb = ensure_rgb(img)
    Y, U, V = rgb_to_yuv(rgb)

    gxY = ndimage.sobel(Y, axis=1); gyY = ndimage.sobel(Y, axis=0)
    gxU = ndimage.sobel(U, axis=1); gyU = ndimage.sobel(U, axis=0)
    gxV = ndimage.sobel(V, axis=1); gyV = ndimage.sobel(V, axis=0)

    # Di Zenzo structure tensor terms
    A = gxY * gxY + gxU * gxU + gxV * gxV
    B = gyY * gyY + gyU * gyU + gyV * gyV
    C = gxY * gyY + gxU * gyU + gxV * gyV

    ang = 0.5 * np.arctan2(2.0 * C, (A - B) + 1e-8)
    # Largest eigenvalue of tensor -> edge strength
    mag = np.sqrt(0.5 * (A + B + np.sqrt((A - B) ** 2 + 4.0 * C * C)))

    gx = mag * np.cos(ang)
    gy = mag * np.sin(ang)
    return mag.astype(np.float32), ang.astype(np.float32), gx.astype(np.float32), gy.astype(np.float32)

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
# COLOR FEATURES (batched): opponent stats + boundary contrast + hue histogram
# =============================================================================

def extract_color_stats_batch(rgb: np.ndarray, masks: np.ndarray, hue_bins: int = 8) -> np.ndarray:
    """Return (Hh, 18) color stats for each mask."""
    rgb = ensure_rgb(rgb)
    Y, U, V = rgb_to_yuv(rgb)
    C = chroma_mag(U, V)
    hue = np.arctan2(V, U)  # [-pi,pi]

    Hh = masks.shape[0]
    m = masks.astype(np.float32)
    denom = m.sum(axis=(1,2)) + 1e-8

    # Inside means
    def wmean(field):
        return (field[None,:,:] * m).sum(axis=(1,2)) / denom

    def wvar(field, mean):
        return ((field[None,:,:] - mean[:,None,None])**2 * m).sum(axis=(1,2)) / denom

    muY = wmean(Y)
    muU = wmean(U)
    muV = wmean(V)
    muC = wmean(C)
    sdU = np.sqrt(wvar(U, muU) + 1e-8)
    sdV = np.sqrt(wvar(V, muV) + 1e-8)
    sdC = np.sqrt(wvar(C, muC) + 1e-8)

    # Boundary ring contrast (1-step dilation ring)
    ring = np.zeros_like(m)
    for i in range(Hh):
        dil = ndimage.binary_dilation(m[i] > 0.5, iterations=1)
        ring[i] = (dil.astype(np.float32) - (m[i] > 0.5).astype(np.float32))
    ring_denom = ring.sum(axis=(1,2)) + 1e-8

    def ringmean(field):
        return (field[None,:,:] * ring).sum(axis=(1,2)) / ring_denom

    rY = ringmean(Y)
    rU = ringmean(U)
    rV = ringmean(V)
    cY = muY - rY
    cU = muU - rU
    cV = muV - rV

    # Hue histogram weighted by chroma inside mask
    hb = (((hue + np.pi) / (2*np.pi)) * hue_bins).astype(np.int32)
    hb = np.clip(hb, 0, hue_bins-1)
    hb_idx = hb.ravel()
    w = (C[None,:,:] * m).reshape(Hh, -1).astype(np.float32)
    bins = np.zeros((Hh, hue_bins), dtype=np.float32)
    idx_h = np.repeat(np.arange(Hh, dtype=np.int32), hb_idx.size)
    idx_b = np.tile(hb_idx, Hh)
    np.add.at(bins, (idx_h, idx_b), w.reshape(-1))
    bins = bins / (bins.sum(axis=1, keepdims=True) + 1e-8)

    feats = np.concatenate([
        muU[:,None], sdU[:,None], muV[:,None], sdV[:,None],
        muC[:,None], sdC[:,None], muY[:,None],
        cY[:,None], cU[:,None], cV[:,None],
        bins
    ], axis=1).astype(np.float32)
    # dims: 1+1+1+1+1+1+1 +3 + hue_bins = 10 + hue_bins -> 18 when hue_bins=8
    return feats

# =============================================================================
# MATH TRICK 6: CONTOUR + SKELETON DESCRIPTORS (camouflage breaker, NumPy/SciPy)
# =============================================================================

def _neighbors8_count(bin_img: np.ndarray) -> np.ndarray:
    """Count 8-neighbors for each pixel in a binary image."""
    b = bin_img.astype(np.uint8)
    s = (
        np.roll(np.roll(b, 1, 0), 1, 1) + np.roll(b, 1, 0) + np.roll(np.roll(b, 1, 0), -1, 1) +
        np.roll(b, 1, 1) + np.roll(b, -1, 1) +
        np.roll(np.roll(b, -1, 0), 1, 1) + np.roll(b, -1, 0) + np.roll(np.roll(b, -1, 0), -1, 1)
    )
    # zero borders to avoid wrap artifacts
    s[0, :] = 0; s[-1, :] = 0; s[:, 0] = 0; s[:, -1] = 0
    return s.astype(np.int32)

def zhang_suen_thinning(bin_img: np.ndarray, max_iter: int = 32) -> np.ndarray:
    """
    Zhang–Suen thinning for 2D binary images.
    Pure NumPy; fine for 28x28 masks on a small set of hypotheses.
    Returns skeleton as uint8 {0,1}.
    """
    img = (bin_img > 0).astype(np.uint8).copy()
    H, W = img.shape
    if img.sum() == 0:
        return img

    def transitions(p2, p3, p4, p5, p6, p7, p8, p9):
        # count 0->1 transitions in the ordered neighbor sequence
        seq = [p2,p3,p4,p5,p6,p7,p8,p9,p2]
        t = 0
        for i in range(8):
            t += (seq[i] == 0 and seq[i+1] == 1)
        return t

    # neighbor offsets (p2..p9)
    nbrs = [(-1,0), (-1,1), (0,1), (1,1), (1,0), (1,-1), (0,-1), (-1,-1)]

    for _ in range(max_iter):
        changed = False
        to_del = []

        # Step 1
        for y in range(1, H-1):
            for x in range(1, W-1):
                if img[y,x] == 0:
                    continue
                ps = [img[y+dy, x+dx] for dy,dx in nbrs]
                p2,p3,p4,p5,p6,p7,p8,p9 = ps
                N = sum(ps)
                if N < 2 or N > 6:
                    continue
                S = transitions(p2,p3,p4,p5,p6,p7,p8,p9)
                if S != 1:
                    continue
                if p2*p4*p6 != 0:
                    continue
                if p4*p6*p8 != 0:
                    continue
                to_del.append((y,x))

        if to_del:
            changed = True
            for y,x in to_del:
                img[y,x] = 0

        to_del = []
        # Step 2
        for y in range(1, H-1):
            for x in range(1, W-1):
                if img[y,x] == 0:
                    continue
                ps = [img[y+dy, x+dx] for dy,dx in nbrs]
                p2,p3,p4,p5,p6,p7,p8,p9 = ps
                N = sum(ps)
                if N < 2 or N > 6:
                    continue
                S = transitions(p2,p3,p4,p5,p6,p7,p8,p9)
                if S != 1:
                    continue
                if p2*p4*p8 != 0:
                    continue
                if p2*p6*p8 != 0:
                    continue
                to_del.append((y,x))

        if to_del:
            changed = True
            for y,x in to_del:
                img[y,x] = 0

        if not changed:
            break

    return img

def mask_invariants(mask: np.ndarray):
    """
    Small integer invariants used for 7/19 dual-lock stability checks.
    Returns tuple: (area, perimeter, holes, cx_bin, cy_bin)
    """
    m = (mask > 0.5).astype(np.uint8)
    area = int(m.sum())

    er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.uint8)
    boundary = m - er
    per = int(boundary.sum())

    filled = ndimage.binary_fill_holes(m).astype(np.uint8)
    holes_img = filled - m
    _, holes = ndimage.label(holes_img)

    if area > 0:
        cy, cx = ndimage.center_of_mass(m)
        cx_bin = int(np.clip(round(cx), 0, 27))
        cy_bin = int(np.clip(round(cy), 0, 27))
    else:
        cx_bin = 14
        cy_bin = 14

    return area, per, int(holes), cx_bin, cy_bin

def contour_fourier_descriptor(mask: np.ndarray, k: int = 10):
    """
    Simple Fourier descriptors from boundary points.
    - boundary points sorted by angle around centroid (fast, deterministic)
    - returns 2k dims: real/imag of coefficients 1..k, normalized
    """
    m = (mask > 0.5).astype(np.uint8)
    if m.sum() < 5:
        return np.zeros((2*k,), dtype=np.float32)

    er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.uint8)
    boundary = (m - er).astype(bool)
    ys, xs = np.where(boundary)
    if ys.size < 8:
        return np.zeros((2*k,), dtype=np.float32)

    cy, cx = ndimage.center_of_mass(m)
    dy = ys.astype(np.float32) - float(cy)
    dx = xs.astype(np.float32) - float(cx)
    ang = np.arctan2(dy, dx)
    order = np.argsort(ang)
    dy = dy[order]
    dx = dx[order]

    z = dx + 1j * dy
    # normalize scale
    scale = np.sqrt((dx*dx + dy*dy).mean()) + 1e-8
    z = z / scale

    Z = np.fft.fft(z)
    # discard DC component
    coeffs = Z[1:k+1]
    # normalize by first harmonic magnitude
    norm = np.abs(coeffs[0]) + 1e-8
    coeffs = coeffs / norm

    out = np.zeros((2*k,), dtype=np.float32)
    out[0::2] = np.real(coeffs).astype(np.float32)
    out[1::2] = np.imag(coeffs).astype(np.float32)
    return out

def curvature_histogram(mask: np.ndarray, bins: int = 8):
    """
    Approx curvature histogram from ordered boundary points (angle differences).
    Returns (bins,) float32 normalized.
    """
    m = (mask > 0.5).astype(np.uint8)
    if m.sum() < 5:
        return np.zeros((bins,), dtype=np.float32)

    er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.uint8)
    boundary = (m - er).astype(bool)
    ys, xs = np.where(boundary)
    if ys.size < 12:
        return np.zeros((bins,), dtype=np.float32)

    cy, cx = ndimage.center_of_mass(m)
    dy = ys.astype(np.float32) - float(cy)
    dx = xs.astype(np.float32) - float(cx)
    ang = np.arctan2(dy, dx)
    order = np.argsort(ang)
    ys = ys[order].astype(np.float32)
    xs = xs[order].astype(np.float32)

    # compute turning angles between successive segments
    dx1 = np.roll(xs, -1) - xs
    dy1 = np.roll(ys, -1) - ys
    dx0 = xs - np.roll(xs, 1)
    dy0 = ys - np.roll(ys, 1)

    a0 = np.arctan2(dy0, dx0)
    a1 = np.arctan2(dy1, dx1)
    dtheta = np.arctan2(np.sin(a1-a0), np.cos(a1-a0))
    curv = np.abs(dtheta)

    # hist in [0, pi]
    idx = np.floor(curv / np.pi * bins).astype(np.int32)
    idx = np.clip(idx, 0, bins-1)
    hist = np.zeros((bins,), dtype=np.float32)
    np.add.at(hist, idx, 1.0)
    hist /= (hist.sum() + 1e-8)
    return hist

def skeleton_stats(mask: np.ndarray):
    """
    Skeleton stats: endpoints, junctions, length, mean stroke width, var stroke width.
    Returns 5 dims.
    """
    m = (mask > 0.5).astype(np.uint8)
    if m.sum() < 8:
        return np.zeros((5,), dtype=np.float32)

    sk = zhang_suen_thinning(m, max_iter=32)
    if sk.sum() == 0:
        return np.zeros((5,), dtype=np.float32)

    n8 = _neighbors8_count(sk)
    endpoints = int(((sk > 0) & (n8 == 1)).sum())
    junctions = int(((sk > 0) & (n8 >= 3)).sum())
    length = int(sk.sum())

    dist = ndimage.distance_transform_edt(m)
    widths = (dist * sk).astype(np.float32)
    vals = widths[widths > 0]
    if vals.size == 0:
        return np.array([endpoints, junctions, length, 0.0, 0.0], dtype=np.float32)

    # stroke width approx = 2*distance
    sw = 2.0 * vals
    return np.array([endpoints, junctions, length, float(sw.mean()), float(sw.var())], dtype=np.float32)

def extract_contour_batch(masks: np.ndarray, fd_k: int = 10, curv_bins: int = 8) -> np.ndarray:
    """
    Return contour descriptor features per mask.
    dims = Fourier(2*fd_k) + curvature(curv_bins) + skeleton(5) = 2*fd_k + curv_bins + 5
    """
    H = masks.shape[0]
    dim = 2*fd_k + curv_bins + 5
    out = np.zeros((H, dim), dtype=np.float32)
    for i in range(H):
        m = masks[i]
        fd = contour_fourier_descriptor(m, k=fd_k)
        ch = curvature_histogram(m, bins=curv_bins)
        ss = skeleton_stats(m)
        out[i] = np.concatenate([fd, ch, ss], axis=0)
    return out.astype(np.float32)

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

def extract_all_features_batch(img: np.ndarray, masks: np.ndarray, gabor_bank: LogGaborBank | None = None) -> np.ndarray:
    """
    Batched feature extraction for selected masks.
    Supports grayscale or RGB input.
    Output dims:
      base=523 (HOG 441 + Polar 64 + Topology 12 + Struct 6)
      + gabor=2*n_filters (default 36)
      + color=10+hue_bins (default 18)
    """
    rgb = ensure_rgb(img)
    Y, _, _ = rgb_to_yuv(rgb)
    R = rank_transform(Y)
    mag, ang, _, _ = compute_gradients(rgb)

    hog = extract_hog_batch(mag, ang, masks)           # (H,441)
    polar = extract_polar_batch(R, masks)              # (H,64)

    topo = np.zeros((masks.shape[0], 12), dtype=np.float32)
    for i in range(masks.shape[0]):
        topo[i] = extract_topology(masks[i])

    struct = extract_structure_batch(R, masks)         # (H,6)

    color = extract_color_stats_batch(rgb, masks, hue_bins=8)  # (H,18)

    if gabor_bank is not None:
        Ey, Ec = gabor_bank.energy_maps(rgb)
        g1 = gabor_bank.pool_features(Ey, masks)
        g2 = gabor_bank.pool_features(Ec, masks)
        gabor = np.concatenate([g1, g2], axis=1)  # (H,2*F)
    else:
        gabor = np.zeros((masks.shape[0], 0), dtype=np.float32)

    contour = extract_contour_batch(masks, fd_k=10, curv_bins=8)  # (H,33)

    return np.concatenate([hog, polar, topo, struct, contour, gabor, color], axis=1).astype(np.float32)

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


class MeanPrior:
    """
    Simple class-mean prior on a feature subspace.
    Produces logits = -||x - μ_c||^2, useful as an additional independent branch.
    """
    def __init__(self, temp: float = 0.65):
        self.temp = temp
        self.means = None
        self.trained = False

    def train(self, X_feat: np.ndarray, Y_onehot: np.ndarray):
        labels = Y_onehot.argmax(1)
        C = 10
        d = X_feat.shape[1]
        means = np.zeros((C, d), dtype=np.float32)
        counts = np.zeros(C, dtype=np.int32)
        for x, y in zip(X_feat, labels):
            means[y] += x.astype(np.float32)
            counts[y] += 1
        for c in range(C):
            if counts[c] > 0:
                means[c] /= counts[c]
        self.means = means
        self.trained = True

    def get_logits_batch(self, X_feat: np.ndarray) -> np.ndarray:
        if not self.trained or self.means is None:
            return np.zeros((X_feat.shape[0], 10), dtype=np.float32)
        diffs = X_feat[:, None, :] - self.means[None, :, :]
        return (-np.sum(diffs * diffs, axis=2)).astype(np.float32)

    def get_probs_batch(self, X_feat: np.ndarray) -> np.ndarray:
        logits = self.get_logits_batch(X_feat)
        return scipy_softmax(logits * self.temp, axis=1).astype(np.float32)

# =============================================================================
# MDL COMPRESSION PRIOR (batched + masked rank support)
# =============================================================================


# =============================================================================
# MATH TRICK 5: LOG-GABOR FILTER BANK (scattering-like energy, color-aware)
# =============================================================================

class LogGaborBank:
    """
    Small log-Gabor filter bank computed in Fourier domain.
    Produces illumination-robust energy features (advanced vision) and works for RGB via Y and chroma magnitude.
    """
    def __init__(self, shape=(28, 28), n_scales: int = 3, n_orients: int = 6,
                 min_wavelength: float = 3.0, mult: float = 2.1, sigmaOnf: float = 0.55,
                 dThetaOnSigma: float = 1.2):
        self.shape = shape
        self.n_scales = n_scales
        self.n_orients = n_orients
        self.n_filters = n_scales * n_orients
        self.min_wavelength = min_wavelength
        self.mult = mult
        self.sigmaOnf = sigmaOnf
        self.dThetaOnSigma = dThetaOnSigma
        self.filters = self._build_filters().astype(np.float32)  # (F,H,W)

    def _build_filters(self):
        H, W = self.shape
        # Frequency grids in cycles/pixel
        y = (np.arange(H) - H // 2) / float(H)
        x = (np.arange(W) - W // 2) / float(W)
        yy, xx = np.meshgrid(y, x, indexing='ij')
        radius = np.sqrt(xx * xx + yy * yy)
        radius[H // 2, W // 2] = 1.0  # avoid log(0)
        theta = np.arctan2(-yy, xx)

        filters = []
        log_sigma = np.log(self.sigmaOnf)
        for s in range(self.n_scales):
            wavelength = self.min_wavelength * (self.mult ** s)
            fo = 1.0 / wavelength
            log_rad = np.log(radius / fo)
            radial = np.exp(-(log_rad * log_rad) / (2.0 * log_sigma * log_sigma))
            radial[H // 2, W // 2] = 0.0

            for o in range(self.n_orients):
                ang0 = o * np.pi / self.n_orients
                dtheta = np.arctan2(np.sin(theta - ang0), np.cos(theta - ang0))
                sigma_theta = (np.pi / self.n_orients) / self.dThetaOnSigma
                angular = np.exp(-(dtheta * dtheta) / (2.0 * sigma_theta * sigma_theta))
                filters.append(radial * angular)

        # shift back to FFT layout (0 freq at [0,0])
        filt = np.stack(filters, axis=0)
        filt = np.fft.ifftshift(filt, axes=(-2, -1))
        return filt

    def energy_maps(self, img_rgb_or_gray: np.ndarray):
        """Return (E_y, E_c) energy maps: shape (F,H,W) each."""
        rgb = ensure_rgb(img_rgb_or_gray)
        Y, U, V = rgb_to_yuv(rgb)
        C = chroma_mag(U, V)

        def _energy(ch):
            F = np.fft.fft2(ch)
            resp = np.fft.ifft2(F[None, :, :] * self.filters, axes=(-2, -1))
            return np.abs(resp).astype(np.float32)

        return _energy(Y.astype(np.float32)), _energy(C.astype(np.float32))

    def pool_features(self, E: np.ndarray, masks: np.ndarray):
        """Pool mean energy per filter within each mask. E:(F,H,W), masks:(Hh,H,W)->(Hh,F)."""
        Hh = masks.shape[0]
        denom = masks.sum(axis=(1,2)) + 1e-8
        feats = (E[None, :, :, :] * masks[:, None, :, :]).sum(axis=(2,3)) / denom[:, None]
        return feats.astype(np.float32)
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

class AthenaNeuralNetworkV80Q:
    """
    Pure NumPy/SciPy quantum-like emergence engine.

    - 6 attention modes (frame charts)
    - K thresholds per mode => H hypotheses
    - flow–prune (keep top N)
    - branch fusion: classifier × MDL × sketch, disagreement gating
    - amplitude collapse
    """

    def __init__(self):
        # Feature dims
        self.hue_bins = 8
        self.gabor_bank = LogGaborBank(shape=(28, 28), n_scales=3, n_orients=6)
        self.gabor_dim = 2 * self.gabor_bank.n_filters  # Y + chroma
        self.color_dim = 10 + self.hue_bins             # see extract_color_stats_batch
        self.contour_dim = 33                        # fd(20)+curv(8)+skel(5)
        self.base_dim = 523
        self.feature_dim = self.base_dim + self.contour_dim + self.gabor_dim + self.color_dim
        # Feature subspace slices
        self.slice_contour = slice(self.base_dim, self.base_dim + self.contour_dim)
        self.slice_gabor = slice(self.base_dim + self.contour_dim, self.base_dim + self.contour_dim + self.gabor_dim)
        self.slice_color = slice(self.base_dim + self.contour_dim + self.gabor_dim, self.feature_dim)

        self.classifier = NeuralClassifier(self.feature_dim, hidden1=160, hidden2=80)
        self.mdl_prior = CompressionPrior(pca_rank=10)
        self.sketch_prior = SketchPrior(out_dim=192, pad_dim=1024, seed=123)
        # Independent priors (additional branches)
        self.gabor_prior = MeanPrior(temp=0.55)
        self.contour_prior = MeanPrior(temp=0.60)

        self.feat_mean = None
        self.feat_std = None

        # Hypothesis parameters
        self.taus = np.linspace(0.25, 0.80, 10).tolist()  # 10 thresholds
        self.keep_top = 12  # flow–prune

        # Fusion temperatures
        self.mdl_temp = 0.55
        self.sketch_temp = 0.55

        # Energy weights
        self.w_js = 1.1
        self.w_cmp = 0.14
        self.w_spin = 0.40  # commutator defect weight (Ω∘D vs D∘Ω)
        # Dual-lock stability penalties (7 completion, 19 verifier)
        self.w_lock19 = 0.10
        self.w_lock7 = 0.04
        self.w_legal = 0.03  # ±7 mod 19 legality tie-break
        self.w_potential = 0.02  # 17/103 hypothesis landscape prior (tiny)
        self.w_nll = 1.0

    def _generate_hypotheses(self, img):
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        R = rank_transform(Y)
        # Rank-space gradients for HOG/shape; color-aware gradients for attention conductance
        mag_r, ang_r, _, _ = compute_gradients(R)
        mag_c, ang_c, gx_c, gy_c = compute_gradients(rgb)
        att_modes = generate_attention_modes(R, gx=gx_c, gy=gy_c, base_iters=7)

        masks = []
        qualities = []
        meta = []  # (mode_idx, tau)
        for mi, u in enumerate(att_modes):
            for tau in self.taus:
                m = generate_mask_from_u(u, R, float(tau))
                if m.sum() < 15:
                    continue
                q = mask_quality(mag_r, m)
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
        return R, mag_r, ang_r, gx_c, gy_c, att_modes, masks, qualities, meta

    def train(self, X_train, Y_train, epochs=20, lr=0.03, batch_size=32, verbose=True):
        """
        Training with feature caching. Mask selection uses multi-hypothesis search (top quality).
        """
        n = len(X_train)
        rng = np.random.RandomState(42)

        if verbose:
            print("  Training MDL prior (rank-space)...")
        # Train priors on rank-transformed images for noise/camouflage robustness
        X_rank = np.zeros((n, 28*28), dtype=np.float32)
        for i in range(n):
            rgb = as_image(X_train[i])
            Y, _, _ = rgb_to_yuv(rgb)
            X_rank[i] = rank_transform(Y).reshape(-1)
        self.mdl_prior.train(X_rank, Y_train)
        self.sketch_prior.train(X_rank, Y_train)

        if verbose:
            print("  Extracting features (cached, best hypothesis)...")

        all_features = np.zeros((n, self.feature_dim), dtype=np.float32)

        for i in range(n):
            img = as_image(X_train[i])
            R, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses(img)
            best = int(np.argmax(qualities))
            feats = extract_all_features_batch(img, masks[best:best+1], self.gabor_bank)[0]
            all_features[i] = feats

        self.feat_mean = all_features.mean(0)
        self.feat_std = all_features.std(0) + 1e-8
        Xn = (all_features - self.feat_mean) / self.feat_std

        # Train independent priors on normalized subspaces
        self.gabor_prior.train(Xn[:, self.slice_gabor], Y_train)
        self.contour_prior.train(Xn[:, self.slice_contour], Y_train)

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
        img = as_image(img)
        R, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses(img)

        # Flow–prune: keep top hypotheses by quality
        order = np.argsort(-qualities)
        keep = order[:min(self.keep_top, len(order))]
        masks_k = masks[keep]
        qual_k = qualities[keep]

        # Full features in batch
        feats = extract_all_features_batch(img, masks_k, self.gabor_bank)
        if self.feat_mean is not None:
            feats = (feats - self.feat_mean) / self.feat_std

        # Branch 1: classifier (full feature vector)
        p_cls = self.classifier.forward(feats)  # (H,10)

        # Shared flat for priors (masked rank)
        X_flat = (R[None, :, :] * masks_k).reshape(masks_k.shape[0], -1).astype(np.float32)

        # Branch 2: MDL/PCA prior on masked rank images
        mdl_logits = self.mdl_prior.get_logits_batch(X_flat)
        p_mdl = scipy_softmax(mdl_logits * self.mdl_temp, axis=1)

        # Branch 3: Hadamard sketch prior (masked rank)
        sk_logits = self.sketch_prior.get_logits_batch(X_flat)
        p_skw = scipy_softmax(sk_logits * self.sketch_temp, axis=1)

        # Branch 4: Gabor-energy mean prior (normalized gabor subspace)
        p_gbr = self.gabor_prior.get_probs_batch(feats[:, self.slice_gabor])

        # Branch 5: Contour mean prior (normalized contour subspace)
        p_cnt = self.contour_prior.get_probs_batch(feats[:, self.slice_contour])

        # Branch weights by entropy (lower entropy => higher weight)
        def entropy(p):
            p = np.clip(p, 1e-10, 1.0)
            return -np.sum(p * np.log(p), axis=1)

        H_cls = entropy(p_cls)
        H_mdl = entropy(p_mdl)
        H_skw = entropy(p_skw)
        H_gbr = entropy(p_gbr)
        H_cnt = entropy(p_cnt)

        w_cls = 1.0 / (H_cls + 0.6)
        w_mdl = 1.0 / (H_mdl + 0.6)
        w_skw = 1.0 / (H_skw + 0.6)
        w_gbr = 1.0 / (H_gbr + 0.6)
        w_cnt = 1.0 / (H_cnt + 0.6)

        w_sum = w_cls + w_mdl + w_skw + w_gbr + w_cnt
        w_cls /= w_sum; w_mdl /= w_sum; w_skw /= w_sum; w_gbr /= w_sum; w_cnt /= w_sum

        # Fuse: product-of-experts with weights (log domain)
        logp = (
            w_cls[:, None] * np.log(np.clip(p_cls, 1e-10, 1.0)) +
            w_mdl[:, None] * np.log(np.clip(p_mdl, 1e-10, 1.0)) +
            w_skw[:, None] * np.log(np.clip(p_skw, 1e-10, 1.0)) +
            w_gbr[:, None] * np.log(np.clip(p_gbr, 1e-10, 1.0)) +
            w_cnt[:, None] * np.log(np.clip(p_cnt, 1e-10, 1.0))
        )
        fused = np.exp(logp - logp.max(axis=1, keepdims=True))
        fused = fused / (fused.sum(axis=1, keepdims=True) + 1e-10)

        # Disagreement: JS divergence among branches
        P_stack = np.stack([p_cls, p_mdl, p_skw, p_gbr, p_cnt], axis=1)  # (H,5,10)
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

        # Spin / commutator defect (Ω∘D vs D∘Ω) + dual-lock stability (7/19) for kept hypotheses
        spin = np.zeros_like(js, dtype=np.float32)
        lock19 = np.zeros_like(js, dtype=np.float32)
        lock7 = np.zeros_like(js, dtype=np.float32)
        legal = np.zeros_like(js, dtype=np.float32)
        pot = np.zeros_like(js, dtype=np.float32)

        Htot = max(1, len(meta))
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

            # Spin = commutator defect in mask space
            spin[i] = 1.0 - iou(m_om, m_mo)

            # Dual-lock invariants (7 completion, 19 verifier): stability of small integer invariants under commutator
            inv_b = np.array(mask_invariants(m_base), dtype=np.int32)
            inv_om = np.array(mask_invariants(m_om), dtype=np.int32)
            inv_mo = np.array(mask_invariants(m_mo), dtype=np.int32)

            r19_b = inv_b % 19
            r19_om = inv_om % 19
            r19_mo = inv_mo % 19
            r7_b = inv_b % 7
            r7_om = inv_om % 7
            r7_mo = inv_mo % 7

            # count residue changes (normalized)
            lock19[i] = (np.sum(r19_b != r19_om) + np.sum(r19_b != r19_mo)) / float(inv_b.size * 2)
            lock7[i] = (np.sum(r7_b != r7_om) + np.sum(r7_b != r7_mo)) / float(inv_b.size * 2)

            # ±7 mod 19 legality tie-break (very small effect)
            key = int(inv_b[0] + 2*inv_b[1] + 5*inv_b[2] + 3*inv_b[3] + 11*inv_b[4])
            legal[i] = 0.0 if (key % 19) in (7, 12) else 1.0

            # 17/103 hypothesis landscape prior (tiny): periodic preference on hypothesis index
            phi = (2.0 * np.pi) * (float(orig_idx) / float(Htot))
            pot[i] = np.cos(17.0 * phi) + 0.8 * np.cos(103.0 * phi)

        # Energy: NLL + disagreement + complexity + spin + dual-lock stability + tiny landscape prior
        energy = (self.w_nll * nll +
                  self.w_js * js +
                  self.w_cmp * comp +
                  self.w_spin * spin +
                  self.w_lock19 * lock19 +
                  self.w_lock7 * lock7 +
                  self.w_legal * legal +
                  self.w_potential * pot)


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
            preds[i] = self.forward(as_image(X[i]))[0]
        return preds

    def evaluate(self, X_test, Y_test, verbose=True):
        correct = 0
        n = len(X_test)
        for i in range(n):
            pred, _, _ = self.forward(as_image(X_test[i]))
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
        # priors are stored templates/bases (approx count)
        mdl = 10 * 784 + 10 * 784 * int(getattr(self.mdl_prior, 'pca_rank', 10))
        sk = 10 * int(getattr(self.sketch_prior, 'out_dim', 192))
        gp = 10 * int(getattr(self, 'gabor_dim', 0))
        cp = 10 * int(getattr(self, 'contour_dim', 0))
        # log-gabor filters are fixed (not learned) but count as precomputed params
        gb = int(np.prod(self.gabor_bank.filters.shape))
        return int(clf + mdl + sk + gp + cp + gb)

class PrimeTunnelScheduler:
    """
    Deterministic prime-tunnel scheduler (braiders → lock bursts → braiders).
    - Maintains a small prime register bank U (mod p) per inference call.
    - Generates config knobs (taus, mode order, morphology) from U.
    - Produces step candidates R that are predictable by valuation (factors).
    This is the explicit "tunneling as emergence" controller.
    """
    def __init__(self, primes=(5, 7, 11, 13, 19)):
        self.primes = tuple(int(p) for p in primes)
        # "Braiders": steps with no factors in the prime set (mostly mixing, no freezes)
        self.braiders = (2, 4, 8, 16, 32)
        # "Lock bursts": strong steps with meaningful valuations (freezes/constraints)
        # 65 = 5*13 (threshold+mode), 133 = 7*19 (dual-lock), 385 = 5*7*11 (triple lock)
        self.locks = (65, 133, 385)

    def init_registers(self, seed_int: int):
        U = {}
        for p in self.primes:
            U[p] = int(seed_int % p)
        return U

    def apply_step(self, U, R: int):
        R = int(R)
        U2 = {}
        for p in self.primes:
            U2[p] = int((U[p] + (R % p)) % p)
        return U2

    def choose_braider(self, U):
        # deterministic pick keyed by 11 and 13 channels
        idx = (U[11] + 2 * U[13]) % len(self.braiders)
        return int(self.braiders[idx])

    def choose_lock(self, U, prefer_dual_lock: bool = True):
        if prefer_dual_lock:
            return int(self.locks[1])  # 133 = 7*19
        # Otherwise choose based on 5/13 phase
        idx = (U[5] + U[13]) % len(self.locks)
        return int(self.locks[idx])

    def config_from_registers(self, U, base_taus, mode_count=6, keep_top_base=12):
        """
        Map prime registers → hypothesis generation knobs.
        - 5: threshold shift
        - 7: threshold scale + morphology strength
        - 11: keep_top perturbation
        - 13: mode rotation
        - 19: "manifestation" toggle (include aggressive mode ordering)
        """
        u5, u7, u11, u13, u19 = U[5], U[7], U[11], U[13], U[19]

        # Threshold shift/scale (small, safe)
        tau_shift = (u5 - 2) * 0.015  # ~[-0.03..0.03]
        tau_scale = 1.0 + (u7 - 3) * 0.03  # ~[0.91..1.09]

        base = np.array(base_taus, dtype=np.float32)
        center = 0.525
        taus = center + (base - center) * tau_scale + tau_shift
        taus = np.clip(taus, 0.12, 0.92).tolist()

        # Morphology strength: 0..2
        morph_level = int(u7 % 3)
        if morph_level == 0:
            open_k, close_k = 2, 2
        elif morph_level == 1:
            open_k, close_k = 3, 3
        else:
            open_k, close_k = 2, 3

        # Mode order rotation
        rot = int(u13 % mode_count)
        mode_order = [(rot + i) % mode_count for i in range(mode_count)]

        # "Manifestation" toggle: if odd, reverse order (forces different basin exploration)
        manifest = bool(u19 % 2)
        if manifest:
            mode_order = list(reversed(mode_order))

        # keep_top small perturbation (bounded)
        keep_top = int(np.clip(keep_top_base + (u11 % 5) - 2, 8, 20))
        preselect = int(np.clip(3 * keep_top, 18, 60))

        return {
            "taus": taus,
            "mode_order": mode_order,
            "open_k": open_k,
            "close_k": close_k,
            "keep_top": keep_top,
            "preselect": preselect,
            "manifest": manifest,
            "U": U,
        }


class AthenaNeuralNetworkV81Q(AthenaNeuralNetworkV80Q):
    """
    v81Q = v80Q + explicit prime tunnel scheduler that actively changes the hypothesis set.

    Key difference:
    - When uncertain/oscillating, it runs extra "tunnel rounds":
        base → braider (mix) → lock burst (dual-lock)
      Each round generates a *different hypothesis bank* (taus, mode order, morphology),
      then we choose the best sealed collapse.
    """
    def __init__(self):
        super().__init__()
        # Base taus kept as canonical seed; scheduler will warp around it deterministically.
        self.base_taus = np.linspace(0.25, 0.80, 10).tolist()
        self.scheduler = PrimeTunnelScheduler(primes=(5, 7, 11, 13, 19))
        # Collapse thresholds
        self.conf_fast = 0.72
        self.amp_fast = 0.62
        self.max_rounds = 3  # base + braider + lock

    def _image_digest(self, R: np.ndarray, mag: np.ndarray, rgb: np.ndarray) -> int:
        # Deterministic integer digest for per-image prime register initialization.
        Y, U, V = rgb_to_yuv(rgb)
        C = chroma_mag(U, V)
        a = int(np.sum(np.floor(R * 255.0)))
        b = int(np.sum(np.floor(np.clip(mag, 0, 1) * 127.0)))
        c = int(np.sum(np.floor(np.clip(C, 0, 1) * 127.0)))
        return (a + 131 * b + 977 * c) & 0x7FFFFFFF

    def _postprocess_mask(self, m: np.ndarray) -> np.ndarray:
        # Keep largest component + fill holes (deterministic).
        labeled, num = ndimage.label(m)
        if num > 0:
            sizes = ndimage.sum(m, labeled, range(1, num + 1))
            largest = int(np.argmax(sizes) + 1)
            m = (labeled == largest).astype(np.float32)
        m = ndimage.binary_fill_holes(m).astype(np.float32)
        return m

    def _generate_hypotheses_config(self, img, config):
        """
        Vectorized candidate generation:
        - batch thresholding per mode
        - batch morphology for all taus in a mode
        - cheap quality scoring for all candidates
        - postprocess only top 'preselect'
        """
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        R = rank_transform(Y)
        mag_r, ang_r, _, _ = compute_gradients(R)
        _, _, gx_c, gy_c = compute_gradients(rgb)

        att_modes = generate_attention_modes(R, gx=gx_c, gy=gy_c, base_iters=7)
        mode_order = config["mode_order"]
        taus = np.array(config["taus"], dtype=np.float32)
        open_k = int(config["open_k"]); close_k = int(config["close_k"])
        preselect = int(config["preselect"])

        all_masks = []
        all_qual = []
        all_meta = []

        # Batch structures
        st_open = np.ones((1, open_k, open_k), dtype=np.uint8)
        st_close = np.ones((1, close_k, close_k), dtype=np.uint8)
        st_erode = np.ones((1, 3, 3), dtype=np.uint8)

        Rf = R[None, :, :]  # (1,28,28)
        magf = mag_r[None, :, :]

        for mi in mode_order:
            u = att_modes[mi]
            uf = u[None, :, :]
            # raw masks: (K,28,28)
            raw = (uf >= taus[:, None, None]) | (Rf >= (taus[:, None, None] + 0.12))
            raw = raw.astype(np.uint8)

            # batch opening + closing
            raw = ndimage.binary_opening(raw, structure=st_open).astype(np.uint8)
            raw = ndimage.binary_closing(raw, structure=st_close).astype(np.uint8)

            # area filter
            areas = raw.sum(axis=(1, 2)).astype(np.float32)
            valid = areas >= 15.0
            if not np.any(valid):
                continue
            raw = raw[valid]
            areas = areas[valid]
            taus_v = taus[valid]

            # perimeter proxy (batched erosion)
            er = ndimage.binary_erosion(raw, structure=st_erode).astype(np.uint8)
            boundary = (raw - er).astype(np.float32)
            per = boundary.sum(axis=(1, 2)).astype(np.float32) + 1e-8

            edge_mass = (magf * raw.astype(np.float32)).sum(axis=(1, 2)) / (areas + 1e-8)
            comp = areas / (per * per)
            frac = areas / 784.0
            area_pen = np.abs(frac - 0.18)

            q = edge_mass + 1.5 * comp - 0.8 * area_pen

            all_masks.append(raw.astype(np.float32))
            all_qual.append(q.astype(np.float32))
            for t in taus_v:
                all_meta.append((int(mi), float(t)))

        if len(all_masks) == 0:
            m = (R > 0.3).astype(np.float32)
            return R, mag_r, ang_r, gx_c, gy_c, att_modes, m[None, :, :], np.array([0.0], np.float32), [(0, 0.3)]

        masks = np.concatenate(all_masks, axis=0)  # (Hc,28,28)
        qual = np.concatenate(all_qual, axis=0)    # (Hc,)

        # preselect top candidates before expensive postprocessing
        pre = int(min(preselect, masks.shape[0]))
        idx = np.argsort(-qual)[:pre]

        masks_pp = []
        qual_pp = []
        meta_pp = []
        for j in idx:
            m = masks[j]
            m = self._postprocess_mask(m)
            if m.sum() < 15:
                continue
            q2 = mask_quality(mag_r, m)
            masks_pp.append(m)
            qual_pp.append(q2)
            meta_pp.append(all_meta[j])

        if len(masks_pp) == 0:
            m = (R > 0.3).astype(np.float32)
            return R, mag_r, ang_r, gx_c, gy_c, att_modes, m[None, :, :], np.array([0.0], np.float32), [(0, 0.3)]

        masks_pp = np.stack(masks_pp, axis=0).astype(np.float32)
        qual_pp = np.array(qual_pp, dtype=np.float32)
        return R, mag_r, ang_r, gx_c, gy_c, att_modes, masks_pp, qual_pp, meta_pp

    def _infer_with_config(self, img, config):
        """
        One inference round with a given hypothesis config.
        Returns (pred, probs, conf, debug).
        """
        img = as_image(img)
        R, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses_config(img, config)

        keep_top = int(config["keep_top"])
        order = np.argsort(-qualities)
        keep = order[:min(keep_top, len(order))]
        masks_k = masks[keep]
        meta_k = [meta[i] for i in keep]

        feats = extract_all_features_batch(img, masks_k, self.gabor_bank)
        if self.feat_mean is not None:
            feats = (feats - self.feat_mean) / self.feat_std

        p_cls = self.classifier.forward(feats)

        X_flat = (R[None, :, :] * masks_k).reshape(masks_k.shape[0], -1).astype(np.float32)
        mdl_logits = self.mdl_prior.get_logits_batch(X_flat)
        p_mdl = scipy_softmax(mdl_logits * self.mdl_temp, axis=1)
        sk_logits = self.sketch_prior.get_logits_batch(X_flat)
        p_skw = scipy_softmax(sk_logits * self.sketch_temp, axis=1)
        p_gbr = self.gabor_prior.get_probs_batch(feats[:, self.slice_gabor])
        p_cnt = self.contour_prior.get_probs_batch(feats[:, self.slice_contour])

        def entropy(p):
            p = np.clip(p, 1e-10, 1.0)
            return -np.sum(p * np.log(p), axis=1)

        H_cls = entropy(p_cls); H_mdl = entropy(p_mdl); H_skw = entropy(p_skw); H_gbr = entropy(p_gbr); H_cnt = entropy(p_cnt)
        w_cls = 1.0 / (H_cls + 0.6); w_mdl = 1.0 / (H_mdl + 0.6); w_skw = 1.0 / (H_skw + 0.6); w_gbr = 1.0 / (H_gbr + 0.6); w_cnt = 1.0 / (H_cnt + 0.6)
        w_sum = w_cls + w_mdl + w_skw + w_gbr + w_cnt
        w_cls /= w_sum; w_mdl /= w_sum; w_skw /= w_sum; w_gbr /= w_sum; w_cnt /= w_sum

        logp = (
            w_cls[:, None] * np.log(np.clip(p_cls, 1e-10, 1.0)) +
            w_mdl[:, None] * np.log(np.clip(p_mdl, 1e-10, 1.0)) +
            w_skw[:, None] * np.log(np.clip(p_skw, 1e-10, 1.0)) +
            w_gbr[:, None] * np.log(np.clip(p_gbr, 1e-10, 1.0)) +
            w_cnt[:, None] * np.log(np.clip(p_cnt, 1e-10, 1.0))
        )
        fused = np.exp(logp - logp.max(axis=1, keepdims=True))
        fused = fused / (fused.sum(axis=1, keepdims=True) + 1e-10)

        P_stack = np.stack([p_cls, p_mdl, p_skw, p_gbr, p_cnt], axis=1)
        js = js_divergence(P_stack)

        comp = np.zeros((masks_k.shape[0],), dtype=np.float32)
        for i in range(masks_k.shape[0]):
            m = masks_k[i]
            area = m.sum() / 784.0
            er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.float32)
            boundary = m - er
            per = boundary.sum() / 784.0
            comp[i] = abs(area - 0.18) + 0.8 * per

        top = fused.max(axis=1)
        nll = -np.log(np.clip(top, 1e-10, 1.0))

        # Spin/dual-lock penalties (reuse v80 logic but on this round's kept hypotheses)
        spin = np.zeros_like(js, dtype=np.float32)
        lock19 = np.zeros_like(js, dtype=np.float32)
        lock7 = np.zeros_like(js, dtype=np.float32)
        legal = np.zeros_like(js, dtype=np.float32)
        pot = np.zeros_like(js, dtype=np.float32)

        Htot = max(1, len(meta))
        # Need original attention modes list for commutator
        rgb = ensure_rgb(img)
        _, _, gx_c, gy_c = compute_gradients(rgb)
        att_modes_all = generate_attention_modes(R, gx=gx_c, gy=gy_c, base_iters=7)

        for i, (mi, tau) in enumerate(meta_k):
            u_mode = att_modes_all[int(mi)]

            u_om = anisotropic_diffuse(u_mode, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_om = generate_mask_from_u(u_om, R, float(tau))

            m_base = masks_k[i]
            u_m = anisotropic_diffuse(m_base, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_mo = (u_m > 0.5).astype(np.float32)

            spin[i] = 1.0 - iou(m_om, m_mo)

            inv_b = np.array(mask_invariants(m_base), dtype=np.int32)
            inv_om = np.array(mask_invariants(m_om), dtype=np.int32)
            inv_mo = np.array(mask_invariants(m_mo), dtype=np.int32)

            lock19[i] = (np.sum((inv_b % 19) != (inv_om % 19)) + np.sum((inv_b % 19) != (inv_mo % 19))) / float(inv_b.size * 2)
            lock7[i]  = (np.sum((inv_b % 7)  != (inv_om % 7))  + np.sum((inv_b % 7)  != (inv_mo % 7)))  / float(inv_b.size * 2)

            key = int(inv_b[0] + 2*inv_b[1] + 5*inv_b[2] + 3*inv_b[3] + 11*inv_b[4])
            legal[i] = 0.0 if (key % 19) in (7, 12) else 1.0

            phi = (2.0 * np.pi) * (float(i) / float(max(1, masks_k.shape[0])))
            pot[i] = np.cos(17.0 * phi) + 0.8 * np.cos(103.0 * phi)

        energy = (self.w_nll * nll +
                  self.w_js * js +
                  self.w_cmp * comp +
                  self.w_spin * spin +
                  self.w_lock19 * lock19 +
                  self.w_lock7 * lock7 +
                  self.w_legal * legal +
                  self.w_potential * pot)

        amps = scipy_softmax(-energy * 2.5)
        final = (amps[:, None] * fused).sum(axis=0)
        final = final / (final.sum() + 1e-10)

        confidence = float(final.max() * amps.max())
        pred = int(final.argmax())

        debug = {
            "confidence": confidence,
            "amp_max": float(amps.max()),
            "js_mean": float(js.mean()),
            "spin_mean": float(spin.mean()),
            "lock19_mean": float(lock19.mean()),
            "best_meta": meta_k[int(np.argmax(amps))],
            "best_energy": float(energy.min()),
            "U": config.get("U", None),
        }
        return pred, final, confidence, debug

    def forward(self, img: np.ndarray):
        """
        Multi-round inference: base → braider → lock burst (if needed).
        Each round *regenerates hypotheses* via prime-tuned config (tunneling).
        """
        img = as_image(img)
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        R = rank_transform(Y)
        mag, _, _, _ = compute_gradients(R)

        seed = self._image_digest(R, mag, rgb)
        U0 = self.scheduler.init_registers(seed)

        # Round 0 (base config)
        cfg0 = self.scheduler.config_from_registers(U0, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
        r0 = self._infer_with_config(img, cfg0)

        pred0, prob0, conf0, dbg0 = r0
        if conf0 >= self.conf_fast and dbg0["amp_max"] >= self.amp_fast:
            return pred0, prob0, conf0

        # Round 1 (braider: mild tunnel)
        Rb = self.scheduler.choose_braider(U0)
        U1 = self.scheduler.apply_step(U0, Rb)
        cfg1 = self.scheduler.config_from_registers(U1, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
        r1 = self._infer_with_config(img, cfg1)

        pred1, prob1, conf1, dbg1 = r1
        best = r0 if conf0 >= conf1 else r1

        # If braider improved enough, stop
        if max(conf0, conf1) >= self.conf_fast and max(dbg0["amp_max"], dbg1["amp_max"]) >= self.amp_fast:
            pred, prob, conf, _ = best
            return pred, prob, conf

        # Decide if we need a lock burst
        oscillate = (dbg0["best_meta"] == dbg1["best_meta"]) and (abs(conf1 - conf0) < 0.03)
        prefer_dual = (dbg0["lock19_mean"] > 0.22) or (dbg1["lock19_mean"] > 0.22) or oscillate or (dbg0["js_mean"] > 0.28)

        Rlock = self.scheduler.choose_lock(U1, prefer_dual_lock=prefer_dual)
        U2 = self.scheduler.apply_step(U1, Rlock)
        cfg2 = self.scheduler.config_from_registers(U2, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
        r2 = self._infer_with_config(img, cfg2)

        pred2, prob2, conf2, dbg2 = r2
        # pick best by confidence; tie-break by best_energy
        cands = [r0, r1, r2]
        cands_dbg = [dbg0, dbg1, dbg2]
        best_idx = int(np.argmax([c[2] for c in cands]))
        # if close, use energy
        if sorted([c[2] for c in cands], reverse=True)[0] - sorted([c[2] for c in cands], reverse=True)[1] < 0.02:
            best_idx = int(np.argmin([d["best_energy"] for d in cands_dbg]))

        pred, prob, conf, _ = cands[best_idx]
        return pred, prob, conf

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

def _center_crop_pad(img, target=28):
    if img.ndim == 2:
        h, w = img.shape
        if h > target:
            s = (h - target) // 2
            img = img[s:s+target, s:s+target]
        elif h < target:
            pad = (target - h) // 2
            img = np.pad(img, ((pad, target-h-pad), (pad, target-w-pad)), mode='constant')
        return img[:target, :target]
    # 3D: (H,W,C)
    h, w, c = img.shape
    if h > target:
        s = (h - target) // 2
        img = img[s:s+target, s:s+target, :]
    elif h < target:
        pad = (target - h) // 2
        img = np.pad(img, ((pad, target-h-pad), (pad, target-w-pad), (0,0)), mode='constant')
    return img[:target, :target, :]

def aug_geometric(img, rng):
    angle = rng.uniform(-25, 25)
    scale = rng.uniform(0.9, 1.1)
    if img.ndim == 3:
        img = ndimage.rotate(img, angle, reshape=False, mode='constant', axes=(0,1))
        img = ndimage.zoom(img, (scale, scale, 1.0), mode='constant')
    else:
        img = ndimage.rotate(img, angle, reshape=False, mode='constant')
        img = ndimage.zoom(img, scale, mode='constant')
    img = _center_crop_pad(img, 28)
    return np.clip(img, 0, 1)

def aug_adversarial(img, rng):
    noise = rng.randn(*img.shape).astype(np.float32) * 0.25
    return np.clip(img + noise, 0, 1)

def aug_cluttered(img, rng):
    out = img.copy()
    for _ in range(rng.randint(3, 7)):
        y, x = rng.randint(0, 24), rng.randint(0, 24)
        s = rng.randint(2, 4)
        if out.ndim == 2:
            out[y:y+s, x:x+s] = rng.uniform(0.1, 0.3)
        else:
            out[y:y+s, x:x+s, :] = rng.uniform(0.1, 0.3, size=(1,1,3))
    return np.clip(out, 0, 1)

def aug_camouflage(img, rng):
    """Grayscale camouflage (legacy)."""
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

def colorize_digit(gray: np.ndarray, rng) -> np.ndarray:
    """Turn grayscale digit into RGB with randomized low-contrast chroma separation."""
    mask = gray > 0.3
    # background chroma texture
    freq = rng.uniform(0.25, 0.55)
    y, x = np.ogrid[:28, :28]
    base = 0.45 + 0.15 * np.sin(freq * x + rng.uniform(0, 2*np.pi)) * np.cos(freq * y + rng.uniform(0, 2*np.pi))
    base = base.astype(np.float32)
    # random background color near base
    bg = np.stack([base, base, base], axis=2)
    bg += rng.randn(28, 28, 3).astype(np.float32) * 0.05
    bg = np.clip(bg, 0, 1)

    # foreground color: similar luminance, shifted chroma
    delta = rng.uniform(0.04, 0.10, size=(3,)).astype(np.float32)
    fg = np.clip(bg + delta[None,None,:], 0, 1)

    out = bg.copy()
    out[mask] = fg[mask]
    # add digit intensity as slight luminance boost
    out = np.clip(out + gray[:, :, None] * 0.10, 0, 1)
    return out

def aug_color_camouflage(gray, rng):
    """Color camouflage: background texture in RGB, digit differs mostly by chroma."""
    rgb = colorize_digit(gray, rng)
    # extra color texture per channel
    y, x = np.ogrid[:28, :28]
    for ch in range(3):
        freq = rng.uniform(0.25, 0.60)
        ph = rng.uniform(0, 2*np.pi)
        tex = 0.06 * np.sin(freq * x + ph) * np.cos(freq * y + ph * 0.7)
        rgb[..., ch] = np.clip(rgb[..., ch] + tex.astype(np.float32), 0, 1)
    return rgb

def generate_data(n, aug_fn, seed, color: bool = False):
    rng = np.random.RandomState(seed)
    dim = 784 * (3 if color else 1)
    X = np.zeros((n, dim), dtype=np.float32)
    Y = np.zeros((n, 10), dtype=np.float32)
    for i in range(n):
        d = rng.randint(0, 10)
        base = draw_digit(d)
        if color:
            img = aug_fn(base, rng)
            X[i] = img.reshape(-1)
        else:
            X[i] = aug_fn(base, rng).reshape(-1)
        Y[i, d] = 1
    return X, Y

def run_benchmark():
    import time
    benchmarks = [
        ('GEOMETRIC', aug_geometric, False),
        ('ADVERSARIAL', aug_adversarial, False),
        ('CLUTTERED', aug_cluttered, False),
        ('CAMOUFLAGE', aug_camouflage, False),
        ('COLOR_CAMOUFLAGE', aug_color_camouflage, True),
    ]

    results = {}
    for name, aug_fn, is_color in benchmarks:
        print(f"\n{'='*50}\n{name.center(50)}\n{'='*50}")
        X_train, Y_train = generate_data(1000, aug_fn, 42, color=is_color)
        X_test, Y_test = generate_data(250, aug_fn, 142, color=is_color)

        model = AthenaNeuralNetworkV83Q()
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
        print(f"{k:<15}: {v*100:5.1f}%")
    print(f"AVG            : {np.mean(list(results.values()))*100:5.1f}%")
    return results


# =============================================================================
# PRIMESEAL TIE-BREAKER (v82Q): modular parity + micro-perturbation stability
# =============================================================================

def _sig_vector_for_primeseal(mask: np.ndarray) -> np.ndarray:
    """
    Build a compact integer signature for a mask. Pure NumPy/SciPy.
    Used for PrimeSeal-style disambiguation: stable hypotheses preserve these signatures
    under micro-perturbations (shift/blur) and commutator variants (Ω∘D, D∘Ω).
    """
    inv = np.array(mask_invariants(mask), dtype=np.int32)               # 5
    topo = extract_topology(mask).astype(np.float32)                    # 12 floats
    topo_i = np.round(topo * 100.0).astype(np.int32)                    # 12 ints
    fd = contour_fourier_descriptor(mask, k=6).astype(np.float32)       # 12 floats
    fd_i = np.round(fd * 50.0).astype(np.int32)                         # 12 ints
    ss = skeleton_stats(mask).astype(np.float32)                        # 5 floats
    # endpoints/junctions/length are already integer-ish; width stats scaled
    ss_i = np.array([
        int(round(ss[0])),
        int(round(ss[1])),
        int(round(ss[2])),
        int(round(ss[3] * 10.0)),
        int(round(ss[4] * 10.0)),
    ], dtype=np.int32)
    return np.concatenate([inv, topo_i, fd_i, ss_i], axis=0).astype(np.int32)

def _parity_vec(sig: np.ndarray, p: int, r: int = 4) -> np.ndarray:
    """
    Deterministic parity checks mod p for signature vector.
    Uses simple deterministic coefficient schedule (no RNG, reproducible).
    """
    p = int(p)
    sigm = np.mod(sig.astype(np.int64), p)
    n = sigm.size
    idx = (np.arange(n, dtype=np.int64) + 1)
    out = np.zeros((r,), dtype=np.int64)
    for j in range(r):
        coeff = (idx * (j + 1) * (p + 1) + 3) % p
        coeff[coeff == 0] = 1
        out[j] = int(np.sum(coeff * sigm) % p)
    return out.astype(np.int64)

def _shift_mask(m: np.ndarray, dy: int, dx: int) -> np.ndarray:
    return ndimage.shift(m.astype(np.float32), shift=(dy, dx), order=0, mode='constant', cval=0.0).astype(np.float32)

def _blur_mask(m: np.ndarray, sigma: float = 0.8, thr: float = 0.35) -> np.ndarray:
    b = ndimage.gaussian_filter(m.astype(np.float32), sigma=sigma)
    return (b > thr).astype(np.float32)

def _primeseal_stability_score(m_base: np.ndarray,
                              m_om: np.ndarray,
                              m_mo: np.ndarray,
                              primes=(5, 7, 11, 13, 19),
                              r_checks: int = 4) -> float:
    """
    Returns a stability score in [0,1] where 0 is best.
    Compare parity vectors of a base signature against variants:
      - Ω∘D mask (m_om)
      - D∘Ω mask (m_mo)
      - 1px shifts (x/y)
      - blurred-threshold variant
    Weighted so p=19 has strongest influence (verifier).
    """
    variants = [
        m_base,
        m_om,
        m_mo,
        _shift_mask(m_base, 0, 1),
        _shift_mask(m_base, 1, 0),
        _blur_mask(m_base),
    ]
    sigs = [_sig_vector_for_primeseal(v) for v in variants]
    sig0 = sigs[0]

    weights = {5: 1.0, 7: 1.6, 11: 1.3, 13: 1.2, 19: 2.6}
    total = 0.0
    denom = 0.0
    for p in primes:
        w = weights.get(int(p), 1.0)
        base_par = _parity_vec(sig0, p=int(p), r=r_checks)
        mism = 0
        for s in sigs[1:]:
            par = _parity_vec(s, p=int(p), r=r_checks)
            mism += int(np.sum(par != base_par))
        total += w * float(mism)
        denom += w * float(r_checks * (len(sigs) - 1))

    score = total / (denom + 1e-10)

    # add a tiny legality penalty on the base invariants key (±7 mod 19)
    inv = sig0[:5].astype(np.int64)
    key = int(inv[0] + 2*inv[1] + 5*inv[2] + 3*inv[3] + 11*inv[4])
    if (key % 19) not in (7, 12):
        score += 0.03

    return float(np.clip(score, 0.0, 1.0))

# =============================================================================
# ATHENA v82Q: v81 + explicit PrimeSeal tie-break on top hypotheses
# =============================================================================

class AthenaNeuralNetworkV82Q(AthenaNeuralNetworkV81Q):
    """
    v82Q = v81Q + explicit PrimeSeal-style tie-breaker on ambiguous collapses.

    - Uses modular parity over a compact signature vector (mask invariants + topology + contour + skeleton),
      and checks stability under micro-perturbations and commutator variants.
    - When mixture collapse is ambiguous (low amp margin / high disagreement), it selects the most stable
      hypothesis and collapses to its fused distribution (rather than soft-mixing).
    """
    def __init__(self):
        super().__init__()
        self.seal_topM = 5          # candidates from amplitude peak
        self.seal_checks = 4        # parity checks per prime
        self.seal_primes = (5, 7, 11, 13, 19)
        self.seal_trigger_js = 0.30
        self.seal_trigger_margin = 0.10

    def _infer_with_config(self, img, config):
        # Copy of v81 core with the PrimeSeal selection inserted at the end.
        img = as_image(img)
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        R = rank_transform(Y)

        Rm, mag, ang, gx, gy, att_modes, masks, qualities, meta = self._generate_hypotheses_config(img, config)

        keep_top = int(config["keep_top"])
        order = np.argsort(-qualities)
        keep = order[:min(keep_top, len(order))]
        masks_k = masks[keep]
        meta_k = [meta[i] for i in keep]

        feats = extract_all_features_batch(img, masks_k, self.gabor_bank)
        if self.feat_mean is not None:
            feats = (feats - self.feat_mean) / self.feat_std

        p_cls = self.classifier.forward(feats)

        X_flat = (R[None, :, :] * masks_k).reshape(masks_k.shape[0], -1).astype(np.float32)
        mdl_logits = self.mdl_prior.get_logits_batch(X_flat)
        p_mdl = scipy_softmax(mdl_logits * self.mdl_temp, axis=1)
        sk_logits = self.sketch_prior.get_logits_batch(X_flat)
        p_skw = scipy_softmax(sk_logits * self.sketch_temp, axis=1)
        p_gbr = self.gabor_prior.get_probs_batch(feats[:, self.slice_gabor])
        p_cnt = self.contour_prior.get_probs_batch(feats[:, self.slice_contour])

        def entropy(p):
            p = np.clip(p, 1e-10, 1.0)
            return -np.sum(p * np.log(p), axis=1)

        H_cls = entropy(p_cls); H_mdl = entropy(p_mdl); H_skw = entropy(p_skw); H_gbr = entropy(p_gbr); H_cnt = entropy(p_cnt)
        w_cls = 1.0 / (H_cls + 0.6); w_mdl = 1.0 / (H_mdl + 0.6); w_skw = 1.0 / (H_skw + 0.6); w_gbr = 1.0 / (H_gbr + 0.6); w_cnt = 1.0 / (H_cnt + 0.6)
        w_sum = w_cls + w_mdl + w_skw + w_gbr + w_cnt
        w_cls /= w_sum; w_mdl /= w_sum; w_skw /= w_sum; w_gbr /= w_sum; w_cnt /= w_sum

        logp = (
            w_cls[:, None] * np.log(np.clip(p_cls, 1e-10, 1.0)) +
            w_mdl[:, None] * np.log(np.clip(p_mdl, 1e-10, 1.0)) +
            w_skw[:, None] * np.log(np.clip(p_skw, 1e-10, 1.0)) +
            w_gbr[:, None] * np.log(np.clip(p_gbr, 1e-10, 1.0)) +
            w_cnt[:, None] * np.log(np.clip(p_cnt, 1e-10, 1.0))
        )
        fused = np.exp(logp - logp.max(axis=1, keepdims=True))
        fused = fused / (fused.sum(axis=1, keepdims=True) + 1e-10)

        P_stack = np.stack([p_cls, p_mdl, p_skw, p_gbr, p_cnt], axis=1)
        js = js_divergence(P_stack)

        comp = np.zeros((masks_k.shape[0],), dtype=np.float32)
        for i in range(masks_k.shape[0]):
            m = masks_k[i]
            area = m.sum() / 784.0
            er = ndimage.binary_erosion(m, structure=np.ones((3,3))).astype(np.float32)
            boundary = m - er
            per = boundary.sum() / 784.0
            comp[i] = abs(area - 0.18) + 0.8 * per

        top = fused.max(axis=1)
        nll = -np.log(np.clip(top, 1e-10, 1.0))

        # Spin/dual-lock penalties + store commutator masks for PrimeSeal
        spin = np.zeros_like(js, dtype=np.float32)
        lock19 = np.zeros_like(js, dtype=np.float32)
        lock7 = np.zeros_like(js, dtype=np.float32)
        legal = np.zeros_like(js, dtype=np.float32)
        pot = np.zeros_like(js, dtype=np.float32)

        m_om_store = np.zeros_like(masks_k, dtype=np.float32)
        m_mo_store = np.zeros_like(masks_k, dtype=np.float32)

        _, _, gx_c, gy_c = compute_gradients(rgb)
        att_modes_all = generate_attention_modes(R, gx=gx_c, gy=gy_c, base_iters=7)

        for i, (mi, tau) in enumerate(meta_k):
            u_mode = att_modes_all[int(mi)]

            u_om = anisotropic_diffuse(u_mode, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_om = generate_mask_from_u(u_om, R, float(tau))

            m_base = masks_k[i]
            u_m = anisotropic_diffuse(m_base, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_mo = (u_m > 0.5).astype(np.float32)

            m_om_store[i] = m_om
            m_mo_store[i] = m_mo

            spin[i] = 1.0 - iou(m_om, m_mo)

            inv_b = np.array(mask_invariants(m_base), dtype=np.int32)
            inv_om = np.array(mask_invariants(m_om), dtype=np.int32)
            inv_mo = np.array(mask_invariants(m_mo), dtype=np.int32)

            lock19[i] = (np.sum((inv_b % 19) != (inv_om % 19)) + np.sum((inv_b % 19) != (inv_mo % 19))) / float(inv_b.size * 2)
            lock7[i]  = (np.sum((inv_b % 7)  != (inv_om % 7))  + np.sum((inv_b % 7)  != (inv_mo % 7)))  / float(inv_b.size * 2)

            key = int(inv_b[0] + 2*inv_b[1] + 5*inv_b[2] + 3*inv_b[3] + 11*inv_b[4])
            legal[i] = 0.0 if (key % 19) in (7, 12) else 1.0

            phi = (2.0 * np.pi) * (float(i) / float(max(1, masks_k.shape[0])))
            pot[i] = np.cos(17.0 * phi) + 0.8 * np.cos(103.0 * phi)

        energy = (self.w_nll * nll +
                  self.w_js * js +
                  self.w_cmp * comp +
                  self.w_spin * spin +
                  self.w_lock19 * lock19 +
                  self.w_lock7 * lock7 +
                  self.w_legal * legal +
                  self.w_potential * pot)

        amps = scipy_softmax(-energy * 2.5)
        final_mix = (amps[:, None] * fused).sum(axis=0)
        final_mix = final_mix / (final_mix.sum() + 1e-10)

        # PrimeSeal tie-break when ambiguous: collapse to most stable hypothesis
        amp_sorted = np.sort(amps)[::-1]
        amp_margin = float(amp_sorted[0] - (amp_sorted[1] if amp_sorted.size > 1 else 0.0))
        use_seal = (js.mean() > self.seal_trigger_js) or (amp_margin < self.seal_trigger_margin)

        chosen_idx = int(np.argmax(amps))
        seal_score = 0.0

        if use_seal and masks_k.shape[0] >= 2:
            M = int(min(self.seal_topM, masks_k.shape[0]))
            cand_idx = np.argsort(-amps)[:M]
            scores = []
            for j in cand_idx:
                sc = _primeseal_stability_score(
                    masks_k[j], m_om_store[j], m_mo_store[j],
                    primes=self.seal_primes, r_checks=self.seal_checks
                )
                # include small penalty from current energy (secondary)
                sc2 = sc + 0.02 * float((energy[j] - energy.min()) / (energy.ptp() + 1e-8))
                scores.append(sc2)
            scores = np.array(scores, dtype=np.float32)
            best_local = int(np.argmin(scores))
            chosen_idx = int(cand_idx[best_local])
            seal_score = float(scores[best_local])

        final = fused[chosen_idx] if use_seal else final_mix
        final = final / (final.sum() + 1e-10)

        confidence = float(final.max() * (amps[chosen_idx] if use_seal else amps.max()) * (1.0 - 0.35 * seal_score))
        confidence = float(np.clip(confidence, 0.0, 1.0))
        pred = int(final.argmax())

        debug = {
            "confidence": confidence,
            "amp_max": float(amps.max()),
            "amp_margin": amp_margin,
            "js_mean": float(js.mean()),
            "spin_mean": float(spin.mean()),
            "lock19_mean": float(lock19.mean()),
            "primeseal_used": bool(use_seal),
            "primeseal_choice": int(chosen_idx),
            "primeseal_score": float(seal_score),
            "best_meta": meta_k[int(chosen_idx)],
            "best_energy": float(energy.min()),
            "U": config.get("U", None),
        }
        return pred, final, confidence, debug






# =============================================================================
# ATHENA v83Q: PrimeSeal-guided lock selection (choose lock burst by predicted seal + tri-lock proxies)
# =============================================================================

class AthenaNeuralNetworkV83Q(AthenaNeuralNetworkV82Q):
    """
    v83Q = v82Q + PrimeSeal-guided lock selection.

    Instead of selecting lock burst via heuristic, we evaluate each lock candidate (65, 133, 385)
    using a cheap seal proxy computed on top hypotheses:
      - PrimeSeal stability score (modular parity + micro-variants) [expected parity stability]
      - spin (Ω∘D vs D∘Ω commutator IoU)                             [holonomy proxy]
      - lock19 / lock7 mismatch rates                               [verifier/completion proxies]
      - legality penalty (±7 mod 19)

    This is the "predictable tunneling" upgrade: tunnel choice is driven by expected sealing.
    """
    def __init__(self):
        super().__init__()
        self.lock_candidates = (65, 133, 385)
        # quick selection weights
        self.lock_w_seal = 1.00
        self.lock_w_spin = 0.35
        self.lock_w_19 = 0.50
        self.lock_w_7 = 0.25
        self.lock_w_legal = 0.10
        self.lock_topM = 3
        self.lock_quick_primes = (5, 7, 19)
        self.lock_quick_checks = 2

    def _lock_candidate_score(self, img, config):
        """Cheap, deterministic score for a lock candidate configuration."""
        img = as_image(img)
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        R = rank_transform(Y)

        # Generate postprocessed hypotheses with cheap quality scoring
        _, _, _, _, _, _, masks, qualities, meta = self._generate_hypotheses_config(img, config)
        if masks.shape[0] == 0:
            return 1e9, {"reason": "no_masks"}

        order = np.argsort(-qualities)
        top = order[:min(max(self.lock_topM, 3), len(order))]
        masks_k = masks[top]
        meta_k = [meta[i] for i in top]

        # Recompute attention modes for commutator variants
        _, _, gx_c, gy_c = compute_gradients(rgb)
        att_modes_all = generate_attention_modes(R, gx=gx_c, gy=gy_c, base_iters=7)

        spin_vals = []
        lock19_vals = []
        lock7_vals = []
        legal_vals = []
        seal_vals = []

        for i, (mi, tau) in enumerate(meta_k):
            u_mode = att_modes_all[int(mi)]
            u_om = anisotropic_diffuse(u_mode, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_om = generate_mask_from_u(u_om, R, float(tau))

            m_base = masks_k[i]
            u_m = anisotropic_diffuse(m_base, gx=gx_c, gy=gy_c, kappa=0.12, dt=0.18, steps=1, bias=None)
            m_mo = (u_m > 0.5).astype(np.float32)

            spin_vals.append(1.0 - iou(m_om, m_mo))

            inv_b = np.array(mask_invariants(m_base), dtype=np.int32)
            inv_om = np.array(mask_invariants(m_om), dtype=np.int32)
            inv_mo = np.array(mask_invariants(m_mo), dtype=np.int32)

            lock19_vals.append((np.sum((inv_b % 19) != (inv_om % 19)) + np.sum((inv_b % 19) != (inv_mo % 19))) / float(inv_b.size * 2))
            lock7_vals.append((np.sum((inv_b % 7) != (inv_om % 7)) + np.sum((inv_b % 7) != (inv_mo % 7))) / float(inv_b.size * 2))

            key = int(inv_b[0] + 2*inv_b[1] + 5*inv_b[2] + 3*inv_b[3] + 11*inv_b[4])
            legal_vals.append(0.0 if (key % 19) in (7, 12) else 1.0)

            # PrimeSeal stability score (quick primes/checks) – expected parity stability
            sc = _primeseal_stability_score(m_base, m_om, m_mo, primes=self.lock_quick_primes, r_checks=self.lock_quick_checks)
            seal_vals.append(sc)

        spin_mean = float(np.mean(spin_vals))
        lock19_mean = float(np.mean(lock19_vals))
        lock7_mean = float(np.mean(lock7_vals))
        legal_mean = float(np.mean(legal_vals))
        seal_min = float(np.min(seal_vals))

        # Score is a weighted combination of expected sealing and tri-lock proxies
        score = (self.lock_w_seal * seal_min +
                 self.lock_w_spin * spin_mean +
                 self.lock_w_19 * lock19_mean +
                 self.lock_w_7 * lock7_mean +
                 self.lock_w_legal * legal_mean)

        detail = {
            "seal_min": seal_min,
            "spin_mean": spin_mean,
            "lock19_mean": lock19_mean,
            "lock7_mean": lock7_mean,
            "legal_mean": legal_mean,
        }
        return float(score), detail

    def forward(self, img: np.ndarray):
        """
        v83 forward = v81 scheduler, but lock burst is chosen by PrimeSeal-guided scoring.
        """
        img = as_image(img)
        rgb = ensure_rgb(img)
        Y, _, _ = rgb_to_yuv(rgb)
        Rimg = rank_transform(Y)
        mag, _, _, _ = compute_gradients(Rimg)

        seed = self._image_digest(Rimg, mag, rgb)
        U0 = self.scheduler.init_registers(seed)

        # Round 0
        cfg0 = self.scheduler.config_from_registers(U0, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
        r0 = self._infer_with_config(img, cfg0)
        pred0, prob0, conf0, dbg0 = r0
        if conf0 >= self.conf_fast and float(dbg0.get("amp_max", 0.0)) >= self.amp_fast:
            return pred0, prob0, conf0

        # Round 1 (braider)
        Rb = self.scheduler.choose_braider(U0)
        U1 = self.scheduler.apply_step(U0, Rb)
        cfg1 = self.scheduler.config_from_registers(U1, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
        r1 = self._infer_with_config(img, cfg1)
        pred1, prob1, conf1, dbg1 = r1

        # Early exit if now strong
        if max(conf0, conf1) >= self.conf_fast and max(float(dbg0.get("amp_max", 0.0)), float(dbg1.get("amp_max", 0.0))) >= self.amp_fast:
            return (pred0, prob0, conf0) if conf0 >= conf1 else (pred1, prob1, conf1)

        # PrimeSeal-guided lock selection: evaluate lock candidates cheaply
        lock_eval = []
        for Rcand in self.lock_candidates:
            Ucand = self.scheduler.apply_step(U1, Rcand)
            cfg = self.scheduler.config_from_registers(Ucand, self.base_taus, mode_count=6, keep_top_base=self.keep_top)
            sc, detail = self._lock_candidate_score(img, cfg)
            lock_eval.append((sc, int(Rcand), cfg, detail))

        lock_eval.sort(key=lambda x: x[0])
        best_sc, best_R, best_cfg, best_detail = lock_eval[0]

        # Round 2 (lock)
        r2 = self._infer_with_config(img, best_cfg)
        pred2, prob2, conf2, dbg2 = r2
        if isinstance(dbg2, dict):
            dbg2["lock_selected_R"] = int(best_R)
            dbg2["lock_select_score"] = float(best_sc)
            dbg2["lock_select_detail"] = best_detail

        # Choose best round (confidence; tie-break by energy)
        cands = [r0, r1, r2]
        confs = [float(c[2]) for c in cands]
        best_idx = int(np.argmax(confs))
        if sorted(confs, reverse=True)[0] - sorted(confs, reverse=True)[1] < 0.02:
            energies = [float(c[3].get("best_energy", 1e9)) if isinstance(c[3], dict) else 1e9 for c in cands]
            best_idx = int(np.argmin(energies))

        pred, prob, conf, _ = cands[best_idx]
        return pred, prob, conf

if __name__ == "__main__":
    run_benchmark()