# Adaptive QP-GEMM Deployment & Stress-Test Pack (Vision-Tuned)

This repository is a **complete, self-contained deployment pack** for the
**Adaptive QP-GEMM Optimization Framework** (Vision-tuned), including:

- **Python framework implementation** (Sigma/Omega/Psi/Delta poles)
- **TorchScript export pipeline** producing `vision_model_qpgemm.pt`
- **Python benchmarks + stress tests**
- **High-performance C++ (LibTorch) inference + stress tests**
- Optional **Docker templates** for CPU and CUDA environments
- A **PDF deployment guide** (generated in this pack)

---

## Directory layout

```
adaptive_qpgemm_deploy/
  docs/
    Adaptive_QP_GEMM_Deployment_Guide.pdf
    Deployment_and_Stress_Test_Guide.md
  python/
    qpgemm.py
    export_torchscript.py
    benchmark.py
    stress_test_qpgemm.py
    validate_rank_selection.py
    requirements.txt
    tests/
  cpp/
    CMakeLists.txt
    src/
      qpgemm_infer.cpp
      qpgemm_stress.cpp
    scripts/
      build_linux.sh
      build_windows.ps1
  docker/
    Dockerfile.cpu
    Dockerfile.cuda
    README.md
```

---

## Quick start (Python)

```bash
cd python
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Export artifacts (includes embedded metadata in the `.pt`):

```bash
python export_torchscript.py --out_dir artifacts --threshold 0.99 --freeze --save_baseline
```

Benchmark:

```bash
python benchmark.py --load_pt artifacts/vision_model_qpgemm.pt --baseline_pt artifacts/vision_model_dense.pt
```

Stress test:

```bash
python stress_test_qpgemm.py --pt artifacts/vision_model_qpgemm.pt --baseline_pt artifacts/vision_model_dense.pt
```

---

## Quick start (C++ / LibTorch)

See `docs/Adaptive_QP_GEMM_Deployment_Guide.pdf` for step-by-step setup and
troubleshooting.

Linux build (example):

```bash
cd cpp
mkdir -p build && cd build
cmake -DCMAKE_PREFIX_PATH=/path/to/libtorch ..
cmake --build . --config Release
./qpgemm_infer ../../python/artifacts/vision_model_qpgemm.pt 32 2048
```

---

## Notes

- **TorchScript deprecation notice:** PyTorch has announced that TorchScript is
  deprecated in favor of `torch.export`, but TorchScript/LibTorch remains a
  practical deployment path if you already have `.pt` artifacts.
- Always match **LibTorch version** to the **PyTorch version** used to export.
