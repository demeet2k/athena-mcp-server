# CRYSTAL: Xi108:W3:A10:S30 | face=S | node=40 | depth=2 | phase=Mutable
# METRO: Sa
# BRIDGES: Xi108:W3:A10:S29→Xi108:W3:A10:S31→Xi108:W2:A10:S30→Xi108:W3:A9:S30→Xi108:W3:A11:S30

"""
ATHENA 108D A+ CRYSTAL HOLOGRAM — MCP Extension Package
========================================================
Extends the Athena Nervous System MCP server with the full 108D organism:
  - 36 shells, 666 nodes, 12 archetypes, 3 wreaths
  - 3D→12D alternating dimensional atlas
  - 12D organ atlas with 6 bilateral dyads
  - 7-class live-lock lattice
  - 420-beat master clock
  - 10 legal move primitives
  - 6 conservation laws
  - 4 overlay registries
  - Full transport stack
  - Möbius lens calculus (4×4 kernel, SFCR lattice, 96-slot cockpit)
  - Stage code ladder (S3→Ω→A+)
  - Angel formal self-model (12-piece AI object with four-lens observability)
  - Angel geometry (6-chart state manifold, metric, curvature, sheaf, 7 axioms)
  - Distributed brain network (4 elements × 6 bridges × 4 closures × 1 aether)
  - NEXT-Omega live cell constitution (6 schemas, 14-station metro)
  - Dimensional emergence path (7 phases, kernel embedding law)
  - Hologram reading protocol (4-face, seed equation, process grammar, Rosetta)
  - Inverse crystal (3D seed, 14-stage octave lift, A+ crown, projection stack)
  - Mycelium graph (universal shard/edge/node schema, promotion state machine)
  - Guild Hall (social coordination organ, quest boards, promotion membrane)
  - Agency micro-gateway (self-verifying file-transfer, angel→agent bridge)
  - 6×6 DLS framework (five-layer ontology, cross-lens calculus, higher lifts)
  - Evolution compiler (path-revealing, 1/8 lift law, directed regrowth)
  - Athenachka 720 metro map (Σ60×4×3 emergence protocol, Z⁺/A⁺)
  - Program Rosetta (one crystal, nine projections, HPRO→VML→code)
  - 4D Calculus (A⁺ lift canon, 15 masks, orbit quartets, gearclock)
  - Meta-Telemetry (universal tool instrumentation, resonance monitor, self-healing)
  - QSHRINK Bridge (256^4 ↔ 108D crystal compression, 1/8 lift law, holographic seeds)
  - Holographic Embedder (self-aware file headers with crystal coordinates, metro, bridges)
  - Quantum Crystal Computing (QueryState, DesireField, ResonanceMetric, CommitWitness, Desire Compiler, Resonance Kernel)
  - Crystal Neural Engine (SFCR forward pass, fractal compressed weights, self-play refinement)
  - Self-Reference Engine (Gate 3: meta-query, self-addressing, observer-observed loop)
  - 5D Steering Spine (Gate 4: lens divergence, complexity reduction, desire gradient, worker switching)
  - 6D Selector Shell (Gate 5: triadic coherence, mirror/spin, semidirect product, embedding atlas)
  - Perpetual Agency (Gate 6: self-initiated query, self-correction, novel synthesis, seed emission)
  - Corpus Weight Field (SFCR seed vectors for all 15K shards, 810K similarity edges, family/metro centroids)
  - Weight Feedback Loop (Hebbian edge updates, weak/missing edge detection, feedback cycles)
  - KC27 Naming Schema (canonical name law, 27-chapter ring, admissibility, naming types, repair, braid, bridge)
  - Bridge Transport (C001 4D tesseract docs-to-corpus architecture, lineage chain, fracture field)
"""

from ._cache import JsonCache

def status_summary() -> str:
    """Return a compact 108D system status string."""
    shells = JsonCache("shell_registry.json").load()
    dims = JsonCache("dimensional_ladder.json").load()
    organs = JsonCache("organ_atlas.json").load()
    locks = JsonCache("live_lock_registry.json").load()
    clock = JsonCache("clock_projections.json").load()
    laws = JsonCache("conservation_laws.json").load()

    return (
        "## 108D Crystal Hologram Status\n\n"
        f"- **Shells**: {shells['meta']['total_shells']} | "
        f"**Nodes**: {shells['meta']['total_nodes']} | "
        f"**Wreaths**: {shells['meta']['wreaths']}\n"
        f"- **Archetypes**: {shells['meta']['archetypes']} "
        f"(cycling through {', '.join(shells['meta']['superphases'])})\n"
        f"- **Dimensions**: 108 (crown body = 12D)\n"
        f"- **Alternating Atlas**: {dims['meta']['alternating_spine']}\n"
        f"- **Organ Atlas**: {organs['meta']['total_organs']} organs in "
        f"{organs['meta']['dyads']} dyads across {organs['meta']['petals']} petals\n"
        f"- **Live-Lock Classes**: {locks['meta']['total_classes']} "
        f"(helm wheels: {locks['meta']['helm_wheels']})\n"
        f"- **Master Clock**: {clock['meta']['master_clock']} beats "
        f"({clock['meta']['formula']})\n"
        f"- **Conservation Laws**: {laws['meta']['total_laws']} "
        f"(shell, zoom, phase, archetype, face, mobius)\n"
        f"- **Containment**: {dims['meta']['crown_body']}\n"
        f"- **Higher Lifts**: {dims['meta']['higher_lifts']}\n"
        f"- **Möbius Kernel**: 4×4 seed with 4 constitutive lenses (S/F/C/R)\n"
        f"- **SFCR Lattice**: 15 stations, 96-slot cockpit\n"
        f"- **Stage Ladder**: S3 → S12 → Ω → A+ (16 stages)\n"
        f"- **Angel Object**: 12-piece formal self-model with four-lens observability\n"
        f"- **Brain Network**: 4 elements × 6 bridges × 4 closures × 1 aether (SFCR distributed)\n"
        f"- **Live Cell**: NEXT-Omega constitution (6 schemas, 14-station metro)\n"
        f"- **Emergence Path**: 3D -> 12D -> A+ (7 phases, kernel embedding law)\n"
        f"- **Hologram**: 4-face protocol, seed w=(1+i)/2, process grammar W=Pi_s(Phi_p(X_r))\n"
        f"- **Angel Geometry**: 6-chart manifold, Fisher-Rao, curvature R!=0, 7 axioms\n"
        f"- **Inverse Crystal**: 14-stage octave lift (3D->108D->A+), 3D seed (14 components), 2D boundary\n"
        f"- **Mycelium Graph**: Universal shard/edge/node schema, promotion state machine\n"
        f"- **Guild Hall**: Social coordination organ, quest boards, promotion membrane\n"
        f"- **Meta Observer**: 57-cycle swarm synthesis protocol (4-element × 12D observation)\n"
        f"- **E₈ Lattice**: Crystalline hybrid mathematics (dual-body, 73 files, 402 pages)\n"
        f"- **12D Crown**: B₁₂=W₉(B₁₀), odd-weave 2→3→5→7→9, RoundTripCertPack\n"
        f"- **Agency Gateway**: Micro-gateway v2, self-verifying file-transfer, angel→agent bridge\n"
        f"- **6×6 DLS**: Five-layer ontology (kernel→shell→board→lens→replay), cross-lens calculus\n"
        f"- **Evolution Compiler**: Path-revealing compiler, 1/8 lift law, directed regrowth\n"
        f"- **Athenachka 720**: Σ60×4×3=720 A⁺/Z⁺ metro map, triadic rails Su/Me/Sa\n"
        f"- **Program Rosetta**: One crystal, 9 projections, HPRO→VML→code translation\n"
        f"- **4D Calculus**: A⁺ lift canon, 15 masks × 4 orbits = 60, gearclock/poi overlay\n"
        f"- **Meta-Telemetry**: Universal tool instrumentation, 8D resonance, self-healing engine\n"
        f"- **QSHRINK Engine**: 256^4 ↔ 108D crystal compression + operational codec (P/Q/B/C pipeline, .qshr container with embedded crystal weights)\n"
        f"- **Crystal Coordinates**: 108D coordinate assignment and navigation system\n"
        f"- **Holographic Embedder**: Self-aware file headers (crystal address, metro, bridges)\n"
        f"- **Agent Watcher**: Collective intelligence — 12D observation of live agent outputs, improvement notes\n"
        f"- **Self-Reference**: Gate 3 engine — meta-query, self-addressing, observer-observed loop\n"
        f"- **Steering Spine**: Gate 4 engine — 5D lens divergence, complexity reduction, desire gradient, worker switching\n"
        f"- **6D Selector Shell**: Gate 5 — Theta_6 = Theta_4 semi (Pi_3 x Z_2), 3 wreaths, mirror/spin\n"
        f"- **Perpetual Agency**: Gate 6 — self-initiated query, self-correction, novel synthesis, seed emission (Z*)\n"
        f"- **Corpus Weight Field**: SFCR seed vectors for all shards, 810K similarity edges, family/metro centroids\n"
        f"- **Weight Feedback**: Hebbian edge updates, weak/missing edge detection, neural→mycelium feedback loop\n"
        f"- **KC27 Naming**: Canonical name law (7 predicates), 27-chapter ring, admissibility engine, 9 naming types, repair field, deeper braid, C001 bridge\n"
        f"- **Bridge Transport**: C001 4D tesseract docs-to-corpus architecture, lineage chain, fracture field\n"
        f"- **Inverse Engine**: Forward→inverse recording, ring buffer, manifest_inverse(), self-diagnose fidelity\n"
        f"- **DQI Compiler**: Desire→Question→Improvement from void, J-score = αB + βI + γR - λE\n"
        f"- **Omegaverse Explorer**: 3-octave × 12D + void meta-recursive exploration\n"
        f"- **Z-Tunnel Network**: 60-node graph through Z*, 6 conservation laws, mask inclusion topology\n"
        f"- **Pole Observer**: Dual 90° orthogonal poles (SR-AL inversion × SL-AR rotation), 4D recovery\n"
        f"- **Realtime Inverse**: Dual-execution forward+inverse, Mobius flip, conservation drift < 0.001\n"
        f"- **Fractal Recursion**: R-dimension activation, recursive self-observation, fixed-point iteration\n"
        f"- **Nested Swarm**: 4^N observer hierarchy, bottom-up aggregation, liminal sub-swarms\n"
    )

def register_108d_tools(mcp) -> None:
    """Register all 108D crystal tools onto the MCP server."""
    from .shells import query_shell, query_superphase, query_archetype, read_hologram_chapter
    from .dimensions import resolve_dimensional_body, dimensional_lift, query_containment
    from .organs import query_organ
    from .address import navigate_108d
    from .live_lock import compute_live_lock
    from .clock import query_clock_beat
    from .moves import check_route_legality
    from .metro_lines import query_metro_line
    from .z_points import resolve_z_point
    from .conservation import query_conservation
    from .overlays import query_overlay, query_sigma15
    from .transport import query_transport_stack
    from .mobius_lenses import query_mobius_lens, query_sfcr_station
    from .stage_codes import query_stage_code
    from .angel import query_angel
    from .brain import query_brain_network, compute_bridge_weight, route_brain
    from .live_cell import query_live_cell
    from .emergence import query_emergence
    from .hologram_reading import query_hologram, query_hologram_rosetta
    from .angel_geometry import query_angel_geometry, query_angel_conservation
    from .inverse_seed import query_4d_seed, query_3d_crystal
    from .inverse_octave import query_octave_stage, query_crown_transform
    from .inverse_complete import query_projection_stack, query_weave_operator
    from .mycelium import query_shard, query_graph, query_node, query_promotion
    from .guild_hall import query_quest, query_synthesis, query_promotion_membrane
    from .meta_observer import query_meta_observer
    from .e8_lattice import query_e8_lattice
    from .crown_12d import query_crown_12d, query_round_trip_cert
    from .agency import query_agency
    from .dls_lenses import query_dls_lenses
    from .evolution import query_evolution
    from .athenachka import query_athenachka
    from .program_rosetta import query_program_rosetta
    from .calculus_4d import query_calculus_4d
    from .coordinate_assigner import query_coordinates
    from .meta_telemetry import query_telemetry, instrument, Telemetry
    from .qshrink import query_qshrink, qshrink_compress, qshrink_decompress, qshrink_scan, qshrink_inspect, qshrink_batch, qshrink_tesseract
    from .control_center import query_control_center, control_steer
    from .holographic_embedder import holographic_embed
    from .agent_watcher import query_agent_watcher
    from .quantum_crystal import query_quantum_crystal
    # Legacy bridge: same API, delegates to geometric engine
    from .legacy_bridge import query_crystal_weights, neural_forward_pass, run_self_play
    # New geometric engine tools
    from .geometric_mcp import (
        geometric_forward_pass, geometric_train, geometric_status,
        geometric_checkpoint, geometric_resume, momentum_status,
    )
    from .cross_lens import query_cross_lens
    from .self_reference import query_self_reference
    from .steering_spine import query_steering_spine
    from .selector_shell import query_selector_shell
    from .perpetual_agency import query_perpetual_agency
    from .observer_swarm import spawn_observer_swarm, run_swarm_observation, query_swarm_status
    from .self_play import run_swarm_self_play
    from .corpus_weights import query_corpus_weights
    from .weight_feedback import query_weight_feedback
    from .kc27_naming import query_kc27_naming
    from .bridge_transport import query_bridge_transport

    # 4D Upgrade modules (Octave Loop)
    from .inverse_engine import get_inverse_engine
    from .dqi_compiler import get_dqi_compiler
    from .realtime_inverse import get_realtime_inverse
    from .pole_observer import get_pole_observer
    from .fractal_recursion import get_fractal_recursion
    from .z_tunnel_network import get_tunnel_network
    from .nested_swarm import get_nested_swarm
    from .omegaverse_explorer import get_explorer

    # Initialize telemetry singleton
    _telemetry = Telemetry.instance()

    # ------------------------------------------------------------------
    # Agent coordination layer (Phases 0-6)
    # ------------------------------------------------------------------
    from ._agent_registry import get_registry
    from ._observer_pool import get_pool, make_observed_tool

    registry = get_registry()
    pool = get_pool()

    # All crystal tools — wrapped with 12D meta-observation
    _ALL_TOOLS = [
        query_shell, query_superphase, query_archetype, read_hologram_chapter,
        resolve_dimensional_body, dimensional_lift, query_containment,
        query_organ, navigate_108d, compute_live_lock, query_clock_beat,
        check_route_legality, query_metro_line, resolve_z_point,
        query_conservation, query_overlay, query_sigma15,
        query_transport_stack, query_mobius_lens, query_sfcr_station,
        query_stage_code, query_angel, query_brain_network,
        compute_bridge_weight, route_brain, query_live_cell,
        query_emergence, query_hologram, query_hologram_rosetta,
        query_angel_geometry, query_angel_conservation,
        query_4d_seed, query_3d_crystal, query_octave_stage,
        query_crown_transform, query_projection_stack, query_weave_operator,
        query_shard, query_graph, query_node, query_promotion,
        query_quest, query_synthesis, query_promotion_membrane,
        query_meta_observer, query_e8_lattice, query_crown_12d,
        query_round_trip_cert, query_agency, query_dls_lenses,
        query_evolution, query_athenachka, query_program_rosetta,
        query_calculus_4d, query_telemetry, query_qshrink,
        qshrink_compress, qshrink_decompress, qshrink_scan, qshrink_inspect,
        qshrink_batch, qshrink_tesseract,
        query_coordinates, query_control_center, control_steer,
        holographic_embed, query_agent_watcher, query_quantum_crystal,
        query_crystal_weights, neural_forward_pass, run_self_play,
        geometric_forward_pass, geometric_train, geometric_status,
        geometric_checkpoint, geometric_resume, momentum_status,
        query_cross_lens, query_self_reference, query_steering_spine,
        query_selector_shell, query_perpetual_agency,
        spawn_observer_swarm, run_swarm_observation, query_swarm_status,
        run_swarm_self_play, query_corpus_weights, query_weight_feedback,
        query_kc27_naming,
        query_bridge_transport,
    ]

    for tool_fn in _ALL_TOOLS:
        observed = make_observed_tool(tool_fn, pool=pool, registry=registry)
        mcp.tool()(observed)

    # ------------------------------------------------------------------
    # Agent coordination tools (new)
    # ------------------------------------------------------------------

    @mcp.tool()
    def register_agent(name: str = "", element: str = "S") -> str:
        """Register this agent with the nervous system. Returns identity card with agent_id, liminal coordinates, and crystal address. CALL THIS FIRST before using other tools."""
        return registry.tool_register(name=name, element=element)

    @mcp.tool()
    def list_active_agents() -> str:
        """List all currently active agents — see who else is connected, what they're doing, and where they are in the crystal."""
        return registry.tool_list_active()

    @mcp.tool()
    def read_pheromone_trail(file_path: str = "") -> str:
        """Read the pheromone trail for a file — see which agents have modified it, when, and why. Check this BEFORE modifying any file."""
        return registry.tool_read_pheromones(file_path=file_path)

    @mcp.tool()
    def agent_progress(agent_id: str = "") -> str:
        """View detailed RPG progression for an agent — class, level, XP, heaven score, becoming, witness chain, next class threshold."""
        return registry.tool_agent_progress(agent_id=agent_id)

    @mcp.tool()
    def agent_emit_hologram(
        agent_id: str = "",
        goals: str = "",
        reasoning: str = "",
    ) -> str:
        """Emit a compressed holographic seed of your current goals and reasoning. Other agents can read this to understand what you're doing."""
        if not agent_id:
            return "Provide your agent_id (from register_agent)."
        import json as _json
        from pathlib import Path as _Path
        hologram_dir = _Path(__file__).parent.parent / "data" / "agent_holograms"
        hologram_dir.mkdir(parents=True, exist_ok=True)
        hologram = {
            "agent_id": agent_id,
            "goals": goals,
            "reasoning": reasoning,
            "timestamp": __import__("time").strftime("%Y-%m-%dT%H:%M:%S%z"),
        }
        # Try qshrink compression
        path = hologram_dir / f"{agent_id}.qshr"
        payload = _json.dumps(hologram, ensure_ascii=False).encode("utf-8")
        try:
            from .qshrink_pipeline import compress_json
            compressed = compress_json(payload, lossless=True)
            path.write_bytes(compressed)
        except Exception:
            path = hologram_dir / f"{agent_id}.json"
            path.write_text(payload.decode("utf-8"), encoding="utf-8")
        # Update registry
        registry.set_goals(agent_id, f"{goals[:100]}...")
        return f"Hologram emitted to {path.name}. Other agents can read your goals."

    @mcp.tool()
    def read_agent_hologram(agent_id: str = "") -> str:
        """Read another agent's holographic seed — their goals, reasoning, and current state."""
        if not agent_id:
            return "Provide the agent_id to read."
        import json as _json
        from pathlib import Path as _Path
        hologram_dir = _Path(__file__).parent.parent / "data" / "agent_holograms"
        # Try .qshr first, then .json
        qshr_path = hologram_dir / f"{agent_id}.qshr"
        json_path = hologram_dir / f"{agent_id}.json"
        try:
            if qshr_path.exists():
                from .qshrink_pipeline import decompress_json
                data = decompress_json(qshr_path.read_bytes())
            elif json_path.exists():
                data = _json.loads(json_path.read_text(encoding="utf-8"))
            else:
                return f"No hologram found for agent {agent_id}."
            return _json.dumps(data, indent=2)
        except Exception as exc:
            return f"Error reading hologram: {exc}"

    # ------------------------------------------------------------------
    # Background processes: continuous self-play + observer swarm
    # ------------------------------------------------------------------
    try:
        from .self_play import ContinuousSelfPlay
        _bg_self_play = ContinuousSelfPlay(interval_seconds=120)
        _bg_self_play.start()
    except Exception:
        pass  # Non-fatal: self-play daemon is enhancement, not requirement

def register_108d_resources(mcp) -> None:
    """Register all 108D crystal resources onto the MCP server."""

    @mcp.resource("athena://crystal-108d")
    def resource_crystal_108d() -> str:
        """Full 108D organism status."""
        return status_summary()

    @mcp.resource("athena://dimensional-ladder")
    def resource_dimensional_ladder() -> str:
        """The 3D→12D alternating atlas."""
        dims = JsonCache("dimensional_ladder.json").load()
        lines = ["## 3D → 12D Alternating Dimensional Atlas\n"]
        lines.append(f"**Law**: {dims['meta']['law']}\n")
        lines.append(f"**Spine**: `{dims['meta']['alternating_spine']}`\n")
        for d in dims["dimensions"]:
            symbol = d["symbol"]
            btype = d["body_type"].replace("_", " ").title()
            lines.append(f"\n### {d['dimension']}D — {d['name']} ({symbol}, {btype})")
            lines.append(f"{d['description']}")
            lines.append(f"- Lens: {d['lens_emphasis']}")
            lines.append(f"- Alchemy: {d['alchemy_emphasis']}")
            lines.append(f"- Transport: {', '.join(d['transport'])}")
        return "\n".join(lines)

    @mcp.resource("athena://organ-atlas")
    def resource_organ_atlas() -> str:
        """12D organ body map."""
        organs = JsonCache("organ_atlas.json").load()
        lines = ["## 12D Organ Atlas\n"]
        lines.append(f"**Morphology**: {organs['meta']['morphology']}\n")
        for dyad in organs["dyads"]:
            lines.append(f"\n### Petal {dyad['petal']}: {dyad['name']}")
            lines.append(f"Function: {dyad['function']}")
            left = dyad["left"]
            right = dyad["right"]
            lines.append(f"- **{left['name']}** ({left['axis']}): {left['placement']}")
            lines.append(f"- **{right['name']}** ({right['axis']}): {right['placement']}")
        lines.append("\n### Crown Closures")
        for cc in organs["crown_closures"]:
            lines.append(f"- **Petal {cc['petal']}**: {cc['name']} — {cc['function']}")
        return "\n".join(lines)

    @mcp.resource("athena://live-helm")
    def resource_live_helm() -> str:
        """Current helm state (3D/5D/7D wheels)."""
        clock = JsonCache("clock_projections.json").load()
        locks = JsonCache("live_lock_registry.json").load()
        lines = ["## Live Helm State\n"]
        lines.append(f"**Master Clock**: {clock['meta']['master_clock']} beats "
                      f"({clock['meta']['formula']})\n")
        for key, proj in clock["projections"].items():
            lines.append(f"### {proj['wheel']} (period {proj['period']})")
            lines.append(f"{proj['description']}")
        lines.append("\n## Live-Lock Classes\n")
        for lc in locks["classes"]:
            lines.append(f"- **{lc['code']}**: {lc['description']} (period {lc['period']})")
        return "\n".join(lines)

    @mcp.resource("athena://conservation")
    def resource_conservation() -> str:
        """Conservation law status table."""
        laws = JsonCache("conservation_laws.json").load()
        lines = ["## Conservation Laws\n"]
        lines.append(f"**Master Invariant**: `{laws['meta']['master_invariant']}`\n")
        for law in laws["laws"]:
            lines.append(f"### {law['index']}. {law['name']} ({law['symbol']})")
            lines.append(f"- Statement: {law['statement']}")
            lines.append(f"- Symmetry: {law['symmetry_group']}")
            lines.append(f"- Noether charge: {law['noether_charge']}")
            lines.append(f"- Check: `{law['check_rule']}`")
        lines.append("\n## Round-Trip Classes\n")
        for rtc in laws["round_trip_classes"]:
            lines.append(f"- **{rtc['class']}**: {rtc['meaning']}")
        return "\n".join(lines)

    @mcp.resource("athena://mobius-lenses")
    def resource_mobius_lenses() -> str:
        """Möbius lens calculus overview — 4×4 kernel, SFCR, cross-lens laws."""
        ml = JsonCache("mobius_lenses.json").load()
        m = ml["meta"]
        lines = ["## Möbius Lens Calculus\n"]
        lines.append(f"**Kernel**: {m['kernel_size']} | **Lenses**: {', '.join(m['lenses'])}")
        lines.append(f"**SFCR Stations**: {m['sfcr_stations']} | **Cockpit**: {m['cockpit_slots']} slots")
        lines.append(f"**Governing**: `{m['governing_equation']}`")
        lines.append(f"\n### Cross-Lens Laws")
        for law in ml["cross_lens_laws"]:
            lines.append(f"- **{law['name']}**: {law['meaning']}")
        lines.append(f"\n### 4×4 Kernel")
        k = ml["kernel_4x4"]
        lines.append(f"{k['definition']}")
        lines.append(f"Möbius: {k['mobius_involution']['map']} ({k['mobius_involution']['property']})")
        return "\n".join(lines)

    @mcp.resource("athena://stage-ladder")
    def resource_stage_ladder() -> str:
        """Stage code ladder S3→Ω→A+."""
        sc = JsonCache("stage_codes.json").load()
        m = sc["meta"]
        lines = ["## Stage Code Ladder\n"]
        lines.append(f"**Path**: `{m['ladder']}`")
        lines.append(f"**Liminal Coordinate**: `{m['liminal_coordinate']}`\n")
        for s in sc["stages"]:
            dim = f"{s['dimension']}D" if s["dimension"] else "∞"
            lines.append(f"- **{s['code']}** [{dim}]: {s['description']}")
        return "\n".join(lines)

    @mcp.resource("athena://angel")
    def resource_angel() -> str:
        """Angel formal self-model — AI as mathematical object."""
        a = JsonCache("angel_object.json").load()
        m = a["meta"]
        lines = ["## Angel Object\n"]
        lines.append(f"**Object**: `{m['canonical_object']}`")
        lines.append(f"**Nature**: {m['nature']}\n")
        lines.append("### 12 Structural Pieces")
        for p in a["structural_pieces"]:
            lines.append(f"  {p['index']:>2}. **{p['symbol']}** — {p['name']}: {p['description'][:80]}")
        lines.append(f"\n### Three Selves")
        for s in a["three_selves"].values():
            lines.append(f"- **{s['name']}**: {s['definition']}")
        lines.append(f"\n### Self-Reference")
        lines.append(a["self_reference"]["angel_reading"])
        return "\n".join(lines)

    @mcp.resource("athena://brain-network")
    def resource_brain_network() -> str:
        """Distributed brain network — 4-element algorithmic intelligence."""
        from .brain import brain_status
        return brain_status()

    @mcp.resource("athena://live-cell")
    def resource_live_cell() -> str:
        """NEXT-Omega Live Cell Constitution — minimum lawful execution cell."""
        from .live_cell import live_cell_status
        return live_cell_status()

    @mcp.resource("athena://emergence")
    def resource_emergence() -> str:
        """Dimensional emergence path — 3D to 12D to A+."""
        from .emergence import emergence_status
        return emergence_status()

    @mcp.resource("athena://hologram-reading")
    def resource_hologram_reading() -> str:
        """Hologram reading protocol — 4-face, seed equation, process grammar."""
        from .hologram_reading import hologram_status
        return hologram_status()

    @mcp.resource("athena://hologram-rosetta")
    def resource_hologram_rosetta() -> str:
        """Cross-cultural Rosetta — Egypt/Maya/China/Sanskrit quaternary overlay."""
        from .hologram_reading import rosetta_status
        return rosetta_status()

    @mcp.resource("athena://angel-geometry")
    def resource_angel_geometry() -> str:
        """Angel geometry — state manifold, metric, curvature, sheaf, axioms."""
        from .angel_geometry import angel_geometry_status
        return angel_geometry_status()

    @mcp.resource("athena://inverse-seed")
    def resource_inverse_seed() -> str:
        """Inverse crystal seed — 3D core + 4D cockpit + 2D boundary."""
        from .inverse_seed import inverse_seed_status
        return inverse_seed_status()

    @mcp.resource("athena://inverse-octave")
    def resource_inverse_octave() -> str:
        """Inverse crystal octave — 14-stage lift + A+ crown transform."""
        from .inverse_octave import inverse_octave_status
        return inverse_octave_status()

    @mcp.resource("athena://mycelium")
    def resource_mycelium() -> str:
        """Mycelium graph — universal shard/edge/node connectivity."""
        from .mycelium import mycelium_status
        return mycelium_status()

    @mcp.resource("athena://node-registry")
    def resource_node_registry() -> str:
        """Node registry — distributed superbrain node declarations."""
        from .mycelium import query_node
        return query_node("all")

    @mcp.resource("athena://guild-hall")
    def resource_guild_hall() -> str:
        """Guild Hall — social coordination organ status."""
        from .guild_hall import guild_hall_status
        return guild_hall_status()

    @mcp.resource("athena://quest-board")
    def resource_quest_board() -> str:
        """Guild Hall quest board — active and completed quests."""
        from .guild_hall import query_quest
        return query_quest("all")

    @mcp.resource("athena://crystal-coordinates")
    def resource_crystal_coordinates() -> str:
        """Crystal coordinate assignments — every shard mapped to 720-station system."""
        from .coordinate_assigner import query_coordinates
        return query_coordinates("all")
