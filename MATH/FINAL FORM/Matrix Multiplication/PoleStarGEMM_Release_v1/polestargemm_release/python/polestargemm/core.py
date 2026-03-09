"""
PoleStarGEMM Core (Quad-Polar Adaptive GEMM)
===========================================

This module provides a *planner + cache + validator* around matrix multiplication.

Design principles
-----------------
- Never claims to beat BLAS by default.
- Opportunistically exploits structure (low-rank, sparsity) and reuse (cached contiguity/factors)
  when it can be proven to help via micro-benchmark selection and (optional) validation.
- Includes hard fallbacks: if approximate output fails validation, it returns exact BLAS result.

Quad-polar mapping for GEMM
---------------------------
- Ψ (Psi): representation + reuse (cached contiguity/packing, cached low-rank factors)
- Σ (Sigma): probing + exploration (sketch diagnostics, candidate plan set, micro-bench selection)
- Ω (Omega): continuous tuning (rank bumps to meet rtol; budget allocation; hysteresis)
- Δ (Delta): discrete execution + hard fallbacks (BLAS, sparse), safety gates

Notes
-----
This is a general-purpose NumPy engine. For PyTorch vision-model optimization and TorchScript/C++
deployment, see `polestargemm.vision`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple, List, Set, Iterable

import time
import math
import hashlib
import numpy as np

try:
    import scipy.sparse as sp  # type: ignore
except Exception:  # pragma: no cover
    sp = None


# ----------------------------
# Fingerprints + Experience DB
# ----------------------------

@dataclass
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

    def _bucket(self) -> Tuple[Any, ...]:
        """
        Coarse bucketing to generalize across nearby workloads.

        We intentionally bucket shapes to powers-of-two-ish sizes and round ratios
        to keep the experience DB stable.
        """
        def _shape_bucket(x: int) -> int:
            if x <= 0:
                return 0
            return int(2 ** int(round(math.log2(max(2, x)))))

        def _ratio_bucket(r: float) -> float:
            return float(round(r, 1))

        def _spar_bucket(s: float) -> str:
            if s >= 0.9:
                return "ultra"
            if s >= 0.7:
                return "high"
            if s >= 0.3:
                return "mid"
            return "low"

        return (
            _shape_bucket(self.m),
            _shape_bucket(self.k),
            _shape_bucket(self.n),
            self.dtype,
            self.a_contig,
            self.b_contig,
            _spar_bucket(self.a_sparsity),
            _spar_bucket(self.b_sparsity),
            _ratio_bucket(self.a_rank_ratio),
            _ratio_bucket(self.b_rank_ratio),
            self.allow_approx,
            float(round(self.rtol, 3)),
            self.reuse_a,
            self.reuse_b,
        )

    def hash(self) -> str:
        return hashlib.md5(str(self._bucket()).encode("utf-8")).hexdigest()[:12]


@dataclass
class GEMMRecord:
    fingerprint: GEMMFingerprint
    plan: str
    time_sec: float
    approx_error: Optional[float] = None
    success: bool = True
    overhead_sec: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)

    def score(self, error_weight: float = 10.0, fail_penalty: float = 1e6) -> float:
        """
        Lower is better.

        We treat approximate error as a soft penalty; hard failures get a big penalty.
        """
        if not self.success:
            return fail_penalty + self.time_sec + self.overhead_sec
        epen = 0.0
        if self.approx_error is not None:
            epen = error_weight * self.approx_error
        return self.time_sec + self.overhead_sec + epen


class GEMMExperienceDB:
    """
    Minimal experience DB:
    - Stores up to `keep_k` best records per fingerprint bucket.
    - Recommends the best plan for exact bucket matches, else nearest neighbor
      using a cheap bucket distance.
    """

    def __init__(self, keep_k: int = 12):
        self.keep_k = keep_k
        self.records: Dict[str, List[GEMMRecord]] = {}
        self.global_stats: Dict[str, Any] = {
            "total_calls": 0,
            "successes": 0,
            "plan_counts": {},
        }

    def add(self, rec: GEMMRecord) -> None:
        key = rec.fingerprint.hash()
        self.records.setdefault(key, []).append(rec)
        self.records[key].sort(key=lambda r: r.score())
        if len(self.records[key]) > self.keep_k:
            self.records[key] = self.records[key][: self.keep_k]

        self.global_stats["total_calls"] += 1
        if rec.success:
            self.global_stats["successes"] += 1
        pc = self.global_stats["plan_counts"]
        pc[rec.plan] = pc.get(rec.plan, 0) + 1

    def best_plan(self, fp: GEMMFingerprint) -> Optional[str]:
        key = fp.hash()
        if key in self.records and self.records[key]:
            return self.records[key][0].plan

        # Nearest-neighbor search over coarse buckets.
        target = fp._bucket()
        best: Tuple[float, Optional[str]] = (float("inf"), None)
        for recs in self.records.values():
            if not recs:
                continue
            cand = recs[0].fingerprint._bucket()
            dist = self._bucket_distance(target, cand)
            if dist < best[0]:
                best = (dist, recs[0].plan)
        return best[1]

    @staticmethod
    def _bucket_distance(a: Tuple[Any, ...], b: Tuple[Any, ...]) -> float:
        d = 0.0
        for x, y in zip(a, b):
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                d += abs(float(x) - float(y))
            else:
                d += 0.0 if x == y else 1.0
        return d


# ----------------------------
# Σ probes (cheap diagnostics)
# ----------------------------

def _sparsity(A: np.ndarray, sample: int = 8192) -> float:
    """
    Estimate fraction of near-zero elements via sampling.
    """
    x = np.asarray(A).ravel()
    if x.size == 0:
        return 0.0
    if x.size <= sample:
        return float(np.mean(np.abs(x) < 1e-12))
    idx = np.random.randint(0, x.size, size=sample)
    return float(np.mean(np.abs(x[idx]) < 1e-12))


def estimate_rank_ratio(A: np.ndarray, rank_probe: int = 16, oversample: int = 6, seed: int = 0) -> float:
    """
    Fast compressibility proxy in [0,1] using sketch + small SVD.

    Interpretation:
      - Near 0.0 => energy is concentrated in top components => "compressible"
      - Near 1.0 => spectrum is flat => "not compressible"

    This is *not* a true rank estimator; it's a planning heuristic.
    """
    A = np.asarray(A)
    if A.size == 0:
        return 0.0
    m, n = A.shape
    k = min(rank_probe + oversample, m, n)
    if k < 2:
        return 1.0
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((n, k))
    Y = A @ G
    Q, _ = np.linalg.qr(Y, mode="reduced")
    B = Q.T @ A
    s = np.linalg.svd(B, compute_uv=False)
    if s.size == 0:
        return 1.0
    rp = min(rank_probe, s.size)
    top = float(np.sum(s[:rp] ** 2))
    tot = float(np.sum(s ** 2)) + 1e-12
    frac = top / tot
    return float(max(0.0, min(1.0, 1.0 - frac)))


def randomized_svd(A: np.ndarray, rank: int, n_iter: int = 1, seed: int = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Randomized SVD (range finder) returning U,S,Vt with S descending.

    A ≈ U diag(S) Vt, where:
      U: (m, r), S: (r,), Vt: (r, n)
    """
    A = np.asarray(A)
    m, n = A.shape
    r = max(1, min(int(rank), m, n))
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((n, r + 8))
    Y = A @ G
    for _ in range(max(0, n_iter)):
        Y = A @ (A.T @ Y)
    Q, _ = np.linalg.qr(Y, mode="reduced")
    B = Q.T @ A
    Ub, S, Vt = np.linalg.svd(B, full_matrices=False)
    U = Q @ Ub
    return U[:, :r], S[:r], Vt[:r, :]


def validate_approx(A: np.ndarray, B: np.ndarray, C: np.ndarray, checks: int = 3, seed: int = 0) -> float:
    """
    Cheap validation for A@B ≈ C without forming full reference:
    sample random vectors x and compare y_ref=A@(B@x) vs y_hat=C@x.

    Returns the maximum relative error across checks.
    """
    A = np.asarray(A)
    B = np.asarray(B)
    C = np.asarray(C)
    rng = np.random.default_rng(seed)
    n = B.shape[1]
    worst = 0.0
    for _ in range(max(1, int(checks))):
        x = rng.standard_normal(n)
        y_ref = A @ (B @ x)
        y_hat = C @ x
        denom = np.linalg.norm(y_ref) + 1e-12
        err = float(np.linalg.norm(y_hat - y_ref) / denom)
        worst = max(worst, err)
    return worst


# ----------------------------
# Strassen (Ψ recursion; educational)
# ----------------------------

def _strassen(A: np.ndarray, B: np.ndarray, leaf: int) -> np.ndarray:
    n = A.shape[0]
    if n <= leaf:
        return A @ B
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

    C = np.empty((n, n), dtype=np.result_type(A, B))
    C[:mid, :mid] = C11
    C[:mid, mid:] = C12
    C[mid:, :mid] = C21
    C[mid:, mid:] = C22
    return C


# ----------------------------
# Plan result
# ----------------------------

@dataclass
class PlanResult:
    C: np.ndarray
    plan: str
    time_sec: float
    approx_error: Optional[float] = None
    overhead_sec: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompiledGEMMPlan:
    """
    A compiled, reuse-friendly GEMM plan.

    Purpose:
    - Separate Ψ (planning/caching) from Δ (execution).
    - Avoid repeated probing/micro-bench overhead for repeated workloads.
    """

    engine: "PoleStarGEMM"
    plan: str
    fp: GEMMFingerprint
    allow_approx: bool
    rtol: float
    reuse_a: bool
    reuse_b: bool
    reuse_horizon: int = 8
    recheck_every: int = 0

    a_key: Optional[str] = None
    b_key: Optional[str] = None
    _calls: int = 0

    def __call__(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        self._calls += 1

        if self.recheck_every and (self._calls % self.recheck_every == 0):
            return self.engine.matmul(
                A, B,
                allow_approx=self.allow_approx,
                rtol=self.rtol,
                reuse_a=self.reuse_a,
                reuse_b=self.reuse_b,
                reuse_horizon=self.reuse_horizon,
            )

        if self.reuse_a and self.a_key is not None:
            if self.engine._matrix_key(A, "A") != self.a_key:
                return self.engine.matmul(
                    A, B,
                    allow_approx=self.allow_approx,
                    rtol=self.rtol,
                    reuse_a=self.reuse_a,
                    reuse_b=self.reuse_b,
                    reuse_horizon=self.reuse_horizon,
                )
        if self.reuse_b and self.b_key is not None:
            if self.engine._matrix_key(B, "B") != self.b_key:
                return self.engine.matmul(
                    A, B,
                    allow_approx=self.allow_approx,
                    rtol=self.rtol,
                    reuse_a=self.reuse_a,
                    reuse_b=self.reuse_b,
                    reuse_horizon=self.reuse_horizon,
                )

        return self.engine._run_plan(self.plan, A, B, self.fp, validate=self.allow_approx)


# ----------------------------
# PoleStarGEMM engine
# ----------------------------

class PoleStarGEMM:
    """
    PoleStarGEMM: Quad-Polar Adaptive GEMM Engine (NumPy)

    Public contract:
      - allow_approx=False => returns exact A@B (up to FP roundoff).
      - allow_approx=True  => may return approximation but validates and falls back if outside rtol.

    Key stability features:
      - Δ gating for low-rank candidates (avoid near-full rank that is slower than BLAS)
      - Ω hysteresis when a prior plan exists (avoid thrashing on small timing deltas)
      - Median micro-bench timing (more robust than "best of N")
    """

    def __init__(
        self,
        *,
        verbose: bool = False,
        max_cache: int = 256,
        key_mode: str = "id",
        hash_samples: int = 2048,
        hash_seed: int = 0,
        experience_db: Optional[GEMMExperienceDB] = None,
        # pole toggles (for ablations)
        enable_psi: bool = True,
        enable_sigma: bool = True,
        enable_omega: bool = True,
        enable_strassen: bool = True,
        enable_sparse: bool = True,
        # stability knobs
        switch_margin: float = 0.07,
        lowrank_max_ratio: float = 0.70,
        lowrank_max_rank_frac: float = 0.60,
        lowrank_min_rank_frac: float = 0.05,
        lowrank_max_rank_ratio_hint: float = 0.35,
    ):
        self.verbose = bool(verbose)
        self.max_cache = int(max_cache)

        # Cache key mode: 'id' (fast) or 'sample_hash' (cheap content hash)
        if key_mode not in ("id", "sample_hash"):
            raise ValueError("key_mode must be 'id' or 'sample_hash'")
        self.key_mode = key_mode
        self.hash_samples = int(hash_samples)
        self.hash_seed = int(hash_seed)

        # Poles
        self.enable_psi = bool(enable_psi)
        self.enable_sigma = bool(enable_sigma)
        self.enable_omega = bool(enable_omega)

        # Features
        self.enable_strassen = bool(enable_strassen)
        self.enable_sparse = bool(enable_sparse)

        # Stability knobs
        self.switch_margin = float(switch_margin)
        self.lowrank_max_ratio = float(lowrank_max_ratio)
        self.lowrank_max_rank_frac = float(lowrank_max_rank_frac)
        self.lowrank_min_rank_frac = float(lowrank_min_rank_frac)
        self.lowrank_max_rank_ratio_hint = float(lowrank_max_rank_ratio_hint)

        # Ψ caches
        self.plan_cache: Dict[str, str] = {}
        self.factor_cache: Dict[Tuple[str, str], Any] = {}
        self.contig_cache: Dict[str, np.ndarray] = {}

        # Ψ memory
        self.db = experience_db or GEMMExperienceDB()

        self._calls = 0

    # ---- public API ----

    def matmul(
        self,
        A: np.ndarray,
        B: np.ndarray,
        *,
        allow_approx: bool = False,
        rtol: float = 1e-2,
        reuse_a: bool = False,
        reuse_b: bool = False,
        reuse_horizon: int = 8,
        force_plan: Optional[str] = None,
        micro_trials: int = 2,
        recheck_every: int = 0,
        validate_checks: int = 3,
    ) -> PlanResult:
        """
        Multiply A@B using an adaptive plan.

        Args:
            allow_approx: if True, may use approximate low-rank plans, but validates and falls back if needed.
            rtol: relative error target used for validation (only matters if allow_approx=True).
            reuse_a/reuse_b: hints that A or B will be reused across calls (enables Ψ caching).
            reuse_horizon: amortization horizon for one-time setup under reuse.
            force_plan: bypass selection and run a specific plan name.
            micro_trials: repeats used in micro-benchmark selection (Σ budget).
            recheck_every: if >0, every N calls ignore cache and re-plan (guards drift).
            validate_checks: number of random-vector checks when validating approximate results.
        """
        self._calls += 1

        A = np.asarray(A)
        B = np.asarray(B)
        if A.ndim != 2 or B.ndim != 2:
            raise ValueError("A and B must be 2D arrays")
        if A.shape[1] != B.shape[0]:
            raise ValueError(f"shape mismatch: A{A.shape} @ B{B.shape}")

        fp = self._fingerprint(A, B, allow_approx=allow_approx, rtol=rtol, reuse_a=reuse_a, reuse_b=reuse_b)
        fph = fp.hash()

        # Forced plan
        if force_plan is not None:
            res = self._run_plan(force_plan, A, B, fp, validate=allow_approx, rtol=rtol, validate_checks=validate_checks)
            self._record(fp, res, allow_approx=allow_approx, rtol=rtol)
            return res

        # Cache hit?
        if recheck_every > 0 and (self._calls % recheck_every == 0):
            cached = None
        else:
            cached = self.plan_cache.get(fph)

        if cached is not None:
            res = self._run_plan(cached, A, B, fp, validate=allow_approx, rtol=rtol, validate_checks=validate_checks)
            if allow_approx and (res.approx_error is not None) and (res.approx_error > rtol):
                if self.verbose:
                    print(f"[PoleStarGEMM] cached plan '{cached}' failed validation ({res.approx_error:.3e} > {rtol}); fallback=blas")
                res = self._run_plan("blas", A, B, fp, validate=False, rtol=rtol, validate_checks=validate_checks)
                self.plan_cache[fph] = "blas"
            self._record(fp, res, allow_approx=allow_approx, rtol=rtol)
            return res

        # No cache: use ExperienceDB prior (Ψ memory)
        prior = self.db.best_plan(fp) if self.enable_psi else None

        plan = self._select_plan(A, B, fp, trials=micro_trials, prior=prior, reuse_horizon=reuse_horizon)

        res = self._run_plan(plan, A, B, fp, validate=allow_approx, rtol=rtol, validate_checks=validate_checks)
        if allow_approx and (res.approx_error is not None) and (res.approx_error > rtol):
            if self.verbose:
                print(f"[PoleStarGEMM] selected plan '{plan}' failed validation ({res.approx_error:.3e} > {rtol}); fallback=blas")
            res = self._run_plan("blas", A, B, fp, validate=False, rtol=rtol, validate_checks=validate_checks)
            plan = "blas"

        # Update cache
        self.plan_cache[fph] = plan
        self._cap_cache(self.plan_cache)
        self._record(fp, res, allow_approx=allow_approx, rtol=rtol)
        return res

    def compile(
        self,
        A: np.ndarray,
        B: np.ndarray,
        *,
        allow_approx: bool = False,
        rtol: float = 1e-2,
        reuse_a: bool = False,
        reuse_b: bool = False,
        reuse_horizon: int = 8,
        force_plan: Optional[str] = None,
        micro_trials: int = 2,
        recheck_every: int = 0,
    ) -> CompiledGEMMPlan:
        """
        Compile a reuse-friendly plan for (A,B).
        """
        A = np.asarray(A)
        B = np.asarray(B)
        if A.ndim != 2 or B.ndim != 2:
            raise ValueError("A and B must be 2D arrays")
        if A.shape[1] != B.shape[0]:
            raise ValueError(f"shape mismatch: A{A.shape} @ B{B.shape}")

        fp = self._fingerprint(A, B, allow_approx=allow_approx, rtol=rtol, reuse_a=reuse_a, reuse_b=reuse_b)
        prior = self.db.best_plan(fp) if self.enable_psi else None

        if force_plan is not None:
            plan = force_plan
        else:
            key = fp.hash()
            plan = self.plan_cache.get(key)
            if plan is None:
                plan = self._select_plan(A, B, fp, trials=micro_trials, prior=prior, reuse_horizon=reuse_horizon)
                self.plan_cache[key] = plan
                self._cap_cache(self.plan_cache)

        # Prime caches for chosen plan
        self._prime_plan(plan, A, B, fp, allow_approx=allow_approx, rtol=rtol)

        return CompiledGEMMPlan(
            engine=self,
            plan=plan,
            fp=fp,
            allow_approx=allow_approx,
            rtol=rtol,
            reuse_a=reuse_a,
            reuse_b=reuse_b,
            reuse_horizon=reuse_horizon,
            recheck_every=recheck_every,
            a_key=self._matrix_key(A, "A") if reuse_a else None,
            b_key=self._matrix_key(B, "B") if reuse_b else None,
        )

    def ablation_run(
        self,
        workloads: Iterable[Tuple[np.ndarray, np.ndarray]],
        *,
        repeats: int = 3,
        allow_approx: bool = False,
        rtol: float = 1e-2,
        reuse_a: bool = False,
        reuse_b: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Run a small benchmark across workloads and return per-run dict rows:
            {plan, time_sec, approx_error, m,k,n,...}
        """
        rows: List[Dict[str, Any]] = []
        for wi, (A, B) in enumerate(workloads):
            for _ in range(max(1, repeats)):
                res = self.matmul(A, B, allow_approx=allow_approx, rtol=rtol, reuse_a=reuse_a, reuse_b=reuse_b, micro_trials=1)
                rows.append({
                    "workload": wi,
                    "m": A.shape[0],
                    "k": A.shape[1],
                    "n": B.shape[1],
                    "dtype": str(A.dtype),
                    "plan": res.plan,
                    "time_sec": res.time_sec,
                    "approx_error": res.approx_error,
                })
        return rows

    # ---- internal: fingerprint + candidate plans ----

    def _fingerprint(self, A: np.ndarray, B: np.ndarray, *, allow_approx: bool, rtol: float, reuse_a: bool, reuse_b: bool) -> GEMMFingerprint:
        a_s = _sparsity(A)
        b_s = _sparsity(B)
        a_rr = estimate_rank_ratio(A, seed=0) if (allow_approx or reuse_a) else 1.0
        b_rr = estimate_rank_ratio(B, seed=1) if (allow_approx or reuse_b) else 1.0
        return GEMMFingerprint(
            m=A.shape[0], k=A.shape[1], n=B.shape[1],
            dtype=str(A.dtype),
            a_contig=bool(A.flags["C_CONTIGUOUS"]),
            b_contig=bool(B.flags["C_CONTIGUOUS"]),
            a_sparsity=float(a_s),
            b_sparsity=float(b_s),
            a_rank_ratio=float(a_rr),
            b_rank_ratio=float(b_rr),
            allow_approx=bool(allow_approx),
            rtol=float(rtol),
            reuse_a=bool(reuse_a),
            reuse_b=bool(reuse_b),
        )

    def _predicted_lowrank_rank(self, shape: Tuple[int, int], rank_ratio: float) -> int:
        m, n = shape
        min_dim = min(m, n)
        rr = max(self.lowrank_min_rank_frac, min(float(rank_ratio), self.lowrank_max_rank_ratio_hint))
        return max(4, int(min_dim * rr))

    def _lowrank_is_worth_it_A(self, m: int, k: int, r: int) -> bool:
        min_dim = min(m, k)
        if r > self.lowrank_max_rank_frac * min_dim:
            return False
        ratio = (r * (m + k)) / (m * k + 1e-12)
        return ratio <= self.lowrank_max_ratio

    def _lowrank_is_worth_it_B(self, k: int, n: int, r: int) -> bool:
        min_dim = min(k, n)
        if r > self.lowrank_max_rank_frac * min_dim:
            return False
        ratio = (r * (k + n)) / (k * n + 1e-12)
        return ratio <= self.lowrank_max_ratio

    def _candidate_plans(self, fp: GEMMFingerprint) -> List[str]:
        plans: List[str] = ["blas"]

        # Ψ: cached contiguity for repeated noncontiguous inputs
        if self.enable_psi and (fp.reuse_a or fp.reuse_b) and (not fp.a_contig or not fp.b_contig):
            if fp.reuse_a and fp.reuse_b and (not fp.a_contig) and (not fp.b_contig):
                plans.append("cached_contig_AB")
            elif fp.reuse_a and (not fp.a_contig):
                plans.append("cached_contig_A")
            elif fp.reuse_b and (not fp.b_contig):
                plans.append("cached_contig_B")

        # One-off contiguity fix
        if (not fp.a_contig or not fp.b_contig) and (not (fp.reuse_a or fp.reuse_b) or not self.enable_psi):
            plans.append("contig_blas")

        # Δ: sparse
        if self.enable_sparse and sp is not None:
            if fp.a_sparsity >= 0.7 or fp.b_sparsity >= 0.7:
                plans.append("sparse")

        # Ψ+Σ: low-rank opportunism with Δ gating (avoid near-full rank)
        if self.enable_psi and self.enable_sigma:
            if (fp.allow_approx or fp.reuse_a) and (fp.a_rank_ratio < self.lowrank_max_rank_ratio_hint):
                r_pred = self._predicted_lowrank_rank((fp.m, fp.k), fp.a_rank_ratio)
                if self._lowrank_is_worth_it_A(fp.m, fp.k, r_pred):
                    plans.append("lowrank_A")
            if (fp.allow_approx or fp.reuse_b) and (fp.b_rank_ratio < self.lowrank_max_rank_ratio_hint):
                r_pred = self._predicted_lowrank_rank((fp.k, fp.n), fp.b_rank_ratio)
                if self._lowrank_is_worth_it_B(fp.k, fp.n, r_pred):
                    plans.append("lowrank_B")

        # Ψ recursion: Strassen (only for square powers of two; python overhead is high)
        if self.enable_psi and self.enable_strassen:
            if fp.m == fp.n == fp.k and fp.m >= 256 and (fp.m & (fp.m - 1) == 0):
                plans.append("strassen")

        # Deduplicate, keep order
        out: List[str] = []
        seen: Set[str] = set()
        for p in plans:
            if p not in seen:
                out.append(p)
                seen.add(p)
        return out

    # ---- internal: plan selection ----

    def _select_plan(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, trials: int, prior: Optional[str], reuse_horizon: int) -> str:
        candidates = self._candidate_plans(fp)
        if self.verbose:
            print(f"[PoleStarGEMM] candidates={candidates} prior={prior} fp_hash={fp.hash()}")

        ordered = candidates[:]
        if prior in ordered:
            ordered.remove(prior)
            ordered.insert(0, prior)

        # More budget for top guess when Ω enabled
        top_trials = max(1, trials + 1) if (self.enable_omega and prior in candidates) else max(1, trials)

        times: Dict[str, float] = {}
        for i, plan in enumerate(ordered):
            t_trials = top_trials if i == 0 else max(1, trials)
            t = self._estimate_plan_cost(plan, A, B, fp, trials=t_trials, reuse_horizon=reuse_horizon)
            times[plan] = t

        best_plan = min(times.keys(), key=lambda p: times[p]) if times else "blas"

        # Ω hysteresis: if prior is close, keep it (avoid plan thrash)
        if self.enable_omega and prior in times and best_plan != prior:
            if times[best_plan] >= times[prior] * (1.0 - self.switch_margin):
                best_plan = prior

        return best_plan

    def _estimate_plan_cost(self, plan: str, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, trials: int, reuse_horizon: int) -> float:
        """
        Estimate amortized per-call cost for plan selection.

        We use median of observed costs (more stable than "best-of-N").
        """
        reuse_h = max(1, int(reuse_horizon))
        costs: List[float] = []

        for _ in range(max(1, int(trials))):
            if plan in ("cached_contig_A", "cached_contig_B", "cached_contig_AB") and self.enable_psi and (fp.reuse_a or fp.reuse_b):
                res = self._run_plan(plan, A, B, fp, validate=False, rtol=fp.rtol, validate_checks=1)
                exec_t = max(0.0, res.time_sec - res.overhead_sec)
                cost = exec_t + (res.overhead_sec / reuse_h)
            elif plan in ("lowrank_A", "lowrank_B") and self.enable_psi and self.enable_sigma:
                wants_reuse = (plan == "lowrank_A" and fp.reuse_a) or (plan == "lowrank_B" and fp.reuse_b)
                if wants_reuse:
                    res1 = self._run_plan(plan, A, B, fp, validate=False, rtol=fp.rtol, validate_checks=1)
                    res2 = self._run_plan(plan, A, B, fp, validate=False, rtol=fp.rtol, validate_checks=1)
                    setup = max(0.0, res1.time_sec - res2.time_sec)
                    cost = res2.time_sec + (setup / reuse_h)
                else:
                    res = self._run_plan(plan, A, B, fp, validate=False, rtol=fp.rtol, validate_checks=1)
                    cost = res.time_sec
            else:
                res = self._run_plan(plan, A, B, fp, validate=False, rtol=fp.rtol, validate_checks=1)
                cost = res.time_sec

            costs.append(float(cost))

        return float(np.median(costs)) if costs else float("inf")

    # ---- internal: execution (Δ) ----

    def _run_plan(self, plan: str, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool, rtol: float, validate_checks: int) -> PlanResult:
        if plan == "blas":
            return self._plan_blas(A, B)
        if plan == "contig_blas":
            return self._plan_contig_blas(A, B)
        if plan == "cached_contig_A":
            return self._plan_cached_contig_A(A, B)
        if plan == "cached_contig_B":
            return self._plan_cached_contig_B(A, B)
        if plan == "cached_contig_AB":
            return self._plan_cached_contig_AB(A, B)
        if plan == "sparse":
            return self._plan_sparse(A, B)
        if plan == "lowrank_A":
            return self._plan_lowrank_A(A, B, fp, validate=validate, rtol=rtol, validate_checks=validate_checks)
        if plan == "lowrank_B":
            return self._plan_lowrank_B(A, B, fp, validate=validate, rtol=rtol, validate_checks=validate_checks)
        if plan == "strassen":
            return self._plan_strassen(A, B, fp)
        return self._plan_blas(A, B)

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
        return PlanResult(C=C, plan="contig_blas", time_sec=t1 - t0, overhead_sec=0.0)

    # ---- Ψ: cache keys ----

    def _hash_matrix_sample(self, X: np.ndarray) -> str:
        x = np.asarray(X).ravel()
        if x.size == 0:
            return "empty"
        step = max(1, x.size // max(1, self.hash_samples))
        sample = x[::step][: self.hash_samples]
        h = hashlib.md5(sample.tobytes()).hexdigest()[:12]
        return h

    def _matrix_key(self, X: np.ndarray, tag: str) -> str:
        if self.key_mode == "sample_hash":
            return f"{tag}:{X.shape}:{X.dtype}:{self._hash_matrix_sample(X)}"
        return f"{tag}:{id(X)}:{X.shape}:{X.dtype}"

    def _get_contig(self, X: np.ndarray, tag: str) -> Tuple[np.ndarray, float]:
        key = self._matrix_key(X, tag)
        if key in self.contig_cache:
            return self.contig_cache[key], 0.0
        t0 = time.perf_counter()
        Xc = np.ascontiguousarray(X)
        t1 = time.perf_counter()
        self.contig_cache[key] = Xc
        self._cap_cache(self.contig_cache)
        return Xc, t1 - t0

    # ---- contiguity plans ----

    def _plan_cached_contig_A(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        t0 = time.perf_counter()
        Ac, ov = self._get_contig(A, "A")
        C = Ac @ B
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="cached_contig_A", time_sec=t1 - t0, overhead_sec=ov)

    def _plan_cached_contig_B(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        t0 = time.perf_counter()
        Bc, ov = self._get_contig(B, "B")
        C = A @ Bc
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="cached_contig_B", time_sec=t1 - t0, overhead_sec=ov)

    def _plan_cached_contig_AB(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        t0 = time.perf_counter()
        Ac, ovA = self._get_contig(A, "A")
        Bc, ovB = self._get_contig(B, "B")
        C = Ac @ Bc
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="cached_contig_AB", time_sec=t1 - t0, overhead_sec=ovA + ovB)

    # ---- sparse plan ----

    def _plan_sparse(self, A: np.ndarray, B: np.ndarray) -> PlanResult:
        if sp is None:
            return self._plan_blas(A, B)
        t0 = time.perf_counter()
        As = sp.csr_matrix(A) if not sp.issparse(A) else A.tocsr()
        Bs = sp.csr_matrix(B) if not sp.issparse(B) else B.tocsr()
        C = (As @ Bs)
        if sp.issparse(C):
            C = C.toarray()
        t1 = time.perf_counter()
        return PlanResult(C=np.asarray(C), plan="sparse", time_sec=t1 - t0)

    # ---- low-rank plans (Ψ+Σ with Ω adaptation) ----

    def _plan_lowrank_A(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool, rtol: float, validate_checks: int) -> PlanResult:
        akey = self._matrix_key(A, "A")
        cache_key = (akey, "svdA")

        t0 = time.perf_counter()

        if cache_key in self.factor_cache:
            U, S, Vt = self.factor_cache[cache_key]
            k = int(S.shape[0])
        else:
            k0 = self._predicted_lowrank_rank((fp.m, fp.k), fp.a_rank_ratio)
            if not self._lowrank_is_worth_it_A(fp.m, fp.k, k0):
                # Δ: refuse unsafe approximation
                return self._plan_blas(A, B)
            U, S, Vt = randomized_svd(A, rank=k0, n_iter=1, seed=0)
            self.factor_cache[cache_key] = (U, S, Vt)
            self._cap_cache(self.factor_cache)
            k = int(k0)

        C = U @ ((S[:, None]) * (Vt @ B))
        t1 = time.perf_counter()

        approx_err = None
        if validate:
            approx_err = validate_approx(A, B, C, checks=validate_checks, seed=0)
            if self.enable_omega and (approx_err > rtol):
                k_try = k
                min_dim = min(fp.m, fp.k)
                for _ in range(3):
                    k_try = min(min_dim, int(k_try * 1.8) + 1)
                    if not self._lowrank_is_worth_it_A(fp.m, fp.k, k_try):
                        break
                    U2, S2, Vt2 = randomized_svd(A, rank=k_try, n_iter=1, seed=1)
                    C_try = U2 @ ((S2[:, None]) * (Vt2 @ B))
                    err_try = validate_approx(A, B, C_try, checks=validate_checks, seed=2)
                    if err_try <= rtol:
                        C, approx_err = C_try, err_try
                        self.factor_cache[cache_key] = (U2, S2, Vt2)
                        break

        return PlanResult(C=C, plan="lowrank_A", time_sec=t1 - t0, approx_error=approx_err, details={"k": int(self.factor_cache.get(cache_key, (None, np.array([k]), None))[1].shape[0])})

    def _plan_lowrank_B(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, validate: bool, rtol: float, validate_checks: int) -> PlanResult:
        bkey = self._matrix_key(B, "B")
        cache_key = (bkey, "svdB")

        t0 = time.perf_counter()

        if cache_key in self.factor_cache:
            U, S, Vt = self.factor_cache[cache_key]
            k = int(S.shape[0])
        else:
            k0 = self._predicted_lowrank_rank((fp.k, fp.n), fp.b_rank_ratio)
            if not self._lowrank_is_worth_it_B(fp.k, fp.n, k0):
                return self._plan_blas(A, B)
            U, S, Vt = randomized_svd(B, rank=k0, n_iter=1, seed=3)
            self.factor_cache[cache_key] = (U, S, Vt)
            self._cap_cache(self.factor_cache)
            k = int(k0)

        C = (A @ U) @ ((S[:, None]) * Vt)
        t1 = time.perf_counter()

        approx_err = None
        if validate:
            approx_err = validate_approx(A, B, C, checks=validate_checks, seed=4)
            if self.enable_omega and (approx_err > rtol):
                k_try = k
                min_dim = min(fp.k, fp.n)
                for _ in range(3):
                    k_try = min(min_dim, int(k_try * 1.8) + 1)
                    if not self._lowrank_is_worth_it_B(fp.k, fp.n, k_try):
                        break
                    U2, S2, Vt2 = randomized_svd(B, rank=k_try, n_iter=1, seed=5)
                    C_try = (A @ U2) @ ((S2[:, None]) * Vt2)
                    err_try = validate_approx(A, B, C_try, checks=validate_checks, seed=6)
                    if err_try <= rtol:
                        C, approx_err = C_try, err_try
                        self.factor_cache[cache_key] = (U2, S2, Vt2)
                        break

        return PlanResult(C=C, plan="lowrank_B", time_sec=t1 - t0, approx_error=approx_err, details={"k": int(self.factor_cache.get(cache_key, (None, np.array([k]), None))[1].shape[0])})

    def _plan_strassen(self, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint) -> PlanResult:
        leaf = 64
        if self.enable_omega:
            if fp.m >= 1024:
                leaf = 128
            elif fp.m >= 512:
                leaf = 96
        t0 = time.perf_counter()
        C = _strassen(A, B, leaf=leaf)
        t1 = time.perf_counter()
        return PlanResult(C=C, plan="strassen", time_sec=t1 - t0, details={"leaf": leaf})

    # ---- internal: recording + cache cap ----

    def _record(self, fp: GEMMFingerprint, res: PlanResult, *, allow_approx: bool, rtol: float) -> None:
        success = True
        if allow_approx and (res.approx_error is not None) and (res.approx_error > rtol):
            success = False
        self.db.add(GEMMRecord(
            fingerprint=fp,
            plan=res.plan,
            time_sec=res.time_sec,
            approx_error=res.approx_error,
            success=success,
            overhead_sec=res.overhead_sec,
            details=res.details,
        ))

    def _cap_cache(self, dct: Dict[Any, Any]) -> None:
        if len(dct) <= self.max_cache:
            return
        while len(dct) > self.max_cache:
            first_key = next(iter(dct))
            dct.pop(first_key, None)

    def _prime_plan(self, plan: str, A: np.ndarray, B: np.ndarray, fp: GEMMFingerprint, *, allow_approx: bool, rtol: float) -> None:
        if plan in ("cached_contig_A", "cached_contig_B", "cached_contig_AB"):
            if "A" in plan:
                _ = self._get_contig(A, "A")
            if "B" in plan:
                _ = self._get_contig(B, "B")
        if plan in ("lowrank_A", "lowrank_B"):
            # Warm to populate factor cache
            _ = self._run_plan(plan, A, B, fp, validate=allow_approx, rtol=rtol, validate_checks=1)


def summarize_ablation(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize ablation run results."""
    times = [r["time_sec"] for r in rows]
    errs = [r["approx_error"] for r in rows if r.get("approx_error") is not None]
    return {
        "mean_time_ms": 1000.0 * (sum(times) / max(1, len(times))),
        "p50_time_ms": 1000.0 * (float(np.median(times)) if times else 0.0),
        "best_time_ms": 1000.0 * (min(times) if times else 0.0),
        "mean_err": float(np.mean(errs)) if errs else None,
        "worst_err": float(np.max(errs)) if errs else None,
    }


def make_ablation_configs(verbose: bool = False) -> List[Tuple[str, PoleStarGEMM]]:
    """
    Returns a list of (name, engine) variants for pole ablations.
    Δ is always present (we never disable it).
    """
    shared_db = GEMMExperienceDB()
    return [
        ("FULL(Ψ+Σ+Ω)", PoleStarGEMM(verbose=verbose, experience_db=shared_db, enable_psi=True, enable_sigma=True, enable_omega=True)),
        ("NO_Ψ(Σ+Ω)", PoleStarGEMM(verbose=verbose, experience_db=shared_db, enable_psi=False, enable_sigma=True, enable_omega=True)),
        ("NO_Σ(Ψ+Ω)", PoleStarGEMM(verbose=verbose, experience_db=shared_db, enable_psi=True, enable_sigma=False, enable_omega=True)),
        ("NO_Ω(Ψ+Σ)", PoleStarGEMM(verbose=verbose, experience_db=shared_db, enable_psi=True, enable_sigma=True, enable_omega=False)),
        ("Δ_ONLY", PoleStarGEMM(verbose=verbose, experience_db=shared_db, enable_psi=False, enable_sigma=False, enable_omega=False)),
    ]
