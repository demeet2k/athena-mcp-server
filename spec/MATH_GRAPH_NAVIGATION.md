# Mathematical + Graph Navigation

## Mathematical registry

Each consequential formal object receives a MATH identity:

`MATH = <kind,symbol,latex,assumptions,status,owner,eid>`.

Kinds: DEFINITION, THEOREM, LEMMA, COROLLARY, OPERATOR, INVARIANT, EQUATION, CONJECTURE, MODEL, ALGORITHM, METRIC, FALSIFIER.

A formula in prose is not enough. The owner is the exact output manifestation (MID), and the EID provides causal provenance.

## JSPACE graph

Binary relation:

`e=(src, relation, dst, EID, attrs)`.

Higher relation:

`h=(relation,{v_1,...,v_n},EID,attrs)`.

The runtime supports directed shortest-path navigation with optional relation filters. Hyperedges remain first-class and are not flattened into arbitrary pairwise edges.

## Dense navigation

`DENSE_NAV(id)` returns identity, current head, KC144 station, version chain, manifestations, coordinate rows, transform matrix, JSPACE in/out/hyperedges, mathematical objects, crystals and RETURN routes.

This is the required distinction:

`coordinate label != navigation`.
