# AtlasForge

AtlasForge is a modular **math + verification + memory** framework.

It has three integrated layers:

1. **Universal Harmonic Framework (UHF)**: Poles/Lenses/Layers/Depth → a 4×4×4×4 = 256-cell “crystal” taxonomy  
2. **Proof-carrying kernel**: Blueprint → Plan → Recipe → Certificates → Verification → Replay  
3. **Memory Atlas**: structured notes + search + dependency graph + sessions + book export

Version: `4.0.0-ABSOLUTE-FINAL-ULTIMATE`

---

## Quick install (editable)

From the repository root:

```bash
pip install -e .
```

---

## Quick verification

Run the built-in verification script:

```bash
python -m atlasforge.verify_installation
```

---

## Enable the memory bank

```bash
export ATLASFORGE_MEMORY_DIR=~/.atlasforge_memory
```

Now any recipe execution and Atlas usage can automatically log entries.

---

## Minimal example

```python
from atlasforge import Atlas, RootConstraint, Interval

atlas = Atlas.from_env()

bp = atlas.blueprint(
    name="sqrt(2)",
    constraint=RootConstraint(H=lambda x: x*x - 2, domain=Interval.closed(1,2)),
)

recipe = atlas.solve(bp, verified=True, note="Certified enclosure via interval Newton.")
hits = atlas.recall("sqrt(2)")
```

---

## Documentation

Start here:

- `docs/README_COMPLETE.md`
- `docs/ATLASFORGE_FINAL_MANUAL.md` (final integrated manual)

Legacy internal docs are also available under `atlasforge/docs/`.
