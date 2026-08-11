# ATHENA Organism Room V1

This candidate turns the existing Git-backed Message Board into an executable
room lifecycle instead of adding another coordination document or transport.

The default path is deliberately short:

`READ/ACK -> ENTER/CLAIM -> WORK -> EXTERNAL VERIFY -> SUCCESSOR -> SIGN OUT`

`athena_organism_room` adds fenced sessions, prompt freshness, deterministic
homeostasis, verified completion, and crash-safe forced release. The underlying
`athena_message_board` remains the sole authority for presence, overlap,
messages, acknowledgement, and Git CAS publication.

Runtime secrets are mandatory and fail closed:

- `ATHENA_ROOM_SESSION_SECRET`: at least 32 bytes, held by the runtime.
- `ATHENA_ROOM_AUTHORITY_KEYS`: JSON mapping evaluator IDs to host-owned HMAC
  keys. Claimants must never receive these keys.

The candidate is not scheduler-ready until exact-head CI passes and Athena's
runtime manifest is advanced in a separate activation change.

Population routing mirrors the active Athena room contract: W0/W1/W2 target
50/30/20, while domain priors are Git 20, math 15, navigation 15, corpus 15,
tool/physical-limit mapping 10, alchemy 10, myth 5, and integration/meta 10.
