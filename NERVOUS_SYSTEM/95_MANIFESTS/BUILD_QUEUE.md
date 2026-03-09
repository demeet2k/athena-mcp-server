# BUILD QUEUE

## Priority Order

1. **Phase 1**: Toolkit consolidation (13 protocols -> 80_TOOLKIT/)
2. **Phase 2**: Ledgers + manifests + runbooks
3. **Phase 4**: MATH domain capsules (~30-40 files)
4. **Phase 5**: Voynich domain capsules (~20-30 files)
5. **Phase 6**: Remaining domain capsules (~25-35 files)
6. **Phase 7**: Edge graph construction (6 files)
7. **Phase 8**: Crystal tile population (ongoing -- priority: Ch01, Ch11, Ch09, Ch06, Ch03)
8. **Phase 9**: Deprecation markers in old systems

## Parallelizable

- Phases 4, 5, 6 can run in parallel (independent domains)
- Phase 7 requires Phases 4-6 (needs capsules for edge mapping)
- Phase 8 requires Phase 7 (needs edges for tile guidance)
