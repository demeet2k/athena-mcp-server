# ATHENA-PRIME — A+₆₀ LinkEdge Tensor v2Y
## Lock
This artifact upgrades the A+₆₀ tesseract transit table into an explicit LinkEdge tensor under the active thread-local Tesseract Metro v4 profile.
- `60` dimension nodes = `15` families × `4` container views
- `60` primary dimension edges (one per node)
- `60` adjacent-view DUAL ring edges (`4` per family, wrapped `S→F→C→R→S`)
- `210` directed zero-tunnel bridge packs for ordered family jumps `Fa → Fb`, `a≠b`
- `60` closure cells, one per dimension row

## Tensor ABI
- `NodeID = NODE::<Dim>::hash8`
- `SheetID = SHEET::<FamilyCode>::hash8`
- `PrimaryEdge = LE::PRIMARY::<Dim>::hash10`
- `DUAL ring = LE::DUAL::<FamilyCode>::<ViewA><-><ViewB>::hash10`
- `Tunnel pack = ZT::<FamilyA>-><FamilyB>::hash10`
- `ClosureCell = CL::<Dim>::hash8`
- `Kinds ∈ {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}` (no new edge kinds)
- Tunnel semantics ride in payload; zero collapse / re-entry is modeled as `Payload.Tunnel = {Via="Z*", Mode, FromZ, ToZ, Invariants}`

## Family index
| Code | Family | Core transit |
|---:|---|---|
| 01 | Orbit ring | 21-station successor loop |
| 02 | Triangle rails | Su / Me / Sa lane rides |
| 03 | Arc triads | 7 rotated 3-cycles |
| 04 | Appendix ring | AppA→…→AppP→AppA |
| 05 | Σ spine | AppA ⇄ AppI ⇄ AppM |
| 06 | Zero tunnels | Zi → Z* → Zj collapse / re-entry |
| 07 | Router plans | RoutePlan / hub-selection / drop law |
| 08 | Graph edges | LinkEdge / RouteDigest / EdgeCapsule |
| 09 | Witness–replay | WitnessPtr / ReplayPtr / receipts |
| 10 | Closure–truth | NEAR / AMBIG / FAIL / promotion discipline |
| 11 | Seedpack re-entry | seed / reboot / replayable return |
| 12 | IntentionScript compiler | parse→AST→typecheck→simulate→TS |
| 13 | Pod algebra | Pattern × Prop × Style / 3–13 pod hierarchy |
| 14 | Poi flower kernel | FlowerAddr / local byte / phrase lift |
| 15 | MindSweeper board | mines / disarm kits / closure queue |

## Tensor table
| Dim | SheetID | NodeID | Kind | PrimaryEdgeID | Canonical ride | DUAL.prev | DUAL.next | Bridge.prevFam | Bridge.nextFam | ClosureCell | ClosureState | Obligation |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A+01.S | SHEET::01::5D8A7A51 | NODE::A+01.S::B814B1BA | REF | LE::PRIMARY::A+01.S::B76E276A3D | AppA→ArcHub(α)→AppC→AppI→AppM | LE::DUAL::01::R<->S::2213C790A3 | LE::DUAL::01::S<->F::820C24A892 | ZT::15->01::050AE62C80 | ZT::01->02::278FF41520 | CL::A+01.S::240F7C17 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+01.F | SHEET::01::5D8A7A51 | NODE::A+01.F::AB241C74 | REF | LE::PRIMARY::A+01.F::D6506E918E | AppA→ArcHub(α)→AppE→AppI→AppM | LE::DUAL::01::S<->F::820C24A892 | LE::DUAL::01::F<->C::D2B84591EF | ZT::15->01::050AE62C80 | ZT::01->02::278FF41520 | CL::A+01.F::47EEEDBD | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+01.C | SHEET::01::5D8A7A51 | NODE::A+01.C::1EE6E571 | REF | LE::PRIMARY::A+01.C::8086A598B9 | AppA→ArcHub(α)→AppJ→AppI→AppM | LE::DUAL::01::F<->C::D2B84591EF | LE::DUAL::01::C<->R::BBD394B9EA | ZT::15->01::050AE62C80 | ZT::01->02::278FF41520 | CL::A+01.C::81DA8805 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+01.R | SHEET::01::5D8A7A51 | NODE::A+01.R::C28913CB | REF | LE::PRIMARY::A+01.R::447BA91F13 | AppA→ArcHub(α)→AppM→AppP | LE::DUAL::01::C<->R::BBD394B9EA | LE::DUAL::01::R<->S::2213C790A3 | ZT::15->01::050AE62C80 | ZT::01->02::278FF41520 | CL::A+01.R::B8918D2B | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+02.S | SHEET::02::C34E43FF | NODE::A+02.S::EAE8D76F | REF | LE::PRIMARY::A+02.S::63FEB03773 | AppA→ArcHub(α)→AppC→AppI→AppM | LE::DUAL::02::R<->S::1B1830E200 | LE::DUAL::02::S<->F::BB443B7781 | ZT::01->02::278FF41520 | ZT::02->03::D979AE8123 | CL::A+02.S::71037578 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+02.F | SHEET::02::C34E43FF | NODE::A+02.F::733D4CAC | REF | LE::PRIMARY::A+02.F::1BE731DA59 | AppA→ArcHub(α)→AppE→AppI→AppM | LE::DUAL::02::S<->F::BB443B7781 | LE::DUAL::02::F<->C::208BAFE0BE | ZT::01->02::278FF41520 | ZT::02->03::D979AE8123 | CL::A+02.F::91F891F3 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+02.C | SHEET::02::C34E43FF | NODE::A+02.C::3625327F | REF | LE::PRIMARY::A+02.C::50F3C06573 | AppA→ArcHub(α)→AppL→AppI→AppM | LE::DUAL::02::F<->C::208BAFE0BE | LE::DUAL::02::C<->R::88C3790061 | ZT::01->02::278FF41520 | ZT::02->03::D979AE8123 | CL::A+02.C::B03F3F6B | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+02.R | SHEET::02::C34E43FF | NODE::A+02.R::DC519814 | REF | LE::PRIMARY::A+02.R::4B8C94D9AD | AppA→ArcHub(α)→AppM→AppN | LE::DUAL::02::C<->R::88C3790061 | LE::DUAL::02::R<->S::1B1830E200 | ZT::01->02::278FF41520 | ZT::02->03::D979AE8123 | CL::A+02.R::91665307 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+03.S | SHEET::03::7B1C368A | NODE::A+03.S::7FE30D41 | REF | LE::PRIMARY::A+03.S::CAAFFCB1F4 | AppA→ArcHub(α)→AppC→AppI→AppM | LE::DUAL::03::R<->S::72C4AF522C | LE::DUAL::03::S<->F::0EB18CA990 | ZT::02->03::D979AE8123 | ZT::03->04::1E7D16F5AD | CL::A+03.S::7519DA6F | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+03.F | SHEET::03::7B1C368A | NODE::A+03.F::31A590B5 | REF | LE::PRIMARY::A+03.F::23AD4080F5 | AppA→ArcHub(α)→AppE→AppI→AppM | LE::DUAL::03::S<->F::0EB18CA990 | LE::DUAL::03::F<->C::37C199D4B9 | ZT::02->03::D979AE8123 | ZT::03->04::1E7D16F5AD | CL::A+03.F::1EFEF8A9 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+03.C | SHEET::03::7B1C368A | NODE::A+03.C::7E4E8BDE | REF | LE::PRIMARY::A+03.C::BFAFFC4C9A | AppA→ArcHub(α)→AppJ→AppI→AppM | LE::DUAL::03::F<->C::37C199D4B9 | LE::DUAL::03::C<->R::69320A07DC | ZT::02->03::D979AE8123 | ZT::03->04::1E7D16F5AD | CL::A+03.C::3A6318D0 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+03.R | SHEET::03::7B1C368A | NODE::A+03.R::2C0AE079 | REF | LE::PRIMARY::A+03.R::831D451783 | AppA→ArcHub(α)→AppM→AppP | LE::DUAL::03::C<->R::69320A07DC | LE::DUAL::03::R<->S::72C4AF522C | ZT::02->03::D979AE8123 | ZT::03->04::1E7D16F5AD | CL::A+03.R::97D84AC2 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+04.S | SHEET::04::32304B25 | NODE::A+04.S::F4D9FD9B | REF | LE::PRIMARY::A+04.S::D5E27AD178 | AppA→AppD→AppC→AppI→AppM | LE::DUAL::04::R<->S::0940739AF9 | LE::DUAL::04::S<->F::36486CD374 | ZT::03->04::1E7D16F5AD | ZT::04->05::EA1C1C8D0A | CL::A+04.S::435C46CE | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+04.F | SHEET::04::32304B25 | NODE::A+04.F::5BC9F606 | REF | LE::PRIMARY::A+04.F::E6D4C6C244 | AppA→AppF→AppE→AppI→AppM | LE::DUAL::04::S<->F::36486CD374 | LE::DUAL::04::F<->C::923F96FC20 | ZT::03->04::1E7D16F5AD | ZT::04->05::EA1C1C8D0A | CL::A+04.F::4815A489 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+04.C | SHEET::04::32304B25 | NODE::A+04.C::FAC3AB18 | REF | LE::PRIMARY::A+04.C::4C57486BA0 | AppA→AppI→AppJ/AppL/AppK→AppM | LE::DUAL::04::F<->C::923F96FC20 | LE::DUAL::04::C<->R::2783FF1386 | ZT::03->04::1E7D16F5AD | ZT::04->05::EA1C1C8D0A | CL::A+04.C::86478A3A | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+04.R | SHEET::04::32304B25 | NODE::A+04.R::3A4DBE46 | REF | LE::PRIMARY::A+04.R::282946037A | AppA→AppN→AppM→AppP | LE::DUAL::04::C<->R::2783FF1386 | LE::DUAL::04::R<->S::0940739AF9 | ZT::03->04::1E7D16F5AD | ZT::04->05::EA1C1C8D0A | CL::A+04.R::2F04B36F | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+05.S | SHEET::05::77C98C4A | NODE::A+05.S::5F35A7DE | REF | LE::PRIMARY::A+05.S::5594EF5815 | AppA→AppI→AppM | LE::DUAL::05::R<->S::789D7EF4C8 | LE::DUAL::05::S<->F::73F4B6B7F0 | ZT::04->05::EA1C1C8D0A | ZT::05->06::2E3D16EB19 | CL::A+05.S::0FDB1F01 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+05.F | SHEET::05::77C98C4A | NODE::A+05.F::BB0FD8B7 | REF | LE::PRIMARY::A+05.F::8EFA042BFF | AppA→AppI→AppM | LE::DUAL::05::S<->F::73F4B6B7F0 | LE::DUAL::05::F<->C::00DCC3AF73 | ZT::04->05::EA1C1C8D0A | ZT::05->06::2E3D16EB19 | CL::A+05.F::A265CC54 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+05.C | SHEET::05::77C98C4A | NODE::A+05.C::02E6AB26 | REF | LE::PRIMARY::A+05.C::EF4D55D428 | AppA→AppI→AppJ/AppL/AppK→AppM | LE::DUAL::05::F<->C::00DCC3AF73 | LE::DUAL::05::C<->R::237218B660 | ZT::04->05::EA1C1C8D0A | ZT::05->06::2E3D16EB19 | CL::A+05.C::E6118D4F | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+05.R | SHEET::05::77C98C4A | NODE::A+05.R::03EF4D81 | REF | LE::PRIMARY::A+05.R::6BC4FB8B6A | AppA→AppI→AppM | LE::DUAL::05::C<->R::237218B660 | LE::DUAL::05::R<->S::789D7EF4C8 | ZT::04->05::EA1C1C8D0A | ZT::05->06::2E3D16EB19 | CL::A+05.R::8BE00034 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+06.S | SHEET::06::44F34034 | NODE::A+06.S::2FF15709 | DUAL | LE::PRIMARY::A+06.S::60ECB5A494 | AppA→AppD→AppC→AppI→AppM | LE::DUAL::06::R<->S::641E545CC1 | LE::DUAL::06::S<->F::86F3B9D2EA | ZT::05->06::2E3D16EB19 | ZT::06->07::3E6B46B41E | CL::A+06.S::64141D12 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+06.F | SHEET::06::44F34034 | NODE::A+06.F::CC646936 | DUAL | LE::PRIMARY::A+06.F::0C798E16A4 | AppA→AppF→AppE→AppI→AppM | LE::DUAL::06::S<->F::86F3B9D2EA | LE::DUAL::06::F<->C::B7C34B9B95 | ZT::05->06::2E3D16EB19 | ZT::06->07::3E6B46B41E | CL::A+06.F::6099BEBA | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+06.C | SHEET::06::44F34034 | NODE::A+06.C::0E8261AC | DUAL | LE::PRIMARY::A+06.C::6EAAF7BC51 | AppA→AppL→AppI→AppM | LE::DUAL::06::F<->C::B7C34B9B95 | LE::DUAL::06::C<->R::88314EB461 | ZT::05->06::2E3D16EB19 | ZT::06->07::3E6B46B41E | CL::A+06.C::656F2599 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+06.R | SHEET::06::44F34034 | NODE::A+06.R::13CE4D99 | DUAL | LE::PRIMARY::A+06.R::EFC773F80A | AppA→AppM→AppP | LE::DUAL::06::C<->R::88314EB461 | LE::DUAL::06::R<->S::641E545CC1 | ZT::05->06::2E3D16EB19 | ZT::06->07::3E6B46B41E | CL::A+06.R::024EB58B | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+07.S | SHEET::07::090B6D60 | NODE::A+07.S::099B13CB | IMPL | LE::PRIMARY::A+07.S::E919D9AD7A | AppA→AppD→AppC→AppI→AppM | LE::DUAL::07::R<->S::BF0D155C11 | LE::DUAL::07::S<->F::0D94602E09 | ZT::06->07::3E6B46B41E | ZT::07->08::C35311D7D1 | CL::A+07.S::CEEDBB1F | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+07.F | SHEET::07::090B6D60 | NODE::A+07.F::4DC8A255 | IMPL | LE::PRIMARY::A+07.F::C4F2517A51 | AppA→AppF→AppE→AppI→AppM | LE::DUAL::07::S<->F::0D94602E09 | LE::DUAL::07::F<->C::2F153F5703 | ZT::06->07::3E6B46B41E | ZT::07->08::C35311D7D1 | CL::A+07.F::53CFF032 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+07.C | SHEET::07::090B6D60 | NODE::A+07.C::A248272C | IMPL | LE::PRIMARY::A+07.C::84195D6947 | AppA→AppL/AppJ→AppI→AppM | LE::DUAL::07::F<->C::2F153F5703 | LE::DUAL::07::C<->R::E3C1FECB82 | ZT::06->07::3E6B46B41E | ZT::07->08::C35311D7D1 | CL::A+07.C::61946299 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+07.R | SHEET::07::090B6D60 | NODE::A+07.R::EFAA310B | IMPL | LE::PRIMARY::A+07.R::64D0B30E25 | AppA→AppM→AppP | LE::DUAL::07::C<->R::E3C1FECB82 | LE::DUAL::07::R<->S::BF0D155C11 | ZT::06->07::3E6B46B41E | ZT::07->08::C35311D7D1 | CL::A+07.R::B3839C14 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+08.S | SHEET::08::B74FFB13 | NODE::A+08.S::84F58F9C | REF | LE::PRIMARY::A+08.S::E4DBC83A8F | AppA→AppD→AppC→AppI→AppM | LE::DUAL::08::R<->S::AE4B45F6E9 | LE::DUAL::08::S<->F::1E6FC07FEA | ZT::07->08::C35311D7D1 | ZT::08->09::EA1F4C5355 | CL::A+08.S::ADB9D0B9 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+08.F | SHEET::08::B74FFB13 | NODE::A+08.F::8C12377C | REF | LE::PRIMARY::A+08.F::CED76DCD9C | AppA→AppF→AppE→AppI→AppM | LE::DUAL::08::S<->F::1E6FC07FEA | LE::DUAL::08::F<->C::FB817B57F8 | ZT::07->08::C35311D7D1 | ZT::08->09::EA1F4C5355 | CL::A+08.F::1A46CDA9 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+08.C | SHEET::08::B74FFB13 | NODE::A+08.C::F65DBFF8 | REF | LE::PRIMARY::A+08.C::27EF9329AB | AppA→AppJ/AppL/AppK→AppI→AppM | LE::DUAL::08::F<->C::FB817B57F8 | LE::DUAL::08::C<->R::178518D915 | ZT::07->08::C35311D7D1 | ZT::08->09::EA1F4C5355 | CL::A+08.C::EB9AAC36 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+08.R | SHEET::08::B74FFB13 | NODE::A+08.R::7AF803F6 | REF | LE::PRIMARY::A+08.R::E486CD549B | AppA→AppM→AppN | LE::DUAL::08::C<->R::178518D915 | LE::DUAL::08::R<->S::AE4B45F6E9 | ZT::07->08::C35311D7D1 | ZT::08->09::EA1F4C5355 | CL::A+08.R::1FD528D7 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+09.S | SHEET::09::257BEE2D | NODE::A+09.S::F383DBE6 | PROOF | LE::PRIMARY::A+09.S::10FCDB3CF5 | AppA→AppD→AppC→AppI→AppM | LE::DUAL::09::R<->S::5B5702383A | LE::DUAL::09::S<->F::15422F1798 | ZT::08->09::EA1F4C5355 | ZT::09->10::3C9A251C4B | CL::A+09.S::5A2CF2DF | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+09.F | SHEET::09::257BEE2D | NODE::A+09.F::B30FF51C | PROOF | LE::PRIMARY::A+09.F::886B2E7AC2 | AppA→AppH→AppE→AppI→AppM | LE::DUAL::09::S<->F::15422F1798 | LE::DUAL::09::F<->C::735B6CC516 | ZT::08->09::EA1F4C5355 | ZT::09->10::3C9A251C4B | CL::A+09.F::BB4DF5EB | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+09.C | SHEET::09::257BEE2D | NODE::A+09.C::12E534B9 | PROOF | LE::PRIMARY::A+09.C::22671D3008 | AppA→AppJ/AppL→AppI→AppM | LE::DUAL::09::F<->C::735B6CC516 | LE::DUAL::09::C<->R::5CC29CCE65 | ZT::08->09::EA1F4C5355 | ZT::09->10::3C9A251C4B | CL::A+09.C::66699F1F | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+09.R | SHEET::09::257BEE2D | NODE::A+09.R::A2311706 | PROOF | LE::PRIMARY::A+09.R::54E92EAEE2 | AppA→AppM→AppP | LE::DUAL::09::C<->R::5CC29CCE65 | LE::DUAL::09::R<->S::5B5702383A | ZT::08->09::EA1F4C5355 | ZT::09->10::3C9A251C4B | CL::A+09.R::E86AF80E | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+10.S | SHEET::10::A9253C60 | NODE::A+10.S::31CA37A6 | PROOF | LE::PRIMARY::A+10.S::AF89BD9C20 | AppA→AppB→AppC→AppI→AppM | LE::DUAL::10::R<->S::D4D0CE0DC0 | LE::DUAL::10::S<->F::1EC50F9099 | ZT::09->10::3C9A251C4B | ZT::10->11::3094C55531 | CL::A+10.S::FA978171 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+10.F | SHEET::10::A9253C60 | NODE::A+10.F::C51594F4 | PROOF | LE::PRIMARY::A+10.F::5447FA06C6 | AppA→AppH→AppE→AppI→AppM | LE::DUAL::10::S<->F::1EC50F9099 | LE::DUAL::10::F<->C::DCE4149F51 | ZT::09->10::3C9A251C4B | ZT::10->11::3094C55531 | CL::A+10.F::24F4D396 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+10.C | SHEET::10::A9253C60 | NODE::A+10.C::B6C064EA | PROOF | LE::PRIMARY::A+10.C::324B0B787C | AppA→AppJ/AppL/AppK→AppI→AppM | LE::DUAL::10::F<->C::DCE4149F51 | LE::DUAL::10::C<->R::E6A0932C99 | ZT::09->10::3C9A251C4B | ZT::10->11::3094C55531 | CL::A+10.C::93CC6424 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+10.R | SHEET::10::A9253C60 | NODE::A+10.R::B4ABD44B | PROOF | LE::PRIMARY::A+10.R::E93677D15B | AppA→AppM→AppO | LE::DUAL::10::C<->R::E6A0932C99 | LE::DUAL::10::R<->S::D4D0CE0DC0 | ZT::09->10::3C9A251C4B | ZT::10->11::3094C55531 | CL::A+10.R::B70AAE7F | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+11.S | SHEET::11::26396E94 | NODE::A+11.S::B687BE05 | GEN | LE::PRIMARY::A+11.S::44ABDA5AFD | AppA→AppD→AppC→AppI→AppM | LE::DUAL::11::R<->S::E3ADB0102C | LE::DUAL::11::S<->F::0464F34915 | ZT::10->11::3094C55531 | ZT::11->12::0CE9EB966D | CL::A+11.S::4A456752 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+11.F | SHEET::11::26396E94 | NODE::A+11.F::868437F4 | GEN | LE::PRIMARY::A+11.F::3C4652BBC9 | AppA→AppN→AppE→AppI→AppM | LE::DUAL::11::S<->F::0464F34915 | LE::DUAL::11::F<->C::CC7329C9DB | ZT::10->11::3094C55531 | ZT::11->12::0CE9EB966D | CL::A+11.F::E1BBDDC2 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+11.C | SHEET::11::26396E94 | NODE::A+11.C::ABBDB17E | GEN | LE::PRIMARY::A+11.C::1EB08DB400 | AppA→AppL→AppI→AppM | LE::DUAL::11::F<->C::CC7329C9DB | LE::DUAL::11::C<->R::35CB165920 | ZT::10->11::3094C55531 | ZT::11->12::0CE9EB966D | CL::A+11.C::D9B87E74 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+11.R | SHEET::11::26396E94 | NODE::A+11.R::7AE87A6A | GEN | LE::PRIMARY::A+11.R::D2B1E872A9 | AppA→AppM→AppP | LE::DUAL::11::C<->R::35CB165920 | LE::DUAL::11::R<->S::E3ADB0102C | ZT::10->11::3094C55531 | ZT::11->12::0CE9EB966D | CL::A+11.R::C5049EFB | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+12.S | SHEET::12::396A2642 | NODE::A+12.S::8AFB09C6 | IMPL | LE::PRIMARY::A+12.S::0C0FFDA0FC | AppA→AppD→AppC→AppI→AppM | LE::DUAL::12::R<->S::616E73E35A | LE::DUAL::12::S<->F::25090D4ED2 | ZT::11->12::0CE9EB966D | ZT::12->13::A2D2A46407 | CL::A+12.S::545ACF20 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+12.F | SHEET::12::396A2642 | NODE::A+12.F::B302E58B | IMPL | LE::PRIMARY::A+12.F::35B3E48D22 | AppA→AppH→AppE→AppI→AppM | LE::DUAL::12::S<->F::25090D4ED2 | LE::DUAL::12::F<->C::374952644B | ZT::11->12::0CE9EB966D | ZT::12->13::A2D2A46407 | CL::A+12.F::F6A6DAC7 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+12.C | SHEET::12::396A2642 | NODE::A+12.C::5EE77693 | IMPL | LE::PRIMARY::A+12.C::31CBC7BE01 | AppA→AppJ→AppI→AppM | LE::DUAL::12::F<->C::374952644B | LE::DUAL::12::C<->R::F11007DFB5 | ZT::11->12::0CE9EB966D | ZT::12->13::A2D2A46407 | CL::A+12.C::B517C006 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+12.R | SHEET::12::396A2642 | NODE::A+12.R::D6778EC4 | IMPL | LE::PRIMARY::A+12.R::9D69CB509E | AppA→AppM→AppN | LE::DUAL::12::C<->R::F11007DFB5 | LE::DUAL::12::R<->S::616E73E35A | ZT::11->12::0CE9EB966D | ZT::12->13::A2D2A46407 | CL::A+12.R::576B6931 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+13.S | SHEET::13::63F10FF3 | NODE::A+13.S::BB33AE77 | GEN | LE::PRIMARY::A+13.S::A8442A8BF7 | AppA→AppD→AppC→AppI→AppM | LE::DUAL::13::R<->S::521CCD5F0C | LE::DUAL::13::S<->F::712195765E | ZT::12->13::A2D2A46407 | ZT::13->14::C711B5E04C | CL::A+13.S::A59AFCA8 | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+13.F | SHEET::13::63F10FF3 | NODE::A+13.F::6DF103AC | GEN | LE::PRIMARY::A+13.F::14F78AD7DE | AppA→AppF→AppE→AppI→AppM | LE::DUAL::13::S<->F::712195765E | LE::DUAL::13::F<->C::69CBBF74D4 | ZT::12->13::A2D2A46407 | ZT::13->14::C711B5E04C | CL::A+13.F::5824B3DB | STABLE_ANCHOR | keep replay hook live; no extra closure debt surfaced |
| A+13.C | SHEET::13::63F10FF3 | NODE::A+13.C::01392F6E | GEN | LE::PRIMARY::A+13.C::66B1BDC825 | AppA→AppJ/AppL→AppI→AppM | LE::DUAL::13::F<->C::69CBBF74D4 | LE::DUAL::13::C<->R::41779389A6 | ZT::12->13::A2D2A46407 | ZT::13->14::C711B5E04C | CL::A+13.C::E4A9DF13 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+13.R | SHEET::13::63F10FF3 | NODE::A+13.R::7CBBC694 | GEN | LE::PRIMARY::A+13.R::A0582E0515 | AppA→AppM→AppN | LE::DUAL::13::C<->R::41779389A6 | LE::DUAL::13::R<->S::521CCD5F0C | ZT::12->13::A2D2A46407 | ZT::13->14::C711B5E04C | CL::A+13.R::BDCE1322 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+14.S | SHEET::14::157C16BD | NODE::A+14.S::DD7B1A67 | IMPL | LE::PRIMARY::A+14.S::A9AE6629BB | AppA→AppD→AppC→AppI→AppM | LE::DUAL::14::R<->S::EBC7B12B3D | LE::DUAL::14::S<->F::27AD90A1E6 | ZT::13->14::C711B5E04C | ZT::14->15::474F217F79 | CL::A+14.S::1E2A5E69 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+14.F | SHEET::14::157C16BD | NODE::A+14.F::78F815DE | IMPL | LE::PRIMARY::A+14.F::0073381E84 | AppA→AppF→AppE→AppI→AppM | LE::DUAL::14::S<->F::27AD90A1E6 | LE::DUAL::14::F<->C::5A6C5965AC | ZT::13->14::C711B5E04C | ZT::14->15::474F217F79 | CL::A+14.F::050F13D6 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+14.C | SHEET::14::157C16BD | NODE::A+14.C::BBD74203 | IMPL | LE::PRIMARY::A+14.C::B49B86E54D | AppA→AppJ/AppL→AppI→AppM | LE::DUAL::14::F<->C::5A6C5965AC | LE::DUAL::14::C<->R::915968121A | ZT::13->14::C711B5E04C | ZT::14->15::474F217F79 | CL::A+14.C::3C4CC529 | NEAR | carry residual ledger + replay + upgrade path before OK |
| A+14.R | SHEET::14::157C16BD | NODE::A+14.R::5600D32B | IMPL | LE::PRIMARY::A+14.R::A7678FDE96 | AppA→AppM→AppN | LE::DUAL::14::C<->R::915968121A | LE::DUAL::14::R<->S::EBC7B12B3D | ZT::13->14::C711B5E04C | ZT::14->15::474F217F79 | CL::A+14.R::8DD65BCB | BOUND_NEAR | candidate bound; needs exact AppD pin and full replay closure |
| A+15.S | SHEET::15::8452EABD | NODE::A+15.S::CD87C2B2 | REF | LE::PRIMARY::A+15.S::6425799583 | AppA→AppD→AppC→AppI→AppM | LE::DUAL::15::R<->S::1B2F6B2F87 | LE::DUAL::15::S<->F::5B727172FB | ZT::14->15::474F217F79 | ZT::15->01::050AE62C80 | CL::A+15.S::5EF46F66 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+15.F | SHEET::15::8452EABD | NODE::A+15.F::09BDBAF5 | REF | LE::PRIMARY::A+15.F::09504F9F71 | AppA→AppH→AppE→AppI→AppM | LE::DUAL::15::S<->F::5B727172FB | LE::DUAL::15::F<->C::59FD3102D1 | ZT::14->15::474F217F79 | ZT::15->01::050AE62C80 | CL::A+15.F::E0C317B8 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+15.C | SHEET::15::8452EABD | NODE::A+15.C::FF3C8B72 | REF | LE::PRIMARY::A+15.C::4D4B174DC1 | AppA→AppL→AppI→AppM | LE::DUAL::15::F<->C::59FD3102D1 | LE::DUAL::15::C<->R::6FB0715D36 | ZT::14->15::474F217F79 | ZT::15->01::050AE62C80 | CL::A+15.C::A9087A5D | PROXY | needs manuscript-native witness or explicit MIGRATE binding |
| A+15.R | SHEET::15::8452EABD | NODE::A+15.R::BC85FA84 | REF | LE::PRIMARY::A+15.R::15A208E5E7 | AppA→AppM→AppN | LE::DUAL::15::C<->R::6FB0715D36 | LE::DUAL::15::R<->S::1B2F6B2F87 | ZT::14->15::474F217F79 | ZT::15->01::050AE62C80 | CL::A+15.R::05346390 | PROXY | needs manuscript-native witness or explicit MIGRATE binding |

## Family-local sheets

### Family 01 — Orbit ring

- Core transit: 21-station successor loop
- Prev family bridge: `ZT::15->01::050AE62C80` from 15 → 01
- Next family bridge: `ZT::01->02::278FF41520` from 01 → 02
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+01.S | LE::PRIMARY::A+01.S::B76E276A3D | station-order object map, successor table, base-4 gate indexing | STABLE_ANCHOR |
| F | A+01.F | LE::PRIMARY::A+01.F::D6506E918E | orbit phase, successor motion, cyclic cadence | STABLE_ANCHOR |
| C | A+01.C | LE::PRIMARY::A+01.C::8086A598B9 | drift / omission / candidate successor repair | NEAR |
| R | A+01.R | LE::PRIMARY::A+01.R::447BA91F13 | orbit closure seed, loop replay, return-to-start | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::01::S<->F::820C24A892`
- `LE::DUAL::01::F<->C::D2B84591EF`
- `LE::DUAL::01::C<->R::BBD394B9EA`
- `LE::DUAL::01::R<->S::2213C790A3`

### Family 02 — Triangle rails

- Core transit: Su / Me / Sa lane rides
- Prev family bridge: `ZT::01->02::278FF41520` from 01 → 02
- Next family bridge: `ZT::02->03::D979AE8123` from 02 → 03
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+02.S | LE::PRIMARY::A+02.S::63FEB03773 | lane membership tables, rail ordering | STABLE_ANCHOR |
| F | A+02.F | LE::PRIMARY::A+02.F::1BE731DA59 | rail circulation and phase-rotated lane transfer | STABLE_ANCHOR |
| C | A+02.C | LE::PRIMARY::A+02.C::50F3C06573 | lane ambiguity, rail overfit, evidence-plan lane repair | NEAR |
| R | A+02.R | LE::PRIMARY::A+02.R::4B8C94D9AD | rail replay, rail compression, lane-seed regeneration | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::02::S<->F::BB443B7781`
- `LE::DUAL::02::F<->C::208BAFE0BE`
- `LE::DUAL::02::C<->R::88C3790061`
- `LE::DUAL::02::R<->S::1B1830E200`

### Family 03 — Arc triads

- Core transit: 7 rotated 3-cycles
- Prev family bridge: `ZT::02->03::D979AE8123` from 02 → 03
- Next family bridge: `ZT::03->04::1E7D16F5AD` from 03 → 04
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+03.S | LE::PRIMARY::A+03.S::CAAFFCB1F4 | triad membership and rotated order tables | STABLE_ANCHOR |
| F | A+03.F | LE::PRIMARY::A+03.F::23AD4080F5 | rotated triad 3-cycles and local phase spin | STABLE_ANCHOR |
| C | A+03.C | LE::PRIMARY::A+03.C::BFAFFC4C9A | mis-rotation / lane divergence checks | NEAR |
| R | A+03.R | LE::PRIMARY::A+03.R::831D451783 | arc-cycle replay and triad seed compression | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::03::S<->F::0EB18CA990`
- `LE::DUAL::03::F<->C::37C199D4B9`
- `LE::DUAL::03::C<->R::69320A07DC`
- `LE::DUAL::03::R<->S::72C4AF522C`

### Family 04 — Appendix ring

- Core transit: AppA→…→AppP→AppA
- Prev family bridge: `ZT::03->04::1E7D16F5AD` from 03 → 04
- Next family bridge: `ZT::04->05::EA1C1C8D0A` from 04 → 05
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+04.S | LE::PRIMARY::A+04.S::D5E27AD178 | outer 4×4 hub grid and station passports | STABLE_ANCHOR |
| F | A+04.F | LE::PRIMARY::A+04.F::E6D4C6C244 | ring walk, inter-hub transport, phase circulation | STABLE_ANCHOR |
| C | A+04.C | LE::PRIMARY::A+04.C::4C57486BA0 | overlay hubs, admissibility, corridor classification | STABLE_ANCHOR |
| R | A+04.R | LE::PRIMARY::A+04.R::282946037A | ring replay, hub seedpack, outer-crystal regeneration | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::04::S<->F::36486CD374`
- `LE::DUAL::04::F<->C::923F96FC20`
- `LE::DUAL::04::C<->R::2783FF1386`
- `LE::DUAL::04::R<->S::0940739AF9`

### Family 05 — Σ spine

- Core transit: AppA ⇄ AppI ⇄ AppM
- Prev family bridge: `ZT::04->05::EA1C1C8D0A` from 04 → 05
- Next family bridge: `ZT::05->06::2E3D16EB19` from 05 → 06
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+05.S | LE::PRIMARY::A+05.S::5594EF5815 | parse/entry/cert backbone as fixed object path | STABLE_ANCHOR |
| F | A+05.F | LE::PRIMARY::A+05.F::8EFA042BFF | handoff along the brainstem spine | STABLE_ANCHOR |
| C | A+05.C | LE::PRIMARY::A+05.C::EF4D55D428 | truth discipline and abstain law on every route | STABLE_ANCHOR |
| R | A+05.R | LE::PRIMARY::A+05.R::6BC4FB8B6A | replay-sealed return path and fixed-point spine | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::05::S<->F::73F4B6B7F0`
- `LE::DUAL::05::F<->C::00DCC3AF73`
- `LE::DUAL::05::C<->R::237218B660`
- `LE::DUAL::05::R<->S::789D7EF4C8`

### Family 06 — Zero tunnels

- Core transit: Zi → Z* → Zj collapse / re-entry
- Prev family bridge: `ZT::05->06::2E3D16EB19` from 05 → 06
- Next family bridge: `ZT::06->07::3E6B46B41E` from 06 → 07
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+06.S | LE::PRIMARY::A+06.S::60ECB5A494 | explicit Zi/Z* checkpoint objects and invariants | PROXY |
| F | A+06.F | LE::PRIMARY::A+06.F::0C798E16A4 | collapse / expand / bridge / rebase motion law | PROXY |
| C | A+06.C | LE::PRIMARY::A+06.C::6EAAF7BC51 | tunnel legality, preserved invariants, no-guess gate | PROXY |
| R | A+06.R | LE::PRIMARY::A+06.R::EFC773F80A | Z* as return seed and highway for re-entry | PROXY |

DUAL ring IDs:
- `LE::DUAL::06::S<->F::86F3B9D2EA`
- `LE::DUAL::06::F<->C::B7C34B9B95`
- `LE::DUAL::06::C<->R::88314EB461`
- `LE::DUAL::06::R<->S::641E545CC1`

### Family 07 — Router plans

- Core transit: RoutePlan / hub-selection / drop law
- Prev family bridge: `ZT::06->07::3E6B46B41E` from 06 → 07
- Next family bridge: `ZT::07->08::C35311D7D1` from 07 → 08
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+07.S | LE::PRIMARY::A+07.S::E919D9AD7A | RoutePlan objects, hub sets, drop logs | NEAR |
| F | A+07.F | LE::PRIMARY::A+07.F::C4F2517A51 | ride ordering, ArcHub coupling, HCRL rotation | NEAR |
| C | A+07.C | LE::PRIMARY::A+07.C::84195D6947 | overlay choice, cap pressure, ambiguity routing | NEAR |
| R | A+07.R | LE::PRIMARY::A+07.R::64D0B30E25 | plan digest, replayability, route seed compression | NEAR |

DUAL ring IDs:
- `LE::DUAL::07::S<->F::0D94602E09`
- `LE::DUAL::07::F<->C::2F153F5703`
- `LE::DUAL::07::C<->R::E3C1FECB82`
- `LE::DUAL::07::R<->S::BF0D155C11`

### Family 08 — Graph edges

- Core transit: LinkEdge / RouteDigest / EdgeCapsule
- Prev family bridge: `ZT::07->08::C35311D7D1` from 07 → 08
- Next family bridge: `ZT::08->09::EA1F4C5355` from 08 → 09
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+08.S | LE::PRIMARY::A+08.S::E4DBC83A8F | node/edge schemas, edge ids, graph objects | NEAR |
| F | A+08.F | LE::PRIMARY::A+08.F::CED76DCD9C | directed transfers, DUAL/MIGRATE/GEN/PROOF motion | NEAR |
| C | A+08.C | LE::PRIMARY::A+08.C::27EF9329AB | conflict packets, candidate bridges, residual edges | NEAR |
| R | A+08.R | LE::PRIMARY::A+08.R::E486CD549B | RouteDigest, EdgeCapsule, graph replay | NEAR |

DUAL ring IDs:
- `LE::DUAL::08::S<->F::1E6FC07FEA`
- `LE::DUAL::08::F<->C::FB817B57F8`
- `LE::DUAL::08::C<->R::178518D915`
- `LE::DUAL::08::R<->S::AE4B45F6E9`

### Family 09 — Witness–replay

- Core transit: WitnessPtr / ReplayPtr / receipts
- Prev family bridge: `ZT::08->09::EA1F4C5355` from 08 → 09
- Next family bridge: `ZT::09->10::3C9A251C4B` from 09 → 10
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+09.S | LE::PRIMARY::A+09.S::10FCDB3CF5 | witness/replay payload objects and schemas | NEAR |
| F | A+09.F | LE::PRIMARY::A+09.F::886B2E7AC2 | evidence flow through build/verify/integrate stages | NEAR |
| C | A+09.C | LE::PRIMARY::A+09.C::22671D3008 | receipt obligations, residual ledgers, evidence plans | NEAR |
| R | A+09.R | LE::PRIMARY::A+09.R::54E92EAEE2 | replay capsules, deterministic re-check, seals | STABLE_ANCHOR |

DUAL ring IDs:
- `LE::DUAL::09::S<->F::15422F1798`
- `LE::DUAL::09::F<->C::735B6CC516`
- `LE::DUAL::09::C<->R::5CC29CCE65`
- `LE::DUAL::09::R<->S::5B5702383A`

### Family 10 — Closure–truth

- Core transit: NEAR / AMBIG / FAIL / promotion discipline
- Prev family bridge: `ZT::09->10::3C9A251C4B` from 09 → 10
- Next family bridge: `ZT::10->11::3094C55531` from 10 → 11
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+10.S | LE::PRIMARY::A+10.S::AF89BD9C20 | truth-state objects, closure predicates, promotion rules | NEAR |
| F | A+10.F | LE::PRIMARY::A+10.F::5447FA06C6 | closure dynamics, upgrade paths, gate transitions | NEAR |
| C | A+10.C | LE::PRIMARY::A+10.C::324B0B787C | OK/NEAR/AMBIG/FAIL corridor typing and stop-rules | STABLE_ANCHOR |
| R | A+10.R | LE::PRIMARY::A+10.R::E93677D15B | closure receipts, promotion certs, quarantine capsules | NEAR |

DUAL ring IDs:
- `LE::DUAL::10::S<->F::1EC50F9099`
- `LE::DUAL::10::F<->C::DCE4149F51`
- `LE::DUAL::10::C<->R::E6A0932C99`
- `LE::DUAL::10::R<->S::D4D0CE0DC0`

### Family 11 — Seedpack re-entry

- Core transit: seed / reboot / replayable return
- Prev family bridge: `ZT::10->11::3094C55531` from 10 → 11
- Next family bridge: `ZT::11->12::0CE9EB966D` from 11 → 12
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+11.S | LE::PRIMARY::A+11.S::44ABDA5AFD | seed schemas, carrier payloads, reboot capsule objects | PROXY |
| F | A+11.F | LE::PRIMARY::A+11.F::3C4652BBC9 | restore flow, replay/reboot sequence, route restore | PROXY |
| C | A+11.C | LE::PRIMARY::A+11.C::1EB08DB400 | unresolved resolver bindings and re-entry obligations | PROXY |
| R | A+11.R | LE::PRIMARY::A+11.R::D2B1E872A9 | seed compression, self-regeneration, rebootable return | PROXY |

DUAL ring IDs:
- `LE::DUAL::11::S<->F::0464F34915`
- `LE::DUAL::11::F<->C::CC7329C9DB`
- `LE::DUAL::11::C<->R::35CB165920`
- `LE::DUAL::11::R<->S::E3ADB0102C`

### Family 12 — IntentionScript compiler

- Core transit: parse→AST→typecheck→simulate→TS
- Prev family bridge: `ZT::11->12::0CE9EB966D` from 11 → 12
- Next family bridge: `ZT::12->13::A2D2A46407` from 12 → 13
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+12.S | LE::PRIMARY::A+12.S::0C0FFDA0FC | grammar, AST nodes, type environment, throw semantics | STABLE_ANCHOR |
| F | A+12.F | LE::PRIMARY::A+12.F::35B3E48D22 | Σ_Tennis/OneSide/Cascade, 1/2 operators, live compile flow | STABLE_ANCHOR |
| C | A+12.C | LE::PRIMARY::A+12.C::31CBC7BE01 | feasibility windows, object-count/type errors, snap-to-grid constraints | NEAR |
| R | A+12.R | LE::PRIMARY::A+12.R::9D69CB509E | parse→AST→TS replay loop, decompile/recover path | NEAR |

DUAL ring IDs:
- `LE::DUAL::12::S<->F::25090D4ED2`
- `LE::DUAL::12::F<->C::374952644B`
- `LE::DUAL::12::C<->R::F11007DFB5`
- `LE::DUAL::12::R<->S::616E73E35A`

### Family 13 — Pod algebra

- Core transit: Pattern × Prop × Style / 3–13 pod hierarchy
- Prev family bridge: `ZT::12->13::A2D2A46407` from 12 → 13
- Next family bridge: `ZT::13->14::C711B5E04C` from 13 → 14
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+13.S | LE::PRIMARY::A+13.S::A8442A8BF7 | pod-size theorems, Pattern×Prop×Style control surface | STABLE_ANCHOR |
| F | A+13.F | LE::PRIMARY::A+13.F::14F78AD7DE | 3→13 pod transitions, cascade↔fountain↔shower dynamics | STABLE_ANCHOR |
| C | A+13.C | LE::PRIMARY::A+13.C::66B1BDC825 | drop-rate thresholds, uncertainty principle, recovery bounds | NEAR |
| R | A+13.R | LE::PRIMARY::A+13.R::A0582E0515 | hierarchical pods, macro/micro recursion, session grammar | NEAR |

DUAL ring IDs:
- `LE::DUAL::13::S<->F::712195765E`
- `LE::DUAL::13::F<->C::69CBBF74D4`
- `LE::DUAL::13::C<->R::41779389A6`
- `LE::DUAL::13::R<->S::521CCD5F0C`

### Family 14 — Poi flower kernel

- Core transit: FlowerAddr / local byte / phrase lift
- Prev family bridge: `ZT::13->14::C711B5E04C` from 13 → 14
- Next family bridge: `ZT::14->15::474F217F79` from 14 → 15
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+14.S | LE::PRIMARY::A+14.S::A9AE6629BB | local byte B, witness pair (B,I), FlowerAddr object skeleton | NEAR |
| F | A+14.F | LE::PRIMARY::A+14.F::0073381E84 | flower ratio, plane, hand relation, beat-locked compile kernel | NEAR |
| C | A+14.C | LE::PRIMARY::A+14.C::B49B86E54D | admissibility, budget, collision, ambiguity-sudoku pruning | NEAR |
| R | A+14.R | LE::PRIMARY::A+14.R::A7678FDE96 | phrase lift, 256^256 crystal word, replay witness pack | BOUND_NEAR |

DUAL ring IDs:
- `LE::DUAL::14::S<->F::27AD90A1E6`
- `LE::DUAL::14::F<->C::5A6C5965AC`
- `LE::DUAL::14::C<->R::915968121A`
- `LE::DUAL::14::R<->S::EBC7B12B3D`

### Family 15 — MindSweeper board

- Core transit: mines / disarm kits / closure queue
- Prev family bridge: `ZT::14->15::474F217F79` from 14 → 15
- Next family bridge: `ZT::15->01::050AE62C80` from 15 → 01
- DUAL ring: `S↔F`, `F↔C`, `C↔R`, `R↔S`

| View | Dim | PrimaryEdge | Local role | Closure |
|---|---|---|---|---|
| S | A+15.S | LE::PRIMARY::A+15.S::6425799583 | mine registry, nexus rows, closure queue objects | PROXY |
| F | A+15.F | LE::PRIMARY::A+15.F::09504F9F71 | pressure fronts, ordered disarm actions, transition board dynamics | PROXY |
| C | A+15.C | LE::PRIMARY::A+15.C::4D4B174DC1 | unresolved keys, stop-if/escalate branches, obligation clouds | PROXY |
| R | A+15.R | LE::PRIMARY::A+15.R::15A208E5E7 | disarm receipts, learned closure paths, recursive queue compression | PROXY |

DUAL ring IDs:
- `LE::DUAL::15::S<->F::5B727172FB`
- `LE::DUAL::15::F<->C::59FD3102D1`
- `LE::DUAL::15::C<->R::6FB0715D36`
- `LE::DUAL::15::R<->S::1B2F6B2F87`

## Zero-tunnel bridge matrix (ordered family jumps)
| From→To | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01 | — | ZT::01->02::278FF41520 | ZT::01->03::67EA063B44 | ZT::01->04::45A962A9D5 | ZT::01->05::858E74C9F3 | ZT::01->06::71E30136DF | ZT::01->07::36F678AD44 | ZT::01->08::0649DBF8FA | ZT::01->09::C12A7D3B5C | ZT::01->10::9D7A9BC072 | ZT::01->11::724639AB39 | ZT::01->12::342067E89A | ZT::01->13::2311E2E9D0 | ZT::01->14::AADC31E567 | ZT::01->15::466C245AC4 |
| 02 | ZT::02->01::CD97AAA493 | — | ZT::02->03::D979AE8123 | ZT::02->04::1CF521E9E1 | ZT::02->05::5BA4E807E4 | ZT::02->06::65B1AC2983 | ZT::02->07::99E171C624 | ZT::02->08::1A85476972 | ZT::02->09::068C6B37CB | ZT::02->10::DD4A6E57AF | ZT::02->11::4D2EAAEA05 | ZT::02->12::06DFEDF44E | ZT::02->13::5057921738 | ZT::02->14::53E1864986 | ZT::02->15::E39ABFDE8C |
| 03 | ZT::03->01::F8C4A6B341 | ZT::03->02::C80D1CC00B | — | ZT::03->04::1E7D16F5AD | ZT::03->05::D9DD8E4B11 | ZT::03->06::25547342BE | ZT::03->07::5734CCA5FA | ZT::03->08::6D1BAA4D3F | ZT::03->09::CBD6DB1FF7 | ZT::03->10::AC64EDE810 | ZT::03->11::9EAE75C9E0 | ZT::03->12::0731A3787F | ZT::03->13::F5819222F8 | ZT::03->14::6A5C3F6A7F | ZT::03->15::935DBD089B |
| 04 | ZT::04->01::84890A5FAE | ZT::04->02::290F1C0951 | ZT::04->03::50831F7965 | — | ZT::04->05::EA1C1C8D0A | ZT::04->06::32FA3DF7B0 | ZT::04->07::D1DD982676 | ZT::04->08::27964CC3B2 | ZT::04->09::CF1B3897D4 | ZT::04->10::613CD6A86D | ZT::04->11::741A262012 | ZT::04->12::BAB30A6AB8 | ZT::04->13::285D1E71BA | ZT::04->14::0243B32B96 | ZT::04->15::03ED269426 |
| 05 | ZT::05->01::211C64ABD7 | ZT::05->02::76E976743C | ZT::05->03::61727AC47E | ZT::05->04::12C077E983 | — | ZT::05->06::2E3D16EB19 | ZT::05->07::030EEF08D1 | ZT::05->08::C2B6B5BE9F | ZT::05->09::3F3AFA00CA | ZT::05->10::018916DE36 | ZT::05->11::F477E3DBCF | ZT::05->12::D7D61E063F | ZT::05->13::0C6B58F0A7 | ZT::05->14::2A8082F1E4 | ZT::05->15::5F5680560F |
| 06 | ZT::06->01::C991D89434 | ZT::06->02::C675553BCA | ZT::06->03::F03FD7C21E | ZT::06->04::0B09B145BB | ZT::06->05::57FEF5FD7D | — | ZT::06->07::3E6B46B41E | ZT::06->08::938DACEB82 | ZT::06->09::58B1E4DC90 | ZT::06->10::687A962D70 | ZT::06->11::F3F1010062 | ZT::06->12::4C78A805E3 | ZT::06->13::AD268D9FB6 | ZT::06->14::9B3DB7C27B | ZT::06->15::BDC0DF1EA8 |
| 07 | ZT::07->01::8785500311 | ZT::07->02::E07203AB1B | ZT::07->03::37FC73BA75 | ZT::07->04::51A2241ABF | ZT::07->05::EBE036E99F | ZT::07->06::3CBF5914CB | — | ZT::07->08::C35311D7D1 | ZT::07->09::80C8B62C74 | ZT::07->10::2B377377C1 | ZT::07->11::E274D85E2D | ZT::07->12::2375484663 | ZT::07->13::BC6466800C | ZT::07->14::5142AEF7B7 | ZT::07->15::8C8799A9D9 |
| 08 | ZT::08->01::0DBE40A341 | ZT::08->02::3FA1FD5165 | ZT::08->03::10FBEA5975 | ZT::08->04::AF8489BC31 | ZT::08->05::2AAA255195 | ZT::08->06::953133F522 | ZT::08->07::4929105C85 | — | ZT::08->09::EA1F4C5355 | ZT::08->10::9A98CCD257 | ZT::08->11::47DF300745 | ZT::08->12::02AD24331C | ZT::08->13::0565418E99 | ZT::08->14::ED5A747D7C | ZT::08->15::1119DD1BDE |
| 09 | ZT::09->01::70E5164821 | ZT::09->02::1E8BEAE99C | ZT::09->03::3D8C8AEB6E | ZT::09->04::AC4A12D0C7 | ZT::09->05::649EB97F96 | ZT::09->06::6A5243D6C0 | ZT::09->07::95D98301B6 | ZT::09->08::2F9EB32783 | — | ZT::09->10::3C9A251C4B | ZT::09->11::3FD4037BB2 | ZT::09->12::5714315960 | ZT::09->13::6090A9C50C | ZT::09->14::3268931C05 | ZT::09->15::ACD396AFB1 |
| 10 | ZT::10->01::6C93C7D1C9 | ZT::10->02::6F60CEBFAF | ZT::10->03::F09759895E | ZT::10->04::499BDB73A6 | ZT::10->05::08CFA10F49 | ZT::10->06::F09663552C | ZT::10->07::8B62FB6077 | ZT::10->08::44AF8B95E1 | ZT::10->09::F36F5EB00F | — | ZT::10->11::3094C55531 | ZT::10->12::0A0E6EBC0D | ZT::10->13::E1DBD44BE6 | ZT::10->14::ACBB6FA387 | ZT::10->15::B44965BA13 |
| 11 | ZT::11->01::7405B74CEF | ZT::11->02::A586A38B2C | ZT::11->03::872E86E18B | ZT::11->04::E69AABC7D1 | ZT::11->05::D9DCC1329A | ZT::11->06::74CA63CF95 | ZT::11->07::29D8628D05 | ZT::11->08::1DF862B867 | ZT::11->09::8B3F10F1D6 | ZT::11->10::C2E26763D0 | — | ZT::11->12::0CE9EB966D | ZT::11->13::63A666E15A | ZT::11->14::B58BA7EE3F | ZT::11->15::4572E57B8F |
| 12 | ZT::12->01::F91AF8BFA2 | ZT::12->02::B99001D902 | ZT::12->03::D0DA79F147 | ZT::12->04::F23BEE8B1A | ZT::12->05::5BA7AA8C30 | ZT::12->06::52AFBA0BCB | ZT::12->07::C3F93333EE | ZT::12->08::C09F1E8F07 | ZT::12->09::9ADBAED3E6 | ZT::12->10::EC62577D4F | ZT::12->11::C5890ADFCC | — | ZT::12->13::A2D2A46407 | ZT::12->14::CB59002679 | ZT::12->15::43D66E4B49 |
| 13 | ZT::13->01::66FA974E0F | ZT::13->02::2BEF452AEE | ZT::13->03::369E5A0523 | ZT::13->04::7D8E0CF458 | ZT::13->05::4D15980410 | ZT::13->06::5C1011624A | ZT::13->07::9B6D5514E8 | ZT::13->08::7E0C47B9F7 | ZT::13->09::EACB199824 | ZT::13->10::9846296CC2 | ZT::13->11::45AD1BCCDB | ZT::13->12::3E79E3F0A2 | — | ZT::13->14::C711B5E04C | ZT::13->15::FF20A9DE67 |
| 14 | ZT::14->01::6136531E15 | ZT::14->02::84B75461F3 | ZT::14->03::D5A89B1B51 | ZT::14->04::A32063E349 | ZT::14->05::A00120C1C0 | ZT::14->06::E7C1BCE6B3 | ZT::14->07::C63352F1B4 | ZT::14->08::67FF807008 | ZT::14->09::01FF9870F2 | ZT::14->10::DCC6B01896 | ZT::14->11::B7546B2CF0 | ZT::14->12::187C50BF6E | ZT::14->13::0BEB82C50A | — | ZT::14->15::474F217F79 |
| 15 | ZT::15->01::050AE62C80 | ZT::15->02::6AB18E3CE0 | ZT::15->03::F498DA13B5 | ZT::15->04::ADEA31F78D | ZT::15->05::E70E76B788 | ZT::15->06::B31DFFAF52 | ZT::15->07::0E32D9C322 | ZT::15->08::5F08443888 | ZT::15->09::E83752CD38 | ZT::15->10::A3A2C4BCF1 | ZT::15->11::A27A9E4EB6 | ZT::15->12::46FF66AA6B | ZT::15->13::171E5A114C | ZT::15->14::FA118C27B4 | — |

## Closure legend
- `STABLE_ANCHOR` ← ANCHORED: keep replay hook live; no extra closure debt surfaced
- `NEAR` ← ANCHORED_NEAR: carry residual ledger + replay + upgrade path before OK
- `BOUND_NEAR` ← BOUND_NEAR: candidate bound; needs exact AppD pin and full replay closure
- `PROXY` ← PROXY: needs manuscript-native witness or explicit MIGRATE binding
- `PENDING` ← PENDING: needs target, witness, and route before promotion

## Compression
`TENSOR_v2Y = {Nodes60, PrimaryEdges60, DUAL60, BridgePacks210, Closure60}`

Every dimension now has a deterministic node, a primary LinkEdge, a local DUAL rotation into adjacent views, an incoming/outgoing family tunnel, and a closure cell that preserves its current truth discipline.
