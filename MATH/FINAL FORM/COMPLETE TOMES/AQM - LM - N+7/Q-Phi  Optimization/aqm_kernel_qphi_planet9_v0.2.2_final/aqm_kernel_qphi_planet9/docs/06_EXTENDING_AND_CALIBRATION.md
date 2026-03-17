# Extending Q‑PHI and improving accuracy

Q‑PHI is intentionally designed to be **upgradeable**. The “kernel” (sampling + scoring + refinement + outputs) is stable; the lens models and the data pipeline are where you improve realism.

This document focuses on practical upgrades that matter for *semi‑accurate* predictions and product reliability.

---

## 1) Replace the demo dataset

The single biggest improvement is to use a curated extreme‑TNO dataset.

Recommended minimum:

- pull from MPC/JPL sources
- version it in your product (so results are reproducible)
- keep a changelog of what objects were added/removed and why

---

## 2) Improve the proposal distribution (speed, not correctness)

Q‑PHI has two proposal modes:

- `data_guided` (default): proposes inclinations/nodes and varpi9 around the sample mean directions
- `broad`: uniform angles

Remember: proposal changes speed, but the lenses define the posterior.

Upgrade ideas:

- importance sampling: keep track of proposal density and correct weights
- adaptive proposals (update proposal sigmas after each refine round)

---

## 3) Upgrade each lens (where accuracy lives)

### Perihelion clustering

Current: von Mises on TNO varpi around (varpi9 + 180°).

Upgrades:

- mixture models (multiple clusters)
- robust likelihood (downweight outliers)
- incorporate measurement uncertainties
- explicit debiasing from survey selection

### Pole alignment

Current: mean pole + Gaussian penalty.

Upgrades:

- robust mean direction estimation
- model discovery bias in i and Omega
- use a joint model of (varpi, pole)

### Precession dominance

Current: quadrupole secular precession scaling.

Upgrades:

- include inclination dependence
- include higher‑order terms or octupole corrections
- compute secular frequencies from a Laplace‑Lagrange model
- replace with short n‑body integrations and compare outcomes (expensive but much closer to reality)

### Detectability

Current: one‑number survey model with (mlim, sky_cov).

Upgrades:

- add a sky footprint map and evaluate p_detect as a function of RA/Dec
- include time dependence (where surveys looked when)
- include a more realistic phase function and bandpass conversions
- incorporate infrared constraints (e.g., WISE‑like limits) if you have a model

---

## 4) Calibrate weights and hyperparameters

Lens weights are not “true” likelihood exponents; they are practical knobs.

A product‑grade calibration loop looks like:

1) Choose a baseline dataset and fixed prior mode.
2) Run injection tests (see `docs/09_VALIDATION.md`).
3) Adjust weights/hyperparameters until the injected truth is recovered reliably.
4) Lock the defaults and version them.

If you want to go further:

- learn weights by maximizing predictive performance on injected simulations
- or by matching published constraints (treat papers as weak supervision)

---

## 5) Add a real posterior sampler (optional)

The current Q‑SEARCH + Q‑REFINE behaves like a deterministic beam search / cross‑entropy method.

If you want a more principled posterior sample:

- add MCMC (Metropolis‑Hastings) with the same lens suite
- add SMC (sequential Monte Carlo)

Both can be implemented without changing the lens interfaces.

---

## 6) Add “product features” without breaking scientific honesty

A monetizable UI can add:

- interactive toggles for weights and priors
- clear display of what each lens contributed (explainability)
- saved run artifacts (summary + dataset digests)
- stable “run IDs” = hash(code_version, cfg_digest, tno_digest, seed)

Be careful:

- don’t claim discovery
- don’t present a single coordinate as “the” location
- always show uncertainty and sensitivity to assumptions

---

## Where to put upgrades in code

- New lenses: `aqm/apps/planet9/lenses.py` (or create `lenses_*.py` and import)
- Data ingestion: `aqm/apps/planet9/tno_data.py` and `aqm/apps/planet9/jpl_sbdb.py`
- Core loop: `aqm/apps/planet9/qphi.py`

