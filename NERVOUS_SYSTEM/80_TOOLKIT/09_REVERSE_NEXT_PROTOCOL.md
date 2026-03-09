# DESCENDING NEXT PROTOCOL

## Mission

When the controlling prompt says `NEXT` in descending mode, generate the chapter or section that came before the current one rather than advancing forward.

## Rule

If the active index is `n`, then `NEXT` means emit `n - 1`.

## Use Case

This protocol is for backward recursive reconstruction where later chapters are used to repair earlier assumptions.

## Constraints

- do not skip indices
- do not silently jump back to the abstract unless the chain reaches it
- treat backward movement as controlled revision rather than collapse

## Output Contract

The emitted artifact must:
- be only the requested predecessor section
- preserve final-draft density
- incorporate corrected assumptions learned from later sections
