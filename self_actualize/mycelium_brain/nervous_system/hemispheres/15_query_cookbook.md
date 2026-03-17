# Navigator Query Cookbook

## Exact Record Lookup

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --record-id 368bd2ec7d2e64e2f5739be7
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --path "Athena FLEET\athena_fleet_corpus_atlas.json"
python -m self_actualize.runtime.query_myth_math_hemisphere_brain record --title "settings.local"
```

## Mixed Search

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain search --query aqm --hemisphere MATH --system CoreMetro --anchor DN03
python -m self_actualize.runtime.query_myth_math_hemisphere_brain search --query bridge --route-mode commissure_direct --expanded
```

## Facet Browse

```powershell
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --system GrandCentral
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --lens SC
python -m self_actualize.runtime.query_myth_math_hemisphere_brain facet --hemisphere MYTH
```
