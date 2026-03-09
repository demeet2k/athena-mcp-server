#!/usr/bin/env bash
set -euo pipefail

# Build helper for Linux/macOS (CPU or CUDA LibTorch).
# Usage:
#   export LIBTORCH=/absolute/path/to/libtorch
#   ./scripts/build_linux.sh
#
# The CMake command uses CMAKE_PREFIX_PATH to find TorchConfig.cmake.

if [[ -z "${LIBTORCH:-}" ]]; then
  echo "ERROR: Please set LIBTORCH to the directory where you extracted libtorch."
  echo "Example: export LIBTORCH=$HOME/libtorch"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${ROOT_DIR}/build"

mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

cmake -DCMAKE_PREFIX_PATH="${LIBTORCH}" -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release -j
echo "[OK] Build finished. Binaries are in: ${BUILD_DIR}"
