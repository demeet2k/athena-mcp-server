"""
QP-GEMM Vision Model Optimizer
==============================

Drop-in optimization for any PyTorch vision neural network.
Uses Quad-Polar principles to speed up matrix multiplication.

Usage:
    python qpgemm_vision_optimizer.py --model resnet50 --rank-ratio 0.4
    
Or in your code:
    from qpgemm_vision_optimizer import optimize_model, benchmark_model
    
    model = load_your_model()
    model_fast, report = optimize_model(model, rank_ratio=0.4)

Author: Based on Quad-Polar Framework
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import time
import argparse
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from collections import OrderedDict
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
#  ANALYSIS: Probe matrix structure (Σ pole)
# ============================================================================

@dataclass
class MatrixFingerprint:
    """Complete structural signature of a weight matrix"""
    name: str
    shape: Tuple[int, int]
    sparsity: float           # Fraction of near-zero elements
    rank_ratio: float         # Effective rank / min(m,n)
    spectral_decay: float     # How fast singular values drop
    condition_estimate: float # Ratio of largest to smallest singular value
    dtype: str
    device: str
    
    # Derived recommendations
    recommended_strategy: str
    recommended_rank: int
    estimated_speedup: float
    estimated_error: float


def analyze_matrix(W: torch.Tensor, name: str = "layer", 
                   sample_size: int = 4096, sketch_rank: int = 32) -> MatrixFingerprint:
    """
    Σ Pole: Probe matrix structure using randomized methods.
    Fast analysis that doesn't require full SVD.
    """
    W_2d = W.view(W.size(0), -1) if W.dim() > 2 else W
    m, n = W_2d.shape
    device = W.device
    dtype = W.dtype
    
    # --- Sparsity (sample-based for speed) ---
    flat = W_2d.flatten()
    if flat.numel() > sample_size:
        idx = torch.randperm(flat.numel(), device=device)[:sample_size]
        sample = flat[idx]
    else:
        sample = flat
    sparsity = (sample.abs() < 1e-6).float().mean().item()
    
    # --- Rank estimation via randomized sketch ---
    k = min(sketch_rank, m, n)
    if k >= 2:
        # Random projection
        Omega = torch.randn(n, k, device=device, dtype=dtype)
        Y = W_2d @ Omega
        
        try:
            # QR for numerical stability
            Q, _ = torch.linalg.qr(Y, mode='reduced')
            B = Q.T @ W_2d
            s = torch.linalg.svdvals(B)
            
            # Spectral analysis
            s_normalized = s / (s[0] + 1e-12)
            
            # Effective rank: how many singular values are "significant"
            threshold = 0.01
            effective_rank = (s_normalized > threshold).sum().item()
            rank_ratio = effective_rank / min(m, n)
            
            # Spectral decay: how fast do singular values drop?
            if len(s) >= 4:
                decay = (s[0] / (s[len(s)//4] + 1e-12)).item()
            else:
                decay = 1.0
            
            # Condition estimate
            condition = (s[0] / (s[-1] + 1e-12)).item()
            
        except Exception:
            rank_ratio = 1.0
            decay = 1.0
            condition = 1.0
    else:
        rank_ratio = 1.0
        decay = 1.0
        condition = 1.0
    
    # --- Strategy recommendation ---
    strategy, rank, speedup, error = _recommend_strategy(
        m, n, sparsity, rank_ratio, decay
    )
    
    return MatrixFingerprint(
        name=name,
        shape=(m, n),
        sparsity=sparsity,
        rank_ratio=rank_ratio,
        spectral_decay=decay,
        condition_estimate=condition,
        dtype=str(dtype),
        device=str(device),
        recommended_strategy=strategy,
        recommended_rank=rank,
        estimated_speedup=speedup,
        estimated_error=error
    )


def _recommend_strategy(m: int, n: int, sparsity: float, 
                        rank_ratio: float, decay: float) -> Tuple[str, int, float, float]:
    """
    Ω Pole: Tune strategy selection based on matrix characteristics.
    Returns: (strategy, rank, estimated_speedup, estimated_error)
    """
    min_dim = min(m, n)
    max_dim = max(m, n)
    
    # Sparse strategy
    if sparsity > 0.8:
        # Sparse matmul wins when >80% zeros
        speedup = 1.0 / (1.0 - sparsity + 0.1)  # Rough estimate
        return ("sparse", 0, speedup, 0.0)
    
    # Low-rank strategy
    if rank_ratio < 0.4 and min_dim >= 64:
        # Effective rank is low, decomposition will help
        rank = max(4, int(min_dim * rank_ratio * 1.2))  # Slight overestimate for safety
        
        # Speedup: O(mn) -> O(mr + rn) = O(r(m+n))
        original_ops = m * n
        new_ops = rank * (m + n)
        speedup = original_ops / new_ops
        
        # Error estimate based on spectral decay
        error = 0.01 / decay if decay > 1 else 0.05
        
        return ("lowrank", rank, speedup, error)
    
    # Dense (BLAS) - no change
    return ("dense", 0, 1.0, 0.0)


# ============================================================================
#  OPTIMIZED LAYERS: Replacement modules
# ============================================================================

class QPLinear(nn.Module):
    """
    Quad-Polar optimized Linear layer.
    
    Ψ (Structure): Caches SVD factors for low-rank weights
    D (Direct): Uses appropriate kernel (sparse/dense/factored)
    """
    
    def __init__(self, original: nn.Linear, fingerprint: MatrixFingerprint):
        super().__init__()
        
        self.in_features = original.in_features
        self.out_features = original.out_features
        self.fingerprint = fingerprint
        self.strategy = fingerprint.recommended_strategy
        
        W = original.weight.data
        
        if self.strategy == "lowrank":
            # Ψ: Decompose and cache factors
            rank = fingerprint.recommended_rank
            U, S, Vt = torch.linalg.svd(W, full_matrices=False)
            
            sqrt_S = torch.sqrt(S[:rank])
            self.U = nn.Parameter(U[:, :rank] * sqrt_S, requires_grad=False)
            self.V = nn.Parameter(sqrt_S.unsqueeze(1) * Vt[:rank, :], requires_grad=False)
            self.rank = rank
            
        elif self.strategy == "sparse":
            # D: Store as sparse tensor
            self.W_sparse = nn.Parameter(W.to_sparse_csr(), requires_grad=False)
            
        else:  # dense
            self.weight = nn.Parameter(W, requires_grad=False)
        
        # Bias
        if original.bias is not None:
            self.bias = nn.Parameter(original.bias.data.clone(), requires_grad=False)
        else:
            self.register_parameter('bias', None)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.strategy == "lowrank":
            # Two smaller matmuls: x @ W.T = x @ V.T @ U.T
            out = x @ self.V.T
            out = out @ self.U.T
            
        elif self.strategy == "sparse":
            # Sparse matmul
            out = torch.sparse.mm(self.W_sparse, x.T).T
            
        else:
            out = F.linear(x, self.weight, None)
        
        if self.bias is not None:
            out = out + self.bias
        
        return out
    
    def extra_repr(self) -> str:
        return (f"in={self.in_features}, out={self.out_features}, "
                f"strategy={self.strategy}" + 
                (f", rank={self.rank}" if self.strategy == "lowrank" else ""))


class QPConv2d(nn.Module):
    """
    Quad-Polar optimized Conv2d layer.
    
    Decomposes convolution when beneficial:
    - Standard conv: [out, in, kH, kW] weights
    - Factored: Two convolutions with smaller kernels
    """
    
    def __init__(self, original: nn.Conv2d, fingerprint: MatrixFingerprint):
        super().__init__()
        
        self.in_channels = original.in_channels
        self.out_channels = original.out_channels
        self.kernel_size = original.kernel_size
        self.stride = original.stride
        self.padding = original.padding
        self.dilation = original.dilation
        self.groups = original.groups
        self.fingerprint = fingerprint
        self.strategy = fingerprint.recommended_strategy
        
        W = original.weight.data  # [out_ch, in_ch/groups, kH, kW]
        
        if self.strategy == "lowrank" and self.groups == 1:
            # Decompose into two convolutions
            # Reshape to 2D: [out_ch, in_ch * kH * kW]
            out_ch, in_ch, kH, kW = W.shape
            W_2d = W.view(out_ch, -1)
            
            rank = fingerprint.recommended_rank
            U, S, Vt = torch.linalg.svd(W_2d, full_matrices=False)
            
            sqrt_S = torch.sqrt(S[:rank])
            
            # First conv: [in_ch, kH, kW] -> [rank, 1, 1] (effectively)
            # We do: [in_ch, kH, kW] -> [rank] using reshaped weights
            V_weights = (sqrt_S.unsqueeze(1) * Vt[:rank, :]).view(rank, in_ch, kH, kW)
            
            # Second conv: [rank] -> [out_ch] using 1x1 conv
            U_weights = (U[:, :rank] * sqrt_S).view(out_ch, rank, 1, 1)
            
            self.conv1 = nn.Conv2d(
                in_ch, rank, (kH, kW),
                stride=self.stride, padding=self.padding,
                dilation=self.dilation, bias=False
            )
            self.conv1.weight = nn.Parameter(V_weights, requires_grad=False)
            
            self.conv2 = nn.Conv2d(rank, out_ch, (1, 1), bias=False)
            self.conv2.weight = nn.Parameter(U_weights, requires_grad=False)
            
            self.rank = rank
            
        else:
            # Keep original conv
            self.strategy = "dense"
            self.conv = nn.Conv2d(
                self.in_channels, self.out_channels, self.kernel_size,
                stride=self.stride, padding=self.padding,
                dilation=self.dilation, groups=self.groups, bias=False
            )
            self.conv.weight = nn.Parameter(W, requires_grad=False)
        
        # Bias
        if original.bias is not None:
            self.bias = nn.Parameter(original.bias.data.clone(), requires_grad=False)
        else:
            self.register_parameter('bias', None)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if self.strategy == "lowrank":
            out = self.conv1(x)
            out = self.conv2(out)
        else:
            out = self.conv(x)
        
        if self.bias is not None:
            out = out + self.bias.view(1, -1, 1, 1)
        
        return out
    
    def extra_repr(self) -> str:
        return (f"in={self.in_channels}, out={self.out_channels}, "
                f"kernel={self.kernel_size}, strategy={self.strategy}" +
                (f", rank={self.rank}" if self.strategy == "lowrank" else ""))


# ============================================================================
#  MODEL OPTIMIZATION: Main entry point
# ============================================================================

@dataclass
class OptimizationReport:
    """Summary of optimization results"""
    original_params: int
    optimized_params: int
    compression_ratio: float
    layers_modified: int
    layers_total: int
    layer_reports: List[Dict[str, Any]]
    estimated_speedup: float


def optimize_model(
    model: nn.Module,
    rank_ratio: float = 0.4,
    min_size: int = 64,
    skip_layers: Optional[List[str]] = None,
    verbose: bool = True
) -> Tuple[nn.Module, OptimizationReport]:
    """
    Optimize a PyTorch model using QP-GEMM principles.
    
    Args:
        model: The neural network to optimize
        rank_ratio: Target rank as fraction of min(m,n) for low-rank layers
        min_size: Minimum layer size to consider for optimization  
        skip_layers: List of layer names to skip
        verbose: Print optimization progress
    
    Returns:
        (optimized_model, report)
    """
    
    if skip_layers is None:
        skip_layers = []
    
    # Put model in eval mode
    model = model.eval()
    
    # Collect stats
    original_params = sum(p.numel() for p in model.parameters())
    layer_reports = []
    layers_modified = 0
    layers_total = 0
    total_speedup = 0.0
    
    if verbose:
        print("=" * 70)
        print("QP-GEMM MODEL OPTIMIZER")
        print("=" * 70)
        print(f"Target rank ratio: {rank_ratio}")
        print(f"Minimum layer size: {min_size}")
        print("-" * 70)
    
    # Recursive optimization
    def optimize_module(module: nn.Module, prefix: str = ""):
        nonlocal layers_modified, layers_total, total_speedup
        
        for name, child in list(module.named_children()):
            full_name = f"{prefix}.{name}" if prefix else name
            
            # Skip if in skip list
            if any(skip in full_name for skip in skip_layers):
                if verbose:
                    print(f"  SKIP: {full_name}")
                continue
            
            # Optimize Linear layers
            if isinstance(child, nn.Linear):
                layers_total += 1
                
                # Check size threshold
                if child.in_features < min_size and child.out_features < min_size:
                    if verbose:
                        print(f"  KEEP: {full_name} (too small: {child.in_features}x{child.out_features})")
                    continue
                
                # Analyze
                fp = analyze_matrix(child.weight.data, name=full_name)
                
                # Override rank if using low-rank strategy
                if fp.recommended_strategy == "lowrank":
                    min_dim = min(child.in_features, child.out_features)
                    fp.recommended_rank = max(4, int(min_dim * rank_ratio))
                
                # Create optimized layer
                if fp.recommended_strategy != "dense":
                    optimized = QPLinear(child, fp)
                    setattr(module, name, optimized)
                    layers_modified += 1
                    total_speedup += fp.estimated_speedup
                    
                    layer_reports.append({
                        "name": full_name,
                        "type": "Linear",
                        "shape": fp.shape,
                        "strategy": fp.recommended_strategy,
                        "rank": fp.recommended_rank if fp.recommended_strategy == "lowrank" else None,
                        "speedup": fp.estimated_speedup,
                        "sparsity": fp.sparsity,
                        "rank_ratio": fp.rank_ratio
                    })
                    
                    if verbose:
                        print(f"  OPT:  {full_name} | {fp.shape} | {fp.recommended_strategy} "
                              f"| rank={fp.recommended_rank} | ~{fp.estimated_speedup:.1f}x")
                else:
                    if verbose:
                        print(f"  KEEP: {full_name} | {fp.shape} | dense (no benefit)")
            
            # Optimize Conv2d layers
            elif isinstance(child, nn.Conv2d):
                layers_total += 1
                
                W = child.weight.data
                out_ch, in_ch, kH, kW = W.shape
                
                # Check size
                effective_size = out_ch * in_ch * kH * kW
                if effective_size < min_size * min_size:
                    if verbose:
                        print(f"  KEEP: {full_name} (too small)")
                    continue
                
                # Analyze as 2D matrix
                W_2d = W.view(out_ch, -1)
                fp = analyze_matrix(W_2d, name=full_name)
                
                # Override rank
                if fp.recommended_strategy == "lowrank":
                    min_dim = min(W_2d.shape)
                    fp.recommended_rank = max(4, int(min_dim * rank_ratio))
                
                # Create optimized layer
                if fp.recommended_strategy == "lowrank" and child.groups == 1:
                    optimized = QPConv2d(child, fp)
                    setattr(module, name, optimized)
                    layers_modified += 1
                    total_speedup += fp.estimated_speedup
                    
                    layer_reports.append({
                        "name": full_name,
                        "type": "Conv2d", 
                        "shape": (out_ch, in_ch, kH, kW),
                        "strategy": fp.recommended_strategy,
                        "rank": fp.recommended_rank,
                        "speedup": fp.estimated_speedup,
                        "sparsity": fp.sparsity,
                        "rank_ratio": fp.rank_ratio
                    })
                    
                    if verbose:
                        print(f"  OPT:  {full_name} | Conv {out_ch}x{in_ch}x{kH}x{kW} | lowrank "
                              f"| rank={fp.recommended_rank} | ~{fp.estimated_speedup:.1f}x")
                else:
                    if verbose:
                        print(f"  KEEP: {full_name} | Conv | dense")
            
            # Recurse into child modules
            elif len(list(child.children())) > 0:
                optimize_module(child, full_name)
    
    # Run optimization
    optimize_module(model)
    
    # Calculate final stats
    optimized_params = sum(p.numel() for p in model.parameters())
    compression = original_params / optimized_params if optimized_params > 0 else 1.0
    avg_speedup = total_speedup / layers_modified if layers_modified > 0 else 1.0
    
    report = OptimizationReport(
        original_params=original_params,
        optimized_params=optimized_params,
        compression_ratio=compression,
        layers_modified=layers_modified,
        layers_total=layers_total,
        layer_reports=layer_reports,
        estimated_speedup=avg_speedup
    )
    
    if verbose:
        print("-" * 70)
        print(f"SUMMARY:")
        print(f"  Layers optimized: {layers_modified}/{layers_total}")
        print(f"  Parameters: {original_params:,} → {optimized_params:,} ({compression:.2f}x compression)")
        print(f"  Estimated speedup: ~{avg_speedup:.1f}x average for optimized layers")
        print("=" * 70)
    
    return model, report


# ============================================================================
#  BENCHMARKING: Measure actual performance
# ============================================================================

def benchmark_model(
    model: nn.Module,
    input_shape: Tuple[int, ...],
    warmup: int = 10,
    iterations: int = 100,
    device: str = "cpu"
) -> Dict[str, float]:
    """
    Benchmark model inference time.
    
    Args:
        model: The model to benchmark
        input_shape: Shape of input tensor (e.g., (1, 3, 224, 224) for images)
        warmup: Number of warmup iterations
        iterations: Number of timed iterations
        device: Device to run on ("cpu" or "cuda")
    
    Returns:
        Dict with timing statistics
    """
    model = model.to(device).eval()
    x = torch.randn(*input_shape, device=device)
    
    # Warmup
    with torch.no_grad():
        for _ in range(warmup):
            _ = model(x)
    
    # Synchronize if CUDA
    if device == "cuda":
        torch.cuda.synchronize()
    
    # Timed runs
    times = []
    with torch.no_grad():
        for _ in range(iterations):
            t0 = time.perf_counter()
            _ = model(x)
            if device == "cuda":
                torch.cuda.synchronize()
            t1 = time.perf_counter()
            times.append(t1 - t0)
    
    times = np.array(times) * 1000  # Convert to ms
    
    return {
        "mean_ms": float(np.mean(times)),
        "std_ms": float(np.std(times)),
        "min_ms": float(np.min(times)),
        "max_ms": float(np.max(times)),
        "median_ms": float(np.median(times)),
        "iterations": iterations
    }


def validate_accuracy(
    model_original: nn.Module,
    model_optimized: nn.Module,
    input_shape: Tuple[int, ...],
    num_samples: int = 10,
    device: str = "cpu"
) -> Dict[str, float]:
    """
    Validate that optimized model produces similar outputs.
    
    Returns:
        Dict with error statistics
    """
    model_original = model_original.to(device).eval()
    model_optimized = model_optimized.to(device).eval()
    
    errors = []
    
    with torch.no_grad():
        for _ in range(num_samples):
            x = torch.randn(*input_shape, device=device)
            
            out_orig = model_original(x)
            out_opt = model_optimized(x)
            
            # Relative error
            diff = (out_orig - out_opt).abs()
            denom = out_orig.abs().mean() + 1e-8
            rel_err = (diff.mean() / denom).item()
            errors.append(rel_err)
    
    errors = np.array(errors)
    
    return {
        "mean_relative_error": float(np.mean(errors)),
        "max_relative_error": float(np.max(errors)),
        "std_relative_error": float(np.std(errors))
    }


# ============================================================================
#  COMPLETE PIPELINE: Optimize and validate
# ============================================================================

def full_optimization_pipeline(
    model: nn.Module,
    input_shape: Tuple[int, ...],
    rank_ratio: float = 0.4,
    device: str = "cpu",
    benchmark_iterations: int = 50
) -> Tuple[nn.Module, Dict[str, Any]]:
    """
    Complete optimization pipeline with benchmarking and validation.
    
    Args:
        model: Original model
        input_shape: Input tensor shape
        rank_ratio: Target rank ratio
        device: Device to run on
        benchmark_iterations: Number of benchmark iterations
    
    Returns:
        (optimized_model, full_report)
    """
    import copy
    
    print("\n" + "=" * 70)
    print("  QP-GEMM FULL OPTIMIZATION PIPELINE")
    print("=" * 70 + "\n")
    
    # Keep original for comparison
    model_original = copy.deepcopy(model)
    
    # Step 1: Optimize
    print("STEP 1: Optimizing model...")
    model_optimized, opt_report = optimize_model(
        model, rank_ratio=rank_ratio, verbose=True
    )
    
    # Step 2: Benchmark original
    print("\nSTEP 2: Benchmarking original model...")
    bench_original = benchmark_model(
        model_original, input_shape, 
        iterations=benchmark_iterations, device=device
    )
    print(f"  Original: {bench_original['mean_ms']:.2f} ± {bench_original['std_ms']:.2f} ms")
    
    # Step 3: Benchmark optimized
    print("\nSTEP 3: Benchmarking optimized model...")
    bench_optimized = benchmark_model(
        model_optimized, input_shape,
        iterations=benchmark_iterations, device=device
    )
    print(f"  Optimized: {bench_optimized['mean_ms']:.2f} ± {bench_optimized['std_ms']:.2f} ms")
    
    # Calculate actual speedup
    actual_speedup = bench_original['mean_ms'] / bench_optimized['mean_ms']
    print(f"  Actual speedup: {actual_speedup:.2f}x")
    
    # Step 4: Validate accuracy
    print("\nSTEP 4: Validating accuracy...")
    accuracy = validate_accuracy(
        model_original, model_optimized, input_shape,
        num_samples=20, device=device
    )
    print(f"  Mean relative error: {accuracy['mean_relative_error']:.2e}")
    print(f"  Max relative error: {accuracy['max_relative_error']:.2e}")
    
    # Final report
    full_report = {
        "optimization": opt_report,
        "benchmark_original": bench_original,
        "benchmark_optimized": bench_optimized,
        "actual_speedup": actual_speedup,
        "accuracy": accuracy
    }
    
    print("\n" + "=" * 70)
    print("  OPTIMIZATION COMPLETE")
    print("=" * 70)
    print(f"""
    Parameters:     {opt_report.original_params:,} → {opt_report.optimized_params:,}
    Compression:    {opt_report.compression_ratio:.2f}x
    Layers changed: {opt_report.layers_modified}/{opt_report.layers_total}
    
    Inference time: {bench_original['mean_ms']:.2f} ms → {bench_optimized['mean_ms']:.2f} ms
    ACTUAL SPEEDUP: {actual_speedup:.2f}x
    
    Accuracy loss:  {accuracy['mean_relative_error']:.2e} (relative)
    """)
    print("=" * 70 + "\n")
    
    return model_optimized, full_report


# ============================================================================
#  CLI INTERFACE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="QP-GEMM Vision Model Optimizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Optimize ResNet50
    python qpgemm_vision_optimizer.py --model resnet50 --rank-ratio 0.4
    
    # Optimize with custom input size
    python qpgemm_vision_optimizer.py --model efficientnet_b0 --input-size 256
    
    # Use GPU
    python qpgemm_vision_optimizer.py --model resnet18 --device cuda
        """
    )
    
    parser.add_argument("--model", type=str, default="resnet18",
                        help="Model architecture (from torchvision or path to .pt file)")
    parser.add_argument("--rank-ratio", type=float, default=0.4,
                        help="Target rank as fraction of min dimension (default: 0.4)")
    parser.add_argument("--input-size", type=int, default=224,
                        help="Input image size (default: 224)")
    parser.add_argument("--batch-size", type=int, default=1,
                        help="Batch size for benchmarking (default: 1)")
    parser.add_argument("--device", type=str, default="cpu",
                        choices=["cpu", "cuda"],
                        help="Device to run on (default: cpu)")
    parser.add_argument("--iterations", type=int, default=50,
                        help="Benchmark iterations (default: 50)")
    parser.add_argument("--save", type=str, default=None,
                        help="Path to save optimized model")
    
    args = parser.parse_args()
    
    # Load model
    print(f"\nLoading model: {args.model}")
    
    if args.model.endswith(".pt") or args.model.endswith(".pth"):
        # Load from file
        model = torch.load(args.model, map_location="cpu")
    else:
        # Load from torchvision
        try:
            import torchvision.models as models
            model_fn = getattr(models, args.model, None)
            if model_fn is None:
                print(f"Error: Unknown model '{args.model}'")
                print("Available models:", [m for m in dir(models) if not m.startswith('_')])
                return
            model = model_fn(pretrained=True)
        except Exception as e:
            print(f"Error loading model: {e}")
            return
    
    # Input shape
    input_shape = (args.batch_size, 3, args.input_size, args.input_size)
    
    # Run optimization
    model_optimized, report = full_optimization_pipeline(
        model,
        input_shape=input_shape,
        rank_ratio=args.rank_ratio,
        device=args.device,
        benchmark_iterations=args.iterations
    )
    
    # Save if requested
    if args.save:
        torch.save(model_optimized.state_dict(), args.save)
        print(f"Saved optimized model to: {args.save}")


# ============================================================================
#  DEMO
# ============================================================================

def demo():
    """Quick demo with a simple model"""
    print("\n" + "=" * 70)
    print("  QP-GEMM DEMO")
    print("=" * 70)
    
    # Create a simple test model
    class SimpleVisionModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(3, 64, 7, stride=2, padding=3)
            self.bn1 = nn.BatchNorm2d(64)
            self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
            self.bn2 = nn.BatchNorm2d(128)
            self.conv3 = nn.Conv2d(128, 256, 3, padding=1)
            self.bn3 = nn.BatchNorm2d(256)
            self.pool = nn.AdaptiveAvgPool2d(1)
            self.fc1 = nn.Linear(256, 512)
            self.fc2 = nn.Linear(512, 100)
        
        def forward(self, x):
            x = F.relu(self.bn1(self.conv1(x)))
            x = F.max_pool2d(x, 2)
            x = F.relu(self.bn2(self.conv2(x)))
            x = F.max_pool2d(x, 2)
            x = F.relu(self.bn3(self.conv3(x)))
            x = self.pool(x)
            x = x.view(x.size(0), -1)
            x = F.relu(self.fc1(x))
            x = self.fc2(x)
            return x
    
    model = SimpleVisionModel()
    input_shape = (1, 3, 224, 224)
    
    # Run full pipeline
    model_opt, report = full_optimization_pipeline(
        model, 
        input_shape=input_shape,
        rank_ratio=0.4,
        device="cpu",
        benchmark_iterations=30
    )
    
    return model_opt, report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main()
    else:
        # Run demo if no arguments
        print("No arguments provided. Running demo...")
        print("For full usage, run: python qpgemm_vision_optimizer.py --help")
        demo()
