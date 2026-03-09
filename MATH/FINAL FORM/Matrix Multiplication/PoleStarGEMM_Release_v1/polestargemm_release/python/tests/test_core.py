import numpy as np

from polestargemm.core import PoleStarGEMM


def test_exact_matches_blas():
    rng = np.random.default_rng(0)
    A = rng.standard_normal((64, 32))
    B = rng.standard_normal((32, 48))
    eng = PoleStarGEMM()
    C0 = A @ B
    C1 = eng.matmul(A, B, allow_approx=False).C
    np.testing.assert_allclose(C1, C0, rtol=1e-6, atol=1e-6)


def test_approx_lowrank_validation():
    rng = np.random.default_rng(1)
    # Construct low-rank A
    m, k, n = 128, 128, 64
    r = 8
    U = rng.standard_normal((m, r))
    V = rng.standard_normal((r, k))
    A = U @ V
    B = rng.standard_normal((k, n))

    eng = PoleStarGEMM()
    res = eng.matmul(A, B, allow_approx=True, rtol=1e-2, reuse_a=True)
    C_ref = A @ B
    err = np.linalg.norm(res.C - C_ref) / (np.linalg.norm(C_ref) + 1e-12)
    assert err <= 1e-1  # loose: validation checks are sampled


def test_compile_runs():
    rng = np.random.default_rng(2)
    A = rng.standard_normal((64, 64))
    B = rng.standard_normal((64, 64))
    eng = PoleStarGEMM()
    plan = eng.compile(A, B, allow_approx=False, reuse_a=True, reuse_b=True)
    out = plan(A, B).C
    np.testing.assert_allclose(out, A @ B, rtol=1e-6, atol=1e-6)
