# Validation and testing

If you want to sell this algorithm, validation is not optional.

This document gives practical, implementable tests you can run today.

---

## 1) Determinism regression test

The minimum product requirement is:

- same version + same config + same dataset + same seed => same outputs

This repo includes a small unit test in `tests/test_determinism.py` that checks:

- the run produces required keys
- repeated runs are identical (within a small tolerance)

Run:

```bash
python -m unittest -v
```

---

## 2) Input-data sanity checks

Before you trust a run, verify:

- you have enough TNOs (a single-digit sample can be unstable)
- your CSV uses degrees, not radians
- you did not swap Omega (node) and omega (argument)

A useful product feature is a “dataset QC report” that prints:

- mean and dispersion of varpi
- mean pole direction and dispersion
- histograms of a, q, i

---

## 3) Injection testing (recommended)

Injection testing answers the question:

> If Planet Nine had parameters Theta_true, would Q‑PHI recover it?

Simple injection workflow:

1) Choose a “true” Planet Nine Theta_true.
2) Generate a synthetic TNO sample that *follows the same proxy assumptions your lenses use*.
   - Example: draw TNO varpi from a von Mises around (varpi9_true + 180 deg)
   - Example: draw poles around the Planet Nine pole
3) Run Q‑PHI on the synthetic sample.
4) Check if the posterior mean sky direction is close to the injected truth.

This test does not prove scientific correctness, but it **does** prove that:

- your pipeline is wired correctly
- your weights/hyperparameters are internally consistent

---

## 4) Sensitivity analysis

You should measure how much results move when you change:

- the extreme‑TNO cut (a_min, q_min)
- lens weights
- precession sigma
- detectability assumptions (mlim, sky_cov)

A product can expose these as UI sliders, but you should still compute “sensitivity summaries” automatically.

---

## 5) Scientific reality checks

Even after the above tests pass, results may still be wrong because:

- real TNO clustering could be a selection artifact
- secular dynamics is not the whole story
- surveys are not “uniform sky coverage at one depth”

Therefore your product language should be:

- “given these assumptions, these regions are higher probability”

and not:

- “Planet Nine is definitely here.”
