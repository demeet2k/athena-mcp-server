"""
NIGHTMARE BENCHMARK 02: ADVERSARIAL ATTACKS
============================================
Intentional attacks on decision boundaries.

CHALLENGES:
    ✗ Perturbations pushing toward confusable classes (3→8, 4→9, 1→7)
    ✗ Adversarial patches in corners (high-frequency patterns)
    ✗ Boundary samples (morphed between two classes)
    ✗ Gradient-direction noise (simulated FGSM)
    ✗ Feature attacks (adding/removing strokes to confuse)
    ✗ 10% TARGETED label noise (flipped to confusable class)
    ✗ Balanced classes (fair boundary test)

TARGET: >90% = EXCEPTIONAL, >85% = EXCELLENT, >75% = GOOD

This tests: DECISION BOUNDARY ROBUSTNESS + FEATURE STABILITY
"""

import numpy as np
import time
from scipy import ndimage
from typing import Tuple
from dataclasses import dataclass

BENCHMARK_ID = "02"
BENCHMARK_NAME = "ADVERSARIAL"
BENCHMARK_FULL = "ADVERSARIAL ATTACKS"

# Confusion pairs: digits that are structurally similar
CONFUSION_PAIRS = [
    (3, 8), (8, 3),  # loops
    (4, 9), (9, 4),  # closed top
    (1, 7), (7, 1),  # vertical stroke
    (5, 6), (6, 5),  # curves
    (0, 6), (6, 0),  # round
    (2, 7), (7, 2),  # diagonal
    (5, 8), (8, 5),  # curves + loops
    (3, 5), (5, 3),  # open curves
]

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
# ADVERSARIAL AUGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_confusion_partner(digit):
    """Get a digit that this one is commonly confused with."""
    partners = [p[1] for p in CONFUSION_PAIRS if p[0] == digit]
    if partners:
        return np.random.choice(partners)
    return (digit + 1) % 10

def create_perturbation_toward(img, source_digit, target_digit, epsilon=0.3):
    """Push the image features toward a target digit."""
    target_img = draw_digit(target_digit, thickness=1.0)
    perturbation = (target_img - img) * epsilon
    return img + perturbation

def add_adversarial_patch(img, patch_size=6):
    """Add high-frequency adversarial patch."""
    img = img.copy()
    corners = [(0, 0), (0, 28-patch_size), (28-patch_size, 0), (28-patch_size, 28-patch_size)]
    y, x = corners[np.random.randint(4)]
    
    # High-frequency checkerboard pattern
    patch = np.zeros((patch_size, patch_size), dtype=np.float32)
    for i in range(patch_size):
        for j in range(patch_size):
            patch[i, j] = ((i + j) % 2) * np.random.uniform(0.7, 1.0)
    
    img[y:y+patch_size, x:x+patch_size] = patch
    return img

def create_boundary_sample(digit):
    """Create a sample on the decision boundary (morphed between classes)."""
    partner = get_confusion_partner(digit)
    img1 = draw_digit(digit, thickness=np.random.uniform(0.9, 1.2))
    img2 = draw_digit(partner, thickness=np.random.uniform(0.9, 1.2))
    alpha = np.random.uniform(0.35, 0.5)  # Ambiguous zone
    return img1 * (1 - alpha) + img2 * alpha

def add_gradient_noise(img, strength=0.2):
    """Simulated FGSM-style gradient direction noise."""
    freq_noise = np.zeros((28, 28), dtype=np.float32)
    for freq in range(2, 8):
        phase = np.random.uniform(0, 2*np.pi)
        freq_noise += np.sin(np.linspace(0, freq*np.pi, 28).reshape(-1, 1) + phase) * 0.1
        freq_noise += np.sin(np.linspace(0, freq*np.pi, 28).reshape(1, -1) + phase) * 0.1
    return img + freq_noise * strength

def apply_feature_attack(img, digit):
    """Add or remove strokes to create confusion."""
    img = img.copy()
    
    if digit == 7 and np.random.random() < 0.6:
        # Add crossbar (makes 7 look like a symbol)
        draw_line(img, 12, 8, 12, 18, thickness=1.0)
    elif digit == 4 and np.random.random() < 0.5:
        # Close the gap (makes 4 look like 9)
        draw_arc(img, 10, 14, 5, 0, np.pi, thickness=0.9)
    elif digit == 1 and np.random.random() < 0.6:
        # Add serifs (ambiguous with 7)
        draw_line(img, 22, 10, 22, 18, thickness=1.0)
        draw_line(img, 6, 12, 6, 16, thickness=0.8)
    elif digit == 3 and np.random.random() < 0.5:
        # Close loops (makes 3 look like 8)
        draw_line(img, 14, 9, 14, 12, thickness=0.8)
    elif digit == 5 and np.random.random() < 0.5:
        # Extend curve (makes 5 look like 6)
        draw_arc(img, 8, 10, 4, np.pi/2, np.pi, thickness=0.9)
    elif digit == 6 and np.random.random() < 0.5:
        # Flatten top (makes 6 look like 0)
        draw_arc(img, 8, 14, 5, 0, np.pi, thickness=0.8)
    elif digit == 9 and np.random.random() < 0.5:
        # Add bottom loop (makes 9 look like 8)
        draw_arc(img, 20, 14, 4, 0, 2*np.pi, thickness=0.7)
    
    return img

def augment_adversarial(img, digit):
    """ADVERSARIAL: Intentional attacks on decision boundaries."""
    
    attack_type = np.random.choice([
        'perturbation', 'patch', 'boundary', 'gradient', 'feature'
    ], p=[0.25, 0.20, 0.20, 0.20, 0.15])
    
    if attack_type == 'perturbation':
        target = get_confusion_partner(digit)
        epsilon = np.random.uniform(0.2, 0.4)
        img = create_perturbation_toward(img, digit, target, epsilon)
        img = img + np.random.randn(28, 28).astype(np.float32) * 0.1
    
    elif attack_type == 'patch':
        img = add_adversarial_patch(img, patch_size=np.random.randint(4, 8))
        img = img + np.random.randn(28, 28).astype(np.float32) * 0.08
    
    elif attack_type == 'boundary':
        img = create_boundary_sample(digit)
        img = img + np.random.randn(28, 28).astype(np.float32) * 0.12
    
    elif attack_type == 'gradient':
        img = add_gradient_noise(img, strength=np.random.uniform(0.15, 0.35))
    
    elif attack_type == 'feature':
        img = apply_feature_attack(img, digit)
        img = img + np.random.randn(28, 28).astype(np.float32) * 0.1
    
    # Light geometric perturbation (keep it recognizable)
    angle = np.random.uniform(-15, 15)
    img = ndimage.rotate(img, angle, reshape=False, mode='constant', order=1)
    
    # Elastic
    shape = img.shape
    dx = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), 0.5) * 2
    dy = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), 0.5) * 2
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = (np.clip(y + dy, 0, shape[0]-1).astype(int),
               np.clip(x + dx, 0, shape[1]-1).astype(int))
    img = img[indices]
    
    return np.clip(img, 0, 1).astype(np.float32)

# ═══════════════════════════════════════════════════════════════════════════════
# DATASET GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

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

def generate_dataset(n_train=60000, n_test=10000, targeted_noise=0.10, seed=None):
    """Generate the ADVERSARIAL dataset."""
    if seed is not None:
        np.random.seed(seed)
    
    print(f"\n{'='*60}")
    print(f"  NIGHTMARE {BENCHMARK_ID}: {BENCHMARK_FULL}")
    print(f"{'='*60}")
    print(f"  Training: {n_train} | Test: {n_test} | Targeted noise: {targeted_noise*100:.0f}%")
    
    def make_batch(n, add_noise):
        X = np.zeros((n, 784), dtype=np.float32)
        Y = np.zeros((n, 10), dtype=np.float32)
        
        for i in range(n):
            d = np.random.randint(0, 10)
            base = draw_digit(d)
            aug = augment_adversarial(base, d)
            X[i] = aug.flatten()
            
            # TARGETED noise: flip to confusable class
            if add_noise and np.random.random() < targeted_noise:
                wrong = get_confusion_partner(d)
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
    """Train model on this benchmark."""
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
