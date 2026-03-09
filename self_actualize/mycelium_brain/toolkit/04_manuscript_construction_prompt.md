# Manuscript Construction Prompt

Use this when building or revising the skeleton of a full manuscript.

Core requirements:

- 21 chapters
- 16 appendices
- every chapter is a 4x4 tile
- every appendix is a routing hub and compressed 4x4 tile
- abstract must function as a metro map
- all outputs must be addressable and routeable

Chapter skeleton rule:

- each chapter has 4 major lenses: S / F / C / R
- each lens has 4 facets
- each facet has 4 atoms

Overlay rule:

- compute chapter station code in base 4
- compute `omega`, `alpha`, `rho`, and `nu`
- stamp every chapter with:
  `[oArc alpha | oRot rho | tLane nu | omega=...]`

Router rule:

- use the bounded router with mandatory signature `Sigma = {AppA, AppI, AppM}`
- keep hub count bounded
- prefer explicit metro rides over vague references
