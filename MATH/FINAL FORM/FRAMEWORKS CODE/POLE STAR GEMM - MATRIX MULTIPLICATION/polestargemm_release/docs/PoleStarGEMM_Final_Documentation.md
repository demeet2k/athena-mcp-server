# PoleStarGEMM — Final Documentation (v1.0)

## 0. What this is

**PoleStarGEMM** is a *Quad-Polar* optimization toolkit that targets two related problems:

1. **Adaptive GEMM**: choosing the best way to compute `A @ B` in NumPy when the workload suggests
   structure (low-rank, sparsity) or reuse (noncontiguous inputs repeated many times).

2. **Vision-model layer optimization**: replacing expensive `nn.Linear` layers (and optionally `nn.Conv2d`)
   with low-rank factorizations that preserve a configurable spectral-energy threshold, then exporting to
   TorchScript for **C++/LibTorch** deployment.

The Quad-Polar mental model:

- **Ψ (Psi) — Representation & Reuse**
  - Cached contiguity / packing
  - Cached low-rank factors
  - Optional recursion (Strassen for square power-of-two matrices)
- **Σ (Sigma) — Probing & Exploration**
  - Sketch-based compressibility diagnostics
  - Candidate plan set generation
  - Micro-benchmark driven plan selection
- **Ω (Omega) — Continuous Tuning**
  - Rank selection to satisfy accuracy threshold
  - Rank "bumps" when validation fails
  - Hysteresis to avoid plan thrashing
- **Δ (Delta) — Hard Decisions & Fallbacks**
  - Only accept approximations if they’re predicted to help
  - Validate approximations; fall back to safe BLAS when outside tolerance

---

## 1. Quick start

### 1.1 Install

```bash
cd polestargemm_release/python
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1.2 Quick GEMM benchmark

```bash
python scripts/bench_matmul.py
```

### 1.3 Optimize + export a toy vision MLP

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

---

## 2. The NumPy GEMM Engine

### 2.1 Public API

```python
from polestargemm.core import PoleStarGEMM

engine = PoleStarGEMM()

# Exact BLAS path
res = engine.matmul(A, B, allow_approx=False)

# Approx path (validated)
res = engine.matmul(A, B, allow_approx=True, rtol=1e-2, reuse_a=True)

print(res.plan, res.time_sec, res.approx_error)
C = res.C
```

### 2.2 Plans (what the engine might choose)

- `blas`
  - Default safe plan: `A @ B`
- `contig_blas`
  - One-off conversion to contiguous buffers before BLAS (helps when A/B are noncontiguous)
- `cached_contig_A`, `cached_contig_B`, `cached_contig_AB`
  - Under reuse hints, cache contiguity once and reuse it
- `lowrank_A`, `lowrank_B`
  - Use randomized SVD factors and validate with random-vector checks
  - Uses Ω rank bumps if validation fails (bounded)
  - Protected by Δ gates (won’t attempt if rank becomes too large)
- `sparse` (optional, requires SciPy)
  - Uses CSR sparse kernels when a matrix appears highly sparse
- `strassen` (educational)
  - Only for square power-of-two sizes; often slower in Python, but included for completeness

### 2.3 Stability features you should care about

- **Median micro-bench cost**:
  - Plan selection uses median timing across micro-trials to reduce noise.
- **Δ gating for low-rank**:
  - If the predicted rank implies little or no compute reduction, the engine avoids low-rank plans.
- **Ω hysteresis**:
  - If the previous best plan is within a small margin, the engine sticks with it to avoid thrashing.
- **Validation + fallback**:
  - In approximate mode the engine validates via random-vector probes.
  - If the approximation is outside `rtol`, the engine returns BLAS output.

---

## 3. Vision Optimizer (PyTorch)

### 3.1 What it changes

For each eligible `nn.Linear` (and optionally `nn.Conv2d`), the optimizer:

1. Runs **SVD** (Σ probe)
2. Chooses minimal rank that meets cumulative spectral-energy threshold (Ω tune)
3. Checks predicted compute/parameter savings (Δ gate)
4. Replaces the layer with a factored variant (Ψ representation)

### 3.2 Energy threshold

For singular values `S`:

- **sv2 mode** (recommended): energy = cumulative sum of `S^2` / sum of `S^2`
- sv mode: energy = cumulative sum of `S` / sum of `S`

`sv2` matches Frobenius-norm energy and is generally the right notion for reconstruction quality.

### 3.3 Config knobs

```python
from polestargemm.vision import PoleStarVisionConfig

cfg = PoleStarVisionConfig(
    energy_threshold=0.99,
    energy_mode="sv2",
    min_gain=0.30,
    rank_multiple=8,
    min_rank=1,
    max_rank=None,
    optimize_conv2d=False,
)
```

### 3.4 Optimizing a model

```python
from polestargemm.vision import optimize_model

model_opt, report = optimize_model(model, config=cfg, verbose=True)
print(report.compression_ratio, report.layers_modified)
```

### 3.5 Benchmark and validate drift

```python
from polestargemm.vision import benchmark_model, validate_relative_error

example = torch.randn(32, 2048)
b0 = benchmark_model(model, example, device="cpu")
b1 = benchmark_model(model_opt, example, device="cpu")
err = validate_relative_error(model, model_opt, example, samples=10)
```

---

## 4. TorchScript export

```python
from polestargemm.vision import export_torchscript

ts_path = export_torchscript(model_opt, example, "vision_polestargemm.pt", method="trace")
```

Recommendations:

- Use **trace** when the model has mostly static control flow.
- Use **script** if the model has data-dependent branches (may require code changes).

---

## 5. C++ / LibTorch deployment

### 5.1 Build

```bash
cd polestargemm_release/cpp
export LIBTORCH=/absolute/path/to/libtorch

mkdir -p build && cd build
cmake -DCMAKE_PREFIX_PATH=${LIBTORCH} ..
cmake --build . --config Release
```

### 5.2 Load and run

```bash
./polestargemm_infer /path/to/model.pt 32 2048 20 200 cpu 0 0 0
```

### 5.3 Stress test

```bash
./polestargemm_stress /path/to/model.pt 60 8 32 2048 cpu 1 1 0 5000 5
```

---

## 6. Practical tuning & performance notes

### 6.1 When low-rank helps most

- Large square-ish Linear layers (e.g., 2048x2048) that are genuinely compressible
- Repeated inference (batching or repeated single-image requests)
- CPU deployments where matmul dominates and memory bandwidth is a bottleneck

### 6.2 When low-rank may not help

- Very small layers (overhead dominates)
- Matrices with flat spectra (random-like weights)
- GPU paths where vendor GEMM kernels are already optimal and the extra matmul can be slower

### 6.3 Suggested workflow

1. Optimize offline (SVD can be expensive)
2. Export TorchScript
3. Benchmark in C++ with your thread settings
4. Validate drift (task accuracy, not just relative output error)
5. Lock config (threshold/min_gain) and deploy

---

## 7. Troubleshooting

- **No speedup**: your model may not be compressible, or BLAS is already optimal.
  Raise `min_gain` to avoid replacing marginal layers.
- **High error**: raise `energy_threshold`, lower `rank_multiple`, or disable conv2d optimization.
- **TorchScript fails**: try `method="script"` or simplify model control flow.
- **LibTorch ABI issues**: ensure your compiler + LibTorch build match your environment.

---

## 8. API reference (short)

- `polestargemm.core.PoleStarGEMM`
  - `matmul(A,B, allow_approx, rtol, reuse_a, reuse_b, ...) -> PlanResult`
  - `compile(A,B, ...) -> CompiledGEMMPlan`
- `polestargemm.vision.optimize_model(model, config, ...) -> (model_opt, report)`
- `polestargemm.vision.export_torchscript(model, example_input, out_path, method)`
