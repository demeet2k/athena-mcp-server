# C++ / LibTorch Deployment (PoleStarGEMM)

This folder contains two executables:

- `polestargemm_infer`: single-thread latency distribution benchmark (p50/p90/p99)
- `polestargemm_stress`: multi-thread stress test with periodic throughput + latency samples

> These tools load a TorchScript `.pt` file produced by `polestargemm.vision.export_torchscript`.

---

## Build (Linux/macOS)

1) Download and extract **LibTorch** (CPU or CUDA build) that matches the PyTorch
   version used to export your `.pt` file.

2) Build:

```bash
export LIBTORCH=/absolute/path/to/libtorch
mkdir -p build && cd build
cmake -DCMAKE_PREFIX_PATH=${LIBTORCH} ..
cmake --build . --config Release
```

---

## Run: inference benchmark

```bash
./polestargemm_infer /path/to/model.pt 32 2048 20 200 cpu 0 0 0
# args:
#   model.pt batch input_size warmup iters device intra_threads interop_threads jit_opt
```

- `device`: `cpu` or `cuda`
- `jit_opt`: `0` (default) or `1` to enable JIT optimizations

---

## Run: stress test

```bash
./polestargemm_stress /path/to/model.pt 60 8 32 2048 cpu 1 1 0 5000 5
# args:
#   model.pt seconds workers batch input_size device intra_threads interop_threads jit_opt sample_size report_every_s
```

---

## Threading guidance (important)

If your serving system already runs many worker threads (one per request), consider:

- Setting `intra_threads=1` to avoid oversubscription.
- Pinning threads / controlling OMP settings in your deployment container/host.

If your system is single-process and you want maximum throughput from a single model instance,
increase `intra_threads` (e.g., number of physical cores) and keep inter-op low.

---

## Troubleshooting

- **`undefined symbol` / ABI errors**: ensure LibTorch matches your compiler ABI (GCC version),
  and matches the major/minor PyTorch version used to export.
- **CUDA errors**: confirm you downloaded the CUDA-enabled LibTorch build, and your driver/runtime is compatible.
