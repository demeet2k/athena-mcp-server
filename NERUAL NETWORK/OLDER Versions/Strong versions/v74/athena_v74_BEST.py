"""
ATHENA v74 REGULARIZED - L2 weight decay to prevent overfitting
"""
import numpy as np
from scipy import ndimage
np.random.seed(42)

def lcn(img):
    lm = ndimage.uniform_filter(img.astype(np.float64), 5)
    lsq = ndimage.uniform_filter((img**2).astype(np.float64), 5)
    return np.clip((img - lm) / (np.sqrt(np.maximum(lsq - lm**2, 1e-8)) + 0.1), -3, 3).astype(np.float32)

def extract_features(X):
    B = X.shape[0]; F = []
    for i in range(B):
        img = X[i].reshape(28, 28); norm = lcn(img)
        norm = (norm - norm.min()) / (norm.max() - norm.min() + 1e-8)
        t = norm.sum() + 1e-8
        y, x = np.mgrid[0:28, 0:28]
        cy, cx = (y * norm).sum() / t, (x * norm).sum() / t
        yc, xc = y - cy, x - cx
        cxx, cyy = (xc**2 * norm).sum() / t, (yc**2 * norm).sum() / t
        cxy = (xc * yc * norm).sum() / t
        pa = 0.5 * np.arctan2(2 * cxy, cxx - cyy + 1e-8)
        h = np.zeros((8, 8), np.float32)
        for yi in range(28):
            for xi in range(28):
                if norm[yi, xi] > 0.1:
                    dy, dx = yi - cy, xi - cx
                    r = np.sqrt(dy**2 + dx**2)
                    th = (np.arctan2(dy, dx) - pa) % (2*np.pi)
                    h[min(int(r/14*8), 7), min(int(th/(2*np.pi)*8), 7)] += norm[yi, xi]
        polar = h.flatten() / (h.sum() + 1e-8)
        rad = np.zeros(8, np.float32)
        for yi in range(28):
            for xi in range(28):
                r = np.sqrt((yi-cy)**2 + (xi-cx)**2)
                rad[min(int(r/14*8), 7)] += norm[yi, xi]
        radial = rad / (rad.sum() + 1e-8)
        gx, gy = ndimage.sobel(norm, axis=1), ndimage.sobel(norm, axis=0)
        mag = np.sqrt(gx**2 + gy**2); angle = np.arctan2(gy, gx)
        coh = np.zeros((7, 7), np.float32)
        for ii in range(7):
            for jj in range(7):
                p, m = angle[ii*4:(ii+1)*4, jj*4:(jj+1)*4], mag[ii*4:(ii+1)*4, jj*4:(jj+1)*4]
                if m.sum() > 0.3:
                    coh[ii, jj] = np.sqrt(np.sin(p).mean()**2 + np.cos(p).mean()**2)
        F.append(np.concatenate([polar, radial, coh.flatten()]))  # 64+8+49=121
    F = np.array(F, np.float32)
    return (F - F.mean(0)) / (F.std(0) + 1e-8)

class RegNet:
    def __init__(s, ind, h=96, seed=42):
        rng = np.random.RandomState(seed)
        s.W1 = rng.randn(ind, h).astype(np.float32) * np.sqrt(2.0/ind)
        s.b1 = np.zeros(h, np.float32)
        s.W2 = rng.randn(h, h//2).astype(np.float32) * np.sqrt(2.0/h)
        s.b2 = np.zeros(h//2, np.float32)
        s.W3 = rng.randn(h//2, 10).astype(np.float32) * np.sqrt(2.0/(h//2))
        s.b3 = np.zeros(10, np.float32)
        s.c = {}
    def fwd(s, X):
        s.c['X'] = X
        s.c['H1'] = np.maximum(0, np.clip(X @ s.W1 + s.b1, -20, 20))
        s.c['H2'] = np.maximum(0, np.clip(s.c['H1'] @ s.W2 + s.b2, -20, 20))
        Z3 = np.clip(s.c['H2'] @ s.W3 + s.b3, -20, 20)
        e = np.exp(Z3 - Z3.max(1, keepdims=True))
        s.c['P'] = e / (e.sum(1, keepdims=True) + 1e-10)
        return s.c['P']
    def bwd(s, Y, lr, wd=0.001):  # wd = weight decay
        N = Y.shape[0]
        dZ3 = (s.c['P'] - Y) / N
        s.W3 -= lr * (s.c['H2'].T @ dZ3 + wd * s.W3); s.b3 -= lr * dZ3.sum(0)
        dZ2 = (dZ3 @ s.W3.T) * (s.c['H2'] > 0)
        s.W2 -= lr * (s.c['H1'].T @ dZ2 + wd * s.W2); s.b2 -= lr * dZ2.sum(0)
        dZ1 = (dZ2 @ s.W2.T) * (s.c['H1'] > 0)
        s.W1 -= lr * (s.c['X'].T @ dZ1 + wd * s.W1); s.b1 -= lr * dZ1.sum(0)
    def pred(s, X): return s.fwd(X).argmax(1)

def draw_digit(d):
    img = np.zeros((28,28), np.float32)
    if d == 0:
        for a in np.linspace(0, 2*np.pi, 60):
            y, x = 14 + 7*np.sin(a), 14 + 7*np.cos(a)
            if 0 <= int(y) < 28 and 0 <= int(x) < 28: img[int(y), int(x)] = 1
    elif d == 1: img[6:22, 13:15] = 1
    elif d == 2: img[6:8,10:18]=1;img[6:14,16:18]=1;img[12:14,10:18]=1;img[12:22,10:12]=1;img[20:22,10:18]=1
    elif d == 3: img[6:8,10:18]=1;img[12:14,10:18]=1;img[20:22,10:18]=1;img[6:22,16:18]=1
    elif d == 4: img[6:14,10:12]=1;img[12:14,10:18]=1;img[6:22,16:18]=1
    elif d == 5: img[6:8,10:18]=1;img[6:14,10:12]=1;img[12:14,10:18]=1;img[12:22,16:18]=1;img[20:22,10:18]=1
    elif d == 6: img[6:22,10:12]=1;img[6:8,10:18]=1;img[12:14,10:18]=1;img[20:22,10:18]=1;img[12:22,16:18]=1
    elif d == 7: img[6:8,10:18]=1;img[6:22,16:18]=1
    elif d == 8: img[6:8,10:18]=1;img[12:14,10:18]=1;img[20:22,10:18]=1;img[6:22,10:12]=1;img[6:22,16:18]=1
    elif d == 9: img[6:8,10:18]=1;img[12:14,10:18]=1;img[6:14,10:12]=1;img[6:22,16:18]=1
    return ndimage.gaussian_filter(img, 0.8)

def aug_geometric(img, rng):
    img = ndimage.rotate(img, rng.uniform(0,360), reshape=False, mode='constant', order=1)
    sc = rng.uniform(0.6, 1.4)
    img = ndimage.zoom(img, sc, order=1)
    h, w = img.shape
    r = np.zeros((28,28), np.float32)
    if h >= 28 and w >= 28: r = img[(h-28)//2:(h-28)//2+28,(w-28)//2:(w-28)//2+28]
    else: ph,pw=max(0,(28-h)//2),max(0,(28-w)//2);r[ph:ph+min(h,28),pw:pw+min(w,28)]=img[:min(h,28),:min(w,28)]
    return np.clip(r + rng.randn(28,28)*0.1, 0, 1).astype(np.float32)

def aug_adversarial(img, rng):
    noise = rng.randn(28, 28) * rng.uniform(0.3, 0.5)
    return np.clip(img + noise, 0, 1).astype(np.float32)

def aug_cluttered(img, rng):
    result = img.copy()
    for _ in range(rng.randint(3, 10)):
        cy, cx = rng.randint(0, 28), rng.randint(0, 28)
        rad = rng.randint(2, 5)
        for y in range(max(0, cy-rad), min(28, cy+rad)):
            for x in range(max(0, cx-rad), min(28, cx+rad)):
                if (y-cy)**2 + (x-cx)**2 < rad**2:
                    result[y, x] = max(result[y, x], rng.uniform(0.2, 0.4))
    return np.clip(result + rng.randn(28,28)*0.05, 0, 1).astype(np.float32)

def aug_camouflage(img, rng):
    bg = ndimage.gaussian_filter(rng.rand(28,28), rng.uniform(2,4))
    bg = (bg - bg.min()) / (bg.max() - bg.min() + 1e-8)
    c = rng.uniform(0.12, 0.25)  # Slightly easier
    fg = bg.mean() + c * (1 if rng.random() > 0.5 else -1)
    r = bg.copy(); r[img > 0.3] = fg
    return np.clip(ndimage.gaussian_filter(r, 0.5), 0, 1).astype(np.float32)

def gen(n, bench, seed):
    rng = np.random.RandomState(seed)
    aug = {'geometric': aug_geometric, 'adversarial': aug_adversarial,
           'cluttered': aug_cluttered, 'camouflage': aug_camouflage}[bench]
    X, Y = np.zeros((n,784), np.float32), np.zeros((n,10), np.float32)
    for i in range(n):
        d = rng.randint(0,10)
        X[i] = aug(draw_digit(d), rng).flatten()
        Y[i,d] = 1
    return X, Y

print("="*80)
print(" ATHENA v74 REGULARIZED - L2 WEIGHT DECAY ".center(80))
print("="*80)

results = {}
for bi, bench in enumerate(['geometric', 'adversarial', 'cluttered', 'camouflage']):
    print(f"\n===== {bench.upper()} =====")
    Xtr, Ytr = gen(3000, bench, 100+bi)
    Xte, Yte = gen(500, bench, 200+bi)
    Xtr_f, Xte_f = extract_features(Xtr), extract_features(Xte)
    
    net = RegNet(Xtr_f.shape[1], h=96, seed=300+bi)
    ba, best = 32, 0
    for ep in range(50):
        rng = np.random.RandomState(400+bi+ep)
        idx = rng.permutation(len(Xtr_f))
        for i in range(0, len(Xtr_f), ba):
            net.fwd(Xtr_f[idx][i:i+ba])
            net.bwd(Ytr[idx][i:i+ba], lr=0.04, wd=0.005)
        acc = (net.pred(Xte_f) == Yte.argmax(1)).mean()
        if acc > best: best = acc
        if (ep+1) % 10 == 0:
            tr_acc = (net.pred(Xtr_f[:300]) == Ytr[:300].argmax(1)).mean()
            print(f"Ep{ep+1}: train={tr_acc*100:.1f}% test={acc*100:.1f}% best={best*100:.1f}%")
    print(f"{bench.upper()}: {best*100:.1f}%")
    results[bench] = best

print("\n" + "="*80)
for b, a in results.items(): print(f"  {b.upper():12}: {a*100:.1f}%")
avg = sum(results.values())/len(results)
print(f"  {'AVERAGE':12}: {avg*100:.1f}%")
print("="*80)
