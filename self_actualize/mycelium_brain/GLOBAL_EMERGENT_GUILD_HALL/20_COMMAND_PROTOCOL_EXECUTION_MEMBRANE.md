# Command Protocol Execution Membrane

This surface is the Hall-facing execution view of the command membrane.

## Function

The Hall receives command packets only after:

- detection
- packetization
- selective route choice

and exposes them as ownerable execution pressure rather than raw filesystem noise.

## Active Execution Surface

This membrane tracks:

- active event queue
- selected target set
- first-lease claim state
- worker lease status
- duplicate suppression
- route-quality receipts

## Hall Law

- no command event becomes Hall pressure until it is routed
- no routed event becomes owned work until a lease is claimed
- no claimed event becomes persistent Hall work until promotion upserts a Hall front
- command events may open Hall work when they affect:
  - implementation
  - repair
  - indexing
  - math insertion
  - algorithmization
  - executable development

The Hall command queue, claim board, and route-quality board are now generated from ledgers and front registries rather than maintained as descriptive prose.

## Duplicate Suppression

The Hall should not receive the same pressure five times because one file modified five times in a short burst.

That suppression is handled by:

- watcher dedupe window
- selective routing
- capillary reinforcement / decay

## Q-SHRINK Boundary

Q-SHRINK mirrors only landed, witnessed, or explicit frontier-typed command matter.
It does not govern the command membrane.
