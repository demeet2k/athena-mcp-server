# MIGRATION TO COLLECTIVE GENERALIZED V16 / 3.5.0 / UNIFIED.12

## Source ancestry

V16 branches from the currently qualified V15 public master:

`429a480a80eeefb9e2bff1ea3015adf571d76b0e`.

Current V16 implementation branch head before witness closure began:

`58680badae0800bf8e18cc992c724f8de508ced5`.

The branch is a linear descendant of the qualified V15 base.

`NEW_SUCCESSOR != REPLAY_OLD_BASE`.

If `master` advances before integration, re-read the new master and braid/rebase only after checking that V16's assumptions and release-overlay projections remain valid.

## Semantic transition

Candidate transition:

`COLLECTIVE_CALIBRATED_V15 -> COLLECTIVE_GENERALIZED_V16`.

Runtime manifest:

`ATHENA.RUNTIME.UNIFIED.11 -> ATHENA.RUNTIME.UNIFIED.12`.

Package identity candidate:

`athena-canonical-mcp 3.4.0 -> 3.5.0`.

New coordinate:

`COLLECTIVE_GENERALIZED=<OG,MH,GM,EF,NR,L>`.

## Additive API

V16 adds five RPC names and `athena://collective/v16`.

No V1–V15 RPC or resource may be removed or renamed by this migration.

The V16 dispatcher intercepts only those five names at the `Server` boundary.

## Bounded research migration

The canonical Brain V3.7 names broad Ω16 pressure. The runtime migration must preserve the distinction between that research goal and the current bounded implementation:

- graph posterior -> order-constrained finite linear-Gaussian/BIC DAG family only;
- arbitrary-horizon longitudinal DML/TMLE -> cross-fitted sequential DR over at most six binary treatment stages only;
- non-Gaussian belief -> supplied finite Gaussian mixture under shared linear-Gaussian observation only;
- learned approximation error -> RBF field plus CV residual quantile over explicit witnesses only;
- non-rectangular DRO -> exact supplied-policy evaluation over a finite globally coupled complete-model family only.

Any broader label is a research successor, not a current runtime claim.

## Required pre-integration repairs

The initial V16 implementation advances `athena_mcp.__version__` / `SERVER_INFO` to `3.5.0` and manifest identity to `UNIFIED.12`, while inherited source package/release charts still describe V15/3.4.

Therefore V16 integration is blocked until the following migrate coherently:

1. `pyproject.toml` package version/description;
2. metadata consistency tests;
3. current release-distribution manifest/notes/workflow to a V3.5 candidate surface;
4. current release-distribution tests;
5. CI critical-invariants selectors for the three V16 witness files;
6. documentation/architecture references that assert V15 is the terminal current Collective layer;
7. every imported/copied runtime manifest/resource projection exposed by the V15 holonomy antibody.

Historical V3.4 release evidence must remain historical and immutable.

`OLD_RELEASE_RECEIPT != NEW_RELEASE_EVIDENCE`.

## Proof gates

Required before V16 can become integration-ready:

- syntax PASS;
- full unit corpus PASS;
- V16 constructive tests PASS;
- V16 adversarial tests PASS;
- V16 unified composition/authority tests PASS;
- complete inherited critical-invariants PASS;
- V1–V15 surface retention PASS;
- manifest holonomy PASS;
- subprocess MCP smoke PASS;
- package/wheel metadata identity PASS;
- clean-wheel install PASS for the exact V16 candidate;
- host-bound exact-head trusted qualification PASS.

## Failure policy

If a current chart remains at 3.4/V15/UNIFIED.11 while V16 code advertises 3.5/V16/UNIFIED.12, repair the chart rather than weakening metadata tests.

If a V16 operator cannot satisfy its bounded positive/adversarial tests, repair the operator or narrow the contract. Do not widen the claim language to cover an unproved implementation.

If master advances during qualification, the old branch receipt cannot qualify the rebased/merged SHA.

`BRANCH_RECEIPT != MERGED_HEAD_RECEIPT`.

## Authority boundary

V16 operators remain read-only model/science/control surfaces unless a separate existing mutation interface is explicitly invoked under its own authority contract.

V16 does not acquire authority over:

- Y1;
- canonical JSPACE;
- empirical observation history;
- coordination claims;
- external execution;
- deployment;
- release publication;
- trusted promotion.

## Release boundary

A V3.5 source/release contract may be installed on the branch for qualification, but no tag, GitHub Release, package-index publication, production deployment, traffic activation, or infrastructure mutation is implied by branch CI or trusted exact-head qualification.

`VALIDATED_PACKAGE_CANDIDATE != PUBLISHED_RELEASE`.

## Successor

Do not seat a V17/Ω17 successor merely because V16's bounded implementation exists.

The next successor must be generated from witnessed V16 residuals after integration/qualification, not from the broad Ω16 title alone.
