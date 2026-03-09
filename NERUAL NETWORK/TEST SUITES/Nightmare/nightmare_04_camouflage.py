"""
NIGHTMARE BENCHMARK 04: CAMOUFLAGE
==================================
Hide the digit in plain sight. Perceptual nightmare.

CHALLENGES:
    ✗ Digits hidden in striped backgrounds (H/V/diagonal)
    ✗ Grid overlay camouflage
    ✗ Smooth noise texture blending
    ✗ Checkerboard interference
    ✗ Negative space (inverse) digits on textured backgrounds
    ✗ Extreme low contrast (8-18% contrast)
    ✗ Texture-matched foreground/background
    ✗ 2% label noise
    ✗ Balanced classes

TARGET: >90% = EXCEPTIONAL, >85% = EXCELLENT, >75% = GOOD

This tests: FIGURE-GROUND SEPARATION + CONTRAST INVARIANCE
"""

import numpy as np
import time
from scipy import ndimage
from typing import Tuple
from dataclasses import dataclass

BENCHMARK_ID = "04"
BENCHMARK_NAME = "CAMOUFLAGE"
BENCHMARK_FULL = "CAMOUFLAGE"

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
# TEXTURE GENERATORS
# ═══════════════════════════════════════════════════════════════════════════════

def create_stripe_texture(size=28, orientation='horizontal', frequency=0.5, phase=0):
    """Create striped pattern."""
    if orientation == 'horizontal':
        texture = np.sin(np.linspace(0, frequency * np.pi * size, size).reshape(-1, 1) + phase)
        texture = np.tile(texture, (1, size))
    elif orientation == 'vertical':
        texture = np.sin(np.linspace(0, frequency * np.pi * size, size).reshape(1, -1) + phase)
        texture = np.tile(texture, (size, 1))
    else:  # diagonal
        x = np.linspace(0, frequency * np.pi * size, size)
        texture = np.sin(x.reshape(-1, 1) + x.reshape(1, -1) + phase)
    
    return ((texture + 1) / 2).astype(np.float32)

def create_grid_texture(size=28, spacing=4):
    """Create grid pattern."""
    texture = np.zeros((size, size), dtype=np.float32)
    texture[::spacing, :] = 1
    texture[:, ::spacing] = 1
    return ndimage.gaussian_filter(texture, sigma=0.5)

def create_noise_texture(size=28, scale=3):
    """Create smooth noise texture (like clouds)."""
    noise = np.random.randn(size, size).astype(np.float32)
    smooth = ndimage.gaussian_filter(noise, sigma=scale)
    return (smooth - smooth.min()) / (smooth.max() - smooth.min() + 1e-8)

def create_checkerboard(size=28, block_size=4):
    """Create checkerboard pattern."""
    texture = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            if ((i // block_size) + (j // block_size)) % 2 == 0:
                texture[i, j] = 1
    return texture

def create_wave_texture(size=28, freq_x=0.3, freq_y=0.4):
    """Create interference wave pattern."""
    x = np.linspace(0, 2*np.pi*freq_x*size, size)
    y = np.linspace(0, 2*np.pi*freq_y*size, size)
    X, Y = np.meshgrid(x, y)
    texture = np.sin(X) * np.cos(Y)
    return ((texture + 1) / 2).astype(np.float32)

# ═══════════════════════════════════════════════════════════════════════════════
# CAMOUFLAGE AUGMENTATION
# ═══════════════════════════════════════════════════════════════════════════════

def augment_camouflage(img, digit):
    """CAMOUFLAGE: Hide the digit in perceptual chaos."""
    
    camo_type = np.random.choice([
        'stripes', 'grid', 'noise', 'checker', 'inverse', 
        'low_contrast', 'texture_match', 'wave'
    ], p=[0.15, 0.12, 0.15, 0.12, 0.12, 0.12, 0.12, 0.10])
    
    if camo_type == 'stripes':
        orientation = np.random.choice(['horizontal', 'vertical', 'diagonal'])
        texture = create_stripe_texture(28, orientation,
                                        frequency=np.random.uniform(0.3, 0.8),
                                        phase=np.random.uniform(0, 2*np.pi))
        contrast = np.random.uniform(0.15, 0.35)
        img = texture * (1 - contrast) + img * contrast
    
    elif camo_type == 'grid':
        texture = create_grid_texture(28, spacing=np.random.randint(3, 6))
        contrast = np.random.uniform(0.2, 0.4)
        img = texture * (1 - contrast) + img * contrast
    
    elif camo_type == 'noise':
        texture = create_noise_texture(28, scale=np.random.uniform(2, 5))
        contrast = np.random.uniform(0.15, 0.35)
        img = texture * (1 - contrast) + img * contrast
    
    elif camo_type == 'checker':
        texture = create_checkerboard(28, block_size=np.random.randint(2, 6))
        contrast = np.random.uniform(0.2, 0.4)
        img = texture * (1 - contrast) + img * contrast
    
    elif camo_type == 'inverse':
        # Negative space digit on textured background
        texture = create_noise_texture(28, scale=np.random.uniform(3, 6))
        texture = texture * 0.4 + 0.3  # Mid-gray range
        
        inv_img = 1 - img
        fg_val = np.random.uniform(0.1, 0.3)
        img = texture * inv_img + (1 - inv_img) * fg_val
    
    elif camo_type == 'low_contrast':
        # Extreme low contrast
        contrast = np.random.uniform(0.08, 0.18)
        base = np.random.uniform(0.4, 0.6)
        img = base + (img - 0.5) * contrast
    
    elif camo_type == 'texture_match':
        # Digit has SAME texture as background (hardest)
        tex_type = np.random.randint(0, 3)
        if tex_type == 0:
            texture = create_stripe_texture(28, 'diagonal', 0.5)
        elif tex_type == 1:
            texture = create_noise_texture(28, 3)
        else:
            texture = create_grid_texture(28, 4)
        
        # Apply texture to both foreground and background
        fg_intensity = np.random.uniform(0.55, 0.85)
        bg_intensity = np.random.uniform(0.2, 0.45)
        
        mask = img > 0.3
        img = np.where(mask, texture * fg_intensity, texture * bg_intensity)
    
    elif camo_type == 'wave':
        texture = create_wave_texture(28, 
                                      freq_x=np.random.uniform(0.2, 0.5),
                                      freq_y=np.random.uniform(0.2, 0.5))
        contrast = np.random.uniform(0.18, 0.38)
        img = texture * (1 - contrast) + img * contrast
    
    # Light geometric augmentation (keep it recognizable)
    angle = np.random.uniform(-15, 15)
    img = ndimage.rotate(img, angle, reshape=False, mode='constant', order=1)
    
    # Light scaling
    scale = np.random.uniform(0.88, 1.12)
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
    
    # Additional noise
    img = img + np.random.randn(28, 28).astype(np.float32) * np.random.uniform(0.05, 0.12)
    
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

def generate_dataset(n_train=60000, n_test=10000, label_noise=0.02, seed=None):
    """Generate the CAMOUFLAGE dataset."""
    if seed is not None:
        np.random.seed(seed)
    
    print(f"\n{'='*60}")
    print(f"  NIGHTMARE {BENCHMARK_ID}: {BENCHMARK_FULL}")
    print(f"{'='*60}")
    print(f"  Training: {n_train} | Test: {n_test} | Label noise: {label_noise*100:.0f}%")
    
    def make_batch(n, add_noise):
        X = np.zeros((n, 784), dtype=np.float32)
        Y = np.zeros((n, 10), dtype=np.float32)
        
        for i in range(n):
            d = np.random.randint(0, 10)
            base = draw_digit(d, thickness=np.random.uniform(1.0, 1.5))
            aug = augment_camouflage(base, d)
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
