# API reference (high level)

This is a **human-written** reference to the most important call points. For implementation details, read the source — the code is intentionally small and direct.

---

## Planet Nine pack

### `aqm.apps.planet9.qphi`

#### `QPHIConfig`

Dataclass containing all hyperparameters for a run.

Key fields:

- `seed`: deterministic RNG seed
- `n_initial`: number of initial Monte Carlo samples
- `elite_keep`: number of elite posterior samples retained
- `refine_rounds`: how many elite-jitter rounds to run
- `offspring_per_elite`: number of jitters per elite per round
- `proposal_mode`: `data_guided` or `broad`
- `a_range_au, q_range_au, i_range_deg, mass_range_earth`: prior ranges
- `w_perihelion, w_pole, w_precession, w_detectability, w_plausibility`: lens weights
- `out_dir`: output directory
- `store_dir`: optional Merkle store directory

#### `load_tnos_for_run(tno_csv, cfg, fetch_jpl=False, jpl_limit=200) -> list[TNO]`

Loads and filters the extreme-TNO sample.

Priority:

1) JPL SBDB fetch (if `fetch_jpl=True`)
2) local CSV (if `tno_csv` provided)
3) built-in demo dataset

Then filters by `cfg.tno_a_min_au` and `cfg.tno_q_min_au`.

#### `run_qphi(tnos, cfg) -> dict`

Runs the full pipeline and writes outputs.

Returns the same dictionary written to `summary.json`.

Side effects:

- writes output files in `cfg.out_dir`
- optionally writes an AQM tile to `cfg.store_dir`

---

### `aqm.apps.planet9.lenses`

Each lens has:

- constructor with hyperparameters
- `.score(theta) -> LensReport`

Lens classes:

- `OrbitPlausibilityLens`
- `PerihelionClusteringLens`
- `PoleAlignmentLens`
- `PrecessionDominanceLens`
- `DetectabilityLens`

---

### `aqm.apps.planet9.tno_data`

- `TNO`: dataclass containing `name` and `OrbitalElements`
- `load_tno_csv(path)`: parse a CSV into `TNO` objects
- `select_extreme(tnos, a_min_au=250, q_min_au=30)`: filter rule
- `demo_extreme_tnos(seed=9)`: synthetic dataset
- `tno_set_digest(tnos)`: SHA-256 digest of the dataset (deterministic)

---

### `aqm.apps.planet9.orbits`

- `OrbitalElements`: dataclass for Keplerian elements
  - `.to_state_vectors()` and `.position_vector()`
  - `.perihelion_longitude_deg()`, `.perihelion_distance_au()`, `.aphelion_distance_au()`
- coordinate helpers:
  - `ecliptic_to_radec_deg(vec)`
  - `xyz_to_lonlat_deg(vec)`
  - `pole_unit_vector(i_deg, Omega_deg)`

---

## AQM Kernel

The kernel is primarily useful if you want content-addressed “run artifacts.”

Top-level imports in `aqm/__init__.py`:

- `TileAddress`
- `KernelObject`, `Tile`
- `MerkleStore`
- `Ledger`
- `CertificateBundle`
- `ExtractionManifest`

For the detailed object model and storage format, see `docs/07_AQM_KERNEL.md`.
