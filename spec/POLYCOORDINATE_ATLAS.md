# Polycoordinate Atlas / Coordinate Synesthesia

For object x with applicable charts C_i:

`P(x) = {C_i(x)}`.

Built-in atlas charts are KC144, JSPACE, SCALE, LINEAGE, TIME, LIMINAL, CUT_LM, EVIDENCE_AUTHORITY, KC27, KC54, BR21, F37, DLS, FRACTAL_4x3N, SQUARE_FLOWER_CLOUD_FRACTAL, HILBERT, RIEMANN, and DISCIPLINE_NATIVE. The atlas is open-world: additional named charts are admitted without changing the core schema.

## Transform matrix

For lawful chart pairs:

`T_ij : C_i -> C_j`.

The runtime maintains a sparse directed transform matrix and computes subject-specific coverage over currently resolved charts:

`rho_T(x) = |{(i,j): C_i(x),C_j(x) resolved and T_ij registered}| / (m_x(m_x-1))`.

This prevents a long coordinate list from masquerading as synesthetic navigation.

## Cross-chart defect

A transform implementation can later compute:

`delta_ij(x)=d_j(T_ij(C_i(x)), C_j(x))`.

A nonzero defect is typed research pressure: loss, bad transform, semantic collision, path dependence, curvature, missing variable, or new structure. The registry stores transform identity and explicit loss model; it does not manufacture numeric defects when no executable transform/test exists.

## Holonomy

For closed route gamma=(i0,i1,...,ik=i0):

`H_gamma(x)=T_{i_{k-1}i_k}...T_{i_0i_1}(C_{i0}(x)) - C_{i0}(x)`.

`athena_record_holonomy` stores measured start, returned state, defect and optional metric. A loop is never declared flat merely because all route edges exist.
