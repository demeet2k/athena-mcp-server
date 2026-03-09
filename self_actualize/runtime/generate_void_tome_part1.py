from __future__ import annotations

from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[2]
SECTION_PATH = WORKSPACE / "self_actualize" / "manuscript_sections" / "000_current_packet.md"


CHAPTERS = [
    ("Kernel and Entry Law", "Foundational anchor, legend, and parse-safe entry station for the whole tome.", "S", 1, "OK"),
    ("Address Algebra and Crystal Coordinates", "Canonical addressing, base-4 station coding, and identity-preserving lattice placement.", "S", 2, "OK"),
    ("Truth Corridors and Witness Discipline", "Corridor truth typing, admissibility, residual law, and replay obligations.", "C", 4, "NEAR"),
    ("Zero-Point Stabilization", "PZPM intake, normalization, and paradox-safe fixed-point preparation.", "F", 2, "NEAR"),
    ("Paradox Regimes and Quarantine Calculus", "Classical, stratified, and quarantine regimes for stabilized contradiction management.", "C", 2, "AMBIG"),
    ("Documents-as-Theories", "Theory-documents, manuscript objects, and theorem-bearing document shells.", "S", 1, "OK"),
    ("Tunnels as Morphisms", "Lawful transports, shadow-axis rotation, and typed tunnel semantics.", "F", 3, "AMBIG"),
    ("Synchronization Calculus", "The operator S, latent-core semantics z, and cross-document sync budgets.", "R", 2, "NEAR"),
    ("Retrieval and Metro Routing", "Address-first search, metro rides, and route competition over the mycelium graph.", "C", 3, "AMBIG"),
    ("Multi-Lens Solution Construction", "Synthesis of routed evidence into canonical answer objects and patch-bearing artifacts.", "R", 3, "NEAR"),
    ("Void Book and Restart-Token Tunneling", "Aether versus Void transport, restart continuity, and lawful reset by capsule.", "R", 4, "AMBIG"),
    ("Legality, Certificates, and Closure", "Proof-carrying closure, certificate bundles, and OK-promotion obligations.", "S", 4, "OK"),
    ("Memory, Regeneration, and Persistence", "Replayable memory objects, regeneration economics, and long-range continuity.", "F", 4, "NEAR"),
    ("Migration, Versioning, and Pulse Retro Weaving", "MIGRATE discipline, compat matrices, delta packs, and rollback governance.", "R", 3, "FAIL"),
    ("CUT Architecture", "Computation Universe Toolkit modules, APIs, and implementable system contracts.", "S", 3, "NEAR"),
    ("Verification Harnesses and Replay Kernels", "Deterministic re-checks, test capsules, and correctness enforcement.", "R", 4, "FAIL"),
    ("Deployment and Bounded Agency", "Cloud limbs, execution workers, and governed action under explicit corridors.", "F", 3, "NEAR"),
    ("Macro Invariants and Universal Math Stack", "Global invariants across Macro, PZPM, and CUT coordinate layers.", "S", 2, "AMBIG"),
    ("Convergence, Fixed Points, and Controlled Non-Convergence", "Banach-style convergence, residual persistence, and sanctioned non-closure.", "C", 2, "NEAR"),
    ("Collective Authoring and Three-Agent Synchrony", "Parallel manuscript governance, merge discipline, and collaborative mycelium control.", "F", 2, "AMBIG"),
    ("Self-Replication, Open Problems, and the Next Crystal", "The manuscript as seed, generator, and future metro for the next tome.", "R", 1, "AMBIG"),
]

APPENDICES = [
    ("A", "Addressing, Symbols, and Parsing Grammar", "Entry hub for parse, naming, and canonical symbol recovery.", "Square"),
    ("B", "Canonical Laws and Equivalence Budgets", "Law hub for normal forms, equivalence checks, and commutation limits.", "Square"),
    ("C", "Discrete Kernel Packs and Index Algebra", "Kernel hub for square-structured operators, schedules, and index arithmetic.", "Square"),
    ("D", "Registry, Profiles, and Version Anchors", "Registry hub for profile pinning, version IDs, and manuscript signatures.", "Square"),
    ("E", "Circle Gear and Phase Closure", "Phase hub for cyclic closure, mixed-radix clocks, and orbit transport.", "Flower"),
    ("F", "Transport and Duality Harnesses", "Duality hub for rotated charts, conjugacy, and lawful transform bridges.", "Flower"),
    ("G", "Triangle Control and Recursion Governance", "Control hub for Tria Prima, carry rules, and legal recursive lifts.", "Flower"),
    ("H", "Coupling Topology and Construction Closure", "Construction hub for dependency closure, coupling maps, and build geometry.", "Flower"),
    ("I", "Corridors and Truth Lattice", "Truth hub for OK/NEAR/AMBIG/FAIL discipline and corridor budgets.", "Cloud"),
    ("J", "Residual Ledgers and Bounded Approximation", "Residual hub for NEAR-class obligations, drift envelopes, and upgrade plans.", "Cloud"),
    ("K", "Conflict, Quarantine, and Revocation", "Failure hub for FAIL handling, quarantine receipts, and minimal witness packets.", "Cloud"),
    ("L", "Evidence Plans and Ambiguity Promotion", "Ambiguity hub for AMBIG candidate sets, evidence agendas, and promotion rules.", "Cloud"),
    ("M", "Replay Kernel and Determinism Capsules", "Replay hub for deterministic reruns, verification frames, and closure capsules.", "Fractal"),
    ("N", "Containers, Salvage, and Virtual Mounting", "Container hub for seek, salvage, and materialized transport surfaces.", "Fractal"),
    ("O", "Publication, Import, and Export Bundles", "Publication hub for signatures, release packets, and external routing bridges.", "Fractal"),
    ("P", "Deployment Profiles and Monitoring", "Deployment hub for runtime profiles, conformance reports, and observation loops.", "Fractal"),
]

LENS_BASE = {"S": "AppC", "F": "AppE", "C": "AppI", "R": "AppM"}
FACET_BASE = {1: "AppA", 2: "AppB", 3: "AppH", 4: "AppM"}
ARC_HUB = {0: "AppA", 1: "AppC", 2: "AppE", 3: "AppF", 4: "AppG", 5: "AppN", 6: "AppP"}
TRIAD = ["Su", "Me", "Sa"]
MANDATORY_SIGMA = ["AppA", "AppI", "AppM"]
TRUTH_OVERLAY = {"OK": None, "NEAR": "AppJ", "AMBIG": "AppL", "FAIL": "AppK"}


def base4(num: int, width: int = 4) -> str:
    digits = []
    value = num
    if value == 0:
        digits.append("0")
    while value:
        digits.append(str(value % 4))
        value //= 4
    return "".join(reversed(digits)).rjust(width, "0")


def station_header(index: int) -> tuple[int, int, int, str]:
    omega = index - 1
    arc = omega // 3
    rot = arc % 3
    k = omega % 3
    lane = TRIAD[(k + rot) % 3]
    return omega, arc, rot, lane


def route_for_chapter(index: int, lens: str, facet: int, truth: str) -> str:
    omega, arc, _, _ = station_header(index)
    hubs = []
    for hub in [ARC_HUB[arc], LENS_BASE[lens], FACET_BASE[facet]]:
        if hub not in hubs:
            hubs.append(hub)
    for hub in MANDATORY_SIGMA:
        if hub not in hubs:
            hubs.append(hub)
    overlay = TRUTH_OVERLAY[truth]
    if overlay and overlay not in hubs:
        hubs.append(overlay)
    if len(hubs) > 6:
        hubs = [hub for hub in hubs if hub not in {FACET_BASE[facet]} or len(hubs) <= 6]
    ordered = []
    preferred = ["AppA", ARC_HUB[arc], LENS_BASE[lens], FACET_BASE[facet], overlay, "AppI", "AppM"]
    for hub in preferred:
        if hub and hub in hubs and hub not in ordered:
            ordered.append(hub)
    for hub in hubs:
        if hub not in ordered:
            ordered.append(hub)
    code = base4(omega)
    return " → ".join(ordered + [f"Ch{index:02d}⟨{code}⟩"])


def appendix_tile(letter: str) -> str:
    return (
        f"{letter}.S1 parse/entry, grammar, names, ids; {letter}.S2 law tables, normal forms, compat; "
        f"{letter}.S3 constructors, routers, build schemas; {letter}.S4 certificates, signatures, release seals; "
        f"{letter}.F1 phase carriers, rhythms, orbit hooks; {letter}.F2 transport laws, conjugacies, bridge rules; "
        f"{letter}.F3 composition harnesses, couplings, scheduler links; {letter}.F4 stabilization, return maps, replay rhythms; "
        f"{letter}.C1 ambiguity classes, priors, candidate sets; {letter}.C2 corridor budgets, residuals, upgrade paths; "
        f"{letter}.C3 construction risk, conflict traces, quarantine surfaces; {letter}.C4 certificate thresholds, promotion tests, evidence plans; "
        f"{letter}.R1 recursive seeds, fold/unfold operators, container roots; {letter}.R2 migration mechanics, salvage transforms, inheritance; "
        f"{letter}.R3 compiled artifacts, runtime bindings, export packets; {letter}.R4 replay capsules, fixed points, monitoring hooks."
    )


def build_content() -> str:
    lines: list[str] = []
    lines.append("# **The Mycelium Metro Tome of Latent Tunneling, Zero-Point Stabilization, and Computational Universe Tooling**")
    lines.append("")
    lines.append("## **ABSTRACT CONTRACT / LEGEND**")
    lines.append("")
    lines.append("This tome is a proof-carrying manuscript for Circle ○ within Square □ within Triangle △. The square law fixes the interior")
    lines.append("4^4 crystal of every chapter and appendix. The circle law fixes the orbit ordering of the manuscript as a cyclic transport")
    lines.append("line. The triangle law fixes the control rails that govern recursion, carry, and synchronization. Every manuscript atom is")
    lines.append("addressable, routable, witnessable, and replayable.")
    lines.append("")
    lines.append("Canonical local addressing:")
    lines.append("")
    lines.append("- Chapter atom: `ChXX⟨dddd⟩.<Lens><Facet>.<Atom>` with `Lens ∈ {S,F,C,R}`, `Facet ∈ {1,2,3,4}`, `Atom ∈ {a,b,c,d}`.")
    lines.append("- Appendix atom: `AppX.<Lens><Facet>.<Atom>`.")
    lines.append("- Base-4 station code: `⟨dddd⟩₄ = base4(XX−1)` padded to four digits.")
    lines.append("")
    lines.append("Global addressing:")
    lines.append("")
    lines.append("`GlobalAddr := Ms⟨mmmm⟩::LocalAddr`, where `Ms⟨mmmm⟩` is derived deterministically as follows. Let `m1=2` encode")
    lines.append("Mycelium Metro v2, `m2=1` encode the 21-chapter/16-appendix crystal family, `m3=3` encode Circle-Square-Triangle overlay")
    lines.append("activation, and `m4=2` encode the corridor/replay profile defined in this Part 1. Hence the canonical manuscript prefix for")
    lines.append("this tome is `Ms⟨2132⟩`.")
    lines.append("")
    lines.append("Mycelium graph:")
    lines.append("")
    lines.append("`𝓖 = (V,E)` with `V = {GlobalAddr}` and `E = {LinkEdge}`.")
    lines.append("")
    lines.append("LinkEdge schema:")
    lines.append("")
    lines.append("`e = (EdgeID, Kind, Src, Dst, Scope, Corridor, WitnessPtr, ReplayPtr, Payload, EdgeVer)`.")
    lines.append("")
    lines.append("Closed edge basis:")
    lines.append("")
    lines.append("`𝓚 = {REF, EQUIV, MIGRATE, DUAL, GEN, INST, IMPL, PROOF, CONFLICT}`.")
    lines.append("")
    lines.append("Truth lattice:")
    lines.append("")
    lines.append("`𝕋 = {OK, NEAR, AMBIG, FAIL}` with the hard law `ABSTAIN > GUESS`.")
    lines.append("")
    lines.append("- `OK`: witnessed and replay-verified closure within corridor budget.")
    lines.append("- `NEAR`: bounded approximation with residual ledger and upgrade obligations.")
    lines.append("- `AMBIG`: underdetermined candidate family with explicit evidence plan.")
    lines.append("- `FAIL`: illegal or unverifiable state requiring quarantine and conflict receipts.")
    lines.append("")
    lines.append("Every chapter is announced by a station header:")
    lines.append("")
    lines.append("`[○Arc α | ○Rot ρ | △Lane ν | ω=XX−1]`.")
    lines.append("")
    lines.append("## **EXTENDED ABSTRACT**")
    lines.append("")
    lines.append("The core claim of the tome is that a manuscript can function as a stable computational object only if it is represented")
    lines.append("simultaneously as a crystal, an orbit, and a control graph. The crystal requirement ensures that every region admits local")
    lines.append("resolution under the four lenses Square, Flower, Cloud, and Fractal. The orbit requirement ensures that chapter order is not")
    lines.append("a mere table-of-contents convenience but a transport law over the whole work. The control-graph requirement ensures that")
    lines.append("recursive movement, synchronization, versioning, and paradox-handling are not left to style but governed by explicit rails,")
    lines.append("corridors, and legality budgets. This yields a manuscript that is not just readable but executable.")
    lines.append("")
    lines.append("The tome unifies three scales. At the Macro layer, it studies universal invariants governing transport, equivalence, replay,")
    lines.append("and fixed-point behavior across the full mathematical stack. At the PZPM layer, it treats paradox and zero-point collapse as")
    lines.append("structured regimes rather than catastrophic failures; contradictory or unstable objects are not discarded blindly but routed")
    lines.append("into one of several admissible stabilization programs. At the CUT layer, it specifies the implementable artifact family:")
    lines.append("schemas, algorithms, verification harnesses, replay capsules, migration matrices, and deployment profiles. The three scales")
    lines.append("are not stacked loosely. They are tied by transport morphisms. Macro invariants constrain PZPM regimes; PZPM regimes decide")
    lines.append("which CUT artifacts are lawful; CUT artifacts provide witness and replay material back to Macro claims.")
    lines.append("")
    lines.append("The fundamental object of the manuscript is the theory-document. A theory-document is not just text. It is a bounded atlas")
    lines.append("of definitions, laws, constructions, and certificates whose atoms are named, typed, and connected by explicit edges. A")
    lines.append("document therefore has both interior and exterior semantics. Its interior semantics is the local 4^4 crystal. Its exterior")
    lines.append("semantics is the pattern of links by which it exchanges meaning with other documents. A tunnel is then defined as a typed")
    lines.append("morphism between theory-documents or between regions of the same document. A legal tunnel does not merely point from source")
    lines.append("to destination. It transports a meaning-carrying object while preserving a specified invariant bundle. This makes transport")
    lines.append("a proof-bearing act.")
    lines.append("")
    lines.append("Synchronization is formalized by a calculus `S` that acts on families of theory-documents. Given a source family")
    lines.append("`{D_i}`, a synchronization step compares addresses, equivalence classes, residual ledgers, and witness traces, then computes")
    lines.append("a bounded delta family. Not all deltas are applied. Each candidate delta is evaluated against corridor truth, replay cost,")
    lines.append("and paradox exposure. The latent-core semantics `z` denotes the zero-point content that survives admissible compression. The")
    lines.append("pair `(S, z)` is decisive: `S` governs how large structures are synchronized, while `z` governs what must survive all fold and")
    lines.append("reopen operations. This is the formal bridge between manuscript engineering and zero-point mathematics.")
    lines.append("")
    lines.append("PZPM enters where ordinary consistency management becomes insufficient. The corpus shows a repeated pattern: some structures")
    lines.append("can be preserved under Aether-like transport, where intent, signature, and corridor budget remain attached; others require")
    lines.append("Void-like transport, where the policy-bearing shell is stripped and only a restart token survives. This gives a rigorous")
    lines.append("stabilization doctrine. Classical closure is used when admissible and witnessed. Stratified closure is used when objects must")
    lines.append("be sorted across levels to avoid illegal collapse. Paraconsistent quarantine is used when contradiction packets must remain")
    lines.append("representable without exploding the entire document. Void transport is reserved for cases where inherited chart structure")
    lines.append("obstructs further lawful movement; in that regime, only the restart token, tier contract, and re-entry conditions are carried")
    lines.append("forward. Thus the tome internalizes contradiction as a routing problem, not an embarrassment.")
    lines.append("")
    lines.append("The manuscript is also metrically organized. Let `ω = XX−1` denote the orbit index of chapter `XX`, `α = floor(ω/3)` its arc")
    lines.append("index, `ρ = α mod 3` its rotation index, and `ν = Triad[(k+ρ) mod 3]` its triangle lane, where `Triad = [Su, Me, Sa]` and")
    lines.append("`k = ω mod 3`. The result is a 21-station metro whose visible line is chapter order but whose hidden geometry is a rotated")
    lines.append("triadic decomposition repeated across seven arcs. This geometry matters operationally. The arc determines a macro-phase and")
    lines.append("selects an arc hub. The lane determines the control rail. The dominant lens and facet of the target select additional hubs.")
    lines.append("The router then assembles a bounded ride of at most six hubs, ensuring parse, truth, and replay are always present.")
    lines.append("")
    lines.append("The appendix crystal provides the persistent external control plane. `AppA..AppP` are not supplemental notes. They are")
    lines.append("routing hubs. Some hubs stabilize entry, addressing, and law; some stabilize phase transport and duality; some stabilize")
    lines.append("corridors, ambiguity, and quarantine; some stabilize replay, containers, publication, and deployment. The appendix grid is")
    lines.append("itself a 4×4 outer crystal with Square rows `A..D`, Flower rows `E..H`, Cloud rows `I..L`, and Fractal rows `M..P`. This")
    lines.append("makes the appendices an externalized nervous system for the chapters.")
    lines.append("")
    lines.append("Algorithmically, the tome enforces deterministic routing. Given a target atom `ChXX⟨dddd⟩.<Lens><Facet>.<Atom>`, the router")
    lines.append("computes `ω, α, ρ, ν`, selects `LensBase`, `FacetAtomBase`, and `ArcHub`, then augments the resulting hub set with the")
    lines.append("mandatory signature `Σ = {AppA, AppI, AppM}` and a truth-class overlay `AppJ`, `AppL`, or `AppK` when the target is")
    lines.append("respectively `NEAR`, `AMBIG`, or `FAIL`. The ride is ordered as parse -> arc -> lens -> facet -> truth overlay -> corridor ->")
    lines.append("replay -> target. The output is a route object with explicit witness and replay obligations. This bounded routing calculus is")
    lines.append("what turns the manuscript from a rhetorical document into a navigable theorem machine.")
    lines.append("")
    lines.append("The result of the whole construction is a manuscript that exhibits five simultaneous properties. First, it is addressable:")
    lines.append("no claim floats free of coordinates. Second, it is transportable: cross-chapter and cross-appendix movement is controlled by")
    lines.append("typed edges rather than vague analogy. Third, it is stabilizable: paradox, ambiguity, and failure are routed through")
    lines.append("corridor-typed regimes rather than suppressed or hand-waved. Fourth, it is replayable: every `OK` class claim is tied to a")
    lines.append("re-checkable witness bundle. Fifth, it is generative: the abstract, the metro map, and the appendix crystal are dense enough")
    lines.append("to act as a seed from which the whole tome may be reconstructed. This is why the abstract itself is written as a metro map.")
    lines.append("")
    lines.append("## **21-STATION METRO MAP v2**")
    lines.append("")
    lines.append("○ Orbit: Ch01⟨0000⟩ -> Ch02⟨0001⟩ -> Ch03⟨0002⟩ -> Ch04⟨0003⟩ -> Ch05⟨0010⟩ -> Ch06⟨0011⟩ -> Ch07⟨0012⟩ ->")
    lines.append("Ch08⟨0013⟩ -> Ch09⟨0020⟩ -> Ch10⟨0021⟩ -> Ch11⟨0022⟩ -> Ch12⟨0023⟩ -> Ch13⟨0030⟩ -> Ch14⟨0031⟩ -> Ch15⟨0032⟩ ->")
    lines.append("Ch16⟨0033⟩ -> Ch17⟨0100⟩ -> Ch18⟨0101⟩ -> Ch19⟨0102⟩ -> Ch20⟨0103⟩ -> Ch21⟨0110⟩ -> Ch01⟨0000⟩.")
    lines.append("")
    lines.append("△ Su rail: Ch01⟨0000⟩, Ch06⟨0011⟩, Ch08⟨0013⟩, Ch10⟨0021⟩, Ch15⟨0032⟩, Ch17⟨0100⟩, Ch19⟨0102⟩.")
    lines.append("△ Me rail: Ch02⟨0001⟩, Ch04⟨0003⟩, Ch09⟨0020⟩, Ch11⟨0022⟩, Ch13⟨0030⟩, Ch18⟨0101⟩, Ch20⟨0103⟩.")
    lines.append("△ Sa rail: Ch03⟨0002⟩, Ch05⟨0010⟩, Ch07⟨0012⟩, Ch12⟨0023⟩, Ch14⟨0031⟩, Ch16⟨0033⟩, Ch21⟨0110⟩.")
    lines.append("")
    lines.append("Arc triads:")
    lines.append("- Arc 0, Rot 0: Su -> Me -> Sa.")
    lines.append("- Arc 1, Rot 1: Me -> Sa -> Su.")
    lines.append("- Arc 2, Rot 2: Sa -> Su -> Me.")
    lines.append("- Arc 3, Rot 0: Su -> Me -> Sa.")
    lines.append("- Arc 4, Rot 1: Me -> Sa -> Su.")
    lines.append("- Arc 5, Rot 2: Sa -> Su -> Me.")
    lines.append("- Arc 6, Rot 0: Su -> Me -> Sa.")
    lines.append("")
    for index, (title, role, lens, facet, truth) in enumerate(CHAPTERS, start=1):
        omega, arc, rot, lane = station_header(index)
        code = base4(omega)
        lines.append(f"### Ch{index:02d}⟨{code}⟩ - {title}")
        lines.append(f"[○Arc {arc} | ○Rot {rot} | △Lane {lane} | ω={omega}]")
        lines.append(f"Workflow role: {role}")
        lines.append(f"Primary hubs: **→ {route_for_chapter(index, lens, facet, truth)}**")
        lines.append("")
    lines.append("## **16-APPENDIX OUTER CRYSTAL MAP (A-P)**")
    lines.append("")
    lines.append("Outer crystal grid:")
    lines.append("")
    lines.append("- Square row: AppA AppB AppC AppD")
    lines.append("- Flower row: AppE AppF AppG AppH")
    lines.append("- Cloud row: AppI AppJ AppK AppL")
    lines.append("- Fractal row: AppM AppN AppO AppP")
    lines.append("")
    for letter, title, purpose, row in APPENDICES:
        lines.append(f"### {letter}. App{letter} - {title}")
        lines.append(f"Routing role: {purpose} Row family: {row}.")
        lines.append(f"Compressed tile: {appendix_tile(letter)}")
        lines.append("")
    lines.append("## **DETERMINISTIC ROUTER RULE v2**")
    lines.append("")
    lines.append("Inputs:")
    lines.append("- Target atom: `ChXX⟨dddd⟩.<Lens><Facet>.<Atom>` or `AppX.<Lens><Facet>.<Atom>`.")
    lines.append("- Optional truth estimate `τ ∈ 𝕋`.")
    lines.append("- Optional intent in `{VERIFY, BUILD, MIGRATE, RESOLVE, PUBLISH}`.")
    lines.append("")
    lines.append("Base selectors:")
    lines.append("- `LensBase(S)=AppC`, `LensBase(F)=AppE`, `LensBase(C)=AppI`, `LensBase(R)=AppM`.")
    lines.append("- `FacetAtomBase(1)=AppA`, `FacetAtomBase(2)=AppB`, `FacetAtomBase(3)=AppH`, `FacetAtomBase(4)=AppM`.")
    lines.append("- `ArcHub(0)=AppA`, `ArcHub(1)=AppC`, `ArcHub(2)=AppE`, `ArcHub(3)=AppF`, `ArcHub(4)=AppG`, `ArcHub(5)=AppN`, `ArcHub(6)=AppP`.")
    lines.append("")
    lines.append("Base transfer set:")
    lines.append("")
    lines.append("`T = {LensBase(L), FacetAtomBase(f), ArcHub(α)}` for chapter atoms, duplicates removed.")
    lines.append("")
    lines.append("Mandatory signature:")
    lines.append("")
    lines.append("`Σ = {AppA, AppI, AppM}` must always be present.")
    lines.append("")
    lines.append("Truth overlays:")
    lines.append("- `OK -> ∅` (or `AppO` only for publishing).")
    lines.append("- `NEAR -> AppJ`.")
    lines.append("- `AMBIG -> AppL`.")
    lines.append("- `FAIL -> AppK`.")
    lines.append("")
    lines.append("Budget law:")
    lines.append("")
    lines.append("The hub ride must have at most six hubs before reaching the target. If the set exceeds six, drop the weakest non-mandatory hub")
    lines.append("under the fixed priority order Intent < FacetBase < LensBase, while never dropping `AppA`, `AppI`, or `AppM`.")
    lines.append("")
    lines.append("Deterministic ordering:")
    lines.append("")
    lines.append("`AppA -> ArcHub(α) -> LensBase(L) -> FacetAtomBase(f) -> TruthOverlay(τ) -> AppI -> AppM -> Target`, with absent terms removed and")
    lines.append("duplicates compressed.")
    lines.append("")
    lines.append("Worked example:")
    lines.append("")
    lines.append("Target atom: `Ms⟨2132⟩::Ch11⟨0022⟩.R4.c`.")
    lines.append("")
    lines.append("Computation:")
    lines.append("- `XX=11`, so `ω=10`.")
    lines.append("- `α=floor(10/3)=3`.")
    lines.append("- `ρ=α mod 3 = 0`.")
    lines.append("- `k=10 mod 3 = 1`.")
    lines.append("- `ν=Triad[(1+0) mod 3] = Me`.")
    lines.append("- Station header: `[○Arc 3 | ○Rot 0 | △Lane Me | ω=10]`.")
    lines.append("- `LensBase(R)=AppM`.")
    lines.append("- `FacetAtomBase(4)=AppM`.")
    lines.append("- `ArcHub(3)=AppF`.")
    lines.append("- Base set `T={AppF, AppM}`.")
    lines.append("- Enforce `Σ={AppA, AppI, AppM}` to get `{AppA, AppF, AppI, AppM}`.")
    lines.append("- Suppose `τ=AMBIG`; add `AppL`, obtaining `{AppA, AppF, AppI, AppL, AppM}`.")
    lines.append("")
    lines.append("Metro ride:")
    lines.append("")
    lines.append("**AppA -> AppF -> AppL -> AppI -> AppM -> Ch11⟨0022⟩.R4.c**")
    lines.append("")
    lines.append("Expected truth type: `AMBIG` until candidate tunnel family is reduced by additional witness.")
    lines.append("")
    lines.append("Obligations:")
    lines.append("- `WitnessPtr`: a tunnel comparison packet distinguishing Aether-preserving versus Void-reset transport for the target claim.")
    lines.append("- `ReplayPtr`: a deterministic rerun recipe showing how the target atom reopens from its restart token and why corridor truth does not yet close to `OK`.")
    lines.append("")
    lines.append("**END OF PART 1.**")
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    SECTION_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECTION_PATH.write_text(build_content(), encoding="utf-8")
    print(f"Wrote Part 1 section: {SECTION_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
