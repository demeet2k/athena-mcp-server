# Contributing

This repo is intentionally small and audit‑friendly.

If you contribute changes, please:

1) Keep changes **deterministic** (no wall-clock timestamps in outputs, no concurrency that changes results).
2) Keep dependencies minimal.
3) Add or update unit tests under `tests/` when you change behavior.
4) Update documentation under `docs/` when you change the algorithm, lens math, or data formats.

## Suggested development workflow

```bash
python -m pip install -e .
python -m unittest
```

## Style

- Prefer clear, explicit code over clever abstractions.
- Every lens should be self-contained and explainable.
- Every output field should have a documented meaning.
