# Destructive active-tree reset

The active `master` tree is rebuilt from scratch. Previous repository state is pinned at `archive/pre-rebuild-2026-08-07` and remains in Git history, but no old file is canonical merely because it existed before the rebuild.

Legacy admission:
`DISCOVER → HASH → CLASSIFY → CCR SEARCH → OID/VID → SOURCE → KC144 → JSPACE → SCALE → TEST/EVIDENCE → STATUS`.

Do not bulk-copy legacy folders into the runtime.
