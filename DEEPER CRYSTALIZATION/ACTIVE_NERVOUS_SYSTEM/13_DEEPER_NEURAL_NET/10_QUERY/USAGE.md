# Query Usage

```powershell
# Document card
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" doc DOC0000

# Fuzzy lookup
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" doc "manuscript seed"

# Strongest neighbors
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" neighbors DOC0000 --mode cross-family --limit 5

# Canonical pair card
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" pair DOC0000 DOC0001

# Slice by element or chapter
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" slice --element Fire --limit 8
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" slice --chapter Ch11 --limit 8

# Zero-point routes
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" zero-point --limit 12 --write

# Chapter drafting-prep packs
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" chapter-pack Ch03 --limit 8 --write
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" chapter-pack Ch10 --limit 8 --write
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" chapter-pack Ch12 --limit 8 --write
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" chapter-pack Ch14 --limit 8 --write

# Materialized frontier plan lattice
python "C:\Users\dmitr\Documents\Athena Agent\DEEPER CRYSTALIZATION\deeper_neural_net_query.py" plan-grid frontier4 --chapter Ch10 --lane chapter_tile_and_handoff --pass manuscript_closure --write
```
