"""Example: plot Q‑PHI sky samples.

Reads `sky_samples.csv` and writes a simple scatter plot.

Usage:
    python examples/plot_sky_samples.py qphi_out/sky_samples.csv

Output:
    sky_samples.png (in the same directory as the CSV)

Notes:
- This is a *quick visualization*, not a publishable all-sky probability map.
- For real sky maps you may want HEALPix binning or other spherical density estimates.
"""

import sys
from pathlib import Path

import csv

import matplotlib.pyplot as plt


def main(argv: list[str]) -> None:
    if len(argv) < 2:
        print("Usage: python examples/plot_sky_samples.py <sky_samples.csv>")
        raise SystemExit(2)

    csv_path = Path(argv[1])
    if not csv_path.exists():
        raise FileNotFoundError(str(csv_path))

    ra = []
    dec = []
    w = []

    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ra.append(float(row["ra_deg"]))
            dec.append(float(row["dec_deg"]))
            w.append(float(row["weight"]))

    # Scale point size by weight (with a floor so low-weight points are still visible)
    sizes = [max(2.0, 800.0 * wi) for wi in w]

    plt.figure()
    plt.scatter(ra, dec, s=sizes, alpha=0.6)
    plt.xlabel("RA (deg)")
    plt.ylabel("Dec (deg)")
    plt.title("Q‑PHI sky samples")
    plt.grid(True)

    out_path = csv_path.parent / "sky_samples.png"
    plt.savefig(out_path, dpi=180)
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main(sys.argv)
