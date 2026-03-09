"""
NIGHTMARE BENCHMARK 03: CLUTTERED SCENE
========================================
Multi-object chaos. Only ONE digit is the target.

CHALLENGES:
    ✗ Multiple overlapping digits in same image
    ✗ Distractor fragments scattered everywhere
    ✗ Partial digits bleeding in from edges
    ✗ Random stroke fragments as noise
    ✗ Figure-ground separation required
    ✗ Target digit is slightly larger/brighter (but not by much)
    ✗ 3% label noise
    ✗ Slight class imbalance toward simple digits (1, 7)

TARGET: >90% = EXCEPTIONAL, >85% = EXCELLENT, >75% = GOOD

This tests: ATTENTION + SEGMENTATION + INTERFERENCE REJECTION
"""

import numpy as np
import time
from scipy import ndimage
from typing import Tuple
from dataclasses import dataclass

BENCHMARK_ID = "03"
BENCHMARK_NAME = "CLUTTERED"
BENCHMARK_FULL = "CLUTTERED SCENE"

# ═══════════════════════════════════════════════════════════════════════════════
# DIGIT RENDERER
# ═══════════════════════════════════════════════════════════════════════════════

def draw_line(img, y0, x0, y1, x1, thickness=1.0, value=1.0):
    length = max(abs(y1-y0), abs(x1-x0), 1)
    for t in np.linspace(0, 1, int(length * 3) + 1):
        y, x = y0 + t * (y1 - y0), x0 + t * (x1 - x0)
        yi, xi = int(round(y)), int(round(x))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = yi + dy, xi + dx
                if 0 <= ny < img.shape[0] and 0 <= nx < img.shape[1]:
                    dist = np.sqrt((y - ny)**2 + (x - nx)**2)
                    contrib = max(0, 1 - dist / thickness) * value
                    img[ny, nx] = max(img[ny, nx], contrib)

def draw_arc(img, cy, cx, radius, start, end, thickness=1.0, value=1.0):
    n_points = max(10, int(abs(end - start) * radius * 2))
    for angle in np.linspace(start, end, n_points):
        y, x = cy + radius * np.sin(angle), cx + radius * np.cos(angle)
        yi, xi = int(round(y)), int(round(x))
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                ny, nx = yi + dy, xi + dx
                if 0 <= ny < img.shape[0] and 0 <= nx < img.shape[1]:
                    dist = np.sqrt((y - ny)**2 + (x - nx)**2)
                    contrib = max(0, 1 - dist / thickness) * value
                    img[ny, nx] = max(img[ny, nx], contrib)

def draw_digit(digit, size=28, thickness=None, scale=1.0, offset_y=0, offset_x=0):
    img = np.zeros((size, size), dtype=np.float32)
    th = thickness if thickness else np.random.uniform(0.8, 1.5)
    cy, cx = size // 2 + offset_y, size // 2 + offset_x
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
# CLUTTER AUGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def add_distractor_fragments(img, target_digit, n_fragments=5):
    """Add random digit fragments as distractors."""
    img = img.copy()
    
    for _ in range(n_fragments):
        # Random digit (different from target)
        frag_digit = np.random.choice([d for d in range(10) if d != target_digit])
        frag_scale = np.random.uniform(0.3, 0.7)
        frag_th = np.random.uniform(0.5, 1.0)
        
        # Draw small fragment
        frag_img = draw_digit(frag_digit, thickness=frag_th, scale=frag_scale)
        
        # Random position
        offset_y = np.random.randint(-12, 12)
        offset_x = np.random.randint(-12, 12)
        frag_img = ndimage.shift(frag_img, [offset_y, offset_x], mode='constant')
        
        # Random rotation
        angle = np.random.uniform(-45, 45)
        frag_img = ndimage.rotate(frag_img, angle, reshape=False, mode='constant')
        
        # Keep only part of fragment (random mask)
        mask = np.random.random((28, 28)) > np.random.uniform(0.4, 0.7)
        frag_img = frag_img * mask
        
        # Blend with lower intensity
        intensity = np.random.uniform(0.25, 0.55)
        img = np.maximum(img, frag_img * intensity)
    
    return img

def add_overlapping_digit(img, target_digit):
    """Add another complete digit overlapping the target."""
    # Choose different digit
    other_digit = np.random.choice([d for d in range(10) if d != target_digit])
    
    # Draw with offset and variation
    offset_y = np.random.uniform(-5, 5)
    offset_x = np.random.uniform(-5, 5)
    other_scale = np.random.uniform(0.7, 1.0)
    other_th = np.random.uniform(0.7, 1.1)
    
    other_img = draw_digit(other_digit, thickness=other_th, scale=other_scale)
    other_img = ndimage.shift(other_img, [offset_y, offset_x], mode='constant')
    
    # Random rotation
    angle = np.random.uniform(-30, 30)
    other_img = ndimage.rotate(other_img, angle, reshape=False, mode='constant')
    
    # Blend strategy
    blend = np.random.choice(['max', 'add', 'behind'])
    intensity = np.random.uniform(0.35, 0.6)
    
    if blend == 'max':
        img = np.maximum(img, other_img * intensity)
    elif blend == 'add':
        img = np.clip(img + other_img * intensity * 0.7, 0, 1)
    else:  # behind
        mask = img > 0.2
        img = np.where(mask, img, np.maximum(img, other_img * intensity))
    
    return img

def add_edge_digits(img, target_digit, n_edges=2):
    """Add partial digits bleeding in from edges."""
    for _ in range(n_edges):
        edge_digit = np.random.choice([d for d in range(10) if d != target_digit])
        edge_scale = np.random.uniform(0.6, 1.0)
        edge_img = draw_digit(edge_digit, scale=edge_scale)
        
        # Position at edge
        edge = np.random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            shift = [-np.random.randint(14, 20), np.random.randint(-10, 10)]
        elif edge == 'bottom':
            shift = [np.random.randint(14, 20), np.random.randint(-10, 10)]
        elif edge == 'left':
            shift = [np.random.randint(-10, 10), -np.random.randint(14, 20)]
        else:
            shift = [np.random.randint(-10, 10), np.random.randint(14, 20)]
        
        edge_img = ndimage.shift(edge_img, shift, mode='constant')
        intensity = np.random.uniform(0.4, 0.7)
        img = np.maximum(img, edge_img * intensity)
    
    return img

def add_random_strokes(img, n_strokes=3):
    """Add random stroke fragments as noise."""
    for _ in range(n_strokes):
        y0 = np.random.randint(0, 28)
        x0 = np.random.randint(0, 28)
        y1 = y0 + np.random.randint(-10, 10)
        x1 = x0 + np.random.randint(-10, 10)
        th = np.random.uniform(0.5, 1.2)
        intensity = np.random.uniform(0.2, 0.5)
        
        temp = np.zeros((28, 28), dtype=np.float32)
        draw_line(temp, y0, x0, y1, x1, th)
        img = np.maximum(img, temp * intensity)
    
    return img

def augment_cluttered(img, digit):
    """CLUTTERED: Multi-object chaos with single target."""
    
    clutter_level = np.random.choice(['light', 'medium', 'heavy'], p=[0.2, 0.4, 0.4])
    
    if clutter_level == 'light':
        # Just fragments
        img = add_distractor_fragments(img, digit, n_fragments=np.random.randint(2, 5))
    
    elif clutter_level == 'medium':
        # Fragments + edge digits
        img = add_distractor_fragments(img, digit, n_fragments=np.random.randint(3, 6))
        img = add_edge_digits(img, digit, n_edges=np.random.randint(1, 3))
    
    else:  # heavy
        # Everything
        img = add_distractor_fragments(img, digit, n_fragments=np.random.randint(4, 8))
        if np.random.random() < 0.6:
            img = add_overlapping_digit(img, digit)
        img = add_edge_digits(img, digit, n_edges=np.random.randint(2, 4))
        img = add_random_strokes(img, n_strokes=np.random.randint(2, 5))
    
    # Light geometric augmentation
    angle = np.random.uniform(-20, 20)
    img = ndimage.rotate(img, angle, reshape=False, mode='constant', order=1)
    
    # Light scaling
    scale = np.random.uniform(0.85, 1.15)
    zoomed = ndimage.zoom(img, scale, order=1)
    h, w = zoomed.shape
    result = np.zeros((28, 28), dtype=np.float32)
    if h >= 28 and w >= 28:
        sh, sw = (h - 28) // 2, (w - 28) // 2
        result = zoomed[sh:sh+28, sw:sw+28]
    else:
        ph, pw = (28 - h) // 2, (28 - w) // 2
        eh, ew = min(h, 28-ph), min(w, 28-pw)
        result[ph:ph+eh, pw:pw+ew] = zoomed[:eh, :ew]
    img = result
    
    # Light elastic
    shape = img.shape
    dx = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), 0.4) * 2
    dy = ndimage.gaussian_filter((np.random.rand(*shape) * 2 - 1), 0.4) * 2
    x, y = np.meshgrid(np.arange(shape[1]), np.arange(shape[0]))
    indices = (np.clip(y + dy, 0, shape[0]-1).astype(int),
               np.clip(x + dx, 0, shape[1]-1).astype(int))
    img = img[indices]
    
    # Light noise
    img = ndimage.gaussian_filter(img, sigma=np.random.uniform(0.2, 0.6))
    img = img + np.random.randn(28, 28).astype(np.float32) * 0.08
    
    return np.clip(img, 0, 1).astype(np.float32)

# ═══════════════════════════════════════════════════════════════════════════════
# DATASET GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

# Slight imbalance toward simple digits
CLASS_WEIGHTS = {0: 1.0, 1: 1.3, 2: 1.0, 3: 1.0, 4: 1.0,
                 5: 1.0, 6: 1.0, 7: 1.3, 8: 1.0, 9: 1.0}

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

def generate_dataset(n_train=60000, n_test=10000, label_noise=0.03, seed=None):
    """Generate the CLUTTERED dataset."""
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
            # Target digit is slightly larger/brighter
            base = draw_digit(d, thickness=np.random.uniform(1.0, 1.4), scale=1.0)
            aug = augment_cluttered(base, d)
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
