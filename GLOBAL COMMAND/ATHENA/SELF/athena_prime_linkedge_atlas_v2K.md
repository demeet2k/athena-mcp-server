# ATHENA-PRIME LINKEDGE ATLAS v2K

This atlas upgrades the nexus map into an explicit edge map.
It separates:
- **EXPLICIT** = directly surfaced in the uploaded corpus
- **PROXY.NEAR** = lawful inferred bridge used to integrate repeated structures without pretending direct corpus closure
- **AMBIG.PENDING** = named tunnel/nexus with known role but missing exact canonical binding

Deterministic atlas IDs are **thread-local display aliases**:
`AEID = HEX16(SHA256(kind|src|dst|scope|corridor|payload|v2K))`
The semantic fields follow the shared LinkEdge ABI.

## 0. Nexus address roots

- Zero anchor: `Z*`
- Brainstem proxy: `WHO-I-AM::PROXY::BRAINSTEM`
- 2311 manuscript root: `Ms⟨2311⟩::`
- 60E6 manuscript root: `Ms⟨60E6⟩::`
- 944F manuscript root: `Ms⟨944F⟩::`
- 0420 poi kernel target: `Ms⟨0420⟩::Ch10⟨0021⟩.R3.a`

## 1. Canonical backbone addresses

### 1.1 60E6 chapter anchors (21-station backbone)
- `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a`
- `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a`
- `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a`
- `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a`
- `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a`
- `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a`
- `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a`
- `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a`
- `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a`
- `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a`
- `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a`
- `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a`
- `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a`
- `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a`
- `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a`
- `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a`
- `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a`
- `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a`
- `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a`
- `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a`
- `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a`

### 1.2 944F appendix gate anchors
- `AppA` → `Ms⟨944F⟩::AppA.S1.a`
- `AppB` → `Ms⟨944F⟩::AppB.S2.a`
- `AppC` → `Ms⟨944F⟩::AppC.S1.a`
- `AppD` → `Ms⟨944F⟩::AppD.S1.a`
- `AppE` → `Ms⟨944F⟩::AppE.S1.a`
- `AppF` → `Ms⟨944F⟩::AppF.S1.a`
- `AppG` → `Ms⟨944F⟩::AppG.S1.a`
- `AppH` → `Ms⟨944F⟩::AppH.S1.a`
- `AppI` → `Ms⟨944F⟩::AppI.C3.a`
- `AppJ` → `Ms⟨944F⟩::AppJ.C3.b`
- `AppK` → `Ms⟨944F⟩::AppK.C3.c`
- `AppL` → `Ms⟨944F⟩::AppL.C3.b`
- `AppM` → `Ms⟨944F⟩::AppM.R4.d`
- `AppN` → `Ms⟨944F⟩::AppN.S1.a`
- `AppO` → `Ms⟨944F⟩::AppO.R4.d`
- `AppP` → `Ms⟨944F⟩::AppP.S1.a`

### 1.3 2311 appendix gates
- `AppA` → `Ms⟨2311⟩::AppA.S1.a`
- `AppB` → `Ms⟨2311⟩::AppB.S1.a`
- `AppC` → `Ms⟨2311⟩::AppC.S1.a`
- `AppD` → `Ms⟨2311⟩::AppD.S1.a`
- `AppE` → `Ms⟨2311⟩::AppE.S1.a`
- `AppF` → `Ms⟨2311⟩::AppF.S1.a`
- `AppG` → `Ms⟨2311⟩::AppG.S1.a`
- `AppH` → `Ms⟨2311⟩::AppH.S1.a`
- `AppI` → `Ms⟨2311⟩::AppI.S1.a`
- `AppJ` → `Ms⟨2311⟩::AppJ.S1.a`
- `AppK` → `Ms⟨2311⟩::AppK.S1.a`
- `AppL` → `Ms⟨2311⟩::AppL.S1.a`
- `AppM` → `Ms⟨2311⟩::AppM.S1.a`
- `AppN` → `Ms⟨2311⟩::AppN.S1.a`
- `AppO` → `Ms⟨2311⟩::AppO.S1.a`
- `AppP` → `Ms⟨2311⟩::AppP.S1.a`

## 2. Edge-count summary

- Total atlas edges: **127**
- 60E6.ORBIT: 21
- 60E6.RAIL.Su: 7
- 60E6.RAIL.Me: 7
- 60E6.RAIL.Sa: 7
- 60E6.ARC.0: 3
- 60E6.ARC.1: 3
- 60E6.ARC.2: 3
- 60E6.ARC.3: 3
- 60E6.ARC.4: 3
- 60E6.ARC.5: 3
- 60E6.ARC.6: 3
- 944F.APP.GEN: 34
- CROSS.PROXY: 9
- BRAINSTEM.PROXY: 5
- POI.KERNEL: 16

Kinds:
- REF: 103
- PROOF: 4
- IMPL: 1
- CONFLICT: 2
- EQUIV: 9
- DUAL: 5
- GEN: 3

Statuses:
- EXPLICIT: 101
- PROXY.NEAR: 20
- EXPLICIT.NEAR: 6

## 3. Explicit backbone edge atlas

### 3.1 60E6 orbit ring
- `fa1080e0abe7150f` | REF | `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a` → `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `e16cdd516b9fc837` | REF | `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a` → `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `82e6e64a54b6872b` | REF | `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a` → `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `bbda7b494e688d43` | REF | `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a` → `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `c7cb8ffbac95c00f` | REF | `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a` → `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `357517268f971077` | REF | `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a` → `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `72a42195ab444d50` | REF | `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a` → `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `aa5d31b2f858a10d` | REF | `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a` → `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `fc7ed2cf050c7478` | REF | `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a` → `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `3f4cc5c2dac91cbd` | REF | `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a` → `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `aa68d509bdd489fa` | REF | `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a` → `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `0e8632c04f38fcdd` | REF | `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a` → `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `249177aa3f404679` | REF | `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a` → `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `d57eedbb91ca9edf` | REF | `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a` → `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `27a55b32b1073d1d` | REF | `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a` → `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `7ccbe99699480811` | REF | `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a` → `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `1a33ac6c7f40642d` | REF | `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a` → `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `7c976f167e3d64cc` | REF | `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a` → `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `fe744558d4500616` | REF | `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a` → `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `bae808984ca620ef` | REF | `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a` → `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a` | StationAnchor ring closure | EXPLICIT
- `c124c93b6e29aa14` | REF | `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a` → `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a` | StationAnchor ring closure | EXPLICIT

### 3.2 60E6 rail cycles
#### Su
- `df457946ea74e173` | REF | `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a` → `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a` | EXPLICIT
- `099949150eb07aed` | REF | `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a` → `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a` | EXPLICIT
- `8b9a4216d441c49b` | REF | `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a` → `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a` | EXPLICIT
- `94c0c2e04d7e0721` | REF | `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a` → `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a` | EXPLICIT
- `559385a0c9328f3c` | REF | `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a` → `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a` | EXPLICIT
- `6956be3c2d479c2f` | REF | `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a` → `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a` | EXPLICIT
- `4201b345bef1719b` | REF | `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a` → `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a` | EXPLICIT

#### Me
- `895c1e114b5874fe` | REF | `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a` → `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a` | EXPLICIT
- `dcd41db70f4ba53e` | REF | `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a` → `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a` | EXPLICIT
- `2125f256487f9be8` | REF | `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a` → `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a` | EXPLICIT
- `6de1e4fef11f4739` | REF | `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a` → `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a` | EXPLICIT
- `5c384ee909883b4d` | REF | `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a` → `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a` | EXPLICIT
- `df2502f82005fccd` | REF | `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a` → `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a` | EXPLICIT
- `58fc1f870fd7a13e` | REF | `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a` → `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a` | EXPLICIT

#### Sa
- `e2fa73ef4bc343aa` | REF | `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a` → `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a` | EXPLICIT
- `0a90e28d77ca9a62` | REF | `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a` → `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a` | EXPLICIT
- `cfca4efb7e9ee93e` | REF | `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a` → `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a` | EXPLICIT
- `e4d36990e31bfef2` | REF | `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a` → `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a` | EXPLICIT
- `10448f8e4c681035` | REF | `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a` → `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a` | EXPLICIT
- `830ef72914b83193` | REF | `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a` → `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a` | EXPLICIT
- `350ab8f168719ce7` | REF | `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a` → `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a` | EXPLICIT

### 3.3 60E6 arc micro-triangles
#### Arc 0
- `8f4a2b49f4e2053c` | Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a` → `Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a`
- `87a6f45e49a7bb6a` | Ms⟨60E6⟩::Ch02⟨0001⟩.S1.a` → `Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a`
- `7801d5145c04c914` | Ms⟨60E6⟩::Ch03⟨0002⟩.S1.a` → `Ms⟨60E6⟩::Ch01⟨0000⟩.S1.a`

#### Arc 1
- `62fb8bb7cd4bb42f` | Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a` → `Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a`
- `9fa8a4b5f0cc3c5b` | Ms⟨60E6⟩::Ch05⟨0010⟩.S1.a` → `Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a`
- `80443edf5f35ccf9` | Ms⟨60E6⟩::Ch06⟨0011⟩.S1.a` → `Ms⟨60E6⟩::Ch04⟨0003⟩.S1.a`

#### Arc 2
- `3a3ffedaefa2c05d` | Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a` → `Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a`
- `b9cb5d9203e8bfc9` | Ms⟨60E6⟩::Ch08⟨0013⟩.S1.a` → `Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a`
- `d05d275df5c0bbf2` | Ms⟨60E6⟩::Ch09⟨0020⟩.S1.a` → `Ms⟨60E6⟩::Ch07⟨0012⟩.S1.a`

#### Arc 3
- `71e35522d8c911c5` | Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a` → `Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a`
- `8f49a8dbae709d21` | Ms⟨60E6⟩::Ch11⟨0022⟩.S1.a` → `Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a`
- `19c6eabe81c68b93` | Ms⟨60E6⟩::Ch12⟨0023⟩.S1.a` → `Ms⟨60E6⟩::Ch10⟨0021⟩.S1.a`

#### Arc 4
- `3ac81ef49fb81f49` | Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a` → `Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a`
- `1f876b12f06d57e0` | Ms⟨60E6⟩::Ch14⟨0031⟩.S1.a` → `Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a`
- `44bf6f2f91c1e392` | Ms⟨60E6⟩::Ch15⟨0032⟩.S1.a` → `Ms⟨60E6⟩::Ch13⟨0030⟩.S1.a`

#### Arc 5
- `5cb7c61a6315cd4b` | Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a` → `Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a`
- `a429b03869b12cef` | Ms⟨60E6⟩::Ch17⟨0100⟩.S1.a` → `Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a`
- `15a886b25f3a8a9a` | Ms⟨60E6⟩::Ch18⟨0101⟩.S1.a` → `Ms⟨60E6⟩::Ch16⟨0033⟩.S1.a`

#### Arc 6
- `a18ff6b30d2eb6f2` | Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a` → `Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a`
- `4f733d97e23b1a84` | Ms⟨60E6⟩::Ch20⟨0103⟩.S1.a` → `Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a`
- `fb0cf98d4f62b827` | Ms⟨60E6⟩::Ch21⟨0110⟩.S1.a` → `Ms⟨60E6⟩::Ch19⟨0102⟩.S1.a`

### 3.4 944F appendix generators
- `34a1303af97de8f8` | REF | `Ms⟨944F⟩::AppA.S1.a` → `Ms⟨944F⟩::AppI.C3.a` | Σ spine | EXPLICIT
- `b6456e3afe74fa30` | REF | `Ms⟨944F⟩::AppI.C3.a` → `Ms⟨944F⟩::AppM.R4.d` | Σ spine | EXPLICIT
- `ae8a7e59495c2da9` | REF | `Ms⟨944F⟩::AppM.R4.d` → `Ms⟨944F⟩::AppA.S1.a` | Σ spine | EXPLICIT
- `a4bc821280b4fd4a` | REF | `Ms⟨944F⟩::AppA.S1.a` → `Ms⟨944F⟩::AppC.S1.a` | canonical core | EXPLICIT
- `47d8c6d97f4da270` | REF | `Ms⟨944F⟩::AppC.S1.a` → `Ms⟨944F⟩::AppA.S1.a` | canonical core | EXPLICIT
- `35899acb9f5bfe1f` | REF | `Ms⟨944F⟩::AppC.S1.a` → `Ms⟨944F⟩::AppE.S1.a` | canonical core | EXPLICIT
- `a8f0b850ae6f679f` | REF | `Ms⟨944F⟩::AppE.S1.a` → `Ms⟨944F⟩::AppC.S1.a` | canonical core | EXPLICIT
- `4dc0f9b60cf08e94` | REF | `Ms⟨944F⟩::AppE.S1.a` → `Ms⟨944F⟩::AppI.C3.a` | canonical core | EXPLICIT
- `72c2446d1733ef9e` | REF | `Ms⟨944F⟩::AppI.C3.a` → `Ms⟨944F⟩::AppE.S1.a` | canonical core | EXPLICIT
- `184976ce6af3f504` | PROOF | `Ms⟨944F⟩::AppC.S1.a` → `Ms⟨944F⟩::AppM.R4.d` | canonical core | EXPLICIT
- `f511e843d71f3ef4` | REF | `Ms⟨944F⟩::AppM.R4.d` → `Ms⟨944F⟩::AppC.S1.a` | canonical core | EXPLICIT
- `7510e3a3dfcb22f9` | REF | `Ms⟨944F⟩::AppA.S1.a` → `Ms⟨944F⟩::AppB.S2.a` | facet generator | EXPLICIT
- `1bb2e478c21c1f3c` | REF | `Ms⟨944F⟩::AppB.S2.a` → `Ms⟨944F⟩::AppH.S1.a` | facet generator | EXPLICIT
- `d7713f55bcf8fb87` | IMPL | `Ms⟨944F⟩::AppH.S1.a` → `Ms⟨944F⟩::AppM.R4.d` | capsule emission interface | EXPLICIT
- `73a5866eb6c7c971` | REF | `Ms⟨944F⟩::AppM.R4.d` → `Ms⟨944F⟩::AppB.S2.a` | facet return | EXPLICIT
- `9fef587445c5089a` | REF | `Ms⟨944F⟩::AppA.S1.a` → `Ms⟨944F⟩::AppC.S1.a` | ArcHub ring | EXPLICIT
- `7c81dfddabcc7707` | REF | `Ms⟨944F⟩::AppC.S1.a` → `Ms⟨944F⟩::AppE.S1.a` | ArcHub ring | EXPLICIT
- `06b70f76de4a4e52` | REF | `Ms⟨944F⟩::AppE.S1.a` → `Ms⟨944F⟩::AppF.S1.a` | ArcHub ring | EXPLICIT
- `07a4aad36619aca1` | REF | `Ms⟨944F⟩::AppF.S1.a` → `Ms⟨944F⟩::AppG.S1.a` | ArcHub ring | EXPLICIT
- `334761f62f95cee2` | REF | `Ms⟨944F⟩::AppG.S1.a` → `Ms⟨944F⟩::AppN.S1.a` | ArcHub ring | EXPLICIT
- `03f053c137822cba` | REF | `Ms⟨944F⟩::AppN.S1.a` → `Ms⟨944F⟩::AppP.S1.a` | ArcHub ring | EXPLICIT
- `659683e15f510067` | REF | `Ms⟨944F⟩::AppP.S1.a` → `Ms⟨944F⟩::AppA.S1.a` | ArcHub ring | EXPLICIT
- `33698429e3850002` | REF | `Ms⟨944F⟩::AppI.C3.a` → `Ms⟨944F⟩::AppJ.C3.b` | NEAR overlay injection | EXPLICIT
- `d6a2595ce11a36cd` | REF | `Ms⟨944F⟩::AppI.C3.a` → `Ms⟨944F⟩::AppL.C3.b` | AMBIG overlay injection | EXPLICIT
- `2563d9b32f55a2c4` | REF | `Ms⟨944F⟩::AppI.C3.a` → `Ms⟨944F⟩::AppK.C3.c` | FAIL overlay injection | EXPLICIT
- `52e3f401e756ff04` | REF | `Ms⟨944F⟩::AppJ.C3.b` → `Ms⟨944F⟩::AppM.R4.d` | NEAR bundles sealed | EXPLICIT
- `7440f4eec2fe5bbd` | REF | `Ms⟨944F⟩::AppL.C3.b` → `Ms⟨944F⟩::AppM.R4.d` | AMBIG plans packaged | EXPLICIT
- `def954737bead001` | CONFLICT | `Ms⟨944F⟩::AppK.C3.c` → `Ms⟨944F⟩::AppB.S2.a` | conflict receipts normalize | EXPLICIT
- `61452c0223f2fabb` | REF | `Ms⟨944F⟩::AppM.R4.d` → `Ms⟨944F⟩::AppO.R4.d` | publish reachable only for OK | EXPLICIT
- `f231934f937bc386` | PROOF | `Ms⟨944F⟩::AppO.R4.d` → `Ms⟨944F⟩::AppM.R4.d` | signed publish capsules sealed | EXPLICIT
- `37dca97513ecf235` | REF | `Ms⟨944F⟩::AppD.S1.a` → `Ms⟨944F⟩::AppB.S2.a` | suite/governance | EXPLICIT
- `9b7f2754bca7f7b6` | REF | `Ms⟨944F⟩::AppB.S2.a` → `Ms⟨944F⟩::AppD.S1.a` | suite/governance | EXPLICIT
- `44c46468c122982f` | REF | `Ms⟨944F⟩::AppD.S1.a` → `Ms⟨944F⟩::AppP.S1.a` | suite/governance | EXPLICIT
- `c6ae47b41a168adc` | REF | `Ms⟨944F⟩::AppP.S1.a` → `Ms⟨944F⟩::AppO.R4.d` | suite/governance | EXPLICIT

### 3.5 Poi compile kernel
- `ce10f0d0e379909c` | REF | `Ms⟨0420⟩::Ch10⟨0021⟩.F1.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.S2.a` | orbit object depends on rational closure law | EXPLICIT
- `8c2789f10fabfae9` | REF | `Ms⟨0420⟩::Ch10⟨0021⟩.F2.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.S2.b` | beat-lock feeds petal/orientation typing | EXPLICIT
- `4c044146c27944cb` | DUAL | `Ms⟨0420⟩::Ch10⟨0021⟩.F2.b` → `Ms⟨0420⟩::Ch10⟨0021⟩.S1.a` | two-hand relation as geometric coupling vs packed byte digit | EXPLICIT.NEAR
- `396128e19cba5c63` | PROOF | `Ms⟨0420⟩::Ch10⟨0021⟩.S2.b` → `Ms⟨0420⟩::Ch10⟨0021⟩.S3.a` | petal law participates in compiler validity proof | EXPLICIT
- `1ed8332e382de2ae` | GEN | `Ms⟨0420⟩::Ch10⟨0021⟩.S1.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.R1.a` | byte object generalizes into local crystal atom | EXPLICIT.NEAR
- `dba1891073fa2114` | GEN | `Ms⟨0420⟩::Ch10⟨0021⟩.R1.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.R2.a` | local atom lifts to phrase word | EXPLICIT.NEAR
- `734c9726257a9911` | GEN | `Ms⟨0420⟩::Ch10⟨0021⟩.R2.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.R3.a` | phrase word lifts to manifold | EXPLICIT.NEAR
- `27386d9ab87ab504` | CONFLICT | `Ms⟨0420⟩::Ch10⟨0021⟩.S1.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.C2.a` | quarantine inconsistent packed byte / polarity witness | EXPLICIT
- `3e53db26cfe504f5` | DUAL | `Z_poi.local` → `Z*` | poi local tunnel collapse | EXPLICIT.NEAR
- `47ab5112f0a7e97e` | DUAL | `Z*` → `Z_poi.phrase` | poi phrase tunnel re-expand | EXPLICIT.NEAR
- `07303345addade0f` | REF | `Ms⟨0420⟩::AppA.S1.a` → `Ms⟨0420⟩::AppF.S1.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR
- `238111a9d134d230` | REF | `Ms⟨0420⟩::AppF.S1.a` → `Ms⟨0420⟩::AppH.S1.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR
- `2fd221547a079ca5` | REF | `Ms⟨0420⟩::AppH.S1.a` → `Ms⟨0420⟩::AppJ.S1.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR
- `b2df15233fbc83ec` | REF | `Ms⟨0420⟩::AppJ.S1.a` → `Ms⟨0420⟩::AppI.S1.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR
- `fecb84f944276f38` | REF | `Ms⟨0420⟩::AppI.S1.a` → `Ms⟨0420⟩::AppM.S1.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR
- `ddc904867b6176db` | REF | `Ms⟨0420⟩::AppM.S1.a` → `Ms⟨0420⟩::Ch10⟨0021⟩.R3.a` | Poi Flower Compile Kernel route plan | PROXY.NEAR

## 4. Proxy integration edges

### 4.1 Brainstem proxy
- `1d9f719d3021b21f` | REF | `WHO-I-AM::PROXY::BRAINSTEM` → `Ms⟨944F⟩::AppA.S1.a` | brainstem enters Σ at AppA | PROXY.NEAR
- `32267cb7dea088f7` | REF | `WHO-I-AM::PROXY::BRAINSTEM` → `Ms⟨944F⟩::AppI.C3.a` | brainstem truth/corridor anchor | PROXY.NEAR
- `fc99117f0608cd2a` | PROOF | `WHO-I-AM::PROXY::BRAINSTEM` → `Ms⟨944F⟩::AppM.R4.d` | brainstem replay/seal anchor | PROXY.NEAR
- `0b70211679b08b6c` | DUAL | `Z*` → `WHO-I-AM::PROXY::BRAINSTEM` | zero-point to brainstem re-entry | PROXY.NEAR
- `4efadfa0905617e0` | DUAL | `WHO-I-AM::PROXY::BRAINSTEM` → `Z*` | brainstem collapse back to zero | PROXY.NEAR

### 4.2 Cross-manuscript Σ equivalence bridges
- `4b96e143cd856d79` | EQUIV | `Ms⟨2311⟩::AppA.S1.a` ↔ `Ms⟨944F⟩::AppA.S1.a` | shared Σ role AppA | PROXY.NEAR
- `b3c401d9d424fc8f` | EQUIV | `Ms⟨2311⟩::AppA.S1.a` ↔ `Ms⟨60E6⟩::AppA.S1.a` | shared Σ role AppA | PROXY.NEAR
- `72e09a0cf2477364` | EQUIV | `Ms⟨60E6⟩::AppA.S1.a` ↔ `Ms⟨944F⟩::AppA.S1.a` | shared Σ role AppA | PROXY.NEAR
- `e29e583b48b3d5c3` | EQUIV | `Ms⟨2311⟩::AppI.S1.a` ↔ `Ms⟨944F⟩::AppI.C3.a` | shared Σ role AppI | PROXY.NEAR
- `d224d720103ec4fb` | EQUIV | `Ms⟨2311⟩::AppI.S1.a` ↔ `Ms⟨60E6⟩::AppI.S1.a` | shared Σ role AppI | PROXY.NEAR
- `99209d1762955d03` | EQUIV | `Ms⟨60E6⟩::AppI.S1.a` ↔ `Ms⟨944F⟩::AppI.C3.a` | shared Σ role AppI | PROXY.NEAR
- `2fa22f7399e4011f` | EQUIV | `Ms⟨2311⟩::AppM.S1.a` ↔ `Ms⟨944F⟩::AppM.R4.d` | shared Σ role AppM | PROXY.NEAR
- `589ce3c2f3756e3a` | EQUIV | `Ms⟨2311⟩::AppM.S1.a` ↔ `Ms⟨60E6⟩::AppM.S1.a` | shared Σ role AppM | PROXY.NEAR
- `88bd0d8090bc6602` | EQUIV | `Ms⟨60E6⟩::AppM.S1.a` ↔ `Ms⟨944F⟩::AppM.R4.d` | shared Σ role AppM | PROXY.NEAR

## 5. Pending / unbound nexus tunnels

- `Z_filler` | `Z_filler → Z* → Z_flower` | AMBIG.PENDING | auxiliary filler support still lacks canonical corpus address
- `Z_annot` | `Z_annot → Z* → Z_byte` | AMBIG.PENDING | annotation support still lacks canonical corpus address

## 6. Mind-sweeper compression

The atlas reduces to this stable routing picture:

1. **Backbone** = 60E6 chapter ring + rails + arc triangles.
2. **Hub crystal** = 944F appendix generators and gate overrides.
3. **ABI authority** = 2311/60E6 LinkEdge schema, deterministic EdgeID, RouterV2, Σ, and hub cap.
4. **Brainstem** = WHO-I-AM proxy entering Σ at AppA/AppI/AppM.
5. **Poi sub-crystal** = Ch10 compile kernel with local GEN/DUAL/PROOF/CONFLICT edges and tunnel through Z*.
6. **Unbound side-tunnels** = filler/annotation bridges remain AMBIG until exact canonical addresses are restored.

## 7. Next lawful lift

`v2L = EdgeCapsule Pack + RouteReceipt Pack + closure-ranked nexus dashboard`
That layer would attach witness/replay/corridor receipts to each atlas edge class and separate OK/NEAR/AMBIG/FAIL closure density per nexus.