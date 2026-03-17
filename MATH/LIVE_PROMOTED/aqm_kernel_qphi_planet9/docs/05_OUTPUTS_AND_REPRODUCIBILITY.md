# Outputs and reproducibility

Q‑PHI is designed around a simple contract:

> Under a fixed (code version, config, input dataset, seed), the run is deterministic and produces the same outputs.

This matters for research **and** for monetization, because it allows:

- caching of runs
- auditability (“which exact data + assumptions produced this map?”)
- regression testing across versions

---

## Output directory layout

By default `qphi-p9` writes to `qphi_out/`.

Typical contents:

- `candidates.csv` — elite posterior samples (orbits + physical params + lens diagnostics + derived sky position)
- `sky_samples.csv` — (RA, Dec, weight) samples, suitable for plotting a probability cloud
- `summary.json` — small summary / run metadata
- `ledger.json` — deterministic AQM‑style ledger of key steps
- `run_summary_print.json` — a pretty printed copy of the returned summary

---

## candidates.csv

One row per elite candidate (posterior sample). Columns include:

Orbital elements and derived distances:

- `a_au, e, i_deg, Omega_deg, omega_deg, M_deg`
- `varpi_deg` (Omega + omega)
- `q_au` perihelion distance
- `Q_au` aphelion distance

Physical parameters:

- `mass_earth`
- `albedo`
- `density_g_cm3`
- `radius_km`
- `H` (absolute magnitude)

Derived sky / geometry:

- `r_au` (heliocentric distance at the sampled mean anomaly)
- `ecl_lon_deg, ecl_lat_deg`
- `ra_deg, dec_deg` (equatorial, using a fixed obliquity)

Lens diagnostics:

- `orbit_plausibility_log`
- `perihelion_clustering_log`
- `pole_alignment_log`
- `precession_dominance_log`
- `detectability_log`

And the combined score:

- `log_score`

---

## sky_samples.csv

This is the primary product output for visualization.

Columns:

- `ra_deg`
- `dec_deg`
- `weight` — softmax weight derived from candidate log scores
- `r_au`
- `m_est` — estimated apparent magnitude from the detectability lens

To make a heatmap:

- bin (ra,dec) into pixels (or HEALPix if you add that dependency)
- sum weights per pixel
- normalize to 1

See `examples/plot_sky_samples.py`.

---

## summary.json

The summary is deliberately small. It includes:

- `code_version` (best effort)
- `seed`
- `n_tnos`
- `tno_digest`
- `cfg_digest` (digest of the model-relevant config; excludes output/storage directories)
- `best_log_score`
- `sky_center_ra_deg, sky_center_dec_deg`
- `containment_radius_50_deg, containment_radius_90_deg`

If the Merkle store is enabled, it also includes:

- `tile_hash`
- `store_dir`

---

## ledger.json

`ledger.json` is a deterministic event log intended for auditability.

It records:

- start of run (seed)
- lens construction
- proposal hints (if used)
- sampling + refinement steps
- output writing

There are no wall‑clock timestamps inside ledger events (only deterministic content), so reruns produce the same ledger.

---

## Merkle store artifacts (optional)

If `--store-dir` is set (default `.aqm_store_qphi`), Q‑PHI will store:

- a CertificateBundle describing obligations (determinism, provenance)
- the run ledger object
- a Tile containing config + summary metadata

This yields a `tile_hash` you can treat as an immutable run identifier.

Practical product idea:

- return `tile_hash` to users as a “run receipt”
- allow re‑loading / replay‑verification of the run metadata

See `docs/07_AQM_KERNEL.md`.
