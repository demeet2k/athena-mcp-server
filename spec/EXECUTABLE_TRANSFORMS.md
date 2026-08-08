# Executable Coordinate Transforms v2.2

A registered relationship between charts is not automatically a mathematical transform.

## Transform modes

- `LOOKUP` — navigational cross-reference by shared subject identity. It can retrieve another resolved chart but does not derive it.
- `DERIVATION` — target is computed from source by a declared program.
- `PROJECTION` — derivation that intentionally loses information.
- `EMBEDDING` — derivation into a larger carrier.
- `ISOMORPHISM` — candidate information-preserving derivation.
- `APPROXIMATION` — derivation with declared loss/metric.

`LOOKUP != DERIVATION` is constitutional.

## Safe transform DSL

Executable transforms use a declarative JSON AST, not arbitrary Python/code execution. Supported primitives include identity, constants, field/path access, object/array construction, coalesce, arithmetic, floor/ceil/round/abs, and concatenation.

For subject x:

`T_ij(x) = Eval(program_ij, C_i(x))`.

If an independently resolved `C_j(x)` exists, the runtime compares derived and observed coordinates using an explicit metric.

## Coverage vector

For `m_x` resolved charts:

`N_x = m_x(m_x-1)` directed possible pairs.

The runtime reports three non-equivalent densities:

`rho_nav = registered_pairs / N_x`

`rho_exec = executable_pairs / N_x`

`rho_der = derivational_pairs / N_x`.

A system may have high navigational coverage and zero derivational coverage.

## Holonomy gate

For closed route `gamma=(i0,...,ik=i0)`:

`H_gamma(x)=T_gamma(C_i0(x))-C_i0(x)`.

The runtime only auto-promotes a holonomy observation if **every** route edge is derivational. If any edge is `LOOKUP`, holonomy status is `N/A_LOOKUP_ROUTE` rather than a counterfeit zero-curvature result.
