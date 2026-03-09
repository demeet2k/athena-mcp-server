# Parallel Agent Queue

## Control Law

The runtime should never hold only one live folio in mind.
Lane Alpha is the active authoritative build.
Lane Beta is the immediate successor shadow lane.
Lane Gamma is the preheated follow-on lane after that.
Lane Delta is the buffered lane after Gamma.
Lane Epsilon extends the queue past the first local buffer.
Lane Zeta keeps the mid-horizon successor already warm.
Lane Eta keeps the far-horizon successor visible.
Lane Theta preserves one more deep reserve so the queue does not collapse back to a short horizon.

## Live Lanes

### Lane Alpha

- role: `primary build lane`
- macro step: `MACRO_112_F057V`
- folio: `F057V`
- book: `Book I - Herbal / materia medica`
- section: `sections/FULL_PLANT.md`
- crystal: `crystals/PLANT_CRYSTAL.md`
- next after handoff: `MACRO_113_SECTION_SYNTHESIS`

### Lane Beta

- role: `shadow successor lane`
- macro step: `MACRO_147_F087R`
- folio: `F087R`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_148_F087V`

### Lane Gamma

- role: `preheated follow-on lane`
- macro step: `MACRO_148_F087V`
- folio: `F087V`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_149_F088R`

### Lane Delta

- role: `buffer lane after the follow-on`
- macro step: `MACRO_149_F088R`
- folio: `F088R`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_150_F088V`

### Lane Epsilon

- role: `mid-horizon reserve lane`
- macro step: `MACRO_150_F088V`
- folio: `F088V`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_151_F093R`

### Lane Zeta

- role: `extended reserve lane`
- macro step: `MACRO_151_F093R`
- folio: `F093R`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_152_F093V`

### Lane Eta

- role: `far-horizon reserve lane`
- macro step: `MACRO_152_F093V`
- folio: `F093V`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_153_F094R`

### Lane Theta

- role: `deep queue stabilization lane`
- macro step: `MACRO_153_F094R`
- folio: `F094R`
- book: `Book V - Pharmaceutical 1`
- section: `sections/PHARMACEUTICAL_1_FULL.md`
- crystal: `crystals/PHARMACEUTICAL_1_CRYSTAL.md`
- next after handoff: `MACRO_154_F094V`

## Lane Rule

When Lane Alpha hands off, every remaining lane slides forward by one position, and the deepest available successor repopulates the last open lane. This file must be rewritten on every handoff so eight successor lanes already exist before Alpha is finished.
