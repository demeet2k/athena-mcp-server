from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from .qphi import QPHIConfig, load_tnos_for_run, run_qphi


def _int(x: str) -> int:
    return int(float(x))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="qphi-p9",
        description="Q-PHI: a deterministic multi-lens Monte Carlo inference pack for Planet Nine (Planet X).",
    )

    p.add_argument("--tno-csv", default=None, help="CSV of TNO orbital elements. If omitted, uses built-in demo dataset (unless --fetch-jpl).")
    p.add_argument("--fetch-jpl", action="store_true", help="Fetch extreme TNOs from NASA/JPL SBDB Query API (requires internet).")
    p.add_argument("--jpl-limit", type=_int, default=200, help="Max number of TNOs to fetch from JPL (when --fetch-jpl).")
    p.add_argument("--out-dir", default="qphi_out", help="Output directory.")
    p.add_argument("--store-dir", default=".aqm_store_qphi", help="Merkle store directory for replay artifacts (set '' to disable).")

    p.add_argument("--seed", type=_int, default=42, help="Random seed (deterministic).")
    p.add_argument("--n-initial", type=_int, default=30000, help="Initial Monte Carlo samples.")
    p.add_argument("--elite-keep", type=_int, default=200, help="Number of elites to keep per round.")
    p.add_argument("--refine-rounds", type=_int, default=2, help="Number of elite-jitter refinement rounds.")
    p.add_argument("--offspring-per-elite", type=_int, default=30, help="Offspring per elite per refinement round.")

    # Proposal
    p.add_argument(
        "--proposal-mode",
        choices=["data_guided", "broad"],
        default="data_guided",
        help="Initial proposal strategy (data_guided uses TNO mean pole + perihelion direction to guide sampling).",
    )
    p.add_argument("--proposal-varpi-sigma", type=float, default=50.0, help="Proposal sigma for varpi9 (deg) when --proposal-mode=data_guided.")
    p.add_argument("--proposal-i-sigma", type=float, default=12.0, help="Proposal sigma for inclination i (deg) when --proposal-mode=data_guided.")
    p.add_argument("--proposal-Omega-sigma", type=float, default=35.0, help="Proposal sigma for Omega (deg) when --proposal-mode=data_guided.")

    # Prior presets
    p.add_argument(
        "--prior-mode",
        choices=["broad", "bb2016", "bb2021"],
        default="broad",
        help="Preset prior ranges for Planet Nine parameters (based on published constraints).",
    )

    # Filters
    p.add_argument("--tno-a-min", type=float, default=250.0, help="Minimum TNO semimajor axis (AU) for inclusion.")
    p.add_argument("--tno-q-min", type=float, default=30.0, help="Minimum TNO perihelion (AU) for inclusion.")

    # Detectability (toy survey model)
    p.add_argument("--mlim", type=float, default=22.0, help="Survey 50 percent completeness depth (V mag) used by the detectability lens.")
    p.add_argument("--sky-cov", type=float, default=0.35, help="Fraction of sky considered 'covered' by surveys.")
    p.add_argument("--detect-width", type=float, default=0.6, help="Transition width (mag) for the detectability logistic curve.")
    p.add_argument("--earth-lon", type=float, default=0.0, help="Earth ecliptic longitude (deg) for a tiny geocentric-distance correction.")

    return p


def main(argv: Optional[list[str]] = None) -> None:
    args = build_parser().parse_args(argv)

    store_dir = args.store_dir
    if isinstance(store_dir, str) and store_dir.strip() == "":
        store_dir = None

    # Prior presets (kept here in CLI so the core library stays explicit/transparent).
    a_range = (300.0, 1200.0)
    q_range = (200.0, 500.0)
    i_range = (0.0, 60.0)
    mass_range = (3.0, 15.0)

    if args.prior_mode == "bb2016":
        # Brown & Batygin (2016) arXiv:1603.05712 (broad ranges from their abstract)
        a_range = (380.0, 980.0)
        q_range = (150.0, 350.0)
        i_range = (5.0, 55.0)
        mass_range = (5.0, 20.0)
    elif args.prior_mode == "bb2021":
        # Brown & Batygin (2021) AJ 162, 219. Use a widened ~2σ envelope.
        a_range = (200.0, 800.0)
        q_range = (180.0, 450.0)
        i_range = (0.0, 35.0)
        mass_range = (3.5, 12.0)

    cfg = QPHIConfig(
        seed=args.seed,
        n_initial=args.n_initial,
        elite_keep=args.elite_keep,
        refine_rounds=args.refine_rounds,
        offspring_per_elite=args.offspring_per_elite,
        out_dir=args.out_dir,
        store_dir=store_dir,
        a_range_au=a_range,
        q_range_au=q_range,
        i_range_deg=i_range,
        mass_range_earth=mass_range,
        proposal_mode=args.proposal_mode,
        proposal_varpi_sigma_deg=float(args.proposal_varpi_sigma),
        proposal_i_sigma_deg=float(args.proposal_i_sigma),
        proposal_Omega_sigma_deg=float(args.proposal_Omega_sigma),
        tno_a_min_au=args.tno_a_min,
        tno_q_min_au=args.tno_q_min,
        mlim=float(args.mlim),
        sky_coverage_fraction=float(args.sky_cov),
        detect_width_mag=float(args.detect_width),
        earth_lon_deg=float(args.earth_lon),
    )

    tnos = load_tnos_for_run(args.tno_csv, cfg, fetch_jpl=bool(args.fetch_jpl), jpl_limit=int(args.jpl_limit))
    summary = run_qphi(tnos, cfg)

    out_dir = Path(cfg.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "run_summary_print.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")

    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
