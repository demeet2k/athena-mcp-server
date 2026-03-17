from __future__ import annotations

import numpy as np
from scipy import ndimage

from .attention_field import generate_attention
from .hypothesis_compiler import generate_mask
from .rank_encoder import compute_gradients, rank_transform


def extract_hog_fast(
    mag: np.ndarray,
    angle: np.ndarray,
    mask: np.ndarray,
    cells: int = 7,
    bins: int = 9,
) -> np.ndarray:
    """Optimized HOG with vectorized bin assignment."""
    cell_size = 4
    hog = np.zeros(cells * cells * bins)

    bin_idx = ((angle + np.pi) / (2 * np.pi) * bins).astype(int) % bins
    weighted_mag = mag * mask

    for i in range(cells):
        for j in range(cells):
            y0, y1 = i * cell_size, (i + 1) * cell_size
            x0, x1 = j * cell_size, (j + 1) * cell_size

            cell_mag = weighted_mag[y0:y1, x0:x1]
            cell_bin = bin_idx[y0:y1, x0:x1]

            for b in range(bins):
                hog[i * cells * bins + j * bins + b] = cell_mag[cell_bin == b].sum()

    norm = np.sqrt(np.sum(hog**2) + 1e-8)
    return hog / norm


def extract_polar(
    R: np.ndarray,
    mask: np.ndarray,
    radial: int = 8,
    angular: int = 8,
) -> np.ndarray:
    """Polar histogram with center-of-mass alignment."""
    weighted = R * mask
    total = weighted.sum()

    if total < 1e-8:
        return np.zeros(radial * angular)

    y_idx, x_idx = np.ogrid[:28, :28]
    cy = (weighted * y_idx).sum() / total
    cx = (weighted * x_idx).sum() / total

    y, x = np.ogrid[:28, :28]
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2)
    theta = np.arctan2(y - cy, x - cx)

    r_max = r.max() + 1e-8
    r_bins = (r / r_max * radial).astype(int).clip(0, radial - 1)
    t_bins = ((theta + np.pi) / (2 * np.pi) * angular).astype(int).clip(0, angular - 1)

    polar = np.zeros(radial * angular)
    for ri in range(radial):
        for ti in range(angular):
            bin_mask = (r_bins == ri) & (t_bins == ti)
            polar[ri * angular + ti] = weighted[bin_mask].sum()

    return polar / (polar.sum() + 1e-8)


def extract_topology(mask: np.ndarray) -> np.ndarray:
    """Topology features from mask."""
    features: list[float] = []

    for thresh in [0.3, 0.5, 0.7]:
        binary = mask > thresh
        labeled, num_comp = ndimage.label(binary)

        filled = ndimage.binary_fill_holes(binary)
        holes = filled.astype(int) - binary.astype(int)
        _, num_holes = ndimage.label(holes)

        features.extend([num_comp / 3.0, num_holes / 2.0])

    total = mask.sum() + 1e-8
    features.append(mask[:14, :].sum() / total)
    features.append(mask[14:, :].sum() / total)
    features.append(mask[:, :14].sum() / total)
    features.append(mask[:, 14:].sum() / total)

    if mask.sum() > 0:
        cy, cx = ndimage.center_of_mass(mask)
        features.extend([cy / 28.0, cx / 28.0])
    else:
        features.extend([0.5, 0.5])

    return np.array(features)


def extract_structure(R: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Structural features."""
    features: list[float] = []

    for qi in range(2):
        for qj in range(2):
            quad = R[qi * 14 : (qi + 1) * 14, qj * 14 : (qj + 1) * 14]
            quad_mask = mask[qi * 14 : (qi + 1) * 14, qj * 14 : (qj + 1) * 14]
            features.append((quad * quad_mask).sum() / 50.0)

    if mask.sum() > 0:
        dilated = ndimage.binary_dilation(mask, iterations=2)
        compactness = mask.sum() / (dilated.sum() + 1e-8)
    else:
        compactness = 0.0
    features.append(compactness)
    features.append(mask.sum() / 784.0)

    return np.array(features)


def extract_all_features(img: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray:
    """Extract complete feature vector."""
    R = rank_transform(img)
    mag, angle = compute_gradients(R)

    if mask is None:
        attention = generate_attention(R)
        mask = generate_mask(attention, R, 0.45)

    if mask.sum() < 10:
        mask = (R > 0.3).astype(np.float32)

    hog = extract_hog_fast(mag, angle, mask)
    polar = extract_polar(R, mask)
    topo = extract_topology(mask)
    struct = extract_structure(R, mask)

    return np.concatenate([hog, polar, topo, struct])
