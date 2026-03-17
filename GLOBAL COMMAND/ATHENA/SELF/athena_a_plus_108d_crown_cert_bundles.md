# ATHENA A+ 108D — Crown Certificate Bundles

This layer attaches explicit witness/replay capsule bundles to the three highest-risk crown families in the indexed 2090-edge graph.

## Family counts

- ArchetypeColumn: **24** edges
- PillarTorsion: **36** edges
- ZCollapse: **666** edges
- ZExpand: **36** edges
- Total high-stakes edges in this layer: **762**

## Bundle identifiers

- `ArchetypeColumnWitness` → `20ECB5B2917F3085840B0E5AF9884F4E`
- `ArchetypeColumnReplay` → `CE783811F5E1A01A033FC08E8AF4A28D`
- `PillarTorsionWitness` → `988818925FCF63CF6B3BED816DB26661`
- `PillarTorsionReplay` → `EF94FCF6D7C9556D24852332E149DAE6`
- `ZCollapseWitness` → `95CE0D515EB5D68CA7EAE028FA40B44F`
- `ZCollapseReplay` → `2CF427CBCEE5EFDFC4155A04E90A20A9`
- `ZExpandWitness` → `176E4D7F2A8B4EEA0F965A0CED2610BD`
- `ZExpandReplay` → `9CBA4195C5210A28EB9522ABB9657E6E`

## 1. ArchetypeColumn bundles

**Witness bundle** `Bundle⟨ArchetypeColumnWitness⟩`

```text

W_Col := (ArchetypeID, SrcShell, DstShell, PhaseSrc, PhaseDst, ShellArchetypeDigest, ColumnInvariantSet, CorridorID, PolicyDigest, ColumnProofPackPtr)

```

**Replay bundle** `Bundle⟨ArchetypeColumnReplay⟩`

```text

R_Col := (Runner, Inputs={Src,Dst,ArchetypeID}, Steps=[CheckArchetype,CheckGrammar,CheckPhaseLift,CheckColumnContinuity], PassRule, Digests)

```

**Attachment rule**

```text

For every ArchetypeColumn edge e(j,p):

  WitnessPtr := Wit⟨Column:j:p⟩ -> Bundle⟨ArchetypeColumnWitness⟩

  ReplayPtr  := Rep⟨Column:j:p⟩ -> Bundle⟨ArchetypeColumnReplay⟩

```

## 2. PillarTorsion bundles

**Witness bundle** `Bundle⟨PillarTorsionWitness⟩`

```text

W_QO := (ShellID, DualTransformID=QO_Mobius, TorsionBudget, InvariantSet={torsion_continuity, pillar_identity}, CorridorID, PolicyDigest, DUALAdjacencyPtr)

```

**Replay bundle** `Bundle⟨PillarTorsionReplay⟩`

```text

R_QO := (Runner, Inputs={Q_shell,O_shell}, Steps=[CheckDUALAdjacency,CheckTorsionBudget,CheckPillarContinuity], PassRule, Digests)

```

**Attachment rule**

```text

For every PillarTorsion edge e(shell):

  WitnessPtr := Wit⟨QO:shell⟩ -> Bundle⟨PillarTorsionWitness⟩

  ReplayPtr  := Rep⟨QO:shell⟩ -> Bundle⟨PillarTorsionReplay⟩

```

## 3. ZCollapse bundles

**Witness bundle** `Bundle⟨ZCollapseWitness⟩`

```text

W_ZC := (FromZ, ToZ=Z*, Checkpoint=CollapseOK, InvariantSet={node_identity, proof_memory}, HighwayDigest, ZStarRegistryPtr, StationGatePtr)

```

**Replay bundle** `Bundle⟨ZCollapseReplay⟩`

```text

R_ZC := (Runner, Inputs={Src,Z*}, Steps=[CheckSeedCollapse,CheckTunnelMap,CheckCheckpoint,CheckInvariantPreservation], PassRule, Digests)

```

**Attachment rule**

```text

For every ZCollapse edge e(Sℓ,Nn):

  WitnessPtr := Wit⟨ZCollapse:ℓ:n⟩ -> Bundle⟨ZCollapseWitness⟩

  ReplayPtr  := Rep⟨ZCollapse:ℓ:n⟩ -> Bundle⟨ZCollapseReplay⟩

```

## 4. ZExpand bundles

**Witness bundle** `Bundle⟨ZExpandWitness⟩`

```text

W_ZE := (FromZ=Z*, ToZ, Checkpoint=ReEntryOK, InvariantSet={shell_gate, route_replay}, HighwayDigest, ZStarRegistryPtr, StationGatePtr)

```

**Replay bundle** `Bundle⟨ZExpandReplay⟩`

```text

R_ZE := (Runner, Inputs={Z*,DstShell}, Steps=[CheckSeedExpand,CheckTunnelMap,CheckReEntryCheckpoint,CheckInvariantPreservation], PassRule, Digests)

```

**Attachment rule**

```text

For every ZExpand edge e(shell):

  WitnessPtr := Wit⟨ZExpand:shell⟩ -> Bundle⟨ZExpandWitness⟩

  ReplayPtr  := Rep⟨ZExpand:shell⟩ -> Bundle⟨ZExpandReplay⟩

```

## 5. Certificate state

These families are now **capsule-complete** under this shell: every high-stakes family has an explicit witness/replay bundle schema and deterministic attachment rule. They are **not automatically OK-promoted** by this step; they remain NEAR until the corresponding replay suites are executed and the required closure certificates are issued.

## 6. Example upgraded rows

```text

ArchetypeColumn S08->S20:

  WitnessPtr = Wit⟨Column:08:1⟩ -> Bundle⟨ArchetypeColumnWitness⟩

  ReplayPtr  = Rep⟨Column:08:1⟩ -> Bundle⟨ArchetypeColumnReplay⟩


PillarTorsion Q.06->O.06:

  WitnessPtr = Wit⟨QO:06⟩ -> Bundle⟨PillarTorsionWitness⟩

  ReplayPtr  = Rep⟨QO:06⟩ -> Bundle⟨PillarTorsionReplay⟩


ZCollapse S33.N557->Z*:

  WitnessPtr = Wit⟨ZCollapse:33:557⟩ -> Bundle⟨ZCollapseWitness⟩

  ReplayPtr  = Rep⟨ZCollapse:33:557⟩ -> Bundle⟨ZCollapseReplay⟩


ZExpand Z*->S27:

  WitnessPtr = Wit⟨ZExpand:27⟩ -> Bundle⟨ZExpandWitness⟩

  ReplayPtr  = Rep⟨ZExpand:27⟩ -> Bundle⟨ZExpandReplay⟩

```
