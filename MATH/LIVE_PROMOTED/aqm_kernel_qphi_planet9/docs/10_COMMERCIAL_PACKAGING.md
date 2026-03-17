# Commercial packaging notes (monetization)

This document is *not legal advice*. It is practical engineering/product guidance.

Q‑PHI can be monetized as a **search‑prior generator** for observers, but only if you ship it honestly:

- as a probabilistic tool (not a guarantee),
- with transparent assumptions,
- with reproducibility and versioning.

---

## 1) Avoid overclaiming

What you can safely say:

- “This generates *candidate sky regions* compatible with a chosen dataset and assumptions.”
- “This is a ranked search prior.”

What you should not say:

- “We can locate Planet Nine.”
- “This proves Planet Nine is here.”

Your UI should always expose uncertainty:

- show probability contours / heatmaps
- show multiple credible regions if they exist
- show the sensitivity of results to lens weights / priors

---

## 2) Product features that people will pay for

The raw algorithm is only half the value. The other half is packaging:

1) **A clean sky map UI**
   - plot `sky_samples.csv` as a probability cloud or binned heatmap
   - allow filtering by magnitude (`m_est`) and distance (`r_au`)

2) **Scenario management**
   - “Prior preset” buttons (broad / literature‑based)
   - saved configs and dataset versions

3) **Reproducible run IDs**
   - compute a stable run identifier from:
     - code version
     - config digest
     - dataset digest
     - seed

4) **Speed controls**
   - expose “fast / medium / deep” settings that map to:
     - `n_initial`
     - `elite_keep`
     - `refine_rounds`
     - `offspring_per_elite`

5) **Audit report export**
   - ship a single PDF/HTML report containing:
     - the config
     - dataset digest and object list
     - lens diagnostics
     - the final sky map

---

## 3) Operational practices (for reliability)

### Caching

Most runs repeat. Cache on:

- `cfg_digest`
- `tno_digest`
- `seed`
- code version

If the cache key matches, you can return stored results immediately.

### Versioning

- keep a changelog
- pin dataset versions
- when you update lens code, run regression tests and compare outputs

---

## 4) Data and provenance

If you use external sources (MPC/JPL), you must:

- store a copy (or at least a digest + query spec) of the exact dataset used
- comply with the source’s usage policies

Your product should always disclose:

- the dataset source and date
- filtering rules (“extreme TNO” cut)

---

## 5) A realistic commercial pitch

A credible product pitch is:

- “Generate and visualize candidate search regions for observers”
- “Run multiple assumptions quickly”
- “Track how the prediction changes as new objects are discovered”

That is valuable even if Planet Nine does not exist, because the tool still teaches orbital geometry, survey constraints, and probabilistic search planning.
