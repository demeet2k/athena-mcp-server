# Data pipeline (TNO inputs)

Q‑PHI is only as good as its input dataset. The default demo dataset is synthetic and exists purely to prove the pipeline works end‑to‑end.

For *semi‑accurate* results you should supply a curated list of “extreme” TNOs from reputable sources (MPC/JPL), and you should understand how selection bias affects the apparent clustering statistics.

---

## What Q‑PHI expects

Each TNO is represented by a single set of osculating Keplerian elements:

- semimajor axis `a` (AU)
- eccentricity `e`
- inclination `i` (degrees)
- longitude of ascending node `Omega` (degrees)
- argument of perihelion `omega` (degrees)
- mean anomaly `M` (degrees, optional)

These are treated as a snapshot (epoch effects are ignored in this simplified model).

---

## CSV format

The CLI accepts a CSV via `--tno-csv`.

Minimum required columns:

- `name`
- `a_au` (or `a`)
- `e`
- `i_deg` (or `i` / `incl_deg`)
- `Omega_deg` (or aliases: `lan_deg`, `node_deg`, `long_asc_node_deg`, `Omega`, `LAN`)
- `omega_deg` (or aliases: `argp_deg`, `peri_arg_deg`, `argument_of_perihelion_deg`, `omega`)

Optional:

- `M_deg` (or `M` / `mean_anomaly_deg`) — if omitted, Q‑PHI sets `M=0`.

### The Omega vs omega pitfall (very important)

- **Omega (Ω)** = longitude of ascending node
- **omega (ω)** = argument of perihelion

They are often both called “omega” in sloppy datasets.

If your input file does not clearly separate these two angles, Q‑PHI cannot interpret the geometry correctly.

---

## Filtering to “extreme” TNOs

After loading, Q‑PHI applies a broad “extreme” filter:

- `a >= cfg.tno_a_min_au` (default 250 AU)
- `q = a(1-e) >= cfg.tno_q_min_au` (default 30 AU)

These defaults are intentionally broad.

**Tip:** If you have a small curated set of well-known extreme objects, you may want to bypass filtering by setting `--tno-a-min` and `--tno-q-min` to very low values.

---

## Fetching from NASA/JPL SBDB Query API (internet)

If you run with `--fetch-jpl`, Q‑PHI calls the SBDB Query API and extracts orbital elements.

Key notes:

- Q‑PHI makes a single request (no concurrency).
- You can limit the number of returned objects with `--jpl-limit`.
- The SBDB API can change; if you are shipping a product, you should add caching and monitoring.

Because this repo is designed to work offline, SBDB fetching is **optional** and falls back to the demo dataset if the request fails.

---

## Data provenance and digests

Every run records:

- a deterministic digest of the full input dataset (`tno_digest`)
- a deterministic digest of the run configuration (`cfg_digest`)

These appear in `summary.json` and (when enabled) in the AQM tile stored in the Merkle store.

This supports:

- reproducibility (“what exactly did we run?”)
- caching
- defensible product outputs

---

## Recommended upgrades for real accuracy

If you want this to be genuinely useful to observers:

1) **Use a curated TNO list** and keep it versioned.
2) Track element **epochs** and (ideally) propagate to a common epoch.
3) Track discovery circumstances / survey biases (for debiasing).
4) Replace “extreme” selection with a scientifically justified selection rule.

See `docs/06_EXTENDING_AND_CALIBRATION.md` and `docs/09_VALIDATION.md`.
