"""
ATHENA NEURAL NETWORK - COMPATIBILITY WRAPPER
=============================================

Legacy benchmark entrypoint preserved while the implementation is routed
through the modular `athenachka` package.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

from athenachka import AthenaKernel, AthenachkaOrganismV0
from athenachka.core import (
    CompressionPrior,
    NeuralClassifier,
    compile_hypotheses,
    compute_gradients,
    extract_all_features,
    extract_hog_fast,
    extract_polar,
    extract_structure,
    extract_topology,
    generate_attention,
    generate_mask,
    rank_transform,
)


AthenaNeuralNetwork = AthenaKernel
AthenachkaOrganism = AthenachkaOrganismV0


def draw_digit(d: int) -> np.ndarray:
    img = np.zeros((28, 28), dtype=np.float32)

    def line(y0: int, x0: int, y1: int, x1: int) -> None:
        n = max(abs(y1 - y0), abs(x1 - x0), 1)
        for i in range(n + 1):
            y = int(y0 + (y1 - y0) * i / n)
            x = int(x0 + (x1 - x0) * i / n)
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0, y - 1) : min(28, y + 2), max(0, x - 1) : min(28, x + 2)] = 1.0

    def circle(cy: int, cx: int, r: int) -> None:
        for angle in np.linspace(0, 2 * np.pi, int(2 * np.pi * r * 2)):
            y = int(cy + r * np.sin(angle))
            x = int(cx + r * np.cos(angle))
            if 0 <= y < 28 and 0 <= x < 28:
                img[max(0, y - 1) : min(28, y + 2), max(0, x - 1) : min(28, x + 2)] = 1.0

    if d == 0:
        circle(14, 14, 8)
    elif d == 1:
        line(6, 14, 22, 14)
    elif d == 2:
        for i in range(8):
            img[6, 10 + i] = 1.0
        line(6, 17, 14, 10)
        for i in range(8):
            img[14, 10 + i] = 1.0
        line(14, 10, 22, 17)
        for i in range(8):
            img[22, 10 + i] = 1.0
    elif d == 3:
        for i in range(8):
            img[6, 10 + i] = 1.0
        line(6, 17, 14, 14)
        for i in range(5):
            img[14, 12 + i] = 1.0
        line(14, 14, 22, 17)
        for i in range(8):
            img[22, 10 + i] = 1.0
    elif d == 4:
        line(6, 10, 14, 10)
        line(14, 10, 14, 18)
        line(6, 18, 22, 18)
    elif d == 5:
        for i in range(8):
            img[6, 10 + i] = 1.0
        line(6, 10, 14, 10)
        for i in range(8):
            img[14, 10 + i] = 1.0
        line(14, 17, 22, 17)
        for i in range(8):
            img[22, 10 + i] = 1.0
    elif d == 6:
        circle(16, 14, 6)
        line(6, 10, 16, 10)
    elif d == 7:
        for i in range(8):
            img[6, 10 + i] = 1.0
        line(6, 17, 22, 12)
    elif d == 8:
        circle(10, 14, 4)
        circle(18, 14, 4)
    elif d == 9:
        circle(10, 14, 5)
        line(10, 19, 22, 19)

    img = ndimage.gaussian_filter(img, 0.8)
    return img / (img.max() + 1e-8)


def aug_geometric(img: np.ndarray, rng) -> np.ndarray:
    angle = rng.uniform(-25, 25)
    scale = rng.uniform(0.9, 1.1)
    img = ndimage.rotate(img, angle, reshape=False, mode="constant")
    img = ndimage.zoom(img, scale, mode="constant")
    h, w = img.shape
    if h > 28:
        s = (h - 28) // 2
        img = img[s : s + 28, s : s + 28]
    elif h < 28:
        pad = (28 - h) // 2
        img = np.pad(img, ((pad, 28 - h - pad), (pad, 28 - w - pad)), mode="constant")
    return np.clip(img[:28, :28], 0, 1)


def aug_adversarial(img: np.ndarray, rng) -> np.ndarray:
    noise = rng.randn(*img.shape) * 0.25
    return np.clip(img + noise, 0, 1)


def aug_cluttered(img: np.ndarray, rng) -> np.ndarray:
    out = img.copy()
    for _ in range(rng.randint(3, 7)):
        y, x = rng.randint(0, 24), rng.randint(0, 24)
        s = rng.randint(2, 4)
        out[y : y + s, x : x + s] = rng.uniform(0.1, 0.3)
    return out


def aug_camouflage(img: np.ndarray, rng) -> np.ndarray:
    freq = rng.uniform(0.3, 0.6)
    phase = rng.uniform(0, 2 * np.pi)
    y, x = np.ogrid[:28, :28]
    texture = 0.5 + 0.25 * np.sin(freq * x + phase) * np.cos(freq * y + phase * 0.7)
    texture += rng.randn(28, 28) * 0.08
    contrast = rng.uniform(0.15, 0.28)
    fg = texture + contrast
    bg = texture
    mask = img > 0.3
    out = np.where(mask, fg, bg)
    return np.clip(out, 0, 1)


def generate_data(n: int, aug_fn, seed: int):
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

    print("=" * 70)
    print(" ATHENA NEURAL NETWORK - MODULAR KERNEL ".center(70))
    print("=" * 70)

    benchmarks = [
        ("GEOMETRIC", aug_geometric),
        ("ADVERSARIAL", aug_adversarial),
        ("CLUTTERED", aug_cluttered),
        ("CAMOUFLAGE", aug_camouflage),
    ]

    results = {}

    for name, aug_fn in benchmarks:
        print(f"\n{'=' * 50}")
        print(f" {name} ".center(50))
        print("=" * 50)

        X_train, Y_train = generate_data(1000, aug_fn, 42)
        X_test, Y_test = generate_data(250, aug_fn, 142)

        model = AthenaNeuralNetwork()
        t0 = time.time()
        model.train(X_train, Y_train, epochs=20, lr=0.03, verbose=True)
        train_time = time.time() - t0

        t0 = time.time()
        accuracy = model.evaluate(X_test, Y_test, verbose=True)
        infer_time = time.time() - t0

        results[name] = accuracy
        print(f"  Train time: {train_time:.2f}s")
        print(f"  Infer time: {infer_time:.2f}s ({infer_time / len(X_test) * 1000:.1f}ms/sample)")
        print(f"  Parameters: {model.get_param_count():,}")

    print("\n" + "=" * 70)
    print(" FINAL RESULTS ".center(70))
    print("=" * 70)
    print(f"\n{'Benchmark':<15} {'Accuracy':>12}")
    print("-" * 30)
    for name in ["GEOMETRIC", "ADVERSARIAL", "CLUTTERED", "CAMOUFLAGE"]:
        print(f"{name:<15} {results[name] * 100:>11.1f}%")
    avg = np.mean(list(results.values()))
    print("-" * 30)
    print(f"{'AVERAGE':<15} {avg * 100:>11.1f}%")
    return results


if __name__ == "__main__":
    run_benchmark()
