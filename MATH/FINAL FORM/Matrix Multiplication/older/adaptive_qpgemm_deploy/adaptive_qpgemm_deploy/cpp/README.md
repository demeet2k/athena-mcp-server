# C++ / LibTorch Deployment (Adaptive QP-GEMM)

This folder contains two executables:

- `qpgemm_infer`: single-thread latency distribution benchmark (p50/p90/p99)
- `qpgemm_stress`: multi-thread stress test with periodic throughput + latency samples

## Build (Linux/macOS)

1) Download and extract **LibTorch** (CPU or CUDA build) that matches the
   PyTorch version used to export your `.pt` file.

2) Build:

```bash
export LIBTORCH=/absolute/path/to/libtorch
./scripts/build_linux.sh
```

## Build (Windows)

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build_windows.ps1 -LibTorchPath "C:\path\to\libtorch"
```

## Run

### Infer benchmark

```bash
./qpgemm_infer /path/to/vision_model_qpgemm.pt 32 2048 20 200 cpu 0 0 0
# args: model.pt batch input_size warmup iters device intra_threads interop_threads jit_opt
```

### Stress test

```bash
./qpgemm_stress /path/to/vision_model_qpgemm.pt 60 8 32 2048 cpu 1 1 0 5000 5
# args: model.pt seconds workers batch input_size device intra_threads interop_threads jit_opt sample_size report_every_s
```

## Threading guidance (important)

If your serving system already runs many worker threads (one per request), consider:
- `intra_threads=1`
- `interop_threads=1`

This helps avoid oversubscription (too many threads fighting for the same cores).

## CUDA timing

For `device=cuda`, these tools synchronize around forward() to measure
kernel time accurately. This is slower but gives correct latency numbers.
