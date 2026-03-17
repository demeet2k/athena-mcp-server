# Documentation Index

This documentation is split into **two layers**:

- **AQM Kernel (audit + replay):** how we represent an inference run as a deterministic, content-addressed artifact.
- **Q‑PHI Planet Nine inference:** how we convert a TNO dataset into a *ranked posterior sky region*.

If you are productizing/monetizing this, you should read the docs in the order below at least once.

---

## Recommended reading order

1) **Quickstart** — `01_QUICKSTART.md`
2) **Q‑PHI algorithm** — `02_QPHI_ALGORITHM.md`
3) **Lens models** — `03_LENSES.md`
4) **Data pipeline** — `04_DATA_PIPELINE.md`
5) **Outputs + reproducibility contract** — `05_OUTPUTS_AND_REPRODUCIBILITY.md`
6) **Extending + calibration** — `06_EXTENDING_AND_CALIBRATION.md`
7) **AQM Kernel internals** — `07_AQM_KERNEL.md`
8) **API reference** — `08_API_REFERENCE.md`
9) **Validation / testing** — `09_VALIDATION.md`
10) **Commercial packaging notes** — `10_COMMERCIAL_PACKAGING.md`

---

## Source materials

If you distributed this repo as a single archive, the original master documents you provided are included under:

- `docs/source_material/`

---

## What Q‑PHI actually outputs

Q‑PHI does **not** output a single “Planet Nine location.”

It outputs:

- a set of **weighted samples** of a candidate Planet Nine orbit + current position (derived from mean anomaly),
- which can be visualized as a **probability cloud** in **RA/Dec**,
- plus a small set of summary statistics (posterior mean direction + 50% / 90% containment radii).

Your product should present this honestly as a *search prior* — “here are the regions most compatible with these assumptions” — and provide users the ability to change those assumptions.

---

## Quick glossary

- **TNO:** Trans‑Neptunian Object.
- **Extreme TNOs:** Distant objects often used in Planet Nine studies; usually selected by large semi‑major axis `a` and/or large perihelion distance `q`.
- **ϖ (varpi):** Longitude of perihelion, `ϖ = Ω + ω`.
- **Ω (Omega):** Longitude of ascending node.
- **ω (omega):** Argument of perihelion.
- **Lens:** A scoring function that converts a candidate planet (`theta`) into a log‑likelihood contribution.
- **Posterior (in this repo):** A softmax‑weighted set of elite candidates from the search/refinement loop.

