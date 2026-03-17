# Q‑PHI algorithm (Planet Nine / Planet X)

Q‑PHI is a **deterministic, audit‑friendly inference loop** that searches over a candidate Planet Nine parameter space (Θ) and produces a **weighted posterior cloud** of candidate sky positions.

It is built to be:

- **Functional now** (runs end‑to‑end with minimal dependencies)
- **Easy to audit** (every term in the score is explicit and separable)
- **Easy to extend** (add lenses, improve physics, plug in survey models)

---

## The target: a *posterior over Θ*

We define a candidate Planet Nine parameter record:

- **Orbital elements** (heliocentric, ecliptic frame):
  - semimajor axis **a** (AU)
  - eccentricity **e**
  - inclination **i** (deg)
  - longitude of ascending node **Ω** (deg)
  - argument of perihelion **ω** (deg)
  - mean anomaly **M** (deg) — used to infer a current orbital position
- **Physical parameters** (for brightness constraints):
  - mass (Earth masses)
  - albedo
  - bulk density

Together these are `PlanetNineTheta`.

We want a distribution:

\[
P(\Theta \mid \text{TNO data}, \text{assumptions}) \propto P(\Theta)\,\prod_{k} \mathcal{L}_k(\Theta)^{w_k}
\]

Where:

- \(P(\Theta)\) is the prior defined by `QPHIConfig` ranges.
- \(\mathcal{L}_k\) are “lenses” (likelihood proxies) computed from the extreme‑TNO dataset.
- \(w_k\) are user‑tunable lens weights.

> Practical note: Q‑PHI is implemented as a **Monte Carlo search + elite refinement** rather than a full MCMC sampler. That choice keeps the code small, deterministic, and easy to productize.

---

## Pipeline summary

### Stage A — data selection

1) Load TNOs from one of:
   - built‑in demo dataset (synthetic)
   - user CSV
   - NASA/JPL SBDB Query API
2) Filter to “extreme” objects:
   - `a >= cfg.tno_a_min_au`
   - `q = a(1-e) >= cfg.tno_q_min_au`

This yields a list of `TNO` records with orbital elements.

### Stage B — build lens suite

A lens is any object with:

- `score(theta) -> LensReport(lens_id, log_score, details)`

Q‑PHI builds the lens suite in a deterministic order:

1) orbit plausibility (hard-ish reject)
2) perihelion clustering
3) pole alignment
4) precession dominance
5) detectability

Each lens returns a **log score**. Q‑PHI forms the weighted sum:

\[
S(\Theta) = \sum_k w_k \; \log \mathcal{L}_k(\Theta)
\]

### Stage C — Q‑SEARCH (initial Monte Carlo)

We sample `cfg.n_initial` candidates Θ from the prior (or a proposal distribution) and compute scores.

Two proposal modes exist:

- `proposal_mode=broad`: sample i/Ω/ω uniformly
- `proposal_mode=data_guided`: compute hints from the TNO sample and propose near them

Data‑guided hints are:

- mean TNO perihelion longitude: \(\bar{\varpi}_{\text{TNO}}\)
- inferred Planet Nine perihelion longitude mean:
  - because the lens assumes anti-alignment, \(\varpi_9 \approx \bar{\varpi}_{\text{TNO}} - 180°\)
- mean orbital pole direction (converted to \(\bar{i}, \bar{\Omega}\))

**Important:** this guidance only changes *proposal efficiency*, not the lens score itself.

### Stage D — elite selection

We keep the top `cfg.elite_keep` candidates by score.

### Stage E — Q‑REFINE (elite jitter)

For `cfg.refine_rounds` rounds:

- For each elite candidate, spawn `cfg.offspring_per_elite` variants by jittering parameters.
- Score all candidates in the pool.
- Keep the best `elite_keep`.

This acts like a deterministic “beam search” / “CEM” (cross‑entropy‑like) refinement.

### Stage F — posterior sky summary

Each posterior candidate includes a derived **heliocentric position vector** from its orbital elements.

We compute:

- weighted mean sky direction (RA/Dec)
- weighted containment radii (50% and 90%) around the mean direction

Weights are derived via a softmax of log scores with a temperature `posterior_temperature`.

---

## What makes this “semi‑accurate” vs “toy”

Q‑PHI is intentionally in between:

- It is **not** a purely decorative simulation: it uses real orbital element geometry and explicit scoring terms.
- It is also **not** a full n‑body dynamical inference with survey selection functions.

Accuracy improves sharply when you:

1) replace the demo TNO sample with curated MPC/JPL data,
2) tune lens weights/hyperparameters against known published constraints,
3) replace the detectability lens with real survey coverage models,
4) upgrade the secular dynamics lens beyond quadrupole order.

Those upgrades are documented in `docs/06_EXTENDING_AND_CALIBRATION.md`.

---

## Determinism contract

Under fixed:

- code version
- `cfg` (full config digest)
- input dataset digest
- random seed

Q‑PHI will produce the same output files.

This is designed to support:

- reproducible “claims” about a run
- caching
- monetizable workflows where you need *auditability* (what did we run, with which data?)

