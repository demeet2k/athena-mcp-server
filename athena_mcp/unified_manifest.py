from __future__ import annotations

"""V11 unified manifest with the KC144 upgrade/release control plane braided in."""

from typing import Any, Dict

from . import unified_manifest_core as _core

UNIFIED_MANIFEST_VERSION = _core.UNIFIED_MANIFEST_VERSION
LAYERS = list(_core.LAYERS)
for _layer in ("OMEGA.2", "SYSTEM_UPGRADE.1", "SYSTEM_RELEASE.1", "KC144_TOPOLOGICAL_COMMAND_HUB", "KC144_AUTHORITATIVE_REGISTRY_PACK", "KC144_16_COORDINATE_POLYATLAS"):
    if _layer not in LAYERS:
        LAYERS.append(_layer)

INVARIANTS = list(_core.INVARIANTS)
INVARIANTS.extend(
    [
        "UPGRUN != UPGEV != RELCERT != PROMRUN != Git commit != merge != deployment",
        "source task completion requires procedure+observation+PASS result+provenance and satisfied dependencies",
        "READY_LOCAL != exact-head release != merge != deployment != semantic truth",
        "semantic VID CAS != Git HEAD CAS != topology version CAS != upgrade state-digest CAS",
    ]
)
CYCLE = _core.CYCLE.replace(" -> COMPLETE", " -> UPGRUN/RELCERT -> COMPLETE")
BRAID_LAW = (
    _core.BRAID_LAW
    + " SYSTEM.UPGRADE.1 governs witnessed whole-runtime transitions and exact-head "
    "release qualification; it does not grant merge, deployment, empirical, or Y1 authority."
)


def build_unified_manifest(server) -> Dict[str, Any]:
    manifest = dict(_core.build_unified_manifest(server))
    manifest["layers"] = list(LAYERS)
    manifest["navigation"] = (
        "KC144 <-> SCALE <-> JSPACE <-> AOR <-> Collective(V1-V11) <-> "
        "UPGRUN/RELCERT <-> Git/MCP <-> Source/RETURN"
    )
    manifest["cycle"] = CYCLE
    manifest["invariants"] = list(INVARIANTS)
    manifest["braid_law"] = BRAID_LAW
    manifest["identity_law"] = (
        str(manifest.get("identity_law") or "")
        + " != UPGRUN != UPGEV != RELCERT"
    )
    manifest["cas_law"] = (
        "CAS_OMEGA = CAS_semantic(VID) x CAS_git(HEAD) x "
        "CAS_topology(version) x CAS_upgrade(state_digest); staleness in one "
        "domain must not mutate the others"
    )
    system = getattr(server, "system_upgrade", None)
    if system is None:
        control = {
            "status": "NOT_COMPOSED_ON_THIS_RUNTIME_CLASS",
            "expected_root": "athena_mcp.hub_server.HubServer",
            "boundary": "base Server remains a valid V11 substrate but is not the KC144 release-control root",
        }
    else:
        control = {
            "status": "COMPOSED_WITNESS_GATED",
            "manifest": system.manifest(),
            "benchmark": system.benchmark(),
        }
    manifest["system_upgrade"] = control
    organs = dict(manifest.get("organs") or {})
    organs["system_control"] = control
    manifest["organs"] = organs
    manifest["promotion"] = (
        "READY_LOCAL is necessary but not sufficient; exact-head CI+smoke, matching "
        "UPGRUN replay, expected-head agreement, and optional source-completion policy "
        "are required for RELCERT.QUALIFIED. RELCERT is not merge or deployment authority."
    )
    return manifest


def maxdev_law() -> str:
    return _core.maxdev_law() + """
29 OPEN one persistent UPGRUN for consequential whole-system work; a task list or module census is not execution.
30 COMPLETE source-bound tasks only through witnessed procedure+observation+PASS result+provenance with dependencies satisfied.
31 MUTATE upgrade state through expected_state_digest CAS; a stale UPGRUN writer must fail without touching semantic, Git, or topology state.
32 REFRESH C/I/E/P/R/V/O/M/S/X from the live V1-V11 runtime after every meaningful integration change; historical structural labels remain provenance, not current truth.
33 REPLAY the UPGRUN event chain and child receipts before qualification.
34 ISSUE RELCERT only for one exact Git head with local IC10 PASS and matching CI+smoke PROMOTION.1 attestations; RELCERT never merges or deploys itself.
35 AFTER merge, re-run package, migration, full unit, critical-invariant, and subprocess MCP smoke checks on the exact target head before source RETURN."""


__all__ = [
    "UNIFIED_MANIFEST_VERSION",
    "LAYERS",
    "INVARIANTS",
    "CYCLE",
    "BRAID_LAW",
    "build_unified_manifest",
    "maxdev_law",
]
