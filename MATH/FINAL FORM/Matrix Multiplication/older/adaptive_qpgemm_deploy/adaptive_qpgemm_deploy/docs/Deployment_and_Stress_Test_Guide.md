# Adaptive QP-GEMM Deployment & Stress-Test Guide (Vision-Tuned)

Version: 1.0  
Generated: 2025-12-23

---

## 0) What you get in this pack

This pack includes everything needed to:

1. **Optimize** a vision-style model by replacing selected `nn.Linear` layers with `QPLinear`.
2. **Export** the optimized model to a TorchScript `.pt` artifact with embedded metadata.
3. **Deploy** the `.pt` artifact in a **high-performance C++ environment** using LibTorch.
4. **Stress test** correctness, stability, and performance in both Python and C++.

---

## 1) Framework overview (Sigma / Omega / Psi / Delta)

### Sigma (Probing)
Per `nn.Linear` weight matrix `W` (shape: `[out_features, in_features]`), we run SVD:

`W = U diag(S) Vh`

### Omega (Tuning)
We select the smallest rank `r` such that cumulative spectral energy meets a threshold.

- Default energy mode in this pack: cumulative sum of singular values ("sv")
- Optional energy mode: cumulative sum of squared singular values ("sv2")

### Psi (Representation)
We store a low-rank approximation as two “skinny” matrices:

- `U_ = U_r * sqrt(S_r)`    shape `[out, r]`
- `V_ = sqrt(S_r) * Vh_r`   shape `[r, in]`

### Delta (Decision)
We only apply low-rank if the theoretical multiply-add proxy is reduced enough:

- Dense proxy: `out * in`
- Low-rank proxy: `r * (out + in)`
- Apply if: `lowrank_proxy <= (1 - min_gain) * dense_proxy`

---

## 2) Python environment setup

### 2.1 Prerequisites

- Python 3.10+ recommended
- A PyTorch build that matches the target deployment runtime (CPU or CUDA)

### 2.2 Install

From the repository root:

```bash
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3) Export TorchScript `.pt` artifacts (Python)

### 3.1 Export optimized model + metadata

```bash
cd python
python export_torchscript.py \
  --out_dir artifacts \
  --threshold 0.99 \
  --energy_mode sv \
  --min_gain 0.30 \
  --freeze \
  --save_baseline
```

Outputs:
- `artifacts/vision_model_qpgemm.pt`  (optimized)
- `artifacts/vision_model_dense.pt`   (optional baseline)
- `artifacts/qpgemm_meta.json`
- `artifacts/qpgemm_layer_report.json`

### 3.2 What’s inside the `.pt` artifact?

The optimized `.pt` includes embedded extra files:

- `qpgemm_meta.json`
- `qpgemm_layer_report.json`

C++ can read these via `torch::jit::ExtraFilesMap`.

---

## 4) Python benchmarking & stress testing

### 4.1 Benchmark (latency + error)

```bash
cd python
python benchmark.py \
  --load_pt artifacts/vision_model_qpgemm.pt \
  --baseline_pt artifacts/vision_model_dense.pt \
  --device cpu \
  --batch 32 \
  --iters 200
```

### 4.2 Thorough stress test sweep

```bash
cd python
python stress_test_qpgemm.py \
  --pt artifacts/vision_model_qpgemm.pt \
  --baseline_pt artifacts/vision_model_dense.pt \
  --device cpu \
  --batch_list 1,4,8,16,32,64,128 \
  --input_size 2048 \
  --iters 200
```

### 4.3 Rank-selection validation

This validates the Sigma/Omega rank decisions per layer:

```bash
cd python
python validate_rank_selection.py --threshold 0.99 --energy_mode sv
```

---

## 5) C++ deployment (LibTorch)

### 5.1 Key rule: version matching

**LibTorch version must match the PyTorch version used to export** your `.pt`.

If they differ, you may see load errors or silent performance differences.

### 5.2 Acquire LibTorch

Download the LibTorch distribution (CPU or CUDA build) that matches your version and platform.

### 5.3 Build (Linux)

```bash
cd cpp
export LIBTORCH=/absolute/path/to/libtorch
./scripts/build_linux.sh
```

Binaries are placed in `cpp/build/`:
- `qpgemm_infer`
- `qpgemm_stress`

### 5.4 Build (Windows)

```powershell
cd cpp
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -LibTorchPath "C:\path\to\libtorch"
```

### 5.5 Run inference benchmark (C++)

```bash
./cpp/build/qpgemm_infer ./python/artifacts/vision_model_qpgemm.pt 32 2048 20 200 cpu 0 0 0
```

Arguments:
1. model path
2. batch
3. input_size
4. warmup
5. iters
6. device: cpu|cuda
7. intra_threads (0 = default)
8. interop_threads (0 = default)
9. jit_opt (0|1) -> apply `optimize_for_inference` in-memory

### 5.6 Run stress test (C++)

```bash
./cpp/build/qpgemm_stress ./python/artifacts/vision_model_qpgemm.pt 60 8 32 2048 cpu 1 1 0 5000 5
```

Arguments:
1. model path
2. seconds
3. workers
4. batch
5. input_size
6. device: cpu|cuda
7. intra_threads
8. interop_threads
9. jit_opt
10. sample_size (reservoir sample cap per thread)
11. report_every_s

---

## 6) High-performance tuning guidance (practical)

### 6.1 Threading

If your serving process is itself multi-threaded (one thread per request), a common best practice is:
- set LibTorch intra-op threads to **1**
- set inter-op threads to **1**
- scale by running more independent workers

This avoids oversubscription (too many threads competing for cores).

### 6.2 Pinning & NUMA

For production:
- pin worker threads to cores
- keep memory local (NUMA-aware scheduling)
- avoid moving modules/tensors across devices at runtime

### 6.3 jemalloc (long-run stability)

For long soak tests, memory fragmentation can become visible.
Consider `jemalloc` on Linux and validate RSS stability with your workload.

---

## 7) Troubleshooting checklist

### `.pt` fails to load in C++
- Confirm PyTorch and LibTorch versions match.
- Confirm the `.pt` is a TorchScript artifact (`torch.jit.save`).
- Confirm CPU vs CUDA build matches your target device.

### Latency is worse than baseline
- Ensure you are not oversubscribed (try `intra_threads=1` and `interop_threads=1`)
- Check that rank selections actually reduce proxy cost
- Verify the model is in eval mode and you use inference mode/no-grad
- Profile: low-rank can be slower if the chosen rank is not small enough, or if the backend
  doesn't hit optimized GEMM kernels for the skinny matrices.

### Accuracy regression
- Increase `energy_threshold` (e.g., 0.995)
- Use `energy_mode=sv2` (Frobenius energy) for more conservative ranks
- Increase `min_rank`
- Exclude sensitive layers from replacement (edit `optimize_vision_model` recursion)

---

## 8) Next hardening steps (production-ready)

- Add per-layer allow/deny lists (replace only some layers).
- Calibrate rank threshold using a validation dataset (task-level metrics).
- Add automated regression tests in CI:
  - load `.pt`, run deterministic inputs, compare outputs
  - measure latency distribution on representative hardware
- Add structured logging of:
  - chosen ranks per layer
  - predicted proxy gain vs measured latency gain
