"""
NIGHTMARE BENCHMARK 01: GEOMETRIC TORTURE
==========================================
The original nightmare. Everything geometric that can go wrong.

CHALLENGES:
    ✗ Extreme rotations (±45°)
    ✗ Extreme scaling (0.5x - 1.5x)  
    ✗ Heavy elastic deformations
    ✗ Random occlusions (10-30%)
    ✗ Stroke dropout
    ✗ Multi-layer noise (blur + salt-pepper + gaussian)
    ✗ 5% label noise in training
    ✗ Class imbalance (1,7 appear 2x more; 0,8 appear 0.5x)

TARGET: >90% = EXCEPTIONAL, >85% = EXCELLENT, >75% = GOOD

This tests: GEOMETRIC INVARIANCE + NOISE ROBUSTNESS
"""

import numpy as np
import time
from scipy import ndimage
from typing import Tuple
from dataclasses import dataclass

BENCHMARK_ID = "01"
BENCHMARK_NAME = "GEOMETRIC"
BENCHMARK_FULL = "GEOMETRIC TORTURE"

# ═══════════════════════════════════════════════════════════════════════════════
# DIGIT RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def draw_line(img, y0, x0, y1, x1, thickness=1.0):
    length = max(abs(y1-y0), abs(x1-x0), 1)
    for t in np.linspace(0, 1, int(length * 3) + 1):
        y, x = y0 + t * (y1 - y0), x0 + t * (x1 - x0)
        yi, xi = int(round(y)), int(round(x))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = yi + dy, xi + dx
                if 0 <= ny < img.shape[0] and 0 <= nx < img.shape[1]:
                    dist = np.sqrt((y - ny)**2 + (x - nx)**2)
                    img[ny, nx] = max(img[ny, nx], max(0, 1 - dist / thickness))

def draw_arc(img, cy, cx, radius, start, end, thickness=1.0):
    n_points = max(10, int(abs(end - start) * radius * 2))
    for angle in np.linspace(start, end, n_points):
        y, x = cy + radius * np.sin(angle), cx + radius * np.cos(angle)
        yi, xi = int(round(y)), int(round(x))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = yi + dy, xi + dx
                if 0 <= ny < img.shape[0] and 0 <= nx < img.shape[1]:
                    dist = np.sqrt((y - ny)**2 + (x - nx)**2)
                    img[ny, nx] = max(img[ny, nx], max(0, 1 - dist / thickness))

def draw_digit(digit, size=28, thickness=None, scale=1.0):
    img = np.zeros((size, size), dtype=np.float32)
    th = thickness if thickness else np.random.uniform(0.8, 1.5)
    cy, cx = size // 2, size // 2
    r = 7 * scale
    
    if digit == 0:
        draw_arc(img, cy, cx, r, 0, 2*np.pi, th)
    elif digit == 1:
        draw_line(img, cy - 8*scale, cx, cy + 8*scale, cx, th)
    elif digit == 2:
        draw_arc(img, cy - 4*scale, cx + 1*scale, 5*scale, np.pi, 0, th)
        draw_line(img, cy - 4*scale, cx + 6*scale, cy + 6*scale, cx - 4*scale, th)
        draw_line(img, cy + 6*scale, cx - 4*scale, cy + 6*scale, cx + 5*scale, th)
    elif digit == 3:
        draw_arc(img, cy - 4*scale, cx, 5*scale, -np.pi/2, np.pi/2, th)
        draw_arc(img, cy + 4*scale, cx, 5*scale, -np.pi/2, np.pi/2, th)
    elif digit == 4:
        draw_line(img, cy - 8*scale, cx + 3*scale, cy + 1*scale, cx - 5*scale, th)
        draw_line(img, cy + 1*scale, cx - 5*scale, cy + 1*scale, cx + 6*scale, th)
        draw_line(img, cy - 8*scale, cx + 3*scale, cy + 8*scale, cx + 3*scale, th)
    elif digit == 5:
        draw_line(img, cy - 8*scale, cx + 4*scale, cy - 8*scale, cx - 4*scale, th)
        draw_line(img, cy - 8*scale, cx - 4*scale, cy - 1*scale, cx - 4*scale, th)
        draw_arc(img, cy + 3*scale, cx, 5*scale, np.pi, -np.pi/3, th)
    elif digit == 6:
        draw_arc(img, cy - 2*scale, cx - 2*scale, 6*scale, np.pi/2, np.pi, th)
        draw_arc(img, cy + 4*scale, cx, 5*scale, 0, 2*np.pi, th)
    elif digit == 7:
        draw_line(img, cy - 8*scale, cx - 5*scale, cy - 8*scale, cx + 5*scale, th)
        draw_line(img, cy - 8*scale, cx + 5*scale, cy + 8*scale, cx - 2*scale, th)
    elif digit == 8:
        draw_arc(img, cy - 4*scale, cx, 4.5*scale, 0, 2*np.pi, th)
        draw_arc(img, cy + 5*scale, cx, 5.5*scale, 0, 2*np.pi, th)
    elif digit == 9:
        draw_arc(img, cy - 4*scale, cx, 5*scale, 0, 2*np.pi, th)
        draw_line(img, cy - 4*scale, cx + 5*scale, cy + 8*scale, cx + 2*scale, th)
    
    return np.clip(img, 0, 1).astype(np.float32)

# ═══════════════════════════════════════════════════════════════════════════════
# GEOMETRIC NIGHTMARE AUGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def elastic_transform(img, alpha=4, sigma=0.5):
    shape = img.shape
    dx = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    dy = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), sigma) * alpha
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = (np.clip(y + dy, 0, shape[0]-1).astype(int),
               np.clip(x + dx, 0, shape[1]-1).astype(int))
    return img[indices]

def scale_image(img, scale):
    zoomed = ndimage.zoom(img, scale, order=1)
    h, w = zoomed.shape
    size = 28
    result = np.zeros((size, size), dtype=np.float32)
    if h >= size and w >= size:
        sh, sw = (h - size) // 2, (w - size) // 2
        result = zoomed[sh:sh+size, sw:sw+size]
    else:
        ph, pw = (size - h) // 2, (size - w) // 2
        eh, ew = min(h, size-ph), min(w, size-pw)
        result[ph:ph+eh, pw:pw+ew] = zoomed[:eh, :ew]
    return result

def augment_geometric(img):
    """GEOMETRIC TORTURE: Everything spatial that can go wrong."""
    
    # EXTREME rotation (±45°)
    angle = np.random.uniform(-45, 45)
    img = ndimage.rotate(img, angle, reshape=False, mode='constant', order=1)
    
    # EXTREME scaling (0.5x - 1.5x)
    scale = np.random.uniform(0.5, 1.5)
    img = scale_image(img, scale)
    
    # Elastic torture
    img = elastic_transform(img, alpha=np.random.uniform(3, 6), sigma=np.random.uniform(0.4, 0.8))
    
    # Heavy translation (±5 pixels)
    img = ndimage.shift(img, [np.random.randint(-5, 6), np.random.randint(-5, 6)], mode='constant')
    
    # Shear transform
    shear = np.random.uniform(-0.3, 0.3)
    transform = np.array([[1, shear], [0, 1]])
    img = ndimage.affine_transform(img, transform, mode='constant')
    
    # Occlusion (50% chance)
    if np.random.random() < 0.5:
        for _ in range(np.random.randint(1, 4)):
            h, w = np.random.randint(3, 10), np.random.randint(3, 10)
            y, x = np.random.randint(0, 28-h), np.random.randint(0, 28-w)
            img[y:y+h, x:x+w] = 0
    
    # Stroke dropout (40% chance)
    if np.random.random() < 0.4:
        mask = np.random.random(img.shape) > np.random.uniform(0.1, 0.3)
        img = img * mask
    
    # Heavy blur
    img = ndimage.gaussian_filter(img, sigma=np.random.uniform(0.5, 1.2))
    
    # Salt and pepper
    noise = np.random.random(img.shape)
    img[noise < 0.02] = 1.0
    img[noise > 0.98] = 0.0
    
    # Gaussian noise
    img = img + np.random.randn(28, 28).astype(np.float32) * np.random.uniform(0.1, 0.25)
    
    # Random gamma (30% chance)
    if np.random.random() < 0.3:
        img = np.clip(img, 0, 1) ** np.random.uniform(0.5, 2.0)
    
    return np.clip(img, 0, 1).astype(np.float32)

# ═══════════════════════════════════════════════════════════════════════════════
# DATASET GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

# Class imbalance
CLASS_WEIGHTS = {0: 0.5, 1: 2.0, 2: 1.0, 3: 1.0, 4: 1.0,
                 5: 1.0, 6: 1.0, 7: 2.0, 8: 0.5, 9: 1.0}

@dataclass 
class BenchmarkResult:
    benchmark_id: str
    benchmark_name: str
    train_acc: float
    test_acc: float
    best_test: float
    total_time: float
    epochs: int
    final_loss: float

def generate_dataset(n_train=60000, n_test=10000, label_noise=0.05, seed=None):
    """Generate the GEOMETRIC NIGHTMARE dataset."""
    if seed is not None:
        np.random.seed(seed)
    
    print(f"\n{'='*60}")
    print(f"  NIGHTMARE {BENCHMARK_ID}: {BENCHMARK_FULL}")
    print(f"{'='*60}")
    print(f"  Training: {n_train} | Test: {n_test} | Label noise: {label_noise*100:.0f}%")
    
    total = sum(CLASS_WEIGHTS.values())
    class_probs = [CLASS_WEIGHTS[i] / total for i in range(10)]
    
    def make_batch(n, add_noise):
        X = np.zeros((n, 784), dtype=np.float32)
        Y = np.zeros((n, 10), dtype=np.float32)
        classes = np.random.choice(10, size=n, p=class_probs)
        
        for i in range(n):
            d = classes[i]
            base = draw_digit(d)
            aug = augment_geometric(base)
            X[i] = aug.flatten()
            
            if add_noise and np.random.random() < label_noise:
                wrong = np.random.choice([x for x in range(10) if x != d])
                Y[i, wrong] = 1
            else:
                Y[i, d] = 1
            
            if (i + 1) % 10000 == 0:
                print(f"    {i+1}/{n}...")
        return X, Y
    
    print(f"  Generating training data...")
    train_X, train_Y = make_batch(n_train, add_noise=True)
    perm = np.random.permutation(n_train)
    train_X, train_Y = train_X[perm], train_Y[perm]
    
    print(f"  Generating test data...")
    test_X, test_Y = make_batch(n_test, add_noise=False)
    perm = np.random.permutation(n_test)
    test_X, test_Y = test_X[perm], test_Y[perm]
    
    return train_X, train_Y, test_X, test_Y

# ═══════════════════════════════════════════════════════════════════════════════
# TRAINING INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

def visualize(img, label=None):
    chars = ' .:-=+*#%@'
    img = img.reshape(28, 28) if img.ndim == 1 else img
    lines = [f"  Label: {label}"] if label is not None else []
    for row in range(0, 28, 2):
        line = '  '
        for col in range(0, 28, 2):
            val = img[row:row+2, col:col+2].mean()
            line += chars[min(int(val * 9), 9)]
        lines.append(line)
    return '\n'.join(lines)

def train_on_benchmark(model, train_X, train_Y, test_X, test_Y, epochs=20, batch_size=128):
    """Train model on this benchmark. Model needs forward/backward/step/param_count."""
    n_train, n_batches = len(train_X), len(train_X) // batch_size
    
    print(f"\n  Training on NIGHTMARE {BENCHMARK_ID}: {BENCHMARK_NAME}")
    print(f"  Parameters: {model.param_count():,}")
    print(f"\n  {'Ep':>3} {'Time':>6} {'Loss':>8} {'TrAcc':>7} {'TeAcc':>7}")
    print(f"  {'-'*45}")
    
    best_test, start, final_loss = 0, time.time(), 0
    
    for epoch in range(1, epochs + 1):
        ep_start = time.time()
        perm = np.random.permutation(n_train)
        train_X_s, train_Y_s = train_X[perm], train_Y[perm]
        total_loss, total_correct = 0, 0
        
        for b in range(n_batches):
            s, e = b * batch_size, (b + 1) * batch_size
            bX, bY = train_X_s[s:e], train_Y_s[s:e]
            pred = model.forward(bX)
            loss = -np.mean(np.sum(bY * np.log(np.clip(pred, 1e-7, 1)), axis=1))
            total_loss += loss
            total_correct += np.sum(pred.argmax(1) == bY.argmax(1))
            model.backward(bY)
            model.step(loss, total_correct / ((b + 1) * batch_size))
        
        train_acc = total_correct / n_train
        test_pred = model.forward(test_X)
        test_acc = np.mean(test_pred.argmax(1) == test_Y.argmax(1))
        best_test = max(best_test, test_acc)
        final_loss = total_loss / n_batches
        
        print(f"  {epoch:3d} {time.time()-ep_start:5.1f}s {final_loss:8.4f} {train_acc:6.1%} {test_acc:6.1%}")
    
    return BenchmarkResult(BENCHMARK_ID, BENCHMARK_NAME, train_acc, test_acc, 
                          best_test, time.time()-start, epochs, final_loss)

def evaluate(result):
    grade = "🏆 EXCEPTIONAL" if result.best_test >= 0.90 else \
            "⭐ EXCELLENT" if result.best_test >= 0.85 else \
            "✓ GOOD" if result.best_test >= 0.75 else "⚠ NEEDS WORK"
    print(f"\n{'='*60}")
    print(f"  NIGHTMARE {result.benchmark_id}: {result.benchmark_name}")
    print(f"  Best: {result.best_test:.1%} | Grade: {grade}")
    print(f"{'='*60}")
    return grade

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("="*70)
    print(f"  NIGHTMARE BENCHMARK {BENCHMARK_ID}: {BENCHMARK_FULL}")
    print("="*70)
    
    np.random.seed(42)
    train_X, train_Y, test_X, test_Y = generate_dataset(n_train=1000, n_test=200, seed=42)
    
    print(f"\n  Sample digits:")
    for i in range(3):
        idx = np.random.randint(len(test_X))
        print(visualize(test_X[idx], test_Y[idx].argmax()))
        print()
