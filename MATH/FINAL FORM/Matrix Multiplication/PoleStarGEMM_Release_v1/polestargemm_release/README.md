# PoleStarGEMM — Quad‑Polar Adaptive GEMM & Vision Optimizer

**PoleStarGEMM** is a practical implementation of the Quad‑Polar idea (Ψ/Σ/Ω/Δ) applied to:

1) **Adaptive GEMM (NumPy)**: a planner + cache + validator around `A @ B`  
2) **Vision model optimization (PyTorch)**: a drop‑in **low‑rank replacement** of large `nn.Linear` layers (and optionally `nn.Conv2d`) with TorchScript export for **C++ (LibTorch)** deployment

> Why “PoleStar”?  
> The framework is built around *four poles* and adaptive “navigation” between strategies.  
> “PoleStar” is the guiding star for those poles (Ψ/Σ/Ω/Δ).

---

## Repository layout

```
polestargemm_release/
  docs/
  python/
    polestargemm/
      core.py          # NumPy adaptive GEMM
      vision.py        # PyTorch vision optimizer + TorchScript export
    scripts/
      bench_matmul.py
      stress_matmul.py
      optimize_and_export_vision.py
    tests/
  cpp/
    src/
    CMakeLists.txt
  docker/
```

---

## 1) Python install (core + vision)

```bash
cd polestargemm_release/python
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
```

### Quick sanity test

```bash
pytest -q
```

---

## 2) Adaptive GEMM (NumPy)

### Minimal usage

```python
import numpy as np
from polestargemm.core import PoleStarGEMM

A = np.random.randn(256, 256)
B = np.random.randn(256, 256)

engine = PoleStarGEMM()

# Exact mode (guaranteed exact up to FP roundoff)
C = engine.matmul(A, B, allow_approx=False).C

# Approx mode (may use low‑rank, but validates; falls back if outside rtol)
C2 = engine.matmul(A, B, allow_approx=True, rtol=1e-2, reuse_a=True).C
```

### Benchmark + ablation

```bash
python scripts/bench_matmul.py
```

### Stress test

```bash
python scripts/stress_matmul.py --out polestargemm_stress.csv --approx --rtol 1e-2
```

---

## 3) Vision model optimization (PyTorch)

### Optimize + benchmark + validate + export TorchScript

Toy MLP (like your 2048‑wide “vision stack”):

```bash
python scripts/optimize_and_export_vision.py \
  --model toy_mlp \
  --input-dim 2048 \
  --batch 32 \
  --energy-threshold 0.99 \
  --energy-mode sv2 \
  --min-gain 0.30 \
  --out vision_polestargemm.pt
```

Torchvision model (requires `torchvision`):

```bash
python scripts/optimize_and_export_vision.py \
  --model resnet18 \
  --image-size 224 \
  --batch 8 \
  --optimize-conv2d \
  --out resnet18_polestargemm.pt
```

---

## 4) C++ (LibTorch) inference

See `cpp/README.md` for detailed setup, CMake, and runtime flags.

At a high level:

```bash
cd polestargemm_release/cpp
mkdir -p build && cd build

cmake -DCMAKE_PREFIX_PATH=/path/to/libtorch ..
cmake --build . --config Release
./polestargemm_infer /path/to/model.pt 32 2048
```

---

## 5) Docker

See `docker/README.md` for CPU/CUDA containers.

---

## Notes / disclaimers

- Low‑rank replacement is **not** a free win. It works best when weights are actually compressible.
- For best performance, benchmark on the target CPU/GPU and set thread counts accordingly.
- TorchScript tracing requires mostly static control flow. Use scripting if your model has data‑dependent branches.
