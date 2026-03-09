# Docker templates

This folder contains **templates** for CPU and CUDA containers.

Why templates?
- Organizations often have standard base images, proxy settings, and hardening requirements.
- LibTorch download URLs vary by PyTorch version and CUDA version.

## CPU

```bash
docker build -f docker/Dockerfile.cpu -t qpgemm_cpu \
  --build-arg LIBTORCH_URL="<libtorch-cpu-zip-url>" .
docker run --rm -it qpgemm_cpu bash
```

## CUDA

```bash
docker build -f docker/Dockerfile.cuda -t qpgemm_cuda \
  --build-arg LIBTORCH_URL="<libtorch-cuda-zip-url>" .
docker run --rm -it --gpus all qpgemm_cuda bash
```

Inside the container:
- Python scripts are in `/workspace/python`
- C++ binaries are in `/workspace/cpp/build`
