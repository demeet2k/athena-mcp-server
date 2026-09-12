# Current-source artifact canary

The historical v3.3 canary binds an older published release. It cannot qualify a
new scheduler or Wiki source. `source-canary.yml` checks out the exact PR head
(or dispatched commit), builds that source, and observes an unpublished candidate.

The route creates a disposable registry bound only to the runner's loopback
interface. It obtains the actual single-platform OCI/Docker manifest bytes and
cross-checks the registry digest header. The image reference uses the manifest
digest. It independently verifies the config blob against the manifest descriptor,
Docker's config ID and RepoDigests, the source revision label, the non-root user,
and every installed Python file against the tracked source inventory. A config
digest or archive checksum is never relabeled as a manifest digest.

Two containers use this exact image with separate fresh SQLite volumes, distinct
ephemeral bearer tokens, read-only roots, dropped capabilities, one CPU and 512 MiB
each, and loopback HTTP ports. The existing observer seeds a semantic witness,
restarts both containers, checks durable readback and catalogs, and collects 31
paired samples over at least 60 seconds. Existing error, latency, readiness and
replay gates apply. Failure retains available diagnostics without manufacturing a
passing result. The wrapper also requires every structural comparison to match.
Docker's observed restart counter is preserved in full; the planned manual restart
is a separate field and grants no subtraction credit against automatic attempts.
The first live candidate had raw counter zero after one manual restart on each
container. A regression case requires rollback for one observed automatic attempt.
See [Docker restart-policy inspection](https://docs.docker.com/reference/cli/docker/container/run/#restart-policies---restart).

Evidence includes raw manifest/config bytes, safe image and container identities,
source/installed Python inventories, observations, assessment, witness, a linked
result and a saved image archive. Container environment arrays are excluded to
avoid retaining bearer tokens. The workflow artifact retains evidence for 30 days.
The local registry and created containers/volumes are cleaned up. Its loopback
image reference is not a durable public distribution endpoint. The archive is a
transport artifact; verify its checksum, reload, and re-observe image identity
before reuse. Preserve the workflow artifact elsewhere if retention must be longer.

Run on a disposable Docker host from a clean committed checkout:

```sh
python -B -m deploy.source_canary --source-head <full-commit> --workflow-run-id <run-id>
```

This witnesses same-image replication and restart behavior, not comparison against
the installed release, multi-host fault tolerance, independent decision quality,
production data migration, or runtime cutover. Source labels and receipts are
host-observed evidence, not signed independent provenance. Mutable build base and
build dependencies prevent a claim of reproducible rebuilding. Full repository
CI and its exact-head promotion receipt remain separate merge requirements.
No production secrets, state, traffic or launch configuration are used. Candidate
witnesses explicitly have no release coordinates and no activation authority.
