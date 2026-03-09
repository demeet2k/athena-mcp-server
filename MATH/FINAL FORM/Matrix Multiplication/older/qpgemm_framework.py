"""
QP-GEMM: Quad-Polar Matrix Multiplication Framework (v0)

Goal:
- Never claim to beat BLAS "by default".
- Detect structure + reuse and exploit it when it measurably helps.
- Use micro-bench + ablation to avoid adding useless poles.

Poles mapping for GEMM:
- Ψ (Psi): reuse + recursion + representation (packing cache, low-rank factors, block structure)
- Ω (Omega): continuous tuning (rank selection, thresholds, parameter refinement)
- Σ (Sigma): probing (randomized sketches) + plan exploration (micro-bench selection)
- D (Delta): direct execution (BLAS/sparse kernels), hard commits/fallbacks
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple, List, Literal
import numpy as np
import time
import hashlib

try:
    import scipy.sparse as sp
except Exception:  # pragma: no cover
    sp = None


# ----------------------------
# Fingerprint / signature
# ----------------------------

@dataclass(frozen=True)
class GEMMFingerprint:
    m: int
    k: int
    n: int
    dtype: str
    a_contig: bool
    b_contig: bool
    a_sparsity: float
    b_sparsity: float
    a_rank_ratio: float
    b_rank_ratio: float
    allow_approx: bool
    rtol: float
    reuse_a: bool
    reuse_b: bool

    def hash(self) -> str:
        # Bucket sizes to keep cache stable while still specific
        features = (
            (self.m // 64, self.k // 64, self.n // 64),
            self.dtype,
            self.a_contig,
            self.b_contig,
            round(self.a_sparsity, 2),
            round(self.b_sparsity, 2),
            round(self.a_rank_ratio, 1),
            round(self.b_rank_ratio, 1),
            self.allow_approx,
            round(self.rtol, 3),
            self.reuse_a,
            self.reuse_b,
        )
        return hashlib.md5(str(features).encode()).hexdigest()[:10]


@dataclass
class PlanResult:
    C: np.ndarray
    plan: str
    time_sec: float
    approx_error: Optional[float] = None
    details: Dict[str, Any] = field(default_factory=dict)


# ----------------------------
# Helpers (Σ probes)
# ----------------------------

def _sparsity(A: np.ndarray, sample: int = 8192) -> float:
    # Estimate fraction of ~zeros; sample to avoid full scan for huge matrices
    x = A.ravel()
    if x.size == 0:
        return 0.0
    if x.size <= sample:
        return float(np.mean(np.abs(x) < 1e-12))
    idx = np.random.randint(0, x.size, size=sample)
    return float(np.mean(np.abs(x[idx]) < 1e-12))


def _rank_ratio_sketch(A: np.ndarray, k: int = 32) -> float:
    # Very cheap sketch-based singular decay proxy: rank_ratio in [0,1]
    m, n = A.shape
    kk = min(k, m, n)
    if kk < 2:
        return 1.0
    # Random range finder
    Omega = np.random.randn(n, kk)
    Y = A @ Omega
    Q, _ = np.linalg.qr(Y, mode="reduced")
    B = Q.T @ A
    # SVD on small matrix
    try:
        s = np.linalg.svd(B, compute_uv=False)
    except Exception:
        return 1.0
    if s.size == 0:
        return 1.0
    thr = 0.01 * s[0]
    eff = int(np.sum(s > thr))
    return float(eff / min(m, n))


def randomized_svd(A: np.ndarray, rank: int, oversample: int = 8) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Randomized SVD: A ≈ U diag(S) Vt, with U:(m,rank), S:(rank,), Vt:(rank,n).
    """
    m, n = A.shape
    r = max(1, min(rank, m, n))
    p = min(oversample, max(0, min(m, n) - r))
    k = r + p
    Omega = np.random.randn(n, k)
    Y = A @ Omega
    Q, _ = np.linalg.qr(Y, mode="reduced")
    B = Q.T @ A
    Uhat, S, Vt = np.linalg.svd(B, full_matrices=False)
    U = Q @ Uhat[:, :r]
    return U, S[:r], Vt[:r, :]


def rel_error(A: np.ndarray, B: np.ndarray) -> float:
    denom = np.linalg.norm(B) + 1e-12
    return float(np.linalg.norm(A - B) / denom)


# ----------------------------
# QP-GEMM engine
# ----------------------------

class QPGEMM:
    """
    Quad-polar matrix multiplication engine.

    Primary contract:
    - If allow_approx=False: return exactly A@B (up to floating roundoff) via safe plan (usually BLAS).
    - If allow_approx=True: may return approximation but must self-validate (sampled) and fallback if outside rtol.

    Caching:
    - plan_cache: signature -> chosen plan name
    - factor_cache: (matrix_key, plan)-> factors (e.g., low-rank U,S,Vt)
    """
    def __init__(self, max_cache: int = 256, verbose: bool = False):
        self.verbose = verbose
        self.plan_cache: Dict[str, str] = {}
        self.factor_cache: Dict[Tuple[str, str], Any] = {}
        self.max_cache = max_cache

    # ---- public API ----

    def matmul(self,
               A: np.ndarray,
               B: np.ndarray,
               *,
               allow_approx: bool = False,
               rtol: float = 1e-2,
               reuse_a: bool = False,
               reuse_b: bool = False,
               force_plan: Optional[str] = None,
               microbench_trials: int = 2) -> PlanResult:
        A = np.asarray(A)
        B = np.asarray(B)
        assert A.ndim == 2 and B.ndim == 2, "A and B must be 2D"
        m, k = A.shape
        k2, n = B.shape
        assert k == k2, "Inner dimensions must match"

        fp = self._analyze(A, B, allow_approx=allow_approx, rtol=rtol, reuse_a=reuse_a, reuse_b=reuse_b)
        key = fp.hash()

        if force_plan is not None:
            return self._run_plan(force_plan, A, B, fp, validate=allow_approx)

        plan = self.plan_cache.get(key)
        if plan is None:
            plan = self._select_plan(A, B, fp, trials=microbench_trials)
            self._cache_plan(key, plan)

        result = self._run_plan(plan, A, B, fp, validate=allow_approx)

        # If approx validation failed, fallback to BLAS and update cache
        if allow_approx and (result.approx_error is None or result.approx_error > rtol):
            if self.verbose:
                print(f"[QP-GEMM] approx plan '{plan}' failed error={result.approx_error}; falling back to BLAS.")
            result = self._run_plan("blas", A, B, fp, validate=False)
            self._cache_plan(key, "blas")

        return result

    # ---- analysis (Σ probes + Ψ reuse flags) ----

    def _analyze(self, A: np.ndarray, B: np.ndarray, *, allow_approx: bool, rtol: float, reuse_a: bool, reuse_b: bool) -> GEMMFingerprint:
        m, k = A.shape
        _, n = B.shape

        a_contig = bool(A.flags["C_CONTIGUOUS"])
        b_contig = bool(B.flags["C_CONTIGUOUS"])
        a_sp = _sparsity(A)
        b_sp = _sparsity(B)
        # Rank probes are more expensive; keep them cheap and conditional
        a_rr = _rank_ratio_sketch(A, k=24) if (reuse_a or allow_approx) else 1.0
        b_rr = _rank_ratio_sketch(B, k=24) if (reuse_b or allow_approx) else 1.0

        return GEMMFingerprint(
            m=m, k=k, n=n,
            dtype=str(A.dtype),
            a_contig=a_contig,
            b_contig=b_contig,
            a_sparsity=a_sp,
            b_sparsity=b_sp,
            a_rank_ratio=a_rr,
            b_rank_ratio=b_rr,
            allow_approx=allow_approx,
            rtol=rtol,
            reuse_a=reuse_a,
            reuse_b=reuse_b,
        )

    # ---- candidate generation + plan selection (Σ plan search) ----

    def _candidate_plans(self, fp: GEMMFingerprint) -> List[str]:
        plans = ["blas"]
        # Ψ: packing / contiguity (cheap)
        if not (fp.a_contig and fp.b_contig):
            plans.append("contig_blas")

        # D: sparse kernel
        if sp is not None and (fp.a_sparsity > 0.7 or fp.b_sparsity > 0.7):
            plans.append("sparse")

        # Ψ+Ω: low-rank opportunism (only when it could help)
        # If either matrix looks compressible and reuse/approx is allowed.
        if (fp.allow_approx or fp.reuse_a) and fp.a_rank_ratio < 0.35:
            plans.append("lowrank_A")
        if (fp.allow_approx or fp.reuse_b) and fp.b_rank_ratio < 0.35:
            plans.append("lowrank_B")

        # Ψ: Strassen only for large-ish, square-ish; python overhead is high so keep optional
        if fp.m == fp.n == fp.k and fp.m >= 256 and (fp.m & (fp.m - 1) == 0):
            plans.append("strassen")

        return plans

    def _select_plan(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, trials: int = 2) -> str:
        candidates = self._candidate_plans(fp)
        if self.verbose:
            print(f"[QP-GEMM] candidates={candidates} fp={fp}")

        # Micro-benchmark candidates on a small number of repeats (Σ selection)
        best_plan = "blas"
        best_t = float("inf")
        for plan in candidates:
            t = self._time_plan(plan, A, B, fp, trials=trials)
            if self.verbose:
                print(f"[QP-GEMM] bench {plan}: {t*1e3:.3f} ms")
            if t < best_t:
                best_t = t
                best_plan = plan

        return best_plan

    def _time_plan(self, plan: str, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, trials: int) -> float:
        # Warm-up once
        _ = self._run_plan(plan, A, B, fp, validate=False).C
        t0 = time.perf_counter()
        for _ in range(max(1, trials)):
            _ = self._run_plan(plan, A, B, fp, validate=False).C
        t1 = time.perf_counter()
        return (t1 - t0) / max(1, trials)

    def _cache_plan(self, key: str, plan: str) -> None:
        if len(self.plan_cache) >= self.max_cache:
            # crude eviction: drop oldest inserted
            self.plan_cache.pop(next(iter(self.plan_cache)))
        self.plan_cache[key] = plan

    # ---- execution (D) + optional validation ----

    def _run_plan(self, plan: str, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool) -> PlanResult:
        if plan == "blas":
            return self._plan_blas(A, B)
        if plan == "contig_blas":
            return self._plan_contig_blas(A, B)
        if plan == "sparse":
            return self._plan_sparse(A, B)
        if plan == "lowrank_A":
            return self._plan_lowrank_A(A, B, fp, validate=validate)
        if plan == "lowrank_B":
            return self._plan_lowrank_B(A, B, fp, validate=validate)
        if plan == "strassen":
            return self._plan_strassen(A, B)
        # fallback
        return self._plan_blas(A, B)

    # ---- individual plans ----

    def _plan_blas(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        t0 = time.perf_counter()
        C = A @ B
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="blas", time_sec=t1 - t0)

    def _plan_contig_blas(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        t0 = time.perf_counter()
        Ac = np.ascontiguousarray(A)
        Bc = np.ascontiguousarray(B)
        C = Ac @ Bc
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="contig_blas", time_sec=t1 - t0, details={"A_contig": True, "B_contig": True})

    def _plan_sparse(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        if sp is None:
            return self._plan_blas(A, B)
        t0 = time.perf_counter()
        # Choose direction based on sparsity
        if _sparsity(A) > 0.7:
            As = sp.csr_matrix(A)
            C = As.dot(B)
        elif _sparsity(B) > 0.7:
            Bs = sp.csr_matrix(B)
            C = A.dot(Bs).toarray()
        else:
            C = A @ B
        t1 = time.perf_counter()
        if sp.issparse(C):
            C = C.toarray()
        return PlanResult(C=np.asarray(C), plan="sparse", time_sec=t1 - t0)

    def _plan_lowrank_A(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool) -> PlanResult:
        # Cache factors by matrix identity + shape + dtype (cheap; assumes A is reused as same object)
        akey = f"A:{id(A)}:{A.shape}:{A.dtype}"
        cache_key = (akey, "svdA")
        t0 = time.perf_counter()
        if cache_key in self.factor_cache:
            U, S, Vt, k = self.factor_cache[cache_key]
        else:
            # choose k from rank ratio
            k = max(4, int(min(A.shape) * max(0.05, min(fp.a_rank_ratio, 0.35))))
            U, S, Vt = randomized_svd(A, rank=k)
            self.factor_cache[cache_key] = (U, S, Vt, k)

        # A@B ≈ U diag(S) (Vt@B)
        C = U @ ((S[:, None]) * (Vt @ B))
        t1 = time.perf_counter()

        approx_err = None
        if validate:
            C_ref = A @ B
            approx_err = rel_error(C, C_ref)

        return PlanResult(C=C, plan="lowrank_A", time_sec=t1 - t0, approx_error=approx_err, details={"k": k})

    def _plan_lowrank_B(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool) -> PlanResult:
        bkey = f"B:{id(B)}:{B.shape}:{B.dtype}"
        cache_key = (bkey, "svdB")
        t0 = time.perf_counter()
        if cache_key in self.factor_cache:
            U, S, Vt, k = self.factor_cache[cache_key]
        else:
            k = max(4, int(min(B.shape) * max(0.05, min(fp.b_rank_ratio, 0.35))))
            U, S, Vt = randomized_svd(B, rank=k)
            self.factor_cache[cache_key] = (U, S, Vt, k)

        # A@B ≈ (A@U) diag(S) Vt
        C = (A @ U) @ ((S[:, None]) * Vt)
        t1 = time.perf_counter()

        approx_err = None
        if validate:
            C_ref = A @ B
            approx_err = rel_error(C, C_ref)

        return PlanResult(C=C, plan="lowrank_B", time_sec=t1 - t0, approx_error=approx_err, details={"k": k})

    # Minimal Strassen (educational; usually slower in Python)
    def _plan_strassen(self, A: np.ndarray, B: np.ndarray, leaf: int = 128) -> PlanResult:
        t0 = time.perf_counter()
        C = _strassen(A, B, leaf=leaf)
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="strassen", time_sec=t1 - t0, details={"leaf": leaf})

    # ---- ablation support ----
    
    def ablation_run(self, workloads: List[Tuple[np.ndarray, np.ndarray]], 
                     repeats: int = 3,
                     allow_approx: bool = False,
                     rtol: float = 1e-2,
                     reuse_a: bool = False,
                     reuse_b: bool = False) -> List[Dict[str, Any]]:
        """Run ablation study on workloads, returning timing and error data."""
        rows = []
        for i, (A, B) in enumerate(workloads):
            for _ in range(repeats):
                result = self.matmul(A, B, allow_approx=allow_approx, rtol=rtol, 
                                     reuse_a=reuse_a, reuse_b=reuse_b)
                rows.append({
                    "workload": i,
                    "plan": result.plan,
                    "time_ms": result.time_sec * 1000,
                    "approx_error": result.approx_error,
                    "shape": (A.shape, B.shape),
                })
        return rows


def _strassen(A: np.ndarray, B: np.ndarray, leaf: int = 128) -> np.ndarray:
    n = A.shape[0]
    if n <= leaf:
        return A @ B
    # split
    mid = n // 2
    A11, A12 = A[:mid, :mid], A[:mid, mid:]
    A21, A22 = A[mid:, :mid], A[mid:, mid:]
    B11, B12 = B[:mid, :mid], B[:mid, mid:]
    B21, B22 = B[mid:, :mid], B[mid:, mid:]

    M1 = _strassen(A11 + A22, B11 + B22, leaf)
    M2 = _strassen(A21 + A22, B11, leaf)
    M3 = _strassen(A11, B12 - B22, leaf)
    M4 = _strassen(A22, B21 - B11, leaf)
    M5 = _strassen(A11 + A12, B22, leaf)
    M6 = _strassen(A21 - A11, B11 + B12, leaf)
    M7 = _strassen(A12 - A22, B21 + B22, leaf)

    C11 = M1 + M4 - M5 + M7
    C12 = M3 + M5
    C21 = M2 + M4
    C22 = M1 - M2 + M3 + M6

    C = np.empty_like(A @ B)  # correct dtype/shape
    C[:mid, :mid] = C11
    C[:mid, mid:] = C12
    C[mid:, :mid] = C21
    C[mid:, mid:] = C22
    return C


# ----------------------------
# Ablation utilities
# ----------------------------

def make_ablation_configs(verbose: bool = False) -> List[Tuple[str, QPGEMM]]:
    """Create a set of QPGEMM configurations for ablation study."""
    configs = [
        ("full", QPGEMM(verbose=verbose)),
        ("blas_only", QPGEMM(verbose=verbose)),  # Will force blas
    ]
    return configs


def summarize_ablation(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize ablation run results."""
    if not rows:
        return {"mean_time_ms": 0, "p50_time_ms": 0, "best_time_ms": 0, 
                "mean_err": None, "worst_err": None}
    
    times = [r["time_ms"] for r in rows]
    errors = [r["approx_error"] for r in rows if r["approx_error"] is not None]
    
    return {
        "mean_time_ms": np.mean(times),
        "p50_time_ms": np.median(times),
        "best_time_ms": np.min(times),
        "mean_err": np.mean(errors) if errors else None,
        "worst_err": np.max(errors) if errors else None,
    }
