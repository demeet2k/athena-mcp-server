# Quickstart

## Install

From the repo root:

```bash
python -m pip install -e .
```

Dependencies are intentionally minimal:

- `numpy`
- `requests` (only required if you use `--fetch-jpl`)

---

## Run a full demo

This runs on the built‑in *synthetic* extreme‑TNO sample (so you can verify the pipeline end‑to‑end without internet or external data):

```bash
qphi-p9 --seed 42 --n-initial 30000 --refine-rounds 2
```

Outputs are written to `qphi_out/` by default.

> Tip: for fast local iteration, start smaller:
>
> ```bash
> qphi-p9 --seed 42 --n-initial 5000 --elite-keep 100 --refine-rounds 1 --offspring-per-elite 10
> ```

---

## Run with your own TNO dataset (CSV)

Prepare a CSV with at least these columns:

- `name`
- `a_au`
- `e`
- `i_deg`
- `Omega_deg`
- `omega_deg`
- `M_deg` (optional)

Then run:

```bash
qphi-p9 --tno-csv my_extreme_tnos.csv --n-initial 80000 --elite-keep 500
```

See `docs/04_DATA_PIPELINE.md` for data notes and pitfalls (Ω vs ω naming, filtering, epoch issues).

---

## Run with NASA/JPL SBDB Query API (internet required)

```bash
qphi-p9 --fetch-jpl --jpl-limit 200 --n-initial 80000
```

---

## Plot the sky samples (optional)

If you want a quick visualization, install matplotlib:

```bash
python -m pip install matplotlib
```

Then run:

```bash
python examples/plot_sky_samples.py qphi_out/sky_samples.csv
```

This writes `qphi_out/sky_samples.png`.

This is convenient, but **not** a replacement for a curated MPC/JPL workflow if you need scientific-grade inference.

---

## What to look at first

1) `qphi_out/summary.json`
   - posterior mean direction (`sky_center_ra_deg`, `sky_center_dec_deg`)
   - containment radii (50% / 90%)
2) `qphi_out/candidates.csv`
   - elite samples with orbital/physical params and per-lens log contributions
3) `qphi_out/sky_samples.csv`
   - RA/Dec + weights suitable for a probability map
4) `qphi_out/ledger.json`
   - event log describing exactly what happened (deterministic audit)

---

## Reproducibility checklist

For a run to be reproducible you need:

- the same code version
- the same `cfg_digest`
- the same `tno_digest` (input dataset)
- the same `seed`

All of these are recorded in `summary.json`.
