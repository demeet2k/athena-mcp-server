# Lens models (likelihood proxies)

A **lens** is a scoring function:

```text
lens.score(theta) -> LensReport(log_score, details)
```

Each lens implements a transparent, explicit **proxy likelihood**. Q‑PHI combines them as a weighted sum of log scores.

Why proxies?

- The true Planet Nine inference problem includes selection effects, survey footprints, non‑linear dynamics, and observational uncertainties.
- For a monetizable / productizable system you want a pipeline that is deterministic and easy to audit and iteratively upgrade.
- These lenses are “first‑order constraints” you can replace one by one without rewriting the whole framework.

---

## Common interface and combination rule

Each lens returns:

- `log_score`: a log‑likelihood‑like scalar (higher is better).
- `details`: a dict of diagnostics used for debugging and UI.

Q‑PHI combines lenses as:

```text
total_log_score(theta) = sum_k w_k * lens_k.log_score(theta)
```

Where `w_k` are user‑controlled weights in `QPHIConfig`.

Important implementation detail:

- `OrbitPlausibilityLens` is treated as a hard-ish reject. If it returns `ok = 0`, Q‑PHI short-circuits and assigns a very low score (effectively removing the sample).

---

## 1) OrbitPlausibilityLens (hard-ish constraints)

Purpose: prune obviously implausible orbits so Monte Carlo budget is not wasted.

Inputs: candidate orbital elements.

Constraints enforced:

- `a` within `[a_min_au, a_max_au]`
- perihelion distance `q = a(1-e)` within `[q_min_au, q_max_au]`
- inclination `i` within `[0, i_max_deg]`
- `0 <= e < 1`

Score:

- `0.0` if constraints pass
- `-1e6` if constraints fail (then Q‑PHI additionally hard‑rejects)

Tuning advice:

- Keep this **wide** unless you have strong published constraints.
- If you tighten it too much you will “force” the inference to agree with your prior instead of your data.

---

## 2) PerihelionClusteringLens (perihelion longitude proxy)

Goal: capture the empirical “perihelion clustering / anti‑alignment” signal often discussed in Planet Nine work.

Definitions:

- longitude of perihelion: `varpi = Omega + omega` (both in degrees)
- Planet Nine candidate has `varpi9`

Model:

- the observed TNO `varpi` values are modeled as draws from a von Mises distribution (a circular Gaussian) centered at:

  `mu = varpi9 + 180 degrees`  (anti‑aligned)

- concentration parameter `kappa` controls how tight the clustering is.

Score:

- `log_score = sum_i log von_mises_pdf(varpi_i | mu, kappa)`

Diagnostics in `details` include:

- `kappa`
- mean TNO varpi
- candidate varpi9
- model center mu

Caveats:

- selection bias can generate apparent clustering.
- if you change your “extreme TNO” filter, this lens can change a lot.

---

## 3) PoleAlignmentLens (orbital pole proxy)

Goal: encode the idea that extreme TNO orbital poles show some alignment, and that Planet Nine might share a related geometry.

Definitions:

- orbital pole is the unit angular momentum direction (computed from inclination `i` and node `Omega`).

Model:

1) compute each TNO pole unit vector
2) compute the mean pole vector and normalize it
3) compute the angle between candidate pole and mean TNO pole: `ang_deg`

Score:

- Gaussian penalty in angle:

  `log_score = -0.5*(ang_deg/sigma_deg)^2 - log(sigma_deg*sqrt(2*pi))`

Where `sigma_deg` is a tunable width (default ~20 degrees).

Caveats / improvements:

- mean‑of‑vectors is not robust; consider a robust estimator or mixture model if you have enough TNOs
- survey geometry can bias which inclinations/nodes are discovered

---

## 4) PrecessionDominanceLens (secular dynamics proxy)

Goal: enforce that Planet Nine contributes meaningfully to the secular perihelion precession of extreme TNOs.

This is intentionally a *quadrupole‑order* toy model: it captures scaling with distance and mass, but not the full resonant/libration dynamics.

Definitions:

- mean motion: `n = sqrt(mu/a^3)` with `mu = 4*pi^2` in AU^3/yr^2
- inner giant planets are treated as fixed perturbers (Jupiter, Saturn, Uranus, Neptune)
- Planet Nine is treated as an outer perturber with `(a9, e9, m9)`

Inner‑planet precession proxy:

- `g_in(a_tno) = sum_p (3/4)*n*(m_p/Msun)*(a_p/a_tno)^3` for planets with `a_p < a_tno`

Outer‑perturber proxy:

- `g_out(a_tno) = (3/4)*n*(m9/Msun)*(a_tno/a9)^3 / (1 - e9^2)^(3/2)` if `a9 > a_tno`

Compute ratio for each TNO:

- `ratio = g_out / g_in`

Score:

- take `log(ratio)` for each TNO
- reward ratios near a target value (default target = 1, i.e. comparable contributions)

  `log_score = sum_i Gaussian(log(ratio_i) ; mu=log(target), sigma=sigma_log)`

Diagnostics include median/min/max ratio.

Caveats / improvements:

- ignores inclination dependence and higher‑order terms
- ignores the possibility that P9 is shaping TNOs through resonances rather than secular precession alone
- upgrade path: replace with higher‑order secular theory or numerical integrations (see `docs/06_EXTENDING_AND_CALIBRATION.md`)

---

## 5) DetectabilityLens (non‑detection / brightness proxy)

Goal: penalize candidates that should have been detected already (given your assumed survey depth + sky coverage).

This is a placeholder for real survey selection functions, but it is *directionally useful* for ruling out “too bright” solutions.

Steps:

1) Convert physical parameters to absolute magnitude H

- radius from mass and density (constant‑density sphere)
- convert diameter + albedo to H using the common asteroid relation

2) Compute a heliocentric position from orbital elements (using mean anomaly M)
3) Compute a crude apparent magnitude:

- approximate geocentric distance by subtracting a 1 AU Earth vector at ecliptic longitude `earth_lon_deg`
- `m = H + 5*log10(r*delta)`  (phase effects ignored)

4) Convert to detection probability

- detection efficiency is logistic in magnitude:

  `eff = 1 / (1 + exp((m - mlim)/width_mag))`

- combine with “covered sky” fraction:

  `p_detect = sky_cov * eff`
  `p_not_detected = 1 - p_detect`

Score:

- `log_score = log(p_not_detected)`

Interpretation:

- bright candidate in covered sky => `p_not_detected` small => large negative penalty
- faint candidate => penalty is near zero

Caveats / improvements:

- real surveys have footprints and depth maps, not a single `sky_cov` and `mlim`
- upgrade path: replace with a survey model that evaluates detection probability as a function of RA/Dec and time

---

## Lens weights (w_k)

`QPHIConfig` exposes weights:

- `w_plausibility`
- `w_perihelion`
- `w_pole`
- `w_precession`
- `w_detectability`

Important: these weights are *not* derived from strict likelihood theory; treat them as:

- a practical way to tune relative influence,
- or learn them later via a calibration process.

A good product workflow is:

1) keep defaults as “balanced”
2) run injection tests
3) tune weights so injected truths are recovered with high probability

See `docs/09_VALIDATION.md`.

---

## Adding a new lens

To add a lens:

1) Create a class with `score(theta) -> LensReport`
2) Add it in `build_lens_suite()` in deterministic order
3) Add its hyperparameters to `QPHIConfig`
4) Record diagnostics in `LensReport.details` (this is important for debugging and UI)
