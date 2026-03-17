# AQM Kernel (Merkle replay skeleton)

The AQM kernel exists to turn computations into **auditable artifacts**.

In plain terms:

- Every stored object is serialized canonically and hashed.
- Dependencies are explicit hashes.
- You can replay the object from bytes and verify it reproduces the hash.

This is useful for monetization because it lets you prove:

- which config + data produced a given prediction
- that the output wasn’t modified after the fact

---

## Core concepts

### KernelObject

Anything that can be stored is a `KernelObject`.

Properties:

- canonical serialization
- deterministic hash

### MerkleStore

A content-addressed storage layer:

- `put(obj)` -> returns hash
- `get(hash)` -> returns raw bytes / reconstructed object
- `verify_hash(hash)` -> checks determinism
- `closure(root_hash)` -> returns full dependency closure

### Tile

A Tile is the primary “unit of meaning”:

- **Seed**: minimal parameters needed to reconstruct meaning
- **Payload**: the computed content (or references)
- **Cert hooks**: obligations and claims about evaluation
- **Ledger hooks**: deterministic audit trail

Tiles are addressed using a compact “chapter / lens / facet” address string.

---

## How Q‑PHI uses the kernel

If `QPHIConfig.store_dir` is set, the Q‑PHI run:

1) builds a `CertificateBundle` with run obligations
2) stores the `Ledger`
3) stores a Tile containing:
   - the full config
   - the summary
   - the input dataset digest
   - references to output filenames

The returned `summary.json` includes:

- `tile_hash`
- `store_dir`

This gives you a stable, replayable anchor for each published run.

---

## Minimal example

Run the kernel demo:

```bash
python -m aqm.cli demo
```

This creates a `.aqm_store_demo` directory with a tiny example tile set and prints a JSON summary.

---

## Practical product note

If you ship this commercially, you can treat the Tile hash as your “run ID”.

- Users can verify a run by re-running with the same seed/config/data and checking the digest.
- You can sign or notarize the tile hash externally if you want stronger provenance.
